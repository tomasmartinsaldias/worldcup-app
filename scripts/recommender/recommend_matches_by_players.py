"""
recommend_matches_by_players.py
================================
Given a list of 1–6 input players, always returns exactly 6 UNIQUE recommended
players ordered by cosine similarity, using the player similarity JSON and
wc2026_data.json instead of the SQLite database.

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
import json
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import pairwise_distances

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TOTAL_RECOMMENDATIONS = 6

# Numeric feature columns used for cosine distance
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

def normalize_name(s):
    import unicodedata
    import re
    if not isinstance(s, str):
        return ""
    replacements = {
        'ø': 'o', 'Ø': 'o',
        'æ': 'ae', 'Æ': 'ae',
        'å': 'a', 'Å': 'a',
        'ß': 'ss',
    }
    for char, repl in replacements.items():
        s = s.replace(char, repl)
    s = unicodedata.normalize('NFD', s)
    s = s.encode('ascii', 'ignore').decode('utf-8').strip().lower()
    s = re.sub(r'\bjr\b\.?', 'junior', s)
    return s

def _resolve_player_indices(df: pd.DataFrame, player_names: list[str]) -> dict[str, int]:
    """
    For each name in *player_names* find the corresponding row index in *df*
    (matching on 'long_name', case-insensitive).
    """
    resolved = {}
    for name in player_names:
        name_clean = normalize_name(name)
        # Try exact match first
        mask = df['long_name'].apply(lambda x: normalize_name(x) == name_clean)
        matches = df[mask]
        
        if matches.empty:
            # Try word subset matching
            name_parts = set(name_clean.split())
            mask = df['long_name'].apply(lambda x: name_parts.issubset(set(normalize_name(x).split())))
            matches = df[mask]
            
        if matches.empty:
            # Try simple substring matching
            mask = df['long_name'].apply(lambda x: name_clean in normalize_name(x))
            matches = df[mask]
            
        if matches.empty:
            raise ValueError(f"Jugador '{name}' no encontrado en el dataset de similitud.")
        resolved[name] = matches.index[0]
    return resolved

def _build_neighbour_lists(
    df: pd.DataFrame,
    scaled_features,
    player_idx_map: dict[str, int],
    excluded_indices: set[int],
) -> dict[str, list[tuple[float, int, str, str]]]:
    """
    For every input player compute the full sorted list of (distance, df_index, real_name, equipo)
    tuples, excluding all input players from the results.
    """
    neighbour_lists: dict[str, list] = {}

    # Load wc2026_data.json to get player, club (equipo), and country (pais)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    wc_data_path = os.path.join(base_dir, 'data', 'wc2026_data.json')
    db_info = {}
    if os.path.exists(wc_data_path):
        try:
            with open(wc_data_path, 'r', encoding='utf-8') as f:
                wc_data = json.load(f)
            for team_code, team_val in wc_data.get("teams", {}).items():
                pais = team_val.get("name", "")
                for player in team_val.get("squad", []):
                    p_name = player.get("name", "")
                    p_club = player.get("club", "Desconocido")
                    norm_p = normalize_name(p_name)
                    if len(norm_p) > 2:
                        db_info[norm_p] = (p_name, p_club, pais)
        except Exception as e:
            print(f"Advertencia: No se pudo parsear wc2026_data.json ({e})")

    for name, idx in player_idx_map.items():
        query_vec = scaled_features[[idx]]
        distances = pairwise_distances(query_vec, scaled_features, metric='cosine')[0]

        candidates = []
        for i in df.index:
            if i in excluded_indices:
                continue
            df_long_name = df.loc[i, 'long_name']
            norm_df_name = normalize_name(df_long_name)
            
            # Find in db_info
            match_info = db_info.get(norm_df_name)
            if not match_info:
                for norm_db_name, info in db_info.items():
                    if len(norm_db_name) > 2 and len(norm_df_name) > 2 and (norm_db_name in norm_df_name or norm_df_name in norm_db_name):
                        match_info = info
                        break
            
            if match_info:
                real_name, equipo, pais = match_info
            else:
                real_name = df_long_name
                equipo = "Desconocido"
                
            candidates.append((float(distances[i]), i, real_name, equipo))
        
        # Sort ascending by distance (= descending by similarity)
        candidates.sort(key=lambda x: x[0])
        neighbour_lists[name] = candidates

    return neighbour_lists

def _allocate_slots(
    neighbour_lists: dict[str, list[tuple[float, int, str, str]]],
    guaranteed_slots_per_player: int,
    extra_slots: int,
) -> list[dict]:
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
                continue
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

def recommend_players(
    input_players: list[str],
    json_path: str | None = None,
) -> list[dict] | dict:
    """
    Given 1–6 player names, return exactly 6 unique recommended players
    ordered by cosine similarity (ascending distance) using JSON datasets.
    """
    n = len(input_players)
    if n < 1 or n > TOTAL_RECOMMENDATIONS:
        return {'error': f"input_players debe contener entre 1 y {TOTAL_RECOMMENDATIONS} jugadores. Se recibieron: {n}."}

    if json_path is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        json_path = os.path.join(base_dir, 'data', 'player_similarity', 'player_similarity_codebase.json')

    if not os.path.exists(json_path):
        return {'error': f"Archivo de similitud no encontrado en: {json_path}."}

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    except Exception as e:
        return {'error': f"Error al cargar el archivo de similitud: {str(e)}"}

    # Resolve indices in the similarity JSON
    try:
        player_idx_map = _resolve_player_indices(df, input_players)
    except ValueError as exc:
        return {'error': str(exc)}

    if 'nationality_name' not in df.columns:
        df['nationality_name'] = 'Unknown'

    # Scale features
    features = df[FEATURE_COLS].fillna(0)
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    excluded_indices = set(player_idx_map.values())

    neighbour_lists = _build_neighbour_lists(df, scaled_features, player_idx_map, excluded_indices)

    # ---- Determine slot distribution -----------------------------------------
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

if __name__ == '__main__':
    test_cases = [
        ['Alphonso Boyle Davies']
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
