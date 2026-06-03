import sqlite3
import json
import glob
import re
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append(os.path.join(base_dir, 'scripts'))
from merge_players import normalize_string

# Load sample from db
db_convocados_path = os.path.join(base_dir, "data", "recommender_data", "convocados.db")
conn = sqlite3.connect(db_convocados_path)
cur = conn.cursor()
cur.execute("SELECT jugador FROM convocados")
db_names = [row[0] for row in cur.fetchall()]
conn.close()

# Load sample from kmeans
kmeans_names = []
pattern = os.path.join(base_dir, "data", "clustering_maps", "kmeans_*_full_distances.json")
for file_path in glob.glob(pattern):
    with open(file_path, "r", encoding="utf-8") as f:
        clusters = json.load(f)
    for cluster in clusters:
        for player in cluster.get("players", []):
            kmeans_names.append(player.get("long_name", ""))

print(f"Total DB names: {len(db_names)}")
print(f"Total Kmeans names: {len(kmeans_names)}")

# Try regex match helper
def match_names(db_name, clean_name):
    norm_db = normalize_string(db_name)
    norm_clean = normalize_string(clean_name)
    
    # If they match exactly
    if norm_db == norm_clean:
        return True
        
    # Replace \ufffd with wildcard for matching
    if '\ufffd' in norm_db or '\u00ef\u00bf\u00bd' in norm_db:
        # Replace either character sequence
        pat_str = norm_db.replace('\ufffd', '.?').replace('\u00ef\u00bf\u00bd', '.?')
        # Also clean up multiple dots
        pat_str = re.sub(r'\.+', '.?', pat_str)
        try:
            if re.match('^' + pat_str + '$', norm_clean):
                return True
        except Exception:
            pass
            
    # Try word-level matching (exact words, ignoring connectors/short words)
    connectors = {'de', 'e', 'y', 'da', 'do', 'di', 'la', 'el', 'al', 'del', 'dos'}
    db_words = [w for w in norm_db.split() if '\ufffd' not in w and w not in connectors and len(w) > 1]
    clean_words = set(w for w in norm_clean.split() if w not in connectors)
    
    if db_words and all(dw in clean_words for dw in db_words):
        return True
        
    return False

matches = 0
for dbn in db_names[:100]:
    found = None
    for kn in kmeans_names:
        if match_names(dbn, kn):
            found = kn
            break
    if found:
        matches += 1
        print(f"MATCH: {repr(dbn)} -> {repr(found)}")
    else:
        print(f"MISS: {repr(dbn)}")

print(f"Match rate on first 100: {matches}%")
