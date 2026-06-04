#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stdin  = io.TextIOWrapper(sys.stdin.buffer,  encoding='utf-8', errors='replace')
"""
Revisión manual de jugadores unresolved contra la API de Transfermarkt.

Para cada jugador:
  - Simula el matching de populate_data.py (Jaccard >= 0.25 o seq >= 0.8)
  - Si va a fallar (no en caché o nombre no matchea), lo muestra para revisión manual
  - Guardás el response con la clave exacta del jugador → populate_data.py lo encuentra primero

Uso:
  python scripts/cache_unresolved_manual.py             (muestra todos los que fallarán)
  python scripts/cache_unresolved_manual.py --all       (muestra los 69, incluso los ya resueltos)
"""

import os
import sys
import json
import sqlite3
import unicodedata
import re
import urllib.parse
import requests

def display(text):
    """Elimina caracteres invisibles/no-imprimibles para la consola de Windows."""
    return re.sub(r'[\u2060\u200b\u200c\u200d\ufeff\u00ad]', '', str(text))

BASE_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
DB_PATH  = os.path.join(BASE_DIR, "data", "worldcup_combined.db")
CSV_PATH = os.path.join(BASE_DIR, "data", "unresolved_after_alternatives.csv")
API_BASE = "http://127.0.0.1:8000"

SHOW_ALL = "--all" in sys.argv

NATIONALITY_KEYWORDS = {
    'ARG': ['Argentina'], 'BRA': ['Brazil'], 'FRA': ['France'], 'ENG': ['England'],
    'ESP': ['Spain'], 'GER': ['Germany'], 'POR': ['Portugal'], 'URU': ['Uruguay'],
    'NED': ['Netherlands'], 'CRO': ['Croatia'], 'JPN': ['Japan'],
    'USA': ['United States', 'US'], 'MEX': ['Mexico'], 'MAR': ['Morocco'],
    'COL': ['Colombia'], 'BEL': ['Belgium'], 'NOR': ['Norway'], 'SEN': ['Senegal'],
    'EGY': ['Egypt'], 'SWE': ['Sweden'], 'KOR': ['Korea, South', 'South Korea', 'Korea'],
    'TUR': ['Turkey', 'Türkiye'], 'SUI': ['Switzerland'], 'CAN': ['Canada'],
    'ECU': ['Ecuador'], 'AUT': ['Austria'], 'ALG': ['Algeria'],
    'CIV': ["Cote d'Ivoire", "Ivory Coast", "Côte d'Ivoire"],
    'SCO': ['Scotland'], 'AUS': ['Australia'], 'GHA': ['Ghana'],
    'KSA': ['Saudi Arabia'], 'PAR': ['Paraguay'], 'CZE': ['Czech Republic', 'Czechia'],
    'COD': ['DR Congo', 'Congo, Democratic Republic'], 'BIH': ['Bosnia-Herzegovina', 'Bosnia'],
    'CPV': ['Cape Verde', 'Cabo Verde'], 'TUN': ['Tunisia'], 'IRQ': ['Iraq'],
    'RSA': ['South Africa'], 'UZB': ['Uzbekistan'], 'QAT': ['Qatar'],
    'NZL': ['New Zealand'], 'JOR': ['Jordan'], 'PAN': ['Panama'], 'HAI': ['Haiti'],
    'CUR': ['Curacao', 'Curaçao'], 'IRN': ['Iran'],
}

# ---------------------------------------------------------------------------
def normalize_name(text):
    if not isinstance(text, str): return ""
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join([c for c in text if "a" <= c <= "z" or c == " "])
    return " ".join(text.split())

def clean_for_search(name):
    name = unicodedata.normalize("NFD", name)
    name = "".join([c for c in name if not unicodedata.combining(c)])
    name = re.sub(r"[^a-zA-Z0-9\s\-]", "", name)
    return " ".join(name.split())

import difflib

def load_full_cache(cur):
    cur.execute("SELECT query, response_json FROM cache_transfermarkt")
    result = {}
    for q, r in cur.fetchall():
        try:
            data = json.loads(r)
            if data and data.get("results"):
                result[q] = data
        except Exception:
            pass
    return result

