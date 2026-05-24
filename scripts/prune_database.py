import os
import sqlite3
import sys

def main():
    base_dir = "c:/Users/User/Downloads/app_mundial/worldcup-app"
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
    
    # Grupo 1: Tablas que NO se usan en ningún script del pipeline ni del proyecto
    unused_tables = [
        "intl_goalscorers",      # 47,601 filas de goleadores históricos
        "squads",                # 10,973 filas de convocatorias históricas
        "intl_shootouts",         # 675 filas de definiciones por penales históricas
        "qualified_teams",       # 489 filas de equipos calificados históricos
        "tournament_stages",     # 113 filas de etapas históricas
        "tournaments",           # 22 filas de torneos históricos
        "confederations",        # 6 filas de confederaciones
        "intl_former_names"      # 36 filas de nombres antiguos de países
    ]
    
    # Grupo 2: Tablas históricas que se usan durante el pipeline (populate o export)
    # pero que se pueden borrar si solo queremos compartir la base de datos final procesada.
    pipeline_historical_tables = [
        "bookings",              # Usada en populate_data.py para calcular tarjetas históricas
        "player_appearances",    # Usada en populate_data.py para calcular tarjetas históricas
        "players",               # Usada en populate_data.py para tarjetas históricas
        "intl_results",          # Usada en export_to_json.py para historial general de enfrentamientos H2H
        "matches",               # Usada en export_to_json.py para historial de enfrentamientos H2H en mundiales
        "teams",                 # Usada en populate_data.py y export_to_json.py para H2H/tarjetas
        "cache_transfermarkt"    # Caché de consultas a la API de Transfermarkt (1,687 consultas)
    ]
    
    tables_to_drop = []
    if clean_all:
        print("\n--- Borrado Completo de Datos Históricos (Solo 2026 y Resultados finales) ---")
        tables_to_drop = unused_tables + pipeline_historical_tables
    else:
        print("\n--- Borrado Seguro de Tablas No Utilizadas (Mantiene pipeline ejecutable) ---")
        tables_to_drop = unused_tables
        
    for table in tables_to_drop:
        print(f"Eliminando tabla '{table}'...")
        cursor.execute(f"DROP TABLE IF EXISTS {table};")
        
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
