# Perfilado de Clusters y Arquetipos de Jugadores

Este reporte analiza empíricamente los clústeres generados mediante **KMeans (Arquetipos >75)** con optimización dinámica de K.
Para cada clúster, comparamos la mediana de sus atributos físicos y técnicos contra la mediana global de su posición.
Las desviaciones positivas revelan las fortalezas características del arquetipo, mientras que las negativas señalan sus carencias.

---

## Goalkeepers (KMeans Arquetipos >75)
Total jugadores analizados: 86

| Clúster | Representante principal | Miembros | Atributos Destacados (Desviación vs Mediana Global) |
| :--- | :--- | :---: | :--- |
| Cluster 1: **Arquero Jugador / Sweeper Keeper** | Alisson Ramsés Becker (89) | 29 | **+17** en skill long passing, **+16** en attacking short passing, **+13** en mentality composure, **+11** en skill ball control, **+10** en movement agility |
| Cluster 2: **Arquero Anómalo / Lóbero** | Yvon Landry Mvogo Nganoma (76) | 2 | **+18** en movement agility, **+17** en movement balance, **+15** en mentality penalties, **+15** en mentality aggression, **+15** en defending marking awareness |
| Cluster 3: **Arquero Tradicional / Atajador** | Thibaut Nicolas Marc Courtois (89) | 55 | **+1** en attacking finishing, **+1** en skill fk accuracy, **+1** en power long shots, **+1** en mentality penalties |

### Análisis Detallado de Arquetipos por Clúster

#### Clúster 1: **"Arquero Jugador / Sweeper Keeper"** (Representante: Alisson Ramsés Becker - 89)

*Dominan absolutamente el juego con los pies, registrando +17 en pase largo y +16 en pase corto frente a la mediana. También superan al resto en compostura (+13). Son la primera línea de creación.*

