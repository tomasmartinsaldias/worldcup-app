import os
import re
import json
import sqlite3
import unicodedata
import pandas as pd

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
        'ø': 'o', 'æ': 'ae', 'å': 'a', 'ß': 'ss', 'ð': 'd', 'þ': 'th',
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
    name = unicodedata.normalize('NFD', name)
    name = "".join([c for c in name if not unicodedata.combining(c)])
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
        name = re.sub(r'^(?:and|y|e)\b\s*', '', name, flags=re.IGNORECASE).strip()
        if not name:
            continue
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
    if norm.startswith("andy "):
        return "Andrew " + name[5:]
        
    return name

def resolve_from_transfermarkt_cache(cursor, player_name, fifa_code, current_age=None):
    player_name = resolve_name_aliases(player_name)
    cursor.execute("SELECT response_json FROM cache_transfermarkt WHERE query = ?;", (player_name,))
    row = cursor.fetchone()
    if row:
        try:
            api_data = json.loads(row[0])
            if not api_data or not api_data.get('results'):
                row = None
        except Exception:
            row = None
            
    if not row:
        clean_name = clean_for_api_search(player_name)
        cursor.execute("SELECT response_json FROM cache_transfermarkt WHERE query = ?;", (clean_name,))
        row = cursor.fetchone()
        if row:
            try:
                api_data = json.loads(row[0])
                if not api_data or not api_data.get('results'):
                    row = None
            except Exception:
                row = None
        
    if not row:
        # Fallback to Jaccard or SequenceMatcher search of query column in the cache to handle inverted names, different spellings, or typos (e.g. Erling Braut Haaland, Jin-seop vs Jin-seob)
        import difflib
        cursor.execute("SELECT query, response_json FROM cache_transfermarkt;")
        all_cache = cursor.fetchall()
        norm_p = normalize_name(player_name)
        tokens_p = set(norm_p.split())
        if tokens_p:
            best_query_score = -1.0
            best_row = None
            for q_name, q_json in all_cache:
                try:
                    q_data = json.loads(q_json)
                    if not q_data or not q_data.get('results'):
                        continue
                except Exception:
                    continue
                norm_q = normalize_name(q_name)
                
                # Method 1: Jaccard (token-based, good for word additions/inversions)
                tokens_q = set(norm_q.split())
                jacc = len(tokens_p.intersection(tokens_q)) / len(tokens_p.union(tokens_q)) if tokens_q else 0.0
                
                # Method 2: Sequence similarity (character-based, good for spelling differences/typos)
                seq_ratio = difflib.SequenceMatcher(None, norm_p, norm_q).ratio()
                
                # Combine score
                is_match = (jacc >= 0.5) or (seq_ratio >= 0.8)
                score = max(jacc, seq_ratio)
                
                if is_match and score > best_query_score:
                    best_query_score = score
                    best_row = q_json
            if best_row:
                row = (best_row,)
                
    if not row:
        import requests
        import urllib.parse
        try:
            print(f"  [API] Buscando '{player_name}' en API local...")
            url = f"http://127.0.0.1:8000/players/search/{urllib.parse.quote(player_name)}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                resp_data = resp.json()
                if resp_data and resp_data.get('results'):
                    resp_str = json.dumps(resp_data)
                    cursor.execute("INSERT OR REPLACE INTO cache_transfermarkt (query, response_json) VALUES (?, ?);", (player_name, resp_str))
                    clean_name = clean_for_api_search(player_name)
                    if clean_name != player_name:
                        cursor.execute("INSERT OR REPLACE INTO cache_transfermarkt (query, response_json) VALUES (?, ?);", (clean_name, resp_str))
                    cursor.connection.commit()
                    row = (resp_str,)
                    print(f"    [+] Guardado en cache para '{player_name}'")
        except Exception as e:
            print(f"    [-] Error consultando API local: {e}")

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
                            
                    import difflib
                    set1 = set(normalize_name(player_name).split())
                    set2 = set(normalize_name(cand_name).split())
                    if not set1 or not set2:
                        continue
                    jaccard = len(set1.intersection(set2)) / len(set1.union(set2))
                    seq_ratio = difflib.SequenceMatcher(None, normalize_name(player_name), normalize_name(cand_name)).ratio()
                    
                    is_cand_match = (jaccard >= 0.35) or (seq_ratio >= 0.8)
                    score = max(jaccard, seq_ratio)
                    
                    if is_cand_match and score > best_score:
                        best_score = score
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

