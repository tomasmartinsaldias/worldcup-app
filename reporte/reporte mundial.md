# INFORME METODOLÓGICO: SISTEMA DE RECOMENDACIÓN DE PARTIDOS – MUNDIAL 2026

*Competencia: "Tu tiempo, tu Mundial"*  
*Facultad de Ingeniería – Maestría en Ingeniería Artificial (MIA)*  
*Integrantes: Simón Canorio, Franco Tomás Esterellas Engler, Francisco Monti y Tomás Martín Saldías*

---
<div class="twocolumn">

## 1. RESUMEN EJECUTIVO

El presente informe expone el diseño, desarrollo e implementación del Sistema de Recomendación de Partidos para la Copa del Mundo FIFA 2026, un sistema de recomendación basado en contenido (Millán Gordillo, 2025) que personaliza la experiencia del usuario durante el certamen mundialista. El objetivo principal de la aplicación es clasificar de forma dinámica los 104 encuentros en tres categorías de recomendación: **Imperdible**, **Vale la pena** y **Para ver el resumen**, adaptando la oferta deportiva a la disponibilidad de tiempo y las preferencias estéticas e identitarias de cada usuario.

### Desafíos Clave y Creatividad Analítica
El principal desafío analítico consistió en mapear las preferencias del usuario y los atributos de los encuentros en un espacio vectorial homogéneo. El sistema define el perfil del usuario dividiendo la toma de decisiones en tres capas complementarias: la del entretenimiento, la del sentimiento y la técnico-analítica. A su vez, cada componente se descompone en microcomponentes que aportan, ponderadamente, a su score.

---

## 2. ARQUITECTURA DEL MODELO

Una arquitectura modular desacoplada separa el procesamiento, enriquecimiento e inferencia de datos pesada (pipeline ejecutado localmente en Python) de la lógica de recomendación dinámica y visualización interactiva del lado del cliente (Frontend). Este enfoque descentralizado optimiza el despliegue en entornos estáticos como GitHub Pages, eliminando la necesidad de servidores de base de datos en producción y reduciendo a cero la latencia de red en las consultas del recomendador.

![[Data Ingestion Pipeline for-2026-06-05-033235.png|500]]

### 2.1. Pipeline de Ingesta y Consolidación de Datos
La base de datos SQLite offline unifica registros históricos y datos actuales del torneo. El script `populate_data.py` estructura las plantillas y consulta valoraciones financieras en Transfermarkt mediante una caché local que elude límites de peticiones. Seguidamente, `parse_convocados.py` procesa el archivo de control `Lista de Convocados.md` para actualizar el fixture mundialista con los nombres definitivos del torneo y etiquetar a las estrellas de cada selección. El criterio de clasificación define como estrellas a los futbolistas con un valor de mercado en Transfermarkt superior a los €40.000.000, junto a una selección de superestrellas globales curada manualmente (ej. Lionel Messi) para asegurar su inclusión sin importar devaluaciones o edad.

### 2.2. Módulo de Agrupamiento y Similitud de Jugadores
Un agrupamiento no supervisado clasifica a los jugadores según su estilo de juego. El sistema realiza una limpieza unicode de nombres para cruzar los planteles del mundial con el dataset técnico de EA SPORTS FC 26. A continuación, el análisis PCA reduce los 40 atributos originales estandarizados. 

El modelo descarta la primera componente principal ($PC1$) al demostrarse una correlación lineal sumamente alta (entre $0.60$ y $0.96$ según la posición) entre la proyección sobre $PC1$ y la valoración general (*overall*) de los futbolistas. La supresión de esta componente de calidad bruta permite al algoritmo KMeans clasificar a los jugadores por sus características tácticas y de distribución de habilidades (*playstyle*) puras en lugar de su nivel de popularidad o habilidad absoluta (ver detalle analítico y gráfico en el **Anexo B**).

### 2.3. Integración en el Cliente
El motor de recomendación utiliza una arquitectura basada en contenido (Millán Gordillo, 2025) que soluciona el problema de arranque en frío (*cold-start*) y prescinde de datos de terceros. El recomendador opera el vector de pesos del usuario con las métricas del partido para segmentar la experiencia en tres niveles:
*   **Usuario Casual:** Centrado en la espectacularidad general y presencia de sus equipos y jugadores favoritos, excluyendo variables técnicas.
*   **Usuario Intermedio:** Combina nociones de estilo y estrategia con el factor afectivo de sus selecciones y jugadores favoritos.
*   **Usuario Experto:** Focalizado en la afinidad táctica de los planteles y arquetipos específicos de los jugadores.

