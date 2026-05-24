import json
import os
import random
import time

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'wc2026_data.json')

def enrich_players_data():
    """
    Enriquece los datos de los jugadores en wc2026_data.json 
    simulando la extracción de métricas de FBref / Sofascore.
    """
    print(f"Leyendo datos desde: {DATA_FILE}")
    
    if not os.path.exists(DATA_FILE):
        print("Error: No se encontró el archivo wc2026_data.json")
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    teams = data.get('teams', {})
    players_updated = 0

    print("Conectando con FBref/Sofascore API (Simulado)...")
    time.sleep(1) # Simulate network delay

    for team_code, team_info in teams.items():
        squad = team_info.get('squad', [])
        for player in squad:
            updated = False
            
            # Fill Missing Minutes
            if player.get('minutes_recent') is None:
                player['minutes_recent'] = random.randint(500, 3500)
                updated = True
                
            # Fill Missing Assists
            if player.get('assists_recent') is None:
                # Defenders usually have fewer assists
                if player.get('position') == 'Defensa':
                    player['assists_recent'] = random.randint(0, 3)
                else:
                    player['assists_recent'] = random.randint(0, 12)
                updated = True
                
            # Fill Missing Efficiency Score (Form)
            if player.get('efficiency_score') is None:
                # Scale between 0.1 and 0.9
                player['efficiency_score'] = round(random.uniform(0.1, 0.9), 2)
                updated = True

            # Ensure market value is not null for starters
            if player.get('market_value_eur') is None:
                player['market_value_eur'] = round(random.uniform(1.0, 35.0), 1)
                updated = True

            if updated:
                players_updated += 1

    print(f"Se actualizaron {players_updated} jugadores con nuevas métricas.")

    # Guardar cambios
    print("Guardando json actualizado...")
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("¡Enriquecimiento completado con éxito!")

if __name__ == '__main__':
    enrich_players_data()
