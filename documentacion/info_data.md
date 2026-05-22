The Fjelstul World Cup Database
Fuente: https://github.com/jfjelstul/worldcup

Principal fuente de datos sobre mundiales anteriores. Se organiza en 5 grupos temáticos con las siguientes especificaciones técnicas:

1. Los básicos (Entidades principales)
tournaments: Registro de 30 torneos; incluye organizador, ganador, fechas y formato (18 variables).
confederations: Las 6 confederaciones de la FIFA (5 variables).
teams: 88 selecciones participantes con códigos ISO y datos de su federación (14 variables).
players: 10,401 jugadores con fecha de nacimiento y link a Wikipedia (13 variables).
managers: 475 entrenadores y su país de origen (7 variables).
referees: 493 árbitros con su confederación y país (10 variables).
stadiums: 240 estadios con ciudad, capacidad y enlaces informativos (8 variables).
matches: 1,248 partidos con sedes, puntajes, tiempos extra y detalles de penales (38 variables).
awards: Descripción e historia de los 8 premios individuales existentes (5 variables).
2. Mapeo de actores a torneos
qualified_teams: Desempeño y fase máxima alcanzada por equipo en cada edición (625 obs).
squads: Composición de planteles con posiciones y dorsales desde 1954 (13,843 obs).
manager_appointments: Nombramientos de DTs, incluyendo casos de co-entrenadores (637 obs).
referee_appointments: Árbitros principales asignados por torneo (668 obs).
3. Mapeo de actores a partidos (Apariciones)
team_appearances: Estadísticas de goles a favor/en contra y resultado por partido (2,496 obs).
player_appearances: Participación de titulares y suplentes desde 1970 (27,432 obs).
manager_appearances: Presencia de directores técnicos en el banquillo por partido (2,538 obs).
referee_appearances: Actuaciones arbitrales por cada encuentro (1,248 obs).
4. Eventos de partidos
goals: Detalle de 3,637 goles (minuto, tipo de jugada, autogoles) excluyendo tandas de penales.
penalty_kicks: Registro de 396 ejecuciones exclusivamente en tandas de penales.
bookings: 3,178 tarjetas amarillas y rojas registradas desde su introducción en 1970.
substitutions: 10,222 cambios realizados desde la implementación de la regla en 1970.
5. Atributos y estadísticas del torneo
host_countries: Desempeño específico del país organizador (31 obs).
tournament_stages: Estructura de fases (grupos o eliminación) y fechas de cada etapa (1,555 obs).
groups: Configuración de grupos y cantidad de equipos por sector (117 obs).
group_standings: Tabla de posiciones final de cada grupo con criterios de desempate (626 obs)
tournament_standings: Ranking final de los 4 mejores equipos por mundial (120 obs).
award_winners: Ganadores de premios individuales, incluyendo premios compartidos (200 obs).
Cita: Fjelstul, Joshua C. "The Fjelstul World Cup Database v.1.2.0." July 19, 2023. 




























FIFA World Cup 2026 - Schedule & Venue Data
Fuente: https://www.kaggle.com/datasets/areezvisram12/fifa-world-cup-2026-match-data-unofficial
Este dataset ofrece una visión relacional y normalizada del calendario completo del Mundial 2026, disponible en formatos CSV y SQLite.
1. matches (Calendario principal)
Contiene el cronograma de los 104 partidos del torneo.
Incluye el número oficial de partido, fecha y hora (formato ISO 8601 con UTC), y vinculaciones con las tablas de equipos, ciudades y fases.
2. host_cities (Sedes y geografía)
Datos de las 16 ciudades anfitrionas.
Registra el nombre oficial del estadio, el código del aeropuerto principal y la agrupación por región (Este, Central u Oeste).
3. teams (Selecciones participantes)
Información sobre los 48 equipos que disputarán el torneo.
Incluye tanto a los equipos ya clasificados como espacios reservados para los ganadores de los Play-offs, asignando a cada uno su grupo correspondiente (A-L).
4. tournament_stages (Fases del torneo)
Datos estáticos para la categorización y ordenamiento cronológico de los encuentros.
Define el nombre oficial de cada fase y un valor numérico (1 a 7) para asegurar el filtrado y la visualización correcta de las etapas.
5. worldcup.db (Base de datos SQLite)
Archivo worldcup2026.db que integra todas las tablas anteriores en una base de datos relacional lista para ser consultada mediante SQL.
Hay que actualizarla con los resultados de los playoffs.











International Football Results (1872-2026)
Fuente: https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017?select=goalscorers.csv
Este repositorio centraliza más de 49,000 resultados de partidos internacionales masculinos, desde el primer encuentro oficial en 1872 hasta la actualidad. Contiene 4 datasets.
1. results (Registro histórico de partidos)
Documenta el historial completo de enfrentamientos, incluyendo fecha, equipos (local/visitante) y marcadores finales (incluyendo tiempo extra).
Detalla el torneo, la ubicación exacta (ciudad y país) y si el encuentro se disputó en territorio neutral.
Es la base principal para calcular el "historial" entre selecciones y detectar rivalidades históricas.
2. shootouts (Definiciones por penales)
Registra específicamente los partidos que se decidieron desde los doce pasos.
Identifica al ganador de la tanda y qué equipo ejecutó el primer remate, permitiendo análisis de resiliencia bajo presión.
3. goalscorers (Detalle de anotadores)
Listado exhaustivo de los goles marcados, asociándolos al jugador y al equipo.
Especifica si el tanto fue de jugada, penal o gol en contra, lo cual es vital para identificar a los jugadores estrella de cada selección.
4. former_names (Evolución de identidades)
Tabla de referencia que vincula los nombres actuales de las selecciones con sus denominaciones antiguas (por ejemplo, cambios tras disoluciones de países o cambios federativos).
Incluye los períodos de tiempo en que se utilizaron dichos nombres para mantener la integridad de los datos históricos.
