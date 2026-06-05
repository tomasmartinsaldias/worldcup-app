import os
import sys
import pandas as pd
import numpy as np
import difflib
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Ensure correct workspace root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Dataset Paths
CSV_PATH = "data/player_similarity/FC26_20250921.csv"

FEATURE_COLUMNS = [
    'overall', 'potential', 'age', 'height_cm', 'weight_kg', 'skill_moves',
    'pace', 'passing', 'shooting', 'dribbling', 'defending', 'physic',
    'attacking_crossing', 'attacking_finishing', 'attacking_heading_accuracy',
    'attacking_short_passing', 'attacking_volleys', 'skill_dribbling',
    'skill_curve', 'skill_fk_accuracy', 'skill_long_passing', 'skill_ball_control',
    'movement_acceleration', 'movement_sprint_speed', 'movement_agility',
    'movement_reactions', 'movement_balance', 'power_shot_power',
    'power_jumping', 'power_stamina', 'power_strength', 'power_long_shots',
    'mentality_aggression', 'mentality_interceptions', 'mentality_positioning',
    'mentality_vision', 'mentality_penalties', 'mentality_composure',
    'defending_marking_awareness', 'defending_standing_tackle', 'defending_sliding_tackle'
]

def load_dataset():
    if not os.path.exists(CSV_PATH):
        print(f"Error: No se encontró el dataset en {CSV_PATH}")
        sys.exit(1)
    df = pd.read_csv(CSV_PATH, low_memory=False)
    # Clean string columns
    df['short_name'] = df['short_name'].fillna('')
    df['long_name'] = df['long_name'].fillna('')
    df['player_positions'] = df['player_positions'].fillna('')
    return df

def clean_positions(pos_string):
    if not pos_string:
        return 'Strikers'
    primary = pos_string.split(',')[0].strip().upper()
    if primary in ['GK']: return 'Goalkeepers'
    if primary in ['CB']: return 'Centerbacks'
    if primary in ['LB', 'RB', 'LWB', 'RWB']: return 'Fullbacks'
    if primary in ['CM', 'CDM', 'CAM', 'LM', 'RM']: return 'Midfielders'
    if primary in ['LW', 'RW', 'LF', 'RF']: return 'Wingers'
    return 'Strikers'
def build_spaces_for_position(df_pos):
    # Estandarización de atributos en el subconjunto específico de la posición
    X = df_pos[FEATURE_COLUMNS].fillna(df_pos[FEATURE_COLUMNS].mean())
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Espacio A: Espacio Completo Estandarizado (41 Dimensiones de la posición)
    space_a = X_scaled

    # PCA sin n_components fijo para calcular varianza explicada dinámica
    pca = PCA(random_state=42)
    X_pca_all = pca.fit_transform(X_scaled)
    
    # Encontrar cuántas componentes explican al menos el 80% de la varianza
    cum_var = np.cumsum(pca.explained_variance_ratio_)
    n_components = np.argmax(cum_var >= 0.80) + 1
    
    # 1. PCA con >= 80% de varianza completo (incluye PC1)
    space_pca_80_with_pc1 = X_pca_all[:, :n_components]
    
    # 2. PCA con >= 80% de varianza sin PC1 (PC2 en adelante)
    space_pca_80_no_pc1 = X_pca_all[:, 1:n_components]
    
    return space_a, space_pca_80_with_pc1, space_pca_80_no_pc1

