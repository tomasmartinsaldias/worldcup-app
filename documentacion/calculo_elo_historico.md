# Metodología y Modelo Matemático: Cálculo de Elo Histórico y Modelo Híbrido

## 1. Introducción y Motivación
El Ranking FIFA clásico presenta limitaciones severas cuando se utiliza como el único motor matemático para estimar la probabilidad de victoria y el nivel absoluto de un partido:
1. **Actualizaciones tardías e inercia:** El ranking responde lentamente al estado de forma actual de las selecciones.
2. **Falta de granularidad histórica:** No permite evaluar el rendimiento acumulado a lo largo de décadas mediante transiciones partido a partido.

Para subsanar esto, el recomendador transicionó a un modelo basado en **Elo Rating**, calculado secuencialmente sobre el histórico completo de partidos internacionales. Sin embargo, para neutralizar las anomalías de aislamiento geográfico (burbujas de confederaciones débiles), el sistema se estructuró bajo un **Modelo Híbrido** que combina el Ranking FIFA moderno de oponentes para la normalización y el Elo secuencial para la simulación del encuentro directo.

---

## 2. Algoritmo de Cálculo de Elo Secuencial
El Elo de cada selección nacional se calcula procesando de forma estrictamente cronológica todos los partidos oficiales y amistosos registrados desde el **30 de noviembre de 1872** (el primer partido internacional de la historia: Escocia vs. Inglaterra).

### 2.1. Reglas de Inferencia y Fórmulas
1. **Inicialización:** Todos los países inician con un Elo base de `1500.0` al disputar su primer partido.
2. **Ajuste por Localía:** Se añaden $+100.0$ puntos de ventaja de localía al equipo que juega en su estadio (si el partido no es en terreno neutral):
   $$R_{\text{Local, adj}} = R_{\text{Local}} + 100.0$$
3. **Expectativa de Resultado ($W_e$):** La probabilidad esperada de victoria se calcula mediante:
   $$W_{e, \text{Local}} = \frac{1}{1 + 10^{(R_{\text{Visitante}} - R_{\text{Local, adj}}) / 400}}$$
   $$W_{e, \text{Visitante}} = 1.0 - W_{e, \text{Local}}$$
4. **Resultado Real ($W$):**
   * Victoria local: $W_{\text{Local}} = 1.0, W_{\text{Visitante}} = 0.0$
   * Empate: $W_{\text{Local}} = 0.5, W_{\text{Visitante}} = 0.5$
   * Victoria visitante: $W_{\text{Local}} = 0.0, W_{\text{Visitante}} = 1.0$

5. **Ponderación del Torneo (Factor $K$):** El peso asignado a cada partido varía según la importancia del marco competitivo:
   * **Copa del Mundo (Fase Final):** $K = 60$
   * **Copas Continentales (Euro, Copa América, Copa Africana, Copa Asiática, Copa Oro):** $K = 50$
   * **Clasificatorias (Mundial o Continental) y Nations League:** $K = 40$
   * **Partidos Amistosos:** $K = 20$
   * **Otros torneos menores:** $K = 30$

6. **Multiplicador por Margen de Goles ($G$):** Ajusta los puntos ganados o perdidos de acuerdo al volumen de la victoria para castigar o premiar goleadas:
   * Diferencia de 0 o 1 gol: $G = 1.0$
   * Diferencia de 2 goles: $G = 1.5$
   * Diferencia de 3 goles: $G = 1.75$
   * Diferencia de más de 3 goles ($d > 3$): $G = 1.75 + \frac{d - 3}{8}$

7. **Ecuación de Actualización de Ratings:**
   $$R_{\text{Nuevo}} = R_{\text{Anterior}} + K \times G \times (W - W_e)$$

---

## 3. El Desafío de la Burbuja de Oceanía (OFC)
En el Elo puro, los sistemas geográficamente semi-aislados generan burbujas de inflación. En la OFC (Oceanía), las selecciones juegan el 98% de sus partidos oficiales entre sí. Al haber una sola potencia dominante (Nueva Zelanda) y múltiples rivales amateurs, la acumulación constante de victorias de Nueva Zelanda eleva su Elo a niveles élite (~1750 puntos), equivalentes a selecciones UEFA de media-alta tabla, a pesar de la diferencia de calidad real del ecosistema.

