import pandas as pd 

df = pd.read_csv("data/player_similarity/FC26_20250921.csv", low_memory=False)

columns_to_keep = [
    'short_name', 'overall', 'potential', 'age', 'height_cm', 'weight_kg', 'nationality_name', 'skill_moves', 
    'pace', 'passing', 'shooting', 'dribbling', 'defending', 'physic',
    "attacking_crossing", "attacking_finishing", "attacking_heading_accuracy", 
    "attacking_short_passing", "attacking_volleys", "skill_dribbling", 
    "skill_curve", "skill_fk_accuracy", "skill_long_passing", 
    "skill_ball_control", "movement_acceleration", "movement_sprint_speed", 
    "movement_agility", "movement_reactions", "movement_balance", 
    "power_shot_power", "power_jumping", "power_stamina", 
    "power_strength", "power_long_shots", "mentality_aggression", 
    "mentality_interceptions", "mentality_positioning", "mentality_vision", 
    "mentality_penalties", "mentality_composure", "defending_marking_awareness", 
    "defending_standing_tackle", "defending_sliding_tackle"
]

# Seleccionamos las columnas (defending corresponde a defense y shooting a shotting)
df_filtered = df[columns_to_keep]



df_filtered.to_json("data/player_similarity/player_similarity_codebase.json", orient="records", indent=4)

print("LISTO")