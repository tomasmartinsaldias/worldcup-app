"""
fetch_footballdata_crests.py
============================
Consulta la API de Football-Data.org para obtener el escudo ("crest") de cada
equipo listado en `data/data_frontend/convocados_equipos.json` y exporta los
resultados a `data/data_frontend/teams.json`.

Pipeline de texto y matching (heurístico por capas):
  1. Normalización base: NFKD → strip acentos → minúsculas.
  2. Limpieza de stopwords deportivas (por token completo).
  3. Manejo de entradas compuestas: "Club A/Club B" → se evalúa cada sub-nombre.
  4. Matching en cascada de 3 capas de confianza decreciente:
       Capa 1 – Identidad absoluta (cadenas limpias idénticas).
       Capa 2 – Intersección de tokens (subconjunto o Jaccard ≥ umbral).
       Capa 3 – Similitud morfológica via difflib.SequenceMatcher.

Uso:
  $env:FOOTBALL_DATA_API_KEY = "tu_api_key"   # PowerShell
  python scripts/fetch_footballdata_crests.py
"""

import difflib
import json
import logging
import os
import sys
import unicodedata
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Configuración de rutas (relativas a la raíz del repositorio)
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_PATH  = BASE_DIR / "data" / "data_frontend" / "convocados_equipos.json"
OUTPUT_DIR  = BASE_DIR / "data" / "data_frontend"
OUTPUT_PATH = OUTPUT_DIR / "teams.json"
LOG_DIR     = BASE_DIR / "logs"
LOG_PATH    = LOG_DIR  / "team_crests.log"

# ---------------------------------------------------------------------------
# Configuración de la API
# ---------------------------------------------------------------------------
API_KEY      = os.getenv("FOOTBALL_DATA_API_KEY", "YOUR_API_KEY_HERE").strip()
HTTP_TIMEOUT = 10  # segundos
BASE_URL     = "https://api.football-data.org/v4/teams"

# ---------------------------------------------------------------------------
# Hiperparámetros del matcher
# ---------------------------------------------------------------------------
# Jaccard mínimo para que la Capa 2 acepte el match por intersección de tokens.
THRESHOLD_JACCARD: float = 0.60
# Ratio mínimo de SequenceMatcher para que la Capa 3 acepte el match difuso.
THRESHOLD_FUZZY: float = 0.80

# Tokens que no aportan identidad al nombre del club.
# REGLA: solo se eliminan siglas/abreviaturas estructurales que NUNCA forman
# parte del nombre semántico de un club. Palabras como "real", "united",
# "city" o "sporting" se conservan porque SÍ diferencian clubes entre sí.
SPORT_STOPWORDS: frozenset[str] = frozenset({
    # Siglas organizativas puras
    "fc", "fk", "sk", "sc", "tc", "sfc", "afc", "bsc", "rsc",
    "bfc", "cfc", "nfc", "hfc",
    # Abreviaturas con puntos (post-normalización ya estarán sin acento)
    "f.c.", "f.c", "a.f.c.", "s.s.c.", "s.s.",
    # Preposiciones y artículos que no distinguen clubes
    "de", "del", "la", "le", "el", "los", "las", "the",
    # Sustantivo genérico
    "as",
})


