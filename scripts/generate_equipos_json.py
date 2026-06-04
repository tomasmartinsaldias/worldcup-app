import json
import sqlite3
from pathlib import Path

def main():
    # Resolve repository root (two levels up from this script)
    base_dir = Path(__file__).resolve().parents[1]
    db_path = base_dir / "data" / "recommender_data" / "convocados.db"
    if not db_path.is_file():
        raise FileNotFoundError(f"Database not found at {db_path}")

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    # Find all tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]

    equipos_set = set()
    for table in tables:
        # Get column info
        cur.execute(f"PRAGMA table_info({table})")
        columns = [(col[1], col[2]) for col in cur.fetchall()]  # (name, type)
        # Look for column named 'equipo' (case‑insensitive)
        equipo_cols = [name for name, _ in columns if name.lower() == "equipo"]
        for col in equipo_cols:
            try:
                cur.execute(f"SELECT DISTINCT {col} FROM {table} WHERE {col} IS NOT NULL")
                for (val,) in cur.fetchall():
                    if val:
                        equipos_set.add(str(val))
            except sqlite3.OperationalError:
                continue
    conn.close()

    # Build JSON list of distinct equipos
    equipos = sorted(equipos_set)
    output_path = base_dir / "data" / "data_frontend" / "convocados_equipos.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(equipos, f, ensure_ascii=False, indent=2)
    print(f"Generated {len(equipos)} distinct equipos -> {output_path}")

if __name__ == "__main__":
    main()
