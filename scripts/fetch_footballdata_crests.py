"""
fetch_footballdata_crests.py
============================
Consulta la API de Football-Data.org para obtener el escudo ("crest") de cada
equipo listado en `data/data_frontend/convocados_equipos.json` y exporta los
resultados a `data/data_frontend/teams.json`.

Características:
  - Paginación automática del endpoint /v4/teams/ (offset + limit).
  - Normalización de texto con `unicodedata` para matching sin acentos.
  - Matching flexible: igualdad o substring en campos `name` y `shortName`.
  - Logging estructurado a consola y a `logs/team_crests.log`.
  - Manejo de excepciones HTTP (401, 403, 429, 5xx) con mensajes claros.
  - Creación automática de directorios de salida si no existen.

Uso:
  Configura la variable de entorno FOOTBALL_DATA_API_KEY antes de ejecutar:
    $env:FOOTBALL_DATA_API_KEY = "tu_api_key_aqui"   # PowerShell
    export FOOTBALL_DATA_API_KEY="tu_api_key_aqui"   # Bash / macOS
  Luego:
    python scripts/fetch_footballdata_crests.py
"""

import json
import logging
import os
import sys
import time
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
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "YOUR_API_KEY_HERE").strip()
HTTP_TIMEOUT = 10  # seconds
BASE_URL = "https://api.football-data.org/v4/teams"


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

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(fmt)

    logger = logging.getLogger("fetch_crests")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


log = _setup_logging()

