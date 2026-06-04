#!/usr/bin/env python3
"""
Enriquece los jugadores de scraped_unresolved_players con datos de Transfermarkt
(age y market_value_eur), usando primero la caché local y luego la API local.

Replica la lógica de resolve_from_transfermarkt_cache de populate_data.py.
"""

import os
import re
import json
import sqlite3
import unicodedata
import difflib
import urllib.parse
import requests

BASE_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
DB_PATH  = os.path.join(BASE_DIR, "data", "worldcup_combined.db")
API_BASE = "http://127.0.0.1:8000"

# ---------------------------------------------------------------------------
# Helpers (copiados de populate_data.py para consistencia)
# ---------------------------------------------------------------------------
def normalize_name(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = text.replace("?", "i")
    char_map = {
        'ı':'i','ğ':'g','ş':'s','ç':'c','ö':'o','ü':'u',
        'ñ':'n','á':'a','é':'e','í':'i','ó':'o','ú':'u',
        'ã':'a','õ':'o','â':'a','ê':'e','î':'i','ô':'o','û':'u',
        'à':'a','è':'e','ì':'i','ò':'o','ù':'u',
        'ä':'a','ë':'e','ï':'i',
        'ø':'o','æ':'ae','å':'a','ß':'ss','ð':'d','þ':'th',
    }
    for k, v in char_map.items():
        text = text.replace(k, v)
    text = unicodedata.normalize('NFD', text)
    text = "".join([c for c in text if 'a' <= c <= 'z' or c == ' '])
    text = " ".join(text.split())
    return text


def clean_for_api_search(name: str) -> str:
    if not isinstance(name, str):
        return ""
    name = name.replace("?", "i")
    name = unicodedata.normalize('NFD', name)
    name = "".join([c for c in name if not unicodedata.combining(c)])
    name = re.sub(r'[^a-zA-Z0-9\s\-]', '', name)
    return " ".join(name.split())


# nationality keywords (same as populate_data.py)
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
def add_column_if_not_exists(cur, table, col, col_type):
    try:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type};")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise


def pick_best_candidate(results, player_name, fifa_code, current_age=None):
    """Selecciona el candidato más probable de la lista de resultados de la API."""
    allowed_nats = [n.lower() for n in NATIONALITY_KEYWORDS.get(fifa_code, [])]
    best_cand  = None
    best_score = -1.0

    for cand in results:
        cand_name = cand.get('name', '')
        cand_age  = cand.get('age')
        cand_nats = [n.lower() for n in cand.get('nationalities', [])]

        # Filtro de nacionalidad
        nat_match = not cand_nats  # sin datos → aceptar
        if not nat_match:
            for nat in cand_nats:
                for ok in allowed_nats:
                    if ok in nat or nat in ok:
                        nat_match = True
                        break
                if nat_match:
                    break
        if not nat_match:
            continue

        # Filtro de edad (tolerancia de 3 años)
        if cand_age is not None and current_age is not None:
            if abs(current_age - cand_age) > 3:
                continue

        set1 = set(normalize_name(player_name).split())
        set2 = set(normalize_name(cand_name).split())
        if not set1 or not set2:
            continue

        jaccard   = len(set1 & set2) / len(set1 | set2)
        seq_ratio = difflib.SequenceMatcher(None, normalize_name(player_name), normalize_name(cand_name)).ratio()
        score     = max(jaccard, seq_ratio)

        if (jaccard >= 0.35 or seq_ratio >= 0.8) and score > best_score:
            best_score = score
            best_cand  = cand

    return best_cand


