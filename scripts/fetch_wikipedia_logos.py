import json
import os
import urllib.request
import urllib.parse
import time

def fetch_logos():
    print("Loading wc2026_data.json...")
    with open('data/wc2026_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract unique clubs
    clubs = set()
    for team in data['teams'].values():
        for player in team.get('squad', []):
            club = player.get('club')
            if club and club != 'Agente Libre':
                clubs.add(club.strip())
                
    clubs = list(clubs)
    print(f"Found {len(clubs)} unique clubs.")
    
    logos = {}
    
    # Process in batches of 50
    batch_size = 50
    for i in range(0, len(clubs), batch_size):
        batch = clubs[i:i+batch_size]
        titles = "|".join([urllib.parse.quote(c) for c in batch])
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&pithumbsize=200&redirects=1&titles={titles}"
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'WorldCupApp/1.0 (Contact: demo@example.com)'})
            resp = urllib.request.urlopen(req).read()
            res_json = json.loads(resp)
            
            pages = res_json.get('query', {}).get('pages', {})
            normalized = {n['to']: n['from'] for n in res_json.get('query', {}).get('normalized', [])}
            redirects = {r['to']: r['from'] for r in res_json.get('query', {}).get('redirects', [])}
            
            for page_id, page_info in pages.items():
                title = page_info.get('title')
                thumbnail = page_info.get('thumbnail')
                if title and thumbnail:
                    # Trace back the title through redirects and normalized
                    original = title
                    if title in redirects:
                        original = redirects[title]
                    if original in normalized:
                        original = normalized[original]
                        
                    # Store exact title match, original requested name, and lowercased
                    logos[title] = thumbnail['source']
                    logos[title.lower()] = thumbnail['source']
                    logos[original] = thumbnail['source']
                    logos[original.lower()] = thumbnail['source']
            
            print(f"Processed batch {i//batch_size + 1}")
            time.sleep(0.1) # Respect API limits
        except Exception as e:
            print(f"Error on batch {i//batch_size + 1}: {e}")

    # For mapping purposes, let's also try to save the original club name by lowercasing it
    # We will just save a huge dictionary that frontend can query.
    out_path = os.path.join('frontend', 'data', 'club_logos.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(logos, f, ensure_ascii=False, indent=2)
        
    print(f"Saved {len(logos)} logo mappings to {out_path}.")

if __name__ == '__main__':
    fetch_logos()
