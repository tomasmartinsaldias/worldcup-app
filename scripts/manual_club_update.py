#!/usr/bin/env python3
"""
Actualiza manualmente los clubes de jugadores que siguen sin resolverse
(Nico Williams y Nicolás González) usando los IDs conocidos en el CSV.
"""
import os, sqlite3

BASE_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
DB_PATH = os.path.join(BASE_DIR, "data", "worldcup_combined.db")

# Mapeo de player_id -> club
UPDATES = {
    35: "Athletic Club",          # Nico Williams
    46: "Atlético de Madrid",    # Nicolás González
}

if not os.path.exists(DB_PATH):
    print("⚠️ DB no encontrada")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

updated = 0
for pid, club in UPDATES.items():
    cur.execute("UPDATE scraped_unresolved_players SET club = ?, resolved = 1 WHERE player_id = ?", (club, pid))
    if cur.rowcount:
        updated += cur.rowcount
        print(f"player_id {pid} actualizado a club '{club}'.")

conn.commit()
conn.close()
print(f"✔️ Total de actualizaciones: {updated}")
