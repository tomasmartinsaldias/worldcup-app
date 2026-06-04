#!/usr/bin/env python3
"""
Actualiza la columna `club` de `scraped_unresolved_players` usando la lista
de convocados que está en 'Lista de Convocados.md'.

- Normaliza nombres (lower‑case, sin acentos) para coincidir con la tabla.
- Si el club actual está vacío o es el placeholder "Centro Juventud Antoniana",
  lo sustituye por el club encontrado en la lista.
- Cuando hay una única coincidencia con similitud >= 0.85, marca `resolved = 1`.
"""

import os
import re
import sqlite3
import unicodedata
import difflib

BASE_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
DB_PATH = os.path.join(BASE_DIR, "data", "worldcup_combined.db")
MD_PATH = os.path.join(BASE_DIR, "Lista de Convocados.md")
PLACEHOLDER_CLUB = "Centro Juventud Antoniana"
SIMILARITY_THRESHOLD = 0.85


def normalize(txt: str) -> str:
    txt = txt.lower()
    txt = unicodedata.normalize("NFD", txt)
    txt = "".join(c for c in txt if unicodedata.category(c) != "Mn")
    return "".join(ch for ch in txt if ch.isalnum())


def parse_convocados(md_path: str) -> dict:
    """Devuelve un dict {norm_name: (display_name, club)}"""
    pattern = re.compile(r"(?P<name>[\w\s\.\-áéíóúÁÉÍÓÚñÑ]+)\s*\(\s*(?P<club>[^,]+),\s*[A-Z]{3}\s*\)")
    result = {}
    with open(md_path, encoding="utf-8") as f:
        for line in f:
            for m in pattern.finditer(line):
                name = m.group("name").strip()
                club = m.group("club").strip()
                result[normalize(name)] = (name, club)
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
    updated = 0
    for rowid, pid, name, club in rows:
        norm_name = normalize(name)
        # Busca la mejor coincidencia en la lista de convocados
        best_match = None
        best_score = 0.0
        for conv_norm, (disp_name, conv_club) in convocados.items():
            score = difflib.SequenceMatcher(None, norm_name, conv_norm).ratio()
            if score > best_score:
                best_score = score
                best_match = (disp_name, conv_club)
        if best_score >= SIMILARITY_THRESHOLD and best_match:
            disp_name, conv_club = best_match
            # Actualiza club si está vacío o es placeholder
            if not club or club == PLACEHOLDER_CLUB:
                cur.execute(
                    "UPDATE scraped_unresolved_players SET club = ?, resolved = 1 WHERE rowid = ?",
                    (conv_club, rowid),
                )
                updated += 1
            # Opcional: armonizar nombre canónico
            cur.execute(
                "UPDATE scraped_unresolved_players SET player_name = ? WHERE rowid = ?",
                (disp_name, rowid),
            )
    conn.commit()
    conn.close()
    print(f"Actualizados {updated} registros con club correcto y marcados como resueltos.")

if __name__ == "__main__":
    main()
