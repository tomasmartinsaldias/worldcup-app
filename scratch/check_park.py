import sqlite3
conn = sqlite3.connect('data/worldcup_combined.db')
c = conn.cursor()
c.execute("SELECT player_name, age, club, market_value_eur FROM scraped_wc2026_probable_squads WHERE player_name LIKE '%Davies%';")
for row in c.fetchall():
    print("Found in DB:", row)
