import json
import pathlib

# Paths
project_root = pathlib.Path(__file__).parents[1]
json_path = project_root / "frontend" / "data" / "players_photos.json"

# Load and reformat
with json_path.open('r', encoding='utf-8') as f:
    data = json.load(f)

# Write formatted JSON back
with json_path.open('w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Formatted {json_path} with indent=2")