# ---------------------------------------------------------------------------
# Logging estructurado (consola + archivo)
# ---------------------------------------------------------------------------
def _setup_logging() -> logging.Logger:
    """Configura un logger que escribe simultáneamente en consola y en archivo."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    fmt = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    file_handler.setFormatter(fmt)

    # En Windows la consola puede ser cp1252; forzamos UTF-8 para evitar
    # UnicodeEncodeError con nombres de clubes con caracteres especiales.
    import io
    console_stream = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
    ) if hasattr(sys.stdout, "buffer") else sys.stdout
    console_handler = logging.StreamHandler(console_stream)
    console_handler.setFormatter(fmt)

    logger = logging.getLogger("fetch_crests")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


log = _setup_logging()


# ---------------------------------------------------------------------------
# REQ. 1 – Normalización de texto con limpieza de stopwords
# ---------------------------------------------------------------------------
def _strip_accents(text: str) -> str:
    """
    Paso 1 – Descompone Unicode (NFKD) y elimina diacríticos.

    Ejemplo: "Ferencváros TC" → "Ferencvaros TC"
    """
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize_text(text: str) -> str:
    """
    Normalización base: desacentúa, pasa a minúsculas y hace strip.

    No elimina stopwords —eso lo hace `clean_tokens()` como paso separado—
    para permitir que las comparaciones de la Capa 1 sean sobre el núcleo limpio.

    Ejemplo:
      "Atlético de Madrid FC" → "atletico de madrid fc"
    """
    if not text or not isinstance(text, str):
        return ""
    return _strip_accents(text).strip().lower()


def clean_tokens(normalized: str) -> str:
    """
    Paso 2 – Tokeniza por espacios y elimina las stopwords deportivas.

    La remoción se realiza únicamente sobre *tokens completos* (comparación
    de igualdad), nunca como substring, para no destruir palabras cortas que
    contengan parcialmente una sigla (e.g. "nice", "standard").

    Ejemplo:
      "atletico de madrid fc" → "madrid"   (tokens: atletico, de, madrid, fc)
      "nice fc"               → "nice"     ("nice" no está en SPORT_STOPWORDS)
      "standard liege sc"     → "standard liege"
    """
    tokens = normalized.split()
    meaningful = [t for t in tokens if t not in SPORT_STOPWORDS]
    # Si la limpieza dejó el string vacío (todos tokens eran stopwords),
    # devolvemos el original para no perder la cadena completa.
    return " ".join(meaningful) if meaningful else normalized


def full_normalize(text: str) -> str:
    """Combina `normalize_text` + `clean_tokens` en un solo paso."""
    return clean_tokens(normalize_text(text))


# ---------------------------------------------------------------------------
# REQ. 2 – Manejo de entradas compuestas (split por '/')
# ---------------------------------------------------------------------------
def split_compound(name: str) -> list[str]:
    """
    Si el nombre contiene '/', lo divide en sub-nombres independientes y
    retorna cada uno ya con strip aplicado.

    Ejemplo:
      "Fenerbahçe SK/Betis"      → ["Fenerbahçe SK", "Betis"]
      "West Ham United/Marsella" → ["West Ham United", "Marsella"]
      "Arsenal"                  → ["Arsenal"]
    """
    if "/" in name:
        parts = [p.strip() for p in name.split("/") if p.strip()]
        return parts if parts else [name]
    return [name]


# ---------------------------------------------------------------------------
# REQ. 3 – Matching heurístico por capas
# ---------------------------------------------------------------------------
def _jaccard(set_a: set[str], set_b: set[str]) -> float:
    """
    Índice de Jaccard entre dos conjuntos de tokens.

    J(A, B) = |A ∩ B| / |A ∪ B|

    Retorna 0.0 si la unión es vacía para evitar división por cero.
    """
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def _fuzzy_ratio(a: str, b: str) -> float:
    """
    Similitud morfológica usando difflib.SequenceMatcher.

    SequenceMatcher cuenta la cantidad de caracteres en subcadenas comunes más
    largas y calcula:
        ratio = 2 * |bloques_comunes| / (len(a) + len(b))

    Ejemplo:
      "bayern munich" vs "fc bayern munchen" (clean) → ratio ≈ 0.82
    """
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def _match_single(local_clean: str, api_teams_processed: list[dict]) -> dict | None:
    """
    Ejecuta el pipeline de 3 capas para un único nombre local ya normalizado
    y sin stopwords.

    Capa 1 – Identidad absoluta (ratio = 1.0):
        clean_local == clean_api_name  OR  clean_local == clean_api_short

    Capa 2 – Intersección de tokens (ratio ≥ THRESHOLD_JACCARD):
        a) El set local es subconjunto del set API: tokens_local ⊆ tokens_api
           Esto captura "milan" ⊆ {"ac", "milan"} → True
        b) Jaccard(tokens_local, tokens_api) ≥ THRESHOLD_JACCARD
           Útil cuando los nombres comparten la mayoría de tokens pero en distinto
           orden o con tokens extra en ambos lados.

    Capa 3 – Fuzzy morphological (SequenceMatcher ≥ THRESHOLD_FUZZY):
        Captura variaciones de spelling o transliteración ("munich" vs "munchen").
    """
    if not local_clean:
        return None

    local_tokens = set(local_clean.split())

    # Pre-compute candidate list once
    for api_team in api_teams_processed:
        api_name  = api_team["name_clean"]
        api_short = api_team["short_clean"]
        api_name_tokens  = set(api_name.split())  if api_name  else set()
        api_short_tokens = set(api_short.split()) if api_short else set()

        # --- CAPA 1: Identidad absoluta ---
        if local_clean == api_name or local_clean == api_short:
            log.debug("  [L1-exacto] '%s' == '%s'", local_clean, api_name or api_short)
            return api_team

        # --- CAPA 2: Intersección de tokens ---
        # 2a) Subconjunto
        if local_tokens and (
            (api_name_tokens  and local_tokens <= api_name_tokens)
            or (api_short_tokens and local_tokens <= api_short_tokens)
        ):
            log.debug("  [L2-subset] '%s' ⊆ '%s'", local_clean, api_name)
            return api_team
        # 2b) Jaccard
        j_name  = _jaccard(local_tokens, api_name_tokens)
        j_short = _jaccard(local_tokens, api_short_tokens)
        if max(j_name, j_short) >= THRESHOLD_JACCARD:
            best = api_name if j_name >= j_short else api_short
            log.debug(
                "  [L2-jaccard] '%s' ~ '%s'  J=%.2f",
                local_clean, best, max(j_name, j_short),
            )
            return api_team

        # --- CAPA 3: Similitud morfológica (fuzzy) ---
        r_name  = _fuzzy_ratio(local_clean, api_name)
        r_short = _fuzzy_ratio(local_clean, api_short)
        best_r  = max(r_name, r_short)
        if best_r >= THRESHOLD_FUZZY:
            best = api_name if r_name >= r_short else api_short
            log.debug(
                "  [L3-fuzzy] '%s' ~ '%s'  ratio=%.2f",
                local_clean, best, best_r,
            )
            return api_team

    return None


def find_match(local_name: str, api_teams_processed: list[dict]) -> dict | None:
    """
    Punto de entrada del matcher.

    Combina REQ. 2 (split de entradas compuestas) con el pipeline de 3 capas:
    - Divide `local_name` si contiene '/'.
    - Evalúa cada sub-nombre de forma independiente.
    - Retorna el primer match positivo (cualquier sub-nombre es suficiente).
    """
    for sub_name in split_compound(local_name):
        local_clean = full_normalize(sub_name)
        result = _match_single(local_clean, api_teams_processed)
        if result:
            return result
    return None


# ---------------------------------------------------------------------------
# Carga del archivo de entrada
# ---------------------------------------------------------------------------
def load_local_teams() -> list[str]:
    """
    Lee `convocados_equipos.json` y devuelve la lista de nombres de equipos.
    Soporta dos formatos:
      - Lista directa:  ["Equipo A", "Equipo B", ...]
      - Objeto con clave "equipo_buscado": {"equipo_buscado": "Equipo A"}
    """
    if not INPUT_PATH.is_file():
        log.error("Archivo de entrada no encontrado: %s", INPUT_PATH)
        sys.exit(1)

    try:
        with open(INPUT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as err:
        log.error("Error al parsear el JSON de entrada: %s", err)
        sys.exit(1)

    if isinstance(data, list):
        teams = [t for t in data if t and isinstance(t, str)]
        log.info("Cargados %d equipos desde %s", len(teams), INPUT_PATH.name)
        return teams

    if isinstance(data, dict) and "equipo_buscado" in data:
        team_name = str(data["equipo_buscado"]).strip()
        if not team_name:
            log.error("La clave 'equipo_buscado' está vacía en el JSON de entrada.")
            sys.exit(1)
        log.info("Modo de búsqueda individual: '%s'", team_name)
        return [team_name]

    log.error(
        "Formato de JSON no reconocido. Se esperaba una lista de strings "
        "o un objeto con la clave 'equipo_buscado'."
    )
    sys.exit(1)


# ---------------------------------------------------------------------------
# Fetching desde la API
# ---------------------------------------------------------------------------
def fetch_all_teams_from_api() -> list[dict]:
    """
    Recupera equipos de la API de Football-Data.org.

    Estrategia:
    1. Obtiene la lista de competiciones y recupera sus equipos.
    2. Respaldo: itera el endpoint genérico /v4/teams con paginación.
    3. Fusiona ambos conjuntos eliminando duplicados por ID de equipo.
    """
    if API_KEY == "YOUR_API_KEY_HERE":
        log.error("API Key no configurada.")
        sys.exit(1)

    headers  = {"X-Auth-Token": API_KEY}
    all_teams: list[dict] = []
    seen_ids: set = set()

    # 1. Equipos por competición
    try:
        comps_resp = requests.get(
            "https://api.football-data.org/v4/competitions",
            headers=headers,
            timeout=HTTP_TIMEOUT,
        )
        comps_resp.raise_for_status()
        competitions = comps_resp.json().get("competitions", [])
    except Exception as err:
        log.error("Error al obtener competiciones: %s", err)
        sys.exit(1)

    for comp in competitions:
        comp_id   = comp.get("id")
        comp_name = comp.get("name", "<sin nombre>")
        if not comp_id:
            continue
        try:
            resp = requests.get(
                f"https://api.football-data.org/v4/competitions/{comp_id}/teams",
                headers=headers,
                timeout=HTTP_TIMEOUT,
            )
            resp.raise_for_status()
            teams = resp.json().get("teams", [])
            for team in teams:
                tid = team.get("id")
                if tid and tid not in seen_ids:
                    all_teams.append(team)
                    seen_ids.add(tid)
            log.info("Competición '%s': %d equipos.", comp_name, len(teams))
        except Exception as err:
            log.warning("No se pudieron obtener equipos de '%s': %s", comp_name, err)

    # 2. Respaldo: paginación genérica /v4/teams
    limit, offset = 200, 0
    while True:
        try:
            resp = requests.get(
                f"{BASE_URL}?limit={limit}&offset={offset}",
                headers=headers,
                timeout=HTTP_TIMEOUT,
            )
            resp.raise_for_status()
        except Exception as err:
            log.warning("Paginación detenida en offset %d: %s", offset, err)
            break

        payload = resp.json()
        batch   = payload.get("teams", payload if isinstance(payload, list) else [])
        if not batch:
            break
        for team in batch:
            tid = team.get("id")
            if tid and tid not in seen_ids:
                all_teams.append(team)
                seen_ids.add(tid)
        log.info("Paginación offset=%d: %d equipos en el batch.", offset, len(batch))
        offset += limit

    if not all_teams:
        log.warning("No se obtuvieron equipos de la API.")
    else:
        log.info("Total equipos únicos recopilados: %d", len(all_teams))
    return all_teams


# ---------------------------------------------------------------------------
# Pre-procesamiento de equipos de la API
# ---------------------------------------------------------------------------
def preprocess_api_teams(api_teams: list[dict]) -> list[dict]:
    """
    Normaliza y limpia los campos `name` y `shortName` de cada equipo.

    Genera las claves:
      - name_clean  : full_normalize(name)
      - short_clean : full_normalize(shortName)
      - crest       : URL del escudo (puede ser None)
      - original_name: nombre sin modificar para reportes
    """
    processed = []
    for team in api_teams:
        name       = team.get("name")       or ""
        short_name = team.get("shortName")  or ""
        crest      = team.get("crest")      or None

        processed.append({
            "name_clean":    full_normalize(name),
            "short_clean":   full_normalize(short_name),
            "crest":         crest,
            "original_name": name,
        })
    return processed


# ---------------------------------------------------------------------------
# Guardado del resultado
# ---------------------------------------------------------------------------
def save_output(results: list[dict]) -> None:
    """Escribe `teams.json` con la lista de equipos y sus crests."""
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        log.info(
            "Archivo generado exitosamente: %s (%d entradas)",
            OUTPUT_PATH,
            len(results),
        )
    except OSError as err:
        log.error("Error al escribir el archivo de salida: %s", err)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Punto de entrada principal
# ---------------------------------------------------------------------------
def main() -> None:
    log.info("=" * 60)
    log.info("Inicio de fetch_footballdata_crests.py")
    log.info("Threshold Jaccard: %.2f | Threshold Fuzzy: %.2f", THRESHOLD_JACCARD, THRESHOLD_FUZZY)
    log.info("=" * 60)

    # 1. Cargar lista de equipos locales
    local_teams = load_local_teams()

    # 2. Descargar todos los equipos de la API
    api_teams_raw = fetch_all_teams_from_api()
    if not api_teams_raw:
        log.error("No se obtuvieron equipos de la API. Abortando.")
        sys.exit(1)

    # 3. Pre-procesar (normalizar + limpiar stopwords) equipos de la API
    api_teams_processed = preprocess_api_teams(api_teams_raw)

    # 4. Iterar equipos locales y realizar el matching
    matched:   list[dict] = []
    unmatched: list[str]  = []

    for local_name in local_teams:
        result = find_match(local_name, api_teams_processed)

        if result:
            crest = result["crest"]
            matched.append({"team": local_name, "crest": crest})

            if crest:
                preview = crest[:60] + "..." if len(crest) > 60 else crest
                log.info("MATCH: %-45s → %s", local_name, preview)
            else:
                log.warning("MATCH SIN CREST: %s", local_name)
        else:
            unmatched.append(local_name)
            log.warning("SIN COINCIDENCIA: %s", local_name)

    # 5. Guardar resultados
    save_output(matched)

    # 6. Reporte final
    log.info("-" * 60)
    log.info("RESUMEN:")
    log.info("  Equipos en lista local : %d", len(local_teams))
    log.info("  Matches encontrados    : %d", len(matched))
    log.info("  Sin coincidencia       : %d", len(unmatched))

    if unmatched:
        log.info("Equipos sin coincidencia en la API:")
        for name in sorted(unmatched):
            log.info("  - %s", name)

    log.info("=" * 60)
    log.info("Script finalizado.")


if __name__ == "__main__":
    main()
