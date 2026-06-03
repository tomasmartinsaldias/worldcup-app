#!/usr/bin/env python3
"""
Lee el CSV `data/unresolved_after_alternatives.csv` y, para cada fila que tenga
un `resolved_name` no vacío, actualiza la tabla `scraped_unresolved_players`:
- `player_name` <- resolved_name
- `resolved`   <- 1
- También guarda `alternative_names` tal como aparecen en el CSV.
Este script complementa `load_player_alternatives.py` cuando queremos forzar
resoluciones manuales.
"""
import csv, json, os, sqlite3

BASE_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
DB_PATH = os.path.join(BASE_DIR, "data", "worldcup_combined.db")
CSV_PATH = os.path.join(BASE_DIR, "data", "unresolved_after_alternatives.csv")

def main():
    if not os.path.exists(DB_PATH) or not os.path.exists(CSV_PATH):
        print("⚠️ DB o CSV no encontrada")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        updated = 0
        for row in reader:
            pid = row["player_id"].strip()
            resolved_name = row.get("resolved_name", "").strip()
            alt_names = row.get("alternative_names", "").strip()
            # Normalizamos el ID a entero para buscar la fila
            try:
                pid_int = int(pid)
            except ValueError:
                continue
            # Actualizamos alternative_names siempre (puede ser NULL)
            cur.execute(
                "UPDATE scraped_unresolved_players SET alternative_names = ? WHERE player_id = ?",
                (alt_names if alt_names else None, pid_int),
            )
            if resolved_name:
                cur.execute(
                    "UPDATE scraped_unresolved_players SET player_name = ?, resolved = 1 WHERE player_id = ?",
                    (resolved_name, pid_int),
                )
                updated += 1
    conn.commit()
    conn.close()
    print(f"Aplicadas {updated} resoluciones manuales desde CSV.")

if __name__ == "__main__":
    main()
