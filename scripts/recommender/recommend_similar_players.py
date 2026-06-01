import json
import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import pairwise_distances

def load_data(json_path):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"No se encontró el archivo: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.DataFrame(data)

def get_similar_players(player_name, k, json_path=None):
    """
    Busca los k jugadores más similares a 'player_name' utilizando la distancia euclídea
    sobre atributos normalizados.
    
    Si hay varios jugadores con el mismo nombre, calcula la distancia a cualquiera de ellos
    y devuelve los k más similares (excluyendo a los propios jugadores buscados).
    """
    
    if json_path is None:
        # Por defecto, buscar en la ruta relativa desde la raíz del proyecto
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        json_path = os.path.join(base_dir, 'data', 'player_similarity', 'player_similarity_codebase.json')
        
    df = load_data(json_path)
    
    # 1. Buscar los jugadores que coincidan con el nombre (ignorando mayúsculas/minúsculas)
    target_players = df[df['short_name'].str.lower() == player_name.lower()]
    
    if target_players.empty:

        return {"error": f"Jugador '{player_name}' no encontrado en la base de datos."}
    
    target_indices = target_players.index.tolist()
    
    # 2. Definir las columnas de características numéricas a utilizar
    feature_cols = ['overall', 'potential', 'age', 'height_cm', 'weight_kg', 'skill_moves', 
    'pace', 'passing', 'shooting', 'dribbling', 'defending', 'physic',
    "attacking_crossing", "attacking_finishing", "attacking_heading_accuracy", 
    "attacking_short_passing", "attacking_volleys", "skill_dribbling", 
    "skill_curve", "skill_fk_accuracy", "skill_long_passing", 
    "skill_ball_control", "movement_acceleration", "movement_sprint_speed", 
    "movement_agility", "movement_reactions", "movement_balance", 
    "power_shot_power", "power_jumping", "power_stamina", 
    "power_strength", "power_long_shots", "mentality_aggression", 
    "mentality_interceptions", "mentality_positioning", "mentality_vision", 
    "mentality_penalties", "mentality_composure", "defending_marking_awareness", 
    "defending_standing_tackle", "defending_sliding_tackle"
    ]
    
    # Rellenar posibles valores nulos con 0 para evitar errores en el cálculo
    features = df[feature_cols].fillna(0)
    
    # 3. Normalizar los datos
    # Como acordamos, usamos StandardScaler para que todas las variables pesen igual
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    
    # 4. Calcular distancias
    target_scaled = scaled_features[target_indices]
    
    # Matriz de distancias entre los objetivos y todos los jugadores
    distances = pairwise_distances(target_scaled, scaled_features, metric='cosine')
    
    # Si hay múltiples coincidencias del mismo nombre, tomamos la distancia mínima a cualquiera de ellos
    min_distances = distances.min(axis=0)
    
    # Añadimos la distancia calculada al DataFrame
    df['distance'] = min_distances
    
    # 5. Filtrar a los propios jugadores buscados y tomar los top K
    df_result = df.drop(index=target_indices)
    top_k_df = df_result.sort_values(by='distance').head(k)
    
    # 6. Devolver los registros completos como una lista de diccionarios JSON
    return top_k_df.to_dict(orient='records')

print(get_similar_players("Lamine Yamal", 5))