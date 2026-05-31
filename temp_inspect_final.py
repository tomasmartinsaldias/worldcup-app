import sqlite3

def main():
    conn = sqlite3.connect("data/worldcup_combined.db")
    cur = conn.cursor()
    
    print("--- 1. Market Values ---")
    cur.execute("SELECT fifa_code, market_value_eur, recent_xg_avg, recent_possession_avg FROM scraped_team_metrics WHERE fifa_code IN ('BIH', 'CAN', 'TUR', 'USA');")
    for row in cur.fetchall():
        print(row)
        
    print("\n--- 2. Team Metrics Sample ---")
    cur.execute("SELECT fifa_code, recent_xg_avg, recent_possession_avg FROM scraped_team_metrics LIMIT 5;")
    for row in cur.fetchall():
        print(row)
        
    print("\n--- 3. Player Age and Market Value Sample (unconfirmed team: Turkey) ---")
    cur.execute("SELECT player_name, age, market_value_eur FROM scraped_wc2026_probable_squads WHERE fifa_code = 'TUR' LIMIT 5;")
    for row in cur.fetchall():
        print(row[0].encode('ascii', 'ignore').decode(), row[1], row[2])

    print("\n--- 4. Player Age Sample (confirmed team: Canada) ---")
    cur.execute("SELECT player_name, age, market_value_eur FROM scraped_wc2026_probable_squads WHERE fifa_code = 'CAN' LIMIT 5;")
    for row in cur.fetchall():
        print(row[0].encode('ascii', 'ignore').decode(), row[1], row[2])
        
    conn.close()

if __name__ == '__main__':
    main()
