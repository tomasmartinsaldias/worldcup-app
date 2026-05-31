import sqlite3, re, unicodedata, os

def normalize_name(text):
    if not isinstance(text, str): return ""
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

def main():
    conn = sqlite3.connect("data/worldcup_combined.db")
    cursor = conn.cursor()
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
        
        for cand in candidates:
            if cand:
                name_to_code[cand] = code

    ranking_path = "data/ranking_fifa.txt"
    with open(ranking_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.strip().split('\t')
            if len(parts) >= 5:
                nation_raw = parts[1].strip()
                nation_words = nation_raw.split()
                half_len = len(nation_words) // 2
                if len(nation_words) >= 2 and half_len > 0 and nation_words[:half_len] == nation_words[half_len:]:
                    nation_name = " ".join(nation_words[:half_len])
                else:
                    nation_name = nation_raw
                    
                val_str = parts[4].strip().lower()
                val_eur = 0.0
                val_clean = re.sub(r'[^0-9.kmb]', '', val_str)
                if 'bn' in val_str or 'b' in val_clean:
                    val_float = float(re.sub(r'[^0-9.]', '', val_clean))
                    val_eur = round(val_float * 1000.0, 1)
                elif 'm' in val_str or 'm' in val_clean:
                    val_float = float(re.sub(r'[^0-9.]', '', val_clean))
                    val_eur = round(val_float, 1)
                
                norm_nation = normalize_name(nation_name)
                code = name_to_code.get(norm_nation)
                
                # Check for USA, CAN, TUR, BIH specifically
                if norm_nation in ('united states usa', 'canada', 'turkiye', 'bosniaherzegovina bosnia', 'turkey', 'bosnia'):
                    print(f"MATCH: {norm_nation} -> code: {code} -> raw_val: {val_str} -> val_eur: {val_eur}")
    conn.close()

if __name__ == '__main__':
    main()
