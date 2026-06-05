# INFORME METODOLÓGICO: SISTEMA DE RECOMENDACIÓN DE PARTIDOS – MUNDIAL 2026

*Competencia: "Tu tiempo, tu Mundial"*  
*Facultad de Ingeniería – Maestría en Inteligencia Artificial (MIA)*  

---

## 1. RESUMEN EJECUTIVO

El presente informe expone el diseño, desarrollo e implementación del Sistema de Recomendación de Partidos para la Copa del Mundo FIFA 2026, un sistema de recomendación basado en el contenido (*Content-Based Recommendation System* (Millán Gordillo, 2025)) que personaliza la experiencia del usuario durante el certamen mundialista. El objetivo principal de la aplicación es clasificar de forma dinámica los 104 encuentros en tres categorías de recomendación: **Imperdible**, **Vale la pena** y **Para ver el resumen**, adaptando la oferta deportiva a la disponibilidad de tiempo y las preferencias estéticas e identitarias de cada usuario.

### Desafíos Clave y Creatividad Analítica
El principal desafío analítico consistió en mapear las preferencias del usuario y los atributos de los encuentros en un espacio vectorial homogéneo. El sistema define el perfil del usuario dividiendo la toma de decisiones en tres capas complementarias: la del entretenimiento, la del sentimiento y la técnico-analítica. A su vez, cada componente es descompuesta en micro-componentes que aportan, ponderadamente, a su score.
### 1. El Vector del Usuario (User Vector)

El Vector del Usuario representa las preferencias y afinidades que el usuario define al interactuar con el Quiz de onboarding. Son los pesos de cada macro componente.
#### Componentes y Origen de los Datos

#### A. Pesos de Importancia (Macro y Micro)
##### 1. Pesos Ajustables por el Usuario (Variables de Entrada)

Son definidos directamente por el usuario mediante controles deslizantes en la interfaz o calculados en base a sus respuestas en el onboarding:
###### A. Pesos Macro Principales (Rango de 1 a 10)

- **Entretenimiento (`w_entretenimiento`)**: Peso del macro-componente de Entretenimiento general.
- **Táctica (`w_tactica` o `w_tac`)**: Peso del macro-componente estratégico.
- **Afectivo (`w_afectivo` o `w_afec`)**: Peso del macro-componente de afinidad afectiva y emocional.
###### B. Pesos Micro de Entretenimiento (Sub-pesos, Rango de 1 a 10)

- **Espectáculo (`w_espectaculo` o `w_esp`)**: Importancia del fútbol dinámico y ocasiones de gol.
- **Fricción (`w_friccion` o `w_fric`)**: Importancia del juego físico y drama.
###### C. Pesos Micro Tácticos (Sub-pesos, Rango de 1 a 10)

- **Estilo de Juego (`w_tactica_estilo`)**: Interés en el estilo táctico del equipo.
- **Clústeres (`w_tactica_cluster`)**: Interés en los perfiles de jugadores drafteados.
###### D. Pesos Micro Afectivos (Sub-pesos, Rango de 1 a 10)

- **Clubes (`w_afectivo_club`)**: Importancia de la afinidad por clubes favoritos.
- **Selecciones (`w_afectivo_seleccion`)**: Importancia de la afinidad por selecciones nacionales.
- **Jugadores (`w_afectivo_jugador`)**: Importancia de la afinidad por jugadores favoritos.
##### 2. Pesos Macro Normalizados (Derivados)

Se calculan automáticamente a partir de los pesos macro principales del usuario para alimentar la ecuación de la Norma $L_2$ (su suma es igual a $1.0$):

- **Peso Macro de Entretenimiento ($W_{ent}$)**: $$W_{ent} = \frac{w_{entretenimiento}}{w_{entretenimiento} + w_{tactica} + w_{afectivo}}$$
- **Peso Macro de Táctica ($W_{tec}$)**: $$W_{tec} = \frac{w_{tactica}}{w_{entretenimiento} + w_{tactica} + w_{afectivo}}$$
- **Peso Macro Afectivo ($W_{af}$)**: $$W_{af} = \frac{w_{afectivo}}{w_{entretenimiento} + w_{tactica} + w_{afectivo}}$$

---

#### B. Vector Táctico del Usuario ($V_U$)

1. **Vector Táctico ($V_U$)**: Mapea el estilo de fútbol preferido del usuario en un espacio tetradimensional: $$V_U = [d_U, p_U, r_U, a_U]$$
	- **Defensa ($d_U$)**: Repliegue bajo (-1.0) vs. Presión alta activa (+1.0).
    - **Posesión ($p_U$)**: Fútbol directo (-1.0) vs. Elaboración asociativa (_Tiki-Taka_) (+1.0).
    - **Ritmo ($r_U$)**: Circulación pausada/control (-1.0) vs. Transiciones verticales rápidas (+1.0).
    - **Ancho ($a_U$)**: Ataque interior por el centro (-1.0) vs. Amplitud por las bandas (+1.0).
2. **Drafted Clusters**: Clústeres de arquetipos elegidos durante el onboarding en el flujo de simulador de draft (utilizados para el cálculo del score táctico basado en jugadores).

#### C. Lista de Afinidades Afectivas

- **Favorite Teams**: Lista de hasta 4 selecciones favoritas (obtenidas en el quiz).
- **Favorite Clubs**: Clubes europeos o locales a los que el usuario sigue.
- **Favorite Players**: Jugadores predilectos cargados por el usuario.

