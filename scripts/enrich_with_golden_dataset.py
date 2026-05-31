import os
import re
import json
import sqlite3
import urllib.parse
import unicodedata
import pandas as pd
import requests

def normalize_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    # Reemplazar el signo de pregunta roto por 'i' (la mayoría de los "?" en este dataset son "í", "ı", "ö", "ü", etc.)
    text = text.replace("?", "i")
    # Mapear caracteres específicos a sus contrapartes ASCII básicas
    char_map = {
        'ı': 'i', 'ğ': 'g', 'ş': 's', 'ç': 'c', 'ö': 'o', 'ü': 'u',
        'ñ': 'n', 'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ã': 'a', 'õ': 'o', 'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
    }
    for k, v in char_map.items():
        text = text.replace(k, v)
    # Normalizar diacríticos restantes
    text = unicodedata.normalize('NFD', text)
    # Conservar solo caracteres alfabéticos a-z y espacios
    text = "".join([c for c in text if 'a' <= c <= 'z' or c == ' '])
    text = " ".join(text.split())
    return text

def clean_for_api_search(name):
    if not isinstance(name, str):
        return ""
    name = name.replace("?", "i")
    char_map = {
        'ı': 'i', 'ğ': 'g', 'ş': 's', 'ç': 'c', 'ö': 'o', 'ü': 'u',
        'İ': 'I', 'Ğ': 'G', 'Ş': 'S', 'Ç': 'C', 'Ö': 'O', 'Ü': 'U',
        'ñ': 'n', 'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ã': 'a', 'õ': 'o', 'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
    }
    for k, v in char_map.items():
        name = name.replace(k, v)
    name = re.sub(r'[^a-zA-Z0-9\s\-]', '', name)
    return " ".join(name.split())

def clean_name_for_regex(text):
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    # Normalize and decompose diacritics
    text = unicodedata.normalize('NFD', text)
    cleaned = []
    for c in text:
        if 'a' <= c <= 'z' or c == ' ':
            cleaned.append(c)
        elif c in ['?', '\ufffd', '']:
            cleaned.append('.')
        else:
            # Treats other non-combining characters as wildcard
            if unicodedata.category(c) != 'Mn':
                cleaned.append('.')
    res = "".join(cleaned)
    return " ".join(res.split())

nationality_keywords = {
    'ARG': ['Argentina'], 'BRA': ['Brazil'], 'FRA': ['France'], 'ENG': ['England'], 
    'ESP': ['Spain'], 'GER': ['Germany'], 'POR': ['Portugal'], 'URU': ['Uruguay'], 
    'NED': ['Netherlands'], 'CRO': ['Croatia'], 'JPN': ['Japan'], 
    'USA': ['United States', 'US'], 'MEX': ['Mexico'], 'MAR': ['Morocco'], 
    'COL': ['Colombia'], 'BEL': ['Belgium'], 'NOR': ['Norway'], 'SEN': ['Senegal'], 
    'EGY': ['Egypt'], 'SWE': ['Sweden'], 'KOR': ['Korea, South', 'South Korea', 'Korea'], 
    'TUR': ['Turkey', 'Türkiye'], 'SUI': ['Switzerland'], 'CAN': ['Canada'], 'ECU': ['Ecuador'], 
    'AUT': ['Austria'], 'ALG': ['Algeria'], 'CIV': ['Cote d\'Ivoire', 'Ivory Coast', 'Côte d\'Ivoire'], 
    'SCO': ['Scotland'], 'AUS': ['Australia'], 'GHA': ['Ghana'], 'KSA': ['Saudi Arabia'], 
    'PAR': ['Paraguay'], 'CZE': ['Czech Republic', 'Czechia'], 'COD': ['DR Congo', 'Congo, Democratic Republic'], 
    'BIH': ['Bosnia-Herzegovina', 'Bosnia'], 'CPV': ['Cape Verde', 'Cabo Verde'], 'TUN': ['Tunisia'], 
    'IRQ': ['Iraq'], 'RSA': ['South Africa'], 'UZB': ['Uzbekistan'], 'QAT': ['Qatar'], 
    'NZL': ['New Zealand'], 'JOR': ['Jordan'], 'PAN': ['Panama'], 'HAI': ['Haiti'], 
    'CUR': ['Curacao', 'Curaçao'], 'IRN': ['Iran']
}


