import os
import sqlite3
import requests
import json
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'worldcup_combined.db')

# Mapping for edge cases and teams not matching REST Countries directly
CUSTOM_MAPPING = {
    'USA': 'United States',
    'IR Iran': 'Iran',
    'South Korea': 'South Korea',
    'England': 'https://flagcdn.com/w320/gb-eng.png',
    'Scotland': 'https://flagcdn.com/w320/gb-sct.png',
    'Wales': 'https://flagcdn.com/w320/gb-wls.png',
    'Curaçao': 'Curacao',
    'Curaao': 'Curacao',
    "Côte d'Ivoire": "Ivory Coast",
    "Cte d'Ivoire": "Ivory Coast",
    'DR Congo': 'DR Congo', # Might need specific query
    'Czech Republic': 'Czechia',
    'Bosnia and Herzegovina': 'Bosnia and Herzegovina',
    'Cabo Verde': 'Cape Verde',
}

def get_flag_url(team_name):
    # Check if we have a hardcoded URL (like England)
    if team_name in CUSTOM_MAPPING and CUSTOM_MAPPING[team_name].startswith('http'):
        return CUSTOM_MAPPING[team_name]
        
    query_name = CUSTOM_MAPPING.get(team_name, team_name)
    
    try:
        # Search by name
        url = f"https://restcountries.com/v3.1/name/{query_name}?fullText=false"
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            if len(data) > 0:
                # Return png flag
                return data[0].get('flags', {}).get('png')
                
        # Fallback to search without fulltext restriction or just parts
        parts = query_name.split(' ')
        if len(parts) > 1:
            url = f"https://restcountries.com/v3.1/name/{parts[0]}"
            resp = requests.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if len(data) > 0:
                    return data[0].get('flags', {}).get('png')
                    
    except Exception as e:
        print(f"Error fetching {team_name}: {e}")
        
    return None

def main():
    print("Iniciando integración de banderas con REST Countries API...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure column exists
    try:
        cursor.execute("ALTER TABLE wc2026_teams ADD COLUMN flag_url TEXT;")
        print("Columna flag_url añadida a wc2026_teams.")
    except sqlite3.OperationalError:
        print("La columna flag_url ya existe.")
        
    cursor.execute("SELECT id, team_name, fifa_code FROM wc2026_teams WHERE is_placeholder = 0;")
    teams = cursor.fetchall()
    
    success_count = 0
    
    for row in teams:
        t_id, t_name, code = row
        print(f"Buscando bandera para: {t_name} ({code})...")
        
        flag_url = get_flag_url(t_name)
        if flag_url:
            cursor.execute("UPDATE wc2026_teams SET flag_url = ? WHERE id = ?", (flag_url, t_id))
            print(f"  [+] Encontrada: {flag_url}")
            success_count += 1
        else:
            print(f"  [-] No se encontró bandera para {t_name}")
            
        time.sleep(0.5) # Be nice to the API
        
    conn.commit()
    conn.close()
    
    print(f"\nProceso finalizado. {success_count}/{len(teams)} banderas actualizadas.")

if __name__ == '__main__':
    main()