---

## 2. El Vector de Partido (Match Vector)

Por otro lado, cada partido cuenta con un conjunto de características objetivas y tácticas asignadas a las selecciones involucradas.
### Componentes de Datos de las Selecciones

#### A. Parámetros de Espectáculo (Scraped Team Metrics)

Métricas calculadas en la fase de clasificación (Eliminatorias o Copa Oro para anfitriones) y normalizadas para amortiguar las diferencias entre confederaciones:

- **Ocasiones de Gol (`ocasiones_norm`)**: Promedio de oportunidades de gol generadas por 90 minutos.
- **Contraataques (`contra_norm`)**: Intensidad y eficacia de transiciones rápidas.
- **Vulnerabilidad (`vuln_norm`)**: Promedio de goles concedidos por 90 minutos (un valor alto indica debilidad defensiva, propiciando partidos abiertos).
- **Drama (`drama_norm`)**: Densidad de tarjetas amarillas, rojas y penales cobrados por 90 minutos (base del score de Fricción).

#### B. Vector Táctico del Equipo ($V_A$, $V_B$)

Define la propuesta de juego real de las selecciones $A$ y $B$ en base a estadísticas reales recopiladas e Sofascore de la competencia más reciente con los datos completos. Si bien generalmente es la eliminatoria de su confederación, excepcionalmente se utiliza una copa, como la Asian Cup. El cálculo se realiza en tres etapas:
##### 1. Coeficiente de Fuerza de Oponentes ($C_{dif}$)

Para neutralizar la disparidad de nivel de las confederaciones (e.g., eliminatorias de CONMEBOL vs. OFC), se calcula un multiplicador de dificultad basado en la mediana del ranking FIFA de todos los rivales enfrentados por el equipo en la competencia de la que están siendo extraídos los datos ($R_{med}$). : $$C_{dif} = 1.0 - 0.5 \cdot \left( \frac{R_{med} - 1.0}{209.0} \right) \quad (\text{acotado en } [0.1, 1.0])$$ Un valor cercano a $1.0$ indica rivales de élite, y premia las estadísticas brutas del equipo.

##### 2. Cálculo de Componentes Tácticas Brutas

Para cada selección, se procesan las métricas agregadas por 90 minutos y se ponderan con el $C_{dif}$:

- **Posesión** ($P_{bruto}$) (Nivel asociativo y control de balón):    $$P_{bruto}=\text{pos\_pct}\cdot\left(1.0-\frac{\text{long\_balls}+\text{crosses}}{\text{accurate\_passes}}\right)\cdot C_{dif}$$
    > Donde $\text{pos\_pct}$ es el % de posesión, y los demás son pases largos, centros y pases precisos totales.
    
- **Ancho** ($A_{bruto}$) (Preferencia de juego exterior/amplitud vs. pasillos interiores):
    $$A_{bruto}=\frac{\text{attempted\_crosses}}{\text{acc\_opposition\_half}}\cdot C_{dif}$$
    > Relaciona los centros intentados frente a los pases completados en el último tercio del campo.
    
- **Ritmo** ($R_{bruto}$) (Velocidad de transición y verticalidad):    $$R_{bruto}=\frac{\text{total\_shots}+\frac{\text{counter\_attacks}}{\text{matches}}}{\text{pos\_pct}}\cdot C_{dif}$$
    > Mide la frecuencia de remates y contragolpes en relación al volumen de posesión del balón.
    
- **Defensa** ($D_{bruto}$) (Altura del bloque e intensidad de presión):
    $$\text{pass\_ratio}=\frac{\text{acc\_opp\_half}}{\text{acc\_own\_half}+\text{acc\_opp\_half}}$$
    $$D_{bruto}=(\text{pass\_ratio}\cdot C_{dif})-\frac{\frac{\text{clearances}}{C_{dif}}}{100.0}$$
    > Determina el porcentaje de pases completados en campo rival frente a los despejes defensivos.

##### 3. Normalización y Ajuste Sigmoidal ($\tanh$)

Para estandarizar las cuatro variables y acotarlas en el rango $[-1.0, 1.0]$ de la aplicación, las métricas se normalizan en la población general de equipos usando su puntuación Z y una tangente hiperbólica con factor de sensibilidad ($k_{sensitivity} = 0.6$): $$z = \frac{x_{bruto} - \mu}{\sigma}$$ $$v_i = \tanh(k_{sensitivity} \cdot z)$$ De este modo, se obtienen los vectores continuos $V_A$ y $V_B$ que representan la identidad táctica pura de cada selección.

---
## 3. Macro y Micro Componentes (Cálculo del Score)

Existen **3 Macro-componentes** principales: Entretenimiento ($X_{ent}$), Táctica ($X_{tec}$) y Afectivo ($X_{af}$). Cada uno produce un score final en el rango `[0, 10]`.

---
### A. Macro-componente: Entretenimiento ($X_{ent}$)

El macro-componente de Entretenimiento se compone a nivel micro de dos elementos ponderados: **Espectáculo (ICE)** y **Fricción**.

#### 1. Micro-componente: Espectáculo (ICE)

Calculado por `calculateICEScore(match, teams)`. Predice cuán emocionante será el partido. $$ice = \left( \text{oc}_{match} \cdot (1 + \gamma \cdot \text{vuln}_{match}) + \alpha \cdot \text{ca}_{match} \right) \cdot (1 - p_{brecha})$$

