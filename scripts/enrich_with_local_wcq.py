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
        
        if code == 'USA': candidates.update([normalize_name(x) for x in ['usa', 'united states', 'us']])
        elif code == 'MEX': candidates.update([normalize_name(x) for x in ['mexico', 'mex']])
        elif code == 'CAN': candidates.update([normalize_name(x) for x in ['canada', 'can']])
        elif code == 'IRN': candidates.update([normalize_name(x) for x in ['ir iran', 'iran', 'irn']])
        elif code == 'KOR': candidates.update([normalize_name(x) for x in ['korea republic', 'south korea', 'korea', 'kor']])
        elif code == 'CIV': candidates.update([normalize_name(x) for x in ["côte d'ivoire", "cote d'ivoire", "ivory coast", "civ"]])
        elif code == 'COD': candidates.update([normalize_name(x) for x in ["congo dr", "dr congo", "cod"]])
        elif code == 'TUR': candidates.update([normalize_name(x) for x in ["türkiye", "turkey", "tur"]])
        elif code == 'CZE': candidates.update([normalize_name(x) for x in ["czechia", "czech republic", "cze"]])
        elif code == 'BIH': candidates.update([normalize_name(x) for x in ["bosnia", "herzegovina", "bosnia and herzegovina", "bosnia-herzegovina"]])
        
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
                        
                        nation_raw = parts[1].strip()
                        # Quitar duplicación si la tiene (ej: 'France France' -> 'France')
                        nation_words = nation_raw.split()
                        half_len = len(nation_words) // 2
                        if len(nation_words) >= 2 and half_len > 0 and nation_words[:half_len] == nation_words[half_len:]:
                            nation_name = " ".join(nation_words[:half_len])
                        else:
                            nation_name = nation_raw
                            
                        norm_nation = normalize_name(nation_name)
                        code = name_to_code.get(norm_nation)
                        if code:
                            if code not in fifa_rankings:
                                fifa_rankings[code] = rank_val
                        else:
                            matched = False
                            for k, v in name_to_code.items():
                                if len(k) <= 3:
                                    continue
                                if norm_nation in k or k in norm_nation:
                                    if v not in fifa_rankings:
                                        fifa_rankings[v] = rank_val
                                    matched = True
                                    break
                            if not matched:
                                for token in norm_nation.split():
                                    if token in name_to_code:
                                        code_token = name_to_code[token]
                                        if code_token not in fifa_rankings:
                                            fifa_rankings[code_token] = rank_val
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
                    
                def get_val(idx, default=0.0):
                    try:
                        val_str = parts[idx].replace(',', '').strip()
                        return float(val_str)
                    except (ValueError, IndexError):
                        return default
                        
                if code not in stats_data:
                    stats_data[code] = {
                        'team': {'MP': 1.0, '90s': 1.0, 'G-PK': 0.0, 'PKatt': 0.0, 'CrdY': 0.0, 'CrdR': 0.0, 'Poss': None},  # None = no data
                        'opp': {'Gls': 0.0, 'PKatt': 0.0, 'CrdY': 0.0, 'CrdR': 0.0},
                        'has_team_stats': False
                    }
                    
                if not is_opponent:
                    stats_data[code]['team']['MP'] = get_val(4, 1.0)
                    stats_data[code]['team']['90s'] = get_val(7, 1.0)
                    stats_data[code]['team']['G-PK'] = get_val(11, 0.0)
                    stats_data[code]['team']['PKatt'] = get_val(13, 0.0)
                    stats_data[code]['team']['CrdY'] = get_val(14, 0.0)
                    stats_data[code]['team']['CrdR'] = get_val(15, 0.0)
                    stats_data[code]['has_team_stats'] = True
                    # Read Poss only if the value is actually numeric; never use 50.0 as fallback
                    try:
                        poss_str = parts[3].replace(',', '').strip()
                        stats_data[code]['team']['Poss'] = float(poss_str) if poss_str else None
                    except (ValueError, IndexError):
                        stats_data[code]['team']['Poss'] = None  # No data → NULL in DB
                else:
                    stats_data[code]['opp']['Gls'] = get_val(8, 0.0)
                    stats_data[code]['opp']['PKatt'] = get_val(13, 0.0)
                    stats_data[code]['opp']['CrdY'] = get_val(14, 0.0)
                    stats_data[code]['opp']['CrdR'] = get_val(15, 0.0)

    # 5. Calcular métricas finales ICE y actualizar SQLite
    print("Calculando y guardando métricas de selecciones en la base de datos...")
    
    cursor.execute("SELECT fifa_code FROM wc2026_teams WHERE is_placeholder = 0;")
    for (code,) in cursor.fetchall():
        cursor.execute("INSERT OR IGNORE INTO scraped_team_metrics (fifa_code) VALUES (?);", (code,))
    conn.commit()
    
    updated_count = 0
    for code, data in stats_data.items():
        if not data.get('has_team_stats'):
            continue
            
        nineties = data['team']['90s']
        if nineties <= 0:
            nineties = 1.0
            
        gnp_90 = round(data['team']['G-PK'] / nineties, 3)
        gc_90 = round(data['opp']['Gls'] / nineties, 3)
        
        total_cards = data['team']['CrdY'] + data['team']['CrdR'] + data['opp']['CrdY'] + data['opp']['CrdR']
        total_penalties = data['team']['PKatt'] + data['opp']['PKatt']
        drama_90 = round((total_cards + total_penalties) / nineties, 3)
        
        mp = data['team']['MP']
        if mp <= 0:
            mp = 1.0
        cards_per_match = round((data['team']['CrdY'] + data['team']['CrdR']) / mp, 3)
        poss = data['team']['Poss']
        
        rank = fifa_rankings.get(code)
        
        cursor.execute("""
            UPDATE scraped_team_metrics
            SET gnp_per_90 = ?,
                gc_per_90 = ?,
                drama_per_90 = ?,
                cards_per_match_avg = ?,
                recent_possession_avg = COALESCE(?, recent_possession_avg),
                fifa_ranking = COALESCE(?, fifa_ranking)
            WHERE fifa_code = ?;
        """, (gnp_90, gc_90, drama_90, cards_per_match, poss, rank, code))
        updated_count += 1

    for code, rank in fifa_rankings.items():
        cursor.execute("""
            UPDATE scraped_team_metrics
            SET fifa_ranking = ?
            WHERE fifa_code = ?;
        """, (rank, code))
        
    conn.commit()
    print(f"¡Métricas de {updated_count} selecciones actualizadas con éxito!")

    # 5b. Complementar posesión desde archivos Sofascore (para equipos sin datos de eliminatorias)
    sofascore_dir = os.path.join(base_dir, "data", "selecciones-sofascore")
    print(f"\nComplementando posesión desde Sofascore ({sofascore_dir})...")
    
    # Mapeo español → código FIFA (igual que en calculate_score_espectaculo.py)
    spanish_to_fifa = {
        'alemania': 'GER', 'arabia saudita': 'KSA', 'argelia': 'ALG', 'argentina': 'ARG',
        'australia': 'AUS', 'austria': 'AUT', 'bosnia y herzegovina': 'BIH', 'brasil': 'BRA',
        'belgica': 'BEL', 'cabo verde': 'CPV', 'canada': 'CAN', 'catar': 'QAT',
        'colombia': 'COL', 'corea del sur': 'KOR', 'costa de marfil': 'CIV', 'croacia': 'CRO',
        'curazao': 'CUR', 'ecuador': 'ECU', 'egipto': 'EGY', 'escocia': 'SCO',
        'espana': 'ESP', 'estados unidos': 'USA', 'francia': 'FRA', 'ghana': 'GHA',
        'haiti': 'HAI', 'inglaterra': 'ENG', 'irak': 'IRQ', 'iran': 'IRN',
        'japon': 'JPN', 'jordania': 'JOR', 'marruecos': 'MAR', 'mexico': 'MEX',
        'noruega': 'NOR', 'panama': 'PAN', 'paraguay': 'PAR', 'paises bajos': 'NED',
        'portugal': 'POR', 'republica checa': 'CZE', 'republica democratica del congo': 'COD',
        'senegal': 'SEN', 'sudafrica': 'RSA', 'suecia': 'SWE', 'suiza': 'SUI',
        'turquia': 'TUR', 'tunez': 'TUN', 'uruguay': 'URU', 'uzbekistan': 'UZB',
        'nueva zelanda': 'NZL'
    }
    
    import re as _re
    sofascore_poss_count = 0
    if os.path.exists(sofascore_dir):
        for filename in os.listdir(sofascore_dir):
            if not filename.endswith(".txt"):
                continue
            # Extraer nombre del país del nombre del archivo
            country_name_sp = filename.split("(")[0].strip() if "(" in filename else filename.replace(".txt", "").strip()
            fifa_code = spanish_to_fifa.get(normalize_name(country_name_sp))
            if not fifa_code:
                print(f"  Advertencia: no se pudo mapear '{country_name_sp}' a código FIFA")
                continue
            
            filepath = os.path.join(sofascore_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            m = _re.search(r"Ball possession:\s*([\d\.]+)%", content, _re.IGNORECASE)
            if not m:
                continue
            poss_val = float(m.group(1))
            
            # Actualizar SOLO si el valor actual es NULL (prioridad a datos de eliminatorias)
            cursor.execute("""
                UPDATE scraped_team_metrics
                SET recent_possession_avg = ?
                WHERE fifa_code = ? AND recent_possession_avg IS NULL;
            """, (poss_val, fifa_code))
            if cursor.rowcount > 0:
                print(f"  {fifa_code}: posesión Sofascore = {poss_val}%")
                sofascore_poss_count += 1
    
    conn.commit()
    print(f"  Posesión Sofascore aplicada a {sofascore_poss_count} selecciones.")

    # 6. Parsear estadísticas de JUGADORES de Eliminatorias 2026
    print("\nProcesando estadísticas individuales de jugadores desde Eliminatorias 2026...")
    player_stats = {}
    
    for filename in os.listdir(wcq_dir):
        if filename.startswith("Player Standard Stats") and filename.endswith(".txt"):
            filepath = os.path.join(wcq_dir, filename)
            print(f"  Procesando jugadores de: {filename}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # All Player Standard Stats files have consistent data column layout:
            # p[1]=Player, p[3]=Squad(with prefix), p[4]=Age, p[5]=Born,
            # p[6]=MP, p[7]=Starts, p[8]=Min, p[9]=90s, p[10]=Gls, p[11]=Ast,
            # p[16]=CrdY, p[17]=CrdR
            # (The CONMEBOL file header is misleadingly offset but data rows are the same.)
            IDX_MP, IDX_MIN, IDX_90S, IDX_GLS, IDX_AST, IDX_CRDY, IDX_CRDR = 6, 8, 9, 10, 11, 16, 17
                
            for line in lines:
                if not line.strip() or line.startswith('Rk') or line.startswith('\t') or line.startswith(' '):
                    continue
                parts = line.strip().split('\t')
                if len(parts) < IDX_CRDR + 1:
                    continue
                    
                player_name = parts[1].strip()
                squad_col_val = parts[3].strip()  # Always index 3: "xx TeamName"
                
                squad_parts = squad_col_val.split(' ', 1)
                if len(squad_parts) < 2:
                    continue
                team_name_raw = squad_parts[1].strip()
                norm_team = normalize_name(team_name_raw)
                team_code = name_to_code.get(norm_team)
                if not team_code:
                    continue
                    
                def get_p_val(idx, default=0.0):
                    try:
                        val_str = parts[idx].replace(',', '').strip()
                        return float(val_str)
                    except (ValueError, IndexError):
                        return default
                
                mp = int(get_p_val(IDX_MP, 0.0))
                minutes = int(get_p_val(IDX_MIN, 0.0))
                nineties = get_p_val(IDX_90S, 0.0)
                goals = int(get_p_val(IDX_GLS, 0.0))
                assists = int(get_p_val(IDX_AST, 0.0))
                crd_y = get_p_val(IDX_CRDY, 0.0)
                crd_r = get_p_val(IDX_CRDR, 0.0)
                
                norm_pname = normalize_name(player_name)
                player_stats[(team_code, norm_pname)] = {
                    'mp': mp,
                    'minutes': minutes,
                    'nineties': nineties,
                    'goals': goals,
                    'assists': assists,
                    'crd_y': crd_y,
                    'crd_r': crd_r
                }
                 
    print("Cruzando jugadores de Eliminatorias con scraped_wc2026_probable_squads...")
    cursor.execute("SELECT player_id, player_name, fifa_code, position FROM scraped_wc2026_probable_squads;")
    db_players = cursor.fetchall()
    
    updated_players_count = 0
    for pid, pname, fcode, pos in db_players:
        norm_db_pname = normalize_name(pname)
        
        p_data = player_stats.get((fcode, norm_db_pname))
        
        if not p_data:
            best_key = None
            best_score = -1.0
            for (tc, npname) in player_stats.keys():
                if tc == fcode:
                    set_db = set(norm_db_pname.split())
                    set_wcq = set(npname.split())
                    if not set_db or not set_wcq:
                        continue
                    jaccard = len(set_db.intersection(set_wcq)) / len(set_db.union(set_wcq))
                    if jaccard > best_score and jaccard >= 0.5:
                        best_score = jaccard
                        best_key = (tc, npname)
            if best_key:
                p_data = player_stats[best_key]
                
        if p_data:
            c_prop = 0.0
            nineties = p_data['nineties']
            if nineties > 0.0:
                c_prop = round(min(max((p_data['crd_y'] + p_data['crd_r'] * 2.0) / nineties, 0.0), 1.0), 2)
            
            mp = p_data['mp']
            goals = p_data['goals']
            assists = p_data['assists']
            eff = round((goals + assists) / mp, 2) if mp > 0 else 0.0
                
            cursor.execute("""
                UPDATE scraped_wc2026_probable_squads
                SET minutes_recent = ?,
                    goals = ?,
                    assists_recent = ?,
                    cards_propensity = ?,
                    caps = ?
                WHERE player_id = ?;
            """, (p_data['minutes'], p_data['goals'], p_data['assists'], c_prop, mp, pid))
            updated_players_count += 1
             
    print(f"  Estadísticas de {updated_players_count} jugadores actualizadas con éxito.")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
