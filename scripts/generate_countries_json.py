import os, json, sqlite3

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, 'data', 'worldcup_combined.db')
OUTPUT_PATH = os.path.join(BASE_DIR, 'data', 'countries.json')

def main():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f'Database not found at {DB_PATH}')
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT team_name, flag_url FROM wc2026_teams WHERE flag_url IS NOT NULL")
    rows = cur.fetchall()
    data = [{"country": name, "flag_url": url} for name, url in rows]
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'Generated {len(data)} entries to {OUTPUT_PATH}')
    conn.close()

if __name__ == '__main__':
    main()
