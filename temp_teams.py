import sqlite3
conn = sqlite3.connect('data/worldcup_combined.db')
c = conn.cursor()
c.execute("SELECT team_name, fifa_code FROM wc2026_teams;")
print(c.fetchall())
