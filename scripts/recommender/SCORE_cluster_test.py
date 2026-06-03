# Ejemplo en un REPL o script separado
import sys
import os
from pathlib import Path

# <-- Añadimos la raíz del repositorio al path de búsqueda
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if repo_root not in sys.path:
    sys.path.append(repo_root)

# Importamos la función del módulo que está bajo scripts/recommender/
from scripts.recommender.score_cluster_players import run_score

# 1️⃣ Definir el partido
match = ("Inglaterra", "Francia")

# 2️⃣ Definir los clusters favoritos (un id por posición)
favourite_clusters = {
    "Goalkeeper": 2,
    "Centerbacks": 2,
    "Fullbacks": 2,
    "Midfielder": 3,
    "Striker": 1,
    "Wingers": 2,
}

# 3️⃣ Opcional: ruta a la base de datos (si no hay DB usa el ejemplo interno)
db_path = Path("data/recommender_data/convocados.db")   # ← nueva ubicación

# 4️⃣ Ejecutar
print("--- Test con a = 3.0 (Default) ---")
normalized_score, breakdown = run_score(match, favourite_clusters, db_path=db_path, a=3.0)

print(f"SCORE_global_normalizado (a=3.0): {normalized_score:.4f}")
for pos, players in breakdown.items():
    if not players:
        continue
    print(f"{pos} (cluster {favourite_clusters.get(pos)}):")
    for p in players:
        print(f"  {p['player']} ({p['country']}): {p['contribution']:.4f}")
    print()

print("\n--- Test con a = 2.0 ---")
normalized_score_2, breakdown_2 = run_score(match, favourite_clusters, db_path=db_path, a=2.0)
print(f"SCORE_global_normalizado (a=2.0): {normalized_score_2:.4f}")

print("\n--- Test con a = 10.0 ---")
normalized_score_10, breakdown_10 = run_score(match, favourite_clusters, db_path=db_path, a=10.0)
print(f"SCORE_global_normalizado (a=10.0): {normalized_score_10:.4f}")