def will_match(name, fifa_code, full_cache, age=26):
    """Simula resolve_from_transfermarkt_cache con umbral 0.25.
    Devuelve True si populate_data.py lo resolverá automáticamente."""
    norm_p = normalize_name(name)
    tokens_p = set(norm_p.split())
    allowed_nats = [n.lower() for n in NATIONALITY_KEYWORDS.get(fifa_code, [])]

    # 1. Exact match por nombre
    candidate_data = full_cache.get(name)

    # 2. Fuzzy si no hay exact match
    if not candidate_data:
        best_score = -1.0
        for q_name, q_data in full_cache.items():
            norm_q   = normalize_name(q_name)
            tokens_q = set(norm_q.split())
            if not tokens_q: continue
            jacc = len(tokens_p & tokens_q) / len(tokens_p | tokens_q)
            seq  = difflib.SequenceMatcher(None, norm_p, norm_q).ratio()
            score = max(jacc, seq)
            if (jacc >= 0.5 or seq >= 0.8) and score > best_score:
                best_score = score
                candidate_data = q_data

    if not candidate_data:
        return False  # no en cache

    # 3. Intentar encontrar candidato válido
    for cand in candidate_data.get("results", []):
        cand_name = cand.get("name", "")
        cand_age  = cand.get("age")
        cand_nats = [n.lower() for n in cand.get("nationalities", [])]
        cand_mv   = cand.get("marketValue")

        nat_match = not cand_nats
        if not nat_match:
            for nat in cand_nats:
                for ok in allowed_nats:
                    if ok in nat or nat in ok:
                        nat_match = True; break
                if nat_match: break
        if not nat_match: continue

        if cand_age is not None and age != 26:
            if abs(age - cand_age) > 3: continue

        set1 = set(normalize_name(name).split())
        set2 = set(normalize_name(cand_name).split())
        if not set1 or not set2: continue
        jacc = len(set1 & set2) / len(set1 | set2)
        seq  = difflib.SequenceMatcher(None, normalize_name(name), normalize_name(cand_name)).ratio()
        if (jacc >= 0.25 or seq >= 0.8) and cand_mv is not None:
            return True  # se resolverá con MV

    return False  # en caché pero no matchea o MV nulo

def search_api(query):
    try:
        url = f"{API_BASE}/players/search/{urllib.parse.quote(query)}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data and data.get("results"):
                return data
    except Exception as e:
        print(f"  [Error API] {e}")
    return None

def save_to_cache(cur, conn, key, api_data):
    cur.execute(
        "INSERT OR REPLACE INTO cache_transfermarkt (query, response_json) VALUES (?, ?)",
        (key, json.dumps(api_data, ensure_ascii=False))
    )
    conn.commit()

def format_mv(mv):
    if mv is None: return "N/D"
    try:
        v = float(mv)
        if v >= 1_000_000:
            return f"€{v/1_000_000:.1f}M"
        elif v >= 1_000:
            return f"€{v/1_000:.0f}K"
        return f"€{v:.0f}"
    except:
        return str(mv)

