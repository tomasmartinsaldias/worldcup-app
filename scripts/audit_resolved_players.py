#!/usr/bin/env python3
"""
Audita los registros marcados como resolved = 1.
Si el nombre coincide con la lista de convocados pero el club es distinto,
restablece resolved = 0 y vacía la columna club para que la posterior
actualización lo corrija.
"""
import os
import re
import sqlite3
import unicodedata

BASE_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
DB_PATH = os.path.join(BASE_DIR, "data", "worldcup_combined.db")
MD_PATH = os.path.join(BASE_DIR, "Lista de Convocados.md")
PLACEHOLDER = "Centro Juventud Antoniana"


def normalize(txt: str) -> str:
    txt = txt.lower()
    txt = unicodedata.normalize("NFD", txt)
    txt = "".join(c for c in txt if unicodedata.category(c) != "Mn")
    return "".join(ch for ch in txt if ch.isalnum())


def parse_convocados(md_path: str) -> dict:
    """Devuelve {norm_name: club} a partir del markdown."""
    pattern = re.compile(r"(?P<name>[\w\s\.\-áéíóúÁÉÍÓÚñÑ]+)\s*\(\s*(?P<club>[^,]+),\s*[A-Z]{3}\s*\)")
    result = {}
    with open(md_path, encoding="utf-8") as f:
        for line in f:
            for m in pattern.finditer(line):
                result[normalize(m.group("name"))] = m.group("club").strip()
    return result


def main():
    if not os.path.exists(DB_PATH) or not os.path.exists(MD_PATH):
        print("⚠️ Base de datos o lista de convocados no encontrada.")
        return
    convocados = parse_convocados(MD_PATH)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT rowid, player_name, club, resolved FROM scraped_unresolved_players")
    rows = cur.fetchall()
    reset_count = 0
    for rowid, name, club, resolved in rows:
        if resolved != 1:
            continue
        norm_name = normalize(name)
        if norm_name in convocados:
            correct_club = convocados[norm_name]
            if club != correct_club:
                cur.execute(
                    "UPDATE scraped_unresolved_players SET resolved = 0, club = NULL WHERE rowid = ?",
                    (rowid,)
                )
                reset_count += 1
    conn.commit()
    conn.close()
    print(f"Auditado. Se han reiniciado {reset_count} registros con datos incorrectos.")

if __name__ == "__main__":
    main()
