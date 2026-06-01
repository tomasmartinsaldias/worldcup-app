"""
recommend_matches_by_players.py
================================
Given a list of 1–6 input players, always returns exactly 6 UNIQUE recommended
players ordered by cosine similarity.

Distribution rules
------------------
1 player  → top-6 neighbours
2 players → top-3 each          (2 × 3 = 6)
3 players → top-2 each          (3 × 2 = 6)
4 players → top-1 each + 2 best remaining
5 players → top-1 each + 1 best remaining
6 players → top-1 each          (6 × 1 = 6)

Collision handling
------------------
If the same neighbour is the best match for multiple inputs the next
available neighbour (lower similarity, still not yet selected) is used
so that the final list always contains 6 *distinct* players.

All input players are excluded from the recommendation pool.
"""

import sys
import os
import heapq

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import pairwise_distances

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.recommender.recommend_similar_players import load_data

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TOTAL_RECOMMENDATIONS = 6

# Numeric feature columns used for cosine distance (same as recommend_similar_players)
FEATURE_COLS = [
    'overall', 'potential', 'age', 'height_cm', 'weight_kg', 'skill_moves',
    'pace', 'passing', 'shooting', 'dribbling', 'defending', 'physic',
    'attacking_crossing', 'attacking_finishing', 'attacking_heading_accuracy',
    'attacking_short_passing', 'attacking_volleys', 'skill_dribbling',
    'skill_curve', 'skill_fk_accuracy', 'skill_long_passing',
    'skill_ball_control', 'movement_acceleration', 'movement_sprint_speed',
    'movement_agility', 'movement_reactions', 'movement_balance',
    'power_shot_power', 'power_jumping', 'power_stamina',
    'power_strength', 'power_long_shots', 'mentality_aggression',
    'mentality_interceptions', 'mentality_positioning', 'mentality_vision',
    'mentality_penalties', 'mentality_composure', 'defending_marking_awareness',
    'defending_standing_tackle', 'defending_sliding_tackle',
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _resolve_player_indices(df: pd.DataFrame, player_names: list[str]) -> dict[str, int]:
    """
    For each name in *player_names* find the corresponding row index in *df*
    (matching on 'long_name', case-insensitive).

    Returns a dict  { original_name: df_index }.
    Raises ValueError if a player is not found.
    """
    import unicodedata

    def remove_accents(s):
        return ''.join(c for c in unicodedata.normalize('NFD', str(s)) if unicodedata.category(c) != 'Mn').lower()

    resolved = {}
    for name in player_names:
        name_clean = remove_accents(name)
        # Try exact match first
        mask = df['long_name'].apply(lambda x: remove_accents(x) == name_clean)
        matches = df[mask]
        
        if matches.empty:
            # Try word subset matching (e.g. 'Lionel Messi' in 'Lionel Andres Messi Cuccittini')
            name_parts = set(name_clean.split())
            mask = df['long_name'].apply(lambda x: name_parts.issubset(set(remove_accents(x).split())))
            matches = df[mask]
            
        if matches.empty:
            # Try simple substring matching
            mask = df['long_name'].apply(lambda x: name_clean in remove_accents(x))
            matches = df[mask]
            
        if matches.empty:
            raise ValueError(f"Jugador '{name}' no encontrado en el dataset de similitud.")
        # If there are duplicates (rare) take the first occurrence
        resolved[name] = matches.index[0]
    return resolved


def _build_neighbour_lists(
    df: pd.DataFrame,
    scaled_features,
    player_idx_map: dict[str, int],
    excluded_indices: set[int],
) -> dict[str, list[tuple[float, int, str]]]:
    """
    For every input player compute the full sorted list of (distance, df_index, short_name)
    tuples, excluding all input players from the results.

    Returns a dict  { input_player_name: [(dist, idx, short_name), ...] }
    sorted ascending by distance (closest first).
    """
    neighbour_lists: dict[str, list] = {}

    # Connect to DB to get names and teams
    import sqlite3
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'recommender_data', 'convocados.db'))
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT jugador, equipo, pais FROM convocados')
    # Create a mapping from lowercase name to (jugador, equipo, pais)
    db_info = {row[0].lower(): (row[0], row[1], row[2]) for row in cur.fetchall()}
    conn.close()

    for name, idx in player_idx_map.items():
        query_vec = scaled_features[[idx]]                           # (1, F)
        distances = pairwise_distances(query_vec, scaled_features, metric='cosine')[0]

        # Build (distance, df_index, short_name, equipo) for every non-excluded player
        candidates = []
        for i in df.index:
            if i in excluded_indices:
                continue
            df_name = df.loc[i, 'long_name'].lower()
            if df_name in db_info:
                real_name, equipo, pais = db_info[df_name]
                candidates.append((float(distances[i]), i, real_name, equipo))
        
        # Sort ascending by distance (= descending by similarity)
        candidates.sort(key=lambda x: x[0])
        neighbour_lists[name] = candidates

    return neighbour_lists


