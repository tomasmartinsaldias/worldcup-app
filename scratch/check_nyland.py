import difflib
import unicodedata
import sqlite3
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
        'ø': 'o', 'æ': 'ae', 'å': 'a', 'ß': 'ss', 'ð': 'd', 'þ': 'th',
    }
    for k, v in char_map.items():
        text = text.replace(k, v)
    text = unicodedata.normalize('NFD', text)
    text = "".join([c for c in text if 'a' <= c <= 'z' or c == ' '])
    text = " ".join(text.split())
    return text

def main():
    conn = sqlite3.connect('data/worldcup_combined.db')
    c = conn.cursor()
    
    player_name = "Jin-seop Park"
    
    c.execute("SELECT query, response_json FROM cache_transfermarkt;")
    all_cache = c.fetchall()
    norm_p = normalize_name(player_name)
    tokens_p = set(norm_p.split())
    
    print(f"norm_p: {norm_p}, tokens_p: {tokens_p}")
    
    for q_name, q_json in all_cache:
        if "Jin-seob" in q_name or "Jin-seop" in q_name:
            norm_q = normalize_name(q_name)
            tokens_q = set(norm_q.split())
            jacc = len(tokens_p.intersection(tokens_q)) / len(tokens_p.union(tokens_q)) if tokens_q else 0.0
            seq_ratio = difflib.SequenceMatcher(None, norm_p, norm_q).ratio()
            
            try:
                q_data = json.loads(q_json)
                has_results = bool(q_data and q_data.get('results'))
            except:
                has_results = False
                
            print(f"Match candidate: {q_name}")
            print(f"  norm_q: {norm_q}, tokens_q: {tokens_q}")
            print(f"  jacc: {jacc}, seq_ratio: {seq_ratio}, has_results: {has_results}")

if __name__ == '__main__':
    main()
