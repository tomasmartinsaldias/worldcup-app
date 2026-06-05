import os
import sys
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Setup workspace paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

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

def main():
    print("=" * 70)
    print("   SIMULADOR DE SCORE AFECTIVO DE JUGADORES (S_jug)")
    print("=" * 70)
    
    df = load_dataset()
    
    # 1. Solicitar jugadores favoritos directos
    print("Definición de Jugadores Favoritos del Usuario:")
    favs_input = input("Ingrese los nombres de jugadores favoritos directos (separados por coma, ej: L. Messi, J. Bellingham): ").strip()
    if not favs_input:
        print("Debe ingresar al menos un jugador favorito para simular.")
        return
        
    fav_names = [f.strip() for f in favs_input.split(',') if f.strip()]
    resolved_favorites = []
    
    for name in fav_names:
        matches = df[(df['short_name'].str.lower() == name.lower()) | (df['long_name'].str.lower().str.contains(name.lower()))]
        if len(matches) == 0:
            print(f"⚠️  No se encontró ningún jugador para: '{name}'")
            continue
        p = matches.iloc[0]
        resolved_favorites.append(p)
        print(f"  ✅ Registrado: {p.short_name} ({p.player_positions}) - Overall: {p.overall}")
        
    if not resolved_favorites:
        print("❌ Ningún jugador favorito pudo ser resuelto.")
        return

    # 2. Configurar una plantilla ficticia o real para la selección a evaluar
    print("\n" + "="*50)
    print("Configurando Plantilla Activa para Evaluar")
    print("="*50)
    
    team_code = input("Código FIFA de la selección (ej: ARG, USA, CAN) [default: ARG]: ").strip().upper()
    if not team_code:
        team_code = "ARG"
        
    print("\nIngrese jugadores que integran la plantilla de este partido (nombres o parte del nombre, uno por línea).")
    print("Escriba 'fin' para terminar la lista o presione Enter para cargar convocados automáticos de esa selección en el dataset.")
    
    eval_squad = []
    while True:
        p_in = input("  Jugador: ").strip()
        if p_in.lower() == 'fin':
            break
        if not p_in:
            if not eval_squad:
                # Cargar automáticamente los que coincidan con la selección (si tiene columna o club similar, o buscando del dataset)
                # Como el dataset original FC26 tiene clubes y nacionalidades, filtramos por nationality_name o similar
                nat_matches = df[df['nationality_name'].str.lower().str.contains(team_code.lower(), na=False)]
                if len(nat_matches) > 0:
                    eval_squad = [nat_matches.iloc[i] for i in range(min(18, len(nat_matches)))]
                    print(f"  👉 Cargados {len(eval_squad)} jugadores automáticos de la nacionalidad '{team_code}'.")
                else:
                    # Fallback general si no hay nacionalidades en el dataset
                    eval_squad = [df.iloc[i] for i in range(100, 118)]
                    print("  👉 Cargada muestra aleatoria de plantilla por defecto.")
            break
        
        matches = df[df['short_name'].str.lower().str.contains(p_in.lower()) | df['long_name'].str.lower().str.contains(p_in.lower())]
        if len(matches) == 0:
            print("  ❌ No se encontró coincidencia.")
        else:
            p = matches.iloc[0]
            eval_squad.append(p)
            print(f"  + Agregado: {p.short_name} (Overall: {p.overall})")

    # Inyectar variables ficticias si no existen
    for p in eval_squad + resolved_favorites:
        if 'minutes_recent' not in p or pd.isna(p.get('minutes_recent')):
            # Asignar minutos ficticios basados en overall o random para simulación
            p['minutes_recent'] = int(p.overall * 15) if 'minutes_recent' not in p else p['minutes_recent']
        if 'market_value_eur' not in p or pd.isna(p.get('market_value_eur')):
            p['market_value_eur'] = int((p.overall ** 4) * 10)

    # 3. Precalculo de espacios PCA de 80% con PC1 por cada grupo táctico para los similares
    print("\nConstruyendo espacios vectoriales latentes por posición (PCA 80% + PC1)...")
    spaces = {}
    positions_mapping = {} # mapea player_id a su índice en el espacio posicional
    df_pos_dict = {}
    
    for pos_group in ['Goalkeepers', 'Centerbacks', 'Fullbacks', 'Midfielders', 'Wingers', 'Strikers']:
        df_pos = df[df['player_positions'].apply(clean_positions) == pos_group].copy().reset_index(drop=True)
        if len(df_pos) == 0:
            continue
            
        X = df_pos[FEATURE_COLUMNS].fillna(df_pos[FEATURE_COLUMNS].mean())
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        pca = PCA(random_state=42)
        X_pca = pca.fit_transform(X_scaled)
        cum_var = np.cumsum(pca.explained_variance_ratio_)
        n_components = np.argmax(cum_var >= 0.80) + 1
        
        space_pca = X_pca[:, :n_components]
        spaces[pos_group] = space_pca
        df_pos_dict[pos_group] = df_pos
        
        for idx, row in df_pos.iterrows():
            positions_mapping[row.player_id] = (pos_group, idx)

    # 4. Cálculo del Score Afectivo
    print("\n" + "="*50)
    print("            EJECUCIÓN DEL CÁLCULO S_jug")
    print("="*50)
    
    # Probabilidad de juego piecemeal
    def get_seleccion_total_minutes(code):
        if code == 'CAN': return 360
        if code in ['MEX', 'USA']: return 540
        return 900
        
    team_max_val = max([p['market_value_eur'] for p in eval_squad]) if eval_squad else 1000000
    total_mins = get_seleccion_total_minutes(team_code)
    
    def calculate_p_juego(p):
        mins = p.get('minutes_recent', 0)
        if mins > 0:
            return min(1.0, mins / total_mins)
        if team_max_val > 0:
            return min(1.0, p.get('market_value_eur', 0) / team_max_val)
        return 0.0

    # Determinar candidatos similares (Top 10-NN para cada favorito en su respectiva macro posición)
    similar_candidates = {} # player_id -> (affinity_w, p_juego, short_name, fav_name)
    epsilon = 0.1
    
    for fav in resolved_favorites:
        fav_id = fav.player_id
        if fav_id not in positions_mapping:
            continue
        pos_group, fav_idx = positions_mapping[fav_id]
        
        space = spaces[pos_group]
        df_pos = df_pos_dict[pos_group]
        
        # Calcular distancias a todos los de esa posición
        fav_vec = space[fav_idx]
        distances = np.sqrt(np.sum((space - fav_vec) ** 2, axis=1))
        
        # Encontrar vecinos
        temp_df = df_pos.copy()
        temp_df['distance'] = distances
        # Excluir al propio favorito
        temp_df = temp_df[temp_df['player_id'] != fav_id]
        
        # Obtener 10-NN
        top_10 = temp_df.sort_values('distance').head(10)
        for _, row in top_10.iterrows():
            w = 1.0 / (row['distance'] + epsilon)
            p_juego_candidate = calculate_p_juego(row)
            
            # Si el candidato ya existe de otro favorito, nos quedamos con la mayor afinidad
            if row['player_id'] in similar_candidates:
                if w > similar_candidates[row['player_id']][0]:
                    similar_candidates[row['player_id']] = (w, p_juego_candidate, row['short_name'], fav.short_name)
            else:
                similar_candidates[row['player_id']] = (w, p_juego_candidate, row['short_name'], fav.short_name)

    # Calcular J_d (Favoritos directos en la plantilla)
    J_d = 0.0
    directos_detectados = []
    for p in eval_squad:
        is_direct = any(fav.player_id == p.player_id for fav in resolved_favorites)
        if is_direct:
            pj = calculate_p_juego(p)
            J_d += pj
            directos_detectados.append((p.short_name, pj))

    # Calcular J_s (Similares en la plantilla)
    J_s = 0.0
    similares_detectados = []
    for p in eval_squad:
        # Si ya es favorito directo, no cuenta como similar
        is_direct = any(fav.player_id == p.player_id for fav in resolved_favorites)
        if not is_direct and p.player_id in similar_candidates:
            w, pj_cand, _, fav_ref = similar_candidates[p.player_id]
            pj = calculate_p_juego(p) # Calculado con el contexto de la plantilla actual
            contribucion = w * pj
            J_s += contribucion
            similares_detectados.append((p.short_name, fav_ref, w, pj, contribucion))

    # Aplicar la fórmula
    lambda_val = 0.5
    term_d = np.log(1.0 + J_d)
    term_s = lambda_val * np.log(1.0 + J_s)
    S_jug = term_d + term_s

    print("\nDETALLE DEL CÁLCULO:")
    print("-" * 75)
    print("1. Jugadores Favoritos Directos en Plantilla:")
    if directos_detectados:
        for name, pj in directos_detectados:
            print(f"  * {name:<20} | P_juego = {pj:.4f}")
    else:
        print("  * Ninguno detectado.")
    print(f"  --> Suma J_d = {J_d:.4f}  |  log(1 + J_d) = {term_d:.4f}")
    
    print("\n2. Jugadores Similares Detectados en Plantilla (Top-10 NN de tus Favoritos):")
    if similares_detectados:
        print(f"  {'Similar':<18} | {'Clon de':<12} | {'Afinidad (w)':<12} | {'P_juego':<8} | {'Contribución':<12}")
        for name, fav_ref, w, pj, contrib in similares_detectados:
            print(f"  * {name:<16} | {fav_ref:<12} | {w:.4f}       | {pj:.4f}  | {contrib:.4f}")
    else:
        print("  * Ninguno detectado.")
    print(f"  --> Suma J_s = {J_s:.4f}  |  lambda * log(1 + J_s) = {term_s:.4f}")
    
    print("-" * 75)
    print(f"🏆 SCORE JUGADOR FINAL (S_jug): {S_jug:.4f}")
    print("-" * 75)

if __name__ == '__main__':
    main()
