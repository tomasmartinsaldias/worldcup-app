import os
import re
import json
import sqlite3
import unicodedata
import pandas as pd
import numpy as np

# Normalizar nombres para comparación (remover diacríticos, acentos y espacios adicionales)
def normalize_name(text):
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = text.replace("?", "i")
    char_map = {
        'ı': 'i', 'ğ': 'g', 'ş': 's', 'ç': 'c', 'ö': 'o', 'ü': 'u',
        'ñ': 'n', 'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ã': 'a', 'õ': 'o', 'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
    }
    for k, v in char_map.items():
        text = text.replace(k, v)
    text = unicodedata.normalize('NFD', text)
    text = "".join([c for c in text if 'a' <= c <= 'z' or c == ' '])
    text = " ".join(text.split())
    return text

def clean_for_api_search(name):
    if not isinstance(name, str):
        return ""
    name = name.replace("?", "i")
    char_map = {
        'ı': 'i', 'ğ': 'g', 'ş': 's', 'ç': 'c', 'ö': 'o', 'ü': 'u',
        'İ': 'I', 'Ğ': 'G', 'Ş': 'S', 'Ç': 'C', 'Ö': 'O', 'Ü': 'U',
        'ñ': 'n', 'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ã': 'a', 'õ': 'o', 'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
    }
    for k, v in char_map.items():
        name = name.replace(k, v)
    name = re.sub(r'[^a-zA-Z0-9\s\-]', '', name)
    return " ".join(name.split())

