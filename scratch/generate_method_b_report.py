import sys
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

sys.path.append('scripts/recommender')
from HAC_clustering import PositionFactory, DataLoader

positions = ['Goalkeepers', 'Centerbacks', 'Fullbacks', 'Midfielders', 'Strikers', 'Wingers']
report_lines = []

report_lines.append("# Reporte de Clusters y Estadísticas Diferenciadoras - Método B (Sin PC1)")
report_lines.append("\nEste reporte detalla los perfiles de estilo de juego puros obtenidos al **ignorar la primera componente principal (PC1)** en el PCA.")
report_lines.append("Esto elimina el sesgo de la calidad general (`overall`), agrupando a los jugadores exclusivamente por la geometría de sus atributos.")
report_lines.append("\n---\n")

for pos in positions:
    filepath = PositionFactory.get_filepath(pos)
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
    
    # Determinar cuántas componentes explican >= 80% en total (Método A)
    cum_var = np.cumsum(pca.explained_variance_ratio_)
    n_components = np.argmax(cum_var >= 0.80) + 1
    
    # Para Método B, tomamos desde PC2 hasta la componente que completa el 80% (omitiendo la columna 0, PC1)
    X_pca_B = X_pca_all[:, 1:n_components]
    
    # Determinar K óptimo para Método B (Silhouette optimizado con min_cluster_size > 10)
    best_k = 3
    best_score = -2.0
    
    for k in range(3, 8):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_pca_B)
        counts = np.bincount(labels, minlength=k)
        if np.min(counts) < 10:
            continue
        score = silhouette_score(X_pca_B, labels)
        if score > best_score:
            best_score = score
            best_k = k
            
    if pos == 'Midfielders':
        best_k = 4
        
    # Ajustamos KMeans óptimo
    kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_pca_B)
    df['Cluster_B'] = labels + 1
    
    # Mediana global de la posición (excluyendo datos demográficos para el perfilado técnico)
    exclude_from_profile = ['overall', 'Cluster_B', 'age', 'height_cm', 'weight_kg']
    profile_cols = [col for col in numeric_cols if col not in exclude_from_profile]
    global_medians = df[profile_cols].median()
    
    report_lines.append(f"## {pos} (K = {best_k} clusters, conservando {X_pca_B.shape[1]} PCs)")
    report_lines.append(f"Total jugadores: {len(df)}")
    report_lines.append("\n| Clúster | Representante principal | Miembros | Atributos Destacados |")
    report_lines.append("| :--- | :--- | :---: | :--- |")
    
    cluster_details = []
    
    for cid in range(1, best_k + 1):
        c_df = df[df['Cluster_B'] == cid]
        if len(c_df) == 0:
            continue
            
        best_player = c_df.sort_values(by='overall', ascending=False).iloc[0]
        rep_name = best_player['long_name']
        rep_overall = best_player['overall']
        
        c_medians = c_df[profile_cols].median()
        deviations = c_medians - global_medians
        
        pos_deviations = deviations[deviations > 0].sort_values(ascending=False).head(5)
        neg_deviations = deviations[deviations < 0].sort_values(ascending=True).head(5)
        
        top_pos_str = ", ".join([f"**+{int(val)}** en {feat.replace('_', ' ')}" for feat, val in pos_deviations.items()])
        report_lines.append(f"| Cluster {cid} | {rep_name} ({rep_overall}) | {len(c_df)} | {top_pos_str} |")
        
        cluster_details.append((cid, rep_name, rep_overall, len(c_df), pos_deviations, neg_deviations, c_df))
        
    report_lines.append("\n### Detalle por Clúster\n")
    for cid, rep_name, rep_overall, size, pos_dev, neg_dev, c_df in cluster_details:
        report_lines.append(f"#### Clúster {cid}: Representado por {rep_name} ({rep_overall})")
        report_lines.append(f"- **Tamaño del grupo:** {size} jugadores.")
        sample_players = c_df.sort_values(by='overall', ascending=False).head(8)['long_name'].tolist()
        report_lines.append(f"- **Jugadores de ejemplo:** {', '.join(sample_players)}")
        
        report_lines.append("\n##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):")
        for feat, val in pos_dev.items():
            clean_feat = feat.replace('_', ' ').title()
            report_lines.append(f"  * **{clean_feat}**: +{val:+.1f} (Mediana: {c_df[feat].median():.1f} vs Global: {global_medians[feat]:.1f})")
            
        report_lines.append("\n##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):")
        for feat, val in neg_dev.items():
            clean_feat = feat.replace('_', ' ').title()
            report_lines.append(f"  * **{clean_feat}**: {val:+.1f} (Mediana: {c_df[feat].median():.1f} vs Global: {global_medians[feat]:.1f})")
            
        report_lines.append("\n" + "_"*40 + "\n")
    report_lines.append("\n---\n")

output_path = "documentacion/clustering_alternative/reporte_datos_crudos_metodo_b.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))
    
print(f"Reporte de datos crudos generado exitosamente en: {output_path}")
