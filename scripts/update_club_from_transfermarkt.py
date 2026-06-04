#!/usr/bin/env python3
"""
Actualiza la columna `club` de los jugadores sin club correcto consultando Transfermarkt.

Mejoras respecto a la versión anterior:
- Usa la columna `alternative_names` (si existe) para intentar varias variantes del nombre.
- Normaliza y elimina apóstrofes y caracteres especiales antes de la búsqueda.
- Parser HTML más robusto: extrae el club del primer resultado de la tabla de resultados.
- Registra en `transfermarkt_updates.log` cada intento y su resultado.
"""

import os
import re
import sqlite3
import unicodedata
import json
import time
import datetime
import urllib.parse
import http.client
from html.parser import HTMLParser

BASE_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
DB_PATH = os.path.join(BASE_DIR, "data", "worldcup_combined.db")
PLACEHOLDER = "Centro Juventud Antoniana"
LOG_FILE = os.path.join(BASE_DIR, "scripts", "logs", "transfermarkt_updates.log")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0 Safari/537.36"
}

# ----------------------------------------------------------------------
def normalize(txt: str) -> str:
    txt = txt.lower()
    txt = unicodedata.normalize("NFD", txt)
    txt = "".join(c for c in txt if unicodedata.category(c) != "Mn")
    return "".join(ch for ch in txt if ch.isalnum())

# ----------------------------------------------------------------------
class TMResultParser(HTMLParser):
    """Parsea la tabla de resultados de Transfermarkt.
    Busca el primer <tr> donde exista una columna con la clase
    'hauptlink' (nombre del jugador) y extrae el club del siguiente <td>
    que contiene la clase 'vereinprofil_tooltip'.
    """
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
            # Detectamos la celda del nombre (clase contiene 'hauptlink')
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
                # guardamos la url del jugador que corresponde a esta fila
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
def search_transfermarkt(name_variants):
    """Intenta buscar usando una lista de variantes de nombre.
    Devuelve (club, url) o (None, None) si no se encontró nada.
    """
    for variant in name_variants:
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
            # Si la petición falla, pasamos a la siguiente variante
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
    if not os.path.exists(DB_PATH):
        print("⚠️ DB no encontrada")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Seleccionamos filas sin club o con placeholder
    cur.execute(
        """SELECT rowid, player_name, club, alternative_names FROM scraped_unresolved_players
           WHERE club IS NULL OR club = ?""",
        (PLACEHOLDER,)
    )
    rows = cur.fetchall()
    if not rows:
        print("✅ No hay jugadores sin club correcto.")
        conn.close()
        return

    updated = 0
    for rowid, name, _, alt_names in rows:
        # Construimos una lista de variantes a probar
        variants = [name]
        if alt_names:
            # la columna se guarda como texto; asumimos lista separada por ';'
            for a in alt_names.split(";"):
                a = a.strip()
                if a:
                    variants.append(a)
        # Normalizamos las variantes para la búsqueda (elimina apóstrofes, etc.)
        variants = [re.sub(r"[\'\`\’]", "", v) for v in variants]
        club, url = search_transfermarkt(variants)
        if club:
            cur.execute(
                """UPDATE scraped_unresolved_players SET club = ?, resolved = 1 WHERE rowid = ?""",
                (club, rowid),
            )
            log_update(name, club, url, "updated")
            updated += 1
            time.sleep(1.2)  # respeto al sitio
        else:
            log_update(name, None, None, "not_found")

    conn.commit()
    conn.close()
    print(f"✔️ Actualizados {updated} registros desde Transfermarkt.")

if __name__ == "__main__":
    main()
