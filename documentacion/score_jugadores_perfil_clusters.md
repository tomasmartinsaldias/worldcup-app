# Perfilado de Clusters y Arquetipos de Jugadores

Este reporte analiza empíricamente los clústeres generados mediante **KMeans (Arquetipos >75)** con optimización dinámica de K.
Para cada clúster, comparamos la mediana de sus atributos físicos y técnicos contra la mediana global de su posición.
Las desviaciones positivas revelan las fortalezas características del arquetipo, mientras que las negativas señalan sus carencias.

---

## Goalkeepers (KMeans Arquetipos >75)
Total jugadores analizados: 40

| Clúster | Representante principal | Miembros | Atributos Destacados (Desviación vs Mediana Global) |
| :---: | :--- | :---: | :--- |
| Cluster 1 | David Raya Martín (87) | 6 | **+18** en mentality vision, **+13** en skill ball control, **+11** en mentality composure, **+9** en defending marking awareness, **+9** en mentality penalties |
| Cluster 2 | Unai Simón Mendibil (85) | 20 | **+9** en movement agility, **+6** en movement acceleration, **+2** en movement sprint speed, **+1** en power stamina, **+0** en movement balance |
| Cluster 3 | Alisson Ramsés Becker (89) | 14 | **+7** en mentality vision, **+6** en mentality composure, **+5** en skill long passing, **+4** en movement reactions, **+4** en attacking short passing |

### Análisis Detallado de Arquetipos por Clúster