Los grandes modelos analíticos (como el antiguo sistema de FiveThirtyEight) controlan esta burbuja mediante tres mecanismos:
1. **Drenaje Intercontinental (Ajuste del Factor K):** Asignar un factor $K$ masivo ($50+$) a repechajes internacionales o mundiales. Si un equipo inflado de la OFC pierde ante un rival de CONCACAF o CONMEBOL, pierde una porción masiva de puntos de golpe, devolviendo ese capital Elo al pool global.
2. **Castigo por Margen de Goles:** Si un equipo de Elo 1700 gana solo 1-0 ante un rival de Elo 1100, el modelo le resta puntos Elo por no cumplir la expectativa mínima de goleada.
3. **Regresión a la Media (Time Decay):** Empujar periódicamente a los equipos inactivos u aislados hacia la media de 1500 puntos al final de los ciclos.

---

## 4. Solución del Modelo Híbrido
Implementar drenaje dinámico y regresión a la media en la base de datos local requiere una calibración costosa y redundante. El recomendador resuelve esto mediante un **Modelo Híbrido**:

* **Fase 1 (Coeficiente de Dificultad $C_{\text{dif}}$):** Se utiliza el **Ranking FIFA actual** de los oponentes históricos para calcular la dificultad. Al utilizar el sistema oficial de la FIFA (el cual desde 2018 utiliza el método SUM de Elo con coeficientes de confederación ya calibrados), delegamos el problema de desinflar a la OFC al motor de cómputo de la FIFA. Tahití o Samoa quedan posicionadas en su jerarquía global real, lo que normaliza el calendario de Nueva Zelanda y limpia sus estadísticas infladas.
* **Fase 2 (Cruce Directo en Frontend):** Se utiliza el **Elo Histórico Secuencial** de los dos contrincantes para calcular la brecha de competitividad ($P_{\text{Brecha}}$) y la calidad absoluta del partido ($Q_{\text{match}}$), ya que en el mano a mano directo el Elo captura la forma deportiva de forma mucho más sensible y reactiva que el Ranking FIFA.

---

$$Elo_{\text{dinámico}} = Elo_{\text{base}} + 200 \times \frac{N_{\text{stars}}}{N_{\text{stars}} + 3}$$

* Donde $N_{\text{stars}}$ es la cantidad total de jugadores estrella convocados para el encuentro en ambos planteles.
* El modificador tiene un comportamiento asintótico (piso de $+0$ y techo de $+200$ puntos Elo) para evitar que potencias con planteles saturados de estrellas (ej. Francia o Brasil) disparen el puntaje de manera artificial. El parámetro de semisaturación $k=3$ asegura que la presencia de estrellas tenga un peso significativo en el cálculo del factor de calidad ($Q_{\text{match}}$).
* Para el cálculo de la paridad competitiva ($P_{\text{Brecha}}$), se mantiene el **Elo base** para evitar que una asimetría de estrellas en un partido parejo altere negativamente la brecha.

---

## 6. Actualización de Elo Dinámico en Vivo y Momentum (EMA) en el Simulador
Para el módulo del simulador de resultados del mundial en el cliente, las puntuaciones ingresadas por el usuario actualizan de manera interactiva el Elo de las selecciones. Esto permite capturar el estado de forma y la moral (momentum) de los equipos a lo largo del torneo.

### 6.1. Ecuación de Actualización con Momentum
Cuando se simula el resultado de un partido, se calcula la expectativa clásica $W_e$ y el resultado real $W$ (Victoria = 1.0, Empate = 0.5, Derrota = 0.0) para obtener el error de predicción $E$:
$$E = W - W_e$$

El **momentum acumulado ($M_t$)** es una media móvil exponencial (EMA) del error de predicción del equipo en sus partidos jugados durante el mundial:
$$M_t = \alpha \cdot E_t + (1 - \alpha) \cdot M_{t-1}$$
* Donde $\alpha = 0.4$ es la constante de suavizado. Un $\alpha$ alto prioriza el desempeño del partido inmediatamente anterior, mientras que el resto amortigua el historial del torneo.
* El momentum se inicializa en $0.0$ al comenzar el certamen.

