# Análisis del Sistema Recomendador

El sistema recomendador de la aplicación "worldcup-app" se encarga de calcular un **"Smart Score"** (puntaje inteligente) para cada partido. Este puntaje va de 1.0 a 10.0 y determina qué tan atractivo podría ser un partido específico para el usuario. 

El cálculo se realiza en el archivo `frontend/js/recommender.js` a través de la función `calculateSmartScore(match, teams)`. 

## Paso a Paso del Algoritmo Actual

El algoritmo funciona en tres fases principales: un cálculo base utilizando métricas objetivas de los equipos, un ajuste por bonificaciones del torneo, y finalmente, un fuerte ajuste basado en las preferencias explícitas del usuario.

### 1. Condiciones Iniciales
- **Partidos por Definir (TBD)**: Si alguno de los equipos es un "placeholder" (por ejemplo, aún no se define quién pasa a la siguiente ronda), el sistema asigna un puntaje por defecto de `5.0`.
- **Falta de Datos**: Si no se encuentra información o métricas de alguno de los equipos, el sistema asigna un puntaje de `6.0`.

### 2. Cálculo Base (Métricas Objetivas)
Si hay datos disponibles, el sistema evalúa 6 métricas clave. Cada métrica aporta un máximo de puntos al puntaje total:

1. **Valor de Plantilla (Max 2.5 pts)**: Suma el valor de mercado en euros (`market_value_eur`) de ambos equipos. Se normaliza tomando 850M como un valor alto de referencia.
2. **Popularidad Global (Max 2.0 pts)**: Promedia el puntaje de popularidad global (`global_popularity_score`) de ambos equipos.
3. **Estilo Ofensivo / xG (Max 1.5 pts)**: Promedia los goles esperados recientes (`recent_xg_avg`) de ambos equipos, buscando partidos con mayor probabilidad de goles.
4. **Desempeño Reciente / Eficiencia (Max 1.5 pts)**: Promedia el puntaje de eficiencia (`efficiency_score_avg`) de ambos equipos.
5. **Intensidad / Fricción Histórica (Max 1.0 pts)**: Promedia las tarjetas por partido (`cards_per_match_avg`) de ambos equipos. Partidos con más tarjetas se consideran más intensos/friccionados.
6. **Cantidad de Estrellas (Max 1.0 pts)**: Cuenta cuántos jugadores están marcados como estrellas (`is_star_player`) en ambas plantillas sumadas. Toma 8 jugadores como el máximo ideal.

### 3. Bonificación por Instancia del Torneo
- **Fase de Eliminatorias**: Si el partido NO es de "Group Stage" (Fase de Grupos), se añade un bono de **`0.5 pts`**.

### 4. Ajustes por Preferencias del Usuario (El más influyente)
Si el usuario ha configurado sus preferencias en la aplicación, el algoritmo ajusta fuertemente el puntaje para personalizar la recomendación:

- **Equipo Favorito**: Si uno de los equipos jugando es el equipo favorito del usuario (`favoriteTeam`), se suman **`+2.5 pts`**.
- **Estilo de Partido Preferido (`matchStyle`)**:
  - Si prefiere **"cerrado" (closed)**: Se premian partidos con bajo xG (< 1.0) sumando **`+1.0 pt`**, y con altas tarjetas (> 1.5) sumando **`+0.5 pts`**.
  - Si prefiere **"caótico" (chaotic)**: Se premian partidos con alto xG (> 1.2) sumando **`+1.0 pt`**, y con bajas tarjetas (< 1.0) sumando **`+0.5 pts`**.
- **Jugadores Favoritos**: Por cada jugador favorito (`favoritePlayers`) del usuario que se encuentre en alguna de las dos plantillas, se suma **`+0.5 pts`**.
- **Horario Preferido (`preferredTime`)**: Evalúa la hora del partido (mañana, tarde o noche). Si coincide con las franjas horarias preferidas del usuario, se suman **`+1.5 pts`**.

### 5. Normalización Final
Al terminar todos los cálculos, el puntaje se limita matemáticamente para asegurar que nunca baje de `1.0` ni supere el máximo de `10.0`. Finalmente, se redondea a un decimal.

---

## Datos Utilizados para el Rediseño

Si planeas rediseñar el algoritmo, estos son los puntos de datos y estructuras exactas a las que tienes acceso dentro de la función:

### Datos de los Equipos (`teams`) y Partido (`match`)
- `match.home_team.is_placeholder` / `match.away_team.is_placeholder`: Booleanos que indican si el equipo ya está definido.
- `match.stage`: String con la etapa del torneo (ej. "Group Stage").
- `match.kickoff_at`: Fecha y hora del partido.
- `team.metrics.market_value_eur`: Valor monetario de la plantilla.
- `team.metrics.global_popularity_score`: Puntaje de popularidad del país/equipo.
- `team.metrics.recent_xg_avg`: Promedio de goles esperados (xG).
- `team.metrics.efficiency_score_avg`: Puntaje de eficiencia del equipo.
- `team.metrics.cards_per_match_avg`: Promedio de tarjetas recibidas por partido.
- `team.squad`: Array de objetos que representan a los jugadores.
- `player.is_star_player`: Booleano que indica si el jugador es una "estrella".
- `player.name`: Nombre completo del jugador.

### Datos del Usuario (`state.userPreferences`)
- `favoriteTeam`: Código FIFA (String) del equipo favorito.
- `matchStyle`: String que indica el estilo de partido preferido (ej. `'closed'`, `'chaotic'`).
- `favoritePlayers`: Array de Strings con los nombres (o partes del nombre) de los jugadores favoritos.
- `preferredTime`: Array de Strings con los momentos del día preferidos (`'morning'`, `'afternoon'`, `'evening'`).
