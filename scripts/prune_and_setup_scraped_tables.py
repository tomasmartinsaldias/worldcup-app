import os
import sqlite3

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "data", "worldcup_combined.db")
    
    if not os.path.exists(db_path):
        print(f"Error: No se encontró la base de datos en {db_path}")
        return
        
    initial_size = os.path.getsize(db_path)
    print(f"Tamaño inicial de la base de datos: {initial_size / (1024 * 1024):.2f} MB")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Lista de tablas a eliminar
    tables_to_drop = [
        # Árbitros
        "referees", "referee_appointments", "referee_appearances",
        # Entrenadores
        "managers", "manager_appointments", "manager_appearances",
        # Cambios y definición por penales histórica detallada
        "substitutions", "penalty_kicks",
        # Estadios antiguos
        "stadiums",
        # Rendimiento detallado redundante
        "team_appearances", "goals",
        # Formatos e información agregada secundaria
        "formats", "groups", "group_standings", "tournament_standings", 
        "award_winners", "awards", "host_countries"
    ]
    
    print("\n--- 1. Eliminando 23 tablas de ruido analítico ---")
    for table in tables_to_drop:
        print(f"Eliminando tabla '{table}'...")
        cursor.execute(f"DROP TABLE IF EXISTS {table};")
        
    conn.commit()
    print("Tablas eliminadas exitosamente.")
    
    print("\n--- 2. Creando nuevas tablas para Scraping ---")
    # Tabla: scraped_team_metrics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scraped_team_metrics (
        fifa_code TEXT PRIMARY KEY,
        market_value_eur REAL,
        recent_xg_avg REAL,
        recent_possession_avg REAL,
        global_popularity_score REAL,
        progressive_passes_per_90_avg REAL,
        sofascore_rating_avg REAL,
        cards_per_match_avg REAL,
        FOREIGN KEY (fifa_code) REFERENCES wc2026_teams (fifa_code)
    );
    """)
    print("Creada tabla 'scraped_team_metrics'.")
    
    # Tabla: scraped_wc2026_probable_squads
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scraped_wc2026_probable_squads (
        player_id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT,
        fifa_code TEXT,
        position TEXT,
        club TEXT,
        age INTEGER,
        caps INTEGER,
        goals INTEGER,
        market_value_eur REAL,
        is_star_player BOOLEAN,
        is_injured BOOLEAN,
        progressive_passes_per_90 REAL,
        sofascore_rating REAL,
        cards_propensity REAL,
        FOREIGN KEY (fifa_code) REFERENCES wc2026_teams (fifa_code)
    );
    """)
    print("Creada tabla 'scraped_wc2026_probable_squads'.")
    
    # Tabla: scraped_unresolved_players
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scraped_unresolved_players (
        player_id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT,
        fifa_code TEXT,
        position TEXT,
        club TEXT,
        age INTEGER,
        caps INTEGER,
        goals INTEGER,
        reason_unresolved TEXT,
        resolved BOOLEAN DEFAULT 0,
        FOREIGN KEY (fifa_code) REFERENCES wc2026_teams (fifa_code)
    );
    """)
    print("Creada tabla 'scraped_unresolved_players'.")
    
    conn.commit()
    
    print("\n--- 3. Optimizando base de datos (VACUUM) ---")
    conn.execute("VACUUM;")
    print("Base de datos optimizada y compactada.")
    
    # Resumen de tablas actuales
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"\n--- 4. Estado final de tablas activas ({len(tables)} tablas) ---")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"  - {table}: {count} filas")
        
    conn.close()
    
    final_size = os.path.getsize(db_path)
    print(f"\nTamaño final de la base de datos: {final_size / (1024 * 1024):.2f} MB")
    print(f"Reducción de tamaño: {(1 - final_size/initial_size)*100:.1f}%")
    print("\n¡Proceso de reducción y estructuración completado con éxito!")

if __name__ == "__main__":
    main()
