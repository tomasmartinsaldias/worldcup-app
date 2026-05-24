import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')


base_dir = "c:/Users/User/Downloads/app_mundial/worldcup-app"
db_path = os.path.join(base_dir, "data", "worldcup_combined.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check some Turkish/Iranian players
players_to_check = ['Altay Bay%', 'Merih Demiral%', 'Kenan Y%ld%z%', 'Eren Elm%', 'irfan Can Kahveci%']
for p_pattern in players_to_check:
    cursor.execute("""
        SELECT player_name, market_value_eur, assists_recent, minutes_recent, efficiency_score
        FROM scraped_wc2026_probable_squads
        WHERE player_name LIKE ?;
    """, (p_pattern,))
    rows = cursor.fetchall()
    print(f"Pattern: {p_pattern}")
    for r in rows:
        print(f"  Found: {r}")

conn.close()