def main():
    print("=" * 60)
    print("      PLAYGROUND DE SIMILITUD DE JUGADORES (MUNDIAL 2026)")
    print("=" * 60)
    
    df = load_dataset()
    print(f"Dataset cargado correctamente. Total de registros: {len(df)}")
    
    while True:
        target_player = None
        while target_player is None:
            query = input("\nIngrese el nombre del jugador a buscar (o 'salir' para terminar): ").strip()
            if not query:
                continue
            if query.lower() in ['salir', 'exit', 'q']:
                print("¡Hasta luego!")
                return
            
            # Búsqueda parcial de coincidencias
            matches = df[df['short_name'].str.lower().str.contains(query.lower()) | df['long_name'].str.lower().str.contains(query.lower())]
            
            if len(matches) == 0:
                print("❌ No se encontraron coincidencias directas.")
                # Intentar sugerir nombres parecidos usando difflib
                all_names = df['short_name'].unique().tolist()
                suggestions = difflib.get_close_matches(query, all_names, n=5, cutoff=0.5)
                if suggestions:
                    print("\nTal vez quisiste decir:")
                    for idx, name in enumerate(suggestions):
                        print(f"  [{idx}] {name}")
                    sel_sug = input("Seleccione el número de sugerencia o escriba el nombre (o presione Enter para volver a buscar): ").strip()
                    if sel_sug:
                        # Intentar primero como índice numérico
                        try:
                            sug_name = suggestions[int(sel_sug)]
                            matches = df[df['short_name'] == sug_name]
                            target_player = matches.iloc[0]
                        except (ValueError, IndexError):
                            # Si no es un número válido, buscar si coincide con el texto escrito
                            matching_sug = [s for s in suggestions if s.lower() == sel_sug.lower()]
                            if matching_sug:
                                matches = df[df['short_name'] == matching_sug[0]]
                                target_player = matches.iloc[0]
                            else:
                                print("❌ Selección inválida. Intente una nueva búsqueda.")
                continue
            elif len(matches) > 1:
                print(f"\nSe encontraron {len(matches)} coincidencias. Mostrando las primeras 10:")
                limit_matches = matches.head(10).reset_index(drop=True)
                for idx, row in enumerate(limit_matches.itertuples()):
                    print(f"  [{idx}] {row.short_name} ({row.player_positions}) - Overall: {row.overall} - Club: {row.club_name}")
                
                sel_idx = input("Seleccione el índice del jugador (o presione Enter para volver a buscar): ").strip()
                if not sel_idx:
                    continue
                try:
                    target_player = limit_matches.iloc[int(sel_idx)]
                except (ValueError, IndexError):
                    # Intentar buscar por coincidencia exacta de nombre de la lista mostrada
                    matching_names = limit_matches[limit_matches['short_name'].str.lower() == sel_idx.lower()]
                    if len(matching_names) > 0:
                        target_player = matching_names.iloc[0]
                    else:
                        print("❌ Selección inválida. Reintentando búsqueda.")
                        continue
            else:
                target_player = matches.iloc[0]
                
        print(f"\n🎯 Jugador Seleccionado: {target_player.short_name} ({target_player.player_positions})")
        
        # Determinar posición arquetípica
        pos_group = clean_positions(target_player.player_positions)
        print(f"Grupo táctico de posición: {pos_group}")
        
        # Filtrar población por esa posición
        df_pos = df[df['player_positions'].apply(clean_positions) == pos_group].copy().reset_index(drop=True)
        print(f"Tamaño de la población del grupo táctico {pos_group}: {len(df_pos)}")
        
        # Construir los espacios vectoriales para esta posición macro (80% varianza explicada)
        space_a, space_pca_80_with_pc1, space_pca_80_no_pc1 = build_spaces_for_position(df_pos)
        
        # Encontrar índice del jugador en el dataframe posicionado
        target_idx_list = df_pos[df_pos['player_id'] == target_player.player_id].index
        if len(target_idx_list) == 0:
            print("❌ Error inesperado: El jugador seleccionado no se encuentra en el subconjunto de su posición.")
            continue
        target_idx = target_idx_list[0]
        
        # Configuración de los parámetros
        print("\nMÉTODOS DE SIMILITUD:")
        print("  [1] Método A: Espacio Completo Estandarizado (41D)")
        print("  [2] Método B: PCA (80% var) con PC1 (Calidad + Estilo)")
        print("  [3] Método C: PCA (80% var) sin PC1 (Estilo puro)")
        method_opt = input("Seleccione el método [1, 2 o 3]: ").strip()
        if method_opt == '2':
            space = space_pca_80_with_pc1
            space_name = f"PCA Completo 80% (D:{space_pca_80_with_pc1.shape[1]})"
        elif method_opt == '3':
            space = space_pca_80_no_pc1
            space_name = f"PCA Sin PC1 80% (D:{space_pca_80_no_pc1.shape[1]})"
        else:
            space = space_a
            space_name = "Original Completo (41D)"
        
        # Calcular distancias desde el jugador objetivo a todos los demás de su posición
        target_vec = space[target_idx]
        distances = np.sqrt(np.sum((space - target_vec) ** 2, axis=1))
        
        # Agregar las distancias al DataFrame
        df_pos['distance'] = distances
        
        # Excluir al propio jugador
        df_results = df_pos[df_pos['player_id'] != target_player.player_id].copy()
        
        # 1. EJECUTAR K-NN DIRECTO (K=10)
        top_k = 10
        knn_candidates = df_results.sort_values('distance').head(top_k).copy().reset_index(drop=True)
        
        # 2. CALCULAR SCORE DE AFINIDAD (Decaimiento Inverso)
        # Formula: w_i = 1 / (d_i + epsilon) con epsilon = 0.1
        epsilon = 0.1
        knn_candidates['affinity_score'] = 1.0 / (knn_candidates['distance'] + epsilon)
        
        print(f"\n👥 10-NN Puro en {space_name}:")
        print(f"  * Calculando afinidades con decaimiento inverso (epsilon={epsilon})")
        
        print("-" * 95)
        print(f"{'Jugador':<25} | {'Overall':<7} | {'Club':<25} | {'Distancia':<10} | {'Score Afinidad (w)':<18}")
        print("-" * 95)
        for row in knn_candidates.itertuples():
            print(f"{row.short_name:<25} | {row.overall:<7} | {str(row.club_name)[:25]:<25} | {row.distance:.4f} | {row.affinity_score:.4f}")
        print("-" * 95)
        
        input("\nPresione Enter para realizar otra consulta...")

if __name__ == '__main__':
    main()


