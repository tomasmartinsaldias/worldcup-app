import re
import sqlite3
import os
import sys

def parse_markdown_and_create_db(md_filepath, db_filepath):
    # Asegurarnos de que el directorio de la base de datos exista
    os.makedirs(os.path.dirname(db_filepath), exist_ok=True)
    
    # Conexión a SQLite
    conn = sqlite3.connect(db_filepath)
    cursor = conn.cursor()
    
    # Crear la tabla solicitada
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS convocados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pais TEXT,
            jugador TEXT,
            equipo TEXT
        )
    ''')
    
    # Limpiar tabla si ya existía para evitar duplicados al correr el script varias veces
    cursor.execute('DELETE FROM convocados')
    
    try:
        with open(md_filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {md_filepath}")
        return
        
    current_country = None
    
    for line in lines:
        # Excluir líneas que no son datos útiles
        if line == "Lista de Convocados":
            continue
        if line.startswith("Grupo"):
            continue
        if line.startswith("Sin confirmar"):
            continue
        if line.startswith("Destacado") or line.startswith("Destacdo") or line.startswith("Destacadado"):
            continue
        if line.startswith("*"):
            continue
        if line == "Bakambu": # artefacto suelto en el texto
            continue
            
        # Determinar si es una línea de lista de jugadores por posición (contiene ":")
        if ":" in line:
            pos_part, players_part = line.split(":", 1)
            players_part = players_part.strip().strip(".")
            
            # Reemplazar la conjunción ' y ' o ' e ' con una coma para facilitar el split
            # Se usa \s+ para asegurar que haya espacios y no afectar nombres o clubes
            players_part = re.sub(r'\s+y\s+', ',', players_part)
            players_part = re.sub(r'\s+e\s+', ',', players_part)
            
            # Separar por comas (cuidando comas dentro de paréntesis)
            # Un split simple por coma funciona si la coma siempre separa jugadores, 
            # pero a veces hay comas dentro del paréntesis ej: (Arsenal, ENG)
            # Para solucionarlo, podemos buscar cada bloque usando un regex iterativo
            
            # Buscamos patrones: "Nombre (Equipo)"
            # Puede haber casos donde falta el paréntesis o hay cosas raras
            matches = re.finditer(r'([^\,]+?\s*\([^)]+\))', players_part)
            found_players = [m.group(1).strip() for m in matches]
            
            # Si no encontró coincidencias con paréntesis, dividimos por comas normal como respaldo
            if not found_players:
                found_players = [p.strip() for p in players_part.split(',') if p.strip()]
            
            for p in found_players:
                p = p.strip().strip('.')
                if not p: continue
                
                # Extraer nombre y equipo usando regex
                match = re.match(r'^(.*?)\s*\((.*?)\)$', p)
                if match:
                    player_name = match.group(1).strip()
                    club_name = match.group(2).strip()
                else:
                    # Si por algún motivo no tiene el formato con paréntesis
                    player_name = p
                    club_name = "Desconocido"
                
                cursor.execute('INSERT INTO convocados (pais, jugador, equipo) VALUES (?, ?, ?)',
                               (current_country, player_name, club_name))
        else:
            # Si no tiene ":", se considera el nombre de un país
            current_country = line
            
    conn.commit()
    conn.close()
    
    print(f"Base de datos creada exitosamente en: {db_filepath}")

if __name__ == "__main__":
    # Rutas absolutas o relativas desde el directorio raíz
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    md_file = os.path.join(base_dir, 'Lista de Convocados.md')
    db_file = os.path.join(base_dir, 'data', 'recommender_data', 'convocados.db')
    
    parse_markdown_and_create_db(md_file, db_file)
