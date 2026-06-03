"""
Diagnóstico: por qué populate_data.py no extrae MV de la caché
para los jugadores que SÍ están en caché con MV.
"""
import sqlite3, json, unicodedata, re, difflib

db = r'c:\Users\tomas\Desktop\proyectos\worldcup-app\data\worldcup_combined.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

NATIONALITY_KEYWORDS = {
    'ARG': ['Argentina'], 'BRA': ['Brazil'], 'FRA': ['France'], 'ENG': ['England'],
    'ESP': ['Spain'], 'GER': ['Germany'], 'POR': ['Portugal'], 'URU': ['Uruguay'],
    'NED': ['Netherlands'], 'CRO': ['Croatia'], 'JPN': ['Japan'],
    'USA': ['United States', 'US'], 'MEX': ['Mexico'], 'MAR': ['Morocco'],
    'COL': ['Colombia'], 'BEL': ['Belgium'], 'NOR': ['Norway'], 'SEN': ['Senegal'],
    'EGY': ['Egypt'], 'SWE': ['Sweden'], 'KOR': ['Korea, South', 'South Korea', 'Korea'],
    'TUR': ['Turkey', 'Türkiye'], 'SUI': ['Switzerland'], 'CAN': ['Canada'],
    'ECU': ['Ecuador'], 'AUT': ['Austria'], 'ALG': ['Algeria'],
    'CIV': ["Cote d'Ivoire", "Ivory Coast", "Côte d'Ivoire"],
    'SCO': ['Scotland'], 'AUS': ['Australia'], 'GHA': ['Ghana'],
    'KSA': ['Saudi Arabia'], 'PAR': ['Paraguay'], 'CZE': ['Czech Republic', 'Czechia'],
    'COD': ['DR Congo', 'Congo, Democratic Republic'], 'BIH': ['Bosnia-Herzegovina', 'Bosnia'],
    'CPV': ['Cape Verde', 'Cabo Verde'], 'TUN': ['Tunisia'], 'IRQ': ['Iraq'],
    'RSA': ['South Africa'], 'UZB': ['Uzbekistan'], 'QAT': ['Qatar'],
    'NZL': ['New Zealand'], 'JOR': ['Jordan'], 'PAN': ['Panama'], 'HAI': ['Haiti'],
    'CUR': ['Curacao', 'Curaçao'], 'IRN': ['Iran'],
}

def normalize_name(text):
    if not isinstance(text, str): return ""
    text = text.lower().strip().replace("?", "i")
    char_map = {'ı':'i','ğ':'g','ş':'s','ç':'c','ö':'o','ü':'u','ñ':'n','á':'a','é':'e','í':'i','ó':'o','ú':'u','ã':'a','õ':'o','â':'a','ê':'e','î':'i','ô':'o','û':'u','à':'a','è':'e','ì':'i','ò':'o','ù':'u','ä':'a','ë':'e','ï':'i','ø':'o','æ':'ae','å':'a','ß':'ss','ð':'d','þ':'th'}
    for k, v in char_map.items(): text = text.replace(k, v)
    text = unicodedata.normalize('NFD', text)
    text = "".join([c for c in text if 'a' <= c <= 'z' or c == ' '])
    return " ".join(text.split())

cur.execute("SELECT query, response_json FROM cache_transfermarkt")
all_cache = {q: json.loads(r) for q, r in cur.fetchall() if r}

cur.execute("SELECT player_id, player_name, fifa_code, age FROM scraped_unresolved_players ORDER BY player_id")
unresolved = cur.fetchall()

def find_in_cache(player_name):
    norm_p = normalize_name(player_name)
    tokens_p = set(norm_p.split())
    best_score = -1.0
    best_data = None
    best_q = None
    for q_name, q_data in all_cache.items():
        if not q_data or not q_data.get("results"): continue
        norm_q = normalize_name(q_name)
        tokens_q = set(norm_q.split())
        if not tokens_q: continue
        jacc = len(tokens_p & tokens_q) / len(tokens_p | tokens_q)
        seq  = difflib.SequenceMatcher(None, norm_p, norm_q).ratio()
        score = max(jacc, seq)
        if (jacc >= 0.5 or seq >= 0.8) and score > best_score:
            best_score = score
            best_data  = q_data
            best_q     = q_name
    return best_data, best_q, best_score

print(f"{'ID':<4} {'Nombre':<30} {'FIFA':<5} {'Razon fallo'}")
print("-" * 90)

for pid, name, code, age in unresolved:
    api_data, matched_q, score = find_in_cache(name)
    if not api_data:
        print(f"{pid:<4} {name:<30} {code:<5} NO EN CACHE")
        continue
    
    allowed_nats = [n.lower() for n in NATIONALITY_KEYWORDS.get(code, [])]
    results = api_data.get("results", [])
    
    reasons = []
    best_cand = None
    best_cand_score = -1.0
    
    for cand in results:
        cand_name = cand.get("name", "")
        cand_age  = cand.get("age")
        cand_nats = [n.lower() for n in cand.get("nationalities", [])]
        cand_mv   = cand.get("marketValue")
        
        # Nat check
        nat_match = not cand_nats
        if not nat_match:
            for nat in cand_nats:
                for ok in allowed_nats:
                    if ok in nat or nat in ok:
                        nat_match = True; break
                if nat_match: break
        
        # Age check
        age_ok = True
        if cand_age is not None and age is not None and age != 26:
            age_ok = abs(age - cand_age) <= 3
        
        # Name check
        set1 = set(normalize_name(name).split())
        set2 = set(normalize_name(cand_name).split())
        jacc = len(set1 & set2) / len(set1 | set2) if (set1 and set2) else 0
        seq  = difflib.SequenceMatcher(None, normalize_name(name), normalize_name(cand_name)).ratio()
        name_ok = jacc >= 0.35 or seq >= 0.8
        name_score = max(jacc, seq)
        
        if nat_match and age_ok and name_ok and name_score > best_cand_score:
            best_cand_score = name_score
            best_cand = cand
        
        if not nat_match:
            reasons.append(f"NAT_FAIL({cand_name}:{cand_nats})")
        elif not age_ok:
            reasons.append(f"AGE_FAIL({cand_name}:edad={cand_age})")
        elif not name_ok:
            reasons.append(f"NAME_FAIL({cand_name}:j={jacc:.2f})")
    
    if best_cand:
        mv = best_cand.get("marketValue")
        print(f"{pid:<4} {name:<30} {code:<5} MATCH OK -> MV={mv} cand='{best_cand.get('name')}' score={best_cand_score:.2f}")
    else:
        reason_str = " | ".join(reasons[:3])
        print(f"{pid:<4} {name:<30} {code:<5} SIN MATCH: {reason_str}")

conn.close()
