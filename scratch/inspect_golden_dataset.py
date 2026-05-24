import os
import pandas as pd
import sqlite3
import unicodedata
import sys

# Reconfigurar stdout para usar UTF-8 en Windows
sys.stdout.reconfigure(encoding='utf-8')

def normalize_text(text):
    if not isinstance(text, str):
        return ""
    # Convertir a minúsculas
    text = text.lower().strip()
    # Reemplazar '?' por nada (ya que representan caracteres especiales rotos en el CSV)
    text = text.replace("?", "")
    # Normalizar para eliminar acentos (NFD descompone caracteres acentuados)
    text = unicodedata.normalize('NFD', text)
    # Filtrar solo caracteres de la a a la z y espacios
    text = "".join([c for c in text if 'a' <= c <= 'z' or c == ' '])
    # Quitar espacios múltiples
    text = " ".join(text.split())
    return text

def main():
    base_dir = "c:/Users/User/Downloads/app_mundial/worldcup-app"
    csv_path = os.path.join(base_dir, "data", "worldcup-2026-predicts", "fifa_world_cup_2026_golden_dataset.csv")
    db_path = os.path.join(base_dir, "data", "worldcup_combined.db")
    
    if not os.path.exists(csv_path):
        print(f"Error: No se encontró el CSV en {csv_path}")
        return
    if not os.path.exists(db_path):
        print(f"Error: No se encontró la BD en {db_path}")
        return
        
    df = pd.read_csv(csv_path)
    conn = sqlite3.connect(db_path)
    
    db_players = pd.read_sql_query("SELECT player_id, player_name, fifa_code, position FROM scraped_wc2026_probable_squads", conn)
    
    # Aplicar normalización avanzada
    df['norm_name'] = df['name'].apply(normalize_text)
    db_players['norm_name'] = db_players['player_name'].apply(normalize_text)
    
    # Hacer merge por nombre normalizado
    merged = pd.merge(db_players, df, on='norm_name', how='inner')
    print(f"Coincidencias con normalización inteligente: {len(merged)} de {len(db_players)} ({(len(merged)/len(db_players))*100:.1f}%)")
    
    # Ver cuántas métricas nulas podemos rescatar con esto
    unresolved_db = pd.read_sql_query("SELECT player_name, fifa_code FROM scraped_wc2026_probable_squads WHERE market_value_eur IS NULL", conn)
    unresolved_db['norm_name'] = unresolved_db['player_name'].apply(normalize_text)
    unresolved_merged = pd.merge(unresolved_db, df, on='norm_name', how='inner')
    print(f"Jugadores con métricas nulas rescatados con normalización inteligente: {len(unresolved_merged)} de {len(unresolved_db)}")
    
    # Ejemplos de rescatados
    if len(unresolved_merged) > 0:
        print("\nEjemplos de jugadores con métricas nulas rescatados:")
        print(unresolved_merged[['player_name', 'name', 'team_name', 'efficiency_score']].head(15).to_string())
        
    conn.close()

if __name__ == "__main__":
    main()