def standardize_club_name(club):
    if not club or not isinstance(club, str):
        return "Agente Libre"
        
    club = club.strip()
    club = re.sub(r'[/,]\s*(GER|FRA|ITA|ESP|ENG|KSA|EEUU|USA|COL|MEX|POR|BRA|RUS|TUR|ING|ALE|ESC|RPC|PBJ|AUT|DIN|EAU|SRB|CHN|RUM|POL|KZJ|SUI|CHI|NZL|GAL|BUL|UAE|SAU|ISR|IRQ|CZE|UKR|BEL|NED|JAP|SUE|ARA|IRK|IRN|EAU|IND|TAI|CAT|FRANCIA|EGIPTO|MARRUECOS|JORDANIA|ECUADOR|MALASIA)$', '', club, flags=re.IGNORECASE).strip()
    
    mapping = {
        'ac milan': 'AC Milan',
        'milan': 'AC Milan',
        'ajax': 'Ajax',
        'al ahli': 'Al-Ahli',
        'al-ahli': 'Al-Ahli',
        'al-ahli sfc': 'Al-Ahli',
        'al-ahli saudi fc': 'Al-Ahli',
        'al ain': 'Al-Ain',
        'al-ain': 'Al-Ain',
        'al-ain fc': 'Al-Ain',
        'al ittihad': 'Al-Ittihad',
        'al-ittihad': 'Al-Ittihad',
        'al-ittihad club': 'Al-Ittihad',
        'al nassr': 'Al-Nassr',
        'al-nassr fc': 'Al-Nassr',
        'al-nassr': 'Al-Nassr',
        'al qadisiah': 'Al-Qadisiah',
        'al qadisiya': 'Al-Qadisiah',
        'al-qadisiyah fc': 'Al-Qadisiah',
        'al-karma': 'Al-Karma',
        'al-shorta': 'Al-Shorta',
        'al-zawraa sc': 'Al-Zawraa',
        'al-zawraa': 'Al-Zawraa',
        'america': 'Club América',
        'america de mexico': 'Club América',
        'club america': 'Club América',
        'anderlecht': 'Anderlecht',
        'arsenal': 'Arsenal',
        'arsenal fc': 'Arsenal',
        'athletic de bilbao': 'Athletic Club',
        'athletic bilbao': 'Athletic Club',
        'athletic club': 'Athletic Club',
        'atletico madrid': 'Atlético de Madrid',
        'atletico de madrid': 'Atlético de Madrid',
        'bayern munich': 'Bayern Múnich',
        'bayern munich': 'Bayern Múnich',
        'basaksehir': 'Başakşehir FK',
        'basaksehir fk': 'Başakşehir FK',
        'betis': 'Real Betis',
        'real betis': 'Real Betis',
        'bournemouth': 'AFC Bournemouth',
        'afc bournemouth': 'AFC Bournemouth',
        'brujas': 'Club Brujas',
        'copenhague': 'Copenhague',
        'copenhagen': 'Copenhague',
        'coventry': 'Coventry City',
        'coventry city': 'Coventry City',
        'dinamo zagreb': 'Dinamo Zagreb',
        'esteghlal fc': 'Esteghlal',
        'esteghlal tehran fc': 'Esteghlal',
        'esteghlal': 'Esteghlal',
        'fenerbahce': 'Fenerbahçe',
        'fenerbahce': 'Fenerbahçe',
        'fenerbahce sk/betis': 'Fenerbahçe',
        'feyenoord': 'Feyenoord',
        'inter': 'Inter de Milán',
        'inter miami': 'Inter Miami',
        'inter milan': 'Inter de Milán',
        'inter de milan': 'Inter de Milán',
        'inter de milan': 'Inter de Milán',
        'inter pa': 'Inter de Milán',
        'olympiacos fc': 'Olympiacos',
        'olympiakos': 'Olympiacos',
        'olympique de marseille': 'Olympique de Marsella',
        'olympique de marsella': 'Olympique de Marsella',
        'olympique marsella': 'Olympique de Marsella',
        'marseille': 'Olympique de Marsella',
        'marsella': 'Olympique de Marsella',
        'monaco': 'AS Mónaco',
        'as monaco': 'AS Mónaco',
        'monaco': 'AS Mónaco',
        'nice': 'OGC Nice',
        'niza': 'OGC Nice',
        'ogc nice': 'OGC Nice',
        'olympique lyon': 'Olympique de Lyon',
        'olympique de lyon': 'Olympique de Lyon',
        'pec zwolle': 'PEC Zwolle',
        'psv': 'PSV Eindhoven',
        'psv eindhoven': 'PSV Eindhoven',
        'pyramids': 'Pyramids FC',
        'pyramids fc': 'Pyramids FC',
        'raja casablanca': 'Raja Casablanca',
        'red bull salzburgo': 'RB Salzburg',
        'salzburgo': 'RB Salzburg',
        'rizespor': 'Çaykur Rizespor',
        'caykur rizespor': 'Çaykur Rizespor',
        'roma': 'AS Roma',
        'as roma': 'AS Roma',
        'sheffield united': 'Sheffield United',
        'sheffield united f.c.': 'Sheffield United',
        'sporting': 'Sporting CP',
        'sporting cp': 'Sporting CP',
        'sporting de portugal': 'Sporting CP',
        'st. pauli': 'St. Pauli',
        'fc st. pauli': 'St. Pauli',
        'stade rennais': 'Stade Rennais',
        'standard liege': 'Standard de Lieja',
        'standard lieja': 'Standard de Lieja',
        'sunderland': 'Sunderland',
        'sunderland afc': 'Sunderland',
        'tottenham': 'Tottenham Hotspur',
        'tottenham hotspur': 'Tottenham Hotspur',
        'tractor sazi tabriz fc': 'Tractor SC',
        'tractor': 'Tractor SC',
        'union saint-gilloise': 'Union Saint-Gilloise',
        'venezia': 'Venezia FC',
        'venezia fc': 'Venezia FC',
        'viktoria pilzno': 'Viktoria Plzeň',
        'viktoria plzen': 'Viktoria Plzeň',
        'west ham': 'West Ham United',
        'west ham united': 'West Ham United',
        'west ham united/marsella': 'West Ham United',
        'wolfsburg': 'Wolfsburgo',
        'wolfsburgo': 'Wolfsburgo',
        'young boys': 'BSC Young Boys',
    }
    
    import unicodedata
    norm = unicodedata.normalize('NFD', club.lower())
    norm = "".join([c for c in norm if not unicodedata.combining(c)]).strip()
    norm = norm.replace('.', '').replace(',', '').replace('f.c.', 'fc').replace('s.f.c.', 'sfc')
    
    if norm in mapping:
        return mapping[norm]
        
    return club

def add_column_if_not_exists(cursor, table, col, col_type):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type};")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            pass
        else:
            raise e

