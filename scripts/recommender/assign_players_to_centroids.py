import os
import json
import re
import sqlite3
import numpy as np
import pandas as pd
from sklearn.preprocessing import MaxAbsScaler, normalize

# ------------------------------------------------------------------
# Mapping of detailed position codes to macro‑position groups (same as in HAC_clustering)
# ------------------------------------------------------------------
POSITION_MAP = {
    "goalkeeper": ["GK"],
    "centerbacks": ["CB"],
    "fullbacks":   ["LB", "RB", "LWB", "RWB"],
    "midfielder": ["CM", "CDM", "CAM", "DM"],
    "striker":    ["ST", "CF", "SS"],
    "wingers":    ["LM", "RM", "RW", "LW"]
}

def assign_macro_group(pos_str: str) -> str | None:
    """Return the macro‑group for a player according to POSITION_MAP.
    The first position listed in the player's detailed positions is used to determine
    the macro‑group."""
    if pd.isna(pos_str):
        return None
    positions = [p.strip() for p in pos_str.split(",")]
    if not positions:
        return None
    first_position = positions[0]
    for macro, codes in POSITION_MAP.items():
        if first_position in codes:
            return macro.title()
    return None

def normalize_string(s):
    """Utility from scrapping_clustering to normalise player names."""
    if not isinstance(s, str):
        return ""
    # simple lower‑case, strip accents, etc.
    s = s.lower().strip()
    return s

# Columns we keep – same list used in scrapping_clustering.py
COLUMNS_TO_KEEP = [
    "short_name", "long_name", "player_positions", "nationality_name", "overall", "age", "height_cm", "weight_kg",
    "pace", "passing", "shooting", "dribbling", "defending", "physic",
    "attacking_crossing", "attacking_finishing", "attacking_heading_accuracy",
    "attacking_short_passing", "attacking_volleys", "skill_dribbling",
    "skill_curve", "skill_fk_accuracy", "skill_long_passing",
    "skill_ball_control", "movement_acceleration", "movement_sprint_speed",
    "movement_agility", "movement_reactions", "movement_balance",
    "power_shot_power", "power_jumping", "power_stamina",
    "power_strength", "power_long_shots", "mentality_aggression",
    "mentality_interceptions", "mentality_positioning", "mentality_vision",
    "mentality_penalties", "mentality_composure",
    "defending_marking_awareness", "defending_standing_tackle",
    "defending_sliding_tackle"
]

COUNTRY_MAP = {
    "sudafrica": "South Africa",
    "corea del sur": "Korea Republic",
    "republica checa": "Czechia",
    "bosnia y herzegovina": "Bosnia and Herzegovina",
    "suiza": "Switzerland",
    "brasil": "Brazil",
    "marruecos": "Morocco",
    "haiti": "Haiti",
    "escocia": "Scotland",
    "estados unidos": "United States",
    "alemania": "Germany",
    "curazao": "Curacao",
    "costa de marfil": "Côte d'Ivoire",
    "ecuador": "Netherlands",
    "japon": "Japan",
    "suecia": "Sweden",
    "tunez": "Tunisia",
    "belgica": "Belgium",
    "egipto": "Egypt",
    "nueva zelanda": "New Zealand",
    "espana": "Spain",
    "cabo verde": "Cabo Verde",
    "francia": "France",
    "senegal": "Senegal",
    "noruega": "Norway",
    "argentina": "Argentina",
    "austria": "Austria",
    "portugal": "Portugal",
    "rd congo": "Congo DR",
    "colombia": "Colombia",
    "inglaterra": "England",
    "croacia": "Croatia",
    "panama": "Panama",
    "canada": "Canada",
    "paises bajos": "Netherlands",
    "uruguay": "Uruguay",
    "argelia": "Algeria"
}

