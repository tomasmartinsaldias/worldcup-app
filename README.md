# Sistema de Recomendación de Partidos - Mundial 2026

## 🚀 ¿Cómo ejecutar la aplicación?

1. **Levantar el servidor web de la aplicación**:
   Abre tu terminal en la raíz del proyecto y ejecuta el servidor web estático de Python:
   ```powershell
   python -m http.server 8080
   ```
   Abre tu navegador e ingresa a: **`http://localhost:8080/frontend/`**

2. **🌐 Despliegue Estático (GitHub Pages)**:
   La aplicación está diseñada para ser completamente estática y ejecutarse en el lado del cliente (sin backend activo de Python).
   * **Directorio autocontenido**: Todo el código y los recursos necesarios están dentro de la carpeta `/frontend`. Los archivos de datos se cargan desde `/frontend/data/`.
   * **Despliegue**: Puedes publicar el sitio en GitHub Pages configurando tu repositorio para que publique la carpeta `frontend/` (por ejemplo, mediante una GitHub Action de despliegue a la rama `gh-pages` apuntando al directorio `frontend`).

3. **API local de Transfermarkt y Limitación de Captcha (WAF)**:
   La API local (`transfermarkt-api`) utiliza raspado de datos directo. Sin embargo, las consultas en vivo a Transfermarkt.com suelen ser bloqueadas por el firewall Cloudfront/WAF (`405 Method Not Allowed / Captcha`). 
   * **Solución**: El pipeline está diseñado para consultar primero la tabla de caché SQLite (`cache_transfermarkt`) que ya cuenta con **más de 1680 registros** listos. Si necesitas levantar el servicio de API local para resolver registros faltantes o nuevos:
     ```powershell
     .venv\Scripts\python.exe -m uvicorn app.main:app --port 8000 --host 127.0.0.1
     ```

---

## ⚙️ Pipeline de Ingesta y Enriquecimiento

El sistema cuenta con un pipeline robusto de scripts modulares en Python y R (`scripts/`) para estructurar, poblar, enriquecer y exportar los datos del Mundial 2026:

### 1. Inicialización de Base de Datos (`scripts/build_database.py`)
- Crea y estructura la base de datos SQLite unificada `worldcup_combined.db`.
- Importa el fixture de partidos del Mundial 2026, ciudades sede y configuraciones iniciales.

### 2. Ingesta Inicial (`scripts/populate_data.py`)
- Extrae la información de planteles probables actualizados para las 48 selecciones desde Wikipedia.
- Llama a la API local de Transfermarkt en el puerto `8000` (usando el caché local prioritariamente para evadir el bloqueo de WAF) para resolver el valor de mercado real, edad oficial y club actual de cada jugador.
- Guarda en `scraped_unresolved_players` los jugadores no vinculados para auditoría posterior.

