# Metodología y Modelo Matemático: Índice de Competitividad y Espectáculo (ICE)

## 1. Introducción y Justificación Analítica
El atractivo o nivel de "espectáculo" de un encuentro de fútbol no es una propiedad lineal que dependa únicamente de la suma bruta de goles convertidos. El espectáculo es una propiedad emergente de la interacción táctica, técnica y física de dos planteles en competencia.

Para modelar de forma empírica esta variable y mitigar los sesgos geográficos inherentes a las distintas confederaciones internacionales (UEFA, CONMEBOL, CAF, AFC, CONCACAF y OFC), se diseñó y desarrolló el **Índice de Competitividad y Espectáculo (ICE)**. Este índice descarta los goles absolutos históricos en favor de métricas subyacentes avanzadas de generación de peligro (oportunidades claras de gol), transiciones rápidas (contraataques), fragilidad defensiva y tensión competitiva (fricción y tarjetas).

---

## 2. Ingesta y Limpieza de Métricas (Fase de Preprocesamiento)
Los datos primarios se extraen de la plataforma Sofascore y de las fases clasificatorias correspondientes. Durante esta fase se mitigan dos problemas analíticos críticos:

### 2.1. Homogeneización de Unidades
Las métricas en bruto se normalizan a la unidad **Por Partido (PG)** para evitar distorsiones debidas a la cantidad desigual de partidos jugados en las fases clasificatorias de cada confederación:
$$\text{Métrica}_{\text{PG}} = \frac{\text{Métrica Total}}{\text{Partidos Disputados}}$$

### 2.2. Tratamiento Estadístico de Confederaciones Asimétricas (Caso de Estudio: Nueva Zelanda / OFC)
Para selecciones que compiten en confederaciones con baja densidad competitiva (como la OFC) y carecen de registros detallados de fricción (faltas) en Sofascore, se utiliza la base de datos de las eliminatorias oceánicas. 

Para resolver la falta de métricas de fricción de forma metodológica, se calcula una **Relación de Fricción Global ($R_{\text{fricción}}$)** utilizando los datos agregados de las 47 selecciones restantes que sí poseen registros completos:
$$R_{\text{fricción}} = \frac{\sum_{i=1}^{47} \text{Faltas PG}_i}{\sum_{i=1}^{47} \text{Tarjetas PG}_i}$$

A partir de esta relación y de las tarjetas promedio por partido registradas por Nueva Zelanda ($\text{Tarjetas PG}_{\text{NZL}}$), se infiere de forma dinámica su volumen de faltas:
$$\text{Faltas PG}_{\text{NZL}} = \text{Tarjetas PG}_{\text{NZL}} \times R_{\text{fricción}}$$

---

## 3. Normalización Intercontinental por Alineación de Medias (Baseline Alignment)
Para neutralizar la inflación artificial de estadísticas ofensivas en eliminatorias de confederaciones de menor competitividad (como Nueva Zelanda en la OFC) sin alterar arbitrariamente las métricas, el modelo implementa una **Alineación de Medias**.

El algoritmo calcula dinámicamente un multiplicador empírico ($M_{\text{conf}}$) para cada confederación dividiendo la media aritmética global de la variable entre la media de esa confederación específica:

$$M_{\text{conf}} = \frac{\mu_{\text{global}}}{\mu_{\text{conf}}}$$

* **OFC:** $\mu_{\text{OC}} = 5.60 \rightarrow M_{\text{conf}} = 0.560$ (Ajusta a la baja las métricas ofensivas de Nueva Zelanda debido a la baja oposición de la OFC).
* **CONMEBOL:** $\mu_{\text{OC}} = 1.80 \rightarrow M_{\text{conf}} = 1.743$ (Premia a Uruguay, Argentina y Brasil por generar peligro en un ecosistema defensivo de alta intensidad táctica).
* **UEFA:** $\mu_{\text{OC}} = 4.14 \rightarrow M_{\text{conf}} = 0.757$ (Ajusta levemente a la baja por la asimetría de los grupos clasificatorios europeos).

---

## 4. Calibración por Coeficiente de Dificultad del Oponente ($C_{\text{dif}}$)
Para purgar el **Sesgo de Calendario** (el hecho de jugar contra rivales de jerarquía dispar en eliminatorias locales), se calcula un factor de ponderación utilizando el **Ranking FIFA actual** de los oponentes como ancla global neutra.

1. Se determina la **mediana de los rankings FIFA de los rivales** enfrentados por cada selección en partidos oficiales recientes ($R_{\text{med}}$).
2. Se calcula el **Coeficiente de Dificultad ($C_{\text{dif}}$)** mediante una curva de decaimiento lineal suavizada:
   $$C_{\text{dif}} = 1.0 - 0.5 \times \left( \frac{R_{\text{med}} - 1}{209.0} \right)$$
   *Esto suaviza la penalización para que selecciones europeas que disputan eliminatorias contra oponentes menores no vean destruida su valoración ofensiva.* El valor resultante se acota estrictamente: $C_{\text{dif}} \in [0.5, 1.0]$.

