import os
import json
import sqlite3
import unicodedata
import re
import glob

def normalize_string(s):
    if not isinstance(s, str):
        return ""
    # Transliterate special characters that NFD does not map to ASCII
    replacements = {
        'ø': 'o', 'Ø': 'o',
        'æ': 'ae', 'Æ': 'ae',
        'å': 'a', 'Å': 'a',
        'ß': 'ss',
        'ı': 'i', 'İ': 'i',
        'đ': 'd', 'Đ': 'd',
        "'": "", '’': "",
        '\u200c': '',
        '-': ' ',
    }
    for char, repl in replacements.items():
        s = s.replace(char, repl)
        
    s = unicodedata.normalize('NFD', s)
    s = s.encode('ascii', 'ignore').decode('utf-8').strip().lower()
    
    # Strip Arabic article prefixes al / el at word boundaries
    s = re.sub(r'\b(al|el)\b\s*', '', s)
    
    # Normalize common prefix spacings
    s = s.replace('abdul ', 'abdul').replace('abdel ', 'abdel')
    
    # Map nickname joe to joseph at word boundary
    s = re.sub(r'\bjoe\b', 'joseph', s)
    
    # Normalize suffixes like "jr." or "jr" to "junior"
    s = re.sub(r'\bjr\b\.?', 'junior', s)
    
    # Map common nicknames/diminutivos to their full matches
    name_variants = {
        'leo messi': 'lionel messi',
        'andy robertson': 'andrew robertson',
        'noni madueke': 'chukwunonso madueke',
        'ollie watkins': 'oliver watkins',
        'grob': 'gross',
        'haaland': 'haland',
        'yaya sithole': 'sphephelo sithole',
        'johnny placide': 'johny placide',
        'wilguens pauguain': 'wilguens paugain',
        'jk duverne': 'jean kevin duverne',
        'jeanricner bellegarde': 'jean ricner bellegarde',
        'nestory irakunda': 'nestory irankunda',
        'kenny mclean': 'kenneth mclean',
        'cristophe kabongo': 'christophe kabongo',
        'redouane hahlal': 'redouane halhal',
        'michail sadilek': 'michal sadilek',
        'meshack elia': 'meschack elia',
        'richie laryea': 'richmond laryea',
        'ben slimane': 'benslimane',
        'ben romdhane': 'benromdhane',
        'ben seghir': 'benseghir',
        'ben ouanes': 'benouanes',
        'ben old': 'benjamin old',
        'ben waine': 'benjamin waine'
    }
    for k, v in name_variants.items():
        s = s.replace(k, v)
        
    return s

