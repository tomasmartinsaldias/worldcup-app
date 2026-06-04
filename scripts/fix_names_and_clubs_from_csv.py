#!/usr/bin/env python3
"""
Actualiza los nombres de los jugadores a partir de `data/unresolved_after_alternatives.csv`
(y sus posibles variantes) y, usando Transfermarkt, rellena el club y marca
`resolved = 1`.

Pasos:
1. Lee cada fila del CSV.
2. Sobrescribe `player_name` con `original_name` (el nombre correcto).
3. Normaliza y crea una lista de variantes que incluye `original_name` y los
   valores de `alternative_names` (JSON lista).
4. Busca en Transfermarkt con esas variantes.
5. Si se encuentra un club, actualiza `club` y `resolved`.
6. Registra cada intento en `transfermarkt_updates.log`.
"""

import csv
import os
import sqlite3
import unicodedata
import urllib.parse
import http.client
import time
import datetime
import re
import json
from html.parser import HTMLParser

BASE_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
DB_PATH = os.path.join(BASE_DIR, "data", "worldcup_combined.db")
CSV_PATH = os.path.join(BASE_DIR, "data", "unresolved_after_alternatives.csv")
PLACEHOLDER = "Centro Juventud Antoniana"
LOG_FILE = os.path.join(BASE_DIR, "scripts", "logs", "transfermarkt_updates.log")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

# ----------------------------------------------------------------------
def normalize(txt: str) -> str:
    txt = txt.lower()
    txt = unicodedata.normalize("NFD", txt)
    txt = "".join(c for c in txt if unicodedata.category(c) != "Mn")
    return "".join(ch for ch in txt if ch.isalnum())

# ----------------------------------------------------------------------
class TMResultParser(HTMLParser):
    """Parse Transfermarkt search result table to get first club and URL."""
    def __init__(self):
        super().__init__()
        self.in_row = False
        self.in_name_cell = False
        self.in_club_cell = False
        self.found = False
        self.club = None
        self.url = None
        self._current_url = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.in_row = True
            self._current_url = None
        if self.in_row and tag == "td":
            for a, v in attrs:
                if a == "class" and "hauptlink" in v:
                    self.in_name_cell = True
        if self.in_name_cell and tag == "a":
            for a, v in attrs:
                if a == "href":
                    self._current_url = "https://www.transfermarkt.com" + v
        if self.in_row and tag == "td":
            for a, v in attrs:
                if a == "class" and "vereinprofil_tooltip" in v:
                    self.in_club_cell = True

    def handle_data(self, data):
        if self.in_club_cell and not self.found:
            club_candidate = data.strip()
            if club_candidate:
                self.club = club_candidate
                self.found = True
                self.url = self._current_url

    def handle_endtag(self, tag):
        if tag == "tr":
            self.in_row = False
            self.in_name_cell = False
            self.in_club_cell = False
            self._current_url = None
        if tag == "td":
            self.in_name_cell = False
            self.in_club_cell = False

# ----------------------------------------------------------------------
def search_transfermarkt(variants):
    for variant in variants:
        query = urllib.parse.quote_plus(variant)
        path = f"/schnellsuche/ergebnis/schnellsuche?query={query}"
        try:
            conn = http.client.HTTPSConnection("www.transfermarkt.com", timeout=15)
            conn.request("GET", path, headers=HEADERS)
            resp = conn.getresponse()
            if resp.status != 200:
                conn.close()
                continue
            html = resp.read().decode(errors="ignore")
            parser = TMResultParser()
            parser.feed(html)
            conn.close()
            if parser.found and parser.club:
                return parser.club, parser.url
        except Exception:
            continue
    return None, None

# ----------------------------------------------------------------------
def log_update(name, club, url, status):
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "player": name,
        "club": club,
        "url": url,
        "status": status,
    }
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# ----------------------------------------------------------------------
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
            original_name = row["original_name"].strip()
            alt_raw = row.get("alternative_names", "").strip()
            # Parse alternative_names JSON (it may be empty or nested)
            try:
                alt_list = json.loads(alt_raw) if alt_raw else []
                # Flatten one level if needed (e.g., [["a","b"]])
                if isinstance(alt_list, list) and len(alt_list) == 1 and isinstance(alt_list[0], list):
                    alt_list = alt_list[0]
                alt_list = [a for a in alt_list if isinstance(a, str)]
            except json.JSONDecodeError:
                alt_list = []

            # Update DB name to the correct original_name
            try:
                pid_int = int(pid)
            except ValueError:
                continue
            cur.execute(
                "UPDATE scraped_unresolved_players SET player_name = ?, alternative_names = ? WHERE player_id = ?",
                (original_name, json.dumps(alt_list, ensure_ascii=False) if alt_list else None, pid_int),
            )

            # Build search variants: original + alternatives
            variants = [original_name] + alt_list
            # Normalise variants for search (remove apostrophes, etc.)
            variants = [re.sub(r"[\'\`\’]", "", v) for v in variants]

            club, url = search_transfermarkt(variants)
            if club:
                cur.execute("SELECT rowid, player_name, club, alternative_names FROM scraped_unresolved_players")
                cur.execute(
                    "UPDATE scraped_unresolved_players SET club = ?, resolved = 1 WHERE player_id = ?",
                    (club, pid_int),
                )
                log_update(original_name, club, url, "updated")
                updated += 1
                time.sleep(1.2)
            else:
                log_update(original_name, None, None, "not_found")

    conn.commit()
    conn.close()
    print(f"Aplicadas {updated} actualizaciones desde CSV + Transfermarkt.")

if __name__ == "__main__":
    main()