### 4.1. Ajuste Asimétrico de Métricas Individuales
El coeficiente se aplica de forma diferenciada según la naturaleza de la métrica:
* **Métricas de producción ofensiva (Ocasiones Claras $OC$ y Contraataques $CA$):** Se multiplican por $C_{\text{dif}}$. El rendimiento contra rivales débiles se penaliza proporcionalmente.
  $$OC_{\text{adj}} = OC_{\text{raw}} \times C_{\text{dif}} \qquad CA_{\text{adj}} = CA_{\text{raw}} \times C_{\text{dif}}$$
* **Métricas de vulnerabilidad y fricción (Goles Concedidos/Vulnerabilidad $Vuln$ y Faltas/Drama $Drama$):** Se dividen por $C_{\text{dif}}$. La fragilidad defensiva demostrada ante rivales de menor ranking se amplifica matemáticamente.
  $$Vuln_{\text{adj}} = \frac{Vuln_{\text{raw}}}{C_{\text{dif}}} \qquad Drama_{\text{adj}} = \frac{Drama_{\text{raw}}}{C_{\text{dif}}}$$

---

## 5. Algoritmo de Simulación del Encuentro (Frontend)
El motor en el navegador ([scoring.js](file:///c:/Users/tomas/Desktop/proyectos/worldcup-app/frontend/js/scoring.js)) calcula el ICE en tiempo real para el cruce directo entre el equipo local ($A$) y el visitante ($B$):

### 5.1. Fusión Táctica de Campo
Se promedian las capacidades normalizadas de ambos contendientes para modelar el escenario del partido:
$$OC_{\text{match}} = \frac{OC_{A,\text{norm}} + OC_{B,\text{norm}}}{2}$$
$$CA_{\text{match}} = \frac{CA_{A,\text{norm}} + CA_{B,\text{norm}}}{2}$$
$$Drama_{\text{match}} = \frac{Drama_{A,\text{norm}} + Drama_{B,\text{norm}}}{2}$$
$$Vuln_{\text{match}} = \frac{Vuln_{A,\text{norm}} + Vuln_{B,\text{norm}}}{2}$$

### 5.2. Penalización por Asimetría Competitiva ($P_{\text{Brecha}}$)
Un partido disparejo carece de tensión competitiva. El recomendador calcula este factor mediante una curva sigmoide (logística) basada en la diferencia de sus **Elo Ratings base**:

$$P_{\text{Brecha}} = \frac{P_{\text{max}}}{1 + e^{-k(\Delta \text{Elo} - R_{\text{mid}})}}$$

*Donde:*
* $\Delta \text{Elo} = |\text{Elo}_{A, \text{base}} - \text{Elo}_{B, \text{base}}|$ es la diferencia de Elo histórico.
* $P_{\text{max}} = 0.60$ (penalización máxima del 60%).
* $R_{\text{mid}} = 350$ puntos de diferencia de Elo (punto medio de penalización).
* $k = 0.01$ (sensibilidad adaptada a la escala Elo).

Esto garantiza que diferencias menores a 200 puntos Elo (ej. Inglaterra vs. Croacia) apenas reciban penalización, mientras que cruces disparejos sufran castigos severos.

### 5.3. Ecuación Estructural del ICE
El puntaje bruto de espectáculo combina los factores ponderados y amplifica el peligro ofensivo según la fragilidad de ambas defensas:
$$ice = \left[ OC_{\text{match}} \times (1.0 + \gamma \cdot Vuln_{\text{match}}) + (\alpha \cdot CA_{\text{match}}) + (\beta \cdot Drama_{\text{match}}) \right] \times (1.0 - P_{\text{Brecha}})$$
* Parámetros estándar: $\alpha = 0.5$, $\gamma = 0.5$, $\beta$ (peso de drama, $0.2$ por defecto).

### 5.4. Factor de Calidad Absoluta ($Q_{\text{match}}$) y Elo Dinámico
Para reflejar el peso de la jerarquía individual sin colinealidad (evitando duplicar el premio al sumar estrellas a un Elo de por sí alto), las estrellas convocadas alimentan un **Elo Dinámico**:

$$Elo_{\text{dinámico}} = Elo_{\text{base}} + 100 \times \frac{N_{\text{stars}}}{N_{\text{stars}} + 5}$$

La calidad absoluta ($Q_{\text{match}}$) escala linealmente basándose en el promedio de los Elos dinámicos del partido:
$$Q_{\text{match}} = \max\left(0.60, \min\left(1.0, 0.60 + 0.40 \times \frac{Elo_{\text{dinámico, prom}} - 1600}{500}\right)\right)$$

---

## 6. Normalización Final
El puntaje bruto se escala linealmente al rango $[1.0, 10.0]$ empleando un **Techo Dinámico ($T$)** y el factor de calidad $Q_{\text{match}}$:
$$T = T_{\text{scale}} \times (1.5 + \alpha + \beta) \qquad \text{con } T_{\text{scale}} = 0.65$$
$$Score_{\text{Espectáculo Base}} = 1.0 + 9.0 \times \left( \frac{\max(ICE_{\text{min}}, \min(ice, T)) - ICE_{\text{min}}}{T - ICE_{\text{min}}} \right)$$
$$Score_{\text{Espectáculo Final}} = Score_{\text{Espectáculo Base}} \times Q_{\text{match}}$$
y se limita estrictamente al rango $[1.0, 10.0]$.
