import sqlite3

def main():
    conn = sqlite3.connect("data/worldcup_combined.db")
    cursor = conn.cursor()
    cursor.execute("SELECT club, COUNT(*) FROM scraped_wc2026_probable_squads GROUP BY club ORDER BY club;")
    rows = cursor.fetchall()
    
    with open("scratch/clubs_list.txt", "w", encoding="utf-8") as f:
        f.write("Clubes unificados con sus frecuencias:\n")
        for row in rows:
            f.write(f"{row[0]} -> {row[1]}\n")
    
    print("Escrito en scratch/clubs_list.txt")
    conn.close()

if __name__ == "__main__":
    main()
