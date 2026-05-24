import sqlite3

def main():
    conn = sqlite3.connect("data/worldcup_combined.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Total tables: {len(tables)}")
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            print(f"  - {table}: {count} rows")
        except Exception as e:
            print(f"  - {table}: Error ({e})")
    conn.close()

if __name__ == "__main__":
    main()