def match_names(norm_db, norm_target):
    # Exact match
    if norm_db == norm_target:
        return True
        
    # Wildcard match if \ufffd (replacement char) is present
    if '\ufffd' in norm_db or '\u00ef\u00bf\u00bd' in norm_db:
        pat_str = norm_db.replace('\ufffd', '.?').replace('\u00ef\u00bf\u00bd', '.?')
        pat_str = re.sub(r'\.+', '.?', pat_str)
        try:
            if re.match('^' + pat_str + '$', norm_target):
                return True
        except Exception:
            pass
            
    # Word-level containment (exact words, ignoring connectors)
    connectors = {'de', 'e', 'y', 'da', 'do', 'di', 'la', 'el', 'al', 'del', 'dos'}
    db_words = [w for w in norm_db.split() if '\ufffd' not in w and w not in connectors and len(w) > 1]
    target_words = set(w for w in norm_target.split() if w not in connectors)
    
    if db_words and all(dw in target_words for dw in db_words):
        return True
        
    return False

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Load Convocados from db
    db_convocados_path = os.path.join(base_dir, "data", "recommender_data", "convocados.db")
    print(f"Loading convocados from {db_convocados_path}...")
    conn = sqlite3.connect(db_convocados_path)
    cur = conn.cursor()
    cur.execute("SELECT jugador, pais, equipo FROM convocados")
    convocados = [{"jugador": row[0], "pais": row[1], "equipo": row[2]} for row in cur.fetchall()]
    conn.close()
    print(f"Loaded {len(convocados)} players from convocados.db")

    # 2. Load Photos from players_photos.json
    photos_path = os.path.join(base_dir, "frontend", "data", "players_photos.json")
    print(f"Loading photos from {photos_path}...")
    with open(photos_path, "r", encoding="utf-8") as f:
        photos_data = json.load(f)
    
    # Index photos by normalized name for fast O(1) lookup
    photo_lookup = {}
    photos_list = []
    for p in photos_data:
        fn_norm = normalize_string(p.get("fn", ""))
        n_norm = normalize_string(p.get("n", ""))
        url = p.get("p", "")
        if fn_norm:
            photo_lookup[fn_norm] = url
        if n_norm and n_norm not in photo_lookup:
            photo_lookup[n_norm] = url
        photos_list.append({
            "fn_norm": fn_norm,
            "n_norm": n_norm,
            "url": url
        })

    # 3. Load Kmeans clusters and distances
    print("Loading kmeans distance data...")
    kmeans_list = []
    kmeans_lookup = {}
    pattern = os.path.join(base_dir, "data", "clustering_maps", "kmeans_*_full_distances.json")
    for file_path in glob.glob(pattern):
        filename = os.path.basename(file_path)
        pos_match = re.search(r"kmeans_(.*)_full_distances\.json", filename)
        if not pos_match:
            continue
        position = pos_match.group(1).title()
        
        with open(file_path, "r", encoding="utf-8") as f:
            clusters = json.load(f)
            
        for cluster in clusters:
            cluster_id = cluster.get("cluster_id")
            for player in cluster.get("players", []):
                long_name = player.get("long_name", "")
                km_norm = normalize_string(long_name)
                item = {
                    "long_name": long_name,
                    "overall": player.get("overall"),
                    "cluster_id": cluster_id,
                    "distance": player.get("distance"),
                    "position": position,
                    "km_norm": km_norm
                }
                kmeans_list.append(item)
                kmeans_lookup[km_norm] = item
    print(f"Loaded {len(kmeans_list)} players from kmeans files.")

    # 4. Load Age and Market Value from worldcup_combined.db
    db_combined_path = os.path.join(base_dir, "data", "worldcup_combined.db")
    print(f"Loading squads info from {db_combined_path}...")
    conn = sqlite3.connect(db_combined_path)
    cur = conn.cursor()
    cur.execute("SELECT player_name, age, market_value_eur FROM scraped_wc2026_probable_squads")
    squad_list = []
    squad_lookup = {}
    for row in cur.fetchall():
        name = row[0]
        sq_norm = normalize_string(name)
        item = {
            "player_name": name,
            "age": row[1],
            "market_value_eur": row[2],
            "sq_norm": sq_norm
        }
        squad_list.append(item)
        squad_lookup[sq_norm] = item
    conn.close()
    print(f"Loaded {len(squad_list)} players from worldcup_combined.db")

    # 5. Perform the merge/crossing
    merged_list = []
    not_found_photos = 0
    not_found_kmeans = 0
    not_found_squads = 0

    for item in convocados:
        name_db = item["jugador"]
        country_db = item["pais"]
        club_db = item["equipo"]
        norm_db = normalize_string(name_db)
        
        # A. Find Photo URL
        photo_url = None
        if norm_db in photo_lookup:
            photo_url = photo_lookup[norm_db]
        else:
            # Fallback to slow matching
            for p in photos_list:
                if match_names(norm_db, p["fn_norm"]) or match_names(norm_db, p["n_norm"]):
                    photo_url = p["url"]
                    break
        if not photo_url:
            not_found_photos += 1
                
        # B. Find Kmeans data
        kmeans_info = None
        if norm_db in kmeans_lookup:
            kmeans_info = kmeans_lookup[norm_db]
        else:
            # Fallback to slow matching
            for km in kmeans_list:
                if match_names(norm_db, km["km_norm"]):
                    kmeans_info = km
                    break
        if not kmeans_info:
            not_found_kmeans += 1

        # C. Find Squad metadata (age, market_value_eur)
        squad_info = None
        if norm_db in squad_lookup:
            squad_info = squad_lookup[norm_db]
        else:
            # Fallback to slow matching
            for sq in squad_list:
                if match_names(norm_db, sq["sq_norm"]):
                    squad_info = sq
                    break
        if not squad_info:
            not_found_squads += 1

        # Extract values
        overall = kmeans_info["overall"] if kmeans_info else None
        cluster_id = kmeans_info["cluster_id"] if kmeans_info else None
        dist_centroid = kmeans_info["distance"] if kmeans_info else None
        position = kmeans_info["position"] if kmeans_info else None
        
        age = squad_info["age"] if squad_info else None
        market_value = squad_info["market_value_eur"] if squad_info else None
        
        merged_list.append({
            "NAME": name_db,
            "Overall": overall,
            "_URL": photo_url,
            "Posicion": position,
            "Cluster_id": cluster_id,
            "Dist_centroid": dist_centroid,
            "edad": age,
            "valor_de_mercado": market_value,
            "pais": country_db,
            "equipo": club_db
        })

    # Save to data/data_frontend/players_final.json
    output_path = os.path.join(base_dir, "data", "data_frontend", "players_final.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged_list, f, ensure_ascii=False, indent=2)
        
    # Calculate complete records count
    complete_count = sum(
        1 for p in merged_list
        if p["Overall"] is not None 
        and p["_URL"] is not None 
        and p["Posicion"] is not None 
        and p["Cluster_id"] is not None 
        and p["Dist_centroid"] is not None 
        and p["edad"] is not None 
        and p["valor_de_mercado"] is not None
    )
    complete_pct = (complete_count / len(merged_list)) * 100 if merged_list else 0.0

    print(f"\nSuccessfully unified player data. Output written to: {output_path}")
    print(f"Total unified players: {len(merged_list)}")
    print(f"Complete records (all fields populated): {complete_count} ({complete_pct:.2f}%)")
    print(f"Players missing photos: {not_found_photos}")
    print(f"Players missing kmeans metrics: {not_found_kmeans}")
    print(f"Players missing squad data: {not_found_squads}")

if __name__ == "__main__":
    main()
