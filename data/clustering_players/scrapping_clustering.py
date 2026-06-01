
import pandas as pd
import sys
import sqlite3
import unicodedata
import re

def normalize_string(s):
    if not isinstance(s, str):
        return ""
    return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('utf-8').strip().lower()

# Set stdout to utf-8 to prevent charmap encode errors on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# ------------------------------------------------------------------
# Mapping of detailed position codes to macro‑position groups
# ------------------------------------------------------------------
POSITION_MAP = {
    "goalkeeper": ["GK"],
    "defender":   ["CB", "LB", "RB", "LWB", "RWB"],
    "midfielder": ["CM", "CDM", "CAM", "DM"],
    "striker":    ["ST", "CF", "SS"],
    "wingers":    ["LM", "RM", "RW", "LW"]
}
# ------------------------------------------------------------------
# Columns we want to keep from the original CSV
# ------------------------------------------------------------------
columns_to_keep = [
    "long_name","player_positions", "nationality_name", "overall", "age", "height_cm", "weight_kg",
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
# ------------------------------------------------------------------
# Load data
# ------------------------------------------------------------------
df = pd.read_csv("data/player_similarity/FC26_20250921.csv", low_memory=False)
# Keep only the selected columns
df_filtered = df[columns_to_keep].copy()

# ------------------------------------------------------------------
# LÓGICA DE FILTRADO POR CONVOCADOS
# ------------------------------------------------------------------
print(f"Total de jugadores iniciales en CSV: {len(df)}")

conn = sqlite3.connect("data/recommender_data/convocados.db")
query = "SELECT id, pais, jugador, equipo FROM convocados"
df_convocados = pd.read_sql_query(query, conn)
conn.close()

print(f"Total de jugadores en base de datos de convocados: {len(df_convocados)}")

matched_indices = []
missing_players = []

df_filtered['long_name_lower'] = df_filtered['long_name'].apply(normalize_string)
df_filtered['nationality_lower'] = df_filtered['nationality_name'].apply(normalize_string)

for index, row_db in df_convocados.iterrows():
    jugador_db = normalize_string(str(row_db['jugador']))
    pais_db = normalize_string(str(row_db['pais']))
    
    pattern = r'\b' + re.escape(jugador_db) + r'\b'
    matches = df_filtered[df_filtered['long_name_lower'].str.contains(pattern, na=False, regex=True)]
    
    if len(matches) == 1:
        matched_indices.append(matches.index[0])
    elif len(matches) > 1:
        matches_pais = matches[matches['nationality_lower'] == pais_db]
        
        if len(matches_pais) == 1:
            matched_indices.append(matches_pais.index[0])
        elif len(matches_pais) > 1:
            best_match_idx = matches_pais.sort_values(by='overall', ascending=False).index[0]
            matched_indices.append(best_match_idx)
        else:
            best_match_idx = matches.sort_values(by='overall', ascending=False).index[0]
            matched_indices.append(best_match_idx)
    else:
        missing_players.append(row_db['jugador'])

matched_indices = list(set(matched_indices))

df_filtered = df_filtered.loc[matched_indices].copy()
df_filtered.drop(columns=['long_name_lower', 'nationality_lower'], inplace=True)

print(f"Jugadores emparejados y conservados tras filtro DB: {len(df_filtered)}")
print(f"Jugadores de la DB no encontrados en el CSV: {len(missing_players)}")

# ------------------------------------------------------------------
# Helper: assign macro‑position based on the first matching group
# ------------------------------------------------------------------
def assign_macro_group(pos_str: str) -> str | None:
    """Return the macro‑group for a player according to POSITION_MAP.
    The first position listed in the player's detailed positions is used to determine
    the macro‑group."""
    if pd.isna(pos_str):
        return None
    # Split the string like "CAM, CM" → ["CAM", "CM"]
    positions = [p.strip() for p in pos_str.split(",")]
    if not positions:
        return None
    first_position = positions[0]
    for macro, codes in POSITION_MAP.items():
        if first_position in codes:
            return macro
    return None
# Create a column with the macro‑group
df_filtered["macro_group"] = df_filtered["player_positions"].apply(assign_macro_group)
# ------------------------------------------------------------------
# Write one JSON file per macro‑group
# ------------------------------------------------------------------
output_dir = "data/clustering_players"
print(f"Total de jugadores para clustering (tras filtro): {len(df_filtered)}")

total_conservados = 0

for macro in POSITION_MAP.keys():
    macro_df = df_filtered[df_filtered["macro_group"] == macro].drop(columns=["macro_group"])
    if not macro_df.empty:
        file_path = f"{output_dir}/player_clustering_{macro}.json"
        macro_df.to_json(file_path, orient="records", indent=4, force_ascii=False)
        num_players = len(macro_df)
        total_conservados += num_players
        print(f"✅  {macro.title()} players ({num_players} conservados) → {file_path}")
print(f"Total de jugadores asignados y conservados en grupos: {total_conservados}")
print("✅  All macro‑group JSON files generated")