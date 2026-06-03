import json
import os

teams_file = r"c:\Users\user\Downloads\app_mundial\worldcup-app\data\data_frontend\teams.json"

new_teams = [
    {
        "team": "Boca Juniors",
        "crest": "https://upload.wikimedia.org/wikipedia/commons/e/e3/Boca_Juniors_logo18.svg"
    },
    {
        "team": "River Plate",
        "crest": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Logo_River_Plate_2022.png"
    },
    {
        "team": "Al Nassr",
        "crest": "https://upload.wikimedia.org/wikipedia/en/b/b4/Al-Nassr_FC_logo.svg"
    },
    {
        "team": "Flamengo",
        "crest": "https://upload.wikimedia.org/wikipedia/commons/2/2e/Flamengo_braz_logo.svg"
    },
    {
        "team": "Palmeiras",
        "crest": "https://upload.wikimedia.org/wikipedia/commons/1/10/Palmeiras_logo.svg"
    },
    {
        "team": "Peñarol",
        "crest": "https://upload.wikimedia.org/wikipedia/commons/3/30/Escudo_del_Club_Atl%C3%A9tico_Pe%C3%B1arol.svg"
    },
    {
        "team": "Independiente del Valle",
        "crest": "https://upload.wikimedia.org/wikipedia/commons/f/fb/Independientedelvalle2022.png"
    },
    {
        "team": "Al Hilal",
        "crest": "https://upload.wikimedia.org/wikipedia/en/2/27/Al_Hilal_SFC_Logo.svg"
    },
    {
        "team": "Inter Miami CF",
        "crest": "https://upload.wikimedia.org/wikipedia/en/e/e1/Inter_Miami_CF_logo.svg"
    },
    {
        "team": "LA Galaxy",
        "crest": "https://upload.wikimedia.org/wikipedia/commons/0/07/Los_Angeles_Galaxy_logo_%282024%29.svg"
    },
    {
        "team": "Bayer 04 Leverkusen",
        "crest": "https://upload.wikimedia.org/wikipedia/en/5/59/Bayer_04_Leverkusen_logo.svg"
    },
    {
        "team": "Sporting CP",
        "crest": "https://upload.wikimedia.org/wikipedia/en/3/3e/Sporting_Clube_de_Portugal_logo.svg"
    },
    {
        "team": "Galatasaray",
        "crest": "https://upload.wikimedia.org/wikipedia/commons/3/37/Galatasaray_Star_Logo.svg"
    }
]

def main():
    if not os.path.exists(teams_file):
        print(f"Error: {teams_file} no encontrado.")
        return

    with open(teams_file, 'r', encoding='utf-8') as f:
        teams = json.load(f)

    # Convert to dictionary by team name to avoid duplicates
    teams_dict = {t["team"]: t for t in teams}

    # Add or update new teams
    for t in new_teams:
        teams_dict[t["team"]] = t

    # Convert back to list and sort alphabetically
    final_teams = list(teams_dict.values())
    final_teams.sort(key=lambda x: x["team"])

    # Write back
    with open(teams_file, 'w', encoding='utf-8') as f:
        json.dump(final_teams, f, indent=2, ensure_ascii=False)

    print(f"Éxito: Se agregaron/actualizaron {len(new_teams)} equipos.")
    print(f"Total de equipos ahora en teams.json: {len(final_teams)}")

if __name__ == "__main__":
    main()
