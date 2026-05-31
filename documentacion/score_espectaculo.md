# Metodología y Modelo Matemático: Índice de Competitividad y Espectáculo (ICE)

## 1. Introducción y Justificación Analítica
El atractivo o nivel de "espectáculo" de un encuentro de fútbol no es una propiedad lineal que dependa únicamente de la suma bruta de goles convertidos. El espectáculo es una propiedad emergente de la interacción táctica, técnica y física de dos planteles en competencia.

Para modelar de forma empírica esta variable y mitigar los sesgos geográficos inherentes a las distintas confederaciones internacionales (UEFA, CONMEBOL, CAF, AFC, CONCACAF y OFC), se diseñó y desarrolló el **Índice de Competitividad y Espectáculo (ICE)**. Este índice descarta los goles absolutos históricos —que suelen estar fuertemente condicionados por la disparidad regional— en favor de métricas subyacentes avanzadas de generación de peligro (oportunidades claras de gol), transiciones rápidas (contraataques), fragilidad defensiva y tensión competitiva (fricción y tarjetas).

---

## 2. Ingesta y Limpieza de Métricas (Fase de Preprocesamiento)
Los datos primarios se extraen de la plataforma Sofascore y de las fases clasificatorias correspondientes. Durante esta fase se mitigan dos problemas analíticos críticos:

### 2.1. Homogeneización de Unidades
Las métricas en bruto suelen informarse mezclando promedios por partido con totales acumulados del torneo. Para evitar distorsionar el espacio analítico, todas las variables se normalizan a la unidad **Por Partido (PG)**:
$$\text{Contraataques}_{\text{PG}} = \frac{\text{Contraataques Totales}}{\text{Partidos Disputados}}$$

### 2.2. Tratamiento Estadístico de Confederaciones Asimétricas (Caso de Estudio: Nueva Zelanda / OFC)
Para selecciones que compiten en confederaciones con baja densidad competitiva (como la OFC) y carecen de registros detallados en Sofascore, se utiliza la base de datos de las eliminatorias oceánicas. Dado el dominio hegemónico en su región, sus métricas ofensivas brutas suelen estar severamente infladas, lo que generaría falsos positivos en el recomendador.

Para resolver la falta de métricas de fricción en la OFC de forma metodológica, se calcula una **Relación de Fricción Global ($R_{\text{fricción}}$)** utilizando los datos agregados de las 47 selecciones restantes que sí poseen registros completos:
$$R_{\text{fricción}} = \frac{\sum_{i=1}^{47} \text{Faltas PG}_i}{\sum_{i=1}^{47} \text{Tarjetas PG}_i}$$

A partir de esta relación y de las tarjetas promedio por partido registradas por Nueva Zelanda ($\text{Tarjetas PG}_{\text{NZL}}$), se infiere de forma dinámica su volumen de faltas:
$$\text{Faltas PG}_{\text{NZL}} = \text{Tarjetas PG}_{\text{NZL}} \times R_{\text{fricción}}$$

---

## 3. Calibración por Coeficiente de Dificultad del Oponente ($C_{\text{dif}}$)
Para corregir el **Sesgo de Calendario** (frecuentar rivales de jerarquía dispar en eliminatorias locales), se calcula un factor de ponderación basado en el Ranking FIFA.

1. Se determina la **mediana de los rankings FIFA de los rivales** enfrentados por cada selección en partidos oficiales recientes ($R_{\text{med}}$).
2. Se calcula el **Coeficiente de Dificultad ($C_{\text{dif}}$)** mediante la siguiente función de decaimiento lineal:
   $$C_{\text{dif}} = 1.0 - \left( \frac{R_{\text{med}}}{210.0} \right)$$
   *Donde $210.0$ representa el límite teórico inferior de selecciones en la escala FIFA.* El valor resultante es estrictamente acotado para garantizar estabilidad: $C_{\text{dif}} \in [0.01, 1.0]$.

