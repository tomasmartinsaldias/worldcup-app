import sqlite3

def main():
    conn = sqlite3.connect("data/worldcup_combined.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM cache_transfermarkt;")
    print("Total rows:", c.fetchone()[0])
    c.execute("SELECT query FROM cache_transfermarkt LIMIT 10;")
    print("Examples:")
    for row in c.fetchall():
        print(" ", row[0])
    conn.close()

if __name__ == "__main__":
    main()
