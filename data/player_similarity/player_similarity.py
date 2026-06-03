import pandas as pd 
import sqlite3
import unicodedata
import re

def normalize_string(s):
    if not isinstance(s, str):
        return ""
    return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('utf-8').strip().lower()

df = pd.read_csv("data/player_similarity/FC26_20250921.csv", low_memory=False)

columns_to_keep = [
    'long_name', 'overall', 'potential', 'age', 'height_cm', 'weight_kg','nationality_name', 'skill_moves', 
    'pace', 'passing', 'shooting', 'dribbling', 'defending', 'physic',
    "attacking_crossing", "attacking_finishing", "attacking_heading_accuracy", 
    "attacking_short_passing", "attacking_volleys", "skill_dribbling", 
    "skill_curve", "skill_fk_accuracy", "skill_long_passing", 
    "skill_ball_control", "movement_acceleration", "movement_sprint_speed", 
    "movement_agility", "movement_reactions", "movement_balance", 
    "power_shot_power", "power_jumping", "power_stamina", 
    "power_strength", "power_long_shots", "mentality_aggression", 
    "mentality_interceptions", "mentality_positioning", "mentality_vision", 
    "mentality_penalties", "mentality_composure", "defending_marking_awareness", 
    "defending_standing_tackle", "defending_sliding_tackle"
]

# Seleccionamos las columnas y hacemos una copia para evitar SettingWithCopyWarning
df_filtered = df[columns_to_keep].copy()

# -------------------------------------------------------------
# LÓGICA DE FILTRADO POR CONVOCADOS
# -------------------------------------------------------------
print(f"Total de jugadores iniciales en CSV: {len(df_filtered)}")

# 1. Cargar la base de datos de convocados
conn = sqlite3.connect("data/recommender_data/convocados.db")
query = "SELECT id, pais, jugador, equipo FROM convocados"
df_convocados = pd.read_sql_query(query, conn)
conn.close()

print(f"Total de jugadores en base de datos de convocados: {len(df_convocados)}")

# 2. Filtrado y emparejamiento
matched_indices = []
missing_players = []

# Normalizamos strings (quitar acentos, a minúsculas) para comparaciones más seguras
df_filtered['long_name_lower'] = df_filtered['long_name'].apply(normalize_string)
df_filtered['nationality_lower'] = df_filtered['nationality_name'].apply(normalize_string)

for index, row_db in df_convocados.iterrows():
    jugador_db = normalize_string(str(row_db['jugador']))
    pais_db = normalize_string(str(row_db['pais']))
    
    # Condición 1: El nombre de la DB está contenido en el long_name del CSV (con boundaries \b para evitar fugas)
    pattern = r'\b' + re.escape(jugador_db) + r'\b'
    matches = df_filtered[df_filtered['long_name_lower'].str.contains(pattern, na=False, regex=True)]
    
    if len(matches) == 1:
        # Match único, lo tomamos como válido
        matched_indices.append(matches.index[0])
    elif len(matches) > 1:
        # Hay múltiples coincidencias, filtramos por país
        matches_pais = matches[matches['nationality_lower'] == pais_db]
        
        if len(matches_pais) == 1:
            matched_indices.append(matches_pais.index[0])
        elif len(matches_pais) > 1:
            # Aún hay múltiples (ej. dos jugadores homónimos del mismo país), tomamos el de mayor overall
            best_match_idx = matches_pais.sort_values(by='overall', ascending=False).index[0]
            matched_indices.append(best_match_idx)
        else:
            # Si no hay coincidencia exacta del país (por nombres diferentes de países), 
            # tomamos el mejor jugador entre los matches iniciales
            best_match_idx = matches.sort_values(by='overall', ascending=False).index[0]
            matched_indices.append(best_match_idx)
    else:
        # No hay coincidencias
        missing_players.append(row_db['jugador'])

# Eliminamos duplicados por si dos jugadores de la DB emparejaron con la misma fila del CSV
matched_indices = list(set(matched_indices))

df_final = df_filtered.loc[matched_indices].copy()

# Limpieza de columnas temporales usadas para emparejamiento
df_final.drop(columns=['long_name_lower', 'nationality_lower'], inplace=True)

# Logs de verificación
print(f"Jugadores emparejados y conservados: {len(df_final)}")
print(f"Jugadores de la DB no encontrados en el CSV: {len(missing_players)}")
if len(missing_players) > 0:
    print(f"Ejemplo de faltantes: {missing_players[:10]}")

# -------------------------------------------------------------

df_final.to_json("data/player_similarity/player_similarity_codebase.json", orient="records", indent=4, force_ascii=False)

print("LISTO")