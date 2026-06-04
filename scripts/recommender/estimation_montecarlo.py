#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
estimation_montecarlo.py
────────────────────────

Este script realiza una calibración estadística (Monte‑Carlo) del
pipeline de scoring de partidos (`run_score`) para estimar los
parámetros de la función sigmoide que normaliza el `total_score`
entre 0 y 1:

    S_match = 1 / (1 + exp(-( (total_score - mu) / sigma )))

Pasos generales:
1️⃣  Obtiene la lista de países disponibles en la base de datos
    SQLite `convocados.db`.
2️⃣  Genera N combinaciones aleatorias de pares de países y
    configuraciones de `favourite_clusters`.
3️⃣  Ejecuta `run_score` para cada combinación y recopila los
    `total_score` resultantes.
4️⃣  Calcula la media (`mu`) y la desviación estándar (`sigma`)
    de esos scores.
5️⃣  Persiste los valores en `data/recommender_config.json` para
    que `score_cluster_players.py` los pueda leer en producción.
6️⃣  Imprime un resumen estadístico.
"""

import json
import random
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Configuración básica
DEFAULT_SIMULATIONS = 2000
RANDOM_SEED = 42

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "recommender_data" / "convocados.db"
CONFIG_PATH = PROJECT_ROOT / "data" / "recommender_config.json"

# Import de la lógica de scoring
try:
    sys.path.append(str(PROJECT_ROOT))
    from scripts.recommender.score_cluster_players import run_score
except Exception as exc:
    sys.stderr.write(f"[ERROR] No se pudo importar run_score: {exc}\n")
    sys.exit(1)


def get_countries(db_path: Path) -> List[str]:
    """Extrae la lista única de países en convocados.db."""
    if not db_path.is_file():
        raise FileNotFoundError(f"Base de datos no encontrada en: {db_path}")

    with sqlite3.connect(str(db_path)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT pais FROM convocados")
        rows = cur.fetchall()
        return [row[0] for row in rows]


def random_match(countries: List[str]) -> Tuple[str, str]:
    """Genera un par de países aleatorios."""
    p1, p2 = random.sample(countries, 2)
    return p1, p2


def random_favourite_clusters() -> Dict[str, int]:
    """Genera configuraciones de clusters favoritos aleatorios (IDs 1 a 4)."""
    positions = [
        "Goalkeeper",
        "Centerbacks",
        "Fullbacks",
        "Midfielder",
        "Striker",
        "Wingers",
    ]
    return {pos: random.randint(1, 4) for pos in positions}


def calibrate(
    n_simulations: int = DEFAULT_SIMULATIONS,
    db_path: Path = DB_PATH,
) -> Tuple[float, float, List[float]]:
    """Ejecuta la simulación Monte-Carlo."""
    random.seed(RANDOM_SEED)

    try:
        countries = get_countries(db_path)
    except Exception as exc:
        sys.stderr.write(f"[ERROR] No se pudieron obtener los países: {exc}\n")
        sys.exit(1)

    if len(countries) < 2:
        sys.stderr.write("[ERROR] Se necesitan al menos 2 países para simular partidos.\n")
        sys.exit(1)

    scores: List[float] = []

    # Intentamos usar tqdm para el progreso
    try:
        from tqdm import tqdm
        iterator = tqdm(range(n_simulations), desc="Simulando partidos")
    except ImportError:
        iterator = range(n_simulations)

    for _ in iterator:
        match = random_match(countries)
        fav_clusters = random_favourite_clusters()

        try:
            # Llamamos a run_score con el valor default a=3.0 establecido
            total_score, _ = run_score(
                match,
                fav_clusters,
                db_path=db_path,
                a=3.0,
            )
            scores.append(total_score)
        except Exception as exc:
            # Emitir warning pero seguir adelante
            sys.stderr.write(f"[WARNING] Omitiendo combinación {match}: {exc}\n")
            continue

    if not scores:
        sys.stderr.write("[ERROR] No se pudo recopilar ningún score.\n")
        sys.exit(1)

    import numpy as np

    mu = float(np.mean(scores))
    sigma = float(np.std(scores, ddof=1))

    return mu, sigma, scores


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Calibración Monte-Carlo para normalización sigmoide."
    )
    parser.add_argument(
        "-n",
        "--num-simulations",
        type=int,
        default=DEFAULT_SIMULATIONS,
        help=f"Número de simulaciones (default: {DEFAULT_SIMULATIONS})",
    )
    args = parser.parse_args()

    print(f"Iniciando simulación Monte-Carlo con {args.num_simulations} iteraciones...")
    mu, sigma, scores = calibrate(n_simulations=args.num_simulations)

    # Persistir parámetros
    config_data = {
        "sigmoid_mu": mu,
        "sigmoid_sigma": sigma,
    }
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as fp:
        json.dump(config_data, fp, indent=4, ensure_ascii=False)

    print("\n--- Resultados de Calibración ---")
    print(f"Simulaciones exitosas: {len(scores)}")
    print(f"Score lineal mínimo  : {min(scores):.4f}")
    print(f"Score lineal máximo  : {max(scores):.4f}")
    print(f"Media (mu)           : {mu:.4f}")
    print(f"Desviación (sigma)   : {sigma:.4f}")
    print(f"Configuración guardada en: {CONFIG_PATH}")


if __name__ == "__main__":
    main()
