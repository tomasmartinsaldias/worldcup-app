#!/usr/bin/env python3
import sqlite3, os, json
BASE = r"c:/Users/tomas/Desktop/proyectos/worldcup-app"
DB = os.path.join(BASE, "data", "worldcup_combined.db")
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT player_id, player_name, club FROM scraped_unresolved_players WHERE player_name LIKE '%Gonzalez%'")
rows = cur.fetchall()
print(json.dumps(rows, ensure_ascii=False, indent=2))
conn.close()