- Donde $\text{oc}_{match}$, $\text{ca}_{match}$ y $\text{vuln}_{match}$ son las medias de ambos rivales.
- $p_{brecha} = \frac{P_{MAX}}{1 + e^{-K \cdot (\Delta_{ELO} - R_{MID})}}$ penaliza partidos muy disparejos.
- El valor crudo `ice` se escala a $[1, 10]$ y se multiplica por la calidad promedio de los planteles ($q_{match}$) y la urgencia dinámica de fase de grupos (Stakes).

#### 2. Micro-componente: Fricción

Mapea el roce y agresividad física del partido en base al parámetro `drama_norm` (de 0 a 10):

- Si el usuario prefiere _Fair Play_, el score es proporcional a la inversa de la fricción: $x_{fric} = 1.0 - \text{drama}_{avg}$.
- Si es indiferente o prefiere roce, se asigna directamente la media de drama: $x_{fric} = \text{drama}_{avg}$.
- Escala a un score final de Fricción: $\text{frictionScore} = 1.0 + 9.0 \cdot x_{fric}$.

#### 3. Agregación de Entretenimiento ($X_{ent}$)

El macro-componente final de Entretenimiento ($X_{ent}$) se calcula mediante la media ponderada de las dos micro-componentes anteriores, utilizando los pesos ingresados por el usuario: $$X_{ent} = \frac{w_{esp} \cdot \text{spectacleScore} + w_{fric} \cdot \text{frictionScore}}{w_{esp} + w_{fric}}$$ _Nota: Si la suma de pesos crudos $w_{esp} + w_{fric}$ es 0, se toma por defecto `spectacleScore`._

---

### B. Macro-componente: Táctico / Estilo de Juego ($X_{tec}$)

Mide qué tanto se adapta la propuesta del partido a la preferencia del usuario, combinando la propuesta estratégica global de las selecciones con el perfil de juego de los jugadores en cancha alineados a los clústeres drafteados en el onboarding.

#### 1. Similitud Coseno de Estilo de Equipo ($s_{style}$)

Se calcula la similitud coseno entre el vector táctico del usuario ($V_U$) y el de cada selección ($V_A$, $V_B$): $$\text{sim}(V, V_U) = \frac{V \cdot V_U}{|V| |V_U|} = \frac{\sum (v_i \cdot u_i)}{\sqrt{\sum v_i^2} \sqrt{\sum u_i^2}}$$ El score táctico crudo combina el mejor representante (protagonista) con un factor de interacción menor ($\lambda = 0.1$) para el rival: $$\text{RawPlaystyle} = \max(\text{sim}_A, \text{sim}_B) + \lambda \cdot \min(\text{sim}_A, \text{sim}_B)$$ Escalado a rango $[0, 10]$: $$s_{style} = 10.0 \cdot \left( \frac{\text{RawPlaystyle} + 1.1}{2.2} \right)$$ *Nota: Si el usuario no tiene preferencias tácticas ($V_U$ en ceros), $s_{style}$ toma el valor de `spectacleScore`.*

#### 2. Afinamiento por Clústeres Drafteados ($s_{cluster}$)

Si el usuario completó el Draft de clústeres, se calcula la afinidad táctica de los jugadores en cancha. Para cada jugador, se obtiene la similitud al centroide de su arquetipo posicional drafteado mediante distancia euclídea ($dist$) y caída exponencial ($\alpha_{decay} = 3.0$): $$J_{draft} = \sum_{p \in \text{Match}} \left( \frac{e^{-\alpha_{decay} \cdot dist_p} - e^{-\alpha_{decay}}}{1.0 - e^{-\alpha_{decay}}} \right) \cdot pJuego_p$$ $$s_{cluster} = \min\left(1.0, \frac{\ln(1 + J_{draft})}{\ln(1 + Z_{draft})}\right) \quad (\text{con } Z_{draft} = 5.0)$$

#### 3. Agregación de la Componente Táctica ($X_{tec}$)

- **Si no hay clústeres drafteados:** Se utiliza directamente el estilo de juego del equipo: $$X_{tec} = s_{style}$$
- **Si hay clústeres drafteados:** Se promedian dinámicamente utilizando los pesos de slider correspondientes (`w_tactica_estilo` y `w_tactica_cluster`): $$X_{tec} = \frac{w_{tactica_estilo} \cdot s_{style} + w_{tactica_cluster} \cdot (s_{cluster} \cdot 10.0)}{w_{tactica_estilo} + w_{tactica_cluster}}$$

---

### C. Macro-componente: Afectivo ($X_{af}$)

Mide el nivel de apego emocional del usuario hacia el partido a través de tres micro-componentes afectivas: **Afinidad por Clubes ($s_{club}$)**, **Afinidad por Selecciones ($s_{sel}$)** y **Afinidad por Jugadores Favoritos ($s_{jug}$)**.

#### 1. Probabilidad de Juego Sigmoide ($pJuego$)

