import os
import sqlite3
import json

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "data", "worldcup_combined.db")
    output_path = os.path.join(base_dir, "data", "wc2026_data.json")
    
    if not os.path.exists(db_path):
        print(f"Error: No se encontró la base de datos en {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Cargar Mapeos de Equipos
    print("Cargando mapeos de equipos...")
    cursor.execute("SELECT fifa_code, wc2026_name, historical_name, intl_results_name FROM team_mappings;")
    mappings = {}
    for row in cursor.fetchall():
        mappings[row[0]] = {
            "wc2026_name": row[1],
            "historical_name": row[2],
            "intl_results_name": row[3]
        }
        
    # 2. Cargar Selecciones y Métricas de Scraping
    print("Cargando selecciones y sus métricas...")
    cursor.execute("""
        SELECT 
            t.id, t.team_name, t.fifa_code, t.group_letter, t.is_placeholder, t.is_confirmed_squad,
            m.market_value_eur, m.recent_xg_avg, m.recent_possession_avg, 
            m.global_popularity_score, m.cards_per_match_avg, m.efficiency_score_avg,
            m.win_rate_last_10, m.draw_rate_last_10, m.loss_rate_last_10,
            m.goals_scored_avg_last_10, m.goals_conceded_avg_last_10,
            m.current_unbeaten_streak, m.top_opponent_beaten
        FROM wc2026_teams t
        LEFT JOIN scraped_team_metrics m ON t.fifa_code = m.fifa_code;
    """)
    
    teams_dict = {}
    groups_dict = {}
    
    for row in cursor.fetchall():
        (tid, name, code, group_letter, is_placeholder, is_confirmed, val, xg, poss, pop, cards, 
         eff_avg, win_rate, draw_rate, loss_rate, gs_avg, gc_avg, streak, top_beaten) = row
        
        # Agrupar por grupo para la vista de grupos
        if group_letter and not is_placeholder:
            if group_letter not in groups_dict:
                groups_dict[group_letter] = []
            groups_dict[group_letter].append(code)
            
        metrics = None
        if not is_placeholder:
            metrics = {
                "market_value_eur": val,
                "recent_xg_avg": xg,
                "recent_possession_avg": poss,
                "global_popularity_score": pop,
                "cards_per_match_avg": cards,
                "efficiency_score_avg": eff_avg,
                "win_rate_last_10": win_rate,
                "draw_rate_last_10": draw_rate,
                "loss_rate_last_10": loss_rate,
                "goals_scored_avg_last_10": gs_avg,
                "goals_conceded_avg_last_10": gc_avg,
                "current_unbeaten_streak": streak,
                "top_opponent_beaten": top_beaten
            }
            
        teams_dict[code] = {
            "id": tid,
            "name": name,
            "fifa_code": code,
            "group": group_letter,
            "is_placeholder": bool(is_placeholder),
            "is_confirmed_squad": bool(is_confirmed),
            "metrics": metrics,
            "squad": []
        }
        
    # 3. Cargar Jugadores de cada Selección
    print("Cargando planteles probables...")
    cursor.execute("""
        SELECT 
            ps.player_id, ps.player_name, ps.fifa_code, ps.position, ps.club, ps.age, ps.caps, ps.goals,
            ps.market_value_eur, ps.is_star_player, ps.is_injured, ps.cards_propensity,
            ps.assists_recent, ps.minutes_recent, ps.efficiency_score,
            ps.xG_intl, ps.sca_intl, ps.gca_intl, ps.progressive_passes_intl, ps.progressive_carries_intl
        FROM scraped_wc2026_probable_squads ps
        JOIN wc2026_teams t ON ps.fifa_code = t.fifa_code
        WHERE t.is_confirmed_squad = 1 
           OR ps.efficiency_score IS NOT NULL 
           OR ps.caps >= 5;
    """)
    
    for row in cursor.fetchall():
        (pid, name, code, pos, club, age, caps, goals, val, star, injured, cards, assists_rec, mins_rec, 
         eff_rec, xg, sca, gca, prog_pass, prog_carr) = row
        if code in teams_dict:
            teams_dict[code]["squad"].append({
                "id": pid,
                "name": name,
                "position": pos,
                "club": club,
                "age": age,
                "caps": caps,
                "goals": goals,
                "market_value_eur": val,
                "is_star_player": bool(star) if star is not None else None,
                "is_injured": bool(injured) if injured is not None else False,
                "cards_propensity": cards,
                "assists_recent": assists_rec,
                "minutes_recent": mins_rec,
                "efficiency_score": eff_rec,
                "xG_intl": xg,
                "sca_intl": sca,
                "gca_intl": gca,
                "progressive_passes_intl": prog_pass,
                "progressive_carries_intl": prog_carr
            })
            
    # Ordenar planteles por valor de mercado desc, luego nombre
    for code in teams_dict:
        teams_dict[code]["squad"].sort(key=lambda x: (-(x["market_value_eur"] or 0), x["name"]))
        
    # 4. Cargar Ciudades Anfitrionas y Estadios
    print("Cargando sedes y estadios...")
    cursor.execute("SELECT id, city_name, country, venue_name, region_cluster, airport_code FROM wc2026_host_cities;")
    stadiums = []
    stadiums_dict = {}
    for row in cursor.fetchall():
        sid, city, country, venue, region, airport = row
        stadium_info = {
            "id": sid,
            "city_name": city,
            "country": country,
            "venue_name": venue,
            "region_cluster": region,
            "airport_code": airport
        }
        stadiums.append(stadium_info)
        stadiums_dict[sid] = stadium_info
        
    # 5. Cargar Partidos y Calcular H2H
    print("Procesando partidos y calculando H2H histórico...")
    cursor.execute("""
        SELECT 
            m.id, m.match_number, m.kickoff_at, m.match_label,
            t1.fifa_code AS home_code, t2.fifa_code AS away_code,
            m.city_id, s.stage_name
        FROM wc2026_matches m
        LEFT JOIN wc2026_teams t1 ON m.home_team_id = t1.id
        LEFT JOIN wc2026_teams t2 ON m.away_team_id = t2.id
        LEFT JOIN wc2026_tournament_stages s ON m.stage_id = s.id
        ORDER BY m.match_number;
    """)
    
    matches = []
    
    for row in cursor.fetchall():
        mid, match_num, kickoff, label, home_code, away_code, city_id, stage_name = row
        
        home_team = teams_dict.get(home_code)
        away_team = teams_dict.get(away_code)
        stadium = stadiums_dict.get(city_id)
        
        h2h_data = {
            "total_matches": 0,
            "home_wins": 0,
            "away_wins": 0,
            "draws": 0,
            "home_goals": 0,
            "away_goals": 0,
            "wc_matches": 0,
            "wc_home_wins": 0,
            "wc_away_wins": 0,
            "wc_draws": 0,
            "last_matches": []
        }
        
        # Calcular H2H si ambos equipos no son placeholders y están mapeados
        if home_team and away_team and not home_team["is_placeholder"] and not away_team["is_placeholder"]:
            map_home = mappings.get(home_code)
            map_away = mappings.get(away_code)
            
            if map_home and map_away:
                h_intl = map_home["intl_results_name"]
                a_intl = map_away["intl_results_name"]
                h_hist = map_home["historical_name"]
                a_hist = map_away["historical_name"]
                
                # A. H2H en partidos internacionales generales (intl_results)
                if h_intl and a_intl:
                    cursor.execute("""
                        SELECT date, tournament, home_team, away_team, home_score, away_score
                        FROM intl_results
                        WHERE (home_team = ? AND away_team = ?)
                           OR (home_team = ? AND away_team = ?)
                        ORDER BY date DESC;
                    """, (h_intl, a_intl, a_intl, h_intl))
                    
                    intl_rows = cursor.fetchall()
                    h2h_data["total_matches"] = len(intl_rows)
                    
                    for idx, i_row in enumerate(intl_rows):
                        date_str, tourn, h_team, a_team, h_score, a_score = i_row
                        
                        # Determinar quién anotó qué goles
                        if h_team == h_intl:
                            g_home = int(h_score) if h_score is not None else 0
                            g_away = int(a_score) if a_score is not None else 0
                        else:
                            g_home = int(a_score) if a_score is not None else 0
                            g_away = int(h_score) if h_score is not None else 0
                            
                        h2h_data["home_goals"] += g_home
                        h2h_data["away_goals"] += g_away
                        
                        # Resultados
                        if g_home > g_away:
                            h2h_data["home_wins"] += 1
                        elif g_home < g_away:
                            h2h_data["away_wins"] += 1
                        else:
                            h2h_data["draws"] += 1
                            
                        # Guardar los últimos 5 partidos como muestra
                        if idx < 5:
                            h2h_data["last_matches"].append({
                                "date": date_str,
                                "tournament": tourn,
                                "home_team": h_team,
                                "away_team": a_team,
                                "score": f"{int(h_score)}-{int(a_score)}" if h_score is not None and a_score is not None else "N/A"
                            })
                            
                # B. H2H específico de Mundiales Pasados (Fjelstul)
                if h_hist and a_hist:
                    cursor.execute("""
                        SELECT 
                            m_hist.match_date, t_h1.team_name, t_h2.team_name, 
                            m_hist.home_team_score, m_hist.away_team_score,
                            t_winner.team_name, m_hist.draw
                        FROM matches m_hist
                        JOIN teams t_h1 ON m_hist.home_team_id = t_h1.team_id
                        JOIN teams t_h2 ON m_hist.away_team_id = t_h2.team_id
                        LEFT JOIN teams t_winner ON m_hist.home_team_win = 1 AND t_winner.team_id = m_hist.home_team_id 
                                                 OR m_hist.away_team_win = 1 AND t_winner.team_id = m_hist.away_team_id
                        WHERE (t_h1.team_name = ? AND t_h2.team_name = ?)
                           OR (t_h1.team_name = ? AND t_h2.team_name = ?)
                        ORDER BY m_hist.match_date DESC;
                    """, (h_hist, a_hist, a_hist, h_hist))
                    
                    wc_rows = cursor.fetchall()
                    h2h_data["wc_matches"] = len(wc_rows)
                    
                    for w_row in wc_rows:
                        date_str, t1_name, t2_name, s1, s2, w_name, draw = w_row
                        
                        if draw:
                            h2h_data["wc_draws"] += 1
                        else:
                            # ¿Quién es el local de 2026 en este partido histórico?
                            if w_name == h_hist:
                                h2h_data["wc_home_wins"] += 1
                            elif w_name == a_hist:
                                h2h_data["wc_away_wins"] += 1
                                
        match_data = {
            "id": mid,
            "match_number": match_num,
            "kickoff_at": kickoff,
            "match_label": label,
            "stage": stage_name,
            "home_team": {
                "fifa_code": home_code,
                "name": home_team["name"] if home_team else "TBD",
                "is_placeholder": home_team["is_placeholder"] if home_team else True,
                "group": home_team["group"] if home_team else None
            },
            "away_team": {
                "fifa_code": away_code,
                "name": away_team["name"] if away_team else "TBD",
                "is_placeholder": away_team["is_placeholder"] if away_team else True,
                "group": away_team["group"] if away_team else None
            },
            "stadium": stadium,
            "h2h": h2h_data
        }
        matches.append(match_data)
        
    conn.close()
    
    # 6. Guardar en JSON
    data_to_export = {
        "teams": teams_dict,
        "stadiums": stadiums,
        "matches": matches,
        "groups": groups_dict
    }
    
    print(f"Exportando datos a {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data_to_export, f, ensure_ascii=False, indent=2)
        
    print("¡Exportación completada con éxito!")

if __name__ == "__main__":
    main()
