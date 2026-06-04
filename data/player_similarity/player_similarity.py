import pandas as pd
import sqlite3
import unicodedata
import re

def normalize_string(s):
    if not isinstance(s, str):
        return ""
    # Transliterate special characters that NFD does not map to ASCII
    replacements = {
        'ø': 'o', 'Ø': 'o',
        'æ': 'ae', 'Æ': 'ae',
        'å': 'a', 'Å': 'a',
        'ß': 'ss',
        'ı': 'i', 'İ': 'i',
        'đ': 'd', 'Đ': 'd',
        "'": "", '’': "",
        '\u200c': '',
        '-': ' ',
    }
    for char, repl in replacements.items():
        s = s.replace(char, repl)

    s = unicodedata.normalize('NFD', s)
    s = s.encode('ascii', 'ignore').decode('utf-8').strip().lower()

    # Strip Arabic article prefixes al / el at word boundaries
    s = re.sub(r'\b(al|el)\b\s*', '', s)

    # Normalize common prefix spacings
    s = s.replace('abdul ', 'abdul').replace('abdel ', 'abdel')

    # Map nickname joe to joseph at word boundary
    s = re.sub(r'\bjoe\b', 'joseph', s)

    # Normalize suffixes like "jr." or "jr" to "junior"
    s = re.sub(r'\bjr\b\.?', 'junior', s)

    # Map common nicknames/diminutivos to their full matches in the CSV
    name_variants = {
        'leo messi': 'lionel messi',
        'andy robertson': 'andrew robertson',
        'noni madueke': 'chukwunonso madueke',
        'ollie watkins': 'oliver watkins',
        'grob': 'gross',
        'haaland': 'haland',
        'yaya sithole': 'sphephelo sithole',
        'johnny placide': 'johny placide',
        'wilguens pauguain': 'wilguens paugain',
        'jk duverne': 'jean kevin duverne',
        'jeanricner bellegarde': 'jean ricner bellegarde',
        'nestory irakunda': 'nestory irankunda',
        'kenny mclean': 'kenneth mclean',
        'cristophe kabongo': 'christophe kabongo',
        'redouane hahlal': 'redouane halhal',
        'michail sadilek': 'michal sadilek',
        'meshack elia': 'meschack elia',
        'richie laryea': 'richmond laryea',
        'ben slimane': 'benslimane',
        'ben romdhane': 'benromdhane',
        'ben seghir': 'benseghir',
        'ben ouanes': 'benouanes',
        'ben old': 'benjamin old',
        'ben waine': 'benjamin waine'
    }
    for k, v in name_variants.items():
        s = s.replace(k, v)

    return s

df = pd.read_csv("data/player_similarity/FC26_20250921.csv", encoding="utf-8", low_memory=False)

# Translation map for convocados.db (Spanish) -> FC26 CSV (English)
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
    "ecuador": "Ecuador",
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
    "argelia": "Algeria",
    "mexico": "Mexico",
    "paraguay": "Paraguay",
    "australia": "Australia",
    "turquia": "Türkiye",
    "iran": "Iran",
    "arabia saudita": "Saudi Arabia",
    "irak": "Iraq"
}

columns_to_keep = [
    'short_name', 'long_name', 'overall', 'potential', 'age', 'height_cm', 'weight_kg','nationality_name', 'skill_moves',
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
# LÓGICA DE FILTRADO POR CONVOCADOS (Mapeo Inteligente)
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
df_filtered['short_name_lower'] = df_filtered['short_name'].apply(normalize_string)

for index, row_db in df_convocados.iterrows():
    jugador_db_raw = str(row_db['jugador'])
    pais_db_raw = str(row_db['pais'])

    jugador_db = normalize_string(jugador_db_raw)
    pais_db_norm = normalize_string(pais_db_raw)

    # Traducir nombre del país para restringir el ámbito de búsqueda y evitar homónimos
    english_country = COUNTRY_MAP.get(pais_db_norm)
    if not english_country:
        df_country = df_filtered
    else:
        df_country = df_filtered[df_filtered['nationality_name'] == english_country]

    # Método 1: Búsqueda de palabra exacta en nombre largo o corto
    pattern = r'\b' + re.escape(jugador_db) + r'\b'
    matches = df_country[df_country['long_name_lower'].str.contains(pattern, na=False, regex=True) |
                         df_country['short_name_lower'].str.contains(pattern, na=False, regex=True)]

    # Método 2: Inclusión de palabras en nombre largo (ej. "Lyle Foster" en "Lyle Brent Foster")
    if len(matches) == 0:
        words = [w for w in re.split(r'[^a-zA-Z0-9]', jugador_db) if len(w) > 1]
        if words:
            mask = df_country['long_name_lower'].apply(lambda name: all(w in name for w in words))
            matches = df_country[mask]

    # Método 3: Inclusión de palabras en nombre corto
    if len(matches) == 0:
        words = [w for w in re.split(r'[^a-zA-Z0-9]', jugador_db) if len(w) > 1]
        if words:
            mask = df_country['short_name_lower'].apply(lambda name: all(w in name for w in words))
            matches = df_country[mask]

    # Fallback global para jugadores con nacionalidad diferente en FIFA (doble ciudadanía)
    if len(matches) == 0 and english_country is not None:
        matches = df_filtered[df_filtered['long_name_lower'].str.contains(pattern, na=False, regex=True) |
                              df_filtered['short_name_lower'].str.contains(pattern, na=False, regex=True)]

        if len(matches) == 0:
            words = [w for w in re.split(r'[^a-zA-Z0-9]', jugador_db) if len(w) > 1]
            if words:
                mask = df_filtered['long_name_lower'].apply(lambda name: all(w in name for w in words))
                matches = df_filtered[mask]

        if len(matches) == 0:
            words = [w for w in re.split(r'[^a-zA-Z0-9]', jugador_db) if len(w) > 1]
            if words:
                mask = df_filtered['short_name_lower'].apply(lambda name: all(w in name for w in words))
                matches = df_filtered[mask]

    if len(matches) >= 1:
        best_match_idx = matches.sort_values(by='overall', ascending=False).index[0]
        matched_indices.append(best_match_idx)
    else:
        missing_players.append(jugador_db_raw)

# Eliminamos duplicados por si dos jugadores de la DB emparejaron con la misma fila del CSV
matched_indices = list(set(matched_indices))

df_final = df_filtered.loc[matched_indices].copy()

# Limpieza de columnas temporales usadas para emparejamiento
df_final.drop(columns=['short_name', 'long_name_lower', 'short_name_lower'], inplace=True)

# Logs de verificación
print(f"Jugadores emparejados y conservados: {len(df_final)}")
print(f"Jugadores de la DB no encontrados en el CSV: {len(missing_players)}")
if len(missing_players) > 0:
    print(f"Ejemplo de faltantes: {missing_players[:10]}")

# -------------------------------------------------------------

df_final.to_json("data/player_similarity/player_similarity_codebase.json", orient="records", indent=4, force_ascii=False)

print("LISTO")