Para medir la relevancia real de un jugador en un partido, se calcula su probabilidad de participación a partir de su proporción de titularidades ($N_{\text{titular}}$) y la densidad de minutos jugados ($M_{\text{jugados}}$) sobre el total del equipo en las eliminatorias ($N_{\text{equipo}}$): $$IPH = 0.7 \cdot \left( \frac{N_{\text{titular}}}{N_{\text{equipo}}} \right) + 0.3 \cdot \min\left( 1.0, \frac{M_{\text{jugados}}}{N_{\text{equipo}} \cdot 90} \right)$$ $$pJuego = \frac{1}{1 + e^{-10 \cdot (IPH - 0.55)}}$$
Para ponderar la participación afectiva de forma realista, se estima la probabilidad de que un jugador $i$ dispute minutos en el encuentro ($P_{\text{juego}}$):
$$P_{\text{juego}}(i) = \begin{cases} \frac{1}{1 + e^{-10 \cdot (IPH - 0.55)}} & \text{Si tiene minutos registrados en Eliminatorias / Copa Oro} \\ \frac{\text{Valor Mercado}_i}{\max(\text{Valor Mercado de su Selección})} & \text{Si es convocado con 0 minutos (Debutantes o regresos por lesión)} \end{cases}$$

#### 2. Micro-componente: Afinidad por Clubes ($s_{club}$)

Evalúa la presencia de jugadores que pertenecen a los clubes favoritos del usuario en ambos planteles. $$x_{partido} = \sum_{p \in \text{Plantel } A} pJuego_p \cdot I_{\text{club } p \in \text{Favs}} + \sum_{q \in \text{Plantel } B} pJuego_q \cdot I_{\text{club } q \in \text{Favs}}$$ $$s_{club} = \min\left(1.0, \frac{\ln(1.0 + x_{partido})}{\ln(1.0 + Z_{club})}\right)$$ Donde $Z_{club} = 5.0$ actúa como factor de saturación logarítmica.

#### 3. Micro-componente: Afinidad por Selecciones ($s_{sel}$)

Evalúa si juegan selecciones de especial interés para el usuario.

- **Selección Principal** (primer elemento de `favoriteTeams`): Si juega, aporta $I_p = 1.0$.
- **Selecciones Secundarias** (siguientes 3 elementos): Cada una que juegue aporta $0.5$. $$s_{sel} = \begin{cases} 1.0 & \text{si juega la Selección Principal} \ \min(1.0, 0.5 \cdot n_{secundarias}) & \text{en otro caso} \end{cases}$$

#### 4. Micro-componente: Afinidad por Jugadores Favoritos ($s_{jug}$)

Evalúa la participación de jugadores favoritos explícitos directos ($J_d$) combinada con la similitud de perfil posicional de otros jugadores en el campo ($J_s$): $$J_d = \sum_{p \in \text{Direct Favs}} pJuego_p$$ $$J_s = \sum_{q \notin \text{Direct Favs}} \max_{f \in \text{Favs}} \left( \frac{1}{\text{dist}(q, f) + \epsilon} \right) \cdot pJuego_q \quad (\epsilon = 0.1)$$ $$s_{jug} = \min\left(1.0, \frac{\ln(1.0 + J_d)}{\ln(2.0)} + \lambda_{sim} \cdot \ln(1.0 + J_s)\right) \quad (\lambda_{sim} = 0.5)$$

#### 5. Agregación de la Componente Afectiva ($X_{af}$)

Los tres scores se promedian dinámicamente utilizando los pesos de importancia dinámicos ingresados por el usuario (`w_afectivo_club`, `w_afectivo_seleccion`, `w_afectivo_jugador`), activando ($m_i = 1$) o desactivando ($m_i = 0$) las componentes según el usuario haya cargado datos para ellas: $$\text{sub\_sum} = (m_{club} \cdot w_{afectivo\_club}) + (m_{sel} \cdot w_{afectivo\_seleccion}) + (m_{jug} \cdot w_{afectivo\_jugador})$$
$$X_{af} = \begin{cases} 10.0 \cdot \left( \frac{m_{club} \cdot w_{afectivo\_club} \cdot s_{club} + m_{sel} \cdot w_{afectivo\_seleccion} \cdot s_{sel} + m_{jug} \cdot w_{afectivo\_jugador} \cdot s_{jug}}{\text{sub\_sum}} \right) & \text{si } \text{sub\_sum} > 0 \\ 0.0 & \text{si } \text{sub\_sum} = 0 \end{cases}$$

---

## 4. Agregación Macro y Score Final (Norma L2)

Para unificar las **3 Macro-componentes** individuales ($X_{ent}$, $X_{tec}$, $X_{af}$) en una única recomendación consolidada, se utiliza una **Norma L2 ponderada con pesos fijos**:

### Fórmulas Matemáticas

1. **Normalización de Pesos Macro (3 Componentes)**: Los pesos macro definidos por el usuario se normalizan para asegurar la estabilidad del score: $$W_{ent} = \frac{w_{entretenimiento}}{w_{entretenimiento} + w_{tactica} + w_{afectivo}}$$ $$W_{tec} = \frac{w_{tactica}}{w_{entretenimiento} + w_{tactica} + w_{afectivo}}$$ $$W_{af} = \frac{w_{afectivo}}{w_{entretenimiento} + w_{tactica} + w_{afectivo}}$$ _(Si la suma total de pesos es 0, se le asigna a cada macro-componente un peso equitativo de $1/3$)_.
    
2. **Fórmula del Score Final ($S$)**: $$S = \sqrt{W_{ent} \cdot X_{ent}^2 + W_{tec} \cdot X_{tec}^2 + W_{af} \cdot X_{af}^2}$$
    