def _allocate_slots(
    neighbour_lists: dict[str, list[tuple[float, int, str]]],
    guaranteed_slots_per_player: int,
    extra_slots: int,
) -> list[dict]:
    """
    Core slot-allocation algorithm.

    1. Each input player grabs its *guaranteed_slots_per_player* neighbours,
       resolving collisions by advancing to the next available neighbour.
    2. Remaining *extra_slots* are filled with the globally best (lowest
       distance) neighbours not yet selected.

    Returns a list of recommendation dicts:
        { 'short_name', 'distance', 'similarity', 'source_player' }
    """
    selected_indices: set[int] = set()
    recommendations: list[dict] = []

    # ---- Phase 1: guaranteed slots per player --------------------------------
    for player_name, candidates in neighbour_lists.items():
        granted = 0
        for dist, idx, short_name, equipo in candidates:
            if granted == guaranteed_slots_per_player:
                break
            if idx not in selected_indices:
                selected_indices.add(idx)
                recommendations.append({
                    'long_name': short_name,
                    'equipo': equipo,
                    'distance': round(dist, 6),
                    'similarity': round(1.0 - dist, 6),
                    'source_player': player_name,
                })
                granted += 1

    # ---- Phase 2: fill extra slots with globally best remaining --------------
    if extra_slots > 0:
        # Flatten all candidate lists into a single min-heap by distance
        all_candidates: list[tuple[float, int, str, str, str]] = []
        for player_name, candidates in neighbour_lists.items():
            for dist, idx, short_name, equipo in candidates:
                if idx not in selected_indices:
                    heapq.heappush(all_candidates, (dist, idx, short_name, equipo, player_name))

        while extra_slots > 0 and all_candidates:
            dist, idx, short_name, equipo, source = heapq.heappop(all_candidates)
            if idx in selected_indices:
                continue   # already grabbed in a previous iteration
            selected_indices.add(idx)
            recommendations.append({
                'long_name': short_name,
                'equipo': equipo,
                'distance': round(dist, 6),
                'similarity': round(1.0 - dist, 6),
                'source_player': f"{source} (extra)",
            })
            extra_slots -= 1

    return recommendations


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def recommend_players(
    input_players: list[str],
    json_path: str | None = None,
) -> list[dict] | dict:
    """
    Given 1–6 player names, return exactly 6 unique recommended players
    ordered by cosine similarity (ascending distance).

    Parameters
    ----------
    input_players : list[str]
        Between 1 and 6 player short_names (case-insensitive).
    json_path : str, optional
        Path to the player similarity JSON.  Defaults to the standard path.

    Returns
    -------
    list[dict]
        Sorted list of recommendation dicts:
            { 'long_name', 'distance', 'similarity', 'source_player' }
    dict
        { 'error': <message> }  on failure.
    """
    # ---- Validation ----------------------------------------------------------
    n = len(input_players)
    if n < 1 or n > TOTAL_RECOMMENDATIONS:
        return {'error': f"input_players debe contener entre 1 y {TOTAL_RECOMMENDATIONS} jugadores. Se recibieron: {n}."}

    # ---- Default path --------------------------------------------------------
    if json_path is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        json_path = os.path.join(base_dir, 'data', 'player_similarity', 'player_similarity_codebase.json')

    # ---- Load & pre-process --------------------------------------------------
    try:
        df = load_data(json_path)
    except FileNotFoundError:
        return {'error': 'Archivo de similitud no encontrado.'}

    # ---- Validate player names against convocados.db ---------------------------------------------------
    import sqlite3
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'recommender_data', 'convocados.db'))
    if not os.path.exists(db_path):
        return {'error': f"Base de datos convocados no encontrada en {db_path}."}
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Use the 'convocados' table and 'jugador' column
    cur.execute('SELECT jugador FROM convocados')
    db_names = {row[0].lower() for row in cur.fetchall()}
    # Verify each input player exists in DB
    missing = [p for p in input_players if p.lower() not in db_names]
    if missing:
        conn.close()
        return {'error': f"Jugadores no encontrados en convocados.db: {', '.join(missing)}"}
    conn.close()
    # Resolve indices in the similarity JSON as before
    try:
        player_idx_map = _resolve_player_indices(df, input_players)
    except ValueError as exc:
        return {'error': str(exc)}

    if 'nationality_name' not in df.columns:
        df['nationality_name'] = 'Unknown'

    # Scale features (same pipeline as recommend_similar_players.py)
    features = df[FEATURE_COLS].fillna(0)
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    excluded_indices = set(player_idx_map.values())

    neighbour_lists = _build_neighbour_lists(df, scaled_features, player_idx_map, excluded_indices)

    # ---- Determine slot distribution -----------------------------------------
    # Guaranteed slots per player + extra slots to fill the remaining quota
    distribution = {
        1: (6, 0),   # 1 player  → 6 slots, 0 extra
        2: (3, 0),   # 2 players → 3 each
        3: (2, 0),   # 3 players → 2 each
        4: (1, 2),   # 4 players → 1 each + 2 extra
        5: (1, 1),   # 5 players → 1 each + 1 extra
        6: (1, 0),   # 6 players → 1 each
    }
    guaranteed, extra = distribution[n]

    # ---- Allocate slots ------------------------------------------------------
    recommendations = _allocate_slots(neighbour_lists, guaranteed, extra)

    # ---- Sort final list by similarity (desc) / distance (asc) --------------
    recommendations.sort(key=lambda r: r['distance'])

    return recommendations[:TOTAL_RECOMMENDATIONS]


# ---------------------------------------------------------------------------
# CLI demo
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    import json

    test_cases = [
        ['Alphonso Davies']
    ]

    for players in test_cases:
        print(f"\n{'=' * 60}")
        print(f"Input ({len(players)} jugador{'es' if len(players) > 1 else ''}): {players}")
        print('=' * 60)
        result = recommend_players(players)
        if isinstance(result, dict) and 'error' in result:
            print(f"  ERROR: {result['error']}")
        else:
            for i, rec in enumerate(result, 1):
                print(f"  {i}. {rec['long_name']:30s} | {rec['equipo']:20s}  sim={rec['similarity']:.4f}  (fuente: {rec['source_player']})")
