import os
import re
import json
import sqlite3
import statistics
import math
import pandas as pd

# Spanish translation helper to map Sofascore files to FIFA codes
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
        
        # Extract Spanish name
        if "(" in filename:
            parts = filename.split("(")
            country_name_sp = parts[0].strip()
            tournament_fn = parts[1].split(")")[0].replace(".txt", "").strip()
        else:
            country_name_sp = filename.replace(".txt", "").strip()
            tournament_fn = "Unknown"
            
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
            
            # Match first number
            match_num = re.match(r"^([\d\.]+)", val_str)
            if match_num:
                stats[metric_name] = float(match_num.group(1))
                
            # Match percentage if present
            match_pct = re.search(r"([\d\.]+)\s*%", val_str)
            if match_pct:
                stats[metric_name + "_pct"] = float(match_pct.group(1))
                
        # Derive metrics
        matches = stats.get("matches", 6.0)
        if "acc. long balls" in stats and "acc. long balls_pct" in stats:
            pct = stats["acc. long balls_pct"]
            stats["attempted_long_balls"] = stats["acc. long balls"] / (pct / 100.0) if pct > 0 else 0.0
        else:
            stats["attempted_long_balls"] = 0.0

        if "acc. crosses" in stats and "acc. crosses_pct" in stats:
            pct = stats["acc. crosses_pct"]
            stats["attempted_crosses"] = stats["acc. crosses"] / (pct / 100.0) if pct > 0 else 0.0
        else:
            stats["attempted_crosses"] = 0.0
            
        if "accurate passes" in stats and "accurate passes_pct" in stats:
            pct = stats["accurate passes_pct"]
            stats["attempted_passes"] = stats["accurate passes"] / (pct / 100.0) if pct > 0 else 0.0
        else:
            stats["attempted_passes"] = 0.0

        if "acc. opposition half" in stats and "acc. own half" in stats:
            stats["opp_to_own_ratio"] = stats["acc. opposition half"] / stats["acc. own half"] if stats["acc. own half"] > 0 else 0.0
        else:
            stats["opp_to_own_ratio"] = 0.0
            
        stats["tournament_fn"] = tournament_fn
        teams_stats[fifa_code] = stats
        
    return teams_stats

def normalize_to_range(val, v_min, v_max):
    if v_max == v_min:
        return 0.0
    return 2.0 * (val - v_min) / (v_max - v_min) - 1.0

def get_normalized_dict(data_dict, invert=False):
    vals = list(data_dict.values())
    v_min = min(vals)
    v_max = max(vals)
    normalized = {}
    for team, val in data_dict.items():
        if invert:
            normalized[team] = normalize_to_range(v_max - val + v_min, v_min, v_max)
        else:
            normalized[team] = normalize_to_range(val, v_min, v_max)
    return normalized

def calculate_spearman(rank1, rank2):
    sorted_teams1 = sorted(rank1.keys(), key=lambda t: rank1[t])
    sorted_teams2 = sorted(rank2.keys(), key=lambda t: rank2[t])
    
    r1 = {team: idx for idx, team in enumerate(sorted_teams1)}
    r2 = {team: idx for idx, team in enumerate(sorted_teams2)}
    
    n = len(rank1)
    sum_d_sq = sum((r1[t] - r2[t])**2 for t in rank1)
    spearman = 1.0 - (6.0 * sum_d_sq) / (n * (n**2 - 1))
    return spearman

def calculate_cdif_for_all(db_path, results_csv, ranking_txt):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Load rankings
    cursor.execute("SELECT fifa_code, fifa_ranking FROM scraped_team_metrics WHERE fifa_ranking IS NOT NULL;")
    rankings = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Load mappings
    cursor.execute("SELECT fifa_code, wc2026_name, historical_name, intl_results_name FROM team_mappings;")
    mappings = cursor.fetchall()
    code_to_names = {row[0]: {"wc": row[1], "hist": row[2], "intl": row[3]} for row in mappings}
    name_to_code = {}
    for row in mappings:
        for name in [row[1], row[2], row[3]]:
            if name:
                name_to_code[normalize_name(name)] = row[0]
                
    # Load ranking text file
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

