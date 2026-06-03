import sqlite3

def main():
    conn = sqlite3.connect('data/worldcup_combined.db')
    c = conn.cursor()
    
    unresolved = [
        'Matej Kovar', 'Che Adams', 'Sergino Dest', 'Marten de Roon', 'Guus Til',
        'Jeremy Doku', 'Nico Williams', 'Erling Haaland', 'Rafael Leao', 'Khusanov Abdukodir',
        'Nico O\'Reilly', 'Josko Gvardiol', 'Luka Modric', 'Mateo Kovacic', 'Mario Pasalic',
        'Nikola Vlasic', 'Ivan Perisic', 'Iñaki Williams'
    ]
    
    for name in unresolved:
        # Check if there is any query containing name parts
        parts = name.split()
        if not parts: continue
        query = f"%{parts[-1]}%"
        c.execute("SELECT query FROM cache_transfermarkt WHERE query LIKE ?", (query,))
        matches = c.fetchall()
        out = f"Name: {name} | Matches for last name {parts[-1]}: {[m[0] for m in matches[:5]]}"
        print(out.encode('ascii', 'backslashreplace').decode('ascii'))

if __name__ == '__main__':
    main()