### 3.1. Ajuste Asimétrico de Métricas Individuales
El coeficiente se aplica de forma diferenciada según la naturaleza de la métrica:
* **Métricas de producción ofensiva (Ocasiones Claras $OC$ y Contraataques $CA$):** Se multiplican por $C_{\text{dif}}$. El rendimiento contra rivales débiles se penaliza proporcionalmente.
  $$OC_{\text{adj}} = OC_{\text{raw}} \times C_{\text{dif}} \qquad CA_{\text{adj}} = CA_{\text{raw}} \times C_{\text{dif}}$$
* **Métricas de vulnerabilidad y fricción (Goles Concedidos/Vulnerabilidad $Vuln$ y Faltas/Drama $Drama$):** Se dividen por $C_{\text{dif}}$. La debilidad defensiva o la fricción demostrada frente a rivales de bajo ranking se amplifica matemáticamente, penalizando su perfil competitivo global.
  $$Vuln_{\text{adj}} = \frac{Vuln_{\text{raw}}}{C_{\text{dif}}} \qquad Drama_{\text{adj}} = \frac{Drama_{\text{raw}}}{C_{\text{dif}}}$$

---

## 4. Normalización y Winsorización
Para evitar que los valores extremos (outliers) afecten la distribución, los vectores de cada equipo se someten a un proceso de **Winsorización** (recorte al percentil 95) en cada dimensión. Luego se aplica un escalamiento Min-Max para proyectar cada variable en un intervalo acotado, generando las variables finales indexadas en la base de datos:
$$X_{\text{norm}} = \frac{\min(X_{\text{adj}}, P_{95}) - X_{\text{min}}}{P_{95} - X_{\text{min}}}$$

* Para la variable de vulnerabilidad ($Vuln_{\text{norm}}$), se utiliza un rango de escalamiento acotado de $[0.2, 1.0]$ mediante un piso mínimo analítico para evitar que defensas perfectas en eliminatorias anulen el cálculo del índice:
  $$Vuln_{\text{norm}} = 0.2 + 0.8 \times \left( \frac{\min(Vuln_{\text{adj}}, P_{95}) - Vuln_{\text{min}}}{P_{95} - Vuln_{\text{min}}} \right)$$

* Variables resultantes por selección: $OC_{\text{norm}} \in [0, 1]$, $CA_{\text{norm}} \in [0, 1]$, $Drama_{\text{norm}} \in [0, 1]$, $Vuln_{\text{norm}} \in [0.2, 1.0]$.

---

## 5. Algoritmo de Simulación del Encuentro
En la interfaz del usuario, el recomendador calcula el índice del cruce directo entre el equipo local ($A$) y el visitante ($B$) mediante los siguientes pasos:

### 5.1. Fusión Táctica de Campo
Se promedian las capacidades de ambos contendientes para estimar el escenario del partido:
$$OC_{\text{match}} = \frac{OC_{A,\text{norm}} + OC_{B,\text{norm}}}{2}$$
$$CA_{\text{match}} = \frac{CA_{A,\text{norm}} + CA_{B,\text{norm}}}{2}$$
$$Drama_{\text{match}} = \frac{Drama_{A,\text{norm}} + Drama_{B,\text{norm}}}{2}$$
$$Vuln_{\text{match}} = \frac{Vuln_{A,\text{norm}} + Vuln_{B,\text{norm}}}{2}$$