La calibración de los pesos macro y microcomponentes se realiza a partir de las respuestas del usuario en una trivia inicial de onboarding y deslizadores en la interfaz.

---

## 3. CONSTRUCCIÓN DE VARIABLES Y MOTORES DE SCORING

Para la formulación de los scores de recomendación, se procesaron datos de SofaScore, Wikipedia, Transfermarkt, EA SPORTS FC 26 e historiales de la FIFA. La recomendación final surge de operar el Vector del Usuario con las variables del encuentro a través de tres dimensiones independientes de puntuación acotadas en el rango $[0, 10]$.

### 3.1. Dimensiones del Usuario y Ponderaciones (User Vector)
El Vector del Usuario ($V_U$) representa las preferencias configuradas en el onboarding o mediante controles deslizantes:
*   **Pesos Macro Principales (`w_entretenimiento`, `w_tactica`, `w_afectivo`):** Determinan el peso asignado a las tres macrodimensiones. Se normalizan automáticamente a Coeficientes Derivados ($W_{ent}, W_{tec}, W_{af}$) mediante una ecuación sum-based para garantizar la estabilidad del score (ver **Anexo A**).
*   **Pesos Micro (Sub-pesos):** Regulan la importancia interna de cada microcomponente (Espectáculo y Fricción para Entretenimiento; Estilo y Clústeres para Táctica; Clubes, Selecciones y Jugadores para Afectivo).
*   **Vector Táctico del Usuario ($V_U = [d_U, p_U, r_U, a_U]$):** Define la propuesta táctica predilecta en un espacio tetradimensional de Defensa, Posesión, Ritmo y Ancho.

### 3.2. Dimensión de Entretenimiento ($X_{ent}$)
El macrocomponente de Entretenimiento ($X_{ent}$) evalúa el dinamismo esperado del encuentro combinando dos microcomponentes ponderados:
1.  **Espectáculo (ICE):** Predice la fluidez y volumen de ataque del partido. Combina los promedios de ocasiones creadas ($OC_{norm}$) y contraataques ($CA_{norm}$) de ambas selecciones (ajustadas por confederación mediante $M_{conf}$ e historial de rivales con $C_{dif}$), atenuadas por la vulnerabilidad defensiva ($Vuln_{norm}$). Este cálculo emplea coeficientes calibrados de $\gamma = 0.5$ (amplificación por vulnerabilidad) y $\alpha = 0.5$ (peso de transiciones rápidas). Además, se escala por el factor de calidad del plantel ($Q_{match}$), la urgencia deportiva ($M_{match}$ o Stakes) y la penalización por asimetría competitiva ($P_{\text{Brecha}}$).
2.  **Fricción:** Mide la intensidad física del encuentro utilizando el promedio de drama y tarjetas ($Drama_{norm}$). El motor discrimina el interés del usuario usando el parámetro `frictionPreference`: si busca juego limpio (*Fair Play*), invierte el drama ($x_{fric} = 1.0 - \text{drama}_{avg}$); si prefiere juego físico o es indiferente, mantiene el valor físico bruto ($x_{fric} = \text{drama}_{avg}$). Los usuarios indiferentes pueden anular el impacto del sub-score asignando un peso micro de cero (`w_fric = 0`).

### 3.3. Dimensión Táctica ($X_{tec}$)
Mide la coincidencia estratégica del partido con las preferencias estratégicas del usuario y opera en dos niveles:
1.  **Estilo de Equipo ($s_{style}$):** Similitud coseno entre $V_U$ y los vectores continuos $V_A, V_B$ (calculados en SofaScore). Aplica la **Heurística del Protagonista** (ponderando al equipo con mayor afinidad y atenuando al rival con un factor $\lambda = 0.1$) para no castigar encuentros donde un solo equipo asume la iniciativa táctica que el usuario desea ver.
2.  **Afinidad por Clústeres ($s_{cluster}$):** Evalúa la similitud euclidiana exponencial de los jugadores en cancha respecto a los arquetipos drafteados en el onboarding, atenuada por su probabilidad de juego.

