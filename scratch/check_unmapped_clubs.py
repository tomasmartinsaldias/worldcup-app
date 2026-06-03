import sqlite3

def main():
    conn = sqlite3.connect("data/worldcup_combined.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fifa_code, player_name, club 
        FROM scraped_wc2026_probable_squads 
        WHERE club IS NULL OR club = '' OR club IN ('Desconocido', 'Agente Libre', 'sin equipo', 'Sin equipo')
        ORDER BY fifa_code, player_name;
    """)
    rows = cursor.fetchall()
    
    with open("scratch/unmapped_clubs_report.txt", "w", encoding="utf-8") as f:
        f.write(f"Total de jugadores sin equipo mapeado en worldcup_combined.db: {len(rows)}\n\n")
        for row in rows:
            f.write(f"  [{row[0]}] {row[1]} -> {row[2]}\n")
            
    print("Reporte escrito en scratch/unmapped_clubs_report.txt")
    conn.close()

if __name__ == "__main__":
    main()
