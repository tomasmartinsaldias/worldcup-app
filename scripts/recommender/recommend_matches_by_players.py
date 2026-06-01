import sys
import os
import math
import pandas as pd

# Añadimos el directorio raíz al path para poder importar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.recommender.recommend_similar_players import get_similar_players, load_data

def recommend_matches(matches, favorite_player, json_path=None):
    """
    Calcula un score de recomendación para una lista de partidos basado en el 
    jugador favorito del usuario y sus jugadores más similares.
    
    Args:
        matches (list of tuples): Lista de partidos, ej. [('Argentina', 'France'), ('Brazil', 'Germany')]
        favorite_player (str): Nombre del jugador favorito
        json_path (str, optional): Ruta al archivo JSON con los datos.
        
    Returns:
        list of dicts: Lista de partidos con sus scores de recomendación, ordenados de mayor a menor.
    """
    if json_path is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        json_path = os.path.join(base_dir, 'data', 'player_similarity', 'player_similarity_codebase.json')
        
    # Obtener dataframe principal para buscar información de los jugadores
    try:
        df = load_data(json_path)
    except FileNotFoundError:
        return {"error": "Archivo de similitud no encontrado."}

    # 1 y 2. Integrar la función de jugadores similares y consumir los datos
    similar_players_result = get_similar_players(favorite_player, 5, json_path)
    
    if isinstance(similar_players_result, dict) and "error" in similar_players_result:
        return similar_players_result
        
    # 3. Diccionario de jugadores de interés con su similitud y equipo (nacionalidad)
    players_of_interest = {}
    
    # Buscamos al jugador favorito para obtener su nacionalidad real en la DB
    fav_player_rows = df[df['short_name'].str.lower() == favorite_player.lower()]
    if fav_player_rows.empty:
        return {"error": f"Jugador favorito '{favorite_player}' no encontrado."}
    
    # Si hay varios con el mismo nombre, tomamos el primero
    fav_nationality = fav_player_rows.iloc[0]['nationality_name']
    fav_name = fav_player_rows.iloc[0]['short_name']
    
    # El jugador favorito tiene similitud 1.0
    players_of_interest[fav_name.lower()] = {
        'name': fav_name,
        'similarity': 1.0,
        'nationality': fav_nationality
    }
    
    # Añadimos los jugadores similares.
    # get_similar_players devuelve una lista de diccionarios con una columna 'distance' (distancia coseno).
    # Convertimos la distancia coseno a similitud coseno: similitud = 1 - distancia
    for player in similar_players_result:
        sim = 1.0 - player['distance']
        players_of_interest[player['short_name'].lower()] = {
            'name': player['short_name'],
            'similarity': sim,
            'nationality': player['nationality_name']
        }
        
    match_scores = []
    
    for team1, team2 in matches:
        team1_score = 0.0
        team2_score = 0.0
        
        team1_players_found = []
        team2_players_found = []
        
        # Evaluamos los jugadores de interés para ver si participan en este partido
        for p_key, data in players_of_interest.items():
            if data['nationality'] == team1:
                team1_score += data['similarity']
                team1_players_found.append((data['name'], round(data['similarity'], 3)))
            elif data['nationality'] == team2:
                team2_score += data['similarity']
                team2_players_found.append((data['name'], round(data['similarity'], 3)))
                
        # Score acumulado del partido
        total_score = team1_score + team2_score
        
        # 4. Normalización
        # Usamos una transformación no lineal que mapea [0, inf) a [0, 1)
        # f(x) = 1 - exp(-x) es ideal porque empieza en 0 y crece asintóticamente hacia 1.
        # Ajustamos el factor dentro de exp() si queremos que sea más suave o más brusco.
        # Con x=1 (solo el fav), score = ~0.63. Con x=2.7, score = ~0.93.
        normalized_score = 1 - math.exp(-total_score)
        
        match_scores.append({
            'match': f"{team1} vs {team2}",
            'team1': team1,
            'team2': team2,
            'raw_score': round(total_score, 4),
            'normalized_score': round(normalized_score, 4),
            'contributing_players': {
                team1: team1_players_found,
                team2: team2_players_found
            }
        })
        
    # 5. Devolver ordenado por score descendente
    match_scores.sort(key=lambda x: x['normalized_score'], reverse=True)
    
    return match_scores

if __name__ == "__main__":
    # Ejemplo de uso
    sample_matches = [
        ("Argentina", "France"),
        ("Spain", "Germany"),
        ("Brazil", "Croatia"),
        ("Portugal", "Morocco"),
        ("Netherlands", "England")
    ]
    
    # Prueba con L. Messi
    fav_player = "L. Messi"
    print(f"--- Recomendando partidos para fan de: {fav_player} ---")
    
    results = recommend_matches(sample_matches, fav_player)
    
    if isinstance(results, dict) and "error" in results:
        print("Error:", results["error"])
    else:
        for idx, r in enumerate(results, 1):
            print(f"{idx}. {r['match']} | Score: {r['normalized_score']} (Raw: {r['raw_score']})")
            print(f"   Jugadores que suman:")
            for team, players in r['contributing_players'].items():
                if players:
                    print(f"      - {team}: {', '.join([f'{p[0]} ({p[1]})' for p in players])}")
            print()
