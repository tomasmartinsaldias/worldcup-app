import json
import os
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import pairwise_distances, silhouette_score

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
        """Preprocesa el DataFrame aislando las variables numéricas, imputando con la mediana,
        aplicando StandardScaler y PCA (excluyendo la primera componente principal para quedarse con la geometría del estilo).
        """
        # Seleccionar todas las columnas numéricas
        exclude_cols = ['overall', 'Cluster_ID', 'id']
        numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns.tolist() if col not in exclude_cols]
        
        # Asegurarnos de que height_cm y weight_kg están en la lista
        for col in ['height_cm', 'weight_kg']:
            if col in df.columns and col not in numeric_cols:
                numeric_cols.append(col)
                
        df_numeric = df[numeric_cols].apply(lambda col: col.fillna(col.median()))
        df_numeric = df_numeric.fillna(0)
        
        # StandardScaler
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(df_numeric)
        
        # PCA
        pca = PCA()
        pca_all = pca.fit_transform(scaled_features)
        
        # Componentes para >= 80% varianza explicada
        cum_var = np.cumsum(pca.explained_variance_ratio_)
        n_components = np.argmax(cum_var >= 0.80) + 1
        
        # Omitir PC1 (columna 0)
        features_pca_B = pca_all[:, 1:n_components]
        
        # Guardamos 'overall' (imputado con la mediana o 50 si falta)
        overall_median = df['overall'].median() if 'overall' in df.columns else 50
        if pd.isna(overall_median):
            overall_median = 50
        overalls = df['overall'].fillna(overall_median).values
        
        # Retornar las características normalizadas, nombres y overalls
        return features_pca_B, df['long_name'].values, overalls

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
    """Clustering mediante KMeans con distancia coseno (sobre características ya pre-normalizadas a L2).
    La optimización de la varianza basada en distancia euclidiana de KMeans sobre
    la hiperesfera unitaria equivale matemáticamente a maximizar la similitud del Coseno.
    """
    def __init__(self, n_clusters=5, random_state=42):
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init='auto')
    
    def fit_predict(self, features):
        """Predice los clusters usando KMeans directamente sobre las características L2."""
        self.labels_ = self.model.fit_predict(features)
        self.features_normalized_ = features
        return self.labels_
    
    def fit_archetypes_predict(self, features, overalls, threshold=75):
        """Entrena (fit) el modelo solo con jugadores de overall > threshold
        y luego asigna (predict) el cluster para todos los jugadores."""
        fit_mask = overalls > threshold
        
        # Resguardo en caso de que no haya suficientes jugadores que superen el umbral
        if np.sum(fit_mask) < self.n_clusters:
            print(f"  [Warning] Not enough players with overall > {threshold} (found {np.sum(fit_mask)}). Fitting on all players.")
            fit_features = features
        else:
            fit_features = features[fit_mask]
            
        self.model.fit(fit_features)
        self.labels_ = self.model.predict(features)
        self.features_normalized_ = features
        return self.labels_
    
    def get_intra_cluster_variance(self, features):
        """Calcula la varianza intra-cluster (promedio de la distancia euclidiana al cuadrado al centroide de todos los jugadores asignados)."""
        assigned_centers = self.model.cluster_centers_[self.labels_]
        squared_distances = np.sum((features - assigned_centers) ** 2, axis=1)
        return float(np.mean(squared_distances))
    
    def find_representatives(self, player_names, overalls):
        """Selecciona al jugador con mayor overall dentro de cada cluster."""
        n_clusters = len(np.unique(self.labels_))
        representatives = {}

        for cluster_id in range(n_clusters):
            cluster_indices = np.where(self.labels_ == cluster_id)[0]
            cluster_names = player_names[cluster_indices]
            cluster_overalls = overalls[cluster_indices]

            if len(cluster_overalls) == 0:
                continue

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
        'Centerbacks': 'player_clustering_centerbacks.json',
        'Fullbacks': 'player_clustering_fullbacks.json',
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

def find_optimal_k(features, overalls, min_k=3, max_k=10, threshold=75, min_players=5):
    """Encuentra el K óptimo evaluando el Silhouette Score de KMeans sobre el subgrupo de arquetipos (>threshold).
    Descarta aquellos K que generen clústeres finales en el total de jugadores con menos de min_players."""
    fit_mask = overalls > threshold
    fit_features = features[fit_mask]
    
    # Resguardo si hay muy pocos jugadores de calidad superior
    if len(fit_features) <= min_k:
        fit_features = features
        
    best_k = None
    best_score = -2.0
    
    for k in range(min_k, min(max_k + 1, len(fit_features))):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
        kmeans.fit(fit_features)
        
        # Validar tamaño mínimo sobre la asignación total de jugadores
        all_labels = kmeans.predict(features)
        counts = np.bincount(all_labels, minlength=k)
        
        if np.min(counts) < min_players:
            continue
        
        # Calcular Silhouette score sobre el subgrupo
        score = silhouette_score(fit_features, kmeans.labels_, metric='euclidean')
        if score > best_score:
            best_score = score
            best_k = k
            
    # Fallback: si todos los K violan el mínimo, elegir el K con mejor Silhouette global
    if best_k is None:
        best_score = -2.0
        for k in range(min_k, min(max_k + 1, len(fit_features))):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
            kmeans.fit(fit_features)
            score = silhouette_score(fit_features, kmeans.labels_, metric='euclidean')
            if score > best_score:
                best_score = score
                best_k = k
            
    return best_k, best_score

