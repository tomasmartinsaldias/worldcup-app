import sqlite3
import os

base_dir = "c:/Users/tomas/Desktop/proyectos/worldcup-app"
db_path = os.path.join(base_dir, "data", "worldcup_combined.db")

if not os.path.exists(db_path):
    print("Database not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Cargar el mapeo de nombres de países para mostrar
cur.execute("SELECT fifa_code, team_name FROM wc2026_teams;")
code_to_name = {code: name for code, name in cur.fetchall()}

# Obtener los valores del ranking oficial FIFA (cargados en scraped_team_metrics de ranking_fifa.txt)
cur.execute("SELECT fifa_code, market_value_eur FROM scraped_team_metrics;")
official_values = {code: val for code, val in cur.fetchall()}

# Calcular la suma del market_value_eur de los jugadores por país
cur.execute("""
    SELECT fifa_code, SUM(market_value_eur) 
    FROM scraped_wc2026_probable_squads 
    GROUP BY fifa_code;
""")
summed_values = {code: round(val, 2) if val is not None else 0.0 for code, val in cur.fetchall()}

print(f"{'País (Código)':<30} | {'Ranking FIFA (M€)':<20} | {'Suma de Jugadores (M€)':<25} | {'Diferencia (M€)':<15} | {'% Var':<10}")
print("-" * 108)

diffs = []
for code, name in sorted(code_to_name.items(), key=lambda x: summed_values.get(x[0], 0.0), reverse=True):
    off_val = official_values.get(code, 0.0)
    sum_val = summed_values.get(code, 0.0)
    diff = sum_val - off_val
    pct = (diff / off_val * 100) if off_val > 0 else 0.0
    diffs.append((code, name, off_val, sum_val, diff, pct))
    print(f"{name:<23} ({code}) | {off_val:>18.1f} | {sum_val:>23.1f} | {diff:>13.1f} | {pct:>8.1f}%")

print("\n--- RESUMEN GENERAL DE CAMBIOS ---")
avg_off = sum(off for _, _, off, _, _, _ in diffs) / len(diffs)
avg_sum = sum(s for _, _, _, s, _, _ in diffs) / len(diffs)
print(f"Valor Promedio según Ranking FIFA: {avg_off:.1f} M€")
print(f"Valor Promedio según Suma de Jugadores: {avg_sum:.1f} M€")

conn.close()
