# Perfilado de Clusters y Arquetipos de Jugadores

Este reporte analiza empíricamente los clústeres generados mediante **KMeans (Arquetipos >75)** con optimización dinámica de K.
Para cada clúster, comparamos la mediana de sus atributos físicos y técnicos contra la mediana global de su posición.
Las desviaciones positivas revelan las fortalezas características del arquetipo, mientras que las negativas señalan sus carencias.

---

## Goalkeepers (KMeans Arquetipos >75)
Total jugadores analizados: 75

| Clúster | Representante principal | Miembros | Atributos Destacados (Desviación vs Mediana Global) |
| :---: | :--- | :---: | :--- |
| Cluster 1 | Alisson Ramsés Becker (89) | 15 | **+23** en skill long passing, **+22** en attacking short passing, **+19** en skill ball control, **+17** en mentality composure, **+15** en mentality vision |
| Cluster 2 | Yvon Landry Mvogo Nganoma (76) | 3 | **+17** en movement balance, **+15** en movement agility, **+14** en defending marking awareness, **+11** en mentality aggression, **+7** en power jumping |
| Cluster 3 | Thibaut Nicolas Marc Courtois (89) | 20 | **+5** en mentality interceptions, **+5** en movement balance, **+4** en movement acceleration, **+4** en movement agility, **+4** en mentality penalties |
| Cluster 4 | Gregor Kobel (86) | 15 | **+9** en movement agility, **+9** en mentality composure, **+8** en attacking short passing, **+8** en skill long passing, **+6** en movement acceleration |
| Cluster 5 | Rui Tiago Dantas da Silva (81) | 7 | **+13** en mentality penalties, **+8** en attacking finishing, **+8** en attacking volleys, **+6** en mentality positioning, **+6** en defending marking awareness |
| Cluster 6 | Senne Lammens (78) | 15 |  |

### Análisis Detallado de Arquetipos por Clúster

#### Clúster 1: Representado por Alisson Ramsés Becker (89)
- **Tamaño del grupo:** 15 jugadores.
- **Ejemplos en el dataset:** Alisson Ramsés Becker, David Raya Martín, Mike Peterson Maignan, Ederson Santana de Moraes, Damián Emiliano Martínez Romero, Manuel Peter Neuer

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Skill Long Passing**: ++23.0 (Mediana del clúster: 58.0 vs Mediana global: 35.0)
  * **Attacking Short Passing**: ++22.0 (Mediana del clúster: 56.0 vs Mediana global: 34.0)
  * **Skill Ball Control**: ++19.0 (Mediana del clúster: 42.0 vs Mediana global: 23.0)
  * **Mentality Composure**: ++17.0 (Mediana del clúster: 65.0 vs Mediana global: 48.0)
  * **Mentality Vision**: ++15.0 (Mediana del clúster: 65.0 vs Mediana global: 50.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):

________________________________________

