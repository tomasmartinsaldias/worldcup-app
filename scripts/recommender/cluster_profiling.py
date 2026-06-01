import json
import os
import sys
import numpy as np
import pandas as pd

# Add the directory containing HAC_clustering.py to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from HAC_clustering import DataLoader, DataPreprocessor, KMeansEngine, PositionFactory, find_optimal_k

# Set stdout to utf-8
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def profile_clusters():
    positions = ['Goalkeepers', 'Centerbacks', 'Fullbacks', 'Midfielders', 'Strikers', 'Wingers']
    
    report_lines = []
    report_lines.append("# Perfilado de Clusters y Arquetipos de Jugadores")
    report_lines.append("\nEste reporte analiza empíricamente los clústeres generados mediante **KMeans (Arquetipos >75)** con optimización dinámica de K.")
    report_lines.append("Para cada clúster, comparamos la mediana de sus atributos físicos y técnicos contra la mediana global de su posición.")
    report_lines.append("Las desviaciones positivas revelan las fortalezas características del arquetipo, mientras que las negativas señalan sus carencias.")
    report_lines.append("\n---\n")
    
    for position in positions:
        filepath = PositionFactory.get_filepath(position)
        df_raw = DataLoader.load_data(filepath)
        
        # Preprocesar para el clustering
        features, player_names, overalls = DataPreprocessor.preprocess(df_raw)
        
        # Encontrar K óptimo dinámicamente
        n_clusters, best_sil_score = find_optimal_k(features, overalls, min_k=3, max_k=10, threshold=75)
        
        # Entrenar KMeans usando Arquetipos >75 con el K óptimo
        kmeans = KMeansEngine(n_clusters=n_clusters)
        labels = kmeans.fit_archetypes_predict(features, overalls, threshold=75)
        
        # Añadir etiquetas al DataFrame original sin escalar
        df_raw['Cluster_ID'] = labels + 1  # 1-indexed
        
        # Identificar columnas numéricas clave (excluyendo IDs, overall, etc.)
        all_numeric_cols = df_raw.select_dtypes(include=[np.number]).columns.tolist()
        exclude_cols = ['overall', 'Cluster_ID', 'age', 'height_cm', 'weight_kg']
        profile_cols = [col for col in all_numeric_cols if col not in exclude_cols]
        
        # Mediana global por posición
        global_medians = df_raw[profile_cols].median()
        
        report_lines.append(f"## {position} (KMeans Arquetipos >75)")
        report_lines.append(f"Total jugadores analizados: {len(df_raw)}")
        report_lines.append("\n| Clúster | Representante principal | Miembros | Atributos Destacados (Desviación vs Mediana Global) |")
        report_lines.append("| :---: | :--- | :---: | :--- |")
        
        cluster_details = []
        
        for cluster_id in range(1, n_clusters + 1):
            cluster_df = df_raw[df_raw['Cluster_ID'] == cluster_id]
            if len(cluster_df) == 0:
                continue
            
            # Representante (jugador con mayor overall en el clúster)
            best_player = cluster_df.sort_values(by='overall', ascending=False).iloc[0]
            rep_name = best_player['long_name']
            rep_overall = best_player['overall']
            
            # Mediana del clúster
            cluster_medians = cluster_df[profile_cols].median()
            
            # Desviaciones (Cluster Median - Global Median)
            deviations = cluster_medians - global_medians
            
            # Destacados positivos y negativos más significativos
            pos_deviations = deviations[deviations > 0].sort_values(ascending=False).head(5)
            neg_deviations = deviations[deviations < 0].sort_values(ascending=True).head(5)
            
            # Formatear lista de atributos destacados para la tabla resumen
            top_pos_str = ", ".join([f"**+{int(val)}** en {feat.replace('_', ' ')}" for feat, val in pos_deviations.items()])
            
            report_lines.append(f"| Cluster {cluster_id} | {rep_name} ({rep_overall}) | {len(cluster_df)} | {top_pos_str} |")
            
            # Guardar detalles más profundos para la sección posterior
            cluster_details.append((cluster_id, rep_name, rep_overall, len(cluster_df), pos_deviations, neg_deviations, cluster_df))
            
        report_lines.append("\n### Análisis Detallado de Arquetipos por Clúster\n")
        
        for cluster_id, rep_name, rep_overall, size, pos_dev, neg_dev, c_df in cluster_details:
            report_lines.append(f"#### Clúster {cluster_id}: Representado por {rep_name} ({rep_overall})")
            report_lines.append(f"- **Tamaño del grupo:** {size} jugadores.")
            
            # Muestra de jugadores de ejemplo en este clúster
            sample_players = c_df.sort_values(by='overall', ascending=False).head(6)['long_name'].tolist()
            report_lines.append(f"- **Ejemplos en el dataset:** {', '.join(sample_players)}")
            
            report_lines.append("\n##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):")
            for feat, val in pos_dev.items():
                clean_feat = feat.replace('_', ' ').title()
                report_lines.append(f"  * **{clean_feat}**: +{val:+.1f} (Mediana del clúster: {c_df[feat].median():.1f} vs Mediana global: {global_medians[feat]:.1f})")
                
            report_lines.append("\n##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):")
            for feat, val in neg_dev.items():
                clean_feat = feat.replace('_', ' ').title()
                report_lines.append(f"  * **{clean_feat}**: {val:+.1f} (Mediana del clúster: {c_df[feat].median():.1f} vs Mediana global: {global_medians[feat]:.1f})")
            
            report_lines.append("\n" + "_"*40 + "\n")
            
        report_lines.append("\n---\n")
        
    # Guardar reporte en markdown
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'documentacion', 'score_jugadores_perfil_clusters.md'))
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
        
    print(f"Reporte generado exitosamente en: {output_path}")

if __name__ == "__main__":
    profile_clusters()
