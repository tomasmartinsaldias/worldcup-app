import os, re, sqlite3

def normalize_name(text):
    if not isinstance(text, str): return ""
    return text.lower().strip()

def main():
    ranking_path = "data/ranking_fifa.txt"
    name_to_code = {
        'bosnia-herzegovina': 'BIH',
        'bosnia': 'BIH',
        'canada': 'CAN',
        'turkey': 'TUR',
        'türkiye': 'TUR',
        'turkiye': 'TUR',
        'united states': 'USA',
        'usa': 'USA',
        'us': 'USA'
    }
    
    with open(ranking_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip() or line.startswith('#'): continue
            parts = line.strip().split('\t')
            # Let's print parts for matching teams
            nation_raw = parts[1].strip()
            # see if it matches any of the teams
            match = False
            for k in name_to_code:
                if k in nation_raw.lower():
                    match = True
            
            if match:
                print(f"Line: {line.strip()}")
                print(f"Parts: {parts} (len: {len(parts)})")
                
if __name__ == '__main__':
    main()