def save_cluster_map(player_names, overalls, labels, representatives, features, position, output_dir):
    """
    Persiste el mapa cluster → jugadores (variante arquetipos) en un archivo JSON.

    Estructura de salida:
    [
      {
        "long_name": "Jude Bellingham",
        "cluster_id": 3,
        "overall": 90,
        "representative_name": "Jude Bellingham",
        "position_vector": [0.12, -0.03, ...]
      },
      ...
    ]
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = f"kmeans_{position.lower()}_arquetipos.json"
    filepath = os.path.join(output_dir, filename)

    records = []
    for idx, (player_name, overall, cluster_id) in enumerate(zip(player_names, overalls, labels)):
        # cluster_id from model is 0-based; representatives uses 1-based keys
        rep_key = int(cluster_id) + 1
        rep_name = representatives.get(rep_key, {}).get('name', '')
        records.append({
            'long_name': str(player_name),
            'cluster_id': int(cluster_id) + 1,   # 1-based for readability
            'overall': int(overall),
            'representative_name': rep_name,
            'position_vector': [round(float(v), 6) for v in features[idx]],
        })

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=4)

    print(f"  --> Mapa arquetipos guardado: {filepath} ({len(records)} jugadores)")


def main():
    positions = ['Goalkeepers', 'Centerbacks', 'Fullbacks', 'Midfielders', 'Strikers', 'Wingers']
    
    for position in positions:
        try:
            # 1. Obtener ruta mediante Factory
            filepath = PositionFactory.get_filepath(position)
            
            # 2. Ingesta de datos
            df = DataLoader.load_data(filepath)
            
            # 3. Preprocesamiento
            features, player_names, overalls = DataPreprocessor.preprocess(df)

            # 4. Encontrar K óptimo dinámicamente usando validación interna de Silhouette
            n_clusters, best_sil_score = find_optimal_k(features, overalls, min_k=3, max_k=10, threshold=75)
            if position == 'Midfielders':
                n_clusters = 4
            elif position == 'Wingers':
                n_clusters = 3
            print(f"=======================================================")
            print(f"POSICIÓN: {position} | K ÓPTIMO DEDUCIDO: {n_clusters} (Silhouette: {best_sil_score:.4f})")
            print(f"=======================================================")

            # -------------------------------------------------------
            # 5a. HAC (Hierarchical Agglomerative Clustering) 
            # -------------------------------------------------------
            hac_engine = ClusteringEngine(n_clusters=n_clusters, metric='cosine', linkage='average')
            hac_labels = hac_engine.fit_predict(features)
            hac_reps = hac_engine.find_representatives(hac_labels, player_names, overalls)

            print(f"HAC {position}:")
            for cluster_id in sorted(hac_reps.keys()):
                rep = hac_reps[cluster_id]
                print(f"  Cluster {cluster_id} = {rep['name']} (overall: {rep['overall']})")

            # -------------------------------------------------------
            # 5b. KMeans (Normal)
            # -------------------------------------------------------
            kmeans_engine = KMeansEngine(n_clusters=n_clusters)
            kmeans_engine.fit_predict(features)
            kmeans_reps = kmeans_engine.find_representatives(player_names, overalls)
            var_normal = kmeans_engine.get_intra_cluster_variance(features)

            print(f"KMeans {position} (Normal):")
            for cluster_id in sorted(kmeans_reps.keys()):
                rep = kmeans_reps[cluster_id]
                print(f"  Cluster {cluster_id} = {rep['name']} (overall: {rep['overall']})")
            print(f"  --> Varianza intra-cluster (Normal): {var_normal:.5f}")
            
            # -------------------------------------------------------
            # 5c. KMeans (Arquetipos >75)
            # -------------------------------------------------------
            kmeans_arch_engine = KMeansEngine(n_clusters=n_clusters)
            kmeans_arch_engine.fit_archetypes_predict(features, overalls, threshold=75)
            kmeans_arch_reps = kmeans_arch_engine.find_representatives(player_names, overalls)
            var_arch = kmeans_arch_engine.get_intra_cluster_variance(features)

            print(f"KMeans {position} (Arquetipos >75):")
            for cluster_id in sorted(kmeans_arch_reps.keys()):
                rep = kmeans_arch_reps[cluster_id]
                print(f"  Cluster {cluster_id} = {rep['name']} (overall: {rep['overall']})")
            print(f"  --> Varianza intra-cluster (Arquetipos >75): {var_arch:.5f}")
            
            # Incremento relativo
            increase = ((var_arch - var_normal) / var_normal) * 100
            print(f"  --> Diferencia en varianza: {increase:+.2f}%")

            # -------------------------------------------------------
            # 6. Guardar mapa KMeans Arquetipos en disco
            # -------------------------------------------------------
            output_dir = os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..', '..', 'data', 'clustering_maps'
            ))

            save_cluster_map(
                player_names, overalls,
                kmeans_arch_engine.labels_, kmeans_arch_reps,
                features, position, output_dir
            )

            print() # Espacio entre posiciones
            
        except Exception as e:
            print(f"Error processing {position}: {str(e)}\n")

if __name__ == "__main__":
    main()