def add_column_if_not_exists(cursor, table, col, col_type):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type};")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            pass
        else:
            raise e

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "data", "worldcup-2026-predicts", "fifa_world_cup_2026_golden_dataset.csv")
    db_path = os.path.join(base_dir, "data", "worldcup_combined.db")
    
    if not os.path.exists(csv_path):
        print(f"Error: No se encontró el CSV en {csv_path}")
        return
    if not os.path.exists(db_path):
        print(f"Error: No se encontró la BD en {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Crear columnas si no existen
    add_column_if_not_exists(cursor, "scraped_wc2026_probable_squads", "assists_recent", "INTEGER")
    add_column_if_not_exists(cursor, "scraped_wc2026_probable_squads", "minutes_recent", "INTEGER")
    add_column_if_not_exists(cursor, "scraped_wc2026_probable_squads", "efficiency_score", "REAL")
    add_column_if_not_exists(cursor, "scraped_team_metrics", "efficiency_score_avg", "REAL")
    conn.commit()
    
    # 2. Leer CSV y agrupar por team_name
    df = pd.read_csv(csv_path)
    csv_by_team = {}
    for idx, row in df.iterrows():
        team = row['team_name']
        if team not in csv_by_team:
            csv_by_team[team] = []
        csv_by_team[team].append({
            'idx': idx,
            'name': row['name'],
            'appearances': int(row['appearances']),
            'goals': int(row['goals']),
            'assists': int(row['assists']),
            'minutes': int(row['minutes']),
            'efficiency_score': float(row['efficiency_score'])
        })
        
    # Obtener mapeo de códigos FIFA a nombres del CSV
    cursor.execute("SELECT fifa_code, wc2026_name, historical_name, intl_results_name FROM team_mappings;")
    fifa_to_csv_teams = {}
    for code, wc, hist, intl in cursor.fetchall():
        candidates = set()
        if wc: candidates.add(wc)
        if hist: candidates.add(hist)
        if intl: candidates.add(intl)
        if code == 'IRN': candidates.update(['IR Iran', 'Iran'])
        elif code == 'KOR': candidates.update(['Korea Republic', 'South Korea'])
        elif code == 'CUR': candidates.update(['Curaçao', 'Curacao', 'Cura?ao'])
        elif code == 'CIV': candidates.update(["Côte d'Ivoire", "Cote d'Ivoire", "Ivory Coast", "C?te d'Ivoire"])
        elif code == 'COD': candidates.update(["Congo DR", "DR Congo"])
        elif code == 'TUR': candidates.update(["Türkiye", "Turkey", "T?rkiye", "Trkiye"])
        fifa_to_csv_teams[code] = list(candidates)
            
    # 3. Cargar todos los jugadores de la BD
    cursor.execute("""
        SELECT player_id, player_name, fifa_code, position, club, age, caps, goals, market_value_eur
        FROM scraped_wc2026_probable_squads;
    """)
    db_rows = cursor.fetchall()
    
    print(f"Enriqueciendo jugadores en BD (normalización robusta con regex y apodos)...")
    
    nickname_map = {
        'andy': 'andrew',
        'andrew': 'andy',
        'alex': 'alejandro',
        'alejandro': 'alex',
        'nacho': 'ignacio',
        'ignacio': 'nacho',
        'memo': 'guillermo',
        'guillermo': 'memo',
        'chicharito': 'javier',
        'javier': 'chicharito',
        'dibu': 'emiliano',
        'emiliano': 'dibu',
        'pepe': 'kepler',
        'kepler': 'pepe',
        'koke': 'jorge',
        'jorge': 'koke',
        'gavi': 'pablo',
        'pablo': 'gavi',
        'manu': 'manuel',
        'manuel': 'manu',
        'nico': 'nicolas',
        'nicolas': 'nico',
        'fred': 'frederico',
        'frederico': 'fred',
        'richy': 'richard',
        'richard': 'richy',
    }
    
    matched_csv_indices = set()
    rescued_count = 0
    matched_count = 0
    
    for row in db_rows:
        pid, db_name, fifa_code, pos, club, age, caps, goals, mval = row
        
        possible_teams = fifa_to_csv_teams.get(fifa_code, [fifa_code])
        csv_candidates = []
        for t in possible_teams:
            if t in csv_by_team:
                csv_candidates.extend(csv_by_team[t])
                
        # Intentar coincidencia exacta o regex
        reg_db = clean_name_for_regex(db_name)
        csv_match = None
        
        # A. Intentar coincidencia exacta/regex
        for cand in csv_candidates:
            if cand['idx'] in matched_csv_indices:
                continue
            reg_cand = clean_name_for_regex(cand['name'])
            try:
                pattern_cand = "^" + reg_cand + "$"
                pattern_db = "^" + reg_db + "$"
                if re.match(pattern_cand, reg_db) or re.match(pattern_db, reg_cand):
                    csv_match = cand
                    break
            except Exception:
                pass
                
        # B. Intentar coincidencia de apodo (nickname)
        if not csv_match:
            db_tokens = set(reg_db.replace('.', ' ').split())
            for cand in csv_candidates:
                if cand['idx'] in matched_csv_indices:
                    continue
                reg_cand = clean_name_for_regex(cand['name'])
                cand_tokens = set(reg_cand.replace('.', ' ').split())
                
                nick_matched = False
                for t1 in db_tokens:
                    if t1 in nickname_map:
                        mapped = nickname_map[t1]
                        mod_db_tokens = (db_tokens - {t1}) | {mapped}
                        if len(mod_db_tokens.intersection(cand_tokens)) >= 2 or (len(mod_db_tokens) == 1 and mod_db_tokens == cand_tokens):
                            nick_matched = True
                            break
                if nick_matched:
                    csv_match = cand
                    break
                    
        # C. Intentar Jaccard >= 0.49
        if not csv_match:
            best_cand = None
            best_score = 0.0
            for cand in csv_candidates:
                if cand['idx'] in matched_csv_indices:
                    continue
                reg_cand = clean_name_for_regex(cand['name'])
                t_db = set(reg_db.replace('.', ' ').split())
                t_cand = set(reg_cand.replace('.', ' ').split())
                if not t_db or not t_cand:
                    continue
                inter = t_db.intersection(t_cand)
                union = t_db.union(t_cand)
                jaccard = len(inter) / len(union)
                if jaccard > best_score:
                    best_score = jaccard
                    best_cand = cand
            if best_cand and best_score >= 0.49:
                csv_match = best_cand
                
        if csv_match:
            matched_csv_indices.add(csv_match['idx'])
            matched_count += 1
            # Actualizar estadísticas de rendimiento reciente
            cursor.execute("""
                UPDATE scraped_wc2026_probable_squads
                SET assists_recent = ?, minutes_recent = ?, efficiency_score = ?
                WHERE player_id = ?;
            """, (csv_match['assists'], csv_match['minutes'], csv_match['efficiency_score'], pid))
            
        # El bloque de API lookup fallback ha sido removido para optimizar velocidad, 
        # dado que los valores de mercado generales provienen de ranking_fifa.txt.
        pass
    conn.commit()
    print(f"\nProceso completado. Jugadores coincidentes en CSV: {matched_count}.")
    
    # 4. Calcular y actualizar el promedio de efficiency_score para cada selección
    print("\nCalculando promedios de efficiency_score por selección...")
    cursor.execute("""
        SELECT fifa_code, AVG(efficiency_score)
        FROM scraped_wc2026_probable_squads
        WHERE efficiency_score IS NOT NULL
        GROUP BY fifa_code;
    """)
    team_avgs = cursor.fetchall()
    
    for code, avg in team_avgs:
        if avg is not None:
            cursor.execute("""
                UPDATE scraped_team_metrics
                SET efficiency_score_avg = ?
                WHERE fifa_code = ?;
            """, (round(avg, 3), code))
            
    conn.commit()
    print("Promedios de eficiencia de selecciones actualizados con éxito.")
    conn.close()

if __name__ == "__main__":
    main()