### 6.2. Constante K Dinámica
El factor de actualización $K$ se ajusta multiplicativamente según la importancia de la fase del torneo ($\Omega_{\text{fase}}$) y el valor absoluto del momentum ($M_t$):
$$K_{\text{dinámico}} = K_{\text{base}} \times \Omega_{\text{fase}} \times (1 + \lambda \cdot |M_t|)$$

* **$K_{\text{base}} = 32$** (constante base de peso).
* **$\lambda = 0.5$** (sensibilidad del momentum). Un equipo en racha positiva o negativa que sorprende continuamente al modelo (alto $|M_t|$) sufrirá o se beneficiará de mayores variaciones de Elo en los siguientes encuentros.
* **$\Omega_{\text{fase}}$ (Ponderación de la fase):**
  * Fase de grupos (Group Stage): $\Omega_{\text{fase}} = 1.0$
  * Rondas eliminatorias intermedias (Round of 32, Round of 16, Quarter-finals): $\Omega_{\text{fase}} = 1.5$
  * Semifinales, Partido por el 3° Puesto y Final: $\Omega_{\text{fase}} = 2.0$

Una vez calculado el ajuste, se actualiza el Elo y se redondea al entero más cercano:
$$R_{\text{nuevo}} = R_{\text{anterior}} + \text{round}(K_{\text{dinámico}} \times E)$$

Este Elo actualizado se propaga cronológicamente como el Elo de partida (pre-match) de los siguientes encuentros del equipo en el torneo, afectando instantáneamente su ICE y posición en las recomendaciones.

---

## 7. Modelo Probabilístico de Simulación de Resultados

Los resultados automáticos generados mediante el botón "Simular Restantes" (y la simulación por jornadas) se computan en base a la brecha de ELO dinámico de los contrincantes, descartando la aleatoriedad pura en favor de una distribución de probabilidad estadística alineada con el rendimiento histórico.

### 7.1. Determinación del Ganador del Partido
Se calcula la probabilidad esperada de victoria $W_{e}$ para el equipo local utilizando la diferencia de ELO dinámico acumulado (que incluye el plus por estrellas convocadas):
$$W_{e} = \frac{1}{1 + 10^{-(ELO_{\text{Local}} - ELO_{\text{Visitante}})/400}}$$

A partir de esta expectativa, se derivan las probabilidades para los tres posibles desenlaces del partido:
* **Probabilidad de Empate ($P_{\text{empate}}$):** Fija en $0.26$ ($26\%$), correspondiente a la tasa histórica promedio de empates en mundiales.
* **Probabilidad de Victoria Local ($P_{\text{local}}$):** $0.74 \times W_{e}$
* **Probabilidad de Victoria Visitante ($P_{\text{visitante}}$):** $0.74 \times (1.0 - W_{e})$

El motor simula el partido generando un número pseudo-aleatorio uniforme $r \in [0, 1)$ y aplicando las siguientes fronteras:
* Si $r < P_{\text{local}}$: El partido es una victoria para el equipo local.
* Si $P_{\text{local}} \le r < P_{\text{local}} + P_{\text{empate}}$: El partido resulta en empate.
* Si $r \ge P_{\text{local}} + P_{\text{empate}}$: El partido es una victoria para el equipo visitante.

### 7.2. Distribución Dinámica de Goles
Una vez obtenido el desenlace, los goles se asignan de forma coherente con el resultado:
* **Empate:** Ambos equipos reciben el mismo número de goles, seleccionando al azar un valor en el rango $[0, 2]$.
* **Victoria:** El ganador recibe una cantidad aleatoria de goles en el rango $[1, 3]$. El perdedor recibe una cantidad de goles seleccionada aleatoriamente que es estrictamente menor a la del ganador (garantizando la coherencia del marcador).

### 7.3. Resolución de Definiciones por Penales en Play-offs
Debido a que en la Fase Eliminatoria (dieciseisavos a final) los partidos no pueden terminar en empate, cuando la simulación inicial resulta en tablas:
* Se simula una definición por penales.
* La probabilidad de que cada equipo gane la tanda de penales se pondera directamente usando la probabilidad esperada $W_{e}$, simulando que el equipo con mayor nivel ELO tiene una ventaja de efectividad/jerarquía proporcional en la tanda:
  - Si un número aleatorio uniforme es menor que $W_{e}$, avanza el local.
  - De lo contrario, avanza el visitante.

