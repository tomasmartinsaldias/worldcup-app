import sqlite3
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'worldcup_combined.db')
JSON_PATH = os.path.join(BASE_DIR, 'data', 'wc2026_data.json')

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. Agregamos la columna a la tabla si no existe
    try:
        c.execute("ALTER TABLE scraped_wc2026_probable_squads ADD COLUMN exact_position TEXT")
    except sqlite3.OperationalError:
        pass # La columna ya existía
        
    # 2. Leemos el JSON que ya tiene los datos procesados
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # 3. Actualizamos la DB
    updated = 0
    for code, team in data.get('teams', {}).items():
        for p in team.get('squad', []):
            exact = p.get('exact_position')
            if exact:
                c.execute("UPDATE scraped_wc2026_probable_squads SET exact_position = ? WHERE player_name = ?", (exact, p['name']))
                updated += 1
                
    conn.commit()
    conn.close()
    print(f"Base de datos SQLite sincronizada exitosamente. {updated} jugadores actualizados con su posicion táctica exacta.")

if __name__ == '__main__':
    main()
