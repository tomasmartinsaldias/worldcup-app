import os
import sqlite3
import sys

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "data", "worldcup_combined.db")
    
    if not os.path.exists(db_path):
        print(f"Error: No se encontró la base de datos en {db_path}")
        return
        
    initial_size = os.path.getsize(db_path)
    print(f"Tamaño inicial de la base de datos: {initial_size / (1024 * 1024):.2f} MB")
    
    # Por defecto, este script eliminará las tablas que están 100% sin usar.
    # Si se pasa el argumento '--clean-all', eliminará todas las tablas históricas y de caché,
    # dejando únicamente las tablas necesarias para la presentación del Mundial 2026.
    clean_all = '--clean-all' in sys.argv
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Grupo 1: Tablas obsoletas o no utilizadas que se eliminarán siempre
    obsolete_tables = [
        "intl_goalscorers",
        "squads",
        "intl_shootouts",
        "qualified_teams",
        "tournament_stages",
        "tournaments",
        "confederations",
        "intl_former_names",
        "bookings",
        "player_appearances",
        "players",
        "matches",
        "teams"
    ]
    
    # Grupo 2: Tablas de caché temporal (se borran solo con --clean-all)
    cache_tables = [
        "cache_transfermarkt"
    ]
    
    tables_to_drop = obsolete_tables
    if clean_all:
        print("\n--- Borrado Completo (Incluyendo Cachés) ---")
        tables_to_drop = obsolete_tables + cache_tables
    else:
        print("\n--- Borrado Seguro de Tablas Obsoletas e Históricas ---")
        
    for table in tables_to_drop:
        print(f"Eliminando tabla '{table}'...")
        cursor.execute(f"DROP TABLE IF EXISTS {table};")
    conn.commit()
    
    # Filtro inteligente para intl_results (mantener últimos 15 años o cruces de las 48 selecciones)
    print("\n--- Aplicando filtrado inteligente a la tabla 'intl_results' ---")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='intl_results';")
    if cursor.fetchone():
        cursor.execute("SELECT COUNT(1) FROM intl_results;")
        initial_rows = cursor.fetchone()[0]
        
        cursor.execute("SELECT DISTINCT intl_results_name FROM team_mappings WHERE intl_results_name IS NOT NULL;")
        wc2026_intl_names = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("DROP TABLE IF EXISTS temp_intl_results;")
        cursor.execute("CREATE TABLE temp_intl_results AS SELECT * FROM intl_results WHERE 1=0;")
        
        placeholders = ",".join(["?"] * len(wc2026_intl_names))
        query = f"""
        INSERT INTO temp_intl_results
        SELECT * FROM intl_results
        WHERE date >= '2011-01-01'
           OR (home_team IN ({placeholders}) AND away_team IN ({placeholders}));
        """
        cursor.execute(query, wc2026_intl_names + wc2026_intl_names)
        
        cursor.execute("DROP TABLE intl_results;")
        cursor.execute("ALTER TABLE temp_intl_results RENAME TO intl_results;")
        
        # Recrear índices para optimizar
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_intl_res_teams ON intl_results(home_team, away_team);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_intl_res_date ON intl_results(date);")
        
        cursor.execute("SELECT COUNT(1) FROM intl_results;")
        final_rows = cursor.fetchone()[0]
        print(f"  intl_results: Reducida de {initial_rows} a {final_rows} filas.")
        conn.commit()
        
    print("\n--- Ejecutando VACUUM para reducir y compactar el archivo SQLite ---")
    cursor.execute("VACUUM;")
    conn.commit()
    
    # Listar tablas resultantes y contar filas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    active_tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n--- Estado final de las tablas activas ({len(active_tables)} tablas) ---")
    for table in active_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"  - {table}: {count} filas")
        
    conn.close()
    
    final_size = os.path.getsize(db_path)
    print(f"\nTamaño final de la base de datos: {final_size / (1024 * 1024):.2f} MB")
    print(f"Reducción de tamaño: {(1 - final_size/initial_size)*100:.1f}%")
    
    if not clean_all:
        print("\n[INFO] Si quieres reducirla al mínimo absoluto para entregarla a tus compañeros,")
        print("puedes correr este script con el parámetro '--clean-all':")
        print("  python scripts/prune_database.py --clean-all")

if __name__ == '__main__':
    main()
