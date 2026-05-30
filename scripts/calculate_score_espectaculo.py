import os
import re
import sqlite3
import statistics
import pandas as pd

def normalize_name(text):
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    char_map = {
        'ı': 'i', 'ğ': 'g', 'ş': 's', 'ç': 'c', 'ö': 'o', 'ü': 'u',
        'ñ': 'n', 'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ã': 'a', 'õ': 'o', 'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
        'í': 'i', 'í': 'i', 'ć': 'c', 'š': 's', 'ž': 'z', 'đ': 'd'
    }
    for k, v in char_map.items():
        text = text.replace(k, v)
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())

def add_column_if_not_exists(cursor, table, col, col_type):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type};")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            pass
        else:
            raise e

def main():
    base_dir = "c:/Users/tomas/Desktop/proyectos/worldcup-app"
    db_path = os.path.join(base_dir, "data", "worldcup_combined.db")
    results_path = os.path.join(base_dir, "data", "international-results", "results.csv")
    ranking_path = os.path.join(base_dir, "data", "ranking_fifa.txt")
    sofascore_dir = os.path.join(base_dir, "data", "selecciones-sofascore")
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Load team mappings from DB
    cursor.execute("SELECT fifa_code, wc2026_name, historical_name, intl_results_name FROM team_mappings;")
    mappings = []
    code_to_names = {}
    name_to_code = {}
    
    for row in cursor.fetchall():
        fifa_code, wc, hist, intl = row
        mappings.append({
            "fifa_code": fifa_code,
            "wc2026_name": wc,
            "historical_name": hist,
            "intl_results_name": intl
        })
        code_to_names[fifa_code] = {
            "wc": wc,
            "hist": hist,
            "intl": intl
        }
        
        # Build lookup dict
        for name in [wc, hist, intl]:
            if name:
                name_to_code[normalize_name(name)] = fifa_code
                
    # Manual overrides/additions
    name_to_code[normalize_name("United States")] = "USA"
    name_to_code[normalize_name("Côte d'Ivoire")] = "CIV"
    name_to_code[normalize_name("DR Congo")] = "COD"
    name_to_code[normalize_name("Curaçao")] = "CUR"
    
    # 2. Parse FIFA Rankings
    print("Loading FIFA rankings...")
    rankings_dict = {}
    if os.path.exists(ranking_path):
        with open(ranking_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    try:
                        rank_val = int(parts[0].strip())
                        nation_raw = parts[1].strip()
                        nation_words = nation_raw.split()
                        if len(nation_words) >= 2 and nation_words[0] == nation_words[1]:
                            nation_name = nation_words[0]
                        else:
                            nation_name = nation_raw
                            
                        rankings_dict[normalize_name(nation_name)] = rank_val
                    except ValueError:
                        continue
                        
    # Helper to get rank of any team name
    def get_fifa_rank(team_name):
        norm = normalize_name(team_name)
        if norm in rankings_dict:
            return rankings_dict[norm]
        # Try finding as substring
        for k, v in rankings_dict.items():
            if norm in k or k in norm:
                return v
        # Try mapped name
        code = name_to_code.get(norm)
        if code and code in code_to_names:
            for name in code_to_names[code].values():
                if name:
                    n2 = normalize_name(name)
                    if n2 in rankings_dict:
                        return rankings_dict[n2]
        return 100 # default fallback
        
    # Spanish to FIFA Code translation helper
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
    
    # 3. Load results.csv
    print("Loading match results...")
    results_df = pd.read_csv(results_path)
    results_df['date'] = pd.to_datetime(results_df['date'])
    results_df_recent = results_df[results_df['date'] >= '2023-01-01']
    
    # 4. Extract Sofascore metrics & compute raw stats
    print("Extracting Sofascore metrics...")
    raw_stats = {}
    
    # Check all files in sofascore directory
    for filename in os.listdir(sofascore_dir):
        if not filename.endswith(".txt"):
            continue
            
        # Parse country name and tournament from filename
        match_fn = re.match(r"^([^\(]+)\s*\(([^\)]+)\)", filename)
        if not match_fn:
            continue
            
        country_name_sp = match_fn.group(1).strip()
        tournament_in_fn = match_fn.group(2).strip()
        
        fifa_code = spanish_to_fifa.get(normalize_name(country_name_sp))
        if not fifa_code:
            print(f"Warning: Could not map Spanish country name '{country_name_sp}' to FIFA code")
            continue
            
        filepath = os.path.join(sofascore_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Parse metrics using regex
        def find_metric(pattern, default=0.0):
            m = re.search(pattern, content, re.IGNORECASE)
            if m:
                return float(m.group(1))
            return default
            
        matches = find_metric(r"Matches:\s*(\d+)", 6.0)
        big_chances_pg = find_metric(r"Big chances per game:\s*([\d\.]+)", 1.5)
        counter_attacks = find_metric(r"Counter attacks:\s*(\d+)", 3.0)
        fouls_pg = find_metric(r"Fouls per game:\s*([\d\.]+)", 10.0)
        
        # CA per game
        counter_attacks_pg = counter_attacks / matches if matches > 0 else 0.5
        
        raw_stats[fifa_code] = {
            "matches": matches,
            "oc_raw": big_chances_pg,
            "ca_raw": counter_attacks_pg,
            "drama_raw": fouls_pg,
            "tournament_fn": tournament_in_fn
        }
        
    # Add New Zealand (OFC) - using old score variables: Gnp, Gc, Drama from qualifiers
    raw_stats["NZL"] = {
        "matches": 5.0,
        "oc_raw": 5.6, # Gnp = (29 - 1) / 5 = 5.6
        "ca_raw": 0.2, # Gc = 1 / 5 = 0.2
        "drama_raw": 1.4, # Drama = (1 + 4 + 2) / 5 = 1.4
        "tournament_fn": "OFC Qualifiers"
    }
    
    # 5. Calculate Cdif based on opponent rankings
    print("Calculating Cdif for each team...")
    adjusted_stats = {}
    
    for code, stats in raw_stats.items():
        intl_name = code_to_names[code]["intl"] if code in code_to_names else None
        if not intl_name:
            # Try getting it from mapping dict
            for k, v in name_to_code.items():
                if v == code:
                    intl_name = k
                    break
        
        if not intl_name:
            intl_name = code_to_names[code]["wc"]
            
        tournament_fn = stats["tournament_fn"]
        
        # Determine tournament filter for results.csv
        tournaments = []
        if "World Cup Qual" in tournament_fn or "OFC" in tournament_fn:
            tournaments = ['FIFA World Cup qualification']
        elif "Arab Cup" in tournament_fn:
            tournaments = ['Arab Cup']
        elif "Africa Cup of Nations" in tournament_fn:
            tournaments = ['African Cup of Nations', 'African Cup of Nations qualification']
        elif "Asian Cup" in tournament_fn:
            tournaments = ['AFC Asian Cup']
        elif "Gold Cup" in tournament_fn:
            tournaments = ['Gold Cup', 'CONCACAF Nations League']
        else:
            tournaments = ['FIFA World Cup qualification', 'Friendly']
            
        # Find matches for this team in these tournaments since 2023
        team_matches = results_df_recent[
            ((results_df_recent['home_team'] == intl_name) | (results_df_recent['away_team'] == intl_name)) &
            (results_df_recent['tournament'].isin(tournaments))
        ]
        
        opponents = []
        for idx, row in team_matches.iterrows():
            if row['home_team'] == intl_name:
                opponents.append(row['away_team'])
            else:
                opponents.append(row['home_team'])
                
        # Get opponent ranks
        ranks = [get_fifa_rank(opp) for opp in opponents if opp != intl_name]
        
        # Fallback if no ranks found
        if not ranks:
            # Let's fallback to typical opponent values based on confederation
            if code in ['GER', 'FRA', 'ENG', 'ESP', 'POR', 'ITA', 'CRO', 'BEL', 'NED']:
                ranks = [40, 50, 60] # UEFA typical WCQ opponents
            elif code in ['ARG', 'BRA', 'URU', 'COL', 'ECU', 'PAR']:
                ranks = [30, 40, 50] # CONMEBOL typical
            elif code in ['USA', 'MEX', 'CAN', 'PAN', 'HAI', 'CUR']:
                ranks = [80, 90, 100] # CONCACAF
            elif code in ['NZL']:
                ranks = [151, 153, 154, 157, 160] # OFC rivals (New Caledonia, Solomons, Fiji, Tahiti, Vanuatu)
            else:
                ranks = [100, 110, 120] # default general
                
        rmed = statistics.median(ranks)
        cdif = 1.0 - (rmed / 211.0)
        cdif = max(0.01, min(1.0, cdif)) # bound between 0.01 and 1.0
        
        adjusted_stats[code] = {
            "oc_adj": stats["oc_raw"] * cdif,
            "ca_adj": stats["ca_raw"] * cdif,
            "drama_adj": stats["drama_raw"] * cdif,
            "cdif": cdif,
            "rmed": rmed
        }
        print(f"Team {code}: Rmed = {rmed:.1f}, Cdif = {cdif:.3f}")
        
    # 6. Min-Max normalization
    print("Normalizing metrics...")
    oc_vals = [s["oc_adj"] for s in adjusted_stats.values()]
    ca_vals = [s["ca_adj"] for s in adjusted_stats.values()]
    drama_vals = [s["drama_adj"] for s in adjusted_stats.values()]
    
    min_oc, max_oc = min(oc_vals), max(oc_vals)
    min_ca, max_ca = min(ca_vals), max(ca_vals)
    min_drama, max_drama = min(drama_vals), max(drama_vals)
    
    final_params = {}
    for code, adj in adjusted_stats.items():
        oc_norm = (adj["oc_adj"] - min_oc) / (max_oc - min_oc) if max_oc != min_oc else 0.5
        ca_norm = (adj["ca_adj"] - min_ca) / (max_ca - min_ca) if max_ca != min_ca else 0.5
        drama_norm = (adj["drama_adj"] - min_drama) / (max_drama - min_drama) if max_drama != min_drama else 0.5
        
        final_params[code] = {
            "ocasiones_norm": round(oc_norm, 3),
            "contra_norm": round(ca_norm, 3),
            "drama_norm": round(drama_norm, 3),
            "cdif": round(adj["cdif"], 3),
            "rmed": adj["rmed"]
        }
        
    # 7. Update database schema and save values
    print("Saving parameters to database...")
    add_column_if_not_exists(cursor, "scraped_team_metrics", "ocasiones_norm", "REAL")
    add_column_if_not_exists(cursor, "scraped_team_metrics", "contra_norm", "REAL")
    add_column_if_not_exists(cursor, "scraped_team_metrics", "drama_norm", "REAL")
    conn.commit()
    
    for code, p in final_params.items():
        cursor.execute("""
            UPDATE scraped_team_metrics
            SET ocasiones_norm = ?,
                contra_norm = ?,
                drama_norm = ?
            WHERE fifa_code = ?;
        """, (p["ocasiones_norm"], p["contra_norm"], p["drama_norm"], code))
        
    conn.commit()
    conn.close()
    print("Database successfully updated with new spectacle parameters!")
    
    # Print sample output for Germany, Argentina, and New Zealand
    for c in ["GER", "ARG", "NZL"]:
        if c in final_params:
            print(f"\n{c} Final Parameters:")
            print(f"  ocasiones_norm: {final_params[c]['ocasiones_norm']}")
            print(f"  contra_norm: {final_params[c]['contra_norm']}")
            print(f"  drama_norm: {final_params[c]['drama_norm']}")
            print(f"  Cdif: {final_params[c]['cdif']}")

if __name__ == "__main__":
    main()
