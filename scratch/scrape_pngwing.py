import json
import os
import urllib.request
import urllib.parse
import re
import time
import ssl

teams_file = r"c:\Users\user\Downloads\app_mundial\worldcup-app\data\data_frontend\teams.json"

def fetch_pngwing_url(team_name):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    query = urllib.parse.quote(f"{team_name} logo escudo")
    url = f"https://www.pngwing.com/es/search?q={query}"
    
    req = urllib.request.Request(
        url, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept-Language': 'es-ES,es;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
    )
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            # Buscamos el primer <img class="lazy lst_img" data-src="https://w7.pngwing.com/pngs/...">
            match = re.search(r'data-src="(https://w7\.pngwing\.com/pngs/[^"]+)"', html)
            if match:
                return match.group(1)
            else:
                # Intento de fallback si cambió el formato
                match2 = re.search(r'src="(https://w7\.pngwing\.com/pngs/[^"]+)"', html)
                if match2:
                    return match2.group(1)
    except Exception as e:
        print(f"  [Error] al extraer {team_name}: {e}")
        
    return None

def main():
    if not os.path.exists(teams_file):
        print("Error: teams.json not found")
        return

    with open(teams_file, 'r', encoding='utf-8') as f:
        teams = json.load(f)

    print(f"Total equipos a procesar: {len(teams)}")
    
    updated_count = 0
    failed_count = 0
    
    # Process all teams
    for i, t in enumerate(teams):
        team_name = t["team"]
        print(f"[{i+1}/{len(teams)}] Buscando en PNGWing: {team_name}...")
        
        img_url = fetch_pngwing_url(team_name)
        if img_url:
            t["crest"] = img_url
            updated_count += 1
            print(f"  -> OK: {img_url}")
        else:
            failed_count += 1
            print(f"  -> NO SE ENCONTRÓ IMAGEN")
            
        time.sleep(0.5)  # Pause to avoid rate limits

    with open(teams_file, 'w', encoding='utf-8') as f:
        json.dump(teams, f, indent=2, ensure_ascii=False)

    print(f"\nProceso completado. Equipos actualizados: {updated_count}. Fallos: {failed_count}.")

if __name__ == "__main__":
    main()
