import re
import sqlite3
import os

def clean_club_name(club):
    if not club:
        return ""
    club = club.replace('*', '').strip()
    # Remove country code suffix like /GER, , RPC, etc.
    if ',' in club or '/' in club:
        sep = ',' if ',' in club else '/'
        parts = club.rsplit(sep, 1)
        suffix = parts[-1].strip()
        # Clean country code: typically 2-4 characters
        if len(suffix) <= 4 and suffix.isalpha():
            return parts[0].strip()
    return club

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

    # Palabras clave de posición al inicio de la línea
    position_pattern = re.compile(
        r'^(arqueros|guardametas|porteros|defensores|defensa|defensas|mediocampistas|centrocampistas|volantes|delanteros|mediocampistas/delanteros|mediocampistas/ delanteros)\b',
        re.IGNORECASE
    )

    for line in lines:
        line_upper = line.upper()
        # Excluir líneas de cabecera, de exclusión o placeholders
        if line == "Lista de Convocados" or line_upper.startswith("GRUPO") or "AÚN NO PRESENTÓ" in line_upper or "SIN CONFIRMAR" in line_upper:
            continue
        if line.startswith("*") or line == "Bakambu":
            continue

        # Determinar si es una línea de lista de jugadores por posición (comienza con una palabra clave de posición)
        if position_pattern.match(line):
            pos_part, players_part = line.split(":", 1)
            players_part = players_part.strip().strip(".")

            # Reemplazar la conjunción ' y ', ' e ' o ' and ' con una coma para facilitar el split
            players_part = re.sub(r'\s+y\s+', ',', players_part)
            players_part = re.sub(r'\s+e\s+', ',', players_part)
            players_part = re.sub(r'\s+and\s+', ',', players_part)


            # Separar por comas (cuidando comas dentro de paréntesis)
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
                    player_name = p
                    club_name = "Desconocido"

                # Limpiar el nombre de estrellas y de apodos entre comillas dobles/simples (rectas o tipográficas)
                player_name = player_name.replace('*', '').strip()
                player_name = re.sub(r'[\"“’\u201d\u201c’‘\'](.*?)[“\"’\u201d\u201c’‘\']', '', player_name)
                player_name = re.sub(r'\s+', ' ', player_name).strip()

                # Limpiar el nombre del club de sufijos de país
                club_name = clean_club_name(club_name)

                cursor.execute('INSERT INTO convocados (pais, jugador, equipo) VALUES (?, ?, ?)',
                               (current_country, player_name, club_name))
        else:
            # Si no tiene ":" y no coincide con exclusiones, se considera el nombre de un país
            if ":" not in line:
                current_country = line.strip()

    conn.commit()
    conn.close()

    print(f"Base de datos creada exitosamente en: {db_filepath}")

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    md_file = os.path.join(base_dir, 'Lista de Convocados.md')
    db_file = os.path.join(base_dir, 'data', 'recommender_data', 'convocados.db')

    parse_markdown_and_create_db(md_file, db_file)

