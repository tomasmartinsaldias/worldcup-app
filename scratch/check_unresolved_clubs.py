import sqlite3

def main():
    conn = sqlite3.connect('data/worldcup_combined.db')
    c = conn.cursor()
    c.execute("""
        SELECT player_name, club, fifa_code 
        FROM scraped_unresolved_players 
        WHERE club LIKE '%Manchester City%' 
           OR club LIKE '%Athletic%' 
           OR club LIKE '%Milan%' 
           OR club LIKE '%Atalanta%' 
           OR club LIKE '%Torino%' 
           OR club LIKE '%PSV%'
    """)
    rows = c.fetchall()
    print(f"Total: {len(rows)}")
    for r in rows:
        print(r)

if __name__ == '__main__':
    main()
