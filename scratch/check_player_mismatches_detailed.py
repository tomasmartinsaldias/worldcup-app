import os
import sqlite3
import pandas as pd
import unicodedata
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def clean_name_for_regex(text):
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    # Normalize/decompose diacritics
    text = unicodedata.normalize('NFD', text)
    # Reemplazar cualquier caracter que no sea a-z o espacio con un punto (.) para regex
    cleaned = []
    for c in text:
        if 'a' <= c <= 'z' or c == ' ':
            cleaned.append(c)
        elif c in ['?', '\ufffd', '']:
            cleaned.append('.')
        else:
            # any other symbol / accent marks that are not combined can be treated as wildcard
            # unless it's a combining diacritic (which unicodedata NFD separates)
            if unicodedata.category(c) != 'Mn':
                cleaned.append('.')
    res = "".join(cleaned)
    # Collapse multiple spaces
    res = " ".join(res.split())
    return res

def main():
    base_dir = "c:/Users/tomas/Desktop/proyectos/worldcup-app"
    csv_path = os.path.join(base_dir, "data", "worldcup-2026-predicts", "fifa_world_cup_2026_golden_dataset.csv")
    db_path = os.path.join(base_dir, "data", "worldcup_combined.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    df = pd.read_csv(csv_path)
    csv_by_team = {}
    for idx, row in df.iterrows():
        team = row['team_name']
        if team not in csv_by_team:
            csv_by_team[team] = []
        csv_by_team[team].append(row)
        
    cursor.execute("""
        SELECT player_id, player_name, fifa_code, position
        FROM scraped_wc2026_probable_squads;
    """)
    db_players = cursor.fetchall()
    
    cursor.execute("SELECT fifa_code, wc2026_name, historical_name, intl_results_name FROM team_mappings;")
    fifa_to_csv_teams = {}
    for code, wc, hist, intl in cursor.fetchall():
        candidates = set()
        if wc: candidates.add(wc)
        if hist: candidates.add(hist)
        if intl: candidates.add(intl)
        if code == 'IRN': candidates.update(['IR Iran', 'Iran'])
        elif code == 'KOR': candidates.update(['Korea Republic', 'South Korea'])
        elif code == 'CUR': candidates.update(['Curaçao', 'Curacao'])
        elif code == 'CIV': candidates.update(["Côte d'Ivoire", "Cote d'Ivoire", "Ivory Coast"])
        elif code == 'COD': candidates.update(["Congo DR", "DR Congo"])
        elif code == 'TUR': candidates.update(["Türkiye", "Turkey"])
        fifa_to_csv_teams[code] = list(candidates)
        
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
    
    matched_count = 0
    mismatches = []
    
    for pid, db_name, fifa_code, position in db_players:
        possible_teams = fifa_to_csv_teams.get(fifa_code, [fifa_code])
        csv_candidates = []
        for t in possible_teams:
            if t in csv_by_team:
                csv_candidates.extend(csv_by_team[t])
                
        # Normalizaciones para comparar
        reg_db = clean_name_for_regex(db_name)
        
        # 1. Intentar coincidencia directa o con regex
        matched_cand = None
        for cand in csv_candidates:
            reg_cand = clean_name_for_regex(cand['name'])
            
            # Check if they match directly or via regex
            # Si uno tiene comodines '.', los usamos como regex
            try:
                # Reemplazar '.' con '\.' y luego los '.' de comodines con '.'
                # O simplemente compilar como regex convirtiendo '.' a '.' y escapando el resto.
                # Como clean_name_for_regex ya limpia todo salvo a-z, espacio y '.', podemos usar '.' directamente.
                # Pero ojo, si hay un '.', en regex coincide con cualquier cosa, que es lo que queremos.
                # Para evitar problemas con ^ y $, hacemos anclaje total.
                pattern_cand = "^" + reg_cand + "$"
                pattern_db = "^" + reg_db + "$"
                
                # Intentar cruzar en ambas direcciones
                if re.match(pattern_cand, reg_db) or re.match(pattern_db, reg_cand):
                    matched_cand = cand
                    break
            except Exception:
                pass
                
        if matched_cand is not None:
            matched_count += 1
            # print(f"MATCHED: '{db_name}' -> '{matched_cand['name']}' ({fifa_code})")
            continue
            
        # 2. Intentar nickname matching
        # Si un token del DB name tiene un nickname que coincide con el CSV name
        db_tokens = set(reg_db.replace('.', ' ').split())
        for cand in csv_candidates:
            reg_cand = clean_name_for_regex(cand['name'])
            cand_tokens = set(reg_cand.replace('.', ' ').split())
            
            # Check if any token has a nickname mapping to the other
            nick_matched = False
            for t1 in db_tokens:
                if t1 in nickname_map:
                    mapped = nickname_map[t1]
                    # Si al reemplazar t1 por mapped coinciden más tokens
                    mod_db_tokens = (db_tokens - {t1}) | {mapped}
                    if len(mod_db_tokens.intersection(cand_tokens)) >= 2 or (len(mod_db_tokens) == 1 and mod_db_tokens == cand_tokens):
                        nick_matched = True
                        break
                        
            if nick_matched:
                matched_cand = cand
                break
                
        if matched_cand is not None:
            matched_count += 1
            print(f"MATCHED (NICKNAME): '{db_name}' -> '{matched_cand['name']}' ({fifa_code})")
            continue
            
        # 3. Intentar Jaccard matching con threshold >= 0.49
        best_cand = None
        best_score = 0.0
        for cand in csv_candidates:
            reg_cand = clean_name_for_regex(cand['name'])
            # Quitar puntos para tokenizar
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
                
        if best_cand is not None and best_score >= 0.49:
            matched_count += 1
            print(f"MATCHED (JACCARD={best_score:.2f}): '{db_name}' -> '{best_cand['name']}' ({fifa_code})")
            continue
            
        mismatches.append((db_name, fifa_code))
        
    print(f"\nTotal matched: {matched_count}")
    print(f"Total unmatched: {len(mismatches)}")
    print(f"Sample unmatched (first 20):")
    for db_n, code in mismatches[:20]:
        print(f"  '{db_n}' ({code})")
        
    conn.close()

if __name__ == '__main__':
    main()
