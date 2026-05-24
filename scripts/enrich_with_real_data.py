import json
import sqlite3
import pandas as pd
import unicodedata
import difflib
import math

def normalize(name):
    if not isinstance(name, str): return ""
    name = unicodedata.normalize('NFD', name.lower())
    return "".join(c for c in name if c.isalpha() or c == ' ').strip()

def main():
    print("Iniciando enriquecimiento con datos reales...")
    
    # Cargar JSON
    with open('data/wc2026_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Cargar SQLite para Market Values
    conn = sqlite3.connect('data/worldcup_combined.db')
    cursor = conn.cursor()
    cursor.execute("SELECT player_name, market_value_eur FROM scraped_wc2026_probable_squads WHERE market_value_eur IS NOT NULL")
    db_players = cursor.fetchall()
    
    db_dict = {}
    for row in db_players:
        n = normalize(row[0])
        if n: db_dict[n] = row[1]
    db_names = list(db_dict.keys())
    
    # Cargar Golden Dataset para Estadísticas (goles, asistencias, minutos)
    df = pd.read_csv('data/worldcup-2026-predicts/fifa_world_cup_2026_golden_dataset.csv')
    df['norm_name'] = df['name'].apply(normalize)
    golden_dict = {}
    for _, row in df.iterrows():
        n = row['norm_name']
        if n:
            golden_dict[n] = {
                'minutes': row['minutes'],
                'assists': row['assists'],
                'goals': row['goals'],
                'efficiency_score': row['efficiency_score']
            }
    golden_names = list(golden_dict.keys())
    
    matched_db = 0
    matched_golden = 0
    total_players = 0
    
    for team_code, team in data['teams'].items():
        for p in team['squad']:
            total_players += 1
            norm_name = normalize(p['name'])
            
            # --- 1. MARKET VALUE ---
            # Borrar cualquier valor random previo si queremos estar seguros
            # Pero en la sesión anterior pusimos random_value = random.uniform(1.0, 35.0) en enrich_players_fbref.py
            # Intentamos match real:
            matches = difflib.get_close_matches(norm_name, db_names, n=1, cutoff=0.7)
            if matches:
                p['market_value_eur'] = db_dict[matches[0]]
                matched_db += 1
            else:
                p['market_value_eur'] = None # Null real, no inventado
                
            # --- 2. STATS GLOBALES ---
            matches_golden = difflib.get_close_matches(norm_name, golden_names, n=1, cutoff=0.7)
            if matches_golden:
                stats = golden_dict[matches_golden[0]]
                p['minutes_recent'] = int(stats['minutes']) if not pd.isna(stats['minutes']) else 0
                p['assists_recent'] = int(stats['assists']) if not pd.isna(stats['assists']) else 0
                
                # Actualizar goals si el golden dataset tiene más info
                g = int(stats['goals']) if not pd.isna(stats['goals']) else 0
                if g > (p.get('goals') or 0):
                    p['goals'] = g
                    
                p['efficiency_score'] = float(stats['efficiency_score']) if not pd.isna(stats['efficiency_score']) else None
                matched_golden += 1
            else:
                # Si no hace match, quitamos los valores random inventados
                p['minutes_recent'] = 0
                p['assists_recent'] = 0
                p['efficiency_score'] = None
                
    with open('data/wc2026_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Total Jugadores procesados: {total_players}")
    print(f"Cruces exitosos de Valor Mercado (DB): {matched_db}")
    print(f"Cruces exitosos de Estadísticas (Golden CSV): {matched_golden}")
    print("El archivo wc2026_data.json ha sido purgado de datos hardcodeados y actualizado.")

if __name__ == '__main__':
    main()