#### Clúster 1: Representado por David Raya Martín (87)
- **Tamaño del grupo:** 6 jugadores.
- **Ejemplos en el dataset:** David Raya Martín, Ederson Santana de Moraes, Alexander Nübel, Jindřich Staněk, Alexander Schlager, Mory Diaw

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Mentality Vision**: ++18.5 (Mediana del clúster: 63.0 vs Mediana global: 44.5)
  * **Skill Ball Control**: ++13.5 (Mediana del clúster: 34.0 vs Mediana global: 20.5)
  * **Mentality Composure**: ++11.0 (Mediana del clúster: 58.0 vs Mediana global: 47.0)
  * **Defending Marking Awareness**: ++9.5 (Mediana del clúster: 23.5 vs Mediana global: 14.0)
  * **Mentality Penalties**: ++9.5 (Mediana del clúster: 27.5 vs Mediana global: 18.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Movement Agility**: -5.0 (Mediana del clúster: 34.0 vs Mediana global: 39.0)

________________________________________

#### Clúster 2: Representado por Unai Simón Mendibil (85)
- **Tamaño del grupo:** 20 jugadores.
- **Ejemplos en el dataset:** Unai Simón Mendibil, Joan García Pons, Bart Verbruggen, Yehvann Diouf, David Ospina Ramírez, Yahia Fofana

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Movement Agility**: ++9.5 (Mediana del clúster: 48.5 vs Mediana global: 39.0)
  * **Movement Acceleration**: ++6.0 (Mediana del clúster: 48.0 vs Mediana global: 42.0)
  * **Movement Sprint Speed**: ++2.5 (Mediana del clúster: 46.5 vs Mediana global: 44.0)
  * **Power Stamina**: ++1.0 (Mediana del clúster: 31.0 vs Mediana global: 30.0)
  * **Movement Balance**: ++0.5 (Mediana del clúster: 38.0 vs Mediana global: 37.5)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Mentality Composure**: -6.5 (Mediana del clúster: 40.5 vs Mediana global: 47.0)
  * **Mentality Vision**: -6.0 (Mediana del clúster: 38.5 vs Mediana global: 44.5)
  * **Power Strength**: -5.5 (Mediana del clúster: 63.5 vs Mediana global: 69.0)
  * **Attacking Short Passing**: -5.0 (Mediana del clúster: 30.5 vs Mediana global: 35.5)
  * **Skill Ball Control**: -4.5 (Mediana del clúster: 16.0 vs Mediana global: 20.5)

________________________________________

#### Clúster 3: Representado por Alisson Ramsés Becker (89)
- **Tamaño del grupo:** 14 jugadores.
- **Ejemplos en el dataset:** Alisson Ramsés Becker, Gregor Kobel, Oliver Baumann, Yassine Bounouياسين بونو, Gerónimo Rulli, Senne Lammens

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Mentality Vision**: ++7.5 (Mediana del clúster: 52.0 vs Mediana global: 44.5)
  * **Mentality Composure**: ++6.5 (Mediana del clúster: 53.5 vs Mediana global: 47.0)
  * **Skill Long Passing**: ++5.5 (Mediana del clúster: 38.5 vs Mediana global: 33.0)
  * **Movement Reactions**: ++4.5 (Mediana del clúster: 74.5 vs Mediana global: 70.0)
  * **Attacking Short Passing**: ++4.0 (Mediana del clúster: 39.5 vs Mediana global: 35.5)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Movement Sprint Speed**: -7.0 (Mediana del clúster: 37.0 vs Mediana global: 44.0)
  * **Movement Balance**: -6.0 (Mediana del clúster: 31.5 vs Mediana global: 37.5)
  * **Movement Acceleration**: -5.5 (Mediana del clúster: 36.5 vs Mediana global: 42.0)
  * **Attacking Heading Accuracy**: -2.0 (Mediana del clúster: 12.0 vs Mediana global: 14.0)
  * **Skill Ball Control**: -1.0 (Mediana del clúster: 19.5 vs Mediana global: 20.5)

________________________________________


---

## Centerbacks (KMeans Arquetipos >75)
Total jugadores analizados: 74

| Clúster | Representante principal | Miembros | Atributos Destacados (Desviación vs Mediana Global) |
| :---: | :--- | :---: | :--- |
| Cluster 1 | John Stones (82) | 9 | **+25** en power long shots, **+24** en attacking crossing, **+21** en skill fk accuracy, **+21** en attacking volleys, **+21** en power shot power |
| Cluster 2 | Ibrahima Konaté (86) | 32 | **+0** en power strength |
| Cluster 3 | Virgil van Dijk (90) | 10 | **+18** en power shot power, **+14** en skill fk accuracy, **+14** en power long shots, **+12** en skill curve, **+8** en mentality penalties |
| Cluster 4 | Gleison Bremer Silva Nascimento (85) | 23 | **+10** en attacking crossing, **+9** en mentality positioning, **+6** en attacking finishing, **+6** en power long shots, **+6** en skill dribbling |

### Análisis Detallado de Arquetipos por Clúster

#### Clúster 1: Representado por John Stones (82)
- **Tamaño del grupo:** 9 jugadores.
- **Ejemplos en el dataset:** John Stones, Lisandro Martínez, Danilo Luís Hélio Pereira, Sead Kolašinac, Ladislav Krejčí, Hiroki Ito伊藤 洋輝

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Power Long Shots**: ++25.5 (Mediana del clúster: 63.0 vs Mediana global: 37.5)
  * **Attacking Crossing**: ++24.0 (Mediana del clúster: 68.0 vs Mediana global: 44.0)
  * **Skill Fk Accuracy**: ++21.5 (Mediana del clúster: 53.0 vs Mediana global: 31.5)
  * **Attacking Volleys**: ++21.5 (Mediana del clúster: 55.0 vs Mediana global: 33.5)
  * **Power Shot Power**: ++21.0 (Mediana del clúster: 73.0 vs Mediana global: 52.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Movement Sprint Speed**: -6.0 (Mediana del clúster: 67.0 vs Mediana global: 73.0)
  * **Pace**: -2.5 (Mediana del clúster: 67.0 vs Mediana global: 69.5)

________________________________________

#### Clúster 2: Representado por Ibrahima Konaté (86)
- **Tamaño del grupo:** 32 jugadores.
- **Ejemplos en el dataset:** Ibrahima Konaté, Ousmane Diomande, Odilon Kossounou Kouakou, Philipp Lienhart, Guy Maxence Lacroix, Kevin Danso

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Power Strength**: ++0.5 (Mediana del clúster: 80.5 vs Mediana global: 80.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Mentality Positioning**: -12.5 (Mediana del clúster: 31.5 vs Mediana global: 44.0)
  * **Power Long Shots**: -11.5 (Mediana del clúster: 26.0 vs Mediana global: 37.5)
  * **Skill Curve**: -10.5 (Mediana del clúster: 30.5 vs Mediana global: 41.0)
  * **Attacking Crossing**: -9.0 (Mediana del clúster: 35.0 vs Mediana global: 44.0)
  * **Skill Dribbling**: -9.0 (Mediana del clúster: 53.0 vs Mediana global: 62.0)

________________________________________

#### Clúster 3: Representado por Virgil van Dijk (90)
- **Tamaño del grupo:** 10 jugadores.
- **Ejemplos en el dataset:** Virgil van Dijk, Antonio Rüdiger, Kalidou Koulibaly, Nayef Aguerdنايف أكرد, Jan Paul van Hecke, Diego Carlos Santos Silva

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Power Shot Power**: ++18.0 (Mediana del clúster: 70.0 vs Mediana global: 52.0)
  * **Skill Fk Accuracy**: ++14.5 (Mediana del clúster: 46.0 vs Mediana global: 31.5)
  * **Power Long Shots**: ++14.5 (Mediana del clúster: 52.0 vs Mediana global: 37.5)
  * **Skill Curve**: ++12.5 (Mediana del clúster: 53.5 vs Mediana global: 41.0)
  * **Mentality Penalties**: ++8.5 (Mediana del clúster: 49.5 vs Mediana global: 41.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Movement Balance**: -7.0 (Mediana del clúster: 49.5 vs Mediana global: 56.5)
  * **Movement Agility**: -5.5 (Mediana del clúster: 54.0 vs Mediana global: 59.5)
  * **Movement Acceleration**: -2.0 (Mediana del clúster: 63.0 vs Mediana global: 65.0)

________________________________________

#### Clúster 4: Representado por Gleison Bremer Silva Nascimento (85)
- **Tamaño del grupo:** 23 jugadores.
- **Ejemplos en el dataset:** Gleison Bremer Silva Nascimento, Pau Cubarsí Paredes, Ezri Konsa Ngoyo, Micky van de Ven, Waldemar AntonРипцов-Антон Владимир Александрович, Davinson Sánchez Mina

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Attacking Crossing**: ++10.0 (Mediana del clúster: 54.0 vs Mediana global: 44.0)
  * **Mentality Positioning**: ++9.0 (Mediana del clúster: 53.0 vs Mediana global: 44.0)
  * **Attacking Finishing**: ++6.5 (Mediana del clúster: 41.0 vs Mediana global: 34.5)
  * **Power Long Shots**: ++6.5 (Mediana del clúster: 44.0 vs Mediana global: 37.5)
  * **Skill Dribbling**: ++6.0 (Mediana del clúster: 68.0 vs Mediana global: 62.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Power Strength**: -3.0 (Mediana del clúster: 77.0 vs Mediana global: 80.0)
  * **Mentality Composure**: -2.0 (Mediana del clúster: 70.0 vs Mediana global: 72.0)
  * **Mentality Aggression**: -1.0 (Mediana del clúster: 75.0 vs Mediana global: 76.0)
  * **Physic**: -1.0 (Mediana del clúster: 76.0 vs Mediana global: 77.0)
  * **Power Stamina**: -0.5 (Mediana del clúster: 70.0 vs Mediana global: 70.5)

________________________________________


---

## Fullbacks (KMeans Arquetipos >75)
Total jugadores analizados: 60

| Clúster | Representante principal | Miembros | Atributos Destacados (Desviación vs Mediana Global) |
| :---: | :--- | :---: | :--- |
| Cluster 1 | Marc Cucurella Saseta (84) | 29 | **+4** en pace, **+4** en movement sprint speed, **+4** en movement acceleration, **+3** en power long shots, **+2** en movement agility |
| Cluster 2 | Antonee Robinson (82) | 17 | **+4** en attacking heading accuracy, **+3** en defending, **+1** en mentality interceptions, **+1** en power strength, **+1** en mentality aggression |
| Cluster 3 | Achraf Hakimi Mouhأشرف حكيمي (89) | 14 | **+16** en skill fk accuracy, **+13** en mentality penalties, **+13** en attacking volleys, **+12** en power long shots, **+11** en attacking finishing |

### Análisis Detallado de Arquetipos por Clúster

#### Clúster 1: Representado por Marc Cucurella Saseta (84)
- **Tamaño del grupo:** 29 jugadores.
- **Ejemplos en el dataset:** Marc Cucurella Saseta, Konrad Laimer, David Raum, Rayan Aït Nouriريان آيت نوري, Noussair Mazraouiنصير مزراوي, Nahuel Molina Lucero

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Pace**: ++4.5 (Mediana del clúster: 81.0 vs Mediana global: 76.5)
  * **Movement Sprint Speed**: ++4.0 (Mediana del clúster: 81.0 vs Mediana global: 77.0)
  * **Movement Acceleration**: ++4.0 (Mediana del clúster: 81.0 vs Mediana global: 77.0)
  * **Power Long Shots**: ++3.0 (Mediana del clúster: 61.0 vs Mediana global: 58.0)
  * **Movement Agility**: ++2.5 (Mediana del clúster: 77.0 vs Mediana global: 74.5)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Attacking Heading Accuracy**: -5.0 (Mediana del clúster: 59.0 vs Mediana global: 64.0)
  * **Physic**: -2.0 (Mediana del clúster: 72.0 vs Mediana global: 74.0)
  * **Power Strength**: -2.0 (Mediana del clúster: 68.0 vs Mediana global: 70.0)
  * **Mentality Penalties**: -2.0 (Mediana del clúster: 44.0 vs Mediana global: 46.0)
  * **Attacking Volleys**: -1.5 (Mediana del clúster: 48.0 vs Mediana global: 49.5)

________________________________________

#### Clúster 2: Representado por Antonee Robinson (82)
- **Tamaño del grupo:** 17 jugadores.
- **Ejemplos en el dataset:** Antonee Robinson, Daniel Muñoz Mejía, Aaron Wan-Bissaka, Stefan Posch, Jorrel Hato, Guéla Doué

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Attacking Heading Accuracy**: ++4.0 (Mediana del clúster: 68.0 vs Mediana global: 64.0)
  * **Defending**: ++3.0 (Mediana del clúster: 73.0 vs Mediana global: 70.0)
  * **Mentality Interceptions**: ++1.5 (Mediana del clúster: 73.0 vs Mediana global: 71.5)
  * **Power Strength**: ++1.0 (Mediana del clúster: 71.0 vs Mediana global: 70.0)
  * **Mentality Aggression**: ++1.0 (Mediana del clúster: 73.0 vs Mediana global: 72.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Power Long Shots**: -15.0 (Mediana del clúster: 43.0 vs Mediana global: 58.0)
  * **Attacking Finishing**: -13.5 (Mediana del clúster: 41.0 vs Mediana global: 54.5)
  * **Power Shot Power**: -12.0 (Mediana del clúster: 55.0 vs Mediana global: 67.0)
  * **Skill Fk Accuracy**: -12.0 (Mediana del clúster: 39.0 vs Mediana global: 51.0)
  * **Shooting**: -11.0 (Mediana del clúster: 46.0 vs Mediana global: 57.0)

________________________________________

#### Clúster 3: Representado por Achraf Hakimi Mouhأشرف حكيمي (89)
- **Tamaño del grupo:** 14 jugadores.
- **Ejemplos en el dataset:** Achraf Hakimi Mouhأشرف حكيمي, Marcos Llorente Moreno, Joško Gvardiol, Reece James, Maxim De Cuyper, Lucas Digne

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Skill Fk Accuracy**: ++16.5 (Mediana del clúster: 67.5 vs Mediana global: 51.0)
  * **Mentality Penalties**: ++13.5 (Mediana del clúster: 59.5 vs Mediana global: 46.0)
  * **Attacking Volleys**: ++13.5 (Mediana del clúster: 63.0 vs Mediana global: 49.5)
  * **Power Long Shots**: ++12.5 (Mediana del clúster: 70.5 vs Mediana global: 58.0)
  * **Attacking Finishing**: ++11.5 (Mediana del clúster: 66.0 vs Mediana global: 54.5)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Movement Agility**: -2.5 (Mediana del clúster: 72.0 vs Mediana global: 74.5)
  * **Defending Sliding Tackle**: -2.5 (Mediana del clúster: 69.5 vs Mediana global: 72.0)
  * **Defending Standing Tackle**: -2.0 (Mediana del clúster: 71.0 vs Mediana global: 73.0)
  * **Movement Reactions**: -1.0 (Mediana del clúster: 73.0 vs Mediana global: 74.0)
  * **Movement Balance**: -0.5 (Mediana del clúster: 72.5 vs Mediana global: 73.0)

________________________________________


---

## Midfielders (KMeans Arquetipos >75)
Total jugadores analizados: 102

| Clúster | Representante principal | Miembros | Atributos Destacados (Desviación vs Mediana Global) |
| :---: | :--- | :---: | :--- |
| Cluster 1 | Alexis Mac Allister (87) | 22 | **+12** en attacking volleys, **+11** en skill fk accuracy, **+8** en power long shots, **+8** en attacking finishing, **+8** en mentality penalties |
| Cluster 2 | Jamal Musiala (88) | 20 | **+9** en attacking volleys, **+5** en movement acceleration, **+5** en movement balance, **+5** en skill curve, **+5** en pace |
| Cluster 3 | Rodrigo Hernández Cascante (90) | 60 | **+3** en defending standing tackle, **+3** en defending marking awareness, **+2** en power strength, **+2** en defending sliding tackle, **+2** en mentality interceptions |

### Análisis Detallado de Arquetipos por Clúster

#### Clúster 1: Representado por Alexis Mac Allister (87)
- **Tamaño del grupo:** 22 jugadores.
- **Ejemplos en el dataset:** Alexis Mac Allister, Kevin De Bruyne, Youri Tielemans, Fabián Ruiz Peña, Granit Xhaka, Luka Modrić

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Attacking Volleys**: ++12.0 (Mediana del clúster: 72.0 vs Mediana global: 60.0)
  * **Skill Fk Accuracy**: ++11.0 (Mediana del clúster: 74.5 vs Mediana global: 63.5)
  * **Power Long Shots**: ++8.5 (Mediana del clúster: 78.5 vs Mediana global: 70.0)
  * **Attacking Finishing**: ++8.5 (Mediana del clúster: 75.5 vs Mediana global: 67.0)
  * **Mentality Penalties**: ++8.5 (Mediana del clúster: 68.5 vs Mediana global: 60.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Movement Balance**: -4.0 (Mediana del clúster: 72.0 vs Mediana global: 76.0)
  * **Movement Agility**: -3.5 (Mediana del clúster: 72.5 vs Mediana global: 76.0)
  * **Power Jumping**: -3.0 (Mediana del clúster: 71.0 vs Mediana global: 74.0)
  * **Movement Acceleration**: -2.5 (Mediana del clúster: 69.0 vs Mediana global: 71.5)
  * **Movement Sprint Speed**: -2.5 (Mediana del clúster: 66.0 vs Mediana global: 68.5)

________________________________________

#### Clúster 2: Representado por Jamal Musiala (88)
- **Tamaño del grupo:** 20 jugadores.
- **Ejemplos en el dataset:** Jamal Musiala, Charles De Ketelaere, Andrej Kramarić, João Félix Sequeira, Ismael Saibari Ben El Basraإسماعيل صيباري, Amad Diallo Traoré

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Attacking Volleys**: ++9.0 (Mediana del clúster: 69.0 vs Mediana global: 60.0)
  * **Movement Acceleration**: ++5.5 (Mediana del clúster: 77.0 vs Mediana global: 71.5)
  * **Movement Balance**: ++5.5 (Mediana del clúster: 81.5 vs Mediana global: 76.0)
  * **Skill Curve**: ++5.0 (Mediana del clúster: 75.0 vs Mediana global: 70.0)
  * **Pace**: ++5.0 (Mediana del clúster: 74.5 vs Mediana global: 69.5)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Mentality Interceptions**: -23.0 (Mediana del clúster: 48.5 vs Mediana global: 71.5)
  * **Defending Standing Tackle**: -23.0 (Mediana del clúster: 49.0 vs Mediana global: 72.0)
  * **Defending Marking Awareness**: -23.0 (Mediana del clúster: 45.0 vs Mediana global: 68.0)
  * **Defending**: -22.5 (Mediana del clúster: 47.5 vs Mediana global: 70.0)
  * **Defending Sliding Tackle**: -22.0 (Mediana del clúster: 45.5 vs Mediana global: 67.5)

________________________________________

#### Clúster 3: Representado por Rodrigo Hernández Cascante (90)
- **Tamaño del grupo:** 60 jugadores.
- **Ejemplos en el dataset:** Rodrigo Hernández Cascante, Frenkie de Jong, Declan Rice, Bruno Guimarães Rodrigues Moura, N'Golo Kanté, Adrien Rabiot-Provost

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Defending Standing Tackle**: ++3.5 (Mediana del clúster: 75.5 vs Mediana global: 72.0)
  * **Defending Marking Awareness**: ++3.0 (Mediana del clúster: 71.0 vs Mediana global: 68.0)
  * **Power Strength**: ++2.5 (Mediana del clúster: 72.5 vs Mediana global: 70.0)
  * **Defending Sliding Tackle**: ++2.5 (Mediana del clúster: 70.0 vs Mediana global: 67.5)
  * **Mentality Interceptions**: ++2.5 (Mediana del clúster: 74.0 vs Mediana global: 71.5)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Mentality Penalties**: -5.0 (Mediana del clúster: 55.0 vs Mediana global: 60.0)
  * **Skill Fk Accuracy**: -4.5 (Mediana del clúster: 59.0 vs Mediana global: 63.5)
  * **Skill Curve**: -4.0 (Mediana del clúster: 66.0 vs Mediana global: 70.0)
  * **Attacking Volleys**: -4.0 (Mediana del clúster: 56.0 vs Mediana global: 60.0)
  * **Power Shot Power**: -4.0 (Mediana del clúster: 70.0 vs Mediana global: 74.0)

________________________________________


---

## Strikers (KMeans Arquetipos >75)
Total jugadores analizados: 47

| Clúster | Representante principal | Miembros | Atributos Destacados (Desviación vs Mediana Global) |
| :---: | :--- | :---: | :--- |
| Cluster 1 | Ante Budimir (82) | 6 | **+11** en mentality aggression, **+9** en power strength, **+6** en attacking heading accuracy, **+5** en mentality penalties, **+4** en physic |
| Cluster 2 | Kylian Mbappé Lottin (91) | 25 | **+7** en movement acceleration, **+7** en defending standing tackle, **+7** en mentality interceptions, **+6** en pace, **+6** en defending |
| Cluster 3 | Cristiano Ronaldo dos Santos Aveiro (85) | 16 | **+5** en mentality vision, **+4** en skill fk accuracy, **+4** en shooting, **+4** en power shot power, **+3** en attacking short passing |

### Análisis Detallado de Arquetipos por Clúster

#### Clúster 1: Representado por Ante Budimir (82)
- **Tamaño del grupo:** 6 jugadores.
- **Ejemplos en el dataset:** Ante Budimir, Tomáš Chorý, Igor Thiago Nascimento Rodrigues, Håkan Gustaf Nilsson, Haris Tabaković, Frantzdy Pierrot

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Mentality Aggression**: ++11.0 (Mediana del clúster: 76.0 vs Mediana global: 65.0)
  * **Power Strength**: ++9.0 (Mediana del clúster: 87.0 vs Mediana global: 78.0)
  * **Attacking Heading Accuracy**: ++6.0 (Mediana del clúster: 81.0 vs Mediana global: 75.0)
  * **Mentality Penalties**: ++5.5 (Mediana del clúster: 73.5 vs Mediana global: 68.0)
  * **Physic**: ++4.0 (Mediana del clúster: 80.0 vs Mediana global: 76.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Movement Balance**: -29.0 (Mediana del clúster: 38.0 vs Mediana global: 67.0)
  * **Skill Curve**: -18.5 (Mediana del clúster: 46.5 vs Mediana global: 65.0)
  * **Movement Agility**: -17.0 (Mediana del clúster: 55.0 vs Mediana global: 72.0)
  * **Movement Acceleration**: -16.5 (Mediana del clúster: 56.5 vs Mediana global: 73.0)
  * **Attacking Crossing**: -16.0 (Mediana del clúster: 43.0 vs Mediana global: 59.0)

________________________________________

#### Clúster 2: Representado por Kylian Mbappé Lottin (91)
- **Tamaño del grupo:** 25 jugadores.
- **Ejemplos en el dataset:** Kylian Mbappé Lottin, Masour Ousmane Dembélé, Alexander Isak, Julián Álvarez, Jean-Philippe Mateta, Nicolas Jackson

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Movement Acceleration**: ++7.0 (Mediana del clúster: 80.0 vs Mediana global: 73.0)
  * **Defending Standing Tackle**: ++7.0 (Mediana del clúster: 39.0 vs Mediana global: 32.0)
  * **Mentality Interceptions**: ++7.0 (Mediana del clúster: 35.0 vs Mediana global: 28.0)
  * **Pace**: ++6.0 (Mediana del clúster: 81.0 vs Mediana global: 75.0)
  * **Defending**: ++6.0 (Mediana del clúster: 40.0 vs Mediana global: 34.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Mentality Aggression**: -4.0 (Mediana del clúster: 61.0 vs Mediana global: 65.0)
  * **Physic**: -2.0 (Mediana del clúster: 74.0 vs Mediana global: 76.0)
  * **Attacking Heading Accuracy**: -2.0 (Mediana del clúster: 73.0 vs Mediana global: 75.0)
  * **Mentality Penalties**: -2.0 (Mediana del clúster: 66.0 vs Mediana global: 68.0)
  * **Power Strength**: -1.0 (Mediana del clúster: 77.0 vs Mediana global: 78.0)

________________________________________

#### Clúster 3: Representado por Cristiano Ronaldo dos Santos Aveiro (85)
- **Tamaño del grupo:** 16 jugadores.
- **Ejemplos en el dataset:** Cristiano Ronaldo dos Santos Aveiro, Patrik Schick, Mikel Oyarzabal Ugarte, Yoane Wissa, Edin Džeko, Memphis Depay

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Mentality Vision**: ++5.5 (Mediana del clúster: 73.5 vs Mediana global: 68.0)
  * **Skill Fk Accuracy**: ++4.5 (Mediana del clúster: 59.5 vs Mediana global: 55.0)
  * **Shooting**: ++4.0 (Mediana del clúster: 80.0 vs Mediana global: 76.0)
  * **Power Shot Power**: ++4.0 (Mediana del clúster: 83.0 vs Mediana global: 79.0)
  * **Attacking Short Passing**: ++3.5 (Mediana del clúster: 75.5 vs Mediana global: 72.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Defending Marking Awareness**: -7.0 (Mediana del clúster: 25.0 vs Mediana global: 32.0)
  * **Defending Sliding Tackle**: -4.0 (Mediana del clúster: 21.0 vs Mediana global: 25.0)
  * **Mentality Interceptions**: -3.5 (Mediana del clúster: 24.5 vs Mediana global: 28.0)
  * **Defending Standing Tackle**: -3.5 (Mediana del clúster: 28.5 vs Mediana global: 32.0)
  * **Defending**: -3.0 (Mediana del clúster: 31.0 vs Mediana global: 34.0)

________________________________________


---

## Wingers (KMeans Arquetipos >75)
Total jugadores analizados: 57

| Clúster | Representante principal | Miembros | Atributos Destacados (Desviación vs Mediana Global) |
| :---: | :--- | :---: | :--- |
| Cluster 1 | Mohamed Salah Hamed Ghalyمحمد صلاح (91) | 22 | **+14** en attacking heading accuracy, **+10** en power jumping, **+6** en movement reactions, **+6** en power strength, **+6** en power shot power |
| Cluster 2 | Lamine Yamal Nasraoui Ebanaلامين يامال نصراوي إبانا (89) | 19 | **+2** en movement balance |
| Cluster 3 | Bukayo Saka (88) | 16 | **+24** en defending standing tackle, **+24** en mentality interceptions, **+20** en defending sliding tackle, **+20** en defending, **+19** en defending marking awareness |

### Análisis Detallado de Arquetipos por Clúster

#### Clúster 1: Representado por Mohamed Salah Hamed Ghalyمحمد صلاح (91)
- **Tamaño del grupo:** 22 jugadores.
- **Ejemplos en el dataset:** Mohamed Salah Hamed Ghalyمحمد صلاح, Bradley Barcola, Ferran Torres García, Sadio Mané, Leandro Trossard, Ritsu Doan堂安 律

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Attacking Heading Accuracy**: ++14.5 (Mediana del clúster: 63.5 vs Mediana global: 49.0)
  * **Power Jumping**: ++10.0 (Mediana del clúster: 79.0 vs Mediana global: 69.0)
  * **Movement Reactions**: ++6.5 (Mediana del clúster: 76.5 vs Mediana global: 70.0)
  * **Power Strength**: ++6.0 (Mediana del clúster: 67.0 vs Mediana global: 61.0)
  * **Power Shot Power**: ++6.0 (Mediana del clúster: 77.0 vs Mediana global: 71.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Movement Balance**: -3.5 (Mediana del clúster: 76.5 vs Mediana global: 80.0)
  * **Defending Sliding Tackle**: -3.0 (Mediana del clúster: 30.0 vs Mediana global: 33.0)
  * **Defending Marking Awareness**: -1.5 (Mediana del clúster: 34.5 vs Mediana global: 36.0)
  * **Movement Agility**: -1.5 (Mediana del clúster: 80.5 vs Mediana global: 82.0)
  * **Mentality Aggression**: -1.0 (Mediana del clúster: 52.0 vs Mediana global: 53.0)

________________________________________

#### Clúster 2: Representado por Lamine Yamal Nasraoui Ebanaلامين يامال نصراوي إبانا (89)
- **Tamaño del grupo:** 19 jugadores.
- **Ejemplos en el dataset:** Lamine Yamal Nasraoui Ebanaلامين يامال نصراوي إبانا, Takefusa Kubo久保 建英, Mathis Rayan Cherki, Jérémy Doku, Assane Diao Diaoune, Simon Adingra

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Movement Balance**: ++2.0 (Mediana del clúster: 82.0 vs Mediana global: 80.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Mentality Interceptions**: -11.0 (Mediana del clúster: 24.0 vs Mediana global: 35.0)
  * **Power Strength**: -11.0 (Mediana del clúster: 50.0 vs Mediana global: 61.0)
  * **Power Jumping**: -10.0 (Mediana del clúster: 59.0 vs Mediana global: 69.0)
  * **Attacking Heading Accuracy**: -9.0 (Mediana del clúster: 40.0 vs Mediana global: 49.0)
  * **Power Stamina**: -8.0 (Mediana del clúster: 65.0 vs Mediana global: 73.0)

________________________________________

#### Clúster 3: Representado por Bukayo Saka (88)
- **Tamaño del grupo:** 16 jugadores.
- **Ejemplos en el dataset:** Bukayo Saka, Désiré Doué, Alejandro Grimaldo García, John McGinn, Ivan Perišić, Maghnes Akliouche

##### Fortalezas del Arquetipo (Desviación Positiva vs Mediana Global):
  * **Defending Standing Tackle**: ++24.5 (Mediana del clúster: 60.5 vs Mediana global: 36.0)
  * **Mentality Interceptions**: ++24.5 (Mediana del clúster: 59.5 vs Mediana global: 35.0)
  * **Defending Sliding Tackle**: ++20.5 (Mediana del clúster: 53.5 vs Mediana global: 33.0)
  * **Defending**: ++20.0 (Mediana del clúster: 56.0 vs Mediana global: 36.0)
  * **Defending Marking Awareness**: ++19.5 (Mediana del clúster: 55.5 vs Mediana global: 36.0)

##### Carencias del Arquetipo (Desviación Negativa vs Mediana Global):
  * **Attacking Volleys**: -2.5 (Mediana del clúster: 61.5 vs Mediana global: 64.0)
  * **Mentality Penalties**: -2.5 (Mediana del clúster: 58.5 vs Mediana global: 61.0)
  * **Power Shot Power**: -2.5 (Mediana del clúster: 68.5 vs Mediana global: 71.0)
  * **Movement Balance**: -2.0 (Mediana del clúster: 78.0 vs Mediana global: 80.0)
  * **Movement Acceleration**: -1.0 (Mediana del clúster: 83.0 vs Mediana global: 84.0)

________________________________________


---
