# Sistema de Recomendación de Partidos - Mundial 2026

## 🚀 ¿Cómo ejecutar la aplicación?

1. **Levantar el servidor web de la aplicación**:
   Abre tu terminal en la raíz del proyecto y ejecuta el servidor web estático de Python:
   ```powershell
   python -m http.server 8080
   ```
   Abre tu navegador e ingresa a: **`http://localhost:8080/frontend/`**

2. **Asegurar que la API local de Transfermarkt esté corriendo** (necesaria para `populate_data.py` y `enrich_with_golden_dataset.py` al rescatar jugadores sin valor):
   ```powershell
   .venv\Scripts\python.exe -m uvicorn app.main:app --port 8000 --host 127.0.0.1
   ```
---

## ⚙️ Pipeline de Ingesta y Enriquecimiento

El sistema cuenta con un pipeline de scripts modulares en Python (`scripts/`) para poblar, enriquecer y exportar los datos del Mundial 2026:

### 1. Ingesta Inicial (`scripts/populate_data.py`)
- Extrae la información de planteles probables actualizados para las 48 selecciones desde Wikipedia.
- Llama a la API local de Transfermarkt en el puerto `8000` para resolver el valor de mercado real, edad oficial y club actual de cada jugador.
- Guarda en `scraped_unresolved_players` los jugadores no vinculados para auditoría posterior y almacena en caché SQLite (`cache_transfermarkt`) las búsquedas exitosas para optimizar ejecuciones futuras.

### 2. Enriquecimiento con Estadísticas Recientes (`scripts/enrich_with_golden_dataset.py`)
- Consume el **Golden Dataset** (`data/worldcup-2026-predicts/fifa_world_cup_2026_golden_dataset.csv`).
- Aplica reglas de coincidencia de nombres avanzada y tolerante para resolver discrepancias ortográficas:
  - **Filtro por Selección**: Mapea y restringe candidatos a la selección nacional del jugador para evitar colisiones internacionales.
  - **Wildcards Regex**: Reemplaza caracteres corruptos de codificación (`?` y `\ufffd`) por comodines (`.`) para emparejamientos exactos.
  - **Mapeo de Apodos (Nicknames)**: Resuelve variantes comunes en español e inglés (ej. *Andy* <-> *Andrew*, *Álex* <-> *Alejandro*).
  - **Similitud Jaccard de Palabras**: Aplica una comparación de tokens con umbral de $\ge 0.49$ como fallback.
  - **Control de Duplicados**: Garantiza que no existan colisiones cuando hay dos jugadores del mismo nombre en una selección (ej. *Danilo* en Brasil).
- Guarda y actualiza las columnas `assists_recent`, `minutes_recent` y `efficiency_score` en la base de datos SQLite y recalcula los promedios globales de eficiencia por país en `scraped_team_metrics`.

### 3. Consolidación y Exportación (`scripts/export_to_json.py`)
- Lee de la base de datos relacional y consolida equipos, planteles, estadios, fixtures y récords H2H históricos en un único archivo JSON en **`data/wc2026_data.json`**. Este archivo es el consumido directamente por el Frontend.

#### Orden de ejecución para actualizar los datos:
```powershell
# 1. Poblar Wikipedia y Transfermarkt
python scripts/populate_data.py

# 2. Enriquecer con el Golden Dataset
python scripts/enrich_with_golden_dataset.py

# 3. Exportar JSON para el Frontend
python scripts/export_to_json.py
```

---

# Diccionario de Datos de la Copa del Mundo (`worldcup_combined.db`) - Versión Simplificada