def filter_by_convocados(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only players that match entries in convocados.db using the same logic as scrapping_clustering."""
    conn = sqlite3.connect(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'recommender_data', 'convocados.db')))
    query = "SELECT id, pais, jugador, equipo FROM convocados"
    df_conv = pd.read_sql_query(query, conn)
    conn.close()

    # add lower‑case normalized columns for matching
    df['long_name_lower'] = df['long_name'].apply(normalize_string)
    df['short_name_lower'] = df['short_name'].apply(normalize_string)

    matched_indices = []
    for _, row in df_conv.iterrows():
        jugador_db_raw = str(row['jugador'])
        pais_db_raw = str(row['pais'])
        jugador_db = normalize_string(jugador_db_raw)
        pais_db_norm = normalize_string(pais_db_raw)
        # Translate country (same map as in scrapping_clustering – simplified here)
        english_country = COUNTRY_MAP.get(pais_db_norm)
        if not english_country:
            df_country = df
        else:
            df_country = df[df['nationality_name'] == english_country]
        pattern = r'\b' + re.escape(jugador_db) + r'\b'
        matches = df_country[df_country['long_name_lower'].str.contains(pattern, na=False, regex=True) |
                          df_country['short_name_lower'].str.contains(pattern, na=False, regex=True)]
        if matches.empty:
            words = [w for w in re.split(r'[^a-zA-Z0-9]', jugador_db) if len(w) > 1]
            if words:
                mask = df_country['long_name_lower'].apply(lambda name: all(w in name for w in words))
                matches = df_country[mask]
        if matches.empty:
            words = [w for w in re.split(r'[^a-zA-Z0-9]', jugador_db) if len(w) > 1]
            if words:
                mask = df_country['short_name_lower'].apply(lambda name: all(w in name for w in words))
                matches = df_country[mask]
        if not matches.empty:
            matched_indices.extend(matches.index.tolist())
    df_filtered = df.loc[sorted(set(matched_indices))].copy()
    # keep only the selected columns
    df_filtered = df_filtered[COLUMNS_TO_KEEP]
    return df_filtered

def preprocess(df: pd.DataFrame):
    """Preprocess the filtered dataframe to obtain normalized feature vectors.
    Returns (features, player_names, overalls)."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if "overall" in numeric_cols:
        numeric_cols.remove("overall")
    df_numeric = df[numeric_cols].apply(lambda col: col.fillna(col.median()))
    df_numeric = df_numeric.fillna(0)
    scaler = MaxAbsScaler()
    scaled = scaler.fit_transform(df_numeric)
    normalized = normalize(scaled, norm='l2')
    overall_median = df['overall'].median() if "overall" in df.columns else 50
    overall_median = 50 if pd.isna(overall_median) else overall_median
    overalls = df['overall'].fillna(overall_median).values
    return normalized, df['long_name'].values, overalls

# The original load_centroids function was overridden later to handle pluralized filenames.
# It is retained here only for reference and will not be used.


# Map macro group names to centroid file suffixes
CENTROID_FILE_MAP = {
    "Goalkeeper": "goalkeepers",
    "Centerbacks": "centerbacks",
    "Fullbacks": "fullbacks",
    "Midfielder": "midfielders",
    "Striker": "strikers",
    "Wingers": "wingers",
    "Winger": "wingers",  # fallback for singular
}

def load_centroids(position: str):
    """Load centroids JSON for the given macro group.
    Returns a NumPy array of shape (n_clusters, n_features)."""
    # Resolve filename suffix using the map; default to lowercased position
    suffix = CENTROID_FILE_MAP.get(position, position.lower())
    centroid_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..', 'data', 'clustering_maps',
        f"kmeans_{suffix}_centroids.json"
    ))
    with open(centroid_path, "r", encoding="utf-8") as f:
        centroids_json = json.load(f)
    # Ensure ordering by cluster_id
    centroids_json.sort(key=lambda x: x["cluster_id"])
    return np.array([c["centroid"] for c in centroids_json])

def main():
    # Load the full player similarity CSV (contains every player)
    csv_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..', 'data', 'player_similarity', 'FC26_20250921.csv'
    ))
    df_raw = pd.read_csv(csv_path, low_memory=False)
    # Apply the same DB matching filter used in scrapping_clustering
    df_filtered = filter_by_convocados(df_raw)
    # Keep only players with overall < 75

    # Add macro group column
    df_filtered["macro_group"] = df_filtered["player_positions"].apply(assign_macro_group)
    print("Macro group counts:", df_filtered['macro_group'].value_counts())

    positions = ["Goalkeeper", "Centerbacks", "Fullbacks", "Midfielder", "Striker", "Wingers"]
    for position in positions:
        df_pos = df_filtered[df_filtered["macro_group"] == position]
        if df_pos.empty:
            print(f"No players found for {position}, skipping.")
            continue
        # Preprocess features for this subset and obtain player names and overalls
        features, names, overalls = preprocess(df_pos)
        # Load centroids for this position
        centroids = load_centroids(position)
        # Align feature dimensionality: truncate or pad if needed
        if features.shape[1] != centroids.shape[1]:
            # Truncate to the smaller dimension
            min_dim = min(features.shape[1], centroids.shape[1])
            features = features[:, :min_dim]
            centroids = centroids[:, :min_dim]
        # Compute distances to centroids (Euclidean)
        distances = np.linalg.norm(features[:, None, :] - centroids[None, :, :], axis=2)  # (n_players, n_clusters)
        suffix = CENTROID_FILE_MAP.get(position, position.lower())
        archetype_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', 'data', 'clustering_maps',
            f"kmeans_{suffix}_arquetipos.json"
        ))
        with open(archetype_path, "r", encoding="utf-8") as f_ar:
            archetype_json = json.load(f_ar)
        # Build name -> cluster_id dict (use long_name field)
        name_to_cluster = {rec["long_name"]: rec["cluster_id"] for rec in archetype_json}
        # Determine nearest centroid indices for all players
        nearest = np.argmin(distances, axis=1)
        # Build result structure preserving original clusters for high‑overall players
        cluster_records = []
        for cid in range(centroids.shape[0]):
            players = []
            # Find players assigned to this cluster either by original mapping (>75) or nearest
            for idx in range(len(names)):
                player_name = str(names[idx])
                player_overall = int(overalls[idx])
                # Check if this high‑overall player has a fixed cluster
                fixed_cluster = name_to_cluster.get(player_name) if player_overall > 75 else None
                if fixed_cluster is not None:
                    assigned_cid = fixed_cluster - 1  # convert to 0‑based index
                else:
                    assigned_cid = nearest[idx]
                if assigned_cid == cid:
                    players.append({
                        "long_name": player_name,
                        "overall": player_overall,
                        "distance": round(float(distances[idx, cid]), 6)
                    })
            cluster_records.append({
                "cluster_id": cid + 1,
                "players": players
            })
        # Save to JSON
        output_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', 'data', 'clustering_maps',
            f"kmeans_{position.lower()}_full_distances.json"
        ))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cluster_records, f, ensure_ascii=False, indent=4)
        print(f"[OK] Distances JSON creado: {output_path} ({len(df_pos)} jugadores)")

if __name__ == "__main__":
    main()
