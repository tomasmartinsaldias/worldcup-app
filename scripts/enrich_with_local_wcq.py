import os
import sqlite3
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
    ranking_path = os.path.join(base_dir, "data", "ranking_fifa.txt")
    wcq_dir = os.path.join(base_dir, "data", "eliminatorias-2026")
    
    if not os.path.exists(db_path):
        print(f"Error: No se encontró la base de datos en {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Crear columnas si no existen
    print("Verificando/creando columnas en scraped_team_metrics...")
    add_column_if_not_exists(cursor, "scraped_team_metrics", "fifa_ranking", "INTEGER")
    add_column_if_not_exists(cursor, "scraped_team_metrics", "gnp_per_90", "REAL")
    add_column_if_not_exists(cursor, "scraped_team_metrics", "gc_per_90", "REAL")
    add_column_if_not_exists(cursor, "scraped_team_metrics", "drama_per_90", "REAL")
    conn.commit()
    
    # 2. Cargar mapeo de equipos para relacionar nombres de FBref con código FIFA
    cursor.execute("SELECT fifa_code, wc2026_name, historical_name, intl_results_name FROM team_mappings;")
    name_to_code = {}
    for code, wc, hist, intl in cursor.fetchall():
        candidates = set()
        if wc: candidates.add(normalize_name(wc))
        if hist: candidates.add(normalize_name(hist))
        if intl: candidates.add(normalize_name(intl))
        
        # Mapeos específicos manuales
        if code == 'USA': candidates.update(['usa', 'united states', 'us'])
        elif code == 'MEX': candidates.update(['mexico', 'mex'])
        elif code == 'CAN': candidates.update(['canada', 'can'])
        elif code == 'IRN': candidates.update(['ir iran', 'iran', 'irn'])
        elif code == 'KOR': candidates.update(['korea republic', 'south korea', 'korea', 'kor'])
        elif code == 'CIV': candidates.update(["côte d'ivoire", "cote d'ivoire", "ivory coast", "civ"])
        elif code == 'COD': candidates.update(["congo dr", "dr congo", "cod"])
        elif code == 'TUR': candidates.update(["türkiye", "turkey", "tur"])
        elif code == 'CZE': candidates.update(["czechia", "czech republic", "cze"])
        
        for cand in candidates:
            if cand:
                name_to_code[cand] = code
                
    # 3. Parsear ranking_fifa.txt
    print(f"Procesando {ranking_path}...")
    fifa_rankings = {}
    if os.path.exists(ranking_path):
        with open(ranking_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    try:
                        # Extraer número de ranking (ej: '1  ' o '13  ')
                        rank_str = parts[0].strip()
                        rank_val = int(rank_str)
                        
                        # Extraer nombre de la nación (ej: 'France France' o 'Argentina Argentina')
                        nation_raw = parts[1].strip()
                        # Quitar duplicación si la tiene (ej: 'France France' -> 'France')
                        nation_words = nation_raw.split()
                        if len(nation_words) >= 2 and nation_words[0] == nation_words[1]:
                            nation_name = nation_words[0]
                        else:
                            nation_name = nation_raw
                            
                        norm_nation = normalize_name(nation_name)
                        code = name_to_code.get(norm_nation)
                        if code:
                            fifa_rankings[code] = rank_val
                        else:
                            # Buscar por palabras
                            for k, v in name_to_code.items():
                                if norm_nation in k or k in norm_nation:
                                    fifa_rankings[v] = rank_val
                                    break
                    except ValueError:
                        continue
        print(f"  Rankings FIFA cargados: {len(fifa_rankings)} selecciones.")
    else:
        print("  Advertencia: No se encontró ranking_fifa.txt.")
        
    # 4. Parsear archivos de estadísticas
    stats_data = {}
    print(f"Procesando estadísticas de Eliminatorias y Copa Oro en {wcq_dir}...")
    
    for filename in os.listdir(wcq_dir):
        if filename.startswith("Squad Standard Stats") and filename.endswith(".txt"):
            filepath = os.path.join(wcq_dir, filename)
            print(f"  Procesando archivo: {filename}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line in lines:
                if not line.strip() or line.startswith('Squad') or line.startswith('\t') or line.startswith(' '):
                    continue
                parts = line.strip().split('\t')
                if len(parts) < 16:
                    continue
                    
                squad_col = parts[0]
                # Separar prefijo y nombre de equipo (ej: 'ca Canada' -> 'ca', 'Canada')
                squad_parts = squad_col.split(' ', 1)
                if len(squad_parts) < 2:
                    continue
                
                team_name_raw = squad_parts[1].strip()
                is_opponent = False
                if team_name_raw.startswith("vs "):
                    is_opponent = True
                    team_name_raw = team_name_raw[3:].strip()
                    
                norm_team = normalize_name(team_name_raw)
                code = name_to_code.get(norm_team)
                if not code:
                    continue
                    
                # Extraer métricas numéricas básicas
                def get_val(idx, default=0.0):
                    try:
                        val_str = parts[idx].replace(',', '').strip()
                        return float(val_str)
                    except (ValueError, IndexError):
                        return default
                        
                if code not in stats_data:
                    stats_data[code] = {
                        'team': {'90s': 1.0, 'G-PK': 0.0, 'PKatt': 0.0, 'CrdY': 0.0, 'CrdR': 0.0},
                        'opp': {'Gls': 0.0, 'PKatt': 0.0, 'CrdY': 0.0, 'CrdR': 0.0}
                    }
                    
                if not is_opponent:
                    stats_data[code]['team']['90s'] = get_val(7, 1.0)
                    stats_data[code]['team']['G-PK'] = get_val(11, 0.0)
                    stats_data[code]['team']['PKatt'] = get_val(13, 0.0)
                    stats_data[code]['team']['CrdY'] = get_val(14, 0.0)
                    stats_data[code]['team']['CrdR'] = get_val(15, 0.0)
                else:
                    stats_data[code]['opp']['Gls'] = get_val(8, 0.0)
                    stats_data[code]['opp']['PKatt'] = get_val(13, 0.0)
                    stats_data[code]['opp']['CrdY'] = get_val(14, 0.0)
                    stats_data[code]['opp']['CrdR'] = get_val(15, 0.0)

    # 5. Calcular métricas finales ICE y actualizar SQLite
    print("Calculando y guardando métricas en la base de datos...")
    
    # Asegurar que existan registros en scraped_team_metrics para todos los equipos
    cursor.execute("SELECT fifa_code FROM wc2026_teams WHERE is_placeholder = 0;")
    for (code,) in cursor.fetchall():
        cursor.execute("INSERT OR IGNORE INTO scraped_team_metrics (fifa_code) VALUES (?);", (code,))
    conn.commit()
    
    updated_count = 0
    for code, data in stats_data.items():
        nineties = data['team']['90s']
        if nineties <= 0:
            nineties = 1.0
            
        gnp_90 = round(data['team']['G-PK'] / nineties, 3)
        gc_90 = round(data['opp']['Gls'] / nineties, 3)
        
        # Tarjetas totales + penaltis totales de ambos en sus partidos por 90 minutos
        total_cards = data['team']['CrdY'] + data['team']['CrdR'] + data['opp']['CrdY'] + data['opp']['CrdR']
        total_penalties = data['team']['PKatt'] + data['opp']['PKatt']
        drama_90 = round((total_cards + total_penalties) / nineties, 3)
        
        # FIFA ranking
        rank = fifa_rankings.get(code)
        
        # Guardar en BD
        cursor.execute("""
            UPDATE scraped_team_metrics
            SET gnp_per_90 = ?,
                gc_per_90 = ?,
                drama_per_90 = ?,
                fifa_ranking = COALESCE(?, fifa_ranking)
            WHERE fifa_code = ?;
        """, (gnp_90, gc_90, drama_90, rank, code))
        updated_count += 1

    # Adicionalmente, actualizar ranking para equipos que tienen ranking pero no jugaron eliminatorias (si los hubiera)
    for code, rank in fifa_rankings.items():
        cursor.execute("""
            UPDATE scraped_team_metrics
            SET fifa_ranking = ?
            WHERE fifa_code = ?;
        """, (rank, code))
        
    conn.commit()
    conn.close()
    
    print(f"¡Base de datos enriquecida con éxito! Se actualizaron {updated_count} selecciones con métricas WCQ/Gold Cup.")

if __name__ == "__main__":
    main()
