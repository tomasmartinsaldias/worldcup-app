import pandas as pd
import sqlite3
import re
import unicodedata

def normalize_string(s):
    if not isinstance(s, str):
        return ""
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
    
    s = re.sub(r'\bjr\b\.?', 'junior', s)
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

def main():
    df = pd.read_csv("data/player_similarity/FC26_20250921.csv", encoding="utf-8", low_memory=False)
    
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
    
    df['long_name_lower'] = df['long_name'].apply(normalize_string)
    df['short_name_lower'] = df['short_name'].apply(normalize_string)
    
    conn = sqlite3.connect("data/recommender_data/convocados.db")
    df_convocados = pd.read_sql_query("SELECT pais, jugador, equipo FROM convocados", conn)
    conn.close()
    
    missing = []
    for index, row_db in df_convocados.iterrows():
        jugador_db_raw = str(row_db['jugador'])
        pais_db_raw = str(row_db['pais'])
        equipo_db_raw = str(row_db['equipo'])
        
        jugador_db = normalize_string(jugador_db_raw)
        pais_db_norm = normalize_string(pais_db_raw)
        
        english_country = COUNTRY_MAP.get(pais_db_norm)
        if english_country:
            df_country = df[df['nationality_name'] == english_country]
        else:
            df_country = df
            
        pattern = r'\b' + re.escape(jugador_db) + r'\b'
        matches = df_country[df_country['long_name_lower'].str.contains(pattern, na=False, regex=True) |
                             df_country['short_name_lower'].str.contains(pattern, na=False, regex=True)]
        
        if len(matches) == 0:
            words = [w for w in re.split(r'[^a-zA-Z0-9]', jugador_db) if len(w) > 1]
            if words:
                mask = df_country['long_name_lower'].apply(lambda name: all(w in name for w in words))
                matches = df_country[mask]
                
        if len(matches) == 0 and english_country is not None:
            matches = df[df['long_name_lower'].str.contains(pattern, na=False, regex=True) |
                         df['short_name_lower'].str.contains(pattern, na=False, regex=True)]
            
            if len(matches) == 0:
                words = [w for w in re.split(r'[^a-zA-Z0-9]', jugador_db) if len(w) > 1]
                if words:
                    mask = df['long_name_lower'].apply(lambda name: all(w in name for w in words))
                    matches = df[mask]
                    
            if len(matches) == 0:
                words = [w for w in re.split(r'[^a-zA-Z0-9]', jugador_db) if len(w) > 1]
                if words:
                    mask = df['short_name_lower'].apply(lambda name: all(w in name for w in words))
                    matches = df[mask]
                    
        if len(matches) == 0:
            missing.append((pais_db_raw, jugador_db_raw, equipo_db_raw))
            
    with open("scratch/missing_fifa_players.txt", "w", encoding="utf-8") as f:
        f.write(f"Total de convocados no mapeados en FIFA: {len(missing)}\n\n")
        current_country = None
        for country, name, club in sorted(missing, key=lambda x: (x[0], x[1])):
            if country != current_country:
                f.write(f"\n=== {country} ===\n")
                current_country = country
            f.write(f"- {name} ({club})\n")
            
    print("Reporte escrito en scratch/missing_fifa_players.txt")

if __name__ == "__main__":
    main()
