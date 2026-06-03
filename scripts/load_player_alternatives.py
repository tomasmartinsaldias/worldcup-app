#!/usr/bin/env python3
"""Load alternative player name variants from the player similarity CSV
and store them in the `scraped_unresolved_players` table.

- Uses only `short_name` and `long_name` columns.
- Normalizes names (lowercase, strip accents, remove punctuation).
- Matches using difflib.SequenceMatcher with a cutoff of 0.85.
- Populates `alternative_names` (JSON list) column.
- If exactly one variant passes the threshold, the row is auto‑resolved
  by setting `resolved` = 1 and copying the variant into `player_name`.
- Generates a CSV report `data/unresolved_after_alternatives.csv` for manual review.
"""
import csv
import json
import os
import sqlite3
import difflib
import unicodedata

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "worldcup_combined.db")
CSV_PATH = os.path.join(BASE_DIR, "data", "player_similarity", "FC26_20250921.csv")
REPORT_PATH = os.path.join(BASE_DIR, "data", "unresolved_after_alternatives.csv")

SIMILARITY_THRESHOLD = 0.85


def normalize(name: str) -> str:
    """Lower‑case, strip accents and non‑alphanumeric characters."""
    name = name.lower()
    # Strip accents
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    # Remove punctuation and spaces for a simple token
    name = "".join(ch for ch in name if ch.isalnum())
    return name


def load_csv_lookup() -> dict:
    """Return a mapping of normalized short_name -> set of long_name variants."""
    lookup = {}
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            short = row.get("short_name", "").strip()
            long = row.get("long_name", "").strip()
            if not short or not long:
                continue
            key = normalize(short)
            lookup.setdefault(key, set()).add(long)
    return lookup


def main():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return
    if not os.path.exists(CSV_PATH):
        print(f"CSV not found at {CSV_PATH}")
        return

    lookup = load_csv_lookup()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Ensure the new column exists (in case the migration script hasn't run yet)
    cur.execute("PRAGMA table_info(scraped_unresolved_players);")
    cols = [c[1] for c in cur.fetchall()]
    if "alternative_names" not in cols:
        cur.execute("ALTER TABLE scraped_unresolved_players ADD COLUMN alternative_names TEXT;")
        print("Added missing column alternative_names.")

    # Fetch unresolved rows
    cur.execute("SELECT rowid, player_id, player_name FROM scraped_unresolved_players WHERE resolved = 0;")
    rows = cur.fetchall()

    report_rows = []
    for rowid, pid, name in rows:
        normalized = normalize(name)
        # Find candidate keys with sufficient similarity
        candidates = []
        for short_key, long_set in lookup.items():
            similarity = difflib.SequenceMatcher(None, normalized, short_key).ratio()
            if similarity >= SIMILARITY_THRESHOLD:
                candidates.extend(list(long_set))
        # Deduplicate
        candidates = list(set(candidates))
        alt_json = json.dumps(candidates, ensure_ascii=False) if candidates else None
        # Update the alternative_names column
        cur.execute(
            "UPDATE scraped_unresolved_players SET alternative_names = ? WHERE rowid = ?;",
            (alt_json, rowid),
        )
        resolved_name = None
        if len(candidates) == 1:
            resolved_name = candidates[0]
            cur.execute(
                "UPDATE scraped_unresolved_players SET player_name = ?, resolved = 1 WHERE rowid = ?;",
                (resolved_name, rowid),
            )
        report_rows.append({
            "player_id": pid,
            "original_name": name,
            "alternative_names": alt_json or "",
            "resolved_name": resolved_name or "",
        })

    conn.commit()
    conn.close()

    # Write CSV report
    with open(REPORT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["player_id", "original_name", "alternative_names", "resolved_name"])
        writer.writeheader()
        writer.writerows(report_rows)
    print(f"Report written to {REPORT_PATH}")

if __name__ == "__main__":
    main()
