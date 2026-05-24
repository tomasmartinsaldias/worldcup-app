import json
import os
import requests
import random
from collections import Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, 'data', 'wc2026_data.json')

# Configuración API-Football (v3)
API_KEY = os.environ.get('API_FOOTBALL_KEY')
API_HOST = "v3.football.api-sports.io"
HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
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

def infer_lineup(team_data, team_code=""):
    """ Genera el 11 inicial combinando la táctica (real o simulada) con los valores de mercado. """
    squad = team_data.get('squad', [])
    valid_players = [p for p in squad if not p.get('is_injured')]
    valid_players.sort(key=lambda x: x.get('market_value_eur') or 0, reverse=True)
    
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

def get_team_id(team_name):
    """ Busca el ID numérico del equipo en la API Externa """
    url = f"https://{API_HOST}/teams?search={team_name}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        if data.get('results', 0) > 0:
            return data['response'][0]['team']['id']
    return None

def fetch_api_formation(team_name):
    """ Consulta el historial de los últimos 5 partidos y retorna la formación moda. """
    try:
        team_id = get_team_id(team_name)
        if not team_id:
            return None
        
        # Últimos 5 fixtures oficiales
        url = f"https://{API_HOST}/fixtures?team={team_id}&last=5"
        resp = requests.get(url, headers=HEADERS).json()
        fixtures = [f['fixture']['id'] for f in resp.get('response', [])]
        
        formations = []
        for fix_id in fixtures:
            l_url = f"https://{API_HOST}/fixtures/lineups?fixture={fix_id}"
            l_resp = requests.get(l_url, headers=HEADERS).json()
            for lineup in l_resp.get('response', []):
                if lineup['team']['id'] == team_id:
                    formation = lineup.get('formation')
                    if formation:
                        formations.append(formation)
                        
        if formations:
            return Counter(formations).most_common(1)[0][0]
            
    except Exception as e:
        print(f"Error llamando a la API: {e}")
    return None

def main():
    if not os.path.exists(JSON_PATH):
        print(f"Error: {JSON_PATH} no encontrado.")
        return
        
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    teams = data.get('teams', {})
    
    if not API_KEY:
        print("=================================================================")
        print(" AVISO: No se detectó la variable de entorno API_FOOTBALL_KEY.")
        print(" El script utilizará las estadísticas tácticas realistas internas.")
        print(" Para conectarlo a la API en vivo, ejecuta en tu terminal local:")
        print(" $env:API_FOOTBALL_KEY=\"tu_clave_gratuita\"")
        print("=================================================================\n")
    
    print("Iniciando extracción de alineaciones (API Externa Web)...")
    
    for code, team in teams.items():
        if team.get('is_placeholder'):
            continue
            
        print(f"Procesando {code} - {team['name']}...")
        
        lineup_data = None
        if API_KEY:
            formation = fetch_api_formation(team['name'])
            if formation:
                inferred = infer_lineup(team, code)
                inferred['formation'] = formation
                inferred['source'] = "api-football"
                lineup_data = inferred
                print(f"  [+] Formación API-Football obtenida: {formation}")
            else:
                print(f"  [-] Error obteniendo de API. Usando fallback analítico.")
                lineup_data = infer_lineup(team, code)
        else:
            lineup_data = infer_lineup(team, code)
            
        team['last_known_lineup'] = lineup_data

    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print("\n¡wc2026_data.json actualizado correctamente con los datos de la web!")

if __name__ == '__main__':
    main()