### Justificación Matemática de la Norma L2

Tradicionalmente, se usa una media ponderada aritmética para agregar puntajes. Sin embargo, la norma $L_2$ ofrece ventajas críticas:

- **Resalta Picos de Excelencia**: Debido al exponente cuadrático, las componentes con puntuaciones altas empujan el score combinado con mayor fuerza. Si un partido es tácticamente impecable ($X_{tec} = 10$) o genera una afinidad afectiva inmensa ($X_{af} = 10$), la norma $L_2$ evitará que los otros componentes promedio diluyan el interés, recomendando el partido al usuario con jerarquía.
- **Evita la Homogeneidad**: Abre el espectro de puntuaciones, permitiendo destacar a los partidos genuinamente emocionantes o afines por encima del pelotón de partidos comunes.
- **Garantía Matemática**: El score resultante se mantiene estrictamente acotado en el rango $[0, 10]$ ya que la suma de las ponderaciones normalizadas es exactamente $1.0$.

---

## 2. EXPLICACIÓN DE VARIABLES CREADAS

Para la formulación de los scores de recomendación, se procesaron datos base de SofaScore, Wikipedia, Transfermarkt, EA SPORTS FC 26 e historiales de la FIFA, a partir de los cuales se construyeron y definieron las siguientes variables clave en el backend (SQLite) y en el runtime del cliente (`state.js`, `scoring.js`):

### 2.1. Variables del Índice de Competitividad y Espectáculo (ICE)

#### Variables de Rendimiento por Selección
*   **`ocasiones_norm`, `contra_norm`, `drama_norm`, `vuln_norm` (Real $[0.0, 1.0]$, Ámbito: Selección):** Vectores que representan el desempeño promedio por partido de cada selección en las eliminatorias. Se obtienen aplicando normalización Min-Max y un recorte de valores extremos (Winsorización al percentil 95):
    *   *Ocasiones Claras ($OC_{norm}$):* Promedio de ocasiones de gol creadas, ajustadas por confederación.
    *   *Contraataques ($CA_{norm}$):* Promedio de transiciones ofensivas rápidas, ajustadas por confederación.
    *   *Drama ($Drama_{norm}$):* Nivel de intensidad física y fricción (tarjetas y faltas cometidas).
    *   *Vulnerabilidad ($Vuln_{norm}$):* Promedio de goles concedidos, acotado con un piso mínimo de $0.20$ para evitar defensas perfectas artificiales.

#### Factores y Coeficientes de Ajuste
*   **$C_{dif}$ - Coeficiente de Dificultad del Oponente (Real $[0.5, 1.0]$, Ámbito: Selección):** Mide la jerarquía de los rivales históricos enfrentados en partidos oficiales recientes. Se calcula usando la mediana del Ranking FIFA de dichos oponentes ($R_{med}$):
    $$C_{dif} = 1.0 - 0.5 \times \left( \frac{R_{med} - 1}{209.0} \right)$$
    Este coeficiente actúa de dos formas para evitar estadísticas distorsionadas por el nivel de los rivales:
    1.  *Multiplicador ofensivo:* Castiga (reduce) el volumen de Ocasiones Claras y Contraataques obtenidos ante rivales débiles (de ranking bajo).
    2.  *Divisor defensivo:* Amplifica (penaliza) la Vulnerabilidad y el Drama si el equipo mostró fragilidad o descontrol ante oponentes menores.
*   **$M_{conf}$ - Multiplicador de Alineación por Confederación (Real $[0.5, 2.0]$, Ámbito: Confederación):** Factor que neutraliza los sesgos competitivos entre regiones. Se calcula dividiendo la media global de una métrica ofensiva ($\mu_{global}$) entre la media de la confederación analizada ($\mu_{conf}$):
    $$M_{conf} = \frac{\mu_{global}}{\mu_{conf}}$$
    Esto ajusta a la baja las estadísticas en zonas menos competitivas (ej. OFC, $M_{conf} = 0.56$) y premia a los equipos en zonas de alta intensidad defensiva (ej. CONMEBOL, $M_{conf} = 1.74$).
*   **$R_{\text{fricción}}$ - Relación de Fricción Global (Real, Ámbito: Auxiliar de Datos):** Coeficiente utilizado para estimar las faltas de selecciones con datos incompletos en Sofascore (como Nueva Zelanda en la OFC). Calcula la proporción histórica entre faltas y tarjetas acumuladas de las 47 selecciones control del modelo:
    $$R_{\text{fricción}} = \frac{\sum_{i=1}^{47} \text{Faltas PG}_i}{\sum_{i=1}^{47} \text{Tarjetas PG}_i}$$
    Multiplicando las tarjetas de la selección sin datos por este ratio, se infiere su promedio de faltas de manera metodológica: $\text{Faltas PG} = \text{Tarjetas PG} \times R_{\text{fricción}}$.
*   **$P_{\text{Brecha}}$ - Penalización por Asimetría Competitiva (Real $[0.0, 0.60]$, Ámbito: Partido):** Factor que castiga el atractivo de un partido cuando hay demasiada diferencia de nivel entre los rivales (pérdida de tensión competitiva). Se modela mediante una curva sigmoide logística sobre la diferencia de sus Elo Ratings base ($\Delta Elo$):
    $$P_{\text{Brecha}} = \frac{0.60}{1 + e^{-0.01(\Delta Elo - 350)}}$$
    Bajo esta curva, diferencias menores a 200 puntos Elo apenas afectan el puntaje de espectáculo, mientras que partidos muy desiguales sufren una penalización de hasta el 60%.

