import sqlite3
import json

def main():
    conn = sqlite3.connect('data/worldcup_combined.db')
    c = conn.cursor()
    c.execute("SELECT query, response_json FROM cache_transfermarkt WHERE query LIKE '%Haaland%'")
    rows = c.fetchall()
    print(f"Haaland queries in cache: {len(rows)}")
    for query, resp in rows:
        print(f"Query: {query}")
        try:
            data = json.loads(resp)
            print(f"Results count: {len(data.get('results', [])) if data else 0}")
            for r in data.get('results', []):
                print(f"  Name: {r.get('name')}, Age: {r.get('age')}, Nationalities: {r.get('nationalities')}, Club: {r.get('club', {}).get('name')}")
        except Exception as e:
            print(f"Error parsing json: {e}")

if __name__ == '__main__':
    main()