### 5.2. Penalización por Asimetría Competitiva (Brecha FIFA)
Un partido con alta disparidad de jerarquía (ej. Rank #3 contra Rank #140) suele carecer de tensión competitiva e imprevisibilidad, tendiendo a la especulación táctica. Para mitigar esto, se calcula un factor de penalización mediante una curva sigmoide (logística) sobre la brecha absoluta de rankings:
$$P_{\text{Brecha}} = \frac{P_{\text{max}}}{1 + e^{-k(\Delta R - R_{\text{mid}})}}$$
*Donde:*
* $\Delta R = |R_A - R_B|$ es la diferencia absoluta entre las posiciones de ranking FIFA de ambos equipos.
* $P_{\text{max}} = 0.60$ es el techo máximo de penalización.
* $R_{\text{mid}} = 35$ es el punto de inflexión de la curva (donde la penalización alcanza exactamente la mitad del máximo, es decir, $0.30$).
* $k = 0.1$ es la pendiente o factor de transición de la curva.

Esta función sigmoide asegura que brechas pequeñas ($0-15$ puestos) apenas apliquen penalización, mientras que la penalización escala rápidamente en el rango medio ($20-50$ puestos) y se estabiliza cerca del máximo para brechas sumamente disparatadas.

### 5.3. Ecuación Estructural del ICE (Amplificador de Vulnerabilidad)
La vulnerabilidad defensiva no añade espectáculo de forma lineal, sino que actúa como un amplificador de la creación de peligro ofensivo. El puntaje bruto del partido se obtiene combinando los factores ponderados mediante una interacción multiplicativa:
$$ICE_{\text{match}} = \left[ OC_{\text{match}} \times (1.0 + \gamma \cdot Vuln_{\text{match}}) + (\alpha \cdot CA_{\text{match}}) + (\beta \cdot Drama_{\text{match}}) \right] \times (1.0 - P_{\text{Brecha}})$$
* Parámetros estándar: 
  * $\gamma = 0.5$ (coeficiente de amplificación de vulnerabilidad).
  * $\alpha = 0.5$ (peso de las transiciones rápidas/contraataques).
  * $\beta \in [0.0, 1.0]$ (peso del roce/drama táctico, parametrizado por el usuario en la interfaz con valor por defecto de $0.2$).

---

## 6. Normalización Final con Techo Dinámico
Para transformar el $ICE_{\text{match}}$ a una escala comprensible de $[1.0, 10.0]$, se establece un **Techo Dinámico ($T$)** proporcional a la máxima puntuación teórica posible bajo condiciones ideales ($P_{\text{Brecha}} = 0$):
$$T = 0.60 \times (1.5 + \alpha + \beta)$$
*El factor de escala $0.60$ previene la saturación prematura y asegura una distribución amplia y realista de los scores finales de espectáculo.*

Se define un límite inferior $ICE_{\text{min}} = 0.1$ para evitar singularidades y se proyecta linealmente:
$$\text{Score Espectáculo Base} = 1.0 + 9.0 \times \left( \frac{\max(ICE_{\text{min}}, \min(ICE_{\text{match}}, T)) - ICE_{\text{min}}}{T - ICE_{\text{min}}} \right)$$

---

## 7. Variables de Ajuste Avanzado
### 7.1. Factor de Atracción Individual (Star Player Bonus)
Para reflejar el peso de la jerarquía individual en la propuesta de entretenimiento, se inyecta un bonus aditivo basado en el número de jugadores catalogados como "estrellas" ($N_{\text{stars}}$) convocados en ambos equipos:
$$\text{Score Espectáculo Final} = \min\left(10.0, \text{Score Espectáculo Base} + \gamma_{\text{star}} \cdot (N_{\text{stars}, A} + N_{\text{stars}, B})\right)$$
*Donde $\gamma_{\text{star}} = 0.15$ es el coeficiente de ponderación por jugador estrella.*

### 7.2. Puntuación Inteligente Unificada (Smart Score)
En última instancia, el recomendador permite unificar el perfil estático de entretenimiento con la afinidad táctica respecto a las preferencias explícitas del usuario ($Score_{\text{Estilo}}$), estructurándose como una media ponderada:
$$\text{Smart Score} = w_{\text{espectáculo}} \cdot \text{Score Espectáculo Final} + (1.0 - w_{\text{espectáculo}}) \cdot Score_{\text{Estilo}}$$
*Donde $w_{\text{espectáculo}}$ es parametrizado libremente por el usuario en la interfaz.*
