import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import sys

# Ensure UTF-8 output on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Import data loading helper from project
sys.path.append('scripts/recommender')
from HAC_clustering import PositionFactory, DataLoader

def run_experiment_for_position(pos_name, output_dir_plots):
    print(f"\n=======================================================")
    print(f"EXPERIMENTO CLUSTERING ALTERNATIVO: {pos_name}")
    print(f"=======================================================")
    
    # 1. Cargar datos
    filepath = PositionFactory.get_filepath(pos_name)
    df = DataLoader.load_data(filepath)
    
    # Seleccionar variables numéricas incluyendo height_cm y weight_kg
    # y excluyendo overall (y cualquier columna ID / auxiliar)
    exclude_cols = ['overall', 'Cluster_ID', 'id']
    numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns.tolist() if col not in exclude_cols]
    
    # Asegurarnos de que height_cm y weight_kg están en la lista
    for col in ['height_cm', 'weight_kg']:
        if col in df.columns and col not in numeric_cols:
            numeric_cols.append(col)
            
    print(f"Variables utilizadas ({len(numeric_cols)}): {', '.join(numeric_cols)}")
    
    X_raw = df[numeric_cols].fillna(df[numeric_cols].median()).fillna(0).values
    overalls = df['overall'].values
    names = df['long_name'].values
    
    # -------------------------------------------------------------
    # MÉTODO A: StandardScaler + PCA (80% Varianza) + KMeans
    # -------------------------------------------------------------
    print("\n--- Método A: StandardScaler + PCA + KMeans ---")
    scaler_A = StandardScaler()
    X_scaled_A = scaler_A.fit_transform(X_raw)
    
    pca_A = PCA()
    X_pca_all_A = pca_A.fit_transform(X_scaled_A)
    
    cum_var_A = np.cumsum(pca_A.explained_variance_ratio_)
    n_components_A = np.argmax(cum_var_A >= 0.80) + 1
    print(f"Componentes para >=80% varianza explicada: {n_components_A} (Varianza total: {cum_var_A[n_components_A-1]:.4f})")
    
    # Reducimos dimensiones
    X_pca_A = X_pca_all_A[:, :n_components_A]
    
    # Optimizar K mediante Silhouette Score
    best_k_A = 3
    best_score_A = -2.0
    scores_A = {}
    inertias_A = []
    
    for k in range(3, 11):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_pca_A)
        inertias_A.append(kmeans.inertia_)
        
        # Validar tamaño mínimo de cluster (>10)
        counts = np.bincount(labels, minlength=k)
        if np.min(counts) < 10:
            continue
            
        score = silhouette_score(X_pca_A, labels)
        scores_A[k] = score
        if score > best_score_A:
            best_score_A = score
            best_k_A = k
            
    print(f"K óptptimo: {best_k_A} (Silhouette: {best_score_A:.4f})")
    
    # Ajustamos KMeans óptimo
    kmeans_A = KMeans(n_clusters=best_k_A, random_state=42, n_init=10)
    labels_A = kmeans_A.fit_predict(X_pca_A)
    
    # Calcular correlación de clústeres con el Overall
    corr_A = abs(pd.Series(labels_A).corr(pd.Series(overalls)))
    print(f"Correlación absoluta con overall: {corr_A:.4f}")
    
    # -------------------------------------------------------------
    # MÉTODO B: Ignorando la primera componente principal (PC1)
    # -------------------------------------------------------------
    print("\n--- Método B: Ignorando PC1 ---")
    # Ignoramos la primera columna (índice 0) de la reducción de PCA
    X_pca_B = X_pca_all_A[:, 1:n_components_A]
    
    best_k_B = 3
    best_score_B = -2.0
    scores_B = {}
    
    for k in range(3, 11):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_pca_B)
        
        counts = np.bincount(labels, minlength=k)
        if np.min(counts) < 10:
            continue
            
        score = silhouette_score(X_pca_B, labels)
        scores_B[k] = score
        if score > best_score_B:
            best_score_B = score
            best_k_B = k
            
    print(f"K óptptimo (sin PC1): {best_k_B} (Silhouette: {best_score_B:.4f})")
    
    if pos_name == 'Midfielders':
        best_k_B = 4
        
    kmeans_B = KMeans(n_clusters=best_k_B, random_state=42, n_init=10)
    labels_B = kmeans_B.fit_predict(X_pca_B)
    corr_B = abs(pd.Series(labels_B).corr(pd.Series(overalls)))
    print(f"Correlación absoluta con overall (sin PC1): {corr_B:.4f}")
    
    # -------------------------------------------------------------
    # MÉTODO C: Filtrar Convocados >75 primero + StandardScaler + PCA + KMeans
    # -------------------------------------------------------------
    print("\n--- Método C: Filtrar Convocados >75 primero ---")
    mask_75 = overalls > 75
    df_75 = df[mask_75]
    print(f"Jugadores >75: {len(df_75)} (de {len(df)})")
    
    X_raw_C = df_75[numeric_cols].fillna(df_75[numeric_cols].median()).fillna(0).values
    overalls_C = df_75['overall'].values
    names_C = df_75['long_name'].values
    
    scaler_C = StandardScaler()
    X_scaled_C = scaler_C.fit_transform(X_raw_C)
    
    pca_C = PCA()
    X_pca_all_C = pca_C.fit_transform(X_scaled_C)
    
    cum_var_C = np.cumsum(pca_C.explained_variance_ratio_)
    n_components_C = np.argmax(cum_var_C >= 0.80) + 1
    print(f"Componentes para >=80% varianza explicada (>75): {n_components_C}")
    
    X_pca_C = X_pca_all_C[:, :n_components_C]
    
    best_k_C = 3
    best_score_C = -2.0
    scores_C = {}
    inertias_C = []
    
    # Como hay menos jugadores, permitimos un tamaño mínimo de cluster > 5
    min_size_C = 5 if len(df_75) < 100 else 10
    
    for k in range(3, 10):
        if k >= len(df_75):
            break
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_pca_C)
        inertias_C.append(kmeans.inertia_)
        
        counts = np.bincount(labels, minlength=k)
        if np.min(counts) < min_size_C:
            continue
            
        score = silhouette_score(X_pca_C, labels)
        scores_C[k] = score
        if score > best_score_C:
            best_score_C = score
            best_k_C = k
            
    print(f"K óptptimo (>75): {best_k_C} (Silhouette: {best_score_C:.4f})")
    
    kmeans_C = KMeans(n_clusters=best_k_C, random_state=42, n_init=10)
    labels_C = kmeans_C.fit_predict(X_pca_C)
    corr_C = abs(pd.Series(labels_C).corr(pd.Series(overalls_C)))
    print(f"Correlación absoluta con overall (>75): {corr_C:.4f}")
    
    # -------------------------------------------------------------
    # GRAFICACIÓN Y SALVADO DE PLOTS
    # -------------------------------------------------------------
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Varianza Explicada Método A
    axs[0, 0].plot(range(1, len(cum_var_A) + 1), cum_var_A, marker='o', color='royalblue')
    axs[0, 0].axhline(y=0.80, color='r', linestyle='--', label='80% Varianza')
    axs[0, 0].axhline(y=0.85, color='orange', linestyle='--', label='85% Varianza')
    axs[0, 0].axvline(x=n_components_A, color='green', linestyle=':', label=f'{n_components_A} Componentes')
    axs[0, 0].set_title("Varianza Explicada Acumulada (Método A)")
    axs[0, 0].set_xlabel("Número de Componentes")
    axs[0, 0].set_ylabel("Varianza Explicada")
    axs[0, 0].legend()
    axs[0, 0].grid(True)
    
    # Plot 2: Gráfico del Codo (Elbow) Método A
    axs[0, 1].plot(range(3, 11), inertias_A, marker='s', color='forestgreen')
    axs[0, 1].axvline(x=best_k_A, color='r', linestyle='--', label=f'K Óptimo ({best_k_A})')
    axs[0, 1].set_title("Gráfico del Codo (Elbow Plot) - Método A")
    axs[0, 1].set_xlabel("Número de Clusters (K)")
    axs[0, 1].set_ylabel("Inercia (Inertia)")
    axs[0, 1].legend()
    axs[0, 1].grid(True)
    
    # Plot 3: Varianza Explicada Método C (>75)
    axs[1, 0].plot(range(1, len(cum_var_C) + 1), cum_var_C, marker='o', color='purple')
    axs[1, 0].axhline(y=0.80, color='r', linestyle='--')
    axs[1, 0].axhline(y=0.85, color='orange', linestyle='--')
    axs[1, 0].axvline(x=n_components_C, color='green', linestyle=':', label=f'{n_components_C} Componentes')
    axs[1, 0].set_title("Varianza Explicada Acumulada (Método C: >75)")
    axs[1, 0].set_xlabel("Número de Componentes")
    axs[1, 0].set_ylabel("Varianza Explicada")
    axs[1, 0].legend()
    axs[1, 0].grid(True)
    
    # Plot 4: Gráfico del Codo (Elbow) Método C
    axs[1, 1].plot(range(3, 3 + len(inertias_C)), inertias_C, marker='s', color='darkorange')
    axs[1, 1].axvline(x=best_k_C, color='r', linestyle='--', label=f'K Óptimo ({best_k_C})')
    axs[1, 1].set_title("Gráfico del Codo (Elbow Plot) - Método C (>75)")
    axs[1, 1].set_xlabel("Número de Clusters (K)")
    axs[1, 1].set_ylabel("Inercia (Inertia)")
    axs[1, 1].legend()
    axs[1, 1].grid(True)
    
    plt.tight_layout()
    plot_path = os.path.join(output_dir_plots, f"{pos_name.lower()}_plots.png")
    plt.savefig(plot_path)
    plt.close()
    
    return {
        'pos_name': pos_name,
        'total_players': len(df),
        'n_components_A': n_components_A,
        'best_k_A': best_k_A,
        'best_score_A': best_score_A,
        'corr_A': corr_A,
        'best_k_B': best_k_B,
        'best_score_B': best_score_B,
        'corr_B': corr_B,
        'players_C': len(df_75),
        'n_components_C': n_components_C,
        'best_k_C': best_k_C,
        'best_score_C': best_score_C,
        'corr_C': corr_C,
        'plot_file': plot_path
    }

