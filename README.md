# Guía de Ejecución y Datos del Recomendador - Mundial 2026

Esta guía describe los pasos para ejecutar la aplicación localmente, las bases de datos efectivamente utilizadas por el motor del recomendador y el orden secuencial de ejecución de los scripts para actualizar el sistema.

---

## 🚀 Cómo ejecutar la aplicación en local

### 1. Servidor Web del Frontend
Abre una terminal en la raíz del proyecto y levanta el servidor web local para servir los archivos estáticos:
```powershell
python -m http.server 8000
```
Luego, abre tu navegador e ingresa a:  
👉 **`http://localhost:8000/frontend/`**

---

### 2. API Local de Transfermarkt (Opcional)
La aplicación y el pipeline pueden interactuar con un servicio local de scraping para resolver información sobre nuevos jugadores. Para levantarlo:
```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --port 8001 --host 127.0.0.1
```
*Nota: Para evadir bloqueos por firewall/WAF de Transfermarkt, el pipeline consulta prioritariamente la base de caché SQLite (`cache_transfermarkt`) que ya cuenta con **más de 1680 registros** de jugadores resueltos.*

---

## 📊 Fuentes de Datos Utilizadas Efectivamente

El recomendador basa sus cálculos únicamente en las siguientes fuentes de datos reales:

1. **API y Caché de Transfermarkt**: Valores de mercado, edad, club oficial, partidos internacionales, goles y propensión a tarjetas para cada jugador.
2. **Datos de Sofifa (Archivos .txt)**: Atributos detallados por jugador extraídos de Sofifa y procesados por macro-posición (Porteros, Centrales, Laterales, Mediocampistas, Delanteros y Extremos) para el análisis de estilos de juego.
3. **FBref (Eliminatorias y Copa Oro)**: Datos históricos de rendimiento en las Eliminatorias Mundiales (CONMEBOL, UEFA, CAF, etc.) y torneos continentales (CONCACAF Gold Cup/Nations League) utilizados para el cálculo de la dificultad de torneos regionales ($C_{dif}$).
4. **Historial Completo de Partidos Internacionales (`intl_results`)**: Base de datos de más de 49,000 partidos jugados desde 1872 hasta 2026. Utilizada para calcular rachas recientes, historial de enfrentamientos directos (H2H) e índices de dificultad.
5. **Base de Datos de EA FC 26**: Atributos técnicos, físicos y de comportamiento de los jugadores en actividad (pace, shooting, passing, dribbling, defending, physic) obtenidos a partir de `FC26_20250921.csv`.
6. **CSVs del Mundial 2026 (Directorio `data/mundial-2026/`)**:
   * `host_cities.csv`: Datos de las 16 sedes, clusters de región (Este, Central, Oeste) y aeropuertos.
   * `matches.csv`: Calendario oficial estructurado de los 104 partidos.
   * `teams.csv`: Las 48 selecciones participantes y su asignación a los grupos (A-L).
   * `tournament_stages.csv`: Fases del torneo (desde fase de grupos hasta la gran final).
7. **Lista de Convocados Manual (`Lista de Convocados.md`)**: Archivo de texto en markdown que actúa como la fuente de verdad definitiva para marcar planteles confirmados de selecciones y catalogar manualmente a los jugadores estrella de cada país.

---

## ⚙️ Pipeline de Ejecución de Scripts

Para regenerar, enriquecer y exportar la base de datos completa del recomendador, ejecuta los scripts en el siguiente orden estricto:

### Bloque A: Ingesta y Consolidación de Datos
1. **Creación de la base unificada**:
   ```powershell
   python scripts/build_database.py
   ```
   *Inicializa y estructura `worldcup_combined.db` e importa fixtures, sedes, selecciones y fases.*

2. **Ingesta y matching de planteles**:
   ```powershell
   python scripts/populate_data.py
   ```
   *Puebla los planteles estimados desde Wikipedia y busca información detallada usando la API/Caché de Transfermarkt.*

3. **Procesar convocatorias oficiales**:
   ```powershell
   python scripts/parse_convocados.py
   ```
   *Actualiza la base de datos a partir del archivo markdown manual de convocados confirmados y define los jugadores estrella.*

4. **Estadísticas de selecciones**:
   ```powershell
   python scripts/enrich_team_stats.py
   ```
   *Calcula el rendimiento reciente (goles, xG, posesión) analizando el histórico de partidos internacionales.*

5. **Cálculo de puntuación de espectáculo y dificultad ($C_{dif}$)**:
   ```powershell
   python scripts/calculate_score_espectaculo.py
   ```
   *Procesa datos de Sofascore y FIFA rankings, aplica ponderaciones de dificultad regional e inyecta los coeficientes de espectáculo normalizados.*

6. **Actualizar vectores tácticos**:
   ```powershell
   python scripts/update_tactical_vectors.py
   ```
   *Calcula y actualiza los vectores de estilo de juego de cada selección.*

7. **Exportar JSON para el Frontend**:
   ```powershell
   python scripts/export_to_json.py
   ```
   *Exporta el JSON consolidado `frontend/data/wc2026_data.json` que consume directamente la interfaz de usuario.*

---

### Bloque B: Modelo de Clustering y Similitud de Jugadores
Si deseas recalcular los clusters de afinidad de jugadores (K-Means y Jerárquico) para las recomendaciones basadas en futbolistas favoritos:

8. **Cálculo de clusters de estilo**:
   ```powershell
   python scripts/recommender/HAC_clustering.py
   ```
   *Agrupa a los jugadores de EA FC 26 en clusters por macro-posición y guarda los centroides en `data/clustering_maps/`.*

9. **Asignación de convocados a centroides**:
   ```powershell
   python scripts/recommender/assign_players_to_centroids.py
   ```
   *Filtra a los jugadores activos del mundial con respecto a la lista de convocados y calcula sus distancias euclidianas a los centroides de estilos.*

10. **Test de afinidad (Opcional)**:
    ```powershell
    python scripts/recommender/score_cluster_players.py --example
    ```
    *Prueba la asignación de puntajes por partido de acuerdo a los clusters de preferencia del usuario.*
