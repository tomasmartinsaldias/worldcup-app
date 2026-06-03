import os
import re
import sqlite3
import unicodedata
import json

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
    name = unicodedata.normalize('NFD', name)
    name = "".join([c for c in name if not unicodedata.combining(c)])
    name = re.sub(r'[^a-zA-Z0-9\s\-]', '', name)
    return " ".join(name.split())

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
                tokens_q = set(norm_q.split())
                if not tokens_q:
                    continue
                jacc = len(tokens_p.intersection(tokens_q)) / len(tokens_p.union(tokens_q))
                if jacc > best_query_score and jacc >= 0.5:
                    best_query_score = jacc
                    best_row = q_json
            if best_row:
                row = (best_row,)

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

def main():
    conn = sqlite3.connect('data/worldcup_combined.db')
    cursor = conn.cursor()
    
    # Load team mappings
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

    wcq_dir = 'data/eliminatorias-2026'
    wcq_ages = load_ages_from_wcq(wcq_dir, name_to_code)
    
    # Load players and check how many defaulted
    cursor.execute("SELECT player_name, fifa_code FROM scraped_wc2026_probable_squads;")
    players = cursor.fetchall()
    
    total = len(players)
    defaulted = 0
    defaulted_list = []
    
    for name, code in players:
        mv_m, tm_age, tm_club = resolve_from_transfermarkt_cache(cursor, name, code)
        wcq_age = wcq_ages.get((normalize_name(name), code))
        
        if tm_age is None and wcq_age is None:
            defaulted += 1
            defaulted_list.append((name, code))
            
    print(f"Total players: {total}")
    print(f"Defaulted to 26: {defaulted}")
    print("Sample defaulted players:")
    for n, c in defaulted_list[:15]:
        print(f"  {n} ({c})")

if __name__ == '__main__':
    main()
