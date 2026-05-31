import sqlite3

def main():
    conn = sqlite3.connect("data/worldcup_combined.db")
    cur = conn.cursor()
    
    print("--- 1. Market Values in scraped_team_metrics ---")
    cur.execute("SELECT fifa_code, market_value_eur FROM scraped_team_metrics WHERE fifa_code IN ('BIH', 'CAN', 'TUR', 'USA');")
    for row in cur.fetchall():
        print(row)
        
    print("\n--- 2. Team Metrics Sample (recent_xg_avg, recent_possession_avg) ---")
    cur.execute("SELECT fifa_code, recent_xg_avg, recent_possession_avg FROM scraped_team_metrics LIMIT 5;")
    for row in cur.fetchall():
        print(row)
        
    print("\n--- 3. Player Age and Market Value Sample ---")
    cur.execute("SELECT player_name, age, market_value_eur FROM scraped_wc2026_probable_squads LIMIT 5;")
    for row in cur.fetchall():
        print(row)
        
    conn.close()

if __name__ == '__main__':
    main()
