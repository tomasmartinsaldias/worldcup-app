import sys
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

sys.path.append('scripts/recommender')
from HAC_clustering import PositionFactory, DataLoader

# Cargar mediocampistas
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

# Conservamos 5 componentes en total del PCA (Método A), por lo que para el Método B
# conservamos las componentes PC2, PC3, PC4 y PC5 (4 dimensiones en total, omitiendo PC1)
X_pca_B = X_pca_all[:, 1:5] 

print(f"Dimensiones conservadas en Método B para Midfielders: {X_pca_B.shape[1]} (desde PC2 hasta PC5)")

# Ejecutar KMeans con K=3 (el óptimo para Método B)
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
labels = kmeans.fit_predict(X_pca_B)

df['Cluster_B'] = labels + 1

# Mediana global de la posición
exclude_from_profile = ['overall', 'Cluster_B', 'age', 'height_cm', 'weight_kg']
profile_cols = [col for col in numeric_cols if col not in exclude_from_profile]
global_medians = df[profile_cols].median()

print("\n=== PERFILES DE LOS CLUSTERS DE MEDIOCAMPISTAS (MÉTODO B - SIN PC1) ===")
for cid in range(1, 4):
    c_df = df[df['Cluster_B'] == cid]
    size = len(c_df)
    
    # Representante
    rep = c_df.sort_values(by='overall', ascending=False).iloc[0]
    
    # Mediana del clúster y desviación
    c_medians = c_df[profile_cols].median()
    deviations = c_medians - global_medians
    
    pos_deviations = deviations[deviations > 0].sort_values(ascending=False).head(5)
    neg_deviations = deviations[deviations < 0].sort_values(ascending=True).head(5)
    
    print(f"\n--- CLUSTER {cid} ---")
    print(f"  * Tamaño: {size} jugadores")
    print(f"  * Representante principal: {rep['long_name']} (overall: {rep['overall']})")
    
    # Muestra de jugadores famosos en el cluster
    sample = c_df.sort_values(by='overall', ascending=False).head(8)['long_name'].tolist()
    print(f"  * Jugadores de ejemplo: {', '.join(sample)}")
    
    print("  * Atributos destacados (Desviación positiva vs Mediana global):")
    for feat, val in pos_deviations.items():
        print(f"    - {feat}: +{val:.1f} (Mediana: {c_df[feat].median():.1f} vs Global: {global_medians[feat]:.1f})")
        
    print("  * Carencias destacadas (Desviación negativa vs Mediana global):")
    for feat, val in neg_deviations.items():
        print(f"    - {feat}: {val:.1f} (Mediana: {c_df[feat].median():.1f} vs Global: {global_medians[feat]:.1f})")
