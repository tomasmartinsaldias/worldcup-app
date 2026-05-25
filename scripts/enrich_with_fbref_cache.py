import os
import sqlite3
import pandas as pd
import unicodedata

def normalize_name(text):
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = text.replace("?", "i")
    char_map = {
        'ı': 'i', 'ğ': 'g', 'ş': 's', 'ç': 'c', 'ö': 'o', 'ü': 'u',
        'ñ': 'n', 'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ã': 'a', 'õ': 'o', 'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
    }
    for k, v in char_map.items():
        text = text.replace(k, v)
    text = unicodedata.normalize('NFD', text)
    text = "".join([c for c in text if 'a' <= c <= 'z' or c == ' '])
    text = " ".join(text.split())
    return text

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
    db_path = os.path.join(base_dir, "data", "worldcup_combined.db")
    csv_path = os.path.join(base_dir, "data", "fbref_qualifiers_cache.csv")
    
    if not os.path.exists(db_path):
        print(f"Error: No se encontró la base de datos en {db_path}")
        return
    if not os.path.exists(csv_path):
        print(f"Error: No se encontró el caché de clasificatorias en {csv_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Agregar columnas a scraped_wc2026_probable_squads si no existen
    add_column_if_not_exists(cursor, "scraped_wc2026_probable_squads", "xG_intl", "REAL")
    add_column_if_not_exists(cursor, "scraped_wc2026_probable_squads", "sca_intl", "INTEGER")
    add_column_if_not_exists(cursor, "scraped_wc2026_probable_squads", "gca_intl", "INTEGER")
    add_column_if_not_exists(cursor, "scraped_wc2026_probable_squads", "progressive_passes_intl", "INTEGER")
    add_column_if_not_exists(cursor, "scraped_wc2026_probable_squads", "progressive_carries_intl", "INTEGER")
    conn.commit()
    
    # 2. Cargar mapeo de nombres de equipos
    cursor.execute("SELECT fifa_code, wc2026_name, historical_name, intl_results_name FROM team_mappings;")
    fifa_to_csv_teams = {}
    for code, wc, hist, intl in cursor.fetchall():
        candidates = set()
        if wc: candidates.add(wc.lower())
        if hist: candidates.add(hist.lower())
        if intl: candidates.add(intl.lower())
        if code == 'IRN': candidates.update(['ir iran', 'iran'])
        elif code == 'KOR': candidates.update(['korea republic', 'south korea'])
        elif code == 'CUR': candidates.update(['curaçao', 'curacao'])
        elif code == 'CIV': candidates.update(["côte d'ivoire", "cote d'ivoire", "ivory coast"])
        elif code == 'COD': candidates.update(["congo dr", "dr congo"])
        elif code == 'TUR': candidates.update(["türkiye", "turkey"])
        fifa_to_csv_teams[code] = list(candidates)
        
    # 3. Leer CSV de FBref
    print(f"Cargando estadísticas de FBref desde {csv_path}...")
    df = pd.read_csv(csv_path)
    df['norm_player'] = df['Player'].apply(normalize_name)
    df['norm_squad'] = df['Squad'].apply(lambda x: x.lower().strip() if isinstance(x, str) else "")
    
    # Organizar el CSV por Squad
    csv_by_squad = {}
    for idx, row in df.iterrows():
        sq = row['norm_squad']
        if sq not in csv_by_squad:
            csv_by_squad[sq] = []
        csv_by_squad[sq].append(row)
        
    # 4. Cargar todos los jugadores de la BD
    cursor.execute("SELECT player_id, player_name, fifa_code FROM scraped_wc2026_probable_squads;")
    players = cursor.fetchall()
    
    matched_count = 0
    print("Enriqueciendo jugadores en base de datos con estadísticas avanzadas de clasificatorias...")
    
    for pid, name, fifa_code in players:
        norm_name = normalize_name(name)
        possible_squads = fifa_to_csv_teams.get(fifa_code, [])
        
        # Buscar en el CSV
        csv_rows = []
        for sq in possible_squads:
            if sq in csv_by_squad:
                csv_rows.extend(csv_by_squad[sq])
                
        # Buscar mejor coincidencia
        best_row = None
        best_score = 0.0
        
        for row in csv_rows:
            norm_c_player = row['norm_player']
            if norm_name == norm_c_player:
                best_row = row
                break
                
            # Jaccard token overlap
            tokens_p = set(norm_name.split())
            tokens_c = set(norm_c_player.split())
            if tokens_p and tokens_c:
                inter = tokens_p.intersection(tokens_c)
                union = tokens_p.union(tokens_c)
                jaccard = len(inter) / len(union)
                if jaccard > best_score:
                    best_score = jaccard
                    best_row = row
                    
        if best_row is not None and (best_row['norm_player'] == norm_name or best_score >= 0.49):
            matched_count += 1
            
            # Obtener métricas
            def get_float(val):
                if pd.isna(val) or val == "":
                    return None
                try:
                    return float(val)
                except ValueError:
                    return None
                    
            def get_int(val):
                if pd.isna(val) or val == "":
                    return None
                try:
                    return int(float(val))
                except ValueError:
                    return None
                    
            xg = get_float(best_row.get('xG'))
            sca = get_int(best_row.get('sca'))
            gca = get_int(best_row.get('gca'))
            pp = get_int(best_row.get('progressive_passes'))
            pc = get_int(best_row.get('progressive_carries'))
            
            # Actualizar BD
            cursor.execute("""
                UPDATE scraped_wc2026_probable_squads
                SET xG_intl = ?,
                    sca_intl = ?,
                    gca_intl = ?,
                    progressive_passes_intl = ?,
                    progressive_carries_intl = ?
                WHERE player_id = ?;
            """, (xg, sca, gca, pp, pc, pid))
            
    conn.commit()
    conn.close()
    
    print(f"\n--- Enriquecimiento con Métricas de FBref Completado ---")
    print(f"Jugadores cruzados y enriquecidos exitosamente: {matched_count} de {len(players)}")

if __name__ == "__main__":
    main()