### 2.2. Variables de Simulación Dinámica y Elo
Para determinar el nivel relativo a priori de un partido y estructurar el simulador de grupos, se diseñó un sistema de puntuación Elo (Esgueva Mariño, 2025) a partir de los datos históricos de partidos internacionales desde 1872.

*   **`Elo_base` y `Elo_dinámico` (Real, Scope: Selección/Partido):**
    *   *Elo Base:* Rating histórico acumulado partido a partido desde 1872 bajo fórmulas tradicionales.
    *   *Elo Dinámico:* Incorpora el factor de calidad de las superestrellas convocadas de manera asintótica para evitar colinealidades:
        $$Elo_{\text{dinámico}} = Elo_{\text{base}} + 200 \times \frac{N_{stars}}{N_{stars} + 3}$$
        Donde $N_{stars}$ representa la cantidad de jugadores destacados en la plantilla.
*   **$Q_{match}$ - Factor de Calidad Absoluta (Real $[0.60, 1.0]$, Scope: Partido):** Escala linealmente el nivel del encuentro basándose en el promedio de los ratings de Elo Dinámico del partido, fijando un pivote mínimo en 1400 puntos y un techo en 2100:
    $$Q_{match} = \max\left(0.60, \min\left(1.0, 0.60 + 0.40 \times \frac{Elo_{\text{dinámico, prom}} - 1400}{700}\right)\right)$$
*   **$M_t$ - Momentum Reciente del Equipo (Real $[-1.0, 1.0]$, Scope: Historial del Torneo):** Media Móvil Exponencial (EMA) del error de predicción ($E = W - W_e$) que mide la inercia deportiva de una selección durante la fase de grupos:
    $$M_t = \alpha \cdot E_t + (1 - \alpha) \cdot M_{t-1} \qquad (\text{con } \alpha = 0.4)$$
*   **$K_{dinámico}$ - Factor K de Peso Adaptativo (Real, Scope: Actualización de Elo):** Ajusta dinámicamente la velocidad de cambio de Elo en el simulador según la fase de competencia ($\Omega_{fase}$) y el momentum acumulado del equipo:
    $$K_{dinámico} = 32 \times \Omega_{fase} \times (1 + 0.5 \cdot |M_t|)$$
*   **$M_{match}$ - Multiplicador de Urgencia Competitiva (Real $[0.60, 1.0]$, Scope: Partido):** Cuantifica la trascendencia matemática de los puntos en juego. Se calcula como la **Media Armónica** de los multiplicadores individuales de los dos contendientes ($M_{home}, M_{away}$):
    $$M_{match} = \frac{2 \times M_{home} \times M_{away}}{M_{home} + M_{away}}$$
    Donde cada equipo recibe un valor según su estado de clasificación en el simulador de grupos: `PLAYING_FOR_LIFE` (1.0), `QUALIFIED` (0.85), `FIRST_PLACE_ASSURED` (0.70) y `ELIMINATED` (0.60). La media armónica prioriza al valor menor, castigando partidos desbalanceados (ej. uno que se juega la vida contra uno ya eliminado).

### 2.3. Variables Tácticas y de Estilo de Juego
*   **Vector Táctico $V = [d, p, r, a]$ (Array 4D $[-1.0, 1.0]$, Scope: Selección/Usuario):** Caracteriza el playstyle del equipo o las preferencias del usuario:
    1.  *Defensa ($d$):* Bloque bajo y repliegue (-1.0) vs. Presión alta activa (1.0).
    2.  *Posesión ($p$):* Transición directa vertical (-1.0) vs. Elaboración asociativa y Tiki-Taka (1.0).
    3.  *Ritmo de Juego ($r$):* Circulación controlada y pausada (-1.0) vs. Transición vertical explosiva (1.0).
    4.  *Ancho ($a$):* Ataque interior por pasillo central (-1.0) vs. Amplitud y desborde por bandas (1.0).
*   **$Score_{\text{Táctico Bruto}}$ (Real $[1.0, 10.0]$, Scope: Partido/Usuario):** Evaluación heurística que mide cuánto se alinean los estilos de juego de los contendientes con la preferencia táctica del usuario ($V_U$). Emplea la **Heurística del Protagonista** aplicando una amortiguación al rival para no penalizar partidos donde un solo equipo asume la propuesta buscada:
    $$Score_{\text{Táctico}} = \max(Sim(V_A, V_U), Sim(V_B, V_U)) + 0.1 \cdot \min(Sim(V_A, V_U), Sim(V_B, V_U))$$

---

## 3. ARQUITECTURA DEL MODELO

El sistema está diseñado bajo una arquitectura modular y desacoplada que separa el procesamiento, enriquecimiento e inferencia de datos pesada (pipeline ejecutado localmente en Python) de la lógica de recomendación dinámica y visualización interactiva del lado del cliente (Frontend). Este enfoque descentralizado optimiza el despliegue en entornos estáticos como GitHub Pages, eliminando la necesidad de servidores de base de datos en producción y reduciendo a cero la latencia de red en las consultas del recomendador.