def parse_players_line(line):
    parts = line.split(":", 1)
    if len(parts) < 2:
        return None, []
    role = parts[0].strip()
    content = parts[1].strip()
    
    players = []
    current = []
    paren_depth = 0
    i = 0
    while i < len(content):
        c = content[i]
        if c == '(':
            paren_depth += 1
            current.append(c)
        elif c == ')':
            paren_depth -= 1
            current.append(c)
        elif paren_depth == 0 and (c == ',' or content[i:i+3] in [' y ', ' e ', ' y\n', ' e\n']):
            if c == ',':
                sep_len = 1
            else:
                sep_len = 3
            player_str = "".join(current).strip()
            if player_str:
                players.append(player_str)
            current = []
            i += sep_len - 1
        else:
            current.append(c)
        i += 1
    player_str = "".join(current).strip()
    if player_str:
        players.append(player_str)
        
    cleaned_players = []
    for p in players:
        p = p.rstrip('.')
        match = re.match(r'^(.*?)\s*\((.*?)\)$', p)
        if match:
            name = match.group(1).strip()
            club = match.group(2).strip()
            club = re.sub(r'[/,]\s*(GER|FRA|ITA|ESP|ENG|KSA|EEUU|USA|COL|MEX|POR|BRA|RUS|TUR|ING|ALE|ESC)$', '', club, flags=re.IGNORECASE).strip()
        else:
            name = p.strip()
            club = "Agente Libre"
        
        name = name.replace('*', '').strip()
        club = standardize_club_name(club)
        cleaned_players.append((name, club))
        
    return role, cleaned_players

spanish_to_fifa = {
    'México': 'MEX', 'Sudáfrica': 'RSA', 'Corea del Sur': 'KOR', 'República Checa': 'CZE',
    'Canadá': 'CAN', 'Bosnia y Herzegovina': 'BIH', 'Qatar': 'QAT', 'Suiza': 'SUI',
    'Brasil': 'BRA', 'Marruecos': 'MAR', 'Haití': 'HAI', 'Escocia': 'SCO',
    'Estados Unidos': 'USA', 'Paraguay': 'PAR', 'Australia': 'AUS', 'Turquía': 'TUR',
    'Alemania': 'GER', 'Curazao': 'CUR', 'Costa de Marfil': 'CIV', 'Ecuador': 'ECU',
    'Países Bajos': 'NED', 'Japón': 'JPN', 'Suecia': 'SWE', 'Túnez': 'TUN',
    'Bélgica': 'BEL', 'Egipto': 'EGY', 'Nueva Zelanda': 'NZL', 'España': 'ESP',
    'Cabo Verde': 'CPV', 'Arabia Saudita': 'KSA', 'Uruguay': 'URU', 'Francia': 'FRA',
    'Senegal': 'SEN', 'Irak': 'IRQ', 'Noruega': 'NOR', 'Argentina': 'ARG',
    'Argelia': 'ALG', 'Austria': 'AUT', 'Jordania': 'JOR', 'Portugal': 'POR',
    'RD Congo': 'COD', 'Uzbekistán': 'UZB', 'Colombia': 'COL', 'Inglaterra': 'ENG',
    'Croacia': 'CRO', 'Ghana': 'GHA', 'Panamá': 'PAN', 'Irán': 'IRN'
}

nationality_keywords = {
    'ARG': ['Argentina'], 'BRA': ['Brazil'], 'FRA': ['France'], 'ENG': ['England'], 
    'ESP': ['Spain'], 'GER': ['Germany'], 'POR': ['Portugal'], 'URU': ['Uruguay'], 
    'NED': ['Netherlands'], 'CRO': ['Croatia'], 'JPN': ['Japan'], 
    'USA': ['United States', 'US'], 'MEX': ['Mexico'], 'MAR': ['Morocco'], 
    'COL': ['Colombia'], 'BEL': ['Belgium'], 'NOR': ['Norway'], 'SEN': ['Senegal'], 
    'EGY': ['Egypt'], 'SWE': ['Sweden'], 'KOR': ['Korea, South', 'South Korea', 'Korea'], 
    'TUR': ['Turkey', 'Türkiye'], 'SUI': ['Switzerland'], 'CAN': ['Canada'], 'ECU': ['Ecuador'], 
    'AUT': ['Austria'], 'ALG': ['Algeria'], 'CIV': ['Cote d\'Ivoire', 'Ivory Coast', 'Côte d\'Ivoire'], 
    'SCO': ['Scotland'], 'AUS': ['Australia'], 'GHA': ['Ghana'], 'KSA': ['Saudi Arabia'], 
    'PAR': ['Paraguay'], 'CZE': ['Czech Republic', 'Czechia'], 'COD': ['DR Congo', 'Congo, Democratic Republic'], 
    'BIH': ['Bosnia-Herzegovina', 'Bosnia'], 'CPV': ['Cape Verde', 'Cabo Verde'], 'TUN': ['Tunisia'], 
    'IRQ': ['Iraq'], 'RSA': ['South Africa'], 'UZB': ['Uzbekistan'], 'QAT': ['Qatar'], 
    'NZL': ['New Zealand'], 'JOR': ['Jordan'], 'PAN': ['Panama'], 'HAI': ['Haiti'], 
    'CUR': ['Curacao', 'Curaçao'], 'IRN': ['Iran']
}

