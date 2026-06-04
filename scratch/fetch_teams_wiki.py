import json
import os
import urllib.request
import urllib.parse
import ssl

teams_file = r"c:\Users\user\Downloads\app_mundial\worldcup-app\data\data_frontend\teams.json"

# List of teams to ensure exist. Format: {"team": "Display Name", "wiki": "Wikipedia_Article_Title_EN"}
# If "wiki" is missing, we use "team" as the search title.
teams_to_add = [
    # AL NASSR FIX
    {"team": "Al Nassr", "wiki": "Al Nassr FC"},
    {"team": "Al Hilal", "wiki": "Al Hilal SFC"},
    {"team": "Al Ittihad", "wiki": "Al-Ittihad Club (Jeddah)"},
    {"team": "Al Ahli", "wiki": "Al Ahli Saudi FC"},
    {"team": "Al Shabab", "wiki": "Al Shabab FC (Riyadh)"},

    # ARGENTINA
    {"team": "Boca Juniors", "wiki": "Boca Juniors"},
    {"team": "River Plate", "wiki": "Club Atlético River Plate"},
    {"team": "Racing Club", "wiki": "Racing Club de Avellaneda"},
    {"team": "Independiente", "wiki": "Club Atlético Independiente"},
    {"team": "San Lorenzo", "wiki": "San Lorenzo de Almagro"},
    {"team": "Estudiantes", "wiki": "Estudiantes de La Plata"},
    {"team": "Rosario Central", "wiki": "Club Atlético Rosario Central"},
    {"team": "Newell's Old Boys", "wiki": "Newell's Old Boys"},
    {"team": "Talleres", "wiki": "Club Atlético Talleres"},
    {"team": "Vélez Sarsfield", "wiki": "Club Atlético Vélez Sarsfield"},

    # MLS
    {"team": "Inter Miami CF", "wiki": "Inter Miami CF"},
    {"team": "LA Galaxy", "wiki": "LA Galaxy"},
    {"team": "Los Angeles FC", "wiki": "Los Angeles FC"},
    {"team": "Seattle Sounders", "wiki": "Seattle Sounders FC"},
    {"team": "Atlanta United", "wiki": "Atlanta United FC"},
    {"team": "New York City FC", "wiki": "New York City FC"},

    # PORTUGAL
    {"team": "FC Porto", "wiki": "FC Porto"},
    {"team": "Benfica", "wiki": "S.L. Benfica"},
    {"team": "Sporting CP", "wiki": "Sporting CP"},
    {"team": "SC Braga", "wiki": "S.C. Braga"},

    # ASIA
    {"team": "Urawa Red Diamonds", "wiki": "Urawa Red Diamonds"},
    {"team": "Al Ain FC", "wiki": "Al Ain FC"},
    {"team": "Jeonbuk Hyundai Motors", "wiki": "Jeonbuk Hyundai Motors"},
    {"team": "Kashima Antlers", "wiki": "Kashima Antlers"},
    {"team": "Guangzhou FC", "wiki": "Guangzhou F.C."},
    {"team": "Al Sadd SC", "wiki": "Al Sadd SC"},

    # SPAIN (Major)
    {"team": "Real Madrid", "wiki": "Real Madrid CF"},
    {"team": "Barcelona", "wiki": "FC Barcelona"},
    {"team": "Atletico Madrid", "wiki": "Atlético Madrid"},
    {"team": "Sevilla", "wiki": "Sevilla FC"},
    {"team": "Valencia", "wiki": "Valencia CF"},
    {"team": "Athletic Bilbao", "wiki": "Athletic Bilbao"},
    {"team": "Real Sociedad", "wiki": "Real Sociedad"},
    {"team": "Villarreal", "wiki": "Villarreal CF"},
    {"team": "Real Betis", "wiki": "Real Betis"},

    # ENGLAND (Major)
    {"team": "Manchester United", "wiki": "Manchester United F.C."},
    {"team": "Manchester City", "wiki": "Manchester City F.C."},
    {"team": "Arsenal", "wiki": "Arsenal F.C."},
    {"team": "Chelsea", "wiki": "Chelsea F.C."},
    {"team": "Liverpool", "wiki": "Liverpool F.C."},
    {"team": "Tottenham Hotspur", "wiki": "Tottenham Hotspur F.C."},
    {"team": "Newcastle United", "wiki": "Newcastle United F.C."},
    {"team": "Aston Villa", "wiki": "Aston Villa F.C."},
    {"team": "Everton", "wiki": "Everton F.C."},
    {"team": "West Ham United", "wiki": "West Ham United F.C."},
    {"team": "Leicester City", "wiki": "Leicester City F.C."},

    # ITALY (Major)
    {"team": "Juventus", "wiki": "Juventus F.C."},
    {"team": "AC Milan", "wiki": "A.C. Milan"},
    {"team": "Inter", "wiki": "Inter Milan"},
    {"team": "Napoli", "wiki": "S.S.C. Napoli"},
    {"team": "Roma", "wiki": "A.S. Roma"},
    {"team": "Lazio", "wiki": "S.S. Lazio"},
    {"team": "Fiorentina", "wiki": "ACF Fiorentina"},
    {"team": "Atalanta", "wiki": "Atalanta B.C."},

    # GERMANY (Major)
    {"team": "Bayern Munich", "wiki": "FC Bayern Munich"},
    {"team": "Borussia Dortmund", "wiki": "Borussia Dortmund"},
    {"team": "RB Leipzig", "wiki": "RB Leipzig"},
    {"team": "Bayer 04 Leverkusen", "wiki": "Bayer 04 Leverkusen"},
    {"team": "VfB Stuttgart", "wiki": "VfB Stuttgart"},
    {"team": "Eintracht Frankfurt", "wiki": "Eintracht Frankfurt"},

    # FRANCE (Major)
    {"team": "Paris Saint-Germain", "wiki": "Paris Saint-Germain F.C."},
    {"team": "Marseille", "wiki": "Olympique de Marseille"},
    {"team": "Lyon", "wiki": "Olympique Lyonnais"},
    {"team": "Monaco", "wiki": "AS Monaco FC"},
    {"team": "Lille", "wiki": "Lille OSC"}
]