### 3.1. Pipeline de Ingesta y Consolidación de Datos (Python/SQLite)
El backend offline utiliza una base de datos relacional compacta de dieciséis tablas, alojada en un archivo SQLite local denominado `worldcup_combined.db`, la cual unifica los registros históricos y el estado de la competición actual.

El proceso de ingesta se inicia en `populate_data.py`, script encargado de estructurar las plantillas iniciales a partir de fuentes abiertas y de realizar consultas enriquecidas a la API de Transfermarkt. Para eludir las restricciones de tasa de peticiones y protecciones de firewall (WAF), el pipeline implementa un mecanismo de persistencia local que actúa como caché relacional de forma local, evitando peticiones redundantes.

Posteriormente, la resolución final de plantillas y estrellas se ejecuta a través de `parse_convocados.py`. Este módulo analiza de manera determinista el archivo de control estructurado `Lista de Convocados.md` para actualizar el fixture mundialista con los nombres definitivos del torneo. Adicionalmente, evalúa y etiqueta a los jugadores clave (superestrellas) que formarán parte del cálculo de calidad absoluta del encuentro.

En paralelo, el subsistema de caracterización táctica procesa las estadísticas del rendimiento histórico de las eliminatorias mediante el algoritmo de agrupamiento jerárquico aglomerativo ($HAC$) en `HAC_clustering.py` y `score_cluster_players.py`, asignando arquetipos funcionales a cada futbolista.

Finalmente, el flujo converge en `export_to_json.py`, script que realiza las consultas cruzadas de Head-to-Head histórico y consolida toda la base relacional en un único archivo serializado de bajo peso, `wc2026_data.json`, el cual se escribe directamente en los directorios del frontend para su posterior consumo.

### 3.2. Runtime del Cliente (GitHub Pages / Client-Side Engine)
Dado que la aplicación se ejecuta de forma serverless en el navegador del usuario, toda la lógica de cálculo dinámico y simulación de estados se traslada al motor de ejecución de JavaScript. El archivo `futstate.js` centraliza el estado de la aplicación actuando como la única fuente de verdad sobre el progreso del torneo y las selecciones personalizadas del usuario.

El cálculo de las dinámicas deportivas se subdivide en dos procesos paralelos en tiempo real. Por un lado, `groups.js` evalúa continuamente los posibles escenarios restantes de la fase de grupos resolviendo el árbol combinatorio de complejidad exponencial $3^N$ por grupo para actualizar las posiciones en vivo y determinar si las selecciones se encuentran clasificadas, eliminadas o peleando su permanencia.

Por otro lado, `scoring.js` opera como el motor matemático de recomendación. Este archivo calcula el puntaje final en dos etapas: primero computa el atractivo analítico del partido ($S_{base}$) a partir del entretenimiento ($X_{ent}$) y el estilo táctico ($S_{\text{táctica}}$):
$$S_{base} = \sqrt{W_{\text{ent}} \cdot X_{\text{ent}}^2 + W_{\text{tec}} \cdot S_{\text{táctica}}^2}$$
Posteriormente, aplica la componente emocional de afinidad afectiva ($x_{af} \in [0.0, 1.0]$) como un interpolador lineal para obtener el score de recomendación final:
$$S_{final} = S_{base} + x_{af} \cdot (10.0 - S_{base})$$
Esta arquitectura modular y reactiva permite ofrecer recomendaciones dinámicas ultra veloces personalizadas sin requerir infraestructura cloud de backend.

### 3.3. Módulo de Agrupamiento y Similitud de Jugadores
Para realizar un mapa de agrupamiento de los jugadores según estilo de juego y la similitud entre jugadores, usamos técnicas de aprendizaje no supervisado, junto a técnicas de limpieza de datos para poder hacer la cruza de datos entre la bases de EA FC 2026, con nuestras tablas de jugadores convocados al mundial.

*   **Limpieza Unicode e Ingesta:** Mapea el dataset de EA FC 26 con la base de datos de convocados mundialistas resolviendo problemas de transliteración de nombres.
*   **PCA con Supresión de PC1:** Estandariza los 40 atributos y aplica análisis PCA para retener la varianza original del dataset. Descartamos el primer componente principal (PC1) debido a que su correlación de Pearson con el *overall* supera el 0.88 en todas las posiciones, lo que traía el conflicto de agrupación meramente por popularidad. Actualmente, KMeans agrupa exclusivamente sobre las componentes estilísticas restantes (PC2 a PCN) para clasificar a los jugadores por su arquetipo táctico en lugar de su nivel de habilidad general.

### 3.4. Integración en el Cliente (Frontend)
El motor de recomendación está basado en la arquitectura de recomendadores basados en contenidos, por encima de los otros tipos de recomendadores, como filtrado colaborativo o propuestas híbridas (Millán Gordillo, 2025). La ventaja que propone esta iniciativa es basar las recomendaciones enteramente en las preferencias del usuario, resolviendo el problema del *cold-start* para ítems nuevos, y nos ahorra la problemática de no tener datos sobre otros usuarios y sus preferencias en los grupos (lo que sería un limitante para un recomendador colaborativo).

