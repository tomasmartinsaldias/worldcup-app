import sqlite3
import pandas as pd
import unicodedata
import re

def normalize_string(s):
    if not isinstance(s, str):
        return ""
    # Treat common encoding errors
    s = s.replace('', 'a') # or similar, let's check
    return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('utf-8').strip().lower()

df = pd.read_csv("data/player_similarity/FC26_20250921.csv", low_memory=False)
df['long_name_lower'] = df['long_name'].apply(normalize_string)
df['short_name_lower'] = df['short_name'].apply(normalize_string)
df['nationality_lower'] = df['nationality_name'].apply(normalize_string)

conn = sqlite3.connect("data/recommender_data/convocados.db")
query = "SELECT id, pais, jugador FROM convocados"
df_convocados = pd.read_sql_query(query, conn)
conn.close()

# Let's inspect some matching and mismatching
print("Ejemplos de países en DB:")
print(df_convocados['pais'].unique()[:10])

print("\nEjemplos de países en CSV:")
print(df['nationality_name'].unique()[:10])

# Let's print some missing players
missing = []
for index, row_db in df_convocados.iterrows():
    jugador_db = normalize_string(str(row_db['jugador']))
    pais_db = normalize_string(str(row_db['pais']))
    
    # Try exact match on long name or short name
    pattern = r'\b' + re.escape(jugador_db) + r'\b'
    matches = df[df['long_name_lower'].str.contains(pattern, na=False, regex=True) | 
                 df['short_name_lower'].str.contains(pattern, na=False, regex=True)]
    
    if len(matches) == 0:
        missing.append((row_db['jugador'], row_db['pais']))

print(f"\nTotal desaparecidos: {len(missing)}")
print("Primeros 20 desaparecidos:")
for m in missing[:20]:
    print(f"  Jugador: {m[0]} | País: {m[1]}")