superstars = [
    'Lionel Messi', 'Kylian Mbappé', 'Kylian Mbappe', 'Jude Bellingham', 
    'Vinícius Júnior', 'Vinícius Jr', 'Rodri', 'Erling Haaland', 'Cristiano Ronaldo'
]

def resolve_name_aliases(name):
    aliases = {
        'leo messi': 'Lionel Messi',
        'lautaro mártinez': 'Lautaro Martínez',
        'lautaro martinez': 'Lautaro Martínez',
        'lea paredes': 'Leandro Paredes',
        'leo balerdi': 'Leonardo Balerdi',
        'nico gonzalez': 'Nicolás González',
        'nico gonzález': 'Nicolás González',
        'nico otamendi': 'Nicolás Otamendi',
        'nico tagliafico': 'Nicolás Tagliafico',
        'nico paz': 'Nicolás Paz',
        'julian alvarez': 'Julián Álvarez',
        'julián alvarez': 'Julián Álvarez',
        'julián álvarez': 'Julián Álvarez',
        'jose lopez': 'José Manuel López',
        'giuliano simeone': 'Giuliano Simeone',
        'grob': 'Pascal Groß',
        'brian gutierrez': 'Brian Gutiérrez',
        'brian gutiérrez': 'Brian Gutiérrez',
        'armando gonzalez': 'Armando González',
        'armando gonzález': 'Armando González',
        'guillermo martinez': 'Guillermo Martínez',
        'guillermo martínez': 'Guillermo Martínez',
    }
    norm = name.lower().strip()
    if norm in aliases:
        return aliases[norm]
        
    if norm.startswith("nico "):
        return "Nicolás " + name[5:]
    if norm.startswith("leo "):
        return "Leonardo " + name[4:]
    if norm.startswith("lea "):
        return "Leandro " + name[4:]
        
    return name

def resolve_from_transfermarkt_cache(cursor, player_name, fifa_code, current_age=None):
    player_name = resolve_name_aliases(player_name)
    cursor.execute("SELECT response_json FROM cache_transfermarkt WHERE query = ?;", (player_name,))
    row = cursor.fetchone()
    if not row:
        clean_name = clean_for_api_search(player_name)
        cursor.execute("SELECT response_json FROM cache_transfermarkt WHERE query = ?;", (clean_name,))
        row = cursor.fetchone()
        
    if row:
        try:
            api_data = json.loads(row[0])
            if api_data and 'results' in api_data:
                allowed_nats = [n.lower() for n in nationality_keywords.get(fifa_code, [])]
                best_cand = None
                best_score = -1.0
                
                for cand in api_data['results']:
                    cand_name = cand.get('name', '')
                    cand_age = cand.get('age')
                    cand_nats = [n.lower() for n in cand.get('nationalities', [])]
                    
                    nat_match = False
                    if not cand_nats:
                        nat_match = True
                    else:
                        for nat in cand_nats:
                            for ok_nat in allowed_nats:
                                if ok_nat in nat or nat in ok_nat:
                                    nat_match = True
                                    break
                            if nat_match: break
                    if not nat_match:
                        continue
                        
                    if cand_age is not None and current_age is not None:
                        if abs(current_age - cand_age) > 3:
                            continue
                            
                    set1 = set(normalize_name(player_name).split())
                    set2 = set(normalize_name(cand_name).split())
                    if not set1 or not set2:
                        continue
                    jaccard = len(set1.intersection(set2)) / len(set1.union(set2))
                    
                    if jaccard > best_score and jaccard >= 0.35:
                        best_score = jaccard
                        best_cand = cand
                        
                if best_cand:
                    mv = best_cand.get('marketValue')
                    mv_m = round(float(mv) / 1_000_000.0, 1) if mv is not None else None
                    age = best_cand.get('age')
                    club = best_cand.get('club', {}).get('name')
                    return mv_m, age, club
        except Exception:
            pass
    return None, None, None