# ---------------------------------------------------------------------------
def main():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: DB no encontrada: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # Fuente de verdad: scraped_unresolved_players en la DB
    full_cache = load_full_cache(cur)
    cur.execute("""
        SELECT player_name, fifa_code, COALESCE(age, 26)
        FROM scraped_unresolved_players
        ORDER BY player_id
    """)
    rows = cur.fetchall()

    players = []
    for name, fifa_code, age in rows:
        players.append({
            "name": name,
            "variants": [name],
            "fifa_code": fifa_code or "",
            "age": age or 26,
        })

    total   = len(players)
    saved   = 0
    skipped = 0
    auto_ok = 0

    # Pre-contar cuántos se saltan automáticamente
    will_fail = [p for p in players if not will_match(p["name"], p["fifa_code"], full_cache, p["age"])]

    print(f"\n{'='*60}")
    print(f"  Revisión manual — {total} unresolved en DB")
    print(f"  Se resolverán solos: {total - len(will_fail)} | Necesitan revisión: {len(will_fail)}")
    print("  Comandos: número=elegir | s=saltar | q=salir | b=buscar otro nombre")
    print(f"{'='*60}\n")

    shown = 0
    for player in players:
        name      = player["name"]
        variants  = player["variants"]
        fifa_code = player["fifa_code"]
        age       = player["age"]

        if not SHOW_ALL and will_match(name, fifa_code, full_cache, age):
            auto_ok += 1
            continue

        shown += 1
        print(f"\n[{shown}/{len(will_fail)}] {display(name)}")
        print(f"  Variantes: {', '.join(display(v) for v in variants)}")

        # Buscar con cada variante hasta obtener resultados
        api_data = None
        used_query = None
        for v in variants:
            clean_v = clean_for_search(v)
            print(f"  Buscando: '{clean_v}' ...", end=" ", flush=True)
            api_data = search_api(clean_v)
            if api_data:
                used_query = clean_v
                print(f"{len(api_data['results'])} resultados")
                break
            else:
                print("sin resultados")

        # Si no hubo resultados, ofrecer búsqueda manual
        if not api_data:
            print("  ⚠️  No se encontraron resultados con ninguna variante.")
            resp = input("  Escribí otro nombre para buscar (o Enter para saltar): ").strip()
            if resp:
                print(f"  Buscando: '{resp}' ...", end=" ", flush=True)
                api_data = search_api(resp)
                if api_data:
                    used_query = resp
                    print(f"{len(api_data['results'])} resultados")
                else:
                    print("sin resultados")

        if not api_data:
            print("  ➡  Saltado (sin resultados)")
            skipped += 1
            continue

        # Mostrar resultados
        results = api_data.get("results", [])[:10]  # máximo 10
        print()
        for i, cand in enumerate(results, 1):
            cand_name  = cand.get("name", "?")
            cand_age   = cand.get("age", "?")
            cand_nats  = ", ".join(cand.get("nationalities", [])) or "?"
            cand_club  = cand.get("club", {}).get("name", "Sin club") if cand.get("club") else "Sin club"
            cand_pos   = cand.get("position", "?")
            cand_mv    = format_mv(cand.get("marketValue"))
            print(f"  [{i}] {cand_name}  |  {cand_pos}  |  {cand_age} años  |  {cand_club}  |  {cand_nats}  |  {cand_mv}")

        # Input del usuario
        while True:
            resp = input(f"\n  Elegí [1-{len(results)}] / s=saltar / q=salir / b=buscar otro: ").strip().lower()

            if resp == "q":
                print(f"\n✅ Sesión terminada. Guardados: {saved} | Saltados: {skipped}")
                conn.close()
                return

            if resp == "s":
                print("  ➡  Saltado")
                skipped += 1
                break

            if resp == "b":
                new_query = input("  Nuevo nombre a buscar: ").strip()
                if new_query:
                    print(f"  Buscando: '{new_query}' ...", end=" ", flush=True)
                    new_data = search_api(new_query)
                    if new_data:
                        used_query = new_query
                        api_data = new_data
                        results = new_data.get("results", [])[:10]
                        print(f"{len(results)} resultados")
                        print()
                        for i, cand in enumerate(results, 1):
                            cand_name = cand.get("name", "?")
                            cand_age  = cand.get("age", "?")
                            cand_nats = ", ".join(cand.get("nationalities", [])) or "?"
                            cand_club = cand.get("club", {}).get("name", "Sin club") if cand.get("club") else "Sin club"
                            cand_pos  = cand.get("position", "?")
                            cand_mv   = format_mv(cand.get("marketValue"))
                            print(f"  [{i}] {cand_name}  |  {cand_pos}  |  {cand_age} años  |  {cand_club}  |  {cand_nats}  |  {cand_mv}")
                    else:
                        print("sin resultados")
                continue

            try:
                choice = int(resp)
                if 1 <= choice <= len(results):
                    chosen = results[choice - 1]
                    # Construir un api_data con solo el candidato elegido
                    # pero guardamos el response completo para que populate_data.py pueda filtrar
                    save_to_cache(cur, conn, name, api_data)
                    # También guardarlo con la query usada
                    if used_query and used_query != name:
                        save_to_cache(cur, conn, used_query, api_data)
                    chosen_name = chosen.get("name", "?")
                    chosen_mv   = format_mv(chosen.get("marketValue"))
                    chosen_club = chosen.get("club", {}).get("name", "?") if chosen.get("club") else "?"
                    print(f"  ✅ Guardado: {chosen_name} | {chosen_club} | {chosen_mv}")
                    saved += 1
                    break
                else:
                    print(f"  Número inválido. Usá 1-{len(results)}")
            except ValueError:
                print("  Entrada inválida.")

    print(f"\n{'='*60}")
    print("  Revisión completada.")
    print(f"  Guardados en caché: {saved}")
    print(f"  Saltados:          {skipped}")
    print(f"{'='*60}")
    conn.close()

if __name__ == "__main__":
    main()
