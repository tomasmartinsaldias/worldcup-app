import json
import os
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, normalize
from sklearn.cluster import AgglomerativeClustering, KMeans
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
        
        # Eliminar 'overall' de las características numéricas si está presente
        if 'overall' in numeric_cols:
            numeric_cols.remove('overall')
            
        # Manejo de valores nulos imputando con 0 (ya que pueden ser atributos que no aplican)
        df_numeric = df[numeric_cols].fillna(0)
        
        # Estandarizar
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(df_numeric)
        
        # Guardamos 'overall' (imputado con la media o 50 si por alguna razón falta)
        overalls = df['overall'].fillna(50).values
        
        # Retornar las características numéricas procesadas, nombres y overalls
        return scaled_features, df['long_name'].values, overalls

class ClusteringEngine:
    def __init__(self, n_clusters=5, metric='cosine', linkage='average'):
        self.model = AgglomerativeClustering(n_clusters=n_clusters, metric=metric, linkage=linkage)
        
    def fit_predict(self, features):
        """Entrena el modelo y predice los clusters."""
        return self.model.fit_predict(features)
        
    @staticmethod
    def find_representatives(labels, player_names, overalls):
        """Selecciona al jugador con mayor overall dentro de cada cluster."""
        n_clusters = len(np.unique(labels))
        representatives = {}
        
        for cluster_id in range(n_clusters):
            cluster_indices = np.where(labels == cluster_id)[0]
            cluster_names = player_names[cluster_indices]
            cluster_overalls = overalls[cluster_indices]

            # Representante = jugador con mayor overall en el cluster
            best_idx = np.argmax(cluster_overalls)
            representatives[cluster_id + 1] = {
                'name': cluster_names[best_idx],
                'overall': int(cluster_overalls[best_idx])
            }
            
        return representatives

class KMeansEngine:
    """Clustering mediante KMeans con distancia coseno (a través de normalización L2).
    Normalizar los vectores a longitud unitaria hace que la distancia euclidiana
    sea equivalente a la distancia coseno, permitiendo usar KMeans estandar.
    """
    def __init__(self, n_clusters=5, random_state=42):
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init='auto')
    
    def fit_predict(self, features):
        """Normaliza a L2 y predice los clusters usando KMeans."""
        # Normalización L2 hace que la distancia euclidiana ≈ distancia coseno
        features_normalized = normalize(features, norm='l2')
        self.labels_ = self.model.fit_predict(features_normalized)
        self.features_normalized_ = features_normalized
        return self.labels_
    
    def find_representatives(self, player_names, overalls):
        """Selecciona al jugador con mayor overall dentro de cada cluster."""
        n_clusters = len(np.unique(self.labels_))
        representatives = {}

        for cluster_id in range(n_clusters):
            cluster_indices = np.where(self.labels_ == cluster_id)[0]
            cluster_names = player_names[cluster_indices]
            cluster_overalls = overalls[cluster_indices]

            # Representante = jugador con mayor overall en el cluster
            best_idx = np.argmax(cluster_overalls)
            representatives[cluster_id + 1] = {
                'name': cluster_names[best_idx],
                'overall': int(cluster_overalls[best_idx])
            }

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
        'Strikers': 'player_clustering_striker.json',
        "Wingers" : 'player_clustering_wingers.json'
    }
    
    @classmethod
    def get_filepath(cls, position_name):
        filename = cls.positions.get(position_name)
        if not filename:
            raise ValueError(f"Unknown position: {position_name}")
        return os.path.join(cls.base_path, filename)

def main():
    positions_clusters = {
        'Goalkeepers': 3,
        'Defenders': 5,
        'Midfielders': 7,
        'Strikers': 3,
        'Wingers': 5
    }
    
    for position, n_clusters in positions_clusters.items():
        try:
            # 1. Obtener ruta mediante Factory
            filepath = PositionFactory.get_filepath(position)
            
            # 2. Ingesta de datos
            df = DataLoader.load_data(filepath)
            
            # 3. Preprocesamiento
            features, player_names, overalls = DataPreprocessor.preprocess(df)

            # -------------------------------------------------------
            # 4a. HAC (Hierarchical Agglomerative Clustering) 
            # -------------------------------------------------------
            hac_engine = ClusteringEngine(n_clusters=n_clusters, metric='cosine', linkage='average')
            hac_labels = hac_engine.fit_predict(features)
            hac_reps = hac_engine.find_representatives(hac_labels, player_names, overalls)

            print(f"HAC {position}:")
            for cluster_id in sorted(hac_reps.keys()):
                rep = hac_reps[cluster_id]
                print(f"  Cluster {cluster_id} = {rep['name']} (overall: {rep['overall']})")

            # -------------------------------------------------------
            # 4b. KMeans (con distancia coseno vía normalización L2)
            # -------------------------------------------------------
            kmeans_engine = KMeansEngine(n_clusters=n_clusters)
            kmeans_engine.fit_predict(features)
            kmeans_reps = kmeans_engine.find_representatives(player_names, overalls)

            print(f"KMeans {position}:")
            for cluster_id in sorted(kmeans_reps.keys()):
                rep = kmeans_reps[cluster_id]
                print(f"  Cluster {cluster_id} = {rep['name']} (overall: {rep['overall']})")
            
            print() # Espacio entre posiciones
            
        except Exception as e:
            print(f"Error processing {position}: {str(e)}\n")

if __name__ == "__main__":
    main()
