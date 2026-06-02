import sqlite3, pathlib, sys

db_path = pathlib.Path(r'c:/Users/Franc/OneDrive/Documentos/ThinkPad/Github/worldcup-app/data/recommender_data/convocados.db')
if not db_path.exists():
    print('DB not found at', db_path)
    sys.exit(1)
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()
# Show all distinct countries
cur.execute('SELECT DISTINCT pais FROM convocados')
print('Countries:', cur.fetchall())
# Show players from France
cur.execute('SELECT jugador, pais FROM convocados WHERE pais = ?', ('Francia',))
rows = cur.fetchall()
print('Players from Francia:', rows)
# Search for Mbappé (different encodings)
cur.execute("SELECT jugador, pais FROM convocados WHERE jugador LIKE ?", ('%Mbapp%',))
print('Mbapp search:', cur.fetchall())
cur.close()
conn.close()
