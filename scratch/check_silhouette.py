import sys
import os
sys.path.append('scripts/recommender')
from HAC_clustering import DataLoader, DataPreprocessor, PositionFactory
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np

for pos in ['Goalkeepers', 'Centerbacks', 'Fullbacks', 'Midfielders', 'Strikers', 'Wingers']:
    filepath = PositionFactory.get_filepath(pos)
    df = DataLoader.load_data(filepath)
    features, player_names, overalls = DataPreprocessor.preprocess(df)
    
    # Use archetypes (> 75)
    fit_mask = overalls > 75
    fit_features = features[fit_mask]
    
    print(f"=== {pos} ===")
    for k in range(3, 8):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(fit_features)
        
        all_labels = kmeans.predict(features)
        counts = np.bincount(all_labels, minlength=k)
        min_cluster_size = np.min(counts)
        
        score = silhouette_score(fit_features, kmeans.labels_, metric='euclidean')
        print(f"  K={k}: Silhouette={score:.4f}, Min Cluster Size={min_cluster_size}")
