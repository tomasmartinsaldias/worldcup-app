import json
from pathlib import Path

# Paths (relative to project root)
BASE_DIR = Path(__file__).resolve().parents[1]
TEAMS_PATH = BASE_DIR / "data" / "data_frontend" / "teams.json"
COUNTRIES_PATH = BASE_DIR / "data" / "data_frontend" / "countries.json"
OUTPUT_PATH = BASE_DIR / "data" / "data_frontend" / "unified_data.json"

def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main() -> None:
    teams = load_json(TEAMS_PATH)
    countries = load_json(COUNTRIES_PATH)

    unified = []
    # Teams -> "Equipo"
    for t in teams:
        unified.append({
            "type": "Equipo",
            "name": t.get("team"),
            "image_url": t.get("crest"),
            "league_country": t.get("league_country")
        })
    # Countries -> "Selección nacional"
    for c in countries:
        unified.append({
            "type": "Selección nacional",
            "name": c.get("country"),
            "image_url": c.get("flag_url"),
            "league_country": None
        })

    # Write pretty JSON
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(unified, f, ensure_ascii=False, indent=2)
    print(f"Unified data written to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