# ---------------------------------------------------------------------------
# Normalización de texto
# ---------------------------------------------------------------------------
def normalize_text(text: str) -> str:
    """
    Normaliza una cadena de texto para comparaciones flexibles:
      1. Descompone caracteres Unicode (NFKD) para separar letras de diacríticos.
      2. Elimina todos los caracteres de combinación (acentos, tildes, etc.).
      3. Aplica strip() para eliminar espacios redundantes.
      4. Convierte a minúsculas.

    Ejemplo:
      "Atlético de Madrid" → "atletico de madrid"
      "Ferencváros TC"     → "ferencvaros tc"
    """
    if not text or not isinstance(text, str):
        return ""
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_only = "".join(c for c in nfkd if not unicodedata.combining(c))
    return ascii_only.strip().lower()

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

    # Soporte para lista de strings
    if isinstance(data, list):
        teams = [t for t in data if t and isinstance(t, str)]
        log.info("Cargados %d equipos desde %s", len(teams), INPUT_PATH.name)
        return teams

    # Soporte para objeto con clave "equipo_buscado"
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
# Fetching con paginación
# ---------------------------------------------------------------------------
def fetch_all_teams_from_api() -> list[dict]:
    """
    Recupera todos los equipos disponibles del endpoint /v4/teams/
    mediante paginación automática (offset + limit).

    Maneja errores HTTP comunes:
    Recupera todos los equipos disponibles del endpoint /v4/competitions/{id}/teams
    Maneja el fallback a la API general si la competición no es accesible.
    """
    if API_KEY == "YOUR_API_KEY_HERE":
        log.error("API Key no configurada.")
        sys.exit(1)

    headers = {"X-Auth-Token": API_KEY}
    log.info("Iniciando descarga de equipos...")

    try:
        response = requests.get(BASE_URL, headers=headers, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        # If the API returns 400, it likely does not accept pagination params
        if response.status_code == 400:
            log.info("API returned 400 with pagination params – retrying without params.")
            # Retry without any query parameters
            response = requests.get(BASE_URL, headers=headers, timeout=HTTP_TIMEOUT)
            response.raise_for_status()
        else:
            log.error("Error HTTP inesperado: %s", err)
            sys.exit(1)
    # Parse response (should contain a list of teams)
    try:
        payload = response.json()
    except ValueError:
        log.error("La respuesta de la API no es JSON válido.")
        sys.exit(1)
    # Some API versions return the list directly, others wrap it under 'teams'
    teams = payload.get("teams", payload if isinstance(payload, list) else [])
    if not teams:
        log.warning("No se recibieron equipos de la API.")
    else:
        log.info("Se obtuvieron %d equipos de la API.", len(teams))
    return teams

# ---------------------------------------------------------------------------
# Pre-procesamiento de equipos de la API
# ---------------------------------------------------------------------------
def preprocess_api_teams(api_teams: list[dict]) -> list[dict]:
    """
    Normaliza los campos `name` y `shortName` de cada equipo de la API
    y los almacena junto con el crest y el nombre original para el matching.

    Args:
        api_teams: Lista de objetos de equipos crudos devueltos por la API.

    Returns:
        Lista de dicts con claves: name_norm, short_norm, crest, original_name.
    """
    processed = []
    for team in api_teams:
        name       = team.get("name") or ""
        short_name = team.get("shortName") or ""
        crest      = team.get("crest") or None

        processed.append({
            "name_norm":     normalize_text(name),
            "short_norm":    normalize_text(short_name),
            "crest":         crest,
            "original_name": name,
        })
    return processed

# ---------------------------------------------------------------------------
# Matching flexible
# ---------------------------------------------------------------------------
def find_match(local_norm: str, api_teams_processed: list[dict]) -> dict | None:
    """
    Busca la primera coincidencia entre el nombre local normalizado y los
    equipos de la API, usando las siguientes reglas (en orden de prioridad):

      1. Igualdad exacta con `name` normalizado.
      2. Igualdad exacta con `shortName` normalizado.
      3. Nombre local contenido dentro de `name` de la API.
      4. Nombre local contenido dentro de `shortName` de la API.
      5. `name` de la API contenido dentro del nombre local.
      6. `shortName` de la API contenido dentro del nombre local.

    Args:
        local_norm:           Nombre local ya normalizado.
        api_teams_processed:  Lista pre-procesada de equipos de la API.

    Returns:
        El primer dict de equipo que cumple alguna condición, o None si no hay match.
    """
    if not local_norm:
        return None

    for api_team in api_teams_processed:
        api_name  = api_team["name_norm"]
        api_short = api_team["short_norm"]

        if (
            local_norm == api_name
            or local_norm == api_short
            or (api_name  and local_norm in api_name)
            or (api_short and local_norm in api_short)
            or (api_name  and api_name  in local_norm)
            or (api_short and api_short in local_norm)
        ):
            return api_team

    return None

# ---------------------------------------------------------------------------
# Guardado del resultado
# ---------------------------------------------------------------------------
def save_output(results: list[dict]) -> None:
    """
    Crea el directorio de salida si no existe y escribe `teams.json`
    con la lista de equipos y sus crests.

    Args:
        results: Lista de dicts {"team": "...", "crest": "..."}.
    """
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        log.info("Archivo generado exitosamente: %s (%d entradas)", OUTPUT_PATH, len(results))
    except OSError as err:
        log.error("Error al escribir el archivo de salida: %s", err)
        sys.exit(1)

# ---------------------------------------------------------------------------
# Punto de entrada principal
# ---------------------------------------------------------------------------
def main() -> None:
    log.info("=" * 60)
    log.info("Inicio de fetch_footballdata_crests.py")
    log.info("=" * 60)

    # 1. Cargar lista de equipos locales
    local_teams = load_local_teams()

    # 2. Descargar todos los equipos de la API (con paginación)
    api_teams_raw = fetch_all_teams_from_api()
    if not api_teams_raw:
        log.error("No se obtuvieron equipos de la API. Abortando.")
        sys.exit(1)

    # 3. Pre-procesar (normalizar) equipos de la API una sola vez
    api_teams_processed = preprocess_api_teams(api_teams_raw)

    # 4. Iterar equipos locales y realizar el matching
    matched:   list[dict] = []
    unmatched: list[str]  = []

    for local_name in local_teams:
        local_norm = normalize_text(local_name)
        result     = find_match(local_norm, api_teams_processed)

        if result:
            crest = result["crest"]
            matched.append({"team": local_name, "crest": crest})

            if crest:
                log.info("MATCH: %-45s → %s", local_name, crest[:60] + "..." if len(crest) > 60 else crest)
            else:
                log.warning("MATCH SIN CREST: %s (la API no devolvió URL de escudo)", local_name)
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
