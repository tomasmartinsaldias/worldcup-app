import sqlite3
import json

def check_cache_json(query, fifa_code):
    conn = sqlite3.connect('data/worldcup_combined.db')
    c = conn.cursor()
    c.execute("SELECT response_json FROM cache_transfermarkt WHERE query = ?", (query,))
    row = c.fetchone()
    if not row:
        print(f"No entry found for query: {query}")
        return
    try:
        data = json.loads(row[0])
        print(f"--- QUERY: {query} ---")
        for res in data.get('results', []):
            print(f"Name: {res.get('name')}")
            print(f"Age: {res.get('age')}")
            print(f"Nationalities: {res.get('nationalities')}")
            print(f"Club: {res.get('club', {}).get('name')}")
            
            # Simulate matching logic:
            allowed_nats = ['england'] if fifa_code == 'ENG' else ['norway'] if fifa_code == 'NOR' else []
            cand_nats = [n.lower() for n in res.get('nationalities', [])]
            nat_match = False
            for nat in cand_nats:
                for ok_nat in allowed_nats:
                    if ok_nat in nat or nat in ok_nat:
                        nat_match = True
                        break
            print(f"Matches nationality? {nat_match}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    check_cache_json("Kim Min-jae", "KOR")

if __name__ == '__main__':
    main()
