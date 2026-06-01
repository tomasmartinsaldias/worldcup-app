import os
import re
import json

def get_sofascore_teams_data(sofascore_dir, file_mapping):
    teams_stats = {}
    for filename in os.listdir(sofascore_dir):
        if not filename.endswith(".txt"):
            continue
        
        filepath = os.path.join(sofascore_dir, filename)
        found_team = None
        for key, val in file_mapping.items():
            if key in filename:
                found_team = val
                break
        
        if not found_team:
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
            
        teams_stats[found_team] = stats
        
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
    # rank1 and rank2 are dicts of team -> value
    sorted_teams1 = sorted(rank1.keys(), key=lambda t: rank1[t])
    sorted_teams2 = sorted(rank2.keys(), key=lambda t: rank2[t])
    
    r1 = {team: idx for idx, team in enumerate(sorted_teams1)}
    r2 = {team: idx for idx, team in enumerate(sorted_teams2)}
    
    n = len(rank1)
    sum_d_sq = sum((r1[t] - r2[t])**2 for t in rank1)
    spearman = 1.0 - (6.0 * sum_d_sq) / (n * (n**2 - 1))
    return spearman

def audit():
    sofascore_dir = "data/selecciones-sofascore"
    style_file = "data/estilos-de-juego/selecciones_estilo"
    
    file_mapping = {
        "Alemania": "Alemania",
        "Argentina": "Argentina",
        "España": "España",
        "Francia": "Francia",
        "Jordania": "Jordania",
        "Panamá": "Panamá",
        "Senegal": "Senegal"
    }
    
    # Cdif values under tournament-filtered rules (from database)
    cdif_dict = {
        "Alemania": 0.8349,
        "Argentina": 0.9067,
        "España": 0.7967,
        "Francia": 0.8230,
        "Jordania": 0.8612,
        "Panamá": 0.8756,
        "Senegal": 0.7871
    }
    
    # 1. Load AI Playstyle vectors
    with open(style_file, "r", encoding="utf-8") as f:
        style_data = json.load(f)
        
    ai_vectors = {}
    for team_info in style_data["response"]:
        name = team_info["equipo"]
        if name in file_mapping.values():
            ai_vectors[name] = team_info["vector"]
            
    # 2. Parse SofaScore files
    teams_stats = get_sofascore_teams_data(sofascore_dir, file_mapping)
    
    # 3. Calculate components with context normalization (applying Cdif)
    # POSESION: Ball possession % with a penalty for accurate long balls count, scaled by Cdif
    raw_pos = {}
    for team, stats in teams_stats.items():
        val = stats["ball possession_pct"] - 0.2 * stats["acc. long balls"]
        raw_pos[team] = val * cdif_dict[team]
    norm_pos = get_normalized_dict(raw_pos)
    
    # DEFENSA: 20% Opp-to-own pass ratio (scaled by Cdif), 30% Clearances (divided by Cdif), 50% Tackles (divided by Cdif)
    raw_opp_to_own = {t: stats["opp_to_own_ratio"] * cdif_dict[t] for t, stats in teams_stats.items()}
    raw_clearances = {t: stats["clearances per game"] / cdif_dict[t] for t, stats in teams_stats.items()}
    raw_tackles = {t: stats["tackles per game"] / cdif_dict[t] for t, stats in teams_stats.items()}
    
    norm_opp_to_own = get_normalized_dict(raw_opp_to_own)
    norm_clearances_inv = get_normalized_dict(raw_clearances, invert=True)
    norm_tackles_inv = get_normalized_dict(raw_tackles, invert=True)
    
    raw_def = {}
    for team in teams_stats:
        raw_def[team] = (
            0.2 * norm_opp_to_own[team] + 
            0.3 * norm_clearances_inv[team] + 
            0.5 * norm_tackles_inv[team]
        )
    norm_def = get_normalized_dict(raw_def)
    
    # RITMO: 33% shots (scaled by Cdif), 33% possession lost (divided by Cdif), 34% counter attacks (scaled by Cdif)
    raw_shots = {t: stats["total shots per game"] * cdif_dict[t] for t, stats in teams_stats.items()}
    raw_lost = {t: stats["possession lost per game"] / cdif_dict[t] for t, stats in teams_stats.items()}
    raw_counters = {t: stats["counter attacks"] * cdif_dict[t] for t, stats in teams_stats.items()}
    
    norm_shots = get_normalized_dict(raw_shots)
    norm_lost = get_normalized_dict(raw_lost)
    norm_counters = get_normalized_dict(raw_counters)
    
    raw_ritmo = {}
    for team in teams_stats:
        raw_ritmo[team] = (
            0.33 * norm_shots[team] + 
            0.33 * norm_lost[team] + 
            0.34 * norm_counters[team]
        )
    norm_ritmo = get_normalized_dict(raw_ritmo)
    
    # ANCHO: 80% attempted crosses (scaled by Cdif), 20% ratio (scaled by Cdif)
    raw_crosses = {t: stats["attempted_crosses"] * cdif_dict[t] for t, stats in teams_stats.items()}
    raw_ratio = {}
    for team, stats in teams_stats.items():
        ratio = stats["attempted_crosses"] / stats["attempted_passes"] if stats["attempted_passes"] > 0 else 0.0
        raw_ratio[team] = ratio * cdif_dict[team]
        
    norm_crosses = get_normalized_dict(raw_crosses)
    norm_ratio = get_normalized_dict(raw_ratio)
    
    raw_ancho = {}
    for team in teams_stats:
        raw_ancho[team] = (
            0.8 * norm_crosses[team] + 
            0.2 * norm_ratio[team]
        )
    norm_ancho = get_normalized_dict(raw_ancho)
    
    # 4. Compute errors and metrics
    output_lines = []
    output_lines.append("# Reporte de Auditoría de Estilo de Juego (Alineado por Contexto)")
    output_lines.append("")
    output_lines.append("Auditoría de los vectores de estilo generados por IA frente a las estadísticas reales de Sofascore normalizadas mediante el Coeficiente de Dificultad ($C_{dif}$) para 7 países.")
    output_lines.append("")
    output_lines.append("## Fórmulas y Composición con Normalización de Calendario")
    output_lines.append("")
    output_lines.append("- **Posesión (`posesion`)**: `% de Posesión` con penalización de `-0.2 * Centros Largos` multiplicada por $C_{dif}$.")
    output_lines.append("- **Defensa (`defensa`)**: `20% Relación de Pases Campo Rival/Propio` * $C_{dif}$ + `30% Despejes / Cdif (Invertido)` + `50% Tackles / Cdif (Invertido)`.")
    output_lines.append("- **Ritmo (`ritmo`)**: `33% Tiros Totales` * $C_{dif}$ + `33% Pérdidas de Balón / Cdif` + `34% Contragolpes` * $C_{dif}$.")
    output_lines.append("- **Ancho (`ancho`)**: `80% Centros Intentados` * $C_{dif}$ + `20% Relación de Centros/Pases` * $C_{dif}$.")
    output_lines.append("")
    output_lines.append("Todas las componentes fueron normalizadas al rango `[-1, 1]` tras la calibración de dificultad.")
    output_lines.append("")
    
    # Table headers
    output_lines.append("## Tabla Comparativa: IA vs Sofascore Real Ajustado")
    output_lines.append("")
    output_lines.append("| Selección | Componente | Valor IA | Valor Sofascore (Ajustado) | Error Absoluto |")
    output_lines.append("| --- | --- | --- | --- | --- |")
    
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
    
    for team in sorted(teams_stats.keys()):
        ai = ai_vectors[team]
        sofascore = {
            "defensa": norm_def[team],
            "posesion": norm_pos[team],
            "ritmo": norm_ritmo[team],
            "ancho": norm_ancho[team]
        }
        
        ai_pos_ranks[team] = ai["posesion"]
        ai_def_ranks[team] = ai["defensa"]
        ai_ritmo_ranks[team] = ai["ritmo"]
        ai_ancho_ranks[team] = ai["ancho"]
        
        sf_pos_ranks[team] = sofascore["posesion"]
        sf_def_ranks[team] = sofascore["defensa"]
        sf_ritmo_ranks[team] = sofascore["ritmo"]
        sf_ancho_ranks[team] = sofascore["ancho"]
        
        for comp in ["defensa", "posesion", "ritmo", "ancho"]:
            ai_val = ai[comp]
            sf_val = sofascore[comp]
            err = abs(ai_val - sf_val)
            errors_by_comp[comp].append(err)
            all_errors.append(err)
            output_lines.append(f"| {team} | `{comp}` | {ai_val:+.2f} | {sf_val:+.2f} | {err:.2f} |")
            
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
    report_path = "documentacion/reporte_auditoria_estilos.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
        
    print("\n".join(output_lines[:40]))
    print("...\n(Reporte completo guardado en documentacion/reporte_auditoria_estilos.md)")

if __name__ == "__main__":
    audit()
