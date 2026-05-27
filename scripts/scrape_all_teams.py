import json
import time
import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
import sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, 'data', 'wc2026_data.json')

def get_sofifa_position(player_name):
    url = f"https://sofifa.com/players?keyword={urllib.parse.quote(player_name)}"
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
    except Exception:
        pass
    return None

def main():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    teams = data.get('teams', {})
    
    for code, team in teams.items():
        if team.get('is_placeholder'): continue
        
        # Obtenemos los 16 mejores jugadores para asegurar titulares
        squad = sorted(team.get('squad', []), key=lambda x: x.get('market_value_eur') or 0, reverse=True)
        top_players = squad[:16]
        
        print(f"Scraping {team['name']}...")
        changed = False
        for p in top_players:
            if p.get('exact_position') and len(p['exact_position']) <= 3 and p['exact_position'] not in ['DEF', 'MID', 'FWD']:
                continue
                
            time.sleep(0.3)
            pos = get_sofifa_position(p['name'])
            if pos:
                p['exact_position'] = pos
                print(f"  [+] {p['name']} -> {pos}")
                changed = True
            else:
                g = p.get('position', '').lower()
                if 'portero' in g: p['exact_position'] = 'GK'
                elif 'defensa' in g: p['exact_position'] = 'CB'
                elif 'centro' in g or 'medio' in g: p['exact_position'] = 'CM'
                elif 'delantero' in g: p['exact_position'] = 'ST'
                else: p['exact_position'] = 'CM'
                
        if changed:
            with open(JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