El resultado de este recomendador opera el vector de pesos del usuario con el vector ponderado del partido y devuelve un score para cada partido. La experiencia del usuario está diferenciada para tres niveles de usuarios según su nivel de conocimiento:
*   **Usuario Casual:** Usuario con nulo conocimiento técnico del deporte. Se le excluye de las preguntas técnicas del fútbol. La interfaz se centra en cuestiones cualitativas del partido, ponderando el espectáculo puro y la presencia de equipos y jugadores favoritos.
*   **Usuario Intermedio:** Fanático promedio del fútbol con nociones de estilo y estrategia, que sigue valorando el factor afectivo de jugadores y selecciones junto al espectáculo general del partido.
*   **Usuario Experto:** Orientado a personas con preferencias muy definidas en la táctica de los equipos y arquetipos de jugadores específicos. Gran parte de su recomendación recae sobre los vectores de juego y estilo técnico puro de los planteles.

Para determinar el peso de cada macro-componente, se calculan coeficientes mediante una trivia inicial con respuestas de opción múltiple y deslizadores (para preservar la granularidad de la respuesta). El mismo procedimiento se realiza para calibrar las micro-componentes, garantizando que el usuario mantenga el control sobre la ponderación analítica final de la recomendación.

---

## 4. METODOLOGÍA DE VALIDACIÓN UTILIZADA

Para garantizar la fiabilidad del recomendador y la robustez del modelo analítico, se ejecutó un protocolo de validación multifásico que abarca desde la cohesión estadística del clustering hasta simulaciones estadísticas de gran escala y pruebas de integración.

### 4.1. Validación del Agrupamiento de Jugadores: Silhouette Score
La transición al agrupamiento estilístico puro (Método B, que descarta el primer componente principal $PC1$ por su alta colinealidad con el *overall* de los jugadores) se validó midiendo el coeficiente de silueta (*Silhouette Score*). Al eliminar el sesgo de habilidad bruta, la cohesión interna y separación de los clústeres tácticos mejoró significativamente en todas las posiciones:
*   **Goalkeepers ($K=3$):** Incrementó de $0.0955$ a $0.1295$ ($+35.6\%$).
*   **Centerbacks ($K=3$):** Incrementó de $0.1682$ a $0.1876$ ($+11.5\%$).
*   **Fullbacks ($K=4$):** Incrementó de $0.1391$ a $0.1979$ ($+42.3\%$).
*   **Midfielders ($K=4$):** Incrementó de $0.1591$ a $0.2268$ ($+42.6\%$).
*   **Strikers ($K=3$):** Incrementó de $0.1886$ a $0.2261$ ($+19.9\%$).
*   **Wingers ($K=3$):** Incrementó de $0.1577$ a $0.2410$ ($+52.8\%$).

Este análisis demuestra que los arquetipos resultantes (como distinguir a un *Central Creador* de un *Stopper Físico*) poseen una sólida significancia estadística y reflejan roles tácticos reales y bien definidos.

### 4.2. Calibración por Simulación de Monte Carlo
El motor de scoring se calibró mediante una simulación masiva de Monte Carlo ($N = 2000$ iteraciones) implementada en `estimation_montecarlo.py`. Se evaluó la distribución del score lineal bruto para calcular su media ($\mu = 1.8654$) y desviación estándar ($\sigma = 0.4320$). Estos parámetros permitieron calibrar una función logística de transferencia:
$$S_{match} = \frac{1}{1 + e^{-\left(\frac{\text{score\_lineal} - \mu}{\sigma}\right)}}$$

Esta calibración asegura que el *Smart Score* final se distribuya uniformemente en toda la escala del $1.0$ al $10.0$, evitando la saturación en los extremos y garantizando recomendaciones equilibradas en las tres categorías del sistema.

### 4.3. Validación Numérica de Multiplicadores de Escenario
Para comprobar la superioridad de la **Media Armónica** frente a la Aritmética y Geométrica en el cálculo del multiplicador de urgencia competitivo ($M_{match}$), se evaluaron dos escenarios asimétricos frecuentes en la fase de grupos:

*   **Caso A (Se juega la vida, $1.0$, vs. Eliminado, $0.60$):**
    *   *Media Aritmética:* $0.800$ | *Media Geométrica:* $0.774$ | *Media Armónica:* $\mathbf{0.750}$
*   **Caso B (Clasificado, $0.85$, vs. 1° Puesto Asegurado, $0.70$):**
    *   *Media Aritmética:* $0.775$ | *Media Geométrica:* $0.771$ | *Media Armónica:* $\mathbf{0.767}$

En la práctica deportiva, la presencia de un rival desmotivado (eliminado, Caso A) devalúa críticamente el espectáculo del encuentro. La media armónica es la única que penaliza severamente esta asimetría de motivación, ordenando correctamente la importancia competitiva del Caso B ($0.767$) por encima del Caso A ($0.750$), a diferencia de las medias aritmética y geométrica que fallan en la ordenación.

### 4.4. Pruebas y Calidad de Código Integrada
La integridad del software y el flujo de datos se validaron mediante una suite integrada de pruebas automatizadas y análisis estático:
*   **Pruebas Unitarias de API (`pytest`):** Cobertura exhaustiva en la suite `/transfermarkt-api/tests` para asegurar la correcta extracción de valores financieros, lesiones y perfiles de jugadores sin corrupción de datos.
*   **Auditoría de Estilo (`ruff`):** Análisis estático para el cumplimiento estricto de las directrices de código limpio en Python.
*   **Validación E2E (Playwright):** Pruebas funcionales en el frontend estático que aseguran el correcto cálculo del recomendador y la recalculación instantánea de los scores al ingresar marcadores dinámicos.