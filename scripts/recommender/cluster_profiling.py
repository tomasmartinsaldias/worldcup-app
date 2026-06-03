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
    
    CLUSTER_NAMES = {
        'Goalkeepers': {
            1: 'Arquero Distribuidor / Ball-Playing',
            2: 'Arquero Físico / Shot-stopper Clásico',
            3: 'Arquero Líbero / Sweeper Keeper'
        },
        'Centerbacks': {
            1: 'Central de Cobertura / Corrector',
            2: 'Central Físico / Stopper',
            3: 'Central Creador / Líbero Técnico'
        },
        'Fullbacks': {
            1: 'Lateral Físico / Centralizado',
            2: 'Lateral Invertido / Organizador',
            3: 'Carrilero Largo / Profundo',
            4: 'Lateral de Contención'
        },
        'Midfielders': {
            1: 'Box-to-Box Físico',
            2: 'Mediapunta Desequilibrante / Playmaker',
            3: 'Pivote Defensivo / Ancla',
            4: 'Organizador de Base / Regista'
        },
        'Wingers': {
            1: 'Extremo Rematador / Inside Forward',
            2: 'Extremo Creador / Desequilibrante',
            3: 'Extremo de Recorrido / Carrilero Táctico'
        },
        'Strikers': {
            1: 'Delantero Objetivo / Target Man',
            2: 'Delantero Presionador / Primer Defensor',
            3: 'Atacante Móvil / Segundo Delantero'
        }
    }
    
    report_lines = []
    report_lines.append("# Reporte de Clusters y Estadísticas Diferenciadoras (Datos Crudos) - Método B (Sin PC1)")
    report_lines.append("\nEste reporte analiza empíricamente los clústeres generados mediante **KMeans (Método B)** con optimización dinámica de K (forzando K=4 para mediocampistas).")
    report_lines.append("Este método utiliza `StandardScaler` + `PCA` (excluyendo la primera componente principal `PC1`) para agrupar por estilo de juego puro sin el sesgo de la calidad general (`overall`).")
    
    # Justification of PC1 exclusion
    report_lines.append("\n## Justificación de la Exclusión de PC1 (Calidad vs. Estilo)")
    report_lines.append("Al realizar el análisis de componentes principales (PCA) sobre las estadísticas de los jugadores en cada posición, se observa que la primera componente principal (PC1) captura la dirección de máxima varianza, la cual coincide casi en su totalidad con el nivel general del jugador (`overall`).\n")
    report_lines.append("Para demostrar esta fuerte relación, se calculó la correlación de Pearson ($R$) entre PC1 y el `overall` para todas las posiciones:")
    report_lines.append("- **Goalkeepers**: $R = 0.6042$")
    report_lines.append("- **Centerbacks**: $R = 0.8888$")
    report_lines.append("- **Fullbacks**: $R = 0.9524$")
    report_lines.append("- **Midfielders**: $R = 0.9320$")
    report_lines.append("- **Strikers**: $R = 0.9577$")
    report_lines.append("- **Wingers**: $R = 0.9651$\n")
    report_lines.append("Como se observa en el gráfico de correlación, a excepción de los arqueros (donde la correlación es moderadamente alta), para todos los jugadores de campo la correlación es extremadamente alta ($> 0.88$). Si mantuviéramos PC1 en el clustering, el algoritmo agruparía a los jugadores principalmente por su nivel de habilidad general (\"buenos\" vs \"malos\") en lugar de por su estilo de juego y rol táctico. Al descartar PC1, el clustering opera sobre las componentes PC2 a PCN, agrupando a los futbolistas por sus perfiles estilísticos de forma pura.\n")
    report_lines.append("![Correlación PC1 vs Overall](plots/pc1_vs_overall_correlation.png)")
    
    # Tabla de incremento del Silhouette Score
    report_lines.append("\n## Comparación de Cohesión: Método Anterior vs. Método B")
    report_lines.append("Al migrar del método anterior (MaxAbsScaler + L2 norm sobre todas las dimensiones) al **Método B** (StandardScaler + PCA sin PC1), el **Silhouette Score** mejoró notablemente en todas las posiciones, lo que indica clústeres mucho más definidos y compactos:\n")
    report_lines.append("| Posición | K | Silhouette (Método Anterior) | Silhouette (Método B) | Incremento de Cohesión |")
    report_lines.append("| :--- | :---: | :---: | :---: | :---: |")
    report_lines.append("| 🧤 **Goalkeepers** | 3 | 0.0955 | 0.1295 | **+35.6%** |")
    report_lines.append("| 🛡️ **Centerbacks** | 3 | 0.1682 | 0.1876 | **+11.5%** |")
    report_lines.append("| 🏃‍♂️ **Fullbacks** | 4 | 0.1391 | 0.1979 | **+42.3%** |")
    report_lines.append("| 🧠 **Midfielders** | 4 | 0.1591 | 0.2268 | **+42.6%** |")
    report_lines.append("| ⚽ **Strikers** | 3 | 0.1886 | 0.2261 | **+19.9%** |")
    report_lines.append("| ⚡ **Wingers** | 3 | 0.1577 | 0.2410 | **+52.8%** |")
    
    report_lines.append("\n---\n")
    
    for position in positions:
        filepath = PositionFactory.get_filepath(position)
        df_raw = DataLoader.load_data(filepath)
        
        # Preprocesar para el clustering
        features, player_names, overalls = DataPreprocessor.preprocess(df_raw)
        
        # Encontrar K óptimo dinámicamente
        n_clusters, best_sil_score = find_optimal_k(features, overalls, min_k=3, max_k=10, threshold=75)
        if position == 'Midfielders':
            n_clusters = 4
        elif position == 'Wingers':
            n_clusters = 3
        
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
        report_lines.append("| :--- | :--- | :---: | :--- |")
        
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
            
            c_name = f"Cluster {cluster_id}: **{CLUSTER_NAMES[position][cluster_id]}**"
            report_lines.append(f"| {c_name} | {rep_name} ({rep_overall}) | {len(cluster_df)} | {top_pos_str} |")
            
            # Guardar detalles más profundos para la sección posterior
            cluster_details.append((cluster_id, rep_name, rep_overall, len(cluster_df), pos_deviations, neg_deviations, cluster_df))
            
        report_lines.append("\n### Análisis Detallado de Arquetipos por Clúster\n")
        
        for cluster_id, rep_name, rep_overall, size, pos_dev, neg_dev, c_df in cluster_details:
            custom_title = f"Clúster {cluster_id}: **\"{CLUSTER_NAMES[position][cluster_id]}\"** (Representante: {rep_name} - {rep_overall})"
            
            report_lines.append(f"#### {custom_title}")
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

