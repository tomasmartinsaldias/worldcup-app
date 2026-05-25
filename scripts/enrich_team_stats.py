import os
import sqlite3

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
    
    if not os.path.exists(db_path):
        print(f"Error: No se encontró la base de datos en {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Agregar nuevas columnas a scraped_team_metrics si no existen
    add_column_if_not_exists(cursor, "scraped_team_metrics", "win_rate_last_10", "REAL")
    add_column_if_not_exists(cursor, "scraped_team_metrics", "draw_rate_last_10", "REAL")
    add_column_if_not_exists(cursor, "scraped_team_metrics", "loss_rate_last_10", "REAL")
    add_column_if_not_exists(cursor, "scraped_team_metrics", "goals_scored_avg_last_10", "REAL")
    add_column_if_not_exists(cursor, "scraped_team_metrics", "goals_conceded_avg_last_10", "REAL")
    add_column_if_not_exists(cursor, "scraped_team_metrics", "current_unbeaten_streak", "INTEGER")
    add_column_if_not_exists(cursor, "scraped_team_metrics", "top_opponent_beaten", "TEXT")
    conn.commit()
    
    # 2. Cargar mapeo de nombres intl a fifa_code y popularidad
    cursor.execute("""
        SELECT m.intl_results_name, m.fifa_code, met.global_popularity_score, m.wc2026_name
        FROM team_mappings m
        LEFT JOIN scraped_team_metrics met ON m.fifa_code = met.fifa_code;
    """)
    mappings = cursor.fetchall()
    
    intl_to_info = {}
    for intl, code, pop, wc_name in mappings:
        if intl:
            intl_to_info[intl] = {
                'code': code,
                'pop': pop if pop is not None else 40.0,
                'name': wc_name
            }
            
    print("Calculando estadísticas de rendimiento reciente para cada selección...")
    
    for intl, code, pop, wc_name in mappings:
        if not intl:
            continue
            
        # Obtener todos los partidos de la selección ordenados por fecha desc
        cursor.execute("""
            SELECT date, home_team, away_team, home_score, away_score
            FROM intl_results
            WHERE home_team = ? OR away_team = ?
            ORDER BY date DESC;
        """, (intl, intl))
        matches = cursor.fetchall()
        
        if not matches:
            print(f"  [!] No se encontraron partidos para {wc_name} ({code}) en intl_results.")
            continue
            
        # A. Calcular últimos 10 partidos jugados (con marcador no nulo)
        played_matches = [m for m in matches if m[3] is not None and m[4] is not None]
        last_10 = played_matches[:10]
        num_matches = len(last_10)
        
        wins = 0
        draws = 0
        losses = 0
        goals_scored = 0
        goals_conceded = 0
        
        for date, home, away, h_score, a_score in last_10:
            h_score = int(h_score)
            a_score = int(a_score)
            
            if home == intl:
                # Local
                goals_scored += h_score
                goals_conceded += a_score
                if h_score > a_score:
                    wins += 1
                elif h_score == a_score:
                    draws += 1
                else:
                    losses += 1
            else:
                # Visitante
                goals_scored += a_score
                goals_conceded += h_score
                if a_score > h_score:
                    wins += 1
                elif h_score == a_score:
                    draws += 1
                else:
                    losses += 1
                    
        win_rate = round(wins / num_matches, 3) if num_matches > 0 else 0.0
        draw_rate = round(draws / num_matches, 3) if num_matches > 0 else 0.0
        loss_rate = round(losses / num_matches, 3) if num_matches > 0 else 0.0
        goals_scored_avg = round(goals_scored / num_matches, 2) if num_matches > 0 else 0.0
        goals_conceded_avg = round(goals_conceded / num_matches, 2) if num_matches > 0 else 0.0
        
        # B. Calcular racha invicta actual (current_unbeaten_streak)
        streak = 0
        for date, home, away, h_score, a_score in matches:
            if h_score is None or a_score is None:
                continue
            h_score = int(h_score)
            a_score = int(a_score)
            
            lost = False
            if home == intl:
                if h_score < a_score:
                    lost = True
            else:
                if a_score < h_score:
                    lost = True
                    
            if lost:
                break
            else:
                streak += 1
                
        # C. Calcular rival más fuerte que derrotaron recientemente (últimos 20 partidos o últimos 2 años)
        # Filtraremos en las últimas 20 participaciones
        top_beaten_opponent = 'N/A'
        top_beaten_pop = -1.0
        
        for date, home, away, h_score, a_score in matches[:20]:
            if h_score is None or a_score is None:
                continue
            h_score = int(h_score)
            a_score = int(a_score)
            
            won = False
            opponent = None
            if home == intl:
                if h_score > a_score:
                    won = True
                    opponent = away
            else:
                if a_score > h_score:
                    won = True
                    opponent = home
                    
            if won and opponent in intl_to_info:
                opp_info = intl_to_info[opponent]
                if opp_info['pop'] > top_beaten_pop:
                    top_beaten_pop = opp_info['pop']
                    top_beaten_opponent = opp_info['name']
                    
        # Actualizar scraped_team_metrics en la BD
        cursor.execute("""
            UPDATE scraped_team_metrics
            SET win_rate_last_10 = ?,
                draw_rate_last_10 = ?,
                loss_rate_last_10 = ?,
                goals_scored_avg_last_10 = ?,
                goals_conceded_avg_last_10 = ?,
                current_unbeaten_streak = ?,
                top_opponent_beaten = ?
            WHERE fifa_code = ?;
        """, (win_rate, draw_rate, loss_rate, goals_scored_avg, goals_conceded_avg, streak, top_beaten_opponent, code))
        
    conn.commit()
    conn.close()
    print("Estadísticas de selección enriquecidas exitosamente.")

if __name__ == "__main__":
    main()
