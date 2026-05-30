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
        # Attempted long balls = acc. long balls / (acc. long balls % / 100)
        if "acc. long balls" in stats and "acc. long balls_pct" in stats:
            pct = stats["acc. long balls_pct"]
            stats["attempted_long_balls"] = stats["acc. long balls"] / (pct / 100.0) if pct > 0 else 0.0
        else:
            stats["attempted_long_balls"] = 0.0

        # Attempted crosses = acc. crosses / (acc. crosses % / 100)
        if "acc. crosses" in stats and "acc. crosses_pct" in stats:
            pct = stats["acc. crosses_pct"]
            stats["attempted_crosses"] = stats["acc. crosses"] / (pct / 100.0) if pct > 0 else 0.0
        else:
            stats["attempted_crosses"] = 0.0
            
        # Attempted passes = accurate passes / (accurate passes % / 100)
        if "accurate passes" in stats and "accurate passes_pct" in stats:
            pct = stats["accurate passes_pct"]
            stats["attempted_passes"] = stats["accurate passes"] / (pct / 100.0) if pct > 0 else 0.0
        else:
            stats["attempted_passes"] = 0.0

        # Opposition half passes / own half passes ratio
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
    
    # 3. Calculate components
    # POSESION: Ball possession % with a penalty for accurate long balls count
    raw_pos = {}
    for team, stats in teams_stats.items():
        raw_pos[team] = stats["ball possession_pct"] - 0.2 * stats["acc. long balls"]
    norm_pos = get_normalized_dict(raw_pos)
    
    # DEFENSA: 20% Opp-to-own pass ratio, 30% Clearances (inverted), 50% Tackles (inverted)
    raw_opp_to_own = {t: stats["opp_to_own_ratio"] for t, stats in teams_stats.items()}
    raw_clearances = {t: stats["clearances per game"] for t, stats in teams_stats.items()}
    raw_tackles = {t: stats["tackles per game"] for t, stats in teams_stats.items()}
    
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
    
    # RITMO: 33% total shots, 33% possession lost, 34% counter attacks (all scaled first)
    raw_shots = {t: stats["total shots per game"] for t, stats in teams_stats.items()}
    raw_lost = {t: stats["possession lost per game"] for t, stats in teams_stats.items()}
    raw_counters = {t: stats["counter attacks"] for t, stats in teams_stats.items()}
    
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
    
    # ANCHO: 80% attempted crosses, 20% attempted crosses / attempted passes ratio
    raw_crosses = {t: stats["attempted_crosses"] for t, stats in teams_stats.items()}
    raw_ratio = {}
    for team, stats in teams_stats.items():
        raw_ratio[team] = stats["attempted_crosses"] / stats["attempted_passes"] if stats["attempted_passes"] > 0 else 0.0
        
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
    output_lines.append("# Reporte de Auditoría de Estilo de Juego")
    output_lines.append("")
    output_lines.append("Auditoría de los vectores de estilo generados por IA frente a las estadísticas reales de Sofascore para 7 países.")
    output_lines.append("")
    output_lines.append("## Fórmulas y Composición Utilizadas")
    output_lines.append("")
    output_lines.append("- **Posesión (`posesion`)**: `% de Posesión` con penalización de `-0.2 * Centros Largos Completados por partido` (para penalizar juego directo/salteo).")
    output_lines.append("- **Defensa (`defensa`)**: Combinación de `20% Relación de Pases Campo Rival/Propio` + `30% Despejes por partido (Invertido)` + `50% Tackles por partido (Invertido)` (un bloque alto realiza menos intervenciones bajas y mantiene el juego arriba).")
    output_lines.append("- **Ritmo (`ritmo`)**: Combinación de `33% Tiros Totales por partido` + `33% Pérdidas de Balón por partido` + `34% Contragolpes por partido` (refleja verticalidad e inmediatez de finalización).")
    output_lines.append("- **Ancho (`ancho`)**: Combinación de `80% Centros Intentados por partido` + `20% Relación de Centros/Pases Totales` (mide amplitud de bandas y frecuencia de centros).")
    output_lines.append("")
    output_lines.append("Todas las componentes fueron normalizadas al rango `[-1, 1]` usando la fórmula:")
    output_lines.append("$$X_{norm} = 2 \\times \\left(\\frac{X - X_{min}}{X_{max} - X_{min}}\\right) - 1$$")
    output_lines.append("")
    
    # Table headers
    output_lines.append("## Tabla Comparativa: IA vs Sofascore Real")
    output_lines.append("")
    output_lines.append("| Selección | Componente | Valor IA | Valor Sofascore (Norm) | Error Absoluto |")
    output_lines.append("| --- | --- | --- | --- | --- |")
    
    errors_by_comp = {"defensa": [], "posesion": [], "ritmo": [], "ancho": []}
    all_errors = []
    
    for team in sorted(teams_stats.keys()):
        ai = ai_vectors[team]
        sofascore = {
            "defensa": norm_def[team],
            "posesion": norm_pos[team],
            "ritmo": norm_ritmo[team],
            "ancho": norm_ancho[team]
        }
        
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
    output_lines.append("| Componente | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) |")
    output_lines.append("| --- | --- | --- |")
    
    for comp, errs in errors_by_comp.items():
        mae = sum(errs) / len(errs)
        rmse = (sum(e**2 for e in errs) / len(errs))**0.5
        output_lines.append(f"| `{comp}` | {mae:.4f} | {rmse:.4f} |")
        
    overall_mae = sum(all_errors) / len(all_errors)
    overall_rmse = (sum(e**2 for e in all_errors) / len(all_errors))**0.5
    
    output_lines.append("")
    output_lines.append(f"**Error Medio Global (MAE):** `{overall_mae:.4f}`")
    output_lines.append(f"**Error Cuadrático Medio Global (RMSE):** `{overall_rmse:.4f}`")
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
