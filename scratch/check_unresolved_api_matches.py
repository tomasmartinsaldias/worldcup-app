import sqlite3
import pandas as pd
import requests
import json
import urllib.parse
import os
import unicodedata
import re
import sys

# Usar UTF-8 para consola de Windows
sys.stdout.reconfigure(encoding='utf-8')

def normalize_text(text):
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


def main():
    base_dir = "c:/Users/tomas/Desktop/proyectos/worldcup-app"
    csv_path = os.path.join(base_dir, "data", "worldcup-2026-predicts", "fifa_world_cup_2026_golden_dataset.csv")
    db_path = os.path.join(base_dir, "data", "worldcup_combined.db")
    
    conn = sqlite3.connect(db_path)
    df = pd.read_csv(csv_path)
    df['norm_name'] = df['name'].apply(normalize_text)
    
    csv_players = {row['norm_name']: row['name'] for idx, row in df.iterrows() if row['norm_name']}
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT player_id, player_name, fifa_code
        FROM scraped_wc2026_probable_squads
        WHERE market_value_eur IS NULL;
    """)
    unresolved = cursor.fetchall()
    
    print(f"Total unresolved in DB: {len(unresolved)}")
    
    check_limit = 0
    for pid, db_name, fifa_code in unresolved:
        norm = normalize_text(db_name)
        csv_name = csv_players.get(norm)
        if csv_name:
            check_limit += 1
            search_term = clean_for_api_search(csv_name)
            encoded = urllib.parse.quote(search_term)
            url = f"http://127.0.0.1:8000/players/search/{encoded}"
            
            print(f"\nChecking player: {db_name} ({fifa_code}) | CSV name: {csv_name} | Search term: {search_term}")
            try:
                r = requests.get(url, timeout=3)
                if r.status_code == 200:
                    data = r.json()
                    results = data.get('results', [])
                    print(f"  API results found: {len(results)}")
                    
                    allowed_nats = [n.lower() for n in nationality_keywords.get(fifa_code, [])]
                    
                    for cand in results:
                        cand_name = cand.get('name')
                        cand_nats = [n.lower() for n in cand.get('nationalities', [])]
                        mval = cand.get('marketValue')
                        
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
                                
                        set1 = set(normalize_text(search_term).split())
                        set2 = set(normalize_text(cand_name).split())
                        jaccard = len(set1.intersection(set2)) / len(set1.union(set2)) if set1.union(set2) else 0
                        
                        print(f"    Candidate: '{cand_name}' | Value: {mval} | Nationalities: {cand_nats} | Nat Match: {nat_match} | Jaccard Score: {jaccard:.3f}")
                else:
                    print(f"  API Error: {r.status_code}")
            except Exception as e:
                print(f"  Query Error: {e}")
                
            if check_limit >= 15:
                print("\nReached limit of 15 checks.")
                break
                
    conn.close()

if __name__ == "__main__":
    main()