### 3. Procesamiento de Convocados Confirmados (`scripts/parse_convocados.py`)
- Toma como fuente de verdad el archivo [Lista de Convocados.md](file:///c:/Users/tomas/Desktop/proyectos/worldcup-app/Lista%20de%20Convocados.md).
- Si la selección tiene estado **Confirmada**, marca `is_confirmed_squad = 1`, limpia los planteles de Wikipedia eliminando jugadores ficticios u omitidos, actualiza clubes y posiciones oficiales, e inserta a los nuevos convocados.
- Si está **Sin confirmar**, marca `is_confirmed_squad = 0` y conserva el plantel probable.
- Identifica y marca jugadores estrella (`is_star_player = 1`) cruzando la sección de "Destacados" del markdown, una lista interna de superestrellas globales, y el percentil 75 de valor de mercado en su país.

### 4. Métricas de Rendimiento Reciente de Selecciones (`scripts/enrich_team_stats.py`)
- Analiza el historial completo de partidos internacionales en la tabla `intl_results`.
- Calcula y actualiza las métricas agregadas por selección en `scraped_team_metrics`.

### 5. Actualización de Vectores Tácticos (`scripts/update_tactical_vectors.py`)
- Calcula los perfiles de estilo de juego de cada selección cruzando datos SofaScore y ELO.
- Guarda los vectores resultantes en `data/estilos-de-juego/selecciones_estilo` y en la ruta de producción del frontend.

### 6. Consolidación y Exportación (`scripts/export_to_json.py`)
- Lee de la base de datos relacional compacta y consolida equipos, planteles con sus estadísticas, estadios, fixtures y récords H2H históricos en un único archivo JSON unificado en **`frontend/data/wc2026_data.json`**. Este archivo es el consumido directamente por el Frontend.

#### Orden de ejecución del pipeline completo para actualizar los datos:
```powershell
# 1. Crear estructura e importar fixtures
python scripts/build_database.py

# 2. Poblar Wikipedia y valores de mercado desde Transfermarkt
python scripts/populate_data.py

# 3. Aplicar las plantillas oficiales del archivo de Convocados
python scripts/parse_convocados.py

# 4. Calcular métricas de selecciones (goles, posesión, xG promedio, etc.)
python scripts/enrich_team_stats.py

# 5. Calcular vectores tácticos y estilos de juego de selecciones
python scripts/update_tactical_vectors.py

# 6. Exportar JSON consolidado para el Frontend
python scripts/export_to_json.py
```

---

# Diccionario de Datos de la Copa del Mundo (`worldcup_combined.db`) - Versión Simplificada

Este documento detalla la estructura y el propósito de cada una de las **16 tablas** optimizadas en la base de datos unificada [worldcup_combined.db](file:///c:/Users/tomas/Desktop/proyectos/worldcup-app/data/worldcup_combined.db). Hemos eliminado 23 tablas de ruido analítico para facilitar el desarrollo del recomendador de partidos, manteniendo los planteles e historiales de tarjetas de los jugadores.

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
| `is_confirmed_squad` | INT |  | Indica si el plantel fue oficialmente confirmado a partir de la fuente de verdad (1) o sigue siendo un plantel estimado de Wikipedia (0) |

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
**Descripción**: Métricas agregadas y de rendimiento reciente de cada selección.

**Esquema de Columnas**:

| Columna | Tipo | Clave | Restricciones |
| :--- | :--- | :--- | :--- |
| `fifa_code` | TEXT | 🔑 PK | FOREIGN KEY -> wc2026_teams (fifa_code) |
| `market_value_eur` | REAL |  | Suma de valores de mercado de los jugadores convocados (en M€) |
| `recent_xg_avg` | REAL |  | Goles esperados promedio por partido recientes |
| `recent_possession_avg` | REAL |  | Porcentaje de posesión promedio reciente de la selección |
| `global_popularity_score` | REAL |  | Índice de popularidad global (0 a 100) |
| `progressive_passes_per_90_avg` | REAL |  | Promedio de pases progresivos por 90 minutos de la selección |
| `sofascore_rating_avg` | REAL |  | Promedio de rating general de SofaScore de los jugadores |
| `cards_per_match_avg` | REAL |  | Promedio de tarjetas amarillas/rojas recibidas por partido |


### Tabla `scraped_wc2026_probable_squads`
**Descripción**: Plantel de jugadores convocados o probables con sus métricas.

**Esquema de Columnas**:

| Columna | Tipo | Clave | Restricciones |
| :--- | :--- | :--- | :--- |
| `player_id` | INTEGER | 🔑 PK | AUTOINCREMENT |
| `player_name` | TEXT |  | Nombre del jugador |
| `fifa_code` | TEXT |  | FOREIGN KEY -> wc2026_teams (fifa_code) |
| `position` | TEXT |  | Posición limpia (Portero, Defensa, Centrocampista, Delantero) |
| `club` | TEXT |  | Club actual del jugador |
| `age` | INTEGER |  | Edad actual del jugador |
| `caps` | INTEGER |  | Partidos internacionales disputados |
| `goals` | INTEGER |  | Goles internacionales anotados |
| `market_value_eur` | REAL |  | Valor de mercado en millones de euros (M€) |
| `is_star_player` | BOOLEAN |  | Verdadero si es considerado jugador estrella en su selección |
| `is_injured` | BOOLEAN |  | Verdadero si presenta lesiones o baja médica |
| `progressive_passes_per_90` | REAL |  | Promedio de pases progresivos por 90 minutos |
| `sofascore_rating` | REAL |  | Rating promedio de SofaScore |
| `cards_propensity` | REAL |  | Índice de propensión a recibir tarjetas |
| `assists_recent` | INTEGER |  | Asistencias en partidos recientes |
| `minutes_recent` | INTEGER |  | Minutos jugados recientes |


### Tabla `scraped_unresolved_players`
**Descripción**: Registro de jugadores que no pudieron ser vinculados en la API local de Transfermarkt.

**Esquema de Columnas**:

| Columna | Tipo | Clave | Restricciones |
| :--- | :--- | :--- | :--- |
| `player_id` | INTEGER | 🔑 PK | AUTOINCREMENT |
| `player_name` | TEXT |  | Nombre del jugador |
| `fifa_code` | TEXT |  | FOREIGN KEY -> wc2026_teams (fifa_code) |
| `position` | TEXT |  | Posición del jugador |
| `club` | TEXT |  | Club del jugador |
| `age` | INTEGER |  | Edad del jugador |
| `caps` | INTEGER |  | Partidos jugados |
| `goals` | INTEGER |  | Goles marcados |
| `reason_unresolved` | TEXT |  | Motivo del fallo de coincidencia |
| `resolved` | BOOLEAN |  | Estado de resolución manual (1 si resuelto, 0 si no) |
| `alternative_names` | TEXT |  | Nombres alternativos candidatos encontrados en formato JSON |

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