def fetch_wiki_image(title):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={urllib.parse.quote(title)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode())
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_info in pages.items():
                if "original" in page_info:
                    return page_info["original"]["source"]
    except Exception as e:
        print(f"Error fetching {title}: {e}")
    return None

def main():
    if not os.path.exists(teams_file):
        print(f"Error: {teams_file} no encontrado.")
        return

    with open(teams_file, 'r', encoding='utf-8') as f:
        teams = json.load(f)

    # dictionary mapping lowercase team name to actual object for easy lookup
    teams_dict = {t["team"].lower(): t for t in teams}

    added = 0
    updated = 0

    for t in teams_to_add:
        name = t["team"]
        wiki_title = t.get("wiki", name)
        
        # specific fix for Al Nassr to force update
        if name.lower() == "al nassr" or name.lower() not in teams_dict:
            print(f"Fetching image for {name}...")
            img_url = fetch_wiki_image(wiki_title)
            if img_url:
                if name.lower() in teams_dict:
                    teams_dict[name.lower()]["crest"] = img_url
                    updated += 1
                else:
                    teams_dict[name.lower()] = {"team": name, "crest": img_url}
                    added += 1
            else:
                print(f"  -> No image found for {name} ({wiki_title})")

    final_teams = list(teams_dict.values())
    final_teams.sort(key=lambda x: x["team"])

    with open(teams_file, 'w', encoding='utf-8') as f:
        json.dump(final_teams, f, indent=2, ensure_ascii=False)

    print(f"Proceso finalizado. {added} equipos nuevos añadidos. {updated} equipos actualizados.")
    print(f"Total de equipos en teams.json: {len(final_teams)}")

if __name__ == "__main__":
    main()
