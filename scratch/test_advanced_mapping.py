import sqlite3
import pandas as pd
import unicodedata
import re

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
    "panama": "Panama"
}

def normalize_string(s):
    if not isinstance(s, str):
        return ""
    # Transliterate special characters that NFD does not map to ASCII
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
    
    # Normalize suffixes like "jr." or "jr" to "junior"
    s = re.sub(r'\bjr\b\.?', 'junior', s)
    return s

df = pd.read_csv("data/player_similarity/FC26_20250921.csv", low_memory=False)
df['long_name_lower'] = df['long_name'].apply(normalize_string)
df['short_name_lower'] = df['short_name'].apply(normalize_string)

conn = sqlite3.connect("data/recommender_data/convocados.db")
query = "SELECT id, pais, jugador FROM convocados"
df_convocados = pd.read_sql_query(query, conn)
conn.close()

matched_indices = []
missing = []

for index, row_db in df_convocados.iterrows():
    jugador_db_raw = str(row_db['jugador'])
    pais_db_raw = str(row_db['pais'])
    
    jugador_db = normalize_string(jugador_db_raw)
    pais_db_norm = normalize_string(pais_db_raw)
    
    # Translate country
    english_country = COUNTRY_MAP.get(pais_db_norm)
    if not english_country:
        # Fallback to direct search if not in map
        df_country = df
    else:
        df_country = df[df['nationality_name'] == english_country]
        
    # Attempt matching
    # 1. Exact regex word match on long_name or short_name
    pattern = r'\b' + re.escape(jugador_db) + r'\b'
    matches = df_country[df_country['long_name_lower'].str.contains(pattern, na=False, regex=True) |
                         df_country['short_name_lower'].str.contains(pattern, na=False, regex=True)]
    
    # 2. If no match, try word-inclusion (all words of jugador_db in long_name_lower)
    if len(matches) == 0:
        words = [w for w in re.split(r'[^a-zA-Z0-9]', jugador_db) if len(w) > 1]
        if words:
            # Check if all words are present in long_name_lower
            mask = df_country['long_name_lower'].apply(lambda name: all(w in name for w in words))
            matches = df_country[mask]
            
    # 3. If still no match, try checking if the words are in short_name_lower
    if len(matches) == 0:
        words = [w for w in re.split(r'[^a-zA-Z0-9]', jugador_db) if len(w) > 1]
        if words:
            mask = df_country['short_name_lower'].apply(lambda name: all(w in name for w in words))
            matches = df_country[mask]

    if len(matches) >= 1:
        # If multiple matches, pick the one with highest overall
        best_match_idx = matches.sort_values(by='overall', ascending=False).index[0]
        matched_indices.append(best_match_idx)
    else:
        missing.append((jugador_db_raw, pais_db_raw))

matched_indices = list(set(matched_indices))
print(f"Total convocados: {len(df_convocados)}")
print(f"Total emparejados exitosamente: {len(matched_indices)}")
print(f"Total desaparecidos: {len(missing)}")
print("\nPrimeros 20 desaparecidos con este nuevo método:")
for m in missing[:20]:
    print(f"  Jugador: {m[0]} | País: {m[1]}")
