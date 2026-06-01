import json
import os
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import pairwise_distances

# Set stdout to utf-8 to prevent charmap encode errors on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

class DataLoader:
    @staticmethod
    def load_data(filepath):
        """Carga datos desde un archivo JSON."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if not data:
            raise ValueError(f"JSON file is empty: {filepath}")
            
        df = pd.DataFrame(data)
        return df

class DataPreprocessor:
    @staticmethod
    def preprocess(df):
        """Preprocesa el DataFrame aislando las variables numéricas y aplicando StandardScaler."""
        # Seleccionar todas las columnas numéricas
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Manejo de valores nulos imputando con 0 (ya que pueden ser atributos que no aplican)
        df_numeric = df[numeric_cols].fillna(0)
        
        # Estandarizar
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(df_numeric)
        
        # Retornar las características numéricas procesadas y los nombres de los jugadores
        return scaled_features, df['short_name'].values

class ClusteringEngine:
    def __init__(self, n_clusters=5, metric='euclidean', linkage='ward'):
        self.model = AgglomerativeClustering(n_clusters=n_clusters, metric=metric, linkage=linkage)
        
    def fit_predict(self, features):
        """Entrena el modelo y predice los clusters."""
        return self.model.fit_predict(features)
        
    @staticmethod
    def find_representatives(features, labels, player_names):
        """Calcula el centroide de cada cluster y encuentra el jugador más representativo."""
        n_clusters = len(np.unique(labels))
        representatives = {}
        
        for cluster_id in range(n_clusters):
            # Obtener índices de los jugadores en este cluster
            cluster_indices = np.where(labels == cluster_id)[0]
            cluster_features = features[cluster_indices]
            cluster_names = player_names[cluster_indices]
            
            # Calcular el centroide (media de las características de este cluster)
            centroid = cluster_features.mean(axis=0).reshape(1, -1)
            
            # Calcular distancia euclidiana al centroide
            distances = pairwise_distances(cluster_features, centroid, metric='euclidean').flatten()
            
            # Encontrar el jugador con la distancia mínima
            closest_idx = np.argmin(distances)
            representative_name = cluster_names[closest_idx]
            
            # Almacenar con base 1 como pide el formato
            representatives[cluster_id + 1] = representative_name
            
        return representatives

class PositionFactory:
    """Factory Pattern para manejar la configuración específica por posición."""
    base_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 
        '..', '..', 'data', 'clustering_players'
    ))
    
    positions = {
        'Goalkeepers': 'player_clustering_goalkeeper.json',
        'Defenders': 'player_clustering_defender.json',
        'Midfielders': 'player_clustering_midfielder.json',
        'Strikers': 'player_clustering_striker.json'
    }
    
    @classmethod
    def get_filepath(cls, position_name):
        filename = cls.positions.get(position_name)
        if not filename:
            raise ValueError(f"Unknown position: {position_name}")
        return os.path.join(cls.base_path, filename)

def main():
    positions = ['Goalkeepers', 'Defenders', 'Midfielders', 'Strikers']
    
    for position in positions:
        try:
            # 1. Obtener ruta mediante Factory
            filepath = PositionFactory.get_filepath(position)
            
            # 2. Ingesta de datos
            df = DataLoader.load_data(filepath)
            
            # 3. Preprocesamiento (Aislamiento de variables y normalización)
            features, player_names = DataPreprocessor.preprocess(df)
            
            # 4. Clustering (HAC con k=5, distancia euclidiana y ward linkage)
            engine = ClusteringEngine(n_clusters=5)
            labels = engine.fit_predict(features)
            
            # 5. Identificación de representantes
            representatives = engine.find_representatives(features, labels, player_names)
            
            # 6. Formato de Salida
            print(f"HAC {position}:")
            # Ordenamos para asegurar que se impriman del 1 al 5 en orden
            for cluster_id in sorted(representatives.keys()):
                rep_name = representatives[cluster_id]
                print(f"Cluster {cluster_id} = {rep_name}")
            print() # Espacio entre posiciones
            
        except Exception as e:
            print(f"Error processing {position}: {str(e)}\n")

if __name__ == "__main__":
    main()