#### Clúster 2: Representado por Yvon Landry Mvogo Nganoma (76)
- **Tamaño del grupo:** 3 jugadores.
- **Ejemplos en el dataset:** Yvon Landry Mvogo Nganoma, Alexander Schlager, Luis Ricardo Mejía Cajar

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Movement Balance**: ++17.0 (Mediana del clúster: 57.0 vs Mediana global: 40.0)
  * **Movement Agility**: ++15.0 (Mediana del clúster: 58.0 vs Mediana global: 43.0)
  * **Defending Marking Awareness**: ++14.0 (Mediana del clúster: 28.0 vs Mediana global: 14.0)
  * **Mentality Aggression**: ++11.0 (Mediana del clúster: 37.0 vs Mediana global: 26.0)
  * **Power Jumping**: ++7.0 (Mediana del clúster: 71.0 vs Mediana global: 64.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Mentality Composure**: -17.0 (Mediana del clúster: 31.0 vs Mediana global: 48.0)
  * **Skill Long Passing**: -13.0 (Mediana del clúster: 22.0 vs Mediana global: 35.0)
  * **Attacking Short Passing**: -10.0 (Mediana del clúster: 24.0 vs Mediana global: 34.0)
  * **Power Stamina**: -4.0 (Mediana del clúster: 28.0 vs Mediana global: 32.0)
  * **Mentality Interceptions**: -2.0 (Mediana del clúster: 13.0 vs Mediana global: 15.0)

________________________________________

#### Clúster 3: Representado por Thibaut Nicolas Marc Courtois (89)
- **Tamaño del grupo:** 20 jugadores.
- **Ejemplos en el dataset:** Thibaut Nicolas Marc Courtois, Unai Simón Mendibil, Oliver Baumann, Gerónimo Rulli, Yassine Bounouياسين بونو, Néstor Fernando Muslera Micol

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Mentality Interceptions**: ++5.0 (Mediana del clúster: 20.0 vs Mediana global: 15.0)
  * **Movement Balance**: ++5.0 (Mediana del clúster: 45.0 vs Mediana global: 40.0)
  * **Movement Acceleration**: ++4.5 (Mediana del clúster: 46.5 vs Mediana global: 42.0)
  * **Movement Agility**: ++4.5 (Mediana del clúster: 47.5 vs Mediana global: 43.0)
  * **Mentality Penalties**: ++4.5 (Mediana del clúster: 20.5 vs Mediana global: 16.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Attacking Short Passing**: -2.0 (Mediana del clúster: 32.0 vs Mediana global: 34.0)
  * **Mentality Vision**: -1.5 (Mediana del clúster: 48.5 vs Mediana global: 50.0)
  * **Mentality Composure**: -1.0 (Mediana del clúster: 47.0 vs Mediana global: 48.0)
  * **Power Shot Power**: -1.0 (Mediana del clúster: 52.0 vs Mediana global: 53.0)
  * **Movement Reactions**: -0.5 (Mediana del clúster: 71.5 vs Mediana global: 72.0)

________________________________________

#### Clúster 4: Representado por Gregor Kobel (86)
- **Tamaño del grupo:** 15 jugadores.
- **Ejemplos en el dataset:** Gregor Kobel, Joan García Pons, Dean Bradley Henderson, Dominik Livaković, Édouard Osoque Mendy, Brice Lauriche Samba

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Movement Agility**: ++9.0 (Mediana del clúster: 52.0 vs Mediana global: 43.0)
  * **Mentality Composure**: ++9.0 (Mediana del clúster: 57.0 vs Mediana global: 48.0)
  * **Attacking Short Passing**: ++8.0 (Mediana del clúster: 42.0 vs Mediana global: 34.0)
  * **Skill Long Passing**: ++8.0 (Mediana del clúster: 43.0 vs Mediana global: 35.0)
  * **Movement Acceleration**: ++6.0 (Mediana del clúster: 48.0 vs Mediana global: 42.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Power Strength**: -4.0 (Mediana del clúster: 64.0 vs Mediana global: 68.0)
  * **Mentality Positioning**: -4.0 (Mediana del clúster: 7.0 vs Mediana global: 11.0)
  * **Attacking Volleys**: -3.0 (Mediana del clúster: 8.0 vs Mediana global: 11.0)
  * **Attacking Finishing**: -2.0 (Mediana del clúster: 8.0 vs Mediana global: 10.0)
  * **Power Long Shots**: -2.0 (Mediana del clúster: 9.0 vs Mediana global: 11.0)

________________________________________

#### Clúster 5: Representado por Rui Tiago Dantas da Silva (81)
- **Tamaño del grupo:** 7 jugadores.
- **Ejemplos en el dataset:** Rui Tiago Dantas da Silva, Juan Agustín Musso, Jindřich Staněk, Álvaro David Montero Perales, Bum-keun Song송범근, Mory Diaw

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Mentality Penalties**: ++13.0 (Mediana del clúster: 29.0 vs Mediana global: 16.0)
  * **Attacking Finishing**: ++8.0 (Mediana del clúster: 18.0 vs Mediana global: 10.0)
  * **Attacking Volleys**: ++8.0 (Mediana del clúster: 19.0 vs Mediana global: 11.0)
  * **Mentality Positioning**: ++6.0 (Mediana del clúster: 17.0 vs Mediana global: 11.0)
  * **Defending Marking Awareness**: ++6.0 (Mediana del clúster: 20.0 vs Mediana global: 14.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Movement Agility**: -11.0 (Mediana del clúster: 32.0 vs Mediana global: 43.0)
  * **Skill Long Passing**: -10.0 (Mediana del clúster: 25.0 vs Mediana global: 35.0)
  * **Movement Balance**: -9.0 (Mediana del clúster: 31.0 vs Mediana global: 40.0)
  * **Movement Sprint Speed**: -9.0 (Mediana del clúster: 35.0 vs Mediana global: 44.0)
  * **Movement Acceleration**: -6.0 (Mediana del clúster: 36.0 vs Mediana global: 42.0)

________________________________________

#### Clúster 6: Representado por Senne Lammens (78)
- **Tamaño del grupo:** 15 jugadores.
- **Ejemplos en el dataset:** Senne Lammens, Mário Ricardo da Silva Velho, Yahia Fofana, Robin Roefs, Zion Suzuki鈴木 彩艶, Dayne Tristan St. Clair

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Mentality Composure**: -17.0 (Mediana del clúster: 31.0 vs Mediana global: 48.0)
  * **Movement Acceleration**: -14.0 (Mediana del clúster: 28.0 vs Mediana global: 42.0)
  * **Mentality Vision**: -14.0 (Mediana del clúster: 36.0 vs Mediana global: 50.0)
  * **Skill Long Passing**: -14.0 (Mediana del clúster: 21.0 vs Mediana global: 35.0)
  * **Movement Balance**: -13.0 (Mediana del clúster: 27.0 vs Mediana global: 40.0)

________________________________________


---

## Centerbacks (KMeans Arquetipos >75)
Total jugadores analizados: 143

| Clúster | Representante principal | Miembros | Atributos Destacados (Desviación vs Mediana Global) |
| :---: | :--- | :---: | :--- |
| Cluster 1 | Virgil van Dijk (90) | 54 | **+8** en attacking finishing, **+8** en mentality positioning, **+7** en shooting, **+6** en power shot power, **+6** en attacking crossing |
| Cluster 2 | Gabriel dos Santos Magalhães (88) | 32 | **+4** en power shot power, **+2** en power strength, **+1** en mentality aggression, **+1** en defending, **+1** en defending marking awareness |
| Cluster 3 | Nathan Benjamin Aké (83) | 13 | **+22** en skill fk accuracy, **+21** en attacking volleys, **+21** en skill curve, **+21** en power long shots, **+20** en attacking crossing |
| Cluster 4 | Ibrahima Konaté (86) | 44 | **+2** en movement sprint speed, **+1** en pace, **+1** en movement acceleration |

### Análisis Detallado de Arquetipos por Clúster

#### Clúster 1: Representado por Virgil van Dijk (90)
- **Tamaño del grupo:** 54 jugadores.
- **Ejemplos en el dataset:** Virgil van Dijk, Marcos Aoás Corrêa, Antonio Rüdiger, Nico Cedric Schlotterbeck, Gleison Bremer Silva Nascimento, Ronald Federico Araújo da Silva

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Attacking Finishing**: ++8.0 (Mediana del clúster: 44.0 vs Mediana global: 36.0)
  * **Mentality Positioning**: ++8.0 (Mediana del clúster: 53.0 vs Mediana global: 45.0)
  * **Shooting**: ++7.0 (Mediana del clúster: 48.0 vs Mediana global: 41.0)
  * **Power Shot Power**: ++6.5 (Mediana del clúster: 62.5 vs Mediana global: 56.0)
  * **Attacking Crossing**: ++6.5 (Mediana del clúster: 54.5 vs Mediana global: 48.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Physic**: -0.5 (Mediana del clúster: 77.5 vs Mediana global: 78.0)
  * **Power Stamina**: -0.5 (Mediana del clúster: 71.5 vs Mediana global: 72.0)

________________________________________

#### Clúster 2: Representado por Gabriel dos Santos Magalhães (88)
- **Tamaño del grupo:** 32 jugadores.
- **Ejemplos en el dataset:** Gabriel dos Santos Magalhães, Jonathan Glao Tah, William Alain André Gabriel Saliba, Rúben dos Santos Gato Alves Dias, José María Giménez de Vargas, Aymeric Jean Louis Gerard Alphonse Laporte

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Power Shot Power**: ++4.5 (Mediana del clúster: 60.5 vs Mediana global: 56.0)
  * **Power Strength**: ++2.0 (Mediana del clúster: 83.0 vs Mediana global: 81.0)
  * **Mentality Aggression**: ++1.0 (Mediana del clúster: 78.0 vs Mediana global: 77.0)
  * **Defending**: ++1.0 (Mediana del clúster: 77.0 vs Mediana global: 76.0)
  * **Defending Marking Awareness**: ++1.0 (Mediana del clúster: 77.0 vs Mediana global: 76.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Movement Agility**: -12.5 (Mediana del clúster: 47.5 vs Mediana global: 60.0)
  * **Movement Acceleration**: -11.5 (Mediana del clúster: 53.5 vs Mediana global: 65.0)
  * **Movement Balance**: -10.5 (Mediana del clúster: 47.5 vs Mediana global: 58.0)
  * **Pace**: -10.0 (Mediana del clúster: 59.0 vs Mediana global: 69.0)
  * **Mentality Positioning**: -9.5 (Mediana del clúster: 35.5 vs Mediana global: 45.0)

________________________________________

#### Clúster 3: Representado por Nathan Benjamin Aké (83)
- **Tamaño del grupo:** 13 jugadores.
- **Ejemplos en el dataset:** Nathan Benjamin Aké, David Olatukunbo Alaba, Lisandro Martínez, Sead Kolašinac, Ladislav Krejčí, Axel Laurent Angel Lambert Witsel

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Skill Fk Accuracy**: ++22.0 (Mediana del clúster: 55.0 vs Mediana global: 33.0)
  * **Attacking Volleys**: ++21.0 (Mediana del clúster: 55.0 vs Mediana global: 34.0)
  * **Skill Curve**: ++21.0 (Mediana del clúster: 66.0 vs Mediana global: 45.0)
  * **Power Long Shots**: ++21.0 (Mediana del clúster: 60.0 vs Mediana global: 39.0)
  * **Attacking Crossing**: ++20.0 (Mediana del clúster: 68.0 vs Mediana global: 48.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Movement Sprint Speed**: -4.0 (Mediana del clúster: 67.0 vs Mediana global: 71.0)
  * **Physic**: -3.0 (Mediana del clúster: 75.0 vs Mediana global: 78.0)
  * **Power Strength**: -3.0 (Mediana del clúster: 78.0 vs Mediana global: 81.0)
  * **Pace**: -2.0 (Mediana del clúster: 67.0 vs Mediana global: 69.0)
  * **Power Jumping**: -2.0 (Mediana del clúster: 81.0 vs Mediana global: 83.0)

________________________________________

#### Clúster 4: Representado por Ibrahima Konaté (86)
- **Tamaño del grupo:** 44 jugadores.
- **Ejemplos en el dataset:** Ibrahima Konaté, Dayotchanculle Oswald Upamecano, Min-jae Kim김민재 金敏在, Pau Cubarsí Paredes, Roger Ibañez da Silva, Ousmane Diomande

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Movement Sprint Speed**: ++2.0 (Mediana del clúster: 73.0 vs Mediana global: 71.0)
  * **Pace**: ++1.5 (Mediana del clúster: 70.5 vs Mediana global: 69.0)
  * **Movement Acceleration**: ++1.0 (Mediana del clúster: 66.0 vs Mediana global: 65.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Attacking Crossing**: -13.0 (Mediana del clúster: 35.0 vs Mediana global: 48.0)
  * **Skill Curve**: -12.5 (Mediana del clúster: 32.5 vs Mediana global: 45.0)
  * **Power Long Shots**: -11.5 (Mediana del clúster: 27.5 vs Mediana global: 39.0)
  * **Power Shot Power**: -10.0 (Mediana del clúster: 46.0 vs Mediana global: 56.0)
  * **Mentality Positioning**: -10.0 (Mediana del clúster: 35.0 vs Mediana global: 45.0)

________________________________________


---

## Fullbacks (KMeans Arquetipos >75)
Total jugadores analizados: 101

| Clúster | Representante principal | Miembros | Atributos Destacados (Desviación vs Mediana Global) |
| :---: | :--- | :---: | :--- |
| Cluster 1 | Denzel Justus Morris Dumfries (84) | 20 | **+5** en mentality aggression, **+4** en attacking heading accuracy, **+3** en power strength, **+3** en defending marking awareness, **+3** en power jumping |
| Cluster 2 | Jules Olivier Koundé (87) | 18 | **+2** en defending, **+1** en mentality interceptions, **+1** en movement sprint speed, **+1** en mentality composure, **+0** en attacking short passing |
| Cluster 3 | Achraf Hakimi Mouhأشرف حكيمي (89) | 28 | **+13** en skill fk accuracy, **+11** en attacking volleys, **+11** en mentality penalties, **+11** en power shot power, **+10** en power long shots |
| Cluster 4 | Nuno Alexandre Tavares Mendes (86) | 35 | **+4** en skill fk accuracy, **+4** en movement acceleration, **+4** en movement agility, **+3** en pace, **+3** en movement sprint speed |

### Análisis Detallado de Arquetipos por Clúster

#### Clúster 1: Representado por Denzel Justus Morris Dumfries (84)
- **Tamaño del grupo:** 20 jugadores.
- **Ejemplos en el dataset:** Denzel Justus Morris Dumfries, Konrad Laimer, Daniel Muñoz Mejía, Noussair Mazraouiنصير مزراوي, Julian Ryerson, Stefan Posch

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Mentality Aggression**: ++5.5 (Mediana del clúster: 78.5 vs Mediana global: 73.0)
  * **Attacking Heading Accuracy**: ++4.0 (Mediana del clúster: 68.0 vs Mediana global: 64.0)
  * **Power Strength**: ++3.5 (Mediana del clúster: 74.5 vs Mediana global: 71.0)
  * **Defending Marking Awareness**: ++3.0 (Mediana del clúster: 75.0 vs Mediana global: 72.0)
  * **Power Jumping**: ++3.0 (Mediana del clúster: 80.0 vs Mediana global: 77.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Skill Fk Accuracy**: -9.0 (Mediana del clúster: 41.0 vs Mediana global: 50.0)
  * **Movement Balance**: -6.5 (Mediana del clúster: 67.5 vs Mediana global: 74.0)
  * **Movement Agility**: -5.0 (Mediana del clúster: 70.0 vs Mediana global: 75.0)
  * **Power Long Shots**: -5.0 (Mediana del clúster: 54.0 vs Mediana global: 59.0)
  * **Movement Sprint Speed**: -4.5 (Mediana del clúster: 73.5 vs Mediana global: 78.0)

________________________________________

#### Clúster 2: Representado por Jules Olivier Koundé (87)
- **Tamaño del grupo:** 18 jugadores.
- **Ejemplos en el dataset:** Jules Olivier Koundé, Antonee Robinson, Jurriën David Norman Timber, Valentino Francisco Livramento, Aaron Wan-Bissaka, Malo Gusto

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Defending**: ++2.0 (Mediana del clúster: 73.0 vs Mediana global: 71.0)
  * **Mentality Interceptions**: ++1.5 (Mediana del clúster: 72.5 vs Mediana global: 71.0)
  * **Movement Sprint Speed**: ++1.0 (Mediana del clúster: 79.0 vs Mediana global: 78.0)
  * **Mentality Composure**: ++1.0 (Mediana del clúster: 74.0 vs Mediana global: 73.0)
  * **Attacking Short Passing**: ++0.5 (Mediana del clúster: 74.5 vs Mediana global: 74.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Power Long Shots**: -17.5 (Mediana del clúster: 41.5 vs Mediana global: 59.0)
  * **Attacking Finishing**: -15.5 (Mediana del clúster: 40.5 vs Mediana global: 56.0)
  * **Shooting**: -14.0 (Mediana del clúster: 45.0 vs Mediana global: 59.0)
  * **Skill Fk Accuracy**: -13.5 (Mediana del clúster: 36.5 vs Mediana global: 50.0)
  * **Power Shot Power**: -10.5 (Mediana del clúster: 55.5 vs Mediana global: 66.0)

________________________________________

#### Clúster 3: Representado por Achraf Hakimi Mouhأشرف حكيمي (89)
- **Tamaño del grupo:** 28 jugadores.
- **Ejemplos en el dataset:** Achraf Hakimi Mouhأشرف حكيمي, Theo Bernard François Hernández, Marcos Llorente Moreno, João Pedro Cavaco Cancelo, Joško Gvardiol, Pedro Antonio Porro Sauceda

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Skill Fk Accuracy**: ++13.0 (Mediana del clúster: 63.0 vs Mediana global: 50.0)
  * **Attacking Volleys**: ++11.5 (Mediana del clúster: 60.5 vs Mediana global: 49.0)
  * **Mentality Penalties**: ++11.5 (Mediana del clúster: 59.5 vs Mediana global: 48.0)
  * **Power Shot Power**: ++11.0 (Mediana del clúster: 77.0 vs Mediana global: 66.0)
  * **Power Long Shots**: ++10.0 (Mediana del clúster: 69.0 vs Mediana global: 59.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Movement Agility**: -3.0 (Mediana del clúster: 72.0 vs Mediana global: 75.0)
  * **Movement Balance**: -3.0 (Mediana del clúster: 71.0 vs Mediana global: 74.0)
  * **Pace**: -2.0 (Mediana del clúster: 77.0 vs Mediana global: 79.0)
  * **Movement Acceleration**: -1.0 (Mediana del clúster: 77.0 vs Mediana global: 78.0)
  * **Movement Sprint Speed**: -1.0 (Mediana del clúster: 77.0 vs Mediana global: 78.0)

________________________________________

#### Clúster 4: Representado por Nuno Alexandre Tavares Mendes (86)
- **Tamaño del grupo:** 35 jugadores.
- **Ejemplos en el dataset:** Nuno Alexandre Tavares Mendes, Alphonso Boyle Davies, Marc Cucurella Saseta, David Raum, Rayan Aït Nouriريان آيت نوري, Sergiño Gianni Dest

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Skill Fk Accuracy**: ++4.0 (Mediana del clúster: 54.0 vs Mediana global: 50.0)
  * **Movement Acceleration**: ++4.0 (Mediana del clúster: 82.0 vs Mediana global: 78.0)
  * **Movement Agility**: ++4.0 (Mediana del clúster: 79.0 vs Mediana global: 75.0)
  * **Pace**: ++3.0 (Mediana del clúster: 82.0 vs Mediana global: 79.0)
  * **Movement Sprint Speed**: ++3.0 (Mediana del clúster: 81.0 vs Mediana global: 78.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Attacking Heading Accuracy**: -6.0 (Mediana del clúster: 58.0 vs Mediana global: 64.0)
  * **Mentality Aggression**: -4.0 (Mediana del clúster: 69.0 vs Mediana global: 73.0)
  * **Defending Marking Awareness**: -4.0 (Mediana del clúster: 68.0 vs Mediana global: 72.0)
  * **Mentality Penalties**: -3.0 (Mediana del clúster: 45.0 vs Mediana global: 48.0)
  * **Attacking Finishing**: -2.0 (Mediana del clúster: 54.0 vs Mediana global: 56.0)

________________________________________


---

## Midfielders (KMeans Arquetipos >75)
Total jugadores analizados: 196

| Clúster | Representante principal | Miembros | Atributos Destacados (Desviación vs Mediana Global) |
| :---: | :--- | :---: | :--- |
| Cluster 1 | Rodrigo Hernández Cascante (90) | 54 | **+10** en attacking heading accuracy, **+8** en mentality aggression, **+7** en defending marking awareness, **+7** en defending, **+6** en defending sliding tackle |
| Cluster 2 | Florian Richard Wirtz (89) | 35 | **+7** en attacking volleys, **+6** en pace, **+6** en movement acceleration, **+6** en movement balance, **+6** en movement sprint speed |
| Cluster 3 | Jude Victor William Bellingham (90) | 107 | **+3** en skill fk accuracy, **+2** en attacking volleys, **+2** en movement balance, **+2** en passing, **+1** en mentality vision |

### Análisis Detallado de Arquetipos por Clúster

#### Clúster 1: Representado por Rodrigo Hernández Cascante (90)
- **Tamaño del grupo:** 54 jugadores.
- **Ejemplos en el dataset:** Rodrigo Hernández Cascante, Declan Rice, Granit Xhaka, N'Golo Kanté, Scott Francis McTominay, Aurélien Djani Tchouameni

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Attacking Heading Accuracy**: ++10.0 (Mediana del clúster: 72.0 vs Mediana global: 62.0)
  * **Mentality Aggression**: ++8.0 (Mediana del clúster: 82.0 vs Mediana global: 74.0)
  * **Defending Marking Awareness**: ++7.0 (Mediana del clúster: 76.0 vs Mediana global: 69.0)
  * **Defending**: ++7.0 (Mediana del clúster: 76.5 vs Mediana global: 69.5)
  * **Defending Sliding Tackle**: ++6.0 (Mediana del clúster: 74.0 vs Mediana global: 68.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Movement Agility**: -9.0 (Mediana del clúster: 67.0 vs Mediana global: 76.0)
  * **Skill Fk Accuracy**: -9.0 (Mediana del clúster: 54.0 vs Mediana global: 63.0)
  * **Movement Balance**: -8.0 (Mediana del clúster: 67.0 vs Mediana global: 75.0)
  * **Movement Acceleration**: -6.5 (Mediana del clúster: 65.5 vs Mediana global: 72.0)
  * **Attacking Volleys**: -6.0 (Mediana del clúster: 55.0 vs Mediana global: 61.0)

________________________________________

#### Clúster 2: Representado por Florian Richard Wirtz (89)
- **Tamaño del grupo:** 35 jugadores.
- **Ejemplos en el dataset:** Florian Richard Wirtz, Jamal Musiala, Daniel Olmo Carvajal, Eberechi Oluchi Eze, Matheus Santos Carneiro da Cunha, Francisco António Machado Mota de Castro Trincão

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Attacking Volleys**: ++7.0 (Mediana del clúster: 68.0 vs Mediana global: 61.0)
  * **Pace**: ++6.5 (Mediana del clúster: 77.0 vs Mediana global: 70.5)
  * **Movement Acceleration**: ++6.0 (Mediana del clúster: 78.0 vs Mediana global: 72.0)
  * **Movement Balance**: ++6.0 (Mediana del clúster: 81.0 vs Mediana global: 75.0)
  * **Movement Sprint Speed**: ++6.0 (Mediana del clúster: 75.0 vs Mediana global: 69.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Defending Marking Awareness**: -25.0 (Mediana del clúster: 44.0 vs Mediana global: 69.0)
  * **Defending Sliding Tackle**: -24.0 (Mediana del clúster: 44.0 vs Mediana global: 68.0)
  * **Mentality Interceptions**: -23.0 (Mediana del clúster: 49.0 vs Mediana global: 72.0)
  * **Defending Standing Tackle**: -22.0 (Mediana del clúster: 50.0 vs Mediana global: 72.0)
  * **Defending**: -19.5 (Mediana del clúster: 50.0 vs Mediana global: 69.5)

________________________________________

#### Clúster 3: Representado por Jude Victor William Bellingham (90)
- **Tamaño del grupo:** 107 jugadores.
- **Ejemplos en el dataset:** Jude Victor William Bellingham, Joshua Walter Kimmich, Federico Santiago Valverde Dipetta, Pedro González López, Vítor Machado Ferreira, Frenkie de Jong

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Skill Fk Accuracy**: ++3.0 (Mediana del clúster: 66.0 vs Mediana global: 63.0)
  * **Attacking Volleys**: ++2.0 (Mediana del clúster: 63.0 vs Mediana global: 61.0)
  * **Movement Balance**: ++2.0 (Mediana del clúster: 77.0 vs Mediana global: 75.0)
  * **Passing**: ++2.0 (Mediana del clúster: 76.0 vs Mediana global: 74.0)
  * **Mentality Vision**: ++1.5 (Mediana del clúster: 78.0 vs Mediana global: 76.5)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Attacking Heading Accuracy**: -2.0 (Mediana del clúster: 60.0 vs Mediana global: 62.0)
  * **Power Shot Power**: -1.5 (Mediana del clúster: 74.0 vs Mediana global: 75.5)
  * **Power Strength**: -1.5 (Mediana del clúster: 69.0 vs Mediana global: 70.5)
  * **Power Jumping**: -1.0 (Mediana del clúster: 72.0 vs Mediana global: 73.0)
  * **Pace**: -0.5 (Mediana del clúster: 70.0 vs Mediana global: 70.5)

________________________________________


---

## Strikers (KMeans Arquetipos >75)
Total jugadores analizados: 90

| Clúster | Representante principal | Miembros | Atributos Destacados (Desviación vs Mediana Global) |
| :---: | :--- | :---: | :--- |
| Cluster 1 | Kylian Mbappé Lottin (91) | 23 | **+8** en skill fk accuracy, **+6** en movement agility, **+6** en movement balance, **+5** en movement acceleration, **+5** en movement sprint speed |
| Cluster 2 | Masour Ousmane Dembélé (90) | 34 | **+11** en defending sliding tackle, **+11** en mentality interceptions, **+10** en defending standing tackle, **+8** en defending, **+7** en defending marking awareness |
| Cluster 3 | Cristiano Ronaldo dos Santos Aveiro (85) | 33 | **+5** en power strength, **+2** en physic, **+2** en attacking heading accuracy, **+2** en mentality aggression, **+1** en power jumping |

### Análisis Detallado de Arquetipos por Clúster

#### Clúster 1: Representado por Kylian Mbappé Lottin (91)
- **Tamaño del grupo:** 23 jugadores.
- **Ejemplos en el dataset:** Kylian Mbappé Lottin, Alexander Isak, Viktor Einar Gyökeres, Omar Khaled Mohamed Marmoush, Yoane Wissa, Jonathan Christian David

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Skill Fk Accuracy**: ++8.0 (Mediana del clúster: 63.0 vs Mediana global: 55.0)
  * **Movement Agility**: ++6.0 (Mediana del clúster: 76.0 vs Mediana global: 70.0)
  * **Movement Balance**: ++6.0 (Mediana del clúster: 73.0 vs Mediana global: 67.0)
  * **Movement Acceleration**: ++5.5 (Mediana del clúster: 80.0 vs Mediana global: 74.5)
  * **Movement Sprint Speed**: ++5.5 (Mediana del clúster: 83.0 vs Mediana global: 77.5)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Defending Marking Awareness**: -10.0 (Mediana del clúster: 25.0 vs Mediana global: 35.0)
  * **Mentality Aggression**: -7.0 (Mediana del clúster: 61.0 vs Mediana global: 68.0)
  * **Power Strength**: -6.0 (Mediana del clúster: 73.0 vs Mediana global: 79.0)
  * **Defending**: -5.5 (Mediana del clúster: 31.0 vs Mediana global: 36.5)
  * **Physic**: -5.5 (Mediana del clúster: 71.0 vs Mediana global: 76.5)

________________________________________

#### Clúster 2: Representado por Masour Ousmane Dembélé (90)
- **Tamaño del grupo:** 34 jugadores.
- **Ejemplos en el dataset:** Masour Ousmane Dembélé, Harry Edward Kane, Lautaro Javier Martínez, Julián Álvarez, Marcus Lilian Thuram-Ulien, Kai Lukas Havertz

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Defending Sliding Tackle**: ++11.5 (Mediana del clúster: 38.5 vs Mediana global: 27.0)
  * **Mentality Interceptions**: ++11.5 (Mediana del clúster: 43.0 vs Mediana global: 31.5)
  * **Defending Standing Tackle**: ++10.5 (Mediana del clúster: 44.0 vs Mediana global: 33.5)
  * **Defending**: ++8.5 (Mediana del clúster: 45.0 vs Mediana global: 36.5)
  * **Defending Marking Awareness**: ++7.0 (Mediana del clúster: 42.0 vs Mediana global: 35.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Power Strength**: -3.0 (Mediana del clúster: 76.0 vs Mediana global: 79.0)
  * **Physic**: -2.5 (Mediana del clúster: 74.0 vs Mediana global: 76.5)
  * **Attacking Heading Accuracy**: -1.0 (Mediana del clúster: 74.0 vs Mediana global: 75.0)
  * **Power Jumping**: -1.0 (Mediana del clúster: 84.0 vs Mediana global: 85.0)
  * **Mentality Penalties**: -1.0 (Mediana del clúster: 70.0 vs Mediana global: 71.0)

________________________________________

#### Clúster 3: Representado por Cristiano Ronaldo dos Santos Aveiro (85)
- **Tamaño del grupo:** 33 jugadores.
- **Ejemplos en el dataset:** Cristiano Ronaldo dos Santos Aveiro, Patrik Schick, Romelu Menama Lukaku Bolingoli, Alexander Sørloth, Ante Budimir, Jean-Philippe Mateta

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Power Strength**: ++5.0 (Mediana del clúster: 84.0 vs Mediana global: 79.0)
  * **Physic**: ++2.5 (Mediana del clúster: 79.0 vs Mediana global: 76.5)
  * **Attacking Heading Accuracy**: ++2.0 (Mediana del clúster: 77.0 vs Mediana global: 75.0)
  * **Mentality Aggression**: ++2.0 (Mediana del clúster: 70.0 vs Mediana global: 68.0)
  * **Power Jumping**: ++1.0 (Mediana del clúster: 86.0 vs Mediana global: 85.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Movement Balance**: -12.0 (Mediana del clúster: 55.0 vs Mediana global: 67.0)
  * **Movement Agility**: -12.0 (Mediana del clúster: 58.0 vs Mediana global: 70.0)
  * **Movement Acceleration**: -9.5 (Mediana del clúster: 65.0 vs Mediana global: 74.5)
  * **Pace**: -9.0 (Mediana del clúster: 68.0 vs Mediana global: 77.0)
  * **Movement Sprint Speed**: -8.5 (Mediana del clúster: 69.0 vs Mediana global: 77.5)

________________________________________


---

## Wingers (KMeans Arquetipos >75)
Total jugadores analizados: 108

| Clúster | Representante principal | Miembros | Atributos Destacados (Desviación vs Mediana Global) |
| :---: | :--- | :---: | :--- |
| Cluster 1 | Raphael Dias Belloli (89) | 41 | **+6** en defending sliding tackle, **+5** en defending standing tackle, **+5** en defending, **+3** en defending marking awareness, **+2** en mentality aggression |
| Cluster 2 | Vinicius José Paixão de Oliveira Junior (89) | 48 | **+2** en mentality penalties, **+2** en movement acceleration, **+1** en pace, **+1** en movement sprint speed, **+1** en attacking finishing |
| Cluster 3 | Alejandro Grimaldo García (84) | 19 | **+28** en defending standing tackle, **+28** en defending sliding tackle, **+27** en mentality interceptions, **+26** en defending, **+26** en defending marking awareness |

### Análisis Detallado de Arquetipos por Clúster

#### Clúster 1: Representado por Raphael Dias Belloli (89)
- **Tamaño del grupo:** 41 jugadores.
- **Ejemplos en el dataset:** Raphael Dias Belloli, Bukayo Saka, Michael Akpovie Olise, Luis Fernando Díaz Marulanda, Désiré Doué, Cody Mathès Gakpo

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Defending Sliding Tackle**: ++6.0 (Mediana del clúster: 41.0 vs Mediana global: 35.0)
  * **Defending Standing Tackle**: ++5.5 (Mediana del clúster: 43.0 vs Mediana global: 37.5)
  * **Defending**: ++5.0 (Mediana del clúster: 44.0 vs Mediana global: 39.0)
  * **Defending Marking Awareness**: ++3.0 (Mediana del clúster: 42.0 vs Mediana global: 39.0)
  * **Mentality Aggression**: ++2.0 (Mediana del clúster: 59.0 vs Mediana global: 57.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Attacking Heading Accuracy**: -1.0 (Mediana del clúster: 49.0 vs Mediana global: 50.0)
  * **Attacking Volleys**: -1.0 (Mediana del clúster: 63.0 vs Mediana global: 64.0)
  * **Movement Acceleration**: -1.0 (Mediana del clúster: 83.0 vs Mediana global: 84.0)
  * **Movement Sprint Speed**: -1.0 (Mediana del clúster: 81.0 vs Mediana global: 82.0)
  * **Mentality Composure**: -1.0 (Mediana del clúster: 73.0 vs Mediana global: 74.0)

________________________________________

#### Clúster 2: Representado por Vinicius José Paixão de Oliveira Junior (89)
- **Tamaño del grupo:** 48 jugadores.
- **Ejemplos en el dataset:** Vinicius José Paixão de Oliveira Junior, Lamine Yamal Nasraoui Ebanaلامين يامال نصراوي إبانا, Nicholas Williams Arthuer, Heung-min Son손흥민 孙兴慜, Rafael Alexandre da Conceição Leão, Bradley Barcola

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Mentality Penalties**: ++2.0 (Mediana del clúster: 62.0 vs Mediana global: 60.0)
  * **Movement Acceleration**: ++2.0 (Mediana del clúster: 86.0 vs Mediana global: 84.0)
  * **Pace**: ++1.5 (Mediana del clúster: 84.0 vs Mediana global: 82.5)
  * **Movement Sprint Speed**: ++1.5 (Mediana del clúster: 83.5 vs Mediana global: 82.0)
  * **Attacking Finishing**: ++1.5 (Mediana del clúster: 73.5 vs Mediana global: 72.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Mentality Interceptions**: -11.0 (Mediana del clúster: 28.0 vs Mediana global: 39.0)
  * **Mentality Aggression**: -9.0 (Mediana del clúster: 48.0 vs Mediana global: 57.0)
  * **Defending Sliding Tackle**: -8.0 (Mediana del clúster: 27.0 vs Mediana global: 35.0)
  * **Defending Marking Awareness**: -7.0 (Mediana del clúster: 32.0 vs Mediana global: 39.0)
  * **Defending**: -6.5 (Mediana del clúster: 32.5 vs Mediana global: 39.0)

________________________________________

#### Clúster 3: Representado por Alejandro Grimaldo García (84)
- **Tamaño del grupo:** 19 jugadores.
- **Ejemplos en el dataset:** Alejandro Grimaldo García, Alejandro Baena Rodríguez, John McGinn, Ivan Perišić, Daizen Maeda前田 大然, Dan Assane Ndoye

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Defending Standing Tackle**: ++28.5 (Mediana del clúster: 66.0 vs Mediana global: 37.5)
  * **Defending Sliding Tackle**: ++28.0 (Mediana del clúster: 63.0 vs Mediana global: 35.0)
  * **Mentality Interceptions**: ++27.0 (Mediana del clúster: 66.0 vs Mediana global: 39.0)
  * **Defending**: ++26.0 (Mediana del clúster: 65.0 vs Mediana global: 39.0)
  * **Defending Marking Awareness**: ++26.0 (Mediana del clúster: 65.0 vs Mediana global: 39.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Shooting**: -4.0 (Mediana del clúster: 67.0 vs Mediana global: 71.0)
  * **Attacking Finishing**: -4.0 (Mediana del clúster: 68.0 vs Mediana global: 72.0)
  * **Mentality Penalties**: -4.0 (Mediana del clúster: 56.0 vs Mediana global: 60.0)
  * **Skill Fk Accuracy**: -3.5 (Mediana del clúster: 57.0 vs Mediana global: 60.5)
  * **Movement Balance**: -3.0 (Mediana del clúster: 76.0 vs Mediana global: 79.0)

________________________________________


---