def load_ages_from_wcq(wcq_dir, name_to_code):
    wcq_ages = {}
    for filename in os.listdir(wcq_dir):
        if filename.startswith("Player Standard Stats") and filename.endswith(".txt"):
            filepath = os.path.join(wcq_dir, filename)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if not line.strip() or line.startswith('Rk') or line.startswith('\t'):
                        continue
                    parts = line.strip().split('\t')
                    if len(parts) < 5:
                        continue
                    player_name = parts[1].strip()
                    squad_col = parts[3].strip()
                    squad_parts = squad_col.split(' ', 1)
                    if len(squad_parts) < 2:
                        continue
                    norm_team = normalize_name(squad_parts[1].strip())
                    code = name_to_code.get(norm_team)
                    if code:
                        try:
                            age = int(parts[4].strip())
                            wcq_ages[(normalize_name(player_name), code)] = age
                        except ValueError:
                            pass
    return wcq_ages

def get_players_from_wcq(wcq_dir, team_code, name_to_code):
    players = []
    for filename in os.listdir(wcq_dir):
        if filename.startswith("Player Standard Stats") and filename.endswith(".txt"):
            filepath = os.path.join(wcq_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip() or line.startswith('Rk') or line.startswith('\t'):
                        continue
                    parts = line.strip().split('\t')
                    if len(parts) < 10:
                        continue
                    squad_col = parts[3].strip()
                    squad_parts = squad_col.split(' ', 1)
                    if len(squad_parts) < 2:
                        continue
                    norm_team = normalize_name(squad_parts[1].strip())
                    code = name_to_code.get(norm_team)
                    if code == team_code:
                        player_name = parts[1].strip()
                        pos_raw = parts[2].strip()
                        role = 'Defensa'
                        if 'GK' in pos_raw: role = 'Portero'
                        elif 'DF' in pos_raw: role = 'Defensa'
                        elif 'MF' in pos_raw: role = 'Centrocampista'
                        elif 'FW' in pos_raw: role = 'Delantero'
                        
                        try:
                            minutes = int(parts[7].replace(',', '').strip())
                        except:
                            minutes = 0
                        try:
                            age = int(parts[4].strip())
                        except:
                            age = 26
                            
                        players.append({
                            'name': player_name,
                            'role': role,
                            'club': 'Desconocido',
                            'age': age,
                            'minutes': minutes
                        })
    players.sort(key=lambda x: x['minutes'], reverse=True)
    
    # Quitar duplicados por nombre
    seen = set()
    unique_players = []
    for p in players:
        norm = normalize_name(p['name'])
        if norm not in seen:
            seen.add(norm)
            unique_players.append(p)
            
    return unique_players[:30]

def load_fifa_market_values(cursor, ranking_path, name_to_code):
    market_values = {}
    if os.path.exists(ranking_path):
        with open(ranking_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.strip().split('\t')
                if len(parts) >= 5:
                    try:
                        nation_raw = parts[1].strip()
                        
                        # Si es un nombre duplicado con espacio (ej: 'France France'), quedarse con la mitad
                        nation_words = nation_raw.split()
                        half_len = len(nation_words) // 2
                        if len(nation_words) >= 2 and half_len > 0 and nation_words[:half_len] == nation_words[half_len:]:
                            nation_name = " ".join(nation_words[:half_len])
                        else:
                            nation_name = nation_raw
                            
                        val_str = parts[4].strip().lower()
                        val_eur = 0.0
                        # Remover caracteres que no sean dígitos, puntos o letras k/m/b
                        val_clean = re.sub(r'[^0-9.kmb]', '', val_str)
                        if 'bn' in val_str or 'b' in val_clean:
                            val_float = float(re.sub(r'[^0-9.]', '', val_clean))
                            val_eur = round(val_float * 1000.0, 1)
                        elif 'm' in val_str or 'm' in val_clean:
                            val_float = float(re.sub(r'[^0-9.]', '', val_clean))
                            val_eur = round(val_float, 1)
                        elif 'k' in val_str or 'k' in val_clean:
                            val_float = float(re.sub(r'[^0-9.]', '', val_clean))
                            val_eur = round(val_float / 1000.0, 3)
                            
                        norm_nation = normalize_name(nation_name)
                        code = name_to_code.get(norm_nation)
                        if code:
                            if code not in market_values:
                                market_values[code] = val_eur
                        else:
                            # Intento de mapeo por substring aproximado
                            matched = False
                            for k, v in name_to_code.items():
                                if len(k) <= 3:
                                    continue
                                if norm_nation in k or k in norm_nation:
                                    if v not in market_values:
                                        market_values[v] = val_eur
                                    matched = True
                                    break
                            if not matched:
                                # Fallback para nombres compuestos como 'Bosnia-Herzegovina Bosnia'
                                for token in norm_nation.split():
                                    if token in name_to_code:
                                        code_token = name_to_code[token]
                                        if code_token not in market_values:
                                            market_values[code_token] = val_eur
                                        break
                    except Exception:
                        continue
    return market_values

def main():
    base_dir = "c:/Users/tomas/Desktop/proyectos/worldcup-app"
    db_path = os.path.join(base_dir, "data", "worldcup_combined.db")
    md_path = os.path.join(base_dir, "Lista de Convocados.md")
    ranking_path = os.path.join(base_dir, "data", "ranking_fifa.txt")
    wcq_dir = os.path.join(base_dir, "data", "eliminatorias-2026")
    
    if not os.path.exists(db_path):
        print(f"Error: No se encontró la base de datos en {db_path}")
        return
    if not os.path.exists(md_path):
        print(f"Error: No se encontró la lista de convocados en {md_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Inicialización y Limpieza de Tablas
    print("--- Inicializando base de datos y limpiando tablas de planteles ---")
    cursor.execute("DROP TABLE IF EXISTS scraped_team_metrics;")
    cursor.execute("DROP TABLE IF EXISTS scraped_wc2026_probable_squads;")
    cursor.execute("DROP TABLE IF EXISTS scraped_unresolved_players;")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scraped_team_metrics (
        fifa_code TEXT PRIMARY KEY,
        market_value_eur REAL,
        recent_xg_avg REAL,
        recent_possession_avg REAL,
        global_popularity_score REAL,
        progressive_passes_per_90_avg REAL,
        sofascore_rating_avg REAL,
        cards_per_match_avg REAL,
        FOREIGN KEY (fifa_code) REFERENCES wc2026_teams (fifa_code)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scraped_wc2026_probable_squads (
        player_id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT,
        fifa_code TEXT,
        position TEXT,
        club TEXT,
        age INTEGER,
        caps INTEGER,
        goals INTEGER,
        market_value_eur REAL,
        is_star_player BOOLEAN,
        is_injured BOOLEAN,
        progressive_passes_per_90 REAL,
        sofascore_rating REAL,
        cards_propensity REAL,
        assists_recent INTEGER,
        minutes_recent INTEGER,
        FOREIGN KEY (fifa_code) REFERENCES wc2026_teams (fifa_code)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scraped_unresolved_players (
        player_id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT,
        fifa_code TEXT,
        position TEXT,
        club TEXT,
        age INTEGER,
        caps INTEGER,
        goals INTEGER,
        reason_unresolved TEXT,
        resolved BOOLEAN DEFAULT 0,
        FOREIGN KEY (fifa_code) REFERENCES wc2026_teams (fifa_code)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cache_transfermarkt (
        query TEXT PRIMARY KEY,
        response_json TEXT
    );
    """)
    conn.commit()
    
    # Agregar columna is_confirmed_squad a wc2026_teams si no existe
    add_column_if_not_exists(cursor, "wc2026_teams", "is_confirmed_squad", "BOOLEAN DEFAULT 0")
    conn.commit()
    
    # Cargar mapeo de nombres a códigos FIFA
    cursor.execute("SELECT fifa_code, wc2026_name, historical_name, intl_results_name FROM team_mappings;")
    name_to_code = {}
    for code, wc, hist, intl in cursor.fetchall():
        candidates = set()
        for name in [wc, hist, intl]:
            if name:
                candidates.add(normalize_name(name))
        
        if code == 'USA': candidates.update([normalize_name(x) for x in ['usa', 'united states', 'us']])
        elif code == 'MEX': candidates.update([normalize_name(x) for x in ['mexico', 'mex']])
        elif code == 'CAN': candidates.update([normalize_name(x) for x in ['canada', 'can']])
        elif code == 'IRN': candidates.update([normalize_name(x) for x in ['ir iran', 'iran', 'irn']])
        elif code == 'KOR': candidates.update([normalize_name(x) for x in ['korea republic', 'south korea', 'korea', 'kor']])
        elif code == 'CIV': candidates.update([normalize_name(x) for x in ["côte d'ivoire", "cote d'ivoire", "ivory coast", "civ"]])
        elif code == 'COD': candidates.update([normalize_name(x) for x in ["congo dr", "dr congo", "cod"]])
        elif code == 'TUR': candidates.update([normalize_name(x) for x in ["türkiye", "turkey", "tur"]])
        elif code == 'CZE': candidates.update([normalize_name(x) for x in ["czechia", "czech republic", "cze"]])
        elif code == 'BIH': candidates.update([normalize_name(x) for x in ["bosnia", "herzegovina", "bosnia and herzegovina", "bosnia-herzegovina"]])
        
        for cand in candidates:
            if cand:
                name_to_code[cand] = code

    # Cargar edades de Eliminatorias 2026
    wcq_ages = load_ages_from_wcq(wcq_dir, name_to_code)

    # Cargar valores oficiales de plantilla desde ranking_fifa.txt
    fifa_market_values = load_fifa_market_values(cursor, ranking_path, name_to_code)
    
    # Parsear Lista de Convocados.md
    print("Parseando Lista de Convocados.md...")
    with open(md_path, 'r', encoding='utf-8') as f:
        md_lines = f.readlines()
        
    teams_data = {}
    current_team = None
    role_mapping = {
        'arqueros': 'Portero',
        'defensores': 'Defensa',
        'mediocampistas': 'Centrocampista',
        'delanteros': 'Delantero',
        'mediocampistas/delanteros': 'Centrocampista',
        'mediocampistas/ delanteros': 'Centrocampista'
    }
    
    norm_spanish_to_fifa = {normalize_name(k): v for k, v in spanish_to_fifa.items()}
    clean_lines = [line.strip() for line in md_lines if line.strip()]
    
    i = 0
    while i < len(clean_lines):
        line = clean_lines[i]
        if re.match(r'^Grupo\s+[A-L]$', line, re.IGNORECASE):
            i += 1
            continue
        if line.lower() == 'sin confirmar':
            if current_team:
                teams_data[current_team] = {'is_confirmed': False, 'players': [], 'destacados': []}
            i += 1
            continue
        if ':' in line:
            parts = line.split(':', 1)
            label = parts[0].strip().lower()
            content = parts[1].strip()
            
            if 'destacado' in label:
                dest_names = []
                raw_names = re.split(r',|\s+y\s+|\s+e\s+', content)
                for rn in raw_names:
                    rn_clean = rn.strip().rstrip('.')
                    if rn_clean:
                        dest_names.append(rn_clean)
                if current_team and current_team in teams_data:
                    teams_data[current_team]['destacados'] = dest_names
            else:
                role = 'Defensa'
                for k, v in role_mapping.items():
                    if k in label:
                        role = v
                        break
                _, parsed_players = parse_players_line(line)
                if current_team and current_team in teams_data:
                    for name, club in parsed_players:
                        teams_data[current_team]['players'].append({'name': name, 'club': club, 'role': role})
            i += 1
            continue
            
        norm_line = normalize_name(line)
        if norm_line in norm_spanish_to_fifa:
            current_team = norm_spanish_to_fifa[norm_line]
            teams_data[current_team] = {'is_confirmed': True, 'players': [], 'destacados': []}
        i += 1

    # Ingesta para las 48 selecciones
    cursor.execute("SELECT team_name, fifa_code FROM wc2026_teams;")
    db_teams = cursor.fetchall()
    
    team_popularity = {
        'ARG': 98.0, 'BRA': 96.0, 'FRA': 97.0, 'ENG': 95.0, 'ESP': 94.0, 'GER': 91.0, 'POR': 95.0,
        'URU': 85.0, 'NED': 85.0, 'CRO': 75.0, 'JPN': 82.0, 'USA': 82.0, 'MEX': 80.0, 'MAR': 78.0,
        'COL': 80.0, 'BEL': 75.0, 'NOR': 72.0, 'SEN': 70.0, 'EGY': 70.0, 'SWE': 68.0, 'KOR': 68.0,
        'TUR': 65.0, 'SUI': 62.0, 'CAN': 60.0, 'ECU': 60.0, 'AUT': 60.0, 'ALG': 58.0, 'CIV': 55.0,
        'SCO': 55.0, 'AUS': 50.0, 'GHA': 50.0, 'KSA': 48.0, 'PAR': 45.0, 'CZE': 45.0, 'COD': 42.0,
        'BIH': 40.0, 'CPV': 40.0, 'TUN': 40.0, 'IRQ': 35.0, 'RSA': 35.0, 'UZB': 32.0, 'QAT': 30.0,
        'NZL': 30.0, 'JOR': 18.0, 'PAN': 15.0, 'HAI': 15.0, 'CUR': 12.0
    }
    
    print("\n--- Ingestando jugadores y métricas para las 48 selecciones ---")
    
    for team_name, code in db_teams:
        md_data = teams_data.get(code)
        
        is_confirmed = 0
        players_to_load = []
        destacados = []
        
        if md_data and md_data['is_confirmed']:
            is_confirmed = 1
            players_to_load = md_data['players']
            destacados = [normalize_name(x) for x in md_data['destacados']]
            print(f"  {team_name} ({code}): Cargando plantel CONFIRMADO ({len(players_to_load)} jugadores)")
        else:
            # Obtener top 30 jugadores de eliminatorias
            players_to_load = get_players_from_wcq(wcq_dir, code, name_to_code)
            print(f"  {team_name} ({code}): Cargando plantel NO confirmado vía Eliminatorias ({len(players_to_load)} jugadores)")
            
        cursor.execute("UPDATE wc2026_teams SET is_confirmed_squad = ? WHERE fifa_code = ?;", (is_confirmed, code))
        
        final_players = []
        for p in players_to_load:
            player_name = p['name']
            role = p.get('role') or p.get('position') or 'Defensa'
            club = p.get('club') or 'Desconocido'
            age_wiki = p.get('age') # None si no está especificado
            
            # Intentar buscar primero en edades de clasificatorias si no viene del MD
            wcq_age = wcq_ages.get((normalize_name(player_name), code))
            search_age = age_wiki if age_wiki is not None else wcq_age
            
            # Resolver de la caché local de Transfermarkt
            mv_m, tm_age, tm_club = resolve_from_transfermarkt_cache(cursor, player_name, code, search_age)
            
            p_age = tm_age if tm_age is not None else (search_age if search_age is not None else 26)
            p_club = tm_club if tm_club is not None else club
            p_club = standardize_club_name(p_club)
            p_mv = mv_m
            
            norm_name = normalize_name(player_name)
            is_destacado = any(d in norm_name or norm_name in d for d in destacados)
            is_super = any(normalize_name(s) == norm_name for s in superstars)
            is_star = 1 if (is_destacado or is_super or (p_mv is not None and p_mv >= 40.0)) else 0
            
            # Valores por defecto para variables temporales
            p_cards = 0.20 if role == 'Defensa' else (0.02 if role == 'Portero' else 0.10)
            
            cursor.execute("""
                INSERT INTO scraped_wc2026_probable_squads (
                    player_name, fifa_code, position, club, age, caps, goals, market_value_eur, 
                    is_star_player, is_injured, cards_propensity, assists_recent, minutes_recent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL);
            """, (player_name, code, role, p_club, p_age, 0, 0, p_mv, is_star, 0, p_cards))
            
            if p_mv is None:
                cursor.execute("""
                    INSERT INTO scraped_unresolved_players (player_name, fifa_code, position, club, age, caps, goals, reason_unresolved)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """, (player_name, code, role, p_club, p_age, 0, 0, "No coincidencia en cache local de Transfermarkt"))
                
        # Guardar métrica agregada
        team_market_value_eur = fifa_market_values.get(code, 0.0)
        pop = team_popularity.get(code, 40.0)
        
        cursor.execute("""
            INSERT INTO scraped_team_metrics (
                fifa_code, market_value_eur, recent_xg_avg, recent_possession_avg, 
                global_popularity_score, progressive_passes_per_90_avg, sofascore_rating_avg, cards_per_match_avg
            ) VALUES (?, ?, NULL, NULL, ?, NULL, NULL, 1.5);
        """, (code, team_market_value_eur, pop))
        
    conn.commit()
    
    # Reporte
    cursor.execute("SELECT COUNT(*) FROM scraped_wc2026_probable_squads;")
    squads_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM scraped_unresolved_players;")
    unres_count = cursor.fetchone()[0]
    
    print(f"\n--- Ingesta Finalizada ---")
    print(f"  Jugadores guardados en scraped_wc2026_probable_squads: {squads_count}")
    print(f"  Jugadores en scraped_unresolved_players (MV Nula): {unres_count}")
    
    conn.close()

if __name__ == "__main__":
    main()