### 3.4. Dimensión Afectiva ($X_{af}$)
Cuantifica el apego emocional del usuario en base a la probabilidad de juego estimada del futbolista ($P_{\text{juego}}$), que evalúa su participación histórica reciente y valor de mercado:
1.  **Afinidad por Clubes ($s_{club}$):** Presencia en ambos planteles de futbolistas pertenecientes a los clubes favoritos del usuario, atenuada de forma logarítmica para modelar rendimientos decrecientes.
2.  **Afinidad por Selecciones ($s_{sel}$):** Premia con peso completo ($1.0$) la presencia de la selección prioritaria del usuario y añade un factor aditivo secundario ($0.5$) por cada selección menor favorita que dispute el encuentro.
3.  **Afinidad por Jugadores ($s_{jug}$):** Combina la participación de jugadores favoritos directos con la similitud en el espacio latente del PCA de otros jugadores de su misma posición.

### 3.5. Agregación y Score Final (Norma L2)
Para unificar los macrocomponentes ($X_{ent}, X_{tec}, X_{af}$) se utiliza una **Norma L2 ponderada con pesos fijos**:
$$S = \sqrt{W_{ent} \cdot X_{ent}^2 + W_{tec} \cdot X_{tec}^2 + W_{af} \cdot X_{af}^2}$$
La norma $L_2$ ofrece dos ventajas analíticas críticas:
- **Resalta Picos de Excelencia:** Los exponentes cuadráticos aseguran que componentes sobresalientes (como una afinidad afectiva máxima o una táctica impecable) empujen con mayor peso el score final, evitando que componentes promedio diluyan el interés de un partido único.
- **Evita la Homogeneidad:** Abre la dispersión de puntuaciones, destacando los encuentros genuinamente emocionantes sobre los promedio.

---

## 4. METODOLOGÍA DE VALIDACIÓN

Se ejecutó un protocolo de validación multifásico para garantizar la consistencia estadística del recomendador:

*   **Validación de Clústeres:** La transición al agrupamiento de *playstyle* puro mediante el **Método B** (que aplica `StandardScaler` + `PCA` sin $PC1$) se validó midiendo el coeficiente de silueta (*Silhouette Score*) frente al **Método Anterior** (que aplicaba `MaxAbsScaler` + `L2 norm` sobre todas las dimensiones en el espacio original sin reducción). La cohesión interna y delimitación de los clústeres mejoró notablemente en todas las posiciones, registrando incrementos de cohesión de entre el **$11.5\%$ y el $52.8\%$** (ver tabla comparativa en el **Anexo B**).
*   **Calibración Monte Carlo:** Una simulación masiva ($N = 2000$ iteraciones) determinó la media ($\mu = 1.8654$) y desviación estándar ($\sigma = 0.4320$) de la distribución lineal del score. Esto permitió ajustar la función de transferencia logística para garantizar una distribución uniforme del score final entre $1.0$ y $10.0$.
*   **Validación de Urgencia (Stakes):** Se demostró numéricamente que la **Media Armónica** implementada en $M_{match}$ es la única métrica capaz de penalizar asimetrías de motivación correctamente. Mientras que la media aritmética pondera un partido asimétrico por encima de uno competitivo equilibrado de menor nivel, la media armónica castiga el extremo desmotivado de la asimetría para priorizar los encuentros donde ambos planteles se juegan la clasificación.
*   **Calidad de Código y Flujo:** Pruebas unitarias de extracción con `pytest` en la suite de Transfermarkt, verificación de ruff para código limpio en Python, y validación E2E en el frontend con Playwright aseguran la robustez integral de la aplicación.

---

## ANEXOS

### ANEXO A: FORMULACIÓN MATEMÁTICA Y MOTORES DE SCORING

#### A.1. Ecuaciones del Vector de Partido
- **Coeficiente de Dificultad del Oponente ($C_{dif}$):**
$$\begin{aligned} \text{pass\_ratio} &= \frac{\text{acc\_opp\_half}}{\text{acc\_own\_half}+\text{acc\_opp\_half}} \\[1ex] D_{bruto} &= (\text{pass\_ratio} \cdot C_{dif}) - \frac{\frac{\text{clearances}}{C_{dif}}}{100.0} \end{aligned}$$
- **Multiplicador por Confederación ($M_{conf}$):**
  $$M_{conf} = \frac{\mu_{global}}{\mu_{conf}}$$
- **Relación de Fricción Global ($R_{\text{fricción}}$):**
  $$R_{\text{fricción}} = \frac{\sum_{i=1}^{47} \text{Faltas PG}_i}{\sum_{i=1}^{47} \text{Tarjetas PG}_i} \implies \text{Faltas PG} = \text{Tarjetas PG} \times R_{\text{fricción}}$$