def audit():
    base_dir = "."
    sofascore_dir = os.path.join(base_dir, "data", "selecciones-sofascore")
    style_file = os.path.join(base_dir, "data", "estilos-de-juego", "selecciones_estilo")
    db_path = os.path.join(base_dir, "data", "worldcup_combined.db")
    results_csv = os.path.join(base_dir, "data", "international-results", "results.csv")
    ranking_txt = os.path.join(base_dir, "data", "ranking_fifa.txt")
    
    # 1. Compute dynamic Cdif for all teams
    print("Calculando coeficientes Cdif dinámicamente...")
    cdif_dict = calculate_cdif_for_all(db_path, results_csv, ranking_txt)
    
    # 2. Load AI Playstyle vectors
    with open(style_file, "r", encoding="utf-8") as f:
        style_data = json.load(f)
        
    # Build a lookup map from FIFA code to AI vector
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT fifa_code, wc2026_name, historical_name, intl_results_name FROM team_mappings;")
    name_to_code = {}
    for row in cursor.fetchall():
        for n in [row[1], row[2], row[3]]:
            if n:
                name_to_code[normalize_name(n)] = row[0]
    conn.close()
    
    ai_vectors = {}
    for team_info in style_data["response"]:
        name = team_info["equipo"]
        norm_name = normalize_name(name)
        code = SPANISH_TO_FIFA.get(norm_name) or name_to_code.get(norm_name)
        if code:
            ai_vectors[code] = team_info["vector"]
            
    # 3. Parse SofaScore files (47 teams)
    print("Procesando archivos SofaScore reales...")
    teams_stats = get_sofascore_teams_data(sofascore_dir)
    
    # Keep only teams present in both datasets
    common_codes = sorted(list(set(teams_stats.keys()).intersection(set(ai_vectors.keys()))))
    print(f"Encontrados {len(common_codes)} países comunes con datos de SofaScore e IA.")
    
    # 4. Calculate raw metrics for each component
    raw_pos = {}
    raw_ancho = {}
    raw_ritmo = {}
    raw_def = {}
    
    for code in common_codes:
        stats = teams_stats[code]
        cdif = cdif_dict.get(code, 0.80)
        
        # Posesión: p_bruto = Posesion (%) * (1 - (Pases Largos Acertados + Centros Acertados) / Pases Totales Acertados)
        accurate_passes = stats.get("accurate passes", 300.0)
        pos_pct = stats.get("ball possession_pct", 50.0) / 100.0
        acc_long_balls = stats.get("acc. long balls", 15.0)
        acc_crosses = stats.get("acc. crosses", 5.0)
        p_bruto = pos_pct * (1.0 - (acc_long_balls + acc_crosses) / accurate_passes) if accurate_passes > 0 else 0.0
        raw_pos[code] = p_bruto * cdif
        
        # Ancho: a_bruto = (Centros Acertados / Eficacia de Centros) / Pases Acertados en Campo Contrario
        acc_opposition_half = stats.get("acc. opposition half", 200.0)
        attempted_crosses = stats.get("attempted_crosses", 15.0)
        a_bruto = attempted_crosses / acc_opposition_half if acc_opposition_half > 0 else 0.0
        raw_ancho[code] = a_bruto * cdif
        
        # Ritmo: r_bruto = (Tiros Totales + (Contraataques Totales / Partidos Jugados)) / Posesión (%)
        matches = stats.get("matches", 6.0)
        total_shots = stats.get("total shots per game", 10.0)
        counter_attacks = stats.get("counter attacks", 0.0)
        pos_pct_val = stats.get("ball possession_pct", 50.0) / 100.0
        r_bruto = (total_shots + (counter_attacks / matches)) / pos_pct_val if pos_pct_val > 0 else 0.0
        raw_ritmo[code] = r_bruto * cdif
        
        # Defensa: d_bruto = (Pases en Campo Contrario / (Pases Campo Propio + Pases Campo Contrario)) - (Despejes / 100)
        acc_own_half = stats.get("acc. own half", 200.0)
        acc_opp_half = stats.get("acc. opposition half", 200.0)
        clearances = stats.get("clearances per game", 15.0)
        total_acc_passes = acc_own_half + acc_opp_half
        pass_ratio = acc_opp_half / total_acc_passes if total_acc_passes > 0 else 0.5
        
        d_bruto_ajustado = (pass_ratio * cdif) - ((clearances / cdif) / 100.0)
        raw_def[code] = d_bruto_ajustado

    # Pipeline de Normalización No Lineal: Z-Score + tanh
    # Coeficiente de sensibilidad k
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
            norm_dict[team] = math.tanh(k * z)
        return norm_dict

    norm_pos = normalize_pipeline(raw_pos, k_sensitivity)
    norm_ancho = normalize_pipeline(raw_ancho, k_sensitivity)
    norm_ritmo = normalize_pipeline(raw_ritmo, k_sensitivity)
    norm_def = normalize_pipeline(raw_def, k_sensitivity)
    
    # 5. Compute errors and metrics
    output_lines = []
    output_lines.append("# Reporte de Auditoría Completa de Estilo de Juego (47 Selecciones)")
    output_lines.append("")
    output_lines.append("Auditoría de los vectores de estilo generados por IA frente a las estadísticas reales de Sofascore normalizadas mediante el Coeficiente de Dificultad ($C_{dif}$) y proyectadas usando Z-Score y la función sigmoidea (tanh) para los 47 países.")
    output_lines.append("")
    output_lines.append("## Fórmulas y Composición con Normalización de Calendario ($C_{dif}$)")
    output_lines.append("")
    output_lines.append("- **Posesión (`posesion`)**: $p_{bruto} = \\text{Posesión (\\%)} \\times (1 - \\frac{\\text{Pases Largos Acertados} + \\text{Centros Acertados}}{\\text{Pases Totales Acertados}})$, multiplicado por $C_{dif}$.")
    output_lines.append("- **Ancho (`ancho`)**: $a_{bruto} = \\frac{\\text{Centros Intentados}}{\\text{Pases Acertados Campo Contrario}}$, multiplicado por $C_{dif}$.")
    output_lines.append("- **Ritmo (`ritmo`)**: $r_{bruto} = \\frac{\\text{Tiros Totales} + \\frac{\\text{Contraataques Totales}}{\\text{Partidos}}}{\\text{Posesión (\\%)}}$, multiplicado por $C_{dif}$.")
    output_lines.append("- **Defensa (`defensa`)**: $d_{bruto} = (\\text{Relación de Pases Campo Rival} \\times C_{dif}) - \\frac{\\text{Despejes} / C_{dif}}{100.0}$.")
    output_lines.append("")
    output_lines.append("## Pipeline de Normalización No Lineal")
    output_lines.append("")
    output_lines.append("1. **Estandarización (Z-Score)**: $z = \\frac{x - \\mu}{\\sigma}$")
    output_lines.append("2. **Proyección Sigmoidea (tanh)**: $V_{norm} = \\tanh(k \\cdot z)$ (con coeficiente de sensibilidad $k = 0.6$)")
    output_lines.append("")
    
    # Table headers
    output_lines.append("## Tabla Comparativa: IA vs Sofascore Real Ajustado")
    output_lines.append("")
    output_lines.append("| Selección | Código | Componente | Valor IA | Valor Sofascore (Ajustado) | Error Absoluto |")
    output_lines.append("| --- | --- | --- | --- | --- | --- |")
    
    errors_by_comp = {"defensa": [], "posesion": [], "ritmo": [], "ancho": []}
    all_errors = []
    
    ai_pos_ranks = {}
    ai_def_ranks = {}
    ai_ritmo_ranks = {}
    ai_ancho_ranks = {}
    
    sf_pos_ranks = {}
    sf_def_ranks = {}
    sf_ritmo_ranks = {}
    sf_ancho_ranks = {}
    
    # Reconnect to get proper names for codes
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT fifa_code, team_name FROM wc2026_teams;")
    code_to_name = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    
    for code in common_codes:
        ai = ai_vectors[code]
        sofascore = {
            "defensa": norm_def[code],
            "posesion": norm_pos[code],
            "ritmo": norm_ritmo[code],
            "ancho": norm_ancho[code]
        }
        
        ai_pos_ranks[code] = ai["posesion"]
        ai_def_ranks[code] = ai["defensa"]
        ai_ritmo_ranks[code] = ai["ritmo"]
        ai_ancho_ranks[code] = ai["ancho"]
        
        sf_pos_ranks[code] = sofascore["posesion"]
        sf_def_ranks[code] = sofascore["defensa"]
        sf_ritmo_ranks[code] = sofascore["ritmo"]
        sf_ancho_ranks[code] = sofascore["ancho"]
        
        team_display_name = code_to_name.get(code, code)
        
        for comp in ["defensa", "posesion", "ritmo", "ancho"]:
            ai_val = ai[comp]
            sf_val = sofascore[comp]
            err = abs(ai_val - sf_val)
            errors_by_comp[comp].append(err)
            all_errors.append(err)
            output_lines.append(f"| {team_display_name} | `{code}` | `{comp}` | {ai_val:+.2f} | {sf_val:+.2f} | {err:.2f} |")
            
    output_lines.append("")
    output_lines.append("## Resumen de Errores por Componente")
    output_lines.append("")
    output_lines.append("| Componente | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) | Correlación Spearman (ρ) |")
    output_lines.append("| --- | --- | --- | --- |")
    
    spearman_pos = calculate_spearman(ai_pos_ranks, sf_pos_ranks)
    spearman_def = calculate_spearman(ai_def_ranks, sf_def_ranks)
    spearman_ritmo = calculate_spearman(ai_ritmo_ranks, sf_ritmo_ranks)
    spearman_ancho = calculate_spearman(ai_ancho_ranks, sf_ancho_ranks)
    
    spearmans = {
        "posesion": spearman_pos,
        "defensa": spearman_def,
        "ritmo": spearman_ritmo,
        "ancho": spearman_ancho
    }
    
    for comp, errs in errors_by_comp.items():
        mae = sum(errs) / len(errs)
        rmse = (sum(e**2 for e in errs) / len(errs))**0.5
        rho = spearmans[comp]
        output_lines.append(f"| `{comp}` | {mae:.4f} | {rmse:.4f} | {rho:+.4f} |")
        
    overall_mae = sum(all_errors) / len(all_errors)
    overall_rmse = (sum(e**2 for e in all_errors) / len(all_errors))**0.5
    overall_spearman = sum(spearmans.values()) / len(spearmans)
    
    output_lines.append("")
    output_lines.append(f"**Error Medio Global (MAE):** `{overall_mae:.4f}`")
    output_lines.append(f"**Error Cuadrático Medio Global (RMSE):** `{overall_rmse:.4f}`")
    output_lines.append(f"**Correlación de Spearman Promedio:** `{overall_spearman:.4f}`")
    output_lines.append("")
    
    # Save to report file
    report_path = "documentacion/reporte_auditoria_completa_estilos.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
        
    print(f"Reporte completo con las {len(common_codes)} selecciones guardado en: {report_path}")

if __name__ == "__main__":
    audit()
