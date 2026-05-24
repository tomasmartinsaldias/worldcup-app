import os
import shutil
import sqlite3
import pandas as pd

def main():
    base_dir = "c:/Users/User/Downloads/app_mundial/worldcup-app"
    data_dir = os.path.join(base_dir, "data")
    
    src_wc_db = os.path.join(data_dir, "worldcup", "data-sqlite", "worldcup.db")
    src_wc26_db = os.path.join(data_dir, "mundial-2026", "worldcup2026.db")
    dest_db = os.path.join(data_dir, "worldcup_combined.db")
    
    print("--- 1. Copiando base de datos histórica inicial ---")
    if os.path.exists(dest_db):
        print(f"Eliminando base de datos existente en {dest_db}...")
        os.remove(dest_db)
    shutil.copy(src_wc_db, dest_db)
    print(f"Copiada con éxito a {dest_db}")
    
    print("\n--- 2. Integrando datos del Mundial 2026 ---")
    conn = sqlite3.connect(dest_db)
    cursor = conn.cursor()
    
    # Adjuntamos la DB del mundial 2026
    cursor.execute(f"ATTACH DATABASE '{src_wc26_db}' AS wc2026;")
    
    # Obtener tablas de wc2026
    cursor.execute("SELECT name FROM wc2026.sqlite_master WHERE type='table';")
    wc26_tables = [row[0] for row in cursor.fetchall()]
    
    for table in wc26_tables:
        new_table_name = f"wc2026_{table}"
        print(f"Importando tabla '{table}' como '{new_table_name}'...")
        cursor.execute(f"DROP TABLE IF EXISTS {new_table_name};")
        cursor.execute(f"CREATE TABLE {new_table_name} AS SELECT * FROM wc2026.{table};")
        
    cursor.execute("DETACH DATABASE wc2026;")
    conn.commit()
    print("Datos de 2026 integrados correctamente.")
    
    print("\n--- 2.1. Actualizando ganadores de Playoffs 2026 ---")
    playoffs_updates = [
        (4, 'Czech Republic', 'CZE', 0),
        (6, 'Bosnia and Herzegovina', 'BIH', 0),
        (16, 'Turkey', 'TUR', 0),
        (23, 'Sweden', 'SWE', 0),
        (35, 'DR Congo', 'COD', 0),
        (42, 'Iraq', 'IRQ', 0)
    ]
    for team_id, name, code, is_placeholder in playoffs_updates:
        cursor.execute("""
        UPDATE wc2026_teams 
        SET team_name = ?, fifa_code = ?, is_placeholder = ? 
        WHERE id = ?;
        """, (name, code, is_placeholder, team_id))
    conn.commit()
    print("Ganadores de Playoffs actualizados en wc2026_teams.")
    
    print("\n--- 3. Cargando archivos CSV de resultados internacionales ---")
    intl_dir = os.path.join(data_dir, "international-results")
    csv_files = {
        "former_names.csv": "intl_former_names",
        "goalscorers.csv": "intl_goalscorers",
        "results.csv": "intl_results",
        "shootouts.csv": "intl_shootouts"
    }
    
    for csv_file, table_name in csv_files.items():
        csv_path = os.path.join(intl_dir, csv_file)
        print(f"Leyendo {csv_file} e insertando en tabla '{table_name}'...")
        
        # Intentar leer con distintas codificaciones
        df = None
        for enc in ['utf-8', 'latin-1', 'cp1252', 'utf-8-sig']:
            try:
                df = pd.read_csv(csv_path, encoding=enc)
                print(f"  Leído con éxito usando codificación: {enc}")
                break
            except (UnicodeDecodeError, LookupError):
                continue
        
        if df is None:
            raise ValueError(f"No se pudo leer {csv_file} con ninguna de las codificaciones intentadas.")
            
        # Escribir en SQLite
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"  Insertadas {len(df)} filas.")
        
    print("\n--- 4. Creando tabla de mapeo de equipos ('team_mappings') ---")
    # Obtener todos los equipos de 2026
    cursor.execute("SELECT team_name, fifa_code FROM wc2026_teams;")
    teams_2026 = cursor.fetchall()
    
    # Obtener equipos históricos de Fjelstul
    cursor.execute("SELECT team_name FROM teams;")
    fjelstul_names = {row[0].lower(): row[0] for row in cursor.fetchall()}
    
    # Obtener equipos de resultados internacionales
    cursor.execute("SELECT DISTINCT home_team FROM intl_results;")
    intl_names = {row[0].lower(): row[0] for row in cursor.fetchall()}
    
    # Crear la tabla de mapeo
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS team_mappings (
        fifa_code TEXT PRIMARY KEY,
        wc2026_name TEXT,
        historical_name TEXT,
        intl_results_name TEXT
    );
    """)
    cursor.execute("DELETE FROM team_mappings;") # Limpiar por si acaso
    
    mappings_to_insert = []
    for name_26, code in teams_2026:
        # Resolver nombre histórico (Fjelstul)
        hist_name = None
        if code == 'USA':
            hist_name = 'United States'
        elif code == 'CIV':
            hist_name = 'Ivory Coast'
        elif code == 'IRN':
            hist_name = 'Iran'
        elif code == 'COD':
            hist_name = 'Zaire'
        else:
            hist_name = fjelstul_names.get(name_26.lower(), None)
            
        # Resolver nombre en intl_results
        intl_name = None
        if code == 'USA':
            intl_name = 'United States'
        elif code == 'CIV':
            intl_name = 'Ivory Coast'
        elif code == 'IRN':
            intl_name = 'Iran'
        elif code == 'CPV':
            intl_name = 'Cape Verde'
        else:
            intl_name = intl_names.get(name_26.lower(), None)
            
        # Si es un marcador de posición (placeholder), no tiene nombres reales
        if "Playoff" in name_26:
            hist_name = None
            intl_name = None
            
        mappings_to_insert.append((code, name_26, hist_name, intl_name))
        
    cursor.executemany("""
    INSERT INTO team_mappings (fifa_code, wc2026_name, historical_name, intl_results_name)
    VALUES (?, ?, ?, ?);
    """, mappings_to_insert)
    
    conn.commit()
    print(f"Creada y poblada tabla 'team_mappings' con {len(mappings_to_insert)} registros.")
    
    print("\n--- 5. Creando índices para optimizar consultas ---")
    # Índices para resultados internacionales
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_intl_res_teams ON intl_results(home_team, away_team);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_intl_res_date ON intl_results(date);")
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_intl_goals_teams ON intl_goalscorers(home_team, away_team);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_intl_goals_scorer ON intl_goalscorers(scorer);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_intl_goals_date ON intl_goalscorers(date);")
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_intl_shoots_teams ON intl_shootouts(home_team, away_team);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_intl_shoots_date ON intl_shootouts(date);")
    
    # Índices para WC 2026
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_wc26_matches_teams ON wc2026_matches(home_team_id, away_team_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_wc26_teams_name ON wc2026_teams(team_name);")
    
    conn.commit()
    print("Índices creados con éxito.")
    
    # Resumen
    print("\n--- 6. Resumen de tablas creadas ---")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Total de tablas en la base de datos unificada: {len(tables)}")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"  - {table}: {count} filas")
        
    conn.close()
    print("\n¡Proceso de creación completado exitosamente con mapeo de equipos!")

if __name__ == "__main__":
    main()
