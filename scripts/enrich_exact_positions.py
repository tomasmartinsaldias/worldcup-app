import json
import time
import requests
from bs4 import BeautifulSoup
import os
import urllib.parse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, 'data', 'wc2026_data.json')

import sys
sys.stdout.reconfigure(encoding='utf-8')

def get_sofifa_position(player_name, country_name):
    # Buscamos directo por nombre para maximizar hits
    query = player_name
    url = f"https://sofifa.com/players?keyword={urllib.parse.quote(query)}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        table = soup.find('table', class_='table')
            
        if table:
            first_row = table.find('tbody').find('tr')
            if first_row:
                pos_span = first_row.find('span', class_='pos')
                if pos_span:
                    return pos_span.text.strip().upper()
    except Exception as e:
        print(f"  [!] Error buscando {player_name}: {e}")
        
    return None

def fallback_position(generic_pos):
    # Fallback heuristico si sofifa falla
    g = generic_pos.lower()
    if 'portero' in g: return 'GK'
    if 'defensa' in g: return 'CB'
    if 'centro' in g or 'medio' in g: return 'CM'
    if 'delantero' in g: return 'ST'
    return 'CM'

def main():
    if not os.path.exists(JSON_PATH):
        print("JSON no encontrado")
        return
        
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    teams = data.get('teams', {})
    
    print("Iniciando extracción de posiciones exactas desde SoFIFA (EA FC 25)...")
    
    # Solo procesamos los titulares para ahorrar tiempo (son los que dibujamos en la cancha)
    for code, team in teams.items():
        if team.get('is_placeholder'): continue
        if code not in ['ARG', 'JPN', 'MAR']: continue
        
        lineup = team.get('last_known_lineup')
        if not lineup or not lineup.get('starting_xi'):
            continue
            
        print(f"Procesando {team['name']}...")
        starters = lineup['starting_xi']
        
        for player in team.get('squad', []):
            # Nos interesa saber la posicion exacta de los que son titulares
            # pero tambien le asignamos a todo el plantel si es facil
            # Para no tardar 20 minutos, solo buscamos los titulares en sofifa.
            if player['name'] in starters:
                if 'exact_position' not in player or not player['exact_position']:
                    time.sleep(0.5) # Anti-ban
                    pos = get_sofifa_position(player['name'], team['name'])
                    if pos:
                        player['exact_position'] = pos
                        print(f"  [+] {player['name']} -> {pos}")
                    else:
                        fallback = fallback_position(player.get('position', ''))
                        player['exact_position'] = fallback
                        print(f"  [-] {player['name']} no encontrado. Fallback -> {fallback}")
            else:
                # Suplentes: heuristica rapida
                if 'exact_position' not in player:
                    player['exact_position'] = fallback_position(player.get('position', ''))

        # Guardar cada X equipos por si corta
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    print("Finalizado. Posiciones EA FC inyectadas.")

if __name__ == '__main__':
    main()