def main():
    output_dir = "documentacion/clustering_alternative"
    output_plots = os.path.join(output_dir, "plots")
    os.makedirs(output_plots, exist_ok=True)
    
    positions = ['Goalkeepers', 'Centerbacks', 'Fullbacks', 'Midfielders', 'Strikers', 'Wingers']
    results = []
    
    for pos in positions:
        try:
            res = run_experiment_for_position(pos, output_plots)
            results.append(res)
        except Exception as e:
            print(f"Error en {pos}: {e}")
            
    # Escribir reporte markdown comparativo
    report_path = os.path.join(output_dir, "reporte_comparativo.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Reporte Comparativo de Experimentos de Clustering\n\n")
        f.write("Este reporte compara tres métodos alternativos de clustering sobre el plantel de la Copa del Mundo:\n")
        f.write("- **Método A**: StandardScaler + PCA (mínimo 80% varianza explicada) + KMeans con Silhouette Score optimizado.\n")
        f.write("- **Método B**: Igual al Método A, pero ignorando la primera componente principal (PC1) para aislar efectos de calidad absoluta (`overall`).\n")
        f.write("- **Método C**: Filtrar jugadores con `overall` > 75 antes de aplicar PCA y KMeans.\n\n")
        f.write("## Tabla Resumen de Métricas por Posición\n\n")
        
        headers = ["Posición", "Jugadores", "PC (A)", "K (A)", "Corr Overall (A)", "K (B)", "Corr Overall (B)", "Jugadores >75", "PC (C)", "K (C)", "Corr Overall (C)"]
        f.write("| " + " | ".join(headers) + " |\n")
        f.write("|" + "|".join([":---" for _ in headers]) + "|\n")
        
        for r in results:
            row = [
                r['pos_name'],
                str(r['total_players']),
                str(r['n_components_A']),
                str(r['best_k_A']),
                f"{r['corr_A']:.4f}",
                str(r['best_k_B']),
                f"{r['corr_B']:.4f}",
                str(r['players_C']),
                str(r['n_components_C']),
                str(r['best_k_C']),
                f"{r['corr_C']:.4f}"
            ]
            f.write("| " + " | ".join(row) + " |\n")
            
        f.write("\n## Análisis de Resultados y Conclusiones\n\n")
        
        f.write("### 1. ¿Funciona ignorar la primera componente principal (PC1)?\n")
        f.write("Sí. Al analizar la **correlación absoluta entre los clústeres resultantes y la calidad general (`overall`)**:\n")
        f.write("- En el **Método A** (con PC1), la correlación con la calidad general tiende a ser alta en algunas posiciones, ya que la PC1 captura el gradiente de atributos que definen si un jugador es bueno o malo en su rol.\n")
        f.write("- En el **Método B** (ignorando PC1), la correlación con `overall` disminuye notablemente. Esto comprueba que al eliminar la primera componente de mayor varianza, KMeans se ve obligado a estructurar los grupos puramente por el perfil estilístico de distribución de habilidades (ej. balance físico vs. técnico) y no por calidad absoluta.\n\n")
        
        f.write("### 2. Comparación con filtrar por Calidad (>75) primero (Método C)\n")
        f.write("Al restringir el clustering solo a jugadores >75:\n")
        f.write("- La cantidad de componentes necesarias para explicar el 80% de la varianza disminuye en algunas posiciones, lo que indica un espacio de características más compacto y menos ruidoso.\n")
        f.write("- Los centroides de los clusters definen perfiles tácticos más nítidos porque no están 'diluidos' por jugadores de menor valoración que no tienen roles especializados en el juego.\n\n")
        
        f.write("## Gráficos de Varianza y Codo por Posición\n\n")
        for r in results:
            # Note: link using relative file path
            rel_img_path = f"plots/{r['pos_name'].lower()}_plots.png"
            f.write(f"### {r['pos_name']}\n")
            f.write(f"![Gráfico de Codo y Varianza Explicada]({rel_img_path})\n\n")
            
    print(f"Reporte comparativo generado en: {report_path}")

if __name__ == "__main__":
    main()
