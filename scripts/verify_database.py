import sqlite3

def run_test_query():
    db_path = "c:/Users/User/Downloads/app_mundial/worldcup-app/data/worldcup_combined.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== Corriendo consulta de prueba usando la tabla de mapeo (team_mappings) ===")
    
    # Consulta: Muestra los primeros 15 partidos del mundial 2026
    # y busca cuántas veces se han enfrentado esos equipos históricamente en intl_results usando el mapeo.
    query = """
    SELECT 
        m.match_number,
        m.match_label,
        t1.team_name AS home_2026,
        t2.team_name AS away_2026,
        map1.intl_results_name AS home_intl,
        map2.intl_results_name AS away_intl,
        (
            SELECT COUNT(*) 
            FROM intl_results 
            WHERE (home_team = map1.intl_results_name AND away_team = map2.intl_results_name)
               OR (home_team = map2.intl_results_name AND away_team = map1.intl_results_name)
        ) AS h2h_count
    FROM wc2026_matches m
    JOIN wc2026_teams t1 ON m.home_team_id = t1.id
    JOIN wc2026_teams t2 ON m.away_team_id = t2.id
    JOIN team_mappings map1 ON t1.fifa_code = map1.fifa_code
    JOIN team_mappings map2 ON t2.fifa_code = map2.fifa_code
    WHERE m.match_number <= 15
    ORDER BY m.match_number;
    """
    
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        print(f"{'N° Part.':<8} | {'Fase':<10} | {'Local (2026)':<15} | {'Visitante (2026)':<25} | {'H2H Count':<10} | {'Mapeado a intl_results (Local vs Visitante)':<50}")
        print("-" * 125)
        for row in rows:
            match_num, label, home_2026, away_2026, home_intl, away_intl, h2h = row
            map_str = f"{home_intl} vs {away_intl}" if home_intl and away_intl else "N/A (Playoffs)"
            print(f"#{match_num:<7} | {label:<10} | {home_2026:<15} | {away_2026:<25} | {h2h:<10} | {map_str:<50}")
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
        
    print("\n=== Verificación de consulta histórica cruzada con Fjelstul (Mundiales Pasados) ===")
    # Busquemos enfrentamientos históricos en mundiales pasados usando la tabla de equipos históricos
    query_hist = """
    SELECT 
        m.match_number,
        t1.team_name AS home_2026,
        t2.team_name AS away_2026,
        (
            SELECT COUNT(*) 
            FROM matches m_hist
            JOIN teams t_h1 ON m_hist.home_team_id = t_h1.team_id
            JOIN teams t_h2 ON m_hist.away_team_id = t_h2.team_id
            JOIN team_mappings map1 ON map1.historical_name = t_h1.team_name
            JOIN team_mappings map2 ON map2.historical_name = t_h2.team_name
            WHERE (map1.fifa_code = t1.fifa_code AND map2.fifa_code = t2.fifa_code)
               OR (map1.fifa_code = t2.fifa_code AND map2.fifa_code = t1.fifa_code)
        ) AS wc_h2h_count
    FROM wc2026_matches m
    JOIN wc2026_teams t1 ON m.home_team_id = t1.id
    JOIN wc2026_teams t2 ON m.away_team_id = t2.id
    WHERE m.match_number <= 15 AND t1.is_placeholder = 0 AND t2.is_placeholder = 0
    ORDER BY m.match_number;
    """
    try:
        cursor.execute(query_hist)
        rows_hist = cursor.fetchall()
        print(f"{'N° Part.':<8} | {'Local (2026)':<15} | {'Visitante (2026)':<25} | {'Partidos en Mundiales Pasados':<30}")
        print("-" * 85)
        for row in rows_hist:
            match_num, home, away, count = row
            print(f"#{match_num:<7} | {home:<15} | {away:<25} | {count:<30}")
    except Exception as e:
        print(f"Error al ejecutar la consulta de mundiales pasados: {e}")
        
    conn.close()

if __name__ == "__main__":
    run_test_query()
