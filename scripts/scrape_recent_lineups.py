import json
import time
import requests
from bs4 import BeautifulSoup
from collections import Counter
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, 'data', 'wc2026_data.json')

# Map of major teams to FBref IDs to prevent searching and hitting captchas.
# More can be added later.
FBREF_MAP = {
    'ARG': 'f9fddd6e/Argentina-Men',
    'FRA': 'b1b36dcd/France-Men',
    'BRA': '304635c3/Brazil-Men',
    'ENG': '18bb7c10/England-Men',
    'ESP': 'b4ba665b/Spain-Men',
    'MEX': 'b009a548/Mexico-Men',
    'USA': '0f66725b/United-States-Men',
    'GER': 'c1e40422/Germany-Men',
    'POR': '4a1b4ea8/Portugal-Men',
    'ITA': '1d8ebcd6/Italy-Men'
}

REALISTIC_FORMATIONS = {
    'ARG': '4-4-2', 'FRA': '4-2-3-1', 'BRA': '4-2-3-1', 'ENG': '4-2-3-1', 
    'ESP': '4-3-3', 'GER': '4-2-3-1', 'POR': '4-3-3', 'ITA': '3-4-2-1', 
    'NED': '3-4-2-1', 'URU': '4-2-3-1', 'COL': '4-2-3-1', 'MEX': '4-3-3',
    'USA': '4-3-3', 'SEN': '4-2-3-1', 'MAR': '4-1-4-1', 'JPN': '3-4-2-1',
    'KOR': '4-4-2', 'CRO': '4-3-3', 'BEL': '4-2-3-1', 'SUI': '3-4-2-1',
    'ECU': '4-2-3-1', 'KSA': '4-3-3', 'QAT': '3-5-2', 'CAN': '4-4-2',
    'AUS': '4-4-2', 'TUN': '3-4-2-1', 'CRC': '5-4-1', 'WAL': '3-4-2-1',
    'SRB': '3-4-2-1', 'POL': '4-2-3-1', 'CHI': '4-3-3', 'PER': '4-2-3-1',
    'VEN': '4-3-3', 'PAR': '4-4-2', 'BOL': '5-3-2'
}

import random

def infer_lineup(team_data, team_code=""):
    squad = team_data.get('squad', [])
    valid_players = [p for p in squad if not p.get('is_injured')]
    
    # Sort by market value to pick the 'best' players
    valid_players.sort(key=lambda x: x.get('market_value_eur') or 0, reverse=True)
    
    # Determine realistic formation
    formation = REALISTIC_FORMATIONS.get(team_code)
    if not formation:
        formation = random.choice(['4-3-3', '4-2-3-1', '4-4-2', '3-5-2', '4-1-4-1'])
        
    formParts = [int(x) for x in formation.split('-')]
    nDef = formParts[0]
    nMid = formParts[1]
    nFwd = formParts[2]
    if len(formParts) == 4:
        nMid = formParts[1] + formParts[2]
        nFwd = formParts[3]
        
    gk = [p for p in valid_players if p.get('position') and 'portero' in p.get('position').lower()][:1]
    defenders = [p for p in valid_players if p.get('position') and 'defensa' in p.get('position').lower()][:nDef]
    mids = [p for p in valid_players if p.get('position') and ('centro' in p.get('position').lower() or 'medio' in p.get('position').lower())][:nMid]
    fwds = [p for p in valid_players if p.get('position') and 'delantero' in p.get('position').lower()][:nFwd]
    
    starting_xi = [p['name'] for p in gk + defenders + mids + fwds]
    
    return {
        "formation": formation,
        "source": "inferred_realistic",
        "starting_xi": starting_xi
    }

def scrape_fbref_formation(url_fragment):
    url = f"https://fbref.com/en/squads/{url_fragment}-Stats"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    try:
        time.sleep(3) # Rate limit protection for FBref
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return None
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        formations = []
        for td in soup.find_all('td', {'data-stat': 'formation'}):
            f = td.get_text(strip=True)
            if f and f != '':
                formations.append(f)
                
        if formations:
            # Most common in last 5 matches
            recent = formations[-5:]
            most_common = Counter(recent).most_common(1)[0][0]
            # Clean up diamond symbols some formations have in FBref
            return most_common.replace('◆', '').strip()
    except Exception as e:
        print(f"Error scraping {url_fragment}: {e}")
    return None

def main():
    if not os.path.exists(JSON_PATH):
        print(f"Error: {JSON_PATH} no encontrado.")
        return
        
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    teams = data.get('teams', {})
    
    print("Iniciando extracción de alineaciones de FBref...")
    for code, team in teams.items():
        if team.get('is_placeholder'):
            continue
            
        print(f"Procesando {code} - {team['name']}...")
        
        lineup_data = None
        if code in FBREF_MAP:
            formation = scrape_fbref_formation(FBREF_MAP[code])
            if formation:
                inferred = infer_lineup(team, code)
                inferred['formation'] = formation
                inferred['source'] = "fbref_recent_average"
                lineup_data = inferred
                print(f"  [+] Formación real obtenida: {formation}")
            else:
                print(f"  [-] Falló FBref, usando inferencia.")
                lineup_data = infer_lineup(team, code)
        else:
            lineup_data = infer_lineup(team, code)
            
        team['last_known_lineup'] = lineup_data

    # Guardar cambios
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print("\n¡wc2026_data.json actualizado con alineaciones tácticas!")

if __name__ == '__main__':
    main()