def get_golden_dataset_stats(csv_by_team, fifa_to_csv_teams, fifa_code, player_name):
    possible_teams = fifa_to_csv_teams.get(fifa_code, [fifa_code])
    csv_candidates = []
    for t in possible_teams:
        if t in csv_by_team:
            csv_candidates.extend(csv_by_team[t])
            
    norm_player = normalize_name(player_name)
    
    best_cand = None
    best_score = 0.0
    for cand in csv_candidates:
        norm_cand = normalize_name(cand['name'])
        if norm_player == norm_cand:
            return cand
        tokens_p = set(norm_player.split())
        tokens_c = set(norm_cand.split())
        if not tokens_p or not tokens_c:
            continue
        inter = tokens_p.intersection(tokens_c)
        union = tokens_p.union(tokens_c)
        jaccard = len(inter) / len(union)
        if jaccard > best_score:
            best_score = jaccard
            best_cand = cand
            
    if best_score >= 0.49:
        return best_cand
        
    return None

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

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "data", "worldcup_combined.db")
    md_path = os.path.join(base_dir, "Lista de Convocados.md")

    
    if not os.path.exists(db_path):
        print(f"Error: No se encontró la base de datos en {db_path}")
        return
    if not os.path.exists(md_path):
        print(f"Error: No se encontró la lista de convocados en {md_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Agregar columna is_confirmed_squad a wc2026_teams si no existe
    add_column_if_not_exists(cursor, "wc2026_teams", "is_confirmed_squad", "BOOLEAN DEFAULT 0")
    add_column_if_not_exists(cursor, "wc2026_teams", "dt", "TEXT")
    conn.commit()

    # Cargar mapeo de nombres a códigos FIFA para wcq_ages
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

    wcq_dir = os.path.join(base_dir, "data", "eliminatorias-2026")
    wcq_ages = load_ages_from_wcq(wcq_dir, name_to_code)
    
    # 1. Parsear el archivo Lista de Convocados.md
    print("Leyendo y parseando Lista de Convocados.md...")
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
                teams_data[current_team] = {
                    'is_confirmed': False,
                    'players': [],
                    'destacados': [],
                    'dt': None
                }
            i += 1
            continue
            
        if ':' in line:
            parts = line.split(':', 1)
            label = parts[0].strip().lower()
            content = parts[1].strip()
            
            if label == 'dt':
                dt_name = content.strip().rstrip('.')
                if current_team and current_team in teams_data:
                    teams_data[current_team]['dt'] = dt_name
            elif 'destacado' in label:
                dest_names = []
                raw_names = re.split(r',|\s+y\s+|\s+e\s+', content)
                for rn in raw_names:
                    rn_clean = rn.strip().rstrip('.')
                    if rn_clean:
                        dest_names.append(rn_clean)
                if current_team and current_team in teams_data:
                    teams_data[current_team]['destacados'] = dest_names
            else:
                # Handle trailing DT (like Argentina: Delanteros: ... DT: Lionel Scaloni.)
                dt_match = re.search(r'\.?\s+DT:\s*(.*)$', line, re.IGNORECASE)
                if dt_match:
                    dt_name = dt_match.group(1).strip().rstrip('.')
                    if current_team and current_team in teams_data:
                        teams_data[current_team]['dt'] = dt_name
                    line = line[:dt_match.start()].strip()
                    parts = line.split(':', 1)
                    label = parts[0].strip().lower()
                
                role = 'Defensa'
                for k, v in role_mapping.items():
                    if k in label:
                        role = v
                        break
                _, parsed_players = parse_players_line(line)
                if current_team and current_team in teams_data:
                    for name, club in parsed_players:
                        teams_data[current_team]['players'].append({
                            'name': name,
                            'club': club,
                            'role': role
                        })
            i += 1
            continue
            
        norm_line = normalize_name(line)
        if norm_line in norm_spanish_to_fifa:
            current_team = norm_spanish_to_fifa[norm_line]
            teams_data[current_team] = {
                'is_confirmed': True,
                'players': [],
                'destacados': [],
                'dt': None
            }
        i += 1
        
    print(f"Parseados {len(teams_data)} equipos del archivo Markdown.")
    

    cursor.execute("SELECT fifa_code, wc2026_name, historical_name, intl_results_name FROM team_mappings;")
    fifa_to_csv_teams = {}
    for code, wc, hist, intl in cursor.fetchall():
        candidates = set()
        if wc: candidates.add(wc)
        if hist: candidates.add(hist)
        if intl: candidates.add(intl)
        if code == 'IRN': candidates.update(['IR Iran', 'Iran'])
        elif code == 'KOR': candidates.update(['Korea Republic', 'South Korea'])
        elif code == 'CUR': candidates.update(['Curaçao', 'Curacao'])
        elif code == 'CIV': candidates.update(["Côte d'Ivoire", "Cote d'Ivoire", "Ivory Coast"])
        elif code == 'COD': candidates.update(["Congo DR", "DR Congo"])
        elif code == 'TUR': candidates.update(["Türkiye", "Turkey"])
        fifa_to_csv_teams[code] = list(candidates)
        
    # 3. Aplicar correcciones a la base de datos
    cursor.execute("SELECT team_name, fifa_code FROM wc2026_teams;")
    db_teams = cursor.fetchall()
    
    players_added = 0
    players_removed = 0
    players_updated = 0
    
    for team_name, fifa_code in db_teams:
        md_data = teams_data.get(fifa_code)
        
        # Si el equipo no está en el MD o está marcado como no confirmado
        if not md_data or not md_data['is_confirmed']:
            cursor.execute("UPDATE wc2026_teams SET is_confirmed_squad = 0, dt = NULL WHERE fifa_code = ?;", (fifa_code,))
            print(f"Seleccion ({fifa_code}): Marcada como NO confirmada.")
            continue
            
        dt_name = md_data.get('dt')
        cursor.execute("UPDATE wc2026_teams SET is_confirmed_squad = 1, dt = ? WHERE fifa_code = ?;", (dt_name, fifa_code))
        print(f"Seleccion ({fifa_code}): Procesando plantilla confirmada (MD)...")
        
        # Eliminar el plantel anterior (para evitar heredar datos obsoletos) e insertar de cero
        cursor.execute("DELETE FROM scraped_wc2026_probable_squads WHERE fifa_code = ?;", (fifa_code,))
        cursor.execute("DELETE FROM scraped_unresolved_players WHERE fifa_code = ?;", (fifa_code,))
        
        db_squad = []
        db_by_norm_name = {}
        
        md_players = md_data['players']
        md_destacados = [normalize_name(x) for x in md_data['destacados']]
        
        md_matched_ids = set()
        md_matched_norm_names = set()
        
        final_squad_players = [] # Lista de jugadores finales para calcular el percentil 75
        
        # Simulamos que todos son 'new' para que parse_convocados inserte los rosters correctos de Lista de Convocados.md
        for md_p in md_players:
            final_squad_players.append({
                'name': md_p['name'],
                'club': md_p['club'],
                'pos': md_p['role'],
                'is_new': True
            })
            
        # Saltamos el bloque A y B, yendo directo a la inserción
        if False:
            pass
            
        # C. Insertar jugadores nuevos y resolver sus estadísticas
        for fp in final_squad_players:
            if not fp['is_new']:
                continue
                
            wcq_age = wcq_ages.get((normalize_name(fp['name']), fifa_code))
            search_age = wcq_age
            
            # Resolver market value, age y club (desde cache o golden dataset)
            mv_m, tm_age, tm_club = resolve_from_transfermarkt_cache(cursor, fp['name'], fifa_code, search_age)
            p_club = tm_club if tm_club is not None else fp['club']
            p_club = standardize_club_name(p_club)
            p_mv = mv_m
            p_age = tm_age if tm_age is not None else (search_age if search_age is not None else 26)
            
            p_caps = 0
            p_goals = 0
            p_assists = 0
            p_mins = 0
            p_cards = 0.0
                
            cursor.execute("""
                INSERT INTO scraped_wc2026_probable_squads (
                    player_name, fifa_code, position, club, age, caps, goals, market_value_eur, 
                    is_star_player, is_injured, cards_propensity,
                    assists_recent, minutes_recent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (fp['name'], fifa_code, fp['pos'], p_club, p_age, p_caps, p_goals, p_mv, 
                  0, 0, p_cards, p_assists, p_mins))
                  
            new_id = cursor.lastrowid
            fp['id'] = new_id
            fp['val'] = p_mv
            players_added += 1
            
            # Si no se pudo resolver valor de mercado, registrar como no resuelto
            if p_mv is None:
                cursor.execute("""
                    INSERT INTO scraped_unresolved_players (player_name, fifa_code, position, club, age, caps, goals, reason_unresolved)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """, (fp['name'], fifa_code, fp['pos'], p_club, p_age, p_caps, p_goals, "New player added from MD, Transfermarkt not resolved"))
                
        # D. Calcular percentil 75 para marcar estrellas
        resolved_vals = [p['val'] for p in final_squad_players if p['val'] is not None]
        q75 = pd.Series(resolved_vals).quantile(0.75) if len(resolved_vals) > 0 else 10.0
        
        # E. Actualizar is_star_player (eliminado el check de destacados del markdown)
        for fp in final_squad_players:
            norm_fp_name = normalize_name(fp['name'])
            is_superstar = any(normalize_name(s) == norm_fp_name for s in superstars)
            is_high_val = fp['val'] is not None and fp['val'] >= 40.0
            
            is_star = 1 if (is_superstar or is_high_val) else 0
            
            cursor.execute("UPDATE scraped_wc2026_probable_squads SET is_star_player = ? WHERE player_id = ?;", (is_star, fp['id']))
            
    conn.commit()
    conn.close()
    
    print("\n--- Ingesta y Corrección de Planteles Finalizada ---")
    print(f"Jugadores agregados: {players_added}")
    print(f"Jugadores actualizados (posición/club): {players_updated}")
    print(f"Jugadores ficticios eliminados: {players_removed}")

if __name__ == "__main__":
    main()