- **Penalización por Asimetría Competitiva ($P_{\text{Brecha}}$):**
  $$P_{\text{Brecha}} = \frac{0.60}{1 + e^{-0.01(\Delta Elo - 350)}}$$
- **Vectores Tácticos del Equipo ($V = [d, p, r, a]$):**
  - *Posesión:* $$P_{bruto}=\text{pos\_pct}\cdot\left(1.0-\frac{\text{long\_balls}+\text{crosses}}{\text{accurate\_passes}}\right)\cdot C_{dif}$$
  - *Ancho:* $$A_{bruto}=\frac{\text{attempted\_crosses}}{\text{acc\_opposition\_half}}\cdot C_{dif}$$
  - *Ritmo:* $$R_{bruto}=\frac{\text{total\_shots}+\frac{\text{counter\_attacks}}{\text{matches}}}{\text{pos\_pct}}\cdot C_{dif}$$
  - *Defensa:* $$D_{bruto}=(\text{pass\_ratio}\cdot C_{dif})-\frac{\frac{\text{clearances}}{C_{dif}}}{100.0} \qquad \text{donde } \text{pass\_ratio} = \frac{\text{acc\_opp\_half}}{\text{acc\_own\_half}+\text{acc\_opp\_half}}$$
  Normalizados de forma individual a: $$z = \frac{x_{bruto} - \mu}{\sigma} \implies v_i = \tanh(0.6 \cdot z)$$

#### A.2. Ecuaciones del Motor de Scoring (Microcomponentes)
- **Fórmula del Espectáculo (ICE) Bruto:**
$$\begin{aligned}
ice &= \Big( \text{oc}_{match} \cdot (1 + 0.5 \cdot \text{vuln}_{match}) \\
&\quad + 0.5 \cdot \text{ca}_{match} \Big) \cdot (1 - p_{brecha})
\end{aligned}
$$
- **Lógica de Fricción ($x_{fric}$):**
  $$
x_{fric} = 
\begin{cases} 
1.0 - \text{drama}_{avg} \\ 
\quad \text{si } \text{frictionPreference} = \text{'fair\_play'} \\[1ex]
\text{drama}_{avg} \\ 
\quad \text{si } \text{frictionPreference} \in \{\text{'roce'}, \text{'indiferente'}\} 
\end{cases}
$$

$$
\text{frictionScore} = 1.0 + 9.0 \cdot x_{fric}
$$
- **Similitud Táctica del Equipo ($s_{style}$):**
 $$\begin{aligned} \text{sim}(V, V_U) &= \frac{V \cdot V_U}{|V| |V_U|} \\[1ex] \text{RawPlaystyle} &= \max(\text{sim}_A, \text{sim}_B) \\ &\quad + 0.1 \cdot \min(\text{sim}_A, \text{sim}_B) \\[1ex] s_{style} &= 10.0 \cdot \left( \frac{\text{RawPlaystyle} + 1.1}{2.2} \right) \end{aligned}$$
- **Afinación de Clústeres Drafteados ($s_{cluster}$):**
  $$\begin{aligned} J_{draft} &= \sum_{p \in \text{Match}} \left( \frac{e^{-3.0 \cdot dist_p} - e^{-3.0}}{1.0 - e^{-3.0}} \right) \cdot P_{\text{juego}}(p) \\[1ex] s_{cluster} &= \min\left(1.0, \frac{\ln(1 + J_{draft})}{\ln(1 + 5.0)}\right) \end{aligned}$$
- **Probabilidad de Juego ($P_{\text{juego}}$):**
  $$\begin{aligned} IPH &= 0.7 \cdot \left( \frac{N_{\text{titular}}}{N_{\text{equipo}}} \right) \\ &\quad + 0.3 \cdot \min\left( 1.0, \frac{M_{\text{jugados}}}{N_{\text{equipo}} \cdot 90} \right) \\[1ex] P_{\text{juego}} &= \frac{1}{1 + e^{-10 \cdot (IPH - 0.55)}} \end{aligned}$$
  *(Si no cuenta con registros en eliminatorias, se utiliza $P_{\text{juego}} = \text{Valor Mercado}_i / \max(\text{Valor Mercado Selección})$)*.
