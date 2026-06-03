import sys
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

sys.path.append('scripts/recommender')
from HAC_clustering import PositionFactory, DataLoader

positions = ['Goalkeepers', 'Centerbacks', 'Fullbacks', 'Midfielders', 'Strikers', 'Wingers']

print("=== AUDITORÍA DE CARGAS (LOADINGS) DE PC1 ===")
for pos in positions:
    filepath = PositionFactory.get_filepath(pos)
    df = DataLoader.load_data(filepath)
    
    exclude_cols = ['overall', 'Cluster_ID', 'id']
    numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns.tolist() if col not in exclude_cols]
    for col in ['height_cm', 'weight_kg']:
        if col in df.columns and col not in numeric_cols:
            numeric_cols.append(col)
            
    X_raw = df[numeric_cols].fillna(df[numeric_cols].median()).fillna(0).values
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)
    
    pca = PCA()
    pca.fit(X_scaled)
    
    # Loadings are in pca.components_[0] (PC1 is index 0)
    pc1_loadings = pca.components_[0]
    
    # Map to feature names
    feature_loadings = pd.Series(pc1_loadings, index=numeric_cols)
    
    print(f"\n[{pos}] - Top 5 variables con mayor carga positiva en PC1:")
    for feat, loading in feature_loadings.sort_values(ascending=False).head(5).items():
        print(f"  * {feat}: {loading:.4f}")
        
    print(f"[{pos}] - Top 5 variables con mayor carga negativa en PC1:")
    for feat, loading in feature_loadings.sort_values(ascending=True).head(5).items():
        print(f"  * {feat}: {loading:.4f}")
