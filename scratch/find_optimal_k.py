import os
import sys
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score

# Add scripts/recommender to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'recommender')))
from HAC_clustering import DataLoader, DataPreprocessor, PositionFactory

def find_optimal_k():
    positions = ['Goalkeepers', 'Defenders', 'Midfielders', 'Strikers', 'Wingers']
    
    print("=== OPTIMIZACIÓN DINÁMICA DE K PARA CADA POSICIÓN ===")
    print("Evaluando K de 3 a 10 (usando jugadores con overall > 75 para definir arquetipos)\n")
    
    for position in positions:
        filepath = PositionFactory.get_filepath(position)
        df = DataLoader.load_data(filepath)
        features, _, overalls = DataPreprocessor.preprocess(df)
        
        # Filtro de arquetipos (>75 overall)
        fit_mask = overalls > 75
        fit_features = features[fit_mask]
        
        print(f"--- {position} (Jugadores >75: {len(fit_features)} de {len(features)}) ---")
        
        best_k_sil = None
        best_sil = -1
        best_k_db = None
        best_db = float('inf')
        
        for k in range(3, 11):
            if len(fit_features) <= k:
                break
                
            kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
            labels = kmeans.fit_predict(fit_features)
            
            sil = silhouette_score(fit_features, labels, metric='euclidean')
            db = davies_bouldin_score(fit_features, labels)
            
            print(f"  k={k:2d} | Silhouette: {sil:.4f} | Davies-Bouldin: {db:.4f}")
            
            if sil > best_sil:
                best_sil = sil
                best_k_sil = k
                
            if db < best_db:
                best_db = db
                best_k_db = k
                
        print(f"  >> Óptimo Silhouette: K = {best_k_sil} (Score: {best_sil:.4f})")
        print(f"  >> Óptimo Davies-Bouldin: K = {best_k_db} (Score: {best_db:.4f})\n")

if __name__ == "__main__":
    find_optimal_k()
