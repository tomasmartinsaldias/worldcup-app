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

CLUSTER_METADATA = {
    'Goalkeepers': {
        1: {
            'name': 'Arquero Jugador / Sweeper Keeper',
            'desc': 'Dominan absolutamente el juego con los pies, registrando +17 en pase largo y +16 en pase corto frente a la mediana. También superan al resto en compostura (+13). Son la primera línea de creación.'
        },
        2: {
            'name': 'Arquero Anómalo / Lóbero',
            'desc': 'Es un micro-clúster de solo 2 jugadores. Tienen altísima agilidad (+18), pero su penalización extrema en compostura (-17.5) sugiere que el algoritmo aisló ruido estadístico o perfiles muy erráticos.'
        },
        3: {
            'name': 'Arquero Tradicional / Atajador',
            'desc': 'El bloque principal (55 jugadores). Tienen deficiencias marcadas en visión (-5.5) y pase corto (-5.0), enfocándose estrictamente en defender bajo los tres palos sin arriesgar en la salida.'
        }
    },
    'Centerbacks': {
        1: {
            'name': 'Central Dominador / Amenaza Aérea',
            'desc': 'No solo defienden; son armas ofensivas en el juego aéreo y pelota parada. Destacan con +13 en finalización, +12 en tiros lejanos y +11.5 en potencia de tiro.'
        },
        2: {
            'name': 'Central de Cobertura / Rápido',
            'desc': 'Su geometría prioriza corregir errores mediante velocidad. Tienen +4 en ritmo y +3 en aceleración, pero carecen del impacto ofensivo del Clúster 1, con -9 en tiros lejanos.'
        },
        3: {
            'name': 'Central Tanque / Físico',
            'desc': 'El arquetipo clásico de choque. Su fuerza supera a la mediana (+3) y tienen alta potencia (+5), pero el modelo detectó su falta de movilidad, penalizándolos severamente en agilidad (-16) y aceleración (-11.5).'
        }
    },
    'Fullbacks': {
        1: {
            'name': 'Lateral Físico / Tercer Central',
            'desc': 'Destacan por su capacidad para el choque y el juego aéreo, con +9 en cabezazo, +5 en fuerza y +4 en salto.'
        },
        2: {
            'name': 'Lateral de Recorrido / Equilibrado',
            'desc': 'Son ágiles y rápidos (+1 en aceleración y velocidad), pero tienen desviaciones muy negativas en impacto en el área rival (-13.5 en finalización, -11.5 en tiros). Su misión principal es la banda, no el arco.'
        },
        3: {
            'name': 'Lateral Ofensivo / Carrilero',
            'desc': 'El arquetipo de ataque profundo. Tienen métricas de delanteros: +8 en precisión de tiros libres, +7 en tiros lejanos y +4.5 en finalización.'
        }
    },
    'Midfielders': {
        1: {
            'name': 'Todocampista / Box-to-Box',
            'desc': 'Son el motor físico del equipo. Tienen superioridad en salto (+4.0) y métricas defensivas consistentes (+3.5 en entradas y defensa general, +3.0 en intercepciones).'
        },
        2: {
            'name': 'Enganche Ágil / Mediapunta',
            'desc': 'Pura creatividad y desequilibrio. Sobresalen en ritmo (+7.0), agilidad (+6.0) y balance (+6.0). A cambio, el algoritmo marca su nulo retroceso, con -23.0 en barridas y -18.5 en defensa general.'
        },
        3: {
            'name': 'Organizador / Pivote Técnico',
            'desc': 'Los dueños de la pelota parada y los pases largos. Resaltan en voleas (+8.0), penales (+8.0) y precisión de libres (+7.0). Son más lentos que el resto (-4.0 en ritmo), compensándolo con posicionamiento.'
        }
    },
    'Strikers': {
        1: {
            'name': 'Delantero de Presión / Primera Línea Defensiva',
            'desc': 'Este es un hallazgo excelente del modelo. Identificó a los atacantes que ahogan la salida rival, registrando +12.5 en intercepciones y +11.0 en barridas frente a la mediana de los delanteros.'
        },
        2: {
            'name': 'Delantero de Ruptura / Velocista',
            'desc': 'Su principal arma es ganar la espalda de la defensa, superando la mediana en aceleración (+3.0) y velocidad (+2.5), con bajo compromiso de marca (-9.0 en entradas).'
        },
        3: {
            'name': 'Hombre Objetivo / Nueve de Área',
            'desc': 'Una bestia física. Arrasan en fuerza (+7.0) y cabezazo (+5.0). La contrapartida matemática es su rigidez: -16.5 en agilidad y -14.5 en balance.'
        }
    },
    'Wingers': {
        1: {
            'name': 'Extremo Completo / Asociativo',
            'desc': 'Jugadores de banda con gran capacidad de creación y definición. Superan la media en tiros libres (+2.0), visión (+2.0) y finalización (+1.5).'
        },
        2: {
            'name': 'Extremo Desequilibrante / Regateador Puro',
            'desc': 'Aislados estrictamente por su habilidad técnica en el uno contra uno, con +2.0 en regate, +1.5 en regate hábil y +2.0 en finalización. Tienen obligaciones defensivas nulas (-13.5 en intercepciones).'
        },
        3: {
            'name': 'Volante Táctico / Extremo Defensivo',
            'desc': 'Ya sea por sacrificio táctico (Saka) o por error de etiqueta del juego (Grimaldo), este grupo se define por sus números irreales de defensa en ataque: +24.0 en barridas y +22.0 en intercepciones.'
        }
    }
}

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
            
            # Obtener nombre personalizado del clúster si está definido
            c_name = f"Cluster {cluster_id}"
            pos_key = 'Centerbacks' if position == 'Centerbacks' else ('Fullbacks' if position == 'Fullbacks' else position)
            if pos_key in CLUSTER_METADATA and cluster_id in CLUSTER_METADATA[pos_key]:
                c_name = f"Cluster {cluster_id}: **{CLUSTER_METADATA[pos_key][cluster_id]['name']}**"
                
            report_lines.append(f"| {c_name} | {rep_name} ({rep_overall}) | {len(cluster_df)} | {top_pos_str} |")
            
            # Guardar detalles más profundos para la sección posterior
            cluster_details.append((cluster_id, rep_name, rep_overall, len(cluster_df), pos_deviations, neg_deviations, cluster_df))
            
        report_lines.append("\n### Análisis Detallado de Arquetipos por Clúster\n")
        
        for cluster_id, rep_name, rep_overall, size, pos_dev, neg_dev, c_df in cluster_details:
            pos_key = 'Centerbacks' if position == 'Centerbacks' else ('Fullbacks' if position == 'Fullbacks' else position)
            custom_title = f"Clúster {cluster_id}: Representado por {rep_name} ({rep_overall})"
            custom_desc = ""
            if pos_key in CLUSTER_METADATA and cluster_id in CLUSTER_METADATA[pos_key]:
                custom_title = f"Clúster {cluster_id}: **\"{CLUSTER_METADATA[pos_key][cluster_id]['name']}\"** (Representante: {rep_name} - {rep_overall})"
                custom_desc = f"\n*{CLUSTER_METADATA[pos_key][cluster_id]['desc']}*\n"
                
            report_lines.append(f"#### {custom_title}")
            if custom_desc:
                report_lines.append(custom_desc)
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