Este documento detalla la estructura y el propósito de cada una de las **22 tablas** optimizadas en la base de datos unificada [worldcup_combined.db](file:///c:/Users/tomas/Desktop/proyectos/worldcup-app/data/worldcup_combined.db). Hemos eliminado 23 tablas de ruido analítico para facilitar el desarrollo del recomendador de partidos, manteniendo los planteles e historiales de tarjetas de los jugadores.

## Indice de Categorías
- [Mundial 2026 (wc2026_)](#mundial-2026-wc2026)
- [Resultados Internacionales (intl_)](#resultados-internacionales-intl)
- [Scraping y Auxiliares (scraped_ y team_mappings)](#scraping-y-auxiliares-scraped-y-teammappings)
- [Histórico de Mundiales (Fjelstul - 1930 a 2022)](#histórico-de-mundiales-fjelstul---1930-a-2022)

---

## Mundial 2026 (wc2026_)

### Tabla `wc2026_host_cities`
**Descripción**: Datos de las 16 ciudades anfitrionas del 2026, estadios, región (Este, Central, Oeste) y aeropuertos.

**Esquema de Columnas**:

| Columna | Tipo | Clave | Restricciones |
| :--- | :--- | :--- | :--- |
| `id` | INT |  |  |
| `city_name` | TEXT |  |  |
| `country` | TEXT |  |  |
| `venue_name` | TEXT |  |  |
| `region_cluster` | TEXT |  |  |
| `airport_code` | TEXT |  |  |

### Tabla `wc2026_matches`
**Descripción**: El calendario oficial de los 104 partidos del Mundial 2026, con fechas, horarios, sedes y equipos asignados.

**Esquema de Columnas**:

| Columna | Tipo | Clave | Restricciones |
| :--- | :--- | :--- | :--- |
| `id` | INT |  |  |
| `match_number` | INT |  |  |
| `home_team_id` | INT |  |  |
| `away_team_id` | INT |  |  |
| `city_id` | INT |  |  |
| `stage_id` | INT |  |  |
| `kickoff_at` | TEXT |  |  |
| `match_label` | TEXT |  |  |

### Tabla `wc2026_teams`
**Descripción**: Las 48 selecciones participantes (o placeholders de playoffs) y su asignación a los grupos A-L.

**Esquema de Columnas**:

| Columna | Tipo | Clave | Restricciones |
| :--- | :--- | :--- | :--- |
| `id` | INT |  |  |
| `team_name` | TEXT |  |  |
| `fifa_code` | TEXT |  |  |
| `group_letter` | TEXT |  |  |
| `is_placeholder` | INT |  |  |

### Tabla `wc2026_tournament_stages`
**Descripción**: Fases y orden cronológico de las etapas del Mundial 2026 (1: Grupos a 7: Final).

**Esquema de Columnas**:

| Columna | Tipo | Clave | Restricciones |
| :--- | :--- | :--- | :--- |
| `id` | INT |  |  |
| `stage_name` | TEXT |  |  |
| `stage_order` | INT |  |  |


---

## Resultados Internacionales (intl_)

### Tabla `intl_results`
**Descripción**: Historial de más de 49,000 partidos internacionales jugados en todo el mundo desde 1872 hasta 2026 (útil para rachas y H2H).

**Esquema de Columnas**:

| Columna | Tipo | Clave | Restricciones |
| :--- | :--- | :--- | :--- |
| `date` | TEXT |  |  |
| `home_team` | TEXT |  |  |
| `away_team` | TEXT |  |  |
| `home_score` | REAL |  |  |
| `away_score` | REAL |  |  |
| `tournament` | TEXT |  |  |
| `city` | TEXT |  |  |
| `country` | TEXT |  |  |
| `neutral` | INTEGER |  |  |

---

## Scraping y Auxiliares (scraped_ y team_mappings)

### Tabla `scraped_team_metrics`
**Descripción**: Métricas de rendimiento reciente (xG, posesión, pases progresivos y calificación de Sofascore promediados del plantel), valor de mercado total de la selección y popularidad global por selección para el Mundial 2026.

**Esquema de Columnas**:

| Columna | Tipo | Clave | Restricciones |
| :--- | :--- | :--- | :--- |
| `fifa_code` | TEXT | 🔑 PK | FOREIGN KEY -> wc2026_teams (fifa_code) |
| `market_value_eur` | REAL |  | Suma de valores de mercado de los jugadores probables convocados (en M€) |
| `recent_xg_avg` | REAL |  | Goles esperados promedio por partido recientes (basado en mundial 2022 o ranking) |
| `recent_possession_avg` | REAL |  | Porcentaje de posesión promedio reciente de la selección |
| `global_popularity_score` | REAL |  | Índice de popularidad global (0 a 100) según el interés global |
| `progressive_passes_per_90_avg` | REAL |  | Promedio de pases progresivos por 90 minutos de los jugadores del plantel |
| `sofascore_rating_avg` | REAL |  | Calificación de Sofascore promedio de la temporada para la selección |
| `cards_per_match_avg` | REAL |  | Promedio histórico de tarjetas amarillas/rojas recibidas por partido en mundiales |
| `efficiency_score_avg` | REAL |  | Promedio de la puntuación de eficiencia de rendimiento reciente de los jugadores de la selección |


### Tabla `scraped_wc2026_probable_squads`
**Descripción**: Plantel de jugadores probables convocados para el Mundial 2026 (extraídos de Wikipedia y cruzados con Transfermarkt API local), incluyendo club, edad, estadísticas en selección (PJ, goles), valor de mercado, lesión, condición de estrella y métricas avanzadas enriquecidas. Si un jugador no pudo ser resuelto por Transfermarkt, sus campos de mercado y estadísticas avanzadas se almacenan como `NULL`.

**Esquema de Columnas**:

| Columna | Tipo | Clave | Restricciones |
| :--- | :--- | :--- | :--- |
| `player_id` | INTEGER | 🔑 PK | AUTOINCREMENT |
| `player_name` | TEXT |  | Nombre del jugador en Wikipedia |
| `fifa_code` | TEXT |  | FOREIGN KEY -> wc2026_teams (fifa_code) |
| `position` | TEXT |  | Posición limpia del jugador (Portero, Defensa, Centrocampista, Delantero) |
| `club` | TEXT |  | Club actual del jugador (actualizado vía Transfermarkt o Wikipedia) |
| `age` | INTEGER |  | Edad actual del jugador |
| `caps` | INTEGER |  | Partidos internacionales disputados con su selección |
| `goals` | INTEGER |  | Goles anotados con su selección |
| `market_value_eur` | REAL |  | Valor de mercado real en millones de euros (M€) |
| `is_star_player` | BOOLEAN |  | Verdadero si el jugador está en el cuartil superior (Q75) de valor en su selección |
| `is_injured` | BOOLEAN |  | Verdadero si presenta lesiones de último momento o baja médica |
| `progressive_passes_per_90` | REAL |  | Pases progresivos completados por 90 minutos (proxy de estilo de juego de FBref) |
| `sofascore_rating` | REAL |  | Calificación promedio del jugador en Sofascore durante la última temporada |
| `cards_propensity` | REAL |  | Índice de propensión a recibir tarjetas por 90 minutos (basado en caché de FBref/historial) |
| `assists_recent` | INTEGER |  | Cantidad de asistencias en partidos recientes (del Golden Dataset) |
| `minutes_recent` | INTEGER |  | Minutos jugados en partidos recientes (del Golden Dataset) |
| `efficiency_score` | REAL |  | Puntuación de eficiencia de rendimiento reciente (del Golden Dataset) |


### Tabla `scraped_unresolved_players`
**Descripción**: Registro de integridad de datos que almacena los jugadores de Wikipedia que no pudieron ser vinculados en la API local de Transfermarkt tras aplicar filtros estrictos de coincidencia por nacionalidad, nombre y rango de edad. Permite auditar y resolver discrepancias de nombres.

**Esquema de Columnas**:

| Columna | Tipo | Clave | Restricciones |
| :--- | :--- | :--- | :--- |
| `player_id` | INTEGER | 🔑 PK | AUTOINCREMENT |
| `player_name` | TEXT |  | Nombre del jugador en Wikipedia |
| `fifa_code` | TEXT |  | FOREIGN KEY -> wc2026_teams (fifa_code) |
| `position` | TEXT |  | Posición en Wikipedia |
| `club` | TEXT |  | Club en Wikipedia |
| `age` | INTEGER |  | Edad estimada en Wikipedia |
| `caps` | INTEGER |  | Partidos jugados |
| `goals` | INTEGER |  | Goles marcados |
| `reason_unresolved` | TEXT |  | Motivo por el cual no se resolvió (ej. error de conexión, sin candidatos, etc.) |
| `resolved` | BOOLEAN |  | Indicador de estado (por defecto 0) para resolución manual posterior |

### Tabla `cache_transfermarkt`
**Descripción**: Caché local persistente de respuestas JSON de la API local de Transfermarkt para acelerar el pipeline y evitar peticiones repetidas sobre los mismos nombres de jugadores en ejecuciones subsecuentes.

**Esquema de Columnas**:

| Columna | Tipo | Clave | Restricciones |
| :--- | :--- | :--- | :--- |
| `query` | TEXT | 🔑 PK | Nombre buscado en el endpoint |
| `response_json` | TEXT |  | Respuesta completa de la API en formato JSON serializado |
| `timestamp` | DATETIME |  | Fecha y hora de almacenamiento (por defecto `CURRENT_TIMESTAMP`) |

### Tabla `team_mappings`
**Descripción**: Tabla auxiliar de resolución que vincula los nombres de las selecciones de 2026 con sus equivalentes históricos y generales.

**Esquema de Columnas**:

| Columna | Tipo | Clave | Restricciones |
| :--- | :--- | :--- | :--- |
| `fifa_code` | TEXT | 🔑 PK |  |
| `wc2026_name` | TEXT |  |  |
| `historical_name` | TEXT |  |  |
| `intl_results_name` | TEXT |  |  |


---

## Histórico de Mundiales (Fjelstul - 1930 a 2022)

### Tabla `bookings`
**Descripción**: Tarjetas amarillas y rojas mostradas en la historia de los mundiales (útil para fricción/intensidad).

**Esquema de Columnas**:

| Columna | Tipo | Clave | Restricciones |
| :--- | :--- | :--- | :--- |
| `booking_id` | TEXT | 🔑 PK | NOT NULL |
| `tournament_id` | TEXT |  | NOT NULL |
| `match_id` | TEXT |  | NOT NULL |
| `team_id` | TEXT |  | NOT NULL |
| `home_team` | BOOLEAN |  |  |
| `away_team` | BOOLEAN |  |  |
| `player_id` | TEXT |  | NOT NULL |
| `shirt_number` | INTEGER |  |  |
| `minute_label` | TEXT |  |  |
| `minute_regulation` | INTEGER |  |  |
| `minute_stoppage` | INTEGER |  |  |
| `match_period` | TEXT |  |  |
| `yellow_card` | BOOLEAN |  |  |
| `red_card` | BOOLEAN |  |  |
| `second_yellow_card` | BOOLEAN |  |  |
| `sending_off` | BOOLEAN |  |  |


### Tabla `matches`
**Descripción**: Sin descripción.

**Esquema de Columnas**:

| Columna | Tipo | Clave | Restricciones |
| :--- | :--- | :--- | :--- |
| `tournament_id` | TEXT |  | NOT NULL |
| `match_id` | TEXT | 🔑 PK | NOT NULL |
| `match_name` | TEXT |  |  |
| `stage_name` | TEXT |  |  |
| `group_name` | TEXT |  |  |
| `group_stage` | BOOLEAN |  |  |
| `knockout_stage` | BOOLEAN |  |  |
| `replayed` | BOOLEAN |  |  |
| `replay` | BOOLEAN |  |  |
| `match_date` | TEXT |  |  |
| `match_time` | TEXT |  |  |
| `stadium_id` | TEXT |  | NOT NULL |
| `home_team_id` | TEXT |  | NOT NULL |
| `away_team_id` | TEXT |  | NOT NULL |
| `score` | TEXT |  |  |
| `home_team_score` | INTEGER |  |  |
| `away_team_score` | INTEGER |  |  |
| `home_team_score_margin` | INTEGER |  |  |
| `away_team_score_margin` | INTEGER |  |  |
| `extra_time` | BOOLEAN |  |  |
| `penalty_shootout` | BOOLEAN |  |  |
| `score_penalties` | TEXT |  |  |
| `home_team_score_penalties` | INTEGER |  |  |
| `away_team_score_penalties` | INTEGER |  |  |
| `result` | TEXT |  |  |
| `home_team_win` | BOOLEAN |  |  |
| `away_team_win` | BOOLEAN |  |  |
| `draw` | BOOLEAN |  |  |

### Tabla `player_appearances`
**Descripción**: Detalle de la participación de cada jugador en un partido (titular, suplente, capitán).

**Esquema de Columnas**:

| Columna | Tipo | Clave | Restricciones |
| :--- | :--- | :--- | :--- |
| `tournament_id` | TEXT | 🔑 PK | NOT NULL |
| `match_id` | TEXT | 🔑 PK | NOT NULL |
| `team_id` | TEXT | 🔑 PK | NOT NULL |
| `home_team` | BOOLEAN |  |  |
| `away_team` | BOOLEAN |  |  |
| `player_id` | TEXT | 🔑 PK | NOT NULL |
| `shirt_number` | INTEGER |  |  |
| `position_name` | TEXT |  |  |
| `position_code` | TEXT |  |  |
| `starter` | BOOLEAN |  |  |
| `substitute` | BOOLEAN |  |  |
| `captain` | BOOLEAN |  |  |

### Tabla `players`
**Descripción**: Detalle de los 8,485 jugadores históricos, incluyendo fecha de nacimiento, posición y enlaces.

**Esquema de Columnas**:

| Columna | Tipo | Clave | Restricciones |
| :--- | :--- | :--- | :--- |
| `player_id` | TEXT | 🔑 PK | NOT NULL |
| `family_name` | TEXT |  |  |
| `given_name` | TEXT |  |  |
| `birth_date` | DATE |  |  |
| `goal_keeper` | BOOLEAN |  |  |
| `defender` | BOOLEAN |  |  |
| `midfielder` | BOOLEAN |  |  |
| `forward` | BOOLEAN |  |  |
| `count_tournaments` | INTEGER |  |  |
| `list_tournaments` | TEXT |  |  |
| `player_wikipedia_link` | TEXT |  |  |



### Tabla `teams`
**Descripción**: Registro de las 85 selecciones históricas que han participado en mundiales con sus federaciones.

**Esquema de Columnas**:

| Columna | Tipo | Clave | Restricciones |
| :--- | :--- | :--- | :--- |
| `team_id` | TEXT | 🔑 PK | NOT NULL |
| `team_name` | TEXT |  |  |
| `team_code` | TEXT |  |  |
| `federation_name` | TEXT |  |  |
| `region_name` | TEXT |  |  |
| `confederation_id` | TEXT |  | NOT NULL |
| `team_wikipedia_link` | TEXT |  |  |
| `federation_wikipedia_link` | TEXT |  |  |




---

