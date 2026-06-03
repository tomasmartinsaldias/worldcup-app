import os
import re
import json
import sqlite3
import statistics
import math
import pandas as pd

SPANISH_TO_FIFA = {
    'alemania': 'GER', 'arabia saudita': 'KSA', 'argelia': 'ALG', 'argentina': 'ARG',
    'australia': 'AUS', 'austria': 'AUT', 'bosnia y herzegovina': 'BIH', 'brasil': 'BRA',
    'belgica': 'BEL', 'cabo verde': 'CPV', 'canada': 'CAN', 'catar': 'QAT', 'qatar': 'QAT',
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
        'ć': 'c', 'š': 's', 'ž': 'z', 'đ': 'd'
    }
    for k, v in char_map.items():
        text = text.replace(k, v)
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())

def get_sofascore_teams_data(sofascore_dir):
    teams_stats = {}
    for filename in os.listdir(sofascore_dir):
        if not filename.endswith(".txt"):
            continue
        
        filepath = os.path.join(sofascore_dir, filename)
        
        if "(" in filename:
            parts = filename.split("(")
            country_name_sp = parts[0].strip()
        else:
            country_name_sp = filename.replace(".txt", "").strip()
            
        norm_sp = normalize_name(country_name_sp)
        fifa_code = SPANISH_TO_FIFA.get(norm_sp)
        if not fifa_code:
            continue
            
        stats = {}
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if not line or ":" not in line:
                continue
            parts = line.split(":", 1)
            metric_name = parts[0].strip().lower()
            val_str = parts[1].strip()
            
            match_num = re.match(r"^([\d\.]+)", val_str)
            if match_num:
                stats[metric_name] = float(match_num.group(1))
                
            match_pct = re.search(r"([\d\.]+)\s*%", val_str)
            if match_pct:
                stats[metric_name + "_pct"] = float(match_pct.group(1))
                
        matches = stats.get("matches", 6.0)
        
        if "acc. crosses" in stats and "acc. crosses_pct" in stats:
            pct = stats["acc. crosses_pct"]
            stats["attempted_crosses"] = stats["acc. crosses"] / (pct / 100.0) if pct > 0 else 0.0
        else:
            stats["attempted_crosses"] = 0.0
            
        teams_stats[fifa_code] = stats
        
    return teams_stats

def calculate_cdif_for_all(db_path, results_csv, ranking_txt):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT fifa_code, wc2026_name, historical_name, intl_results_name FROM team_mappings;")
    mappings = cursor.fetchall()
    code_to_names = {row[0]: {"wc": row[1], "hist": row[2], "intl": row[3]} for row in mappings}
    name_to_code = {}
    for row in mappings:
        for name in [row[1], row[2], row[3]]:
            if name:
                name_to_code[normalize_name(name)] = row[0]
                
    rankings_dict = {}
    if os.path.exists(ranking_txt):
        with open(ranking_txt, 'r', encoding='utf-8', errors='ignore') as f:
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
                    except:
                        continue
                        
    def get_fifa_rank(team_name):
        norm = normalize_name(team_name)
        if norm in rankings_dict:
            return rankings_dict[norm]
        for k, v in rankings_dict.items():
            if norm in k or k in norm:
                return v
        code = name_to_code.get(norm)
        if code and code in code_to_names:
            for name in code_to_names[code].values():
                if name:
                    n2 = normalize_name(name)
                    if n2 in rankings_dict:
                        return rankings_dict[n2]
        return 100
        
    df = pd.read_csv(results_csv)
    df['date'] = pd.to_datetime(df['date'])
    df_recent = df[df['date'] >= '2022-01-01']
    
    cdifs = {}
    cursor.execute("SELECT fifa_code FROM wc2026_teams WHERE is_placeholder = 0;")
    all_codes = [r[0] for r in cursor.fetchall()]
    
    for code in all_codes:
        intl_name = None
        if code in code_to_names:
            intl_name = code_to_names[code]["intl"]
        else:
            for k, v in name_to_code.items():
                if v == code:
                    intl_name = k
                    break
        if not intl_name and code in code_to_names:
            intl_name = code_to_names[code]["wc"]
            
        m = df_recent[((df_recent['home_team'] == intl_name) | (df_recent['away_team'] == intl_name))]
        opponents = []
        for _, row in m.iterrows():
            opp = row['away_team'] if row['home_team'] == intl_name else row['home_team']
            if opp != intl_name:
                opponents.append(opp)
                
        ranks = [get_fifa_rank(opp) for opp in opponents]
        if not ranks:
            if code in ['GER', 'FRA', 'ENG', 'ESP', 'POR', 'ITA', 'CRO', 'BEL', 'NED']:
                ranks = [40, 50, 60]
            elif code in ['ARG', 'BRA', 'URU', 'COL', 'ECU', 'PAR']:
                ranks = [30, 40, 50]
            elif code in ['USA', 'MEX', 'CAN', 'PAN', 'HAI', 'CUR']:
                ranks = [80, 90, 100]
            elif code in ['NZL']:
                ranks = [151, 153, 154, 157, 160]
            else:
                ranks = [100, 110, 120]
                
        rmed = statistics.median(ranks)
        cdif = 1.0 - 0.5 * ((rmed - 1.0) / 209.0)
        cdif = max(0.1, min(1.0, cdif))
        cdifs[code] = cdif
        
    conn.close()
    return cdifs

