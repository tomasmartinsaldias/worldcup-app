# Sistema de Recomendación de Partidos del Mundial

**Versión:** 1.0  
**Fecha:** Mayo 2026  
**Ubicación base:** `scripts/recommender/` y `data/player_similarity/`

---

## Índice

1. [Visión General](#visión-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Scripts y Módulos](#scripts-y-módulos)
   - [player_similarity.py](#1-player_similaritypy)
   - [recommend_similar_players.py](#2-recommend_similar_playerspy)
   - [parse_convocados.py](#3-parse_convocadospy)
   - [recommend_matches_by_players.py](#4-recommend_matches_by_playerspy)
   - [recommend_matches_by_team.py](#5-recommend_matches_by_teampy)
4. [Flujo de Datos](#flujo-de-datos)
5. [Fundamento Matemático](#fundamento-matemático)
6. [Dependencias](#dependencias)

---

## Visión General

El sistema está compuesto por dos motores de recomendación independientes que le permiten al usuario descubrir qué partidos del Mundial son más interesantes para él, según dos tipos distintos de preferencia:

| Motor | Entrada del usuario | Lógica |
|---|---|---|
| `recommend_matches_by_players.py` | Un **jugador favorito** | Busca jugadores similares por estadísticas y asigna score según cuántos de ellos juegan en cada partido |
| `recommend_matches_by_team.py` | Un **club favorito** | Asigna score según la proporción de jugadores de ese club que están convocados en cada selección |

Ambos motores devuelven una lista de partidos ordenados de mayor a menor score, normalizado en el rango `[0, 1]`.

---

## Arquitectura del Sistema

```
data/
├── player_similarity/
│   ├── FC26_20250921.csv                  ← Base de datos de jugadores (EA FC 26)
│   ├── player_similarity.py               ← Genera el JSON filtrado
│   └── player_similarity_codebase.json    ← JSON de atributos para cálculo de similitud
│
└── recommender_data/
    └── convocados.db                      ← Base de datos SQLite de convocados al Mundial

scripts/
└── recommender/
    ├── recommend_similar_players.py       ← Módulo: encuentra jugadores similares (distancia coseno)
    ├── parse_convocados.py                ← Módulo: parsea el .md de convocados y crea la DB
    ├── recommend_matches_by_players.py    ← Motor 1: recomendación por jugador favorito
    └── recommend_matches_by_team.py       ← Motor 2: recomendación por club favorito

Lista de Convocados.md                     ← Fuente de datos de convocatorias mundialistas
```

---

## Scripts y Módulos

---

### 1. `player_similarity.py`

**Ruta:** `data/player_similarity/player_similarity.py`  
**Tipo:** Script de preparación de datos (se ejecuta una vez)

#### Propósito
Lee el CSV completo de EA FC 26 (`FC26_20250921.csv`) y exporta un subconjunto de columnas relevantes a un archivo JSON. Este JSON es la fuente de datos que consumen los módulos de similitud de jugadores.

#### Funcionamiento

1. Lee el CSV completo con `pandas`.
2. Selecciona un subconjunto de **43 columnas** de atributos del jugador.
3. Exporta el DataFrame filtrado a JSON en formato `records`.

#### Columnas exportadas

| Categoría | Columnas |
|---|---|
| Identificación | `short_name`, `nationality_name` |
| Generales | `overall`, `potential`, `age`, `height_cm`, `weight_kg`, `skill_moves` |
| Físico | `pace`, `passing`, `shooting`, `dribbling`, `defending`, `physic` |
| Ataque | `attacking_crossing`, `attacking_finishing`, `attacking_heading_accuracy`, `attacking_short_passing`, `attacking_volleys` |
| Habilidad | `skill_dribbling`, `skill_curve`, `skill_fk_accuracy`, `skill_long_passing`, `skill_ball_control` |
| Movimiento | `movement_acceleration`, `movement_sprint_speed`, `movement_agility`, `movement_reactions`, `movement_balance` |
| Potencia | `power_shot_power`, `power_jumping`, `power_stamina`, `power_strength`, `power_long_shots` |
| Mentalidad | `mentality_aggression`, `mentality_interceptions`, `mentality_positioning`, `mentality_vision`, `mentality_penalties`, `mentality_composure` |
| Defensa | `defending_marking_awareness`, `defending_standing_tackle`, `defending_sliding_tackle` |

#### Ejecución

```bash
# Desde la raíz del proyecto
python data/player_similarity/player_similarity.py
```

#### Salida
- Archivo: `data/player_similarity/player_similarity_codebase.json`
- Formato: Array JSON de objetos, uno por jugador.

```json
[
  {
    "short_name": "L. Messi",
    "nationality_name": "Argentina",
    "overall": 91,
    "pace": 81,
    ...
  },
  ...
]
```

---

### 2. `recommend_similar_players.py`

**Ruta:** `scripts/recommender/recommend_similar_players.py`  
**Tipo:** Módulo de utilidad (importado por otros scripts)

#### Propósito
Dada la colección de atributos de jugadores, calcula la **distancia coseno** entre un jugador objetivo y todos los demás, devolviendo los `k` más similares.

#### Funciones

---

##### `load_data(json_path) → pd.DataFrame`

Carga el archivo JSON de similitud y lo retorna como un DataFrame de pandas.

| Parámetro | Tipo | Descripción |
|---|---|---|
| `json_path` | `str` | Ruta absoluta al archivo `player_similarity_codebase.json` |

**Errores:** Lanza `FileNotFoundError` si el archivo no existe.

---

##### `get_similar_players(player_name, k, json_path=None) → list[dict] | dict`

Encuentra los `k` jugadores más similares a un jugador dado.

| Parámetro | Tipo | Descripción |
|---|---|---|
| `player_name` | `str` | Nombre corto del jugador (ej: `"L. Messi"`, `"Lamine Yamal"`) |
| `k` | `int` | Cantidad de jugadores similares a devolver |
| `json_path` | `str` (opcional) | Ruta al JSON; si es `None`, usa la ruta por defecto del proyecto |

**Retorna:**
- En caso de éxito: lista de `k` diccionarios con todos los atributos del jugador, más la columna `distance` (distancia coseno al jugador buscado).
- En caso de error: `{"error": "mensaje"}`.

**Algoritmo interno:**

1. **Búsqueda del jugador:** Filtra por `short_name` (insensible a mayúsculas). Si hay duplicados de nombre, los toma a todos como "objetivo".
2. **Selección de features:** Toma las 41 columnas numéricas definidas (excluyendo `short_name` y `nationality_name`).
3. **Normalización:** Aplica `StandardScaler` (media 0, desvío 1) sobre todas las features para que ningún atributo tenga más peso por su escala.
4. **Cálculo de distancia coseno:** Usa `sklearn.metrics.pairwise_distances` con `metric='cosine'` entre el jugador(es) objetivo y todos los demás.
5. **Selección de los top-K:** Si había múltiples jugadores con el mismo nombre, toma la distancia mínima a cualquiera de ellos. Excluye al propio jugador buscado del resultado.

```python
# Ejemplo de uso
from scripts.recommender.recommend_similar_players import get_similar_players

similares = get_similar_players("L. Messi", k=5)
# Retorna lista de 5 dicts con atributos + 'distance'
```

> **Nota:** La `distance` coseno está en rango `[0, 2]`. Un valor cercano a `0` indica alta similitud. Para convertir a **similitud coseno**: `similitud = 1 - distance`.

---

### 3. `parse_convocados.py`

**Ruta:** `scripts/recommender/parse_convocados.py`  
**Tipo:** Script ETL (Extract-Transform-Load) — se ejecuta una vez para preparar los datos

#### Propósito
Parsea el archivo Markdown `Lista de Convocados.md` (que contiene los planteles convocados al Mundial por país) y lo transforma en una base de datos SQLite estructurada en `data/recommender_data/convocados.db`.

#### Funciones

---

##### `parse_markdown_and_create_db(md_filepath, db_filepath) → None`

Realiza todo el proceso ETL: lectura del Markdown, parseo, e inserción en SQLite.

| Parámetro | Tipo | Descripción |
|---|---|---|
| `md_filepath` | `str` | Ruta al archivo `Lista de Convocados.md` |
| `db_filepath` | `str` | Ruta de destino para el archivo `.db` SQLite |

**Esquema de la tabla `convocados`:**

```sql
CREATE TABLE convocados (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    pais    TEXT,    -- Nombre del país/selección (ej: "Argentina")
    jugador TEXT,    -- Nombre del jugador (ej: "L. Messi")
    equipo  TEXT     -- Club del jugador (ej: "Inter Miami, USA")
)
```

**Lógica de parseo del Markdown:**

El archivo `.md` tiene la siguiente estructura:
```
Argentina
Porteros: Franco Armani (River Plate), Emiliano Martínez (Aston Villa, ENG)
Defensas: Gonzalo Montiel (Nottingham Forest, ENG) y Cristian Romero (Tottenham, ENG)
```

El script interpreta cada línea así:

| Condición | Acción |
|---|---|
| Línea sin `:` | Se trata como nombre de país → actualiza `current_country` |
| Línea con `:` | Contiene posición y lista de jugadores → parsea jugadores |
| Líneas filtradas | `"Lista de Convocados"`, líneas con `"Grupo"`, `"Sin confirmar"`, `"Destacado"`, líneas con `*` |

**Parseo de jugadores:**
- Usa regex `r'([^\,]+?\s*\([^)]+\))'` para extraer bloques `Nombre (Club)` correctamente, incluso cuando el club tiene comas (ej: `"Arsenal, ENG"`).
- Separa la conjunción `" y "` / `" e "` convirtiéndola a coma antes del split.
- Si el jugador no tiene formato `(Club)`, guarda club como `"Desconocido"`.

> **Importante:** La tabla se limpia (`DELETE FROM convocados`) antes de cada inserción para evitar duplicados al re-ejecutar el script.

**Ejecución:**

```bash
# Desde la raíz del proyecto
python scripts/recommender/parse_convocados.py
```

**Salida esperada:**
```
Base de datos creada exitosamente en: data/recommender_data/convocados.db
```

---

### 4. `recommend_matches_by_players.py`

**Ruta:** `scripts/recommender/recommend_matches_by_players.py`  
**Tipo:** Motor de recomendación — Motor 1

#### Propósito
Recibe una lista de partidos y el nombre de un **jugador favorito** del usuario. Devuelve los partidos ordenados por score de recomendación, basado en cuántos jugadores similares al favorito participan en cada partido y qué tan similares son.

#### Funciones

---

##### `recommend_matches(matches, favorite_player, json_path=None) → list[dict] | dict`

| Parámetro | Tipo | Descripción |
|---|---|---|
| `matches` | `list[tuple[str, str]]` | Lista de partidos como tuplas `(equipo1, equipo2)` |
| `favorite_player` | `str` | Nombre del jugador favorito (ej: `"L. Messi"`) |
| `json_path` | `str` (opcional) | Ruta al JSON de similitud; si es `None`, usa la ruta por defecto |

**Retorna:** Lista de dicts ordenada por `normalized_score` (descendente). En caso de error, retorna `{"error": "..."}`.

**Estructura de cada resultado:**

```python
{
    'match': 'Argentina vs France',
    'team1': 'Argentina',
    'team2': 'France',
    'raw_score': 1.7823,          # Suma de similitudes coseno acumuladas
    'normalized_score': 0.8318,   # Score final en [0, 1]
    'contributing_players': {
        'Argentina': [('L. Messi', 1.0), ('J. Alvarez', 0.821)],
        'France': [('K. Mbappé', 0.743)]
    }
}
```

**Algoritmo paso a paso:**

1. **Obtener similares:** Llama a `get_similar_players(favorite_player, 5)` para obtener los 5 jugadores más similares.
2. **Construir pool de jugadores de interés:**
   - El jugador favorito → similitud = `1.0`
   - Cada jugador similar → similitud = `1 - distance` (distancia coseno convertida a similitud)
3. **Para cada partido:** Itera el pool y suma las similitudes de los jugadores cuya `nationality_name` coincide con `team1` o `team2`.
4. **Score del partido:** `raw_score = team1_score + team2_score`
5. **Normalización:** Aplica `f(x) = 1 - exp(-x)` al `raw_score`.

> **Nota sobre los nombres de selecciones:** Este motor usa la `nationality_name` del JSON de EA FC 26. Los equipos en la lista de partidos deben coincidir exactamente con ese campo (ej: `"Argentina"`, `"France"`, no `"Francia"`).

**Ejemplo de uso:**

```python
from scripts.recommender.recommend_matches_by_players import recommend_matches

partidos = [
    ("Argentina", "France"),
    ("Spain", "Germany"),
    ("Brazil", "Croatia"),
]

resultados = recommend_matches(partidos, "L. Messi")
for r in resultados:
    print(r['match'], "→", r['normalized_score'])
```

---

### 5. `recommend_matches_by_team.py`

**Ruta:** `scripts/recommender/recommend_matches_by_team.py`  
**Tipo:** Motor de recomendación — Motor 2

#### Propósito
Recibe una lista de partidos y el nombre de un **club favorito** del usuario. Devuelve los partidos ordenados por score de recomendación, basado en la proporción de jugadores de ese club que están convocados en los países que juegan cada partido.

Este motor no usa embeddings ni similitud coseno; en cambio, consulta directamente la base de datos SQLite de convocados.

#### Funciones

---

##### `get_country_totals(db_path) → dict[str, int]`

Consulta la DB y retorna un diccionario con el total de jugadores convocados por cada selección.

| Parámetro | Tipo | Descripción |
|---|---|---|
| `db_path` | `str` | Ruta al archivo `convocados.db` |

**Retorna:** `{"Argentina": 26, "España": 26, ...}`

**Query SQL:**
```sql
SELECT pais, COUNT(*) FROM convocados GROUP BY pais
```

---

##### `get_club_players_by_country(db_path, club_name) → dict[str, list[tuple]]`

Busca todos los jugadores convocados que pertenecen al club indicado, agrupados por selección.

| Parámetro | Tipo | Descripción |
|---|---|---|
| `db_path` | `str` | Ruta al archivo `convocados.db` |
| `club_name` | `str` | Nombre del club (ej: `"Real Madrid"`, `"Arsenal"`) |

**Retorna:** `{"España": [("Bellingham", "Real Madrid"), ...], "Francia": [...]}`

**Query SQL:**
```sql
SELECT pais, jugador, equipo FROM convocados WHERE equipo LIKE '%club_name%'
```

> **Importante — Búsqueda flexible:** Se usa `LIKE '%club_name%'` para tolerar variaciones en el nombre del club tal como está guardado en el Markdown (ej: `"Arsenal, ENG"` coincidirá con la búsqueda `"Arsenal"`).

---

##### `recommend_matches_by_team(matches, favorite_club, db_path=None) → list[dict] | dict`

Función principal del motor 2. Calcula el score de cada partido basado en el club favorito.

| Parámetro | Tipo | Descripción |
|---|---|---|
| `matches` | `list[tuple[str, str]]` | Lista de partidos como tuplas `(equipo1, equipo2)` |
| `favorite_club` | `str` | Nombre del club favorito (ej: `"Real Madrid"`) |
| `db_path` | `str` (opcional) | Ruta a `convocados.db`; si es `None`, usa la ruta por defecto del proyecto |

**Retorna:** Lista de dicts ordenada por `normalized_score` (descendente). En caso de error, retorna `{"error": "..."}`.

**Estructura de cada resultado:**

```python
{
    'match': 'España vs Alemania',
    'team1': 'España',
    'team2': 'Alemania',
    'team1_ratio': '5/8',          # jugadores del club en España / total del club en el torneo
    'team2_ratio': '1/8',
    'raw_score': 0.75,             # proporción acumulada
    'normalized_score': 0.9502,    # score final en [0, 1]
    'contributing_players': {
        'España': ['Bellingham (Real Madrid)', 'Vinicius Jr. (Real Madrid)'],
        'Alemania': ['Antonio Rüdiger (Real Madrid)']
    }
}
```

**Algoritmo paso a paso:**

1. **Cargar totales:** `get_country_totals()` → total de convocados por selección.
2. **Buscar jugadores del club:** `get_club_players_by_country()` → jugadores del club agrupados por selección.
3. **Error si no hay datos:** Si no se encontraron jugadores del club, retorna error.
4. **Para cada partido:**
   - `team1_count` = cantidad de jugadores del club en equipo 1
   - `team2_count` = cantidad de jugadores del club en equipo 2
   - `total_club_players` = total de jugadores del club en **todo** el torneo (denominador compartido)
   - `t1_prop = team1_count / total_club_players`
   - `t2_prop = team2_count / total_club_players`
   - `raw_score = t1_prop + t2_prop`
5. **Normalización:** `normalized_score = 1 - exp(-4 * raw_score)`

> **Nota sobre los nombres de selecciones:** Este motor usa los nombres tal como están en la DB de convocados (generalmente en español, ej: `"España"`, `"Alemania"`). Deben coincidir exactamente.

**Ejemplo de uso:**

```python
from scripts.recommender.recommend_matches_by_team import recommend_matches_by_team

partidos = [
    ("España", "Alemania"),
    ("Inglaterra", "Francia"),
    ("Brasil", "Croacia"),
]

resultados = recommend_matches_by_team(partidos, "Real Madrid")
for r in resultados:
    print(r['match'], "→", r['normalized_score'])
    print("  Jugadores:", r['contributing_players'])
```

---

## Flujo de Datos

### Preparación (una vez)

```
FC26_20250921.csv
      │
      ▼
player_similarity.py  →  player_similarity_codebase.json

Lista de Convocados.md
      │
      ▼
parse_convocados.py  →  convocados.db
```

### En tiempo de ejecución

**Motor 1 (por jugador):**
```
player_similarity_codebase.json
      │
      ├─▶ recommend_similar_players.py  ─▶  5 jugadores similares
      │
recommend_matches_by_players.py
      │
      ▼
Lista de partidos con scores [0,1]
```

**Motor 2 (por club):**
```
convocados.db
      │
      ├─▶ get_club_players_by_country()  ─▶  Jugadores del club por selección
      │
recommend_matches_by_team.py
      │
      ▼
Lista de partidos con scores [0,1]
```

---

## Fundamento Matemático

### Distancia y Similitud Coseno

La **distancia coseno** entre dos vectores de atributos `A` y `B` se define como:

```
d_cos(A, B) = 1 - (A · B) / (||A|| * ||B||)
```

- `d = 0` → jugadores perfectamente similares
- `d = 1` → jugadores sin correlación
- `d = 2` → jugadores diametralmente opuestos

Para obtener la **similitud coseno** (usada en el Motor 1):

```
similitud = 1 - distancia_coseno
```

### Normalización Exponencial

Ambos motores mapean un score en `[0, ∞)` al rango `[0, 1)` usando la función:

```
f(x) = 1 - e^(-k * x)
```

| Motor | Valor de `k` | Razón |
|---|---|---|
| Motor 1 (por jugador) | `k = 1` | Los scores son similitudes coseno en `[0, 1]`; con k=1, un partido con el jugador favorito solo da ~0.63 |
| Motor 2 (por club) | `k = 4` | Las proporciones son generalmente menores (ej: 2/10 = 0.2); k=4 amplifica para usar mejor el rango |

**Propiedades de la función:**
- `f(0) = 0` → sin coincidencias, score 0
- `f(∞) → 1` → asintótico; nunca llega a 1 exactamente
- Monótonamente creciente → mayor acumulación = mayor score

### Proporción en Motor 2

```
Proporción equipo 1 = jugadores_del_club_en_equipo1 / total_jugadores_del_club_en_torneo
Proporción equipo 2 = jugadores_del_club_en_equipo2 / total_jugadores_del_club_en_torneo
raw_score = proporción_1 + proporción_2
```

Este enfoque es **relativo al club** (no al tamaño del plantel), lo que significa que un club con 10 jugadores convocados en total distribuye esa "cuota" entre las selecciones que juegan.

---

## Dependencias

```
pandas>=1.3.0        # Manipulación de DataFrames
scikit-learn>=0.24   # StandardScaler, pairwise_distances
sqlite3              # Incluido en la librería estándar de Python
re                   # Incluido en la librería estándar de Python
math                 # Incluido en la librería estándar de Python
```

Instalar dependencias externas:

```bash
pip install -r requirements.txt
```

---

*Documentación generada para el proyecto `worldcup-app`.*
