import sqlite3

def run_verification():
    db_path = "c:/Users/User/Downloads/app_mundial/worldcup-app/data/worldcup_combined.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== 1. Insertando Datos Simulados en Tablas de Scraping ===")
    
    # Limpiar datos previos
    cursor.execute("DELETE FROM scraped_team_metrics;")
    cursor.execute("DELETE FROM scraped_wc2026_probable_squads;")
    
    # Insertar métricas simuladas de selecciones (Argentina, México, USA, España)
    dummy_metrics = [
        ('ARG', 950.5, 2.1, 62.5, 98.4, 52.4, 7.15, 1.8), # Argentina
        ('MEX', 220.0, 1.4, 52.0, 75.0, 35.1, 6.85, 2.1), # México
        ('USA', 350.0, 1.6, 55.4, 80.2, 40.2, 6.92, 1.9), # USA
        ('ESP', 880.0, 1.9, 65.1, 91.0, 58.6, 7.08, 1.6)  # España
    ]
    cursor.executemany("""
    INSERT INTO scraped_team_metrics (fifa_code, market_value_eur, recent_xg_avg, recent_possession_avg, global_popularity_score, progressive_passes_per_90_avg, sofascore_rating_avg, cards_per_match_avg)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, dummy_metrics)
    
    # Insertar algunos jugadores probables con edad, caps, goles y métricas
    dummy_players = [
        ('Lionel Messi', 'ARG', 'Delantero', 'Inter Miami', 38, 191, 109, 30.0, 1, 0, 4.8, 7.82, 0.05),
        ('Enzo Fernández', 'ARG', 'Centrocampista', 'Chelsea', 25, 28, 4, 75.0, 1, 0, 6.2, 7.12, 0.22),
        ('Santiago Giménez', 'MEX', 'Delantero', 'Feyenoord', 25, 32, 4, 45.0, 1, 0, 1.8, 6.95, 0.15),
        ('Christian Pulisic', 'USA', 'Delantero', 'AC Milan', 27, 68, 29, 40.0, 1, 1, 3.5, 7.05, 0.10), # lesionado
        ('Pedri', 'ESP', 'Centrocampista', 'FC Barcelona', 23, 24, 2, 80.0, 1, 0, 7.1, 7.25, 0.08)
    ]
    cursor.executemany("""
    INSERT INTO scraped_wc2026_probable_squads (player_name, fifa_code, position, club, age, caps, goals, market_value_eur, is_star_player, is_injured, progressive_passes_per_90, sofascore_rating, cards_propensity)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, dummy_players)
    
    conn.commit()
    print("Datos simulados insertados con éxito.")
    
    print("\n=== 2. Consulta Cruzada: Recomendación de Partidos con Métricas y Tarjetas Históricas ===")
    
    # Query que cruza el fixture de 2026, datos de valor de plantilla (scraped),
    # lesionados, popularidad, y estadísticas de tarjetas históricas (bookings) en mundiales.
    query = """
    SELECT 
        m.match_number,
        m.match_label,
        t1.team_name AS local_2026,
        t2.team_name AS visita_2026,
        IFNULL(met1.market_value_eur, 0) AS valor_local_m,
        IFNULL(met2.market_value_eur, 0) AS valor_visita_m,
        (IFNULL(met1.global_popularity_score, 0) + IFNULL(met2.global_popularity_score, 0)) / 2 AS pop_promedio,
        -- Contar tarjetas amarillas/rojas históricas en mundiales para el equipo local
        (
            SELECT COUNT(*) 
            FROM bookings b
            JOIN team_mappings map ON map.historical_name = (SELECT team_name FROM teams WHERE team_id = b.team_id)
            WHERE map.fifa_code = t1.fifa_code
        ) AS tarjetas_historicas_local,
        -- Contar estrellas lesionadas en el plantel probable
        (
            SELECT COUNT(*) 
            FROM scraped_wc2026_probable_squads ps
            WHERE ps.fifa_code = t1.fifa_code AND ps.is_injured = 1
        ) + 
        (
            SELECT COUNT(*) 
            FROM scraped_wc2026_probable_squads ps
            WHERE ps.fifa_code = t2.fifa_code AND ps.is_injured = 1
        ) AS total_estrellas_lesionadas
    FROM wc2026_matches m
    JOIN wc2026_teams t1 ON m.home_team_id = t1.id
    JOIN wc2026_teams t2 ON m.away_team_id = t2.id
    LEFT JOIN scraped_team_metrics met1 ON t1.fifa_code = met1.fifa_code
    LEFT JOIN scraped_team_metrics met2 ON t2.fifa_code = met2.fifa_code
    WHERE m.match_number <= 15
    ORDER BY m.match_number;
    """
    
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        print(f"{'Partido':<8} | {'Local vs Visitante':<32} | {'Val. Loc.':<10} | {'Val. Vis.':<10} | {'Pop. Prom.':<10} | {'Tarjetas Loc.':<13} | {'Bajas/Lesion.':<13}")
        print("-" * 115)
        for row in rows:
            num, label, home, away, val_h, val_a, pop, cards_h, injuries = row
            teams_str = f"{home} vs {away}"
            print(f"#{num:<7} | {teams_str:<32} | {val_h:<10.1f} | {val_a:<10.1f} | {pop:<10.1f} | {cards_h:<13} | {injuries:<13}")
    except Exception as e:
        print(f"Error al ejecutar consulta cruzada: {e}")
        
    # Limpiar datos simulados para dejar las tablas vacías y listas para el scraping real
    cursor.execute("DELETE FROM scraped_team_metrics;")
    cursor.execute("DELETE FROM scraped_wc2026_probable_squads;")
    conn.commit()
    print("\nBase de datos limpiada de datos simulados (tablas listas para scraping real).")
    
    conn.close()

if __name__ == "__main__":
    run_verification()