def update_vectors():
    base_dir = "."
    sofascore_dir = os.path.join(base_dir, "data", "selecciones-sofascore")
    style_file = os.path.join(base_dir, "data", "estilos-de-juego", "selecciones_estilo")
    db_path = os.path.join(base_dir, "data", "worldcup_combined.db")
    results_csv = os.path.join(base_dir, "data", "international-results", "results.csv")
    ranking_txt = os.path.join(base_dir, "data", "ranking_fifa.txt")
    
    print("Calculando coeficientes Cdif...")
    cdif_dict = calculate_cdif_for_all(db_path, results_csv, ranking_txt)
    
    print("Cargando SofaScore de los equipos...")
    teams_stats = get_sofascore_teams_data(sofascore_dir)
    
    codes = list(teams_stats.keys())
    
    raw_pos = {}
    raw_ancho = {}
    raw_ritmo = {}
    raw_def = {}
    
    for code in codes:
        stats = teams_stats[code]
        cdif = cdif_dict.get(code, 0.80)
        
        # Posesión
        accurate_passes = stats.get("accurate passes", 300.0)
        pos_pct = stats.get("ball possession_pct", 50.0) / 100.0
        acc_long_balls = stats.get("acc. long balls", 15.0)
        acc_crosses = stats.get("acc. crosses", 5.0)
        p_bruto = pos_pct * (1.0 - (acc_long_balls + acc_crosses) / accurate_passes) if accurate_passes > 0 else 0.0
        raw_pos[code] = p_bruto * cdif
        
        # Ancho
        acc_opposition_half = stats.get("acc. opposition half", 200.0)
        attempted_crosses = stats.get("attempted_crosses", 15.0)
        a_bruto = attempted_crosses / acc_opposition_half if acc_opposition_half > 0 else 0.0
        raw_ancho[code] = a_bruto * cdif
        
        # Ritmo
        matches = stats.get("matches", 6.0)
        total_shots = stats.get("total shots per game", 10.0)
        counter_attacks = stats.get("counter attacks", 0.0)
        pos_pct_val = stats.get("ball possession_pct", 50.0) / 100.0
        r_bruto = (total_shots + (counter_attacks / matches)) / pos_pct_val if pos_pct_val > 0 else 0.0
        raw_ritmo[code] = r_bruto * cdif
        
        # Defensa
        acc_own_half = stats.get("acc. own half", 200.0)
        acc_opp_half = stats.get("acc. opposition half", 200.0)
        clearances = stats.get("clearances per game", 15.0)
        total_acc_passes = acc_own_half + acc_opp_half
        pass_ratio = acc_opp_half / total_acc_passes if total_acc_passes > 0 else 0.5
        
        d_bruto_ajustado = (pass_ratio * cdif) - ((clearances / cdif) / 100.0)
        raw_def[code] = d_bruto_ajustado

    k_sensitivity = 0.6

    def normalize_pipeline(raw_dict, k):
        vals = list(raw_dict.values())
        mean_val = statistics.mean(vals)
        stdev_val = statistics.stdev(vals) if len(vals) > 1 else 1.0
        if stdev_val == 0:
            stdev_val = 1.0
        
        norm_dict = {}
        for team, val in raw_dict.items():
            z = (val - mean_val) / stdev_val
            norm_dict[team] = round(math.tanh(k * z), 4)
        return norm_dict

    norm_pos = normalize_pipeline(raw_pos, k_sensitivity)
    norm_ancho = normalize_pipeline(raw_ancho, k_sensitivity)
    norm_ritmo = normalize_pipeline(raw_ritmo, k_sensitivity)
    norm_def = normalize_pipeline(raw_def, k_sensitivity)
    
    def generate_analisis_tactico(defensa, posesion, ritmo, ancho):
        if defensa > 0.4:
            def_str = "Ejecuta una presión alta asfixiante con una defensa adelantada y proactiva."
        elif defensa < -0.4:
            def_str = "Se organiza en un bloque bajo muy denso, priorizando la solidez y el repliegue."
        else:
            def_str = "Adopta un bloque medio equilibrado, alternando repliegue con momentos de presión activa."
            
        if posesion > 0.4:
            pos_str = "Privilegia la posesión paciente y asociativa para controlar el ritmo del encuentro."
        elif posesion < -0.4:
            pos_str = "Apuesta por transiciones rápidas y juego vertical directo tras recuperar el balón."
        else:
            pos_str = "Mantiene una circulación de balón progresiva con equilibrio entre asociación y verticalidad."
            
        if ritmo > 0.4:
            rit_str = "Imprime un ritmo de juego frenético y de alta velocidad en la finalización de jugadas."
        elif ritmo < -0.4:
            rit_str = "Controla los tiempos con un ritmo pausado y circulación muy segura."
        else:
            rit_str = "Desarrolla el juego a un ritmo moderado y controlado."
            
        if ancho > 0.4:
            anc_str = "Busca abrir la cancha explotando al máximo la amplitud y el desborde por las bandas."
        elif ancho < -0.4:
            anc_str = "Concentra sus ataques por los pasillos interiores y el juego interior por el centro."
        else:
            anc_str = "Alterna el ataque por bandas con la penetración central según los espacios."
            
        return f"{def_str} {pos_str} {rit_str} {anc_str}"

    # Load and update styles file
    with open(style_file, "r", encoding="utf-8") as f:
        style_data = json.load(f)
        
    updated_count = 0
    for team_info in style_data["response"]:
        name = team_info["equipo"]
        norm_name = normalize_name(name)
        code = SPANISH_TO_FIFA.get(norm_name)
        
        if code and code in norm_pos:
            team_info["vector"] = {
                "defensa": norm_def[code],
                "posesion": norm_pos[code],
                "ritmo": norm_ritmo[code],
                "ancho": norm_ancho[code]
            }
            updated_count += 1
        elif code == "NZL":
            # Use Australia (AUS) as tactical proxy
            aus_code = "AUS"
            team_info["vector"] = {
                "defensa": norm_def[aus_code],
                "posesion": norm_pos[aus_code],
                "ritmo": norm_ritmo[aus_code],
                "ancho": norm_ancho[aus_code]
            }
            print(f"Nueva Zelanda (NZL) mapeada utilizando Australia (AUS) como proxy táctico.")
            updated_count += 1
        else:
            # Fallback
            team_info["vector"] = {
                "defensa": 0.0,
                "posesion": 0.0,
                "ritmo": 0.0,
                "ancho": 0.0
            }
            print(f"Advertencia: No se encontraron datos para {name} ({code}). Asignando vector neutro.")
            
        # Dynamically update the tactical description to match the vector values
        v = team_info["vector"]
        team_info["analisis_tactico"] = generate_analisis_tactico(v["defensa"], v["posesion"], v["ritmo"], v["ancho"])
            
    with open(style_file, "w", encoding="utf-8") as f:
        json.dump(style_data, f, indent=4, ensure_ascii=False)
        
    print(f"Se actualizaron los vectores y descripciones para {updated_count} selecciones en {style_file}")

if __name__ == "__main__":
    update_vectors()
