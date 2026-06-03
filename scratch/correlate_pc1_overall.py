import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

sys.path.append('scripts/recommender')
from HAC_clustering import PositionFactory, DataLoader

positions = ['Goalkeepers', 'Centerbacks', 'Fullbacks', 'Midfielders', 'Strikers', 'Wingers']

fig, axs = plt.subplots(2, 3, figsize=(18, 11))
axs = axs.ravel()

print("=== CORRELACIÓN DE PC1 CON EL OVERALL ===")

for idx, pos in enumerate(positions):
    filepath = PositionFactory.get_filepath(pos)
    df = DataLoader.load_data(filepath)
    
    exclude_cols = ['overall', 'Cluster_ID', 'id']
    numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns.tolist() if col not in exclude_cols]
    for col in ['height_cm', 'weight_kg']:
        if col in df.columns and col not in numeric_cols:
            numeric_cols.append(col)
            
    X_raw = df[numeric_cols].fillna(df[numeric_cols].median()).fillna(0).values
    overalls = df['overall'].values
    
    # Scale and PCA
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)
    
    pca = PCA(n_components=1)
    pc1 = pca.fit_transform(X_scaled).ravel()
    
    # Calculate correlation
    corr = np.corrcoef(pc1, overalls)[0, 1]
    print(f"  * {pos}: R = {corr:.4f}")
    
    # Plot scatter
    axs[idx].scatter(pc1, overalls, alpha=0.6, color='dodgerblue', edgecolor='k', s=40)
    
    # Add trend line
    m, b = np.polyfit(pc1, overalls, 1)
    axs[idx].plot(pc1, m*pc1 + b, color='red', linestyle='--', linewidth=2, label=f'R = {corr:.4f}')
    
    axs[idx].set_title(f"{pos} (R = {corr:.4f})")
    axs[idx].set_xlabel("Componente Principal 1 (PC1)")
    axs[idx].set_ylabel("Overall Rating")
    axs[idx].grid(True, linestyle=':', alpha=0.6)
    axs[idx].legend()

plt.suptitle("Correlación entre la Componente Principal 1 (PC1) y la Calidad General (Overall)", fontsize=16, fontweight='bold')
plt.tight_layout()

# Save plot
output_dir = "documentacion/plots"
os.makedirs(output_dir, exist_ok=True)
plot_path = os.path.join(output_dir, "pc1_vs_overall_correlation.png")
plt.savefig(plot_path, dpi=150)
plt.close()

print(f"\nGráfico guardado en: {plot_path}")