- **Tamaño del grupo:** 29 jugadores.
- **Ejemplos en el dataset:** Alisson Ramsés Becker, David Raya Martín, Mike Peterson Maignan, Gregor Kobel, Ederson Santana de Moraes, Damián Emiliano Martínez Romero

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Skill Long Passing**: ++17.0 (Mediana del clúster: 50.0 vs Mediana global: 33.0)
  * **Attacking Short Passing**: ++16.0 (Mediana del clúster: 50.0 vs Mediana global: 34.0)
  * **Mentality Composure**: ++13.0 (Mediana del clúster: 61.0 vs Mediana global: 48.0)
  * **Skill Ball Control**: ++11.0 (Mediana del clúster: 34.0 vs Mediana global: 23.0)
  * **Movement Agility**: ++10.0 (Mediana del clúster: 51.0 vs Mediana global: 41.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Power Long Shots**: -2.0 (Mediana del clúster: 9.0 vs Mediana global: 11.0)
  * **Attacking Finishing**: -1.5 (Mediana del clúster: 9.0 vs Mediana global: 10.5)
  * **Attacking Volleys**: -1.0 (Mediana del clúster: 10.0 vs Mediana global: 11.0)
  * **Mentality Penalties**: -1.0 (Mediana del clúster: 16.0 vs Mediana global: 17.0)
  * **Defending Sliding Tackle**: -1.0 (Mediana del clúster: 13.0 vs Mediana global: 14.0)

________________________________________

#### Clúster 2: **"Arquero Anómalo / Lóbero"** (Representante: Yvon Landry Mvogo Nganoma - 76)

*Es un micro-clúster de solo 2 jugadores. Tienen altísima agilidad (+18), pero su penalización extrema en compostura (-17.5) sugiere que el algoritmo aisló ruido estadístico o perfiles muy erráticos.*

- **Tamaño del grupo:** 2 jugadores.
- **Ejemplos en el dataset:** Yvon Landry Mvogo Nganoma, Luis Ricardo Mejía Cajar

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Movement Agility**: ++18.0 (Mediana del clúster: 59.0 vs Mediana global: 41.0)
  * **Movement Balance**: ++17.5 (Mediana del clúster: 57.5 vs Mediana global: 40.0)
  * **Mentality Penalties**: ++15.5 (Mediana del clúster: 32.5 vs Mediana global: 17.0)
  * **Mentality Aggression**: ++15.0 (Mediana del clúster: 41.0 vs Mediana global: 26.0)
  * **Defending Marking Awareness**: ++15.0 (Mediana del clúster: 29.0 vs Mediana global: 14.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Mentality Composure**: -17.5 (Mediana del clúster: 30.5 vs Mediana global: 48.0)
  * **Skill Long Passing**: -11.0 (Mediana del clúster: 22.0 vs Mediana global: 33.0)
  * **Attacking Short Passing**: -10.0 (Mediana del clúster: 24.0 vs Mediana global: 34.0)
  * **Skill Ball Control**: -1.5 (Mediana del clúster: 21.5 vs Mediana global: 23.0)
  * **Defending Sliding Tackle**: -1.5 (Mediana del clúster: 12.5 vs Mediana global: 14.0)

________________________________________

#### Clúster 3: **"Arquero Tradicional / Atajador"** (Representante: Thibaut Nicolas Marc Courtois - 89)

*El bloque principal (55 jugadores). Tienen deficiencias marcadas en visión (-5.5) y pase corto (-5.0), enfocándose estrictamente en defender bajo los tres palos sin arriesgar en la salida.*

- **Tamaño del grupo:** 55 jugadores.
- **Ejemplos en el dataset:** Thibaut Nicolas Marc Courtois, Unai Simón Mendibil, Oliver Baumann, Gerónimo Rulli, Yassine Bounouياسين بونو, Rui Tiago Dantas da Silva

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Attacking Finishing**: ++1.5 (Mediana del clúster: 12.0 vs Mediana global: 10.5)
  * **Skill Fk Accuracy**: ++1.0 (Mediana del clúster: 14.0 vs Mediana global: 13.0)
  * **Power Long Shots**: ++1.0 (Mediana del clúster: 12.0 vs Mediana global: 11.0)
  * **Mentality Penalties**: ++1.0 (Mediana del clúster: 18.0 vs Mediana global: 17.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Mentality Composure**: -7.0 (Mediana del clúster: 41.0 vs Mediana global: 48.0)
  * **Mentality Vision**: -5.5 (Mediana del clúster: 42.0 vs Mediana global: 47.5)
  * **Attacking Short Passing**: -5.0 (Mediana del clúster: 29.0 vs Mediana global: 34.0)
  * **Skill Long Passing**: -4.0 (Mediana del clúster: 29.0 vs Mediana global: 33.0)
  * **Skill Ball Control**: -4.0 (Mediana del clúster: 19.0 vs Mediana global: 23.0)

________________________________________


---

## Centerbacks (KMeans Arquetipos >75)
Total jugadores analizados: 161

| Clúster | Representante principal | Miembros | Atributos Destacados (Desviación vs Mediana Global) |
| :--- | :--- | :---: | :--- |
| Cluster 1: **Central Dominador / Amenaza Aérea** | Virgil van Dijk (90) | 62 | **+13** en attacking finishing, **+12** en power long shots, **+12** en attacking crossing, **+11** en power shot power, **+11** en skill curve |
| Cluster 2: **Central de Cobertura / Rápido** | William Alain André Gabriel Saliba (87) | 65 | **+4** en pace, **+3** en movement acceleration, **+2** en movement sprint speed, **+1** en movement agility, **+1** en power jumping |
| Cluster 3: **Central Tanque / Físico** | Gabriel dos Santos Magalhães (88) | 34 | **+5** en power shot power, **+3** en power strength, **+1** en mentality aggression |

### Análisis Detallado de Arquetipos por Clúster

#### Clúster 1: **"Central Dominador / Amenaza Aérea"** (Representante: Virgil van Dijk - 90)

*No solo defienden; son armas ofensivas en el juego aéreo y pelota parada. Destacan con +13 en finalización, +12 en tiros lejanos y +11.5 en potencia de tiro.*

- **Tamaño del grupo:** 62 jugadores.
- **Ejemplos en el dataset:** Virgil van Dijk, Marcos Aoás Corrêa, Antonio Rüdiger, Nico Cedric Schlotterbeck, Nathan Benjamin Aké, Ronald Federico Araújo da Silva

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Attacking Finishing**: ++13.0 (Mediana del clúster: 48.0 vs Mediana global: 35.0)
  * **Power Long Shots**: ++12.0 (Mediana del clúster: 49.0 vs Mediana global: 37.0)
  * **Attacking Crossing**: ++12.0 (Mediana del clúster: 58.0 vs Mediana global: 46.0)
  * **Power Shot Power**: ++11.5 (Mediana del clúster: 65.5 vs Mediana global: 54.0)
  * **Skill Curve**: ++11.5 (Mediana del clúster: 54.5 vs Mediana global: 43.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Power Strength**: -1.0 (Mediana del clúster: 80.0 vs Mediana global: 81.0)

________________________________________

#### Clúster 2: **"Central de Cobertura / Rápido"** (Representante: William Alain André Gabriel Saliba - 87)

*Su geometría prioriza corregir errores mediante velocidad. Tienen +4 en ritmo y +3 en aceleración, pero carecen del impacto ofensivo del Clúster 1, con -9 en tiros lejanos.*

- **Tamaño del grupo:** 65 jugadores.
- **Ejemplos en el dataset:** William Alain André Gabriel Saliba, Ibrahima Konaté, Willian Joel Pacho Tenorio, Dayotchanculle Oswald Upamecano, Gleison Bremer Silva Nascimento, Piero Martín Hincapié Reyna

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Pace**: ++4.0 (Mediana del clúster: 72.0 vs Mediana global: 68.0)
  * **Movement Acceleration**: ++3.0 (Mediana del clúster: 68.0 vs Mediana global: 65.0)
  * **Movement Sprint Speed**: ++2.0 (Mediana del clúster: 73.0 vs Mediana global: 71.0)
  * **Movement Agility**: ++1.0 (Mediana del clúster: 61.0 vs Mediana global: 60.0)
  * **Power Jumping**: ++1.0 (Mediana del clúster: 83.0 vs Mediana global: 82.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Power Long Shots**: -9.0 (Mediana del clúster: 28.0 vs Mediana global: 37.0)
  * **Shooting**: -7.0 (Mediana del clúster: 33.0 vs Mediana global: 40.0)
  * **Power Shot Power**: -7.0 (Mediana del clúster: 47.0 vs Mediana global: 54.0)
  * **Skill Curve**: -7.0 (Mediana del clúster: 36.0 vs Mediana global: 43.0)
  * **Mentality Positioning**: -7.0 (Mediana del clúster: 37.0 vs Mediana global: 44.0)

________________________________________

#### Clúster 3: **"Central Tanque / Físico"** (Representante: Gabriel dos Santos Magalhães - 88)

*El arquetipo clásico de choque. Su fuerza supera a la mediana (+3) y tienen alta potencia (+5), pero el modelo detectó su falta de movilidad, penalizándolos severamente en agilidad (-16) y aceleración (-11.5).*

- **Tamaño del grupo:** 34 jugadores.
- **Ejemplos en el dataset:** Gabriel dos Santos Magalhães, Jonathan Glao Tah, Rúben dos Santos Gato Alves Dias, José María Giménez de Vargas, Kalidou Koulibaly, Alexsandro Victor de Souza Ribeiro

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Power Shot Power**: ++5.0 (Mediana del clúster: 59.0 vs Mediana global: 54.0)
  * **Power Strength**: ++3.0 (Mediana del clúster: 84.0 vs Mediana global: 81.0)
  * **Mentality Aggression**: ++1.0 (Mediana del clúster: 77.0 vs Mediana global: 76.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Movement Agility**: -16.0 (Mediana del clúster: 44.0 vs Mediana global: 60.0)
  * **Movement Balance**: -14.0 (Mediana del clúster: 44.0 vs Mediana global: 58.0)
  * **Mentality Positioning**: -13.0 (Mediana del clúster: 31.0 vs Mediana global: 44.0)
  * **Movement Acceleration**: -11.5 (Mediana del clúster: 53.5 vs Mediana global: 65.0)
  * **Movement Sprint Speed**: -10.0 (Mediana del clúster: 61.0 vs Mediana global: 71.0)

________________________________________


---

## Fullbacks (KMeans Arquetipos >75)
Total jugadores analizados: 120

| Clúster | Representante principal | Miembros | Atributos Destacados (Desviación vs Mediana Global) |
| :--- | :--- | :---: | :--- |
| Cluster 1: **Lateral Físico / Tercer Central** | Joško Gvardiol (84) | 27 | **+9** en attacking heading accuracy, **+5** en power strength, **+4** en defending, **+4** en power jumping, **+4** en physic |
| Cluster 2: **Lateral de Recorrido / Equilibrado** | Jules Olivier Koundé (87) | 31 | **+1** en movement acceleration, **+1** en movement sprint speed, **+1** en movement balance, **+0** en pace |
| Cluster 3: **Lateral Ofensivo / Carrilero** | Achraf Hakimi Mouhأشرف حكيمي (89) | 62 | **+8** en skill fk accuracy, **+7** en power long shots, **+4** en attacking finishing, **+4** en shooting, **+4** en mentality penalties |

### Análisis Detallado de Arquetipos por Clúster

#### Clúster 1: **"Lateral Físico / Tercer Central"** (Representante: Joško Gvardiol - 84)

*Destacan por su capacidad para el choque y el juego aéreo, con +9 en cabezazo, +5 en fuerza y +4 en salto.*

- **Tamaño del grupo:** 27 jugadores.
- **Ejemplos en el dataset:** Joško Gvardiol, Denzel Justus Morris Dumfries, Konrad Laimer, Daniel Muñoz Mejía, Noussair Mazraouiنصير مزراوي, Ramy Bensebainiرامي بن سبعيني

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Attacking Heading Accuracy**: ++9.0 (Mediana del clúster: 72.0 vs Mediana global: 63.0)
  * **Power Strength**: ++5.0 (Mediana del clúster: 76.0 vs Mediana global: 71.0)
  * **Defending**: ++4.0 (Mediana del clúster: 74.0 vs Mediana global: 70.0)
  * **Power Jumping**: ++4.0 (Mediana del clúster: 81.0 vs Mediana global: 77.0)
  * **Physic**: ++4.0 (Mediana del clúster: 78.0 vs Mediana global: 74.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Skill Fk Accuracy**: -7.0 (Mediana del clúster: 43.0 vs Mediana global: 50.0)
  * **Movement Balance**: -7.0 (Mediana del clúster: 67.0 vs Mediana global: 74.0)
  * **Movement Agility**: -6.0 (Mediana del clúster: 69.0 vs Mediana global: 75.0)
  * **Movement Sprint Speed**: -4.0 (Mediana del clúster: 74.0 vs Mediana global: 78.0)
  * **Movement Acceleration**: -4.0 (Mediana del clúster: 74.0 vs Mediana global: 78.0)

________________________________________

#### Clúster 2: **"Lateral de Recorrido / Equilibrado"** (Representante: Jules Olivier Koundé - 87)

*Son ágiles y rápidos (+1 en aceleración y velocidad), pero tienen desviaciones muy negativas en impacto en el área rival (-13.5 en finalización, -11.5 en tiros). Su misión principal es la banda, no el arco.*

- **Tamaño del grupo:** 31 jugadores.
- **Ejemplos en el dataset:** Jules Olivier Koundé, Antonee Robinson, Jurriën David Norman Timber, Rayan Aït Nouriريان آيت نوري, Valentino Francisco Livramento, Aaron Wan-Bissaka

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Movement Acceleration**: ++1.0 (Mediana del clúster: 79.0 vs Mediana global: 78.0)
  * **Movement Sprint Speed**: ++1.0 (Mediana del clúster: 79.0 vs Mediana global: 78.0)
  * **Movement Balance**: ++1.0 (Mediana del clúster: 75.0 vs Mediana global: 74.0)
  * **Pace**: ++0.5 (Mediana del clúster: 79.0 vs Mediana global: 78.5)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Attacking Finishing**: -13.5 (Mediana del clúster: 41.0 vs Mediana global: 54.5)
  * **Skill Fk Accuracy**: -13.0 (Mediana del clúster: 37.0 vs Mediana global: 50.0)
  * **Power Long Shots**: -13.0 (Mediana del clúster: 43.0 vs Mediana global: 56.0)
  * **Shooting**: -11.5 (Mediana del clúster: 45.0 vs Mediana global: 56.5)
  * **Power Shot Power**: -9.0 (Mediana del clúster: 56.0 vs Mediana global: 65.0)

________________________________________

#### Clúster 3: **"Lateral Ofensivo / Carrilero"** (Representante: Achraf Hakimi Mouhأشرف حكيمي - 89)

*El arquetipo de ataque profundo. Tienen métricas de delanteros: +8 en precisión de tiros libres, +7 en tiros lejanos y +4.5 en finalización.*

- **Tamaño del grupo:** 62 jugadores.
- **Ejemplos en el dataset:** Achraf Hakimi Mouhأشرف حكيمي, Nuno Alexandre Tavares Mendes, Marcos Llorente Moreno, Alphonso Boyle Davies, Marc Cucurella Saseta, Theo Bernard François Hernández

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Skill Fk Accuracy**: ++8.0 (Mediana del clúster: 58.0 vs Mediana global: 50.0)
  * **Power Long Shots**: ++7.0 (Mediana del clúster: 63.0 vs Mediana global: 56.0)
  * **Attacking Finishing**: ++4.5 (Mediana del clúster: 59.0 vs Mediana global: 54.5)
  * **Shooting**: ++4.0 (Mediana del clúster: 60.5 vs Mediana global: 56.5)
  * **Mentality Penalties**: ++4.0 (Mediana del clúster: 52.0 vs Mediana global: 48.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Attacking Heading Accuracy**: -3.5 (Mediana del clúster: 59.5 vs Mediana global: 63.0)
  * **Power Strength**: -3.0 (Mediana del clúster: 68.0 vs Mediana global: 71.0)
  * **Physic**: -1.0 (Mediana del clúster: 73.0 vs Mediana global: 74.0)
  * **Defending**: -1.0 (Mediana del clúster: 69.0 vs Mediana global: 70.0)
  * **Mentality Aggression**: -1.0 (Mediana del clúster: 71.0 vs Mediana global: 72.0)

________________________________________


---

## Midfielders (KMeans Arquetipos >75)
Total jugadores analizados: 228

| Clúster | Representante principal | Miembros | Atributos Destacados (Desviación vs Mediana Global) |
| :--- | :--- | :---: | :--- |
| Cluster 1: **Todocampista / Box-to-Box** | Jude Victor William Bellingham (90) | 126 | **+4** en power jumping, **+3** en defending, **+3** en defending standing tackle, **+3** en mentality interceptions, **+3** en defending marking awareness |
| Cluster 2: **Enganche Ágil / Mediapunta** | Florian Richard Wirtz (89) | 41 | **+7** en pace, **+7** en attacking volleys, **+7** en movement sprint speed, **+6** en movement agility, **+6** en movement balance |
| Cluster 3: **Organizador / Pivote Técnico** | Rodrigo Hernández Cascante (90) | 61 | **+8** en attacking volleys, **+8** en mentality penalties, **+7** en skill fk accuracy, **+6** en power long shots, **+6** en attacking crossing |

### Análisis Detallado de Arquetipos por Clúster

#### Clúster 1: **"Todocampista / Box-to-Box"** (Representante: Jude Victor William Bellingham - 90)

*Son el motor físico del equipo. Tienen superioridad en salto (+4.0) y métricas defensivas consistentes (+3.5 en entradas y defensa general, +3.0 en intercepciones).*

- **Tamaño del grupo:** 126 jugadores.
- **Ejemplos en el dataset:** Jude Victor William Bellingham, Federico Santiago Valverde Dipetta, Pedro González López, Frenkie de Jong, Declan Rice, Moisés Isaac Caicedo Corozo

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Power Jumping**: ++4.0 (Mediana del clúster: 76.0 vs Mediana global: 72.0)
  * **Defending**: ++3.5 (Mediana del clúster: 72.0 vs Mediana global: 68.5)
  * **Defending Standing Tackle**: ++3.5 (Mediana del clúster: 74.5 vs Mediana global: 71.0)
  * **Mentality Interceptions**: ++3.0 (Mediana del clúster: 73.0 vs Mediana global: 70.0)
  * **Defending Marking Awareness**: ++3.0 (Mediana del clúster: 71.0 vs Mediana global: 68.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Skill Fk Accuracy**: -6.0 (Mediana del clúster: 57.0 vs Mediana global: 63.0)
  * **Attacking Volleys**: -5.0 (Mediana del clúster: 55.0 vs Mediana global: 60.0)
  * **Attacking Finishing**: -5.0 (Mediana del clúster: 62.0 vs Mediana global: 67.0)
  * **Mentality Penalties**: -5.0 (Mediana del clúster: 55.0 vs Mediana global: 60.0)
  * **Power Long Shots**: -4.0 (Mediana del clúster: 66.0 vs Mediana global: 70.0)

________________________________________

#### Clúster 2: **"Enganche Ágil / Mediapunta"** (Representante: Florian Richard Wirtz - 89)

*Pura creatividad y desequilibrio. Sobresalen en ritmo (+7.0), agilidad (+6.0) y balance (+6.0). A cambio, el algoritmo marca su nulo retroceso, con -23.0 en barridas y -18.5 en defensa general.*

- **Tamaño del grupo:** 41 jugadores.
- **Ejemplos en el dataset:** Florian Richard Wirtz, Jamal Musiala, Daniel Olmo Carvajal, Matheus Santos Carneiro da Cunha, Eberechi Oluchi Eze, Charles De Ketelaere

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Pace**: ++7.0 (Mediana del clúster: 77.0 vs Mediana global: 70.0)
  * **Attacking Volleys**: ++7.0 (Mediana del clúster: 67.0 vs Mediana global: 60.0)
  * **Movement Sprint Speed**: ++7.0 (Mediana del clúster: 76.0 vs Mediana global: 69.0)
  * **Movement Agility**: ++6.0 (Mediana del clúster: 81.0 vs Mediana global: 75.0)
  * **Movement Balance**: ++6.0 (Mediana del clúster: 81.0 vs Mediana global: 75.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Defending Sliding Tackle**: -23.0 (Mediana del clúster: 44.0 vs Mediana global: 67.0)
  * **Defending Marking Awareness**: -23.0 (Mediana del clúster: 45.0 vs Mediana global: 68.0)
  * **Mentality Interceptions**: -19.0 (Mediana del clúster: 51.0 vs Mediana global: 70.0)
  * **Defending**: -18.5 (Mediana del clúster: 50.0 vs Mediana global: 68.5)
  * **Defending Standing Tackle**: -18.0 (Mediana del clúster: 53.0 vs Mediana global: 71.0)

________________________________________

#### Clúster 3: **"Organizador / Pivote Técnico"** (Representante: Rodrigo Hernández Cascante - 90)

*Los dueños de la pelota parada y los pases largos. Resaltan en voleas (+8.0), penales (+8.0) y precisión de libres (+7.0). Son más lentos que el resto (-4.0 en ritmo), compensándolo con posicionamiento.*

- **Tamaño del grupo:** 61 jugadores.
- **Ejemplos en el dataset:** Rodrigo Hernández Cascante, Joshua Walter Kimmich, Vítor Machado Ferreira, Kevin De Bruyne, Alexis Mac Allister, Martin Ødegaard

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Attacking Volleys**: ++8.0 (Mediana del clúster: 68.0 vs Mediana global: 60.0)
  * **Mentality Penalties**: ++8.0 (Mediana del clúster: 68.0 vs Mediana global: 60.0)
  * **Skill Fk Accuracy**: ++7.0 (Mediana del clúster: 70.0 vs Mediana global: 63.0)
  * **Power Long Shots**: ++6.0 (Mediana del clúster: 76.0 vs Mediana global: 70.0)
  * **Attacking Crossing**: ++6.0 (Mediana del clúster: 74.0 vs Mediana global: 68.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Pace**: -4.0 (Mediana del clúster: 66.0 vs Mediana global: 70.0)
  * **Movement Acceleration**: -4.0 (Mediana del clúster: 68.0 vs Mediana global: 72.0)
  * **Movement Sprint Speed**: -4.0 (Mediana del clúster: 65.0 vs Mediana global: 69.0)
  * **Movement Agility**: -2.0 (Mediana del clúster: 73.0 vs Mediana global: 75.0)
  * **Power Jumping**: -2.0 (Mediana del clúster: 70.0 vs Mediana global: 72.0)

________________________________________


---

## Strikers (KMeans Arquetipos >75)
Total jugadores analizados: 108

| Clúster | Representante principal | Miembros | Atributos Destacados (Desviación vs Mediana Global) |
| :--- | :--- | :---: | :--- |
| Cluster 1: **Delantero de Presión / Primera Línea Defensiva** | Masour Ousmane Dembélé (90) | 34 | **+12** en mentality interceptions, **+11** en defending sliding tackle, **+9** en defending marking awareness, **+9** en defending standing tackle, **+8** en defending |
| Cluster 2: **Delantero de Ruptura / Velocista** | Kylian Mbappé Lottin (91) | 48 | **+3** en movement acceleration, **+2** en movement sprint speed, **+2** en movement agility, **+1** en pace, **+1** en movement balance |
| Cluster 3: **Hombre Objetivo / Nueve de Área** | Erling Braut Håland (90) | 26 | **+7** en power strength, **+6** en mentality aggression, **+5** en attacking heading accuracy, **+3** en physic, **+3** en movement reactions |

### Análisis Detallado de Arquetipos por Clúster

#### Clúster 1: **"Delantero de Presión / Primera Línea Defensiva"** (Representante: Masour Ousmane Dembélé - 90)

*Este es un hallazgo excelente del modelo. Identificó a los atacantes que ahogan la salida rival, registrando +12.5 en intercepciones y +11.0 en barridas frente a la mediana de los delanteros.*

- **Tamaño del grupo:** 34 jugadores.
- **Ejemplos en el dataset:** Masour Ousmane Dembélé, Lautaro Javier Martínez, Julián Álvarez, Marcus Lilian Thuram-Ulien, Oliver George Arthur Watkins, Mikel Oyarzabal Ugarte

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Mentality Interceptions**: ++12.5 (Mediana del clúster: 43.0 vs Mediana global: 30.5)
  * **Defending Sliding Tackle**: ++11.0 (Mediana del clúster: 38.0 vs Mediana global: 27.0)
  * **Defending Marking Awareness**: ++9.0 (Mediana del clúster: 43.5 vs Mediana global: 34.5)
  * **Defending Standing Tackle**: ++9.0 (Mediana del clúster: 43.0 vs Mediana global: 34.0)
  * **Defending**: ++8.5 (Mediana del clúster: 44.5 vs Mediana global: 36.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Power Strength**: -4.5 (Mediana del clúster: 74.5 vs Mediana global: 79.0)
  * **Physic**: -2.0 (Mediana del clúster: 74.0 vs Mediana global: 76.0)
  * **Attacking Heading Accuracy**: -1.5 (Mediana del clúster: 73.5 vs Mediana global: 75.0)
  * **Power Jumping**: -1.0 (Mediana del clúster: 84.0 vs Mediana global: 85.0)
  * **Mentality Penalties**: -0.5 (Mediana del clúster: 70.5 vs Mediana global: 71.0)

________________________________________

#### Clúster 2: **"Delantero de Ruptura / Velocista"** (Representante: Kylian Mbappé Lottin - 91)

*Su principal arma es ganar la espalda de la defensa, superando la mediana en aceleración (+3.0) y velocidad (+2.5), con bajo compromiso de marca (-9.0 en entradas).*

- **Tamaño del grupo:** 48 jugadores.
- **Ejemplos en el dataset:** Kylian Mbappé Lottin, Alexander Isak, Viktor Einar Gyökeres, Cristiano Ronaldo dos Santos Aveiro, Patrik Schick, Omar Khaled Mohamed Marmoush

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Movement Acceleration**: ++3.0 (Mediana del clúster: 78.0 vs Mediana global: 75.0)
  * **Movement Sprint Speed**: ++2.5 (Mediana del clúster: 79.5 vs Mediana global: 77.0)
  * **Movement Agility**: ++2.5 (Mediana del clúster: 73.0 vs Mediana global: 70.5)
  * **Pace**: ++1.5 (Mediana del clúster: 78.5 vs Mediana global: 77.0)
  * **Movement Balance**: ++1.0 (Mediana del clúster: 68.0 vs Mediana global: 67.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Defending Standing Tackle**: -9.0 (Mediana del clúster: 25.0 vs Mediana global: 34.0)
  * **Defending Marking Awareness**: -8.5 (Mediana del clúster: 26.0 vs Mediana global: 34.5)
  * **Mentality Interceptions**: -7.5 (Mediana del clúster: 23.0 vs Mediana global: 30.5)
  * **Defending Sliding Tackle**: -6.0 (Mediana del clúster: 21.0 vs Mediana global: 27.0)
  * **Defending**: -5.0 (Mediana del clúster: 31.0 vs Mediana global: 36.0)

________________________________________

#### Clúster 3: **"Hombre Objetivo / Nueve de Área"** (Representante: Erling Braut Håland - 90)

*Una bestia física. Arrasan en fuerza (+7.0) y cabezazo (+5.0). La contrapartida matemática es su rigidez: -16.5 en agilidad y -14.5 en balance.*

- **Tamaño del grupo:** 26 jugadores.
- **Ejemplos en el dataset:** Erling Braut Håland, Harry Edward Kane, Romelu Menama Lukaku Bolingoli, Ante Budimir, Christopher Grant Wood, Jean-Philippe Mateta

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Power Strength**: ++7.0 (Mediana del clúster: 86.0 vs Mediana global: 79.0)
  * **Mentality Aggression**: ++6.0 (Mediana del clúster: 73.0 vs Mediana global: 67.0)
  * **Attacking Heading Accuracy**: ++5.0 (Mediana del clúster: 80.0 vs Mediana global: 75.0)
  * **Physic**: ++3.5 (Mediana del clúster: 79.5 vs Mediana global: 76.0)
  * **Movement Reactions**: ++3.5 (Mediana del clúster: 78.5 vs Mediana global: 75.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Movement Agility**: -16.5 (Mediana del clúster: 54.0 vs Mediana global: 70.5)
  * **Movement Acceleration**: -15.0 (Mediana del clúster: 60.0 vs Mediana global: 75.0)
  * **Movement Balance**: -14.5 (Mediana del clúster: 52.5 vs Mediana global: 67.0)
  * **Pace**: -14.0 (Mediana del clúster: 63.0 vs Mediana global: 77.0)
  * **Skill Curve**: -12.0 (Mediana del clúster: 50.5 vs Mediana global: 62.5)

________________________________________


---

## Wingers (KMeans Arquetipos >75)
Total jugadores analizados: 130

| Clúster | Representante principal | Miembros | Atributos Destacados (Desviación vs Mediana Global) |
| :--- | :--- | :---: | :--- |
| Cluster 1: **Extremo Completo / Asociativo** | Mohamed Salah Hamed Ghalyمحمد صلاح (91) | 57 | **+2** en skill fk accuracy, **+2** en mentality penalties, **+2** en mentality vision, **+2** en defending sliding tackle, **+1** en attacking finishing |
| Cluster 2: **Extremo Desequilibrante / Regateador Puro** | Lamine Yamal Nasraoui Ebanaلامين يامال نصراوي إبانا (89) | 40 | **+2** en attacking finishing, **+2** en dribbling, **+1** en attacking short passing, **+1** en skill dribbling, **+1** en power shot power |
| Cluster 3: **Volante Táctico / Extremo Defensivo** | Bukayo Saka (88) | 33 | **+24** en defending sliding tackle, **+24** en defending standing tackle, **+22** en mentality interceptions, **+21** en defending marking awareness, **+20** en defending |

### Análisis Detallado de Arquetipos por Clúster

#### Clúster 1: **"Extremo Completo / Asociativo"** (Representante: Mohamed Salah Hamed Ghalyمحمد صلاح - 91)

*Jugadores de banda con gran capacidad de creación y definición. Superan la media en tiros libres (+2.0), visión (+2.0) y finalización (+1.5).*

- **Tamaño del grupo:** 57 jugadores.
- **Ejemplos en el dataset:** Mohamed Salah Hamed Ghalyمحمد صلاح, Raphael Dias Belloli, Michael Akpovie Olise, Heung-min Son손흥민 孙兴慜, Luis Fernando Díaz Marulanda, Christian Mate Pulišić

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Skill Fk Accuracy**: ++2.0 (Mediana del clúster: 62.0 vs Mediana global: 60.0)
  * **Mentality Penalties**: ++2.0 (Mediana del clúster: 62.0 vs Mediana global: 60.0)
  * **Mentality Vision**: ++2.0 (Mediana del clúster: 73.0 vs Mediana global: 71.0)
  * **Defending Sliding Tackle**: ++2.0 (Mediana del clúster: 37.0 vs Mediana global: 35.0)
  * **Attacking Finishing**: ++1.5 (Mediana del clúster: 72.0 vs Mediana global: 70.5)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Passing**: -1.0 (Mediana del clúster: 69.0 vs Mediana global: 70.0)
  * **Movement Balance**: -1.0 (Mediana del clúster: 78.0 vs Mediana global: 79.0)
  * **Attacking Crossing**: -0.5 (Mediana del clúster: 70.0 vs Mediana global: 70.5)
  * **Pace**: -0.5 (Mediana del clúster: 82.0 vs Mediana global: 82.5)
  * **Movement Acceleration**: -0.5 (Mediana del clúster: 83.0 vs Mediana global: 83.5)

________________________________________

#### Clúster 2: **"Extremo Desequilibrante / Regateador Puro"** (Representante: Lamine Yamal Nasraoui Ebanaلامين يامال نصراوي إبانا - 89)

*Aislados estrictamente por su habilidad técnica en el uno contra uno, con +2.0 en regate, +1.5 en regate hábil y +2.0 en finalización. Tienen obligaciones defensivas nulas (-13.5 en intercepciones).*

- **Tamaño del grupo:** 40 jugadores.
- **Ejemplos en el dataset:** Lamine Yamal Nasraoui Ebanaلامين يامال نصراوي إبانا, Vinicius José Paixão de Oliveira Junior, Lionel Andrés Messi Cuccitini, Nicholas Williams Arthuer, Riyad Mahrezرياض محرز, Rafael Alexandre da Conceição Leão

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Attacking Finishing**: ++2.0 (Mediana del clúster: 72.5 vs Mediana global: 70.5)
  * **Dribbling**: ++2.0 (Mediana del clúster: 80.0 vs Mediana global: 78.0)
  * **Attacking Short Passing**: ++1.5 (Mediana del clúster: 73.5 vs Mediana global: 72.0)
  * **Skill Dribbling**: ++1.5 (Mediana del clúster: 80.5 vs Mediana global: 79.0)
  * **Power Shot Power**: ++1.5 (Mediana del clúster: 74.5 vs Mediana global: 73.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Mentality Interceptions**: -13.5 (Mediana del clúster: 25.5 vs Mediana global: 39.0)
  * **Mentality Aggression**: -10.5 (Mediana del clúster: 47.0 vs Mediana global: 57.5)
  * **Defending Marking Awareness**: -10.0 (Mediana del clúster: 29.0 vs Mediana global: 39.0)
  * **Defending Sliding Tackle**: -10.0 (Mediana del clúster: 25.0 vs Mediana global: 35.0)
  * **Defending**: -9.0 (Mediana del clúster: 30.0 vs Mediana global: 39.0)

________________________________________

#### Clúster 3: **"Volante Táctico / Extremo Defensivo"** (Representante: Bukayo Saka - 88)

*Ya sea por sacrificio táctico (Saka) o por error de etiqueta del juego (Grimaldo), este grupo se define por sus números irreales de defensa en ataque: +24.0 en barridas y +22.0 en intercepciones.*

- **Tamaño del grupo:** 33 jugadores.
- **Ejemplos en el dataset:** Bukayo Saka, Désiré Doué, Alejandro Grimaldo García, Alejandro Baena Rodríguez, Salem Al Dawsariسالم الدوسري, Ivan Perišić

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Defending Sliding Tackle**: ++24.0 (Mediana del clúster: 59.0 vs Mediana global: 35.0)
  * **Defending Standing Tackle**: ++24.0 (Mediana del clúster: 62.0 vs Mediana global: 38.0)
  * **Mentality Interceptions**: ++22.0 (Mediana del clúster: 61.0 vs Mediana global: 39.0)
  * **Defending Marking Awareness**: ++21.0 (Mediana del clúster: 60.0 vs Mediana global: 39.0)
  * **Defending**: ++20.0 (Mediana del clúster: 59.0 vs Mediana global: 39.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Shooting**: -3.0 (Mediana del clúster: 67.0 vs Mediana global: 70.0)
  * **Attacking Volleys**: -3.0 (Mediana del clúster: 61.0 vs Mediana global: 64.0)
  * **Skill Fk Accuracy**: -3.0 (Mediana del clúster: 57.0 vs Mediana global: 60.0)
  * **Movement Balance**: -3.0 (Mediana del clúster: 76.0 vs Mediana global: 79.0)
  * **Mentality Composure**: -3.0 (Mediana del clúster: 70.0 vs Mediana global: 73.0)

________________________________________


---
