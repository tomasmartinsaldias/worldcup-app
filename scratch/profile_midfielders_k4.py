import sys
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

sys.path.append('scripts/recommender')
from HAC_clustering import PositionFactory, DataLoader

filepath = PositionFactory.get_filepath('Midfielders')
df = DataLoader.load_data(filepath)

exclude_cols = ['overall', 'Cluster_ID', 'id']
numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns.tolist() if col not in exclude_cols]
for col in ['height_cm', 'weight_kg']:
    if col in df.columns and col not in numeric_cols:
        numeric_cols.append(col)
        
X_raw = df[numeric_cols].fillna(df[numeric_cols].median()).fillna(0).values
overalls = df['overall'].values
names = df['long_name'].values

# Escalar y aplicar PCA
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_raw)
pca = PCA()
X_pca_all = pca.fit_transform(X_scaled)

# Omitir PC1
X_pca_B = X_pca_all[:, 1:5]

# Ejecutar KMeans con K=4
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
labels = kmeans.fit_predict(X_pca_B)
df['Cluster_B'] = labels + 1

profile_cols = [col for col in numeric_cols if col not in ['overall', 'Cluster_B', 'age', 'height_cm', 'weight_kg']]
global_medians = df[profile_cols].median()

print("=== PERFILADO DE MEDIOCAMPISTAS CON K=4 (SIN PC1) ===")
for cid in range(1, 5):
    c_df = df[df['Cluster_B'] == cid]
    rep = c_df.sort_values(by='overall', ascending=False).iloc[0]
    
    c_medians = c_df[profile_cols].median()
    deviations = c_medians - global_medians
    
    pos_dev = deviations[deviations > 0].sort_values(ascending=False).head(3)
    neg_dev = deviations[deviations < 0].sort_values(ascending=True).head(3)
    
    sample = c_df.sort_values(by='overall', ascending=False).head(5)['long_name'].tolist()
    
    print(f"\nCluster {cid} (Tamaño: {len(c_df)}): Rep = {rep['long_name']} (overall: {rep['overall']})")
    print(f"  * Ejemplos: {', '.join(sample)}")
    print("  * Destacados:")
    for f, v in pos_dev.items():
        print(f"    - {f}: +{v:.1f}")
    print("  * Carencias:")
    for f, v in neg_dev.items():
        print(f"    - {f}: {v:.1f}")