def resolve_from_cache(cur, player_name, fifa_code, current_age=None):
    """
    Busca en cache_transfermarkt y devuelve (market_value_eur, age, club) o (None, None, None).
    Estrategia de búsqueda:
      1. Exact match por nombre
      2. Exact match por nombre limpio
      3. Fuzzy (Jaccard / SequenceMatcher) sobre todos los queries de la caché
      4. Llamada a la API local
    """

    def try_json(row):
        if not row:
            return None
        try:
            data = json.loads(row[0])
            if data and data.get('results'):
                return data
        except Exception:
            pass
        return None

    # 1. Exact match
    cur.execute("SELECT response_json FROM cache_transfermarkt WHERE query = ?", (player_name,))
    api_data = try_json(cur.fetchone())

    # 2. Clean name
    if not api_data:
        clean = clean_for_api_search(player_name)
        cur.execute("SELECT response_json FROM cache_transfermarkt WHERE query = ?", (clean,))
        api_data = try_json(cur.fetchone())

    # 3. Fuzzy search sobre toda la caché
    if not api_data:
        cur.execute("SELECT query, response_json FROM cache_transfermarkt")
        all_cache = cur.fetchall()
        norm_p   = normalize_name(player_name)
        tokens_p = set(norm_p.split())
        best_score = -1.0
        best_json  = None
        for q_name, q_json in all_cache:
            try:
                q_data = json.loads(q_json)
                if not q_data or not q_data.get('results'):
                    continue
            except Exception:
                continue
            norm_q   = normalize_name(q_name)
            tokens_q = set(norm_q.split())
            jacc     = (len(tokens_p & tokens_q) / len(tokens_p | tokens_q)) if tokens_q else 0.0
            seq      = difflib.SequenceMatcher(None, norm_p, norm_q).ratio()
            score    = max(jacc, seq)
            if (jacc >= 0.5 or seq >= 0.8) and score > best_score:
                best_score = score
                best_json  = q_json
        if best_json:
            api_data = try_json((best_json,))

    # 4. API local
    if not api_data:
        try:
            url  = f"{API_BASE}/players/search/{urllib.parse.quote(player_name)}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                resp_data = resp.json()
                if resp_data and resp_data.get('results'):
                    resp_str = json.dumps(resp_data)
                    cur.execute(
                        "INSERT OR REPLACE INTO cache_transfermarkt (query, response_json) VALUES (?, ?)",
                        (player_name, resp_str)
                    )
                    clean = clean_for_api_search(player_name)
                    if clean != player_name:
                        cur.execute(
                            "INSERT OR REPLACE INTO cache_transfermarkt (query, response_json) VALUES (?, ?)",
                            (clean, resp_str)
                        )
                    cur.connection.commit()
                    api_data = resp_data
                    print(f"    [API] Guardado en caché para '{player_name}'")
        except Exception as e:
            print(f"    [API] Error: {e}")

    if not api_data:
        return None, None, None

    cand = pick_best_candidate(api_data['results'], player_name, fifa_code, current_age)
    if cand:
        mv   = cand.get('marketValue')
        mv_m = round(float(mv) / 1_000_000.0, 1) if mv is not None else None
        age  = cand.get('age')
        club = cand.get('club', {}).get('name') if cand.get('club') else None
        return mv_m, age, club

    return None, None, None


# ---------------------------------------------------------------------------
def main():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: DB no encontrada en {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # Aseguramos que exista la columna market_value_eur
    add_column_if_not_exists(cur, "scraped_unresolved_players", "market_value_eur", "REAL")
    conn.commit()

    # Traer todos los jugadores sin resolver (o todos, para completar datos faltantes)
    cur.execute(
        "SELECT player_id, player_name, fifa_code, age FROM scraped_unresolved_players"
        " WHERE market_value_eur IS NULL OR age IS NULL OR age = 26"
    )
    players = cur.fetchall()
    print(f"Procesando {len(players)} jugadores sin datos completos de Transfermarkt...")

    enriched = 0
    for pid, name, fifa_code, current_age in players:
        print(f"[{pid}] {name} ({fifa_code}) ...", end=" ")
        mv, age, club = resolve_from_cache(cur, name, fifa_code, current_age)

        updates = []
        params  = []
        if mv is not None:
            updates.append("market_value_eur = ?")
            params.append(mv)
        if age is not None:
            updates.append("age = ?")
            params.append(age)
        if club is not None:
            updates.append("club = ?")
            params.append(club)

        if updates:
            params.append(pid)
            cur.execute(
                f"UPDATE scraped_unresolved_players SET {', '.join(updates)} WHERE player_id = ?",
                params
            )
            conn.commit()
            enriched += 1
            print(f"OK => mv={mv}M, age={age}, club={club}")
        else:
            print("sin datos")

    conn.close()
    print(f"\nFinalizado: {enriched}/{len(players)} jugadores enriquecidos.")


if __name__ == "__main__":
    main()