- **Afinidad por Clubes ($s_{club}$):**
  $$\begin{aligned} x_{partido} &= \sum_{p \in A} P_{\text{juego}}(p) I_{\text{club } p \in \text{Favs}} \\ &\quad + \sum_{q \in B} P_{\text{juego}}(q) I_{\text{club } q \in \text{Favs}} \\[1ex] s_{club} &= \min\left(1.0, \frac{\ln(1.0 + x_{partido})}{\ln(1.0 + 5.0)}\right) \end{aligned}$$
- **Afinidad por Jugadores Favoritos ($s_{jug}$):**
  $$\begin{aligned} J_d &= \sum_{p \in \text{Direct Favs}} P_{\text{juego}}(p) \\[1ex] J_s &= \sum_{q \notin \text{Direct Favs}} \max_{f \in \text{Favs}} \left( \frac{1}{\text{dist}(q, f) + 0.1} \right) \\ &\quad \cdot P_{\text{juego}}(q) \\[1ex] s_{jug} &= \min\left(1.0, \frac{\ln(1.0 + J_d)}{\ln(2.0)} + 0.5 \cdot \ln(1.0 + J_s)\right) \end{aligned}$$

---

### ANEXO B: VALIDACIÓN DEL AGRUPAMIENTO Y SIMULACIONES

#### B.1. Coeficientes de Correlación de Pearson ($R$) entre PC1 y Overall
La Componente Principal 1 ($PC1$) captura el nivel bruto del futbolista en lugar de sus características estilísticas particulares de distribución de atributos:
*   **Goalkeepers:** $R = 0.6042$
*   **Centerbacks:** $R = 0.8888$
*   **Fullbacks:** $R = 0.9524$
*   **Midfielders:** $R = 0.9320$
*   **Strikers:** $R = 0.9577$
*   **Wingers:** $R = 0.9651$

El siguiente gráfico consolida esta correlación para todas las posiciones:

![Correlación entre la Componente Principal 1 (PC1) y el Overall|500](../documentacion/plots/pc1_vs_overall_correlation.png)

#### B.2. Tabla de Silhouette Scores por Posición (Método Anterior vs. Método B)
La comparación muestra la mejora al migrar del agrupamiento sobre el espacio original con normalización básica (Método Anterior) al agrupamiento estilístico con StandardScaler + PCA sin $PC1$ (Método B):

| Posición | K Óptimo | Silhouette (Método Anterior - Espacio Original) | Silhouette (Método B - sin PC1) | Incremento de Cohesión |
| :--- | :---: | :---: | :---: | :---: |
| **Goalkeepers** | 3 | 0.0955 | 0.1295 | **+35.6%** |
| **Centerbacks** | 3 | 0.1682 | 0.1876 | **+11.5%** |
| **Fullbacks** | 4 | 0.1391 | 0.1979 | **+42.3%** |
| **Midfielders** | 4 | 0.1591 | 0.2268 | **+42.6%** |
| **Strikers** | 3 | 0.1886 | 0.2261 | **+19.9%** |
| **Wingers** | 3 | 0.1577 | 0.2410 | **+52.8%** |

#### B.3. Comparativa Numérica del Multiplicador de Stakes ($M_{match}$)
La media armónica prioriza al valor menor, castigando partidos desbalanceados (un equipo jugándose la vida vs. uno desmotivado):
- **Caso A (Motivación 1.0 vs. Eliminado 0.60):**
  - *Media Aritmética:* $0.800$ | *Media Geométrica:* $0.774$ | *Media Armónica:* $\mathbf{0.750}$ (mayor castigo analítico).
- **Caso B (Motivación Clasificado 0.85 vs. 1° Puesto Asegurado 0.70):**
  - *Media Aritmética:* $0.775$ | *Media Geométrica:* $0.771$ | *Media Armónica:* $\mathbf{0.767}$ (representación de alta competencia).

</div>

---

## 7. REFERENCIAS

- Esgueva Mariño, G. (2025). *Economía del deporte: Rankings y ratings* [Trabajo de fin de grado, Universidad de Valladolid]. Repositorio Documental de la Universidad de Valladolid. https://uvadoc.uva.es/handle/10324/77397
- Millán Gordillo, M. (2025, julio). *Estudio comparativo de sistemas de recomendación mediante filtrado colaborativo, basado en contenido y propuestas híbridas* [Trabajo de Fin de Máster, Universidad Loyola]. Repositorio Institucional de la Universidad Loyola (Brújula). https://hdl.handle.net/20.500.12412/6735