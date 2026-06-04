import json
import os

teams_file = r"c:\Users\user\Downloads\app_mundial\worldcup-app\data\data_frontend\teams.json"

teams_to_add = [
    # AL NASSR FIX
    {"team": "Al Nassr", "crest": "https://upload.wikimedia.org/wikipedia/en/b/b4/Al-Nassr_FC_logo.svg"}, 
    {"team": "Al Nassr", "crest": "https://a.espncdn.com/i/teamlogos/soccer/500/10008.png"}, # Fallback safe ESPN image
    
    # SAUDI
    {"team": "Al Hilal", "crest": "https://a.espncdn.com/i/teamlogos/soccer/500/10023.png"},
    {"team": "Al Ittihad", "crest": "https://a.espncdn.com/i/teamlogos/soccer/500/10006.png"},
    {"team": "Al Ahli", "crest": "https://a.espncdn.com/i/teamlogos/soccer/500/10020.png"},

    # ARGENTINA
    {"team": "Boca Juniors", "crest": "https://a.espncdn.com/i/teamlogos/soccer/500/14.png"},
    {"team": "River Plate", "crest": "https://a.espncdn.com/i/teamlogos/soccer/500/16.png"},
    {"team": "Racing Club", "crest": "https://a.espncdn.com/i/teamlogos/soccer/500/15.png"},
    {"team": "Independiente", "crest": "https://a.espncdn.com/i/teamlogos/soccer/500/12.png"},
    {"team": "San Lorenzo", "crest": "https://a.espncdn.com/i/teamlogos/soccer/500/17.png"},
    {"team": "Estudiantes", "crest": "https://a.espncdn.com/i/teamlogos/soccer/500/10.png"},
    {"team": "Rosario Central", "crest": "https://a.espncdn.com/i/teamlogos/soccer/500/22.png"},

    # MLS
    {"team": "Inter Miami CF", "crest": "https://a.espncdn.com/i/teamlogos/soccer/500/20250.png"},
    {"team": "LA Galaxy", "crest": "https://a.espncdn.com/i/teamlogos/soccer/500/188.png"},
    {"team": "Los Angeles FC", "crest": "https://a.espncdn.com/i/teamlogos/soccer/500/19088.png"},
    {"team": "Seattle Sounders FC", "crest": "https://a.espncdn.com/i/teamlogos/soccer/500/9726.png"},
    {"team": "Atlanta United FC", "crest": "https://a.espncdn.com/i/teamlogos/soccer/500/18241.png"},

    # ASIA
    {"team": "Urawa Red Diamonds", "crest": "https://a.espncdn.com/i/teamlogos/soccer/500/3141.png"},
    {"team": "Al Ain FC", "crest": "https://a.espncdn.com/i/teamlogos/soccer/500/10058.png"},
    {"team": "Jeonbuk Hyundai Motors", "crest": "https://a.espncdn.com/i/teamlogos/soccer/500/13444.png"},
    {"team": "Kashima Antlers", "crest": "https://a.espncdn.com/i/teamlogos/soccer/500/3133.png"},

    # PORTUGAL
    {"team": "Benfica", "crest": "https://crests.football-data.org/1903.png"},
    {"team": "FC Porto", "crest": "https://crests.football-data.org/503.png"},
    {"team": "Sporting CP", "crest": "https://crests.football-data.org/498.png"},

    # ENGLAND
    {"team": "Arsenal", "crest": "https://crests.football-data.org/57.png"},
    {"team": "Aston Villa", "crest": "https://crests.football-data.org/58.png"},
    {"team": "Chelsea", "crest": "https://crests.football-data.org/61.png"},
    {"team": "Everton", "crest": "https://crests.football-data.org/62.png"},
    {"team": "Liverpool", "crest": "https://crests.football-data.org/64.png"},
    {"team": "Manchester City", "crest": "https://crests.football-data.org/65.png"},
    {"team": "Manchester United", "crest": "https://crests.football-data.org/66.png"},
    {"team": "Newcastle United", "crest": "https://crests.football-data.org/67.png"},
    {"team": "Tottenham Hotspur", "crest": "https://crests.football-data.org/73.png"},
    {"team": "West Ham United", "crest": "https://crests.football-data.org/563.png"},
    {"team": "Leicester City", "crest": "https://crests.football-data.org/338.png"},

    # SPAIN
    {"team": "Athletic Bilbao", "crest": "https://crests.football-data.org/77.png"},
    {"team": "Atletico Madrid", "crest": "https://crests.football-data.org/78.png"},
    {"team": "Barcelona", "crest": "https://crests.football-data.org/81.png"},
    {"team": "Real Madrid", "crest": "https://crests.football-data.org/86.png"},
    {"team": "Real Betis", "crest": "https://crests.football-data.org/90.png"},
    {"team": "Real Sociedad", "crest": "https://crests.football-data.org/92.png"},
    {"team": "Villarreal", "crest": "https://crests.football-data.org/94.png"},
    {"team": "Valencia", "crest": "https://crests.football-data.org/95.png"},
    {"team": "Sevilla", "crest": "https://crests.football-data.org/559.png"},

    # ITALY
    {"team": "AC Milan", "crest": "https://crests.football-data.org/98.png"},
    {"team": "Fiorentina", "crest": "https://crests.football-data.org/99.png"},
    {"team": "Roma", "crest": "https://crests.football-data.org/100.png"},
    {"team": "Atalanta", "crest": "https://crests.football-data.org/102.png"},
    {"team": "Inter", "crest": "https://crests.football-data.org/108.png"},
    {"team": "Juventus", "crest": "https://crests.football-data.org/109.png"},
    {"team": "Lazio", "crest": "https://crests.football-data.org/110.png"},
    {"team": "Napoli", "crest": "https://crests.football-data.org/113.png"},

    # GERMANY
    {"team": "Bayer Leverkusen", "crest": "https://crests.football-data.org/3.png"},
    {"team": "Borussia Dortmund", "crest": "https://crests.football-data.org/4.png"},
    {"team": "Bayern Munich", "crest": "https://crests.football-data.org/5.png"},
    {"team": "VfB Stuttgart", "crest": "https://crests.football-data.org/16.png"},
    {"team": "Eintracht Frankfurt", "crest": "https://crests.football-data.org/19.png"},
    {"team": "RB Leipzig", "crest": "https://crests.football-data.org/721.png"},

    # FRANCE
    {"team": "Marseille", "crest": "https://crests.football-data.org/516.png"},
    {"team": "Lille", "crest": "https://crests.football-data.org/521.png"},
    {"team": "Lyon", "crest": "https://crests.football-data.org/523.png"},
    {"team": "Paris Saint-Germain", "crest": "https://crests.football-data.org/524.png"},
    {"team": "Monaco", "crest": "https://crests.football-data.org/548.png"}
]

def main():
    with open(teams_file, 'r', encoding='utf-8') as f:
        teams = json.load(f)

    teams_dict = {t["team"].lower(): t for t in teams}
    
    # Also index by some variations
    # Just standardizing
    for t in teams_to_add:
        name = t["team"]
        # specifically for Al Nassr, force overwrite the old one
        if name.lower() == "al nassr":
            teams_dict["al nassr"] = t
        elif name.lower() not in teams_dict:
            teams_dict[name.lower()] = t

    final_teams = list(teams_dict.values())
    final_teams.sort(key=lambda x: x["team"])

    with open(teams_file, 'w', encoding='utf-8') as f:
        json.dump(final_teams, f, indent=2, ensure_ascii=False)
        
    print(f"Total de equipos ahora: {len(final_teams)}")

if __name__ == "__main__":
    main()
