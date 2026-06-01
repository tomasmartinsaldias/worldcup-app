import sys
import os
import math
import sqlite3

def get_country_totals(db_path):
    """
    Obtiene el total de jugadores convocados por cada selección.
    """
    if not os.path.exists(db_path):
        return {}
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT pais, COUNT(*) FROM convocados GROUP BY pais")
    results = cursor.fetchall()
    conn.close()
    
    return {row[0]: row[1] for row in results}

def get_club_players_by_country(db_path, club_name):
    """
    Obtiene los jugadores que pertenecen al club especificado, agrupados por selección.
    Retorna: {pais: [(jugador1, club), (jugador2, club)]}
    """
    if not os.path.exists(db_path):
        return {}
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Buscamos coincidencias parciales por si hay variaciones como "Arsenal FC" o "Arsenal"
    # pero preferimos exactas. Usaremos LIKE '%club_name%' para ser más flexibles.
    cursor.execute("SELECT pais, jugador, equipo FROM convocados WHERE equipo LIKE ?", (f'%{club_name}%',))
    results = cursor.fetchall()
    conn.close()
    
    club_players = {}
    for pais, jugador, equipo_real in results:
        if pais not in club_players:
            club_players[pais] = []
        club_players[pais].append((jugador, equipo_real))
        
    return club_players

def recommend_matches_by_team(matches, favorite_club, db_path=None):
    """
    Calcula un score de recomendación para una lista de partidos basado en la
    proporción de jugadores del club favorito sobre el total de convocados por selección.
    """
    if db_path is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        db_path = os.path.join(base_dir, 'data', 'recommender_data', 'convocados.db')
        
    # Totales por selección
    country_counts = get_country_totals(db_path)
    if not country_counts:
        return {"error": "Base de datos de convocados no encontrada o vacía."}
        
    # Jugadores del club
    club_players = get_club_players_by_country(db_path, favorite_club)
    
    # Verificación si no hay jugadores
    if not club_players:
        return {"error": f"No se encontraron jugadores convocados pertenecientes al club '{favorite_club}'."}
        
    match_scores = []
    
    for team1, team2 in matches:
        # Obtenemos los totales. Mantenemos esto por si se quiere volver a usar, 
        # pero la proporción ahora será sobre el total de jugadores del club
        t1_total = country_counts.get(team1, 26) 
        t2_total = country_counts.get(team2, 26)
        
        t1_players = club_players.get(team1, [])
        t2_players = club_players.get(team2, [])
        
        team1_count = len(t1_players)
        team2_count = len(t2_players)
        
        # Calcular el total de jugadores del club encontrados en TODAS las selecciones
        total_club_players = sum(len(players) for players in club_players.values())
        
        # Nueva Proporción: Jugadores de ese club en la nación / Total de jugadores de ese club
        t1_prop = team1_count / total_club_players if total_club_players > 0 else 0
        t2_prop = team2_count / total_club_players if total_club_players > 0 else 0
        
        total_score = t1_prop + t2_prop
        
        # Normalización
        # f(x) = 1 - exp(-k * x)
        # Ajustamos k para que refleje los nuevos rangos de proporción (generalmente mayores)
        k = 4
        normalized_score = 1 - math.exp(-k * total_score) if total_score > 0 else 0.0
        
        match_scores.append({
            'match': f"{team1} vs {team2}",
            'team1': team1,
            'team2': team2,
            'team1_ratio': f"{team1_count}/{total_club_players}",
            'team2_ratio': f"{team2_count}/{total_club_players}",
            'raw_score': round(total_score, 4),
            'normalized_score': round(normalized_score, 4),
            'contributing_players': {
                team1: [f"{p[0]} ({p[1]})" for p in t1_players],
                team2: [f"{p[0]} ({p[1]})" for p in t2_players]
            }
        })
        
    match_scores.sort(key=lambda x: x['normalized_score'], reverse=True)
    return match_scores

if __name__ == "__main__":
    sample_matches = [
        ("Inglaterra", "Países Bajos"), # Nota: Asegurar que los nombres coinciden con la DB
        ("España", "Alemania"),
        ("Brasil", "Croacia"),
        ("Portugal", "Marruecos"),
        ("Inglaterra", "Francia")
    ]
    
    fav_club = "Real Madrid"
    print(f"--- Recomendando partidos para fan de: {fav_club} ---")
    
    results = recommend_matches_by_team(sample_matches, fav_club)
    
    if isinstance(results, dict) and "error" in results:
        print("Error:", results["error"])
    else:
        for idx, r in enumerate(results, 1):
            print(f"{idx}. {r['match']} | Score: {r['normalized_score']} (Proporciones: {r['team1_ratio']} + {r['team2_ratio']} = {r['raw_score']})")
            print(f"   Jugadores encontrados:")
            for team, players in r['contributing_players'].items():
                if players:
                    print(f"      - {team}: {', '.join(players)}")
            print()
