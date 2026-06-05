# INFORME METODOLÓGICO: SISTEMA DE RECOMENDACIÓN DE PARTIDOS – MUNDIAL 2026

**Equipo de Desarrollo & Especialistas en IA**  
*Competencia: "Tu tiempo, tu Mundial"*  
*Facultad de Ingeniería – Maestría en Inteligencia Artificial (MIA)*  

---

## 1. RESUMEN EJECUTIVO

El presente informe expone el diseño, desarrollo e implementación del **Sistema de Recomendación de Partidos para la Copa del Mundo FIFA 2026**, una solución de software interactiva y analíticamente avanzada diseñada para optimizar y personalizar la experiencia del usuario final durante el certamen mundialista. El objetivo principal de la aplicación es clasificar de forma dinámica los 104 encuentros en tres categorías de recomendación: **Imperdible**, **Vale la pena** y **Para ver el resumen**, adaptando la oferta deportiva a la disponibilidad de tiempo y las preferencias estéticas e identitarias de cada usuario.

### Desafíos Clave y Creatividad Analítica
El atractivo de un partido de fútbol no es una propiedad lineal que dependa de la suma simple de goles convertidos o de clasificaciones generales inerciales como el Ranking FIFA. El espectáculo es una propiedad emergente de la interacción táctica, física y competitiva entre dos selecciones. El principal desafío analítico resuelto por el equipo radica en **neutralizar los sesgos de aislamiento geográfico y distorsiones estadísticas de confederaciones asimétricas** (como la OFC o la AFC frente a UEFA o CONMEBOL) sin alterar arbitrariamente las métricas originales. 

Para lograrlo, el sistema introduce innovaciones analíticas de alta creatividad:
*   **Ajuste Métrico por Confederación ($M_{conf}$):** Alinea las medias ofensivas y defensivas de los equipos según la exigencia del ecosistema competitivo donde lograron dichos registros.
*   **Supresión de la Componente de Calidad ($PC1$):** Mediante el Análisis de Componentes Principales (PCA) aplicado al dataset técnico de jugadores de EA FC 26, se identificó que la primera componente principal ($PC1$) correlaciona en un $>88\%$ con la calidad general del futbolista. Al descartarla, el algoritmo KMeans agrupa a los futbolistas en arquetipos tácticos de forma estilística pura, evitando el sesgo de clasificar simplemente por habilidad o rendimiento bruto.
*   **Modelo de Elo Dinámico y Momentum (EMA):** En lugar de depender de rankings estáticos, el recomendador implementa un motor secuencial que actualiza el Elo y el estado de forma física y moral (momentum) en tiempo real mediante una media móvil exponencial sobre el error de predicción.

### Rigor Metodológico y Éxito del Sistema
Cada recomendación se encuentra respaldada por un marco matemático estricto. La calibración del motor de recomendación se realizó mediante una **simulación estadística de Monte Carlo de 2000 iteraciones**, permitiendo ajustar una función sigmoide de transferencia para normalizar de forma homogénea las similitudes y los puntajes. Asimismo, la urgencia deportiva de las selecciones se computa de manera dinámica en el cliente simulando exhaustivamente los escenarios restantes del grupo ($3^N$ combinaciones), aplicando una **Media Armónica** de urgencias para penalizar asimetrías de motivación y evitar que los partidos de equipos ya clasificados o eliminados falseen el Score de Espectáculo.

### Funcionalidad de la Demo Interactiva
El proyecto final culmina en una **aplicación web estática (GitHub Pages)** de alta fidelidad, con una landing page interactiva en 3D que conduce al usuario a un panel principal desacoplado (`app.html`). En él, cualquier usuario sin conocimientos técnicos puede modelar su perfil, cargar marcadores dinámicos para los encuentros, simular jornadas completas y visualizar instantáneamente cómo cambian el Elo, las posiciones del grupo y las recomendaciones de partidos.

---

## 2. EXPLICACIÓN DE VARIABLES CREADAS

Para la formulación de los scores de recomendación, se procesaron datos base de SofaScore, Wikipedia, Transfermarkt e historiales de la FIFA, a partir de los cuales se construyeron y definieron las siguientes variables clave en el backend (SQLite) y en el runtime del cliente (`state.js`, `scoring.js`):

### 2.1. Variables del Índice de Competitividad y Espectáculo (ICE)

*   **`ocasiones_norm`, `contra_norm`, `drama_norm`, `vuln_norm` (Real, Scope: Selección/Partido):** Representan los vectores normalizados de desempeño por partido del equipo. 
    *   *Ocasiones Claras ($OC_{norm}$):* Promedio de ocasiones de gol creadas por partido, ajustadas por confederación.
    *   *Contraataques ($CA_{norm}$):* Promedio de transiciones ofensivas rápidas.
    *   *Drama ($Drama_{norm}$):* Intensidad física y fricción del equipo (tarjetas y faltas por partido).
    *   *Vulnerabilidad ($Vuln_{norm}$):* Goles concedidos por partido, ajustados de manera inversa.
*   **$C_{dif}$ - Coeficiente de Dificultad del Oponente (Real $[0.5, 1.0]$, Scope: Selección):** Variable que mide la jerarquía de los rivales históricos enfrentados durante las eliminatorias oficiales, calculada a partir de la mediana del Ranking FIFA de los oponentes recientes ($R_{med}$):
    $$C_{dif} = 1.0 - 0.5 \times \left( \frac{R_{med} - 1}{209.0} \right)$$
    Este coeficiente actúa de forma multiplicativa en variables de producción ofensiva para castigar el volumen inflado frente a rivales de ranking bajo, y divisoria en variables de vulnerabilidad defensiva para penalizar la fragilidad mostrada ante oponentes menores.
*   **$M_{conf}$ - Multiplicador de Alineación por Confederación (Real, Scope: Confederación):** Factor de normalización intercontinental calculado como la división entre la media aritmética global de una variable y la media específica de la confederación:
    $$M_{conf} = \frac{\mu_{global}}{\mu_{conf}}$$
    Ajusta a la baja las estadísticas de regiones débiles (ej. OFC, $M_{conf} = 0.56$) y premia las logradas en zonas altamente competitivas (ej. CONMEBOL, $M_{conf} = 1.74$).
*   **$R_{\text{fricción}}$ - Relación de Fricción Global (Real, Scope: Auxiliar del Pipeline):** Coeficiente utilizado para imputar de manera rigurosa las faltas promedio de selecciones de confederaciones de baja densidad informativa en Sofascore, calculando la proporción de faltas/tarjetas de las 47 selecciones control:
    $$R_{\text{fricción}} = \frac{\sum_{i=1}^{47} \text{Faltas PG}_i}{\sum_{i=1}^{47} \text{Tarjetas PG}_i}$$
*   **$P_{\text{Brecha}}$ - Penalización por Asimetría Competitiva (Real $[0.0, 0.60]$, Scope: Partido):** Mide la falta de tensión competitiva cuando dos selecciones presentan una brecha de nivel excesiva. Se modela mediante una curva sigmoide logística sobre la diferencia de sus ratings de Elo Base:
    $$P_{\text{Brecha}} = \frac{0.60}{1 + e^{-0.01(\Delta Elo - 350)}}$$
    Esto asegura que diferencias menores a 200 puntos de Elo apenas afecten el score de espectáculo, mientras que cruces disparejos sufran castigos severos (hasta del 60%).

### 2.2. Variables de Simulación Dinámica y Elo

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

*   **Vector Táctico $V = [d, p, r, a]$ (Array 4D $[ -1.0, 1.0 ]$, Scope: Selección/Usuario):** Caracteriza el playstyle del equipo o las preferencias del usuario:
    1.  *Defensa ($d$):* Bloque bajo y repliegue (-1.0) vs. Presión alta activa (1.0).
    2.  *Posesión ($p$):* Transición directa vertical (-1.0) vs. Elaboración asociativa y Tiki-Taka (1.0).
    3.  *Ritmo de Juego ($r$):* Circulación controlada y pausada (-1.0) vs. Transición vertical explosiva (1.0).
    4.  *Ancho ($a$):* Ataque interior por pasillo central (-1.0) vs. Amplitud y desborde por bandas (1.0).
*   **$Score_{\text{Táctico Bruto}}$ (Real $[1.0, 10.0]$, Scope: Partido/Usuario):** Evaluación heurística que mide cuánto se alinean los estilos de juego de los contendientes con la preferencia táctica del usuario ($V_U$). Emplea la **Heurística del Protagonista** aplicando una amortiguación al rival para no penalizar partidos donde un solo equipo asume la propuesta buscada:
    $$Score_{\text{Táctico}} = \max(Sim(V_A, V_U), Sim(V_B, V_U)) + 0.1 \cdot \min(Sim(V_A, V_U), Sim(V_B, V_U))$$

### 2.4. Variables del Espacio de Recomendación Vectorial y Afectivo

*   **$\mathbf{W}_U$ - Vector de Pesos Normalizados del Usuario (Array $[0.0, 1.0]$, Scope: Usuario):** Coeficientes de importancia de las macro-componentes, calculados dinámicamente según un vector binario de activación $\mathbf{M} \in \{0, 1\}^3$ donde cada componente indica si el usuario proporcionó datos para esa dimensión (por ejemplo, si realizó el test táctico o configuró equipos/clubes/jugadores favoritos):
    $$\mathbf{W}_U = \left[ \frac{M_{\text{esp}} \cdot w_{\text{esp}}}{w_{\text{sum}}}, \frac{M_{\text{tác}} \cdot w_{\text{tác}}}{w_{\text{sum}}}, \frac{M_{\text{afec}} \cdot w_{\text{afec}}}{w_{\text{sum}}} \right]$$
    $$\text{donde } w_{\text{sum}} = \sum_{k=1}^{3} (M_k \cdot w_k)$$
    Esta normalización sum-based dinámica asegura que las componentes inactivas (como la afinidad táctica cuando no se ha hecho el test, o la afinidad afectiva si no hay favoritos configurados) sean completamente omitidas de la ecuación y no diluyan los puntajes de las dimensiones activas, permitiendo que un partido de puro espectáculo alcance la escala máxima de `10.0`.
*   **$P_{\text{juego}}$ - Probabilidad de Juego Estructurada (Real $[0.0, 1.0]$, Scope: Jugador):** Mide la probabilidad esperada de que un jugador $i$ vea minutos en el campo en base a su participación histórica en Eliminatorias o la Copa de Oro 2025:
    $$P_{\text{juego}}(i) = 
    \begin{cases} 
    \frac{\text{Minutos Jugados}_i}{\text{Partidos de Selección} \times 90} & \text{Si tiene minutos registrados en Eliminatorias / Copa Oro} \\
    \\
    \frac{\text{Valor Mercado}_i}{\max(\text{Valor Mercado de su Selección})} & \text{Si es convocado con 0 minutos (Regreso por lesión / Debutante)}
    \end{cases}$$
*   **$S_{\text{club}}$ - Score de Afinidad por Club (Real $[0.0, 1.0]$, Scope: Partido):** Mide el volumen acumulado de minutos probables de futbolistas pertenecientes al club favorito del usuario. Emplea una atenuación logarítmica para modelar rendimientos decrecientes y normaliza respecto a un factor del torneo ($Z_{\text{club}} = 5.0$):
    $$S_{\text{club}} = \frac{\log(1 + \sum P_{\text{juego}}(i))}{\log(1 + Z_{\text{club}})}$$
*   **$S_{\text{sel}}$ - Score de Selecciones Favoritas (Real $[0.0, 1.0]$, Scope: Partido):** Suma ponderada lineal aditiva que asigna un peso de $0.70$ a la selección principal del usuario ($I_p \in \{0,1\}$) y $0.30$ a cada selección menor secundaria ($n_m \in \{0, 1, 2\}$) que juegue el partido:
    $$S_{\text{sel}} = 0.70 I_p + 0.30 n_m$$
*   **$S_{\text{jug}}$ - Score de Jugadores Favoritos y Similares (Real $[0.0, 1.0]$, Scope: Partido):** Combina la presencia de los jugadores favoritos directos ($D$) del usuario y futbolistas similares en el espacio latente ($S$), atenuados por distancia euclidiana en el vector PCA y normalizados por $Z_{\text{jug}} = 3.0$:
    $$S_{\text{jug}} = \frac{1}{Z_{\text{jug}}} \left( \sum_{i \in D} P_{\text{juego}}(i) + \sum_{j \in S} \text{Sim}(j) P_{\text{juego}}(j) \right) \qquad (\text{con } \text{Sim}(j) = \frac{1}{1 + d_j})$$
*   **$\beta_{\text{drama}}$ (o `dramaBeta`) - Factor Dinámico de Fricción (Real $[0.0, 0.60]$, Scope: Parámetro de Ajuste del Usuario):** Mide la intensidad física tolerada o buscada por el usuario en el espectáculo, calibrable mediante el slider de la interfaz. Si se establece en `0.0`, anula por completo el peso de la fricción física (`dramaMatch`) dentro de la ecuación objetiva del espectáculo (ICE), impidiendo que contamine el score. Si el usuario prefiere juego limpio, la variable se invierte: $S_{\text{fricción}} = 11.0 - FriccionScore$; si prefiere juego físico, equivale al $FriccionScore$ bruto.

---

## 3. ARQUITECTURA DEL MODELO

El sistema está diseñado bajo una arquitectura modular y desacoplada que separa el procesamiento, enriquecimiento e inferencia de datos pesada (pipeline en Python) de la lógica de recomendación dinámica y visualización interactiva del lado del cliente (Frontend).

```mermaid
flowchart TD
    subgraph Pipeline de Ingesta y Datos (Python/SQLite)
        A[Wikipedia probable squads] -->|Ingesta Inicial| B[populate_data.py]
        C[API Transfermarkt Cache] -->|Market Value/Club/Edad| B
        B -->|worldcup_combined.db| D[parse_convocados.py]
        E[Lista de Convocados.md] -->|Verdad de Plantel / Stars| D
        D -->|Rachas y H2H histórico| F[enrich_team_stats.py]
        F -->|Vectores SofaScore/ELO| G[update_tactical_vectors.py]
        G -->|Consolidación JSON unificado| H[export_to_json.py]
    subgraph Algoritmos y Clustering de Jugadores
        EA[EA FC 26 Dataset] -->|StandardScaler + PCA sin PC1| I[HAC_clustering.py]
        I -->|Arquetipos por posición| J[cluster_profiling.py]
        J -->|Configuración de Similitudes| H
    end
    end

    H -->|wc2026_data.json| K((FRONTEND CLIENTE))
    
    subgraph Runtime del Navegador (HTML5/Vanilla JS)
        K --> L[state.js: Estado y Simulador]
        K --> M[scoring.js: Motor de Recomendación]
        L -->|Actualización Marcadores| N[results.js: Panel interactivo]
        L -->|Simulación Escenarios Grupos 3^N| O[groups.js: Posiciones en vivo]
        M -->|Fusión ICE + Playstyle + Boosts| P[main.js: Controlador y Renders]
        P -->|Recomendación Final: Smart Score| N
    end
end
```

### 3.1. Pipeline de Ingesta y Consolidación de Datos
El flujo de datos se consolida en una base de datos relacional compacta de 16 tablas (`worldcup_combined.db`), la cual unifica datos históricos y actuales:
1.  **Ingesta y Enriquecimiento Financiero:** `populate_data.py` recupera los planteles probables desde Wikipedia y consulta una API local de Transfermarkt. Para saltar los bloqueos por WAF/Captcha, el script implementa un almacenamiento en caché de base de datos (`cache_transfermarkt`) con más de 1680 registros resueltos de forma local.
2.  **Resolución de Convocados y Superestrellas:** `parse_convocados.py` cruza de forma estricta el fixture y los planteles confirmados desde el archivo estructurado [Lista de Convocados.md](file:///c:/Users/tomas/Desktop/proyectos/worldcup-app/Lista%20de%20Convocados.md), asignando el tag de jugador estrella a partir del percentil 75 del valor de mercado nacional o su estatus de crack histórico global.
3.  **Vectores Tácticos y Exportación:** `update_tactical_vectors.py` procesa los datos ofensivos y defensivos brutos de Sofascore y calcula los perfiles representados en los arrays 4D. Finalmente, `export_to_json.py` unifica las tablas relacionales en un único JSON compacto (`wc2026_data.json`) que elimina latencias de consulta backend al ser consumido de manera asíncrona por el frontend estático.

### 3.2. Módulo de Agrupamiento y Similitud de Jugadores
El cálculo del estilo de los jugadores opera mediante agrupamiento no supervisado:
*   **Limpieza Unicode e Ingesta:** Mapea el dataset de EA FC 26 con la base de datos de convocados mundialistas resolviendo problemas de transliteración de nombres.
*   **PCA con Supresión de PC1:** Estandariza los 40 atributos y aplica análisis PCA para retener el $\ge 80\%$ de varianza explicada. Descarta el primer componente principal (PC1) debido a que su correlación de Pearson con el *overall* supera el 0.88 en todas las posiciones. KMeans agrupa exclusivamente sobre las componentes estilísticas restantes (PC2 a PCN) para clasificar a los jugadores por su arquetipo táctico en lugar de su nivel de habilidad general.

### 3.3. Integración en el Cliente (Frontend)
El motor de ejecución reside enteramente en el lado del cliente, garantizando la escalabilidad del sistema y su costo cero de infraestructura:
*   **`state.js`:** Centraliza las preferencias de usuario, pesos asignados, marcadores simulados por el usuario (`simulatedScores`) y dispara de forma secuencial la recalculación de las tablas de posiciones y los Elo dinámicos.
*   **`scoring.js`:** Ejecuta en tiempo real la combinación ponderada de los scores de espectáculo (ICE) y tácticos de afinidad (Playstyle), sumando las bonificaciones aditivas configuradas por el usuario (club favorito, jugadores favoritos, etc.).
*   **`results.js` y `groups.js`:** Interfaces de usuario diseñadas en CSS puro que renderizan la interacción, permitiendo ingresar goles en vivo y ejecutar simulaciones probabilísticas con base en el diferencial de Elo en un solo clic.

---

## 4. METODOLOGÍA DE VALIDACIÓN UTILIZADA

Para garantizar la fiabilidad del recomendador y la robustez del modelo analítico, el equipo de desarrollo diseñó y ejecutó un protocolo de validación multifásico que abarca desde la cohesión del clustering hasta simulaciones estadísticas de gran escala.

### 4.1. Validación del Agrupamiento de Jugadores: Silhouette Score
La transición al **Método B** (eliminación de la componente de calidad $PC1$) se validó comparando el Silhouette Score de cohesión interna de los clústeres frente al modelo base de normalización simple. El incremento en la calidad de los grupos es evidente:

| Posición | K Óptimo | Silhouette (Original) | Silhouette (Método B) | Incremento de Cohesión |
| :--- | :---: | :---: | :---: | :---: |
| 🧤 **Goalkeepers** | 3 | 0.0955 | 0.1295 | **+35.6%** |
| 🛡️ **Centerbacks** | 3 | 0.1682 | 0.1876 | **+11.5%** |
| 🏃‍♂️ **Fullbacks** | 4 | 0.1391 | 0.1979 | **+42.3%** |
| 🧠 **Midfielders** | 4 | 0.1591 | 0.2268 | **+42.6%** |
| ⚽ **Strikers** | 3 | 0.1886 | 0.2261 | **+19.9%** |
| ⚡ **Wingers** | 3 | 0.1577 | 0.2410 | **+52.8%** |

Este análisis prueba que los arquetipos resultantes (ej. *Central Creador* liderado por Nathan Aké vs. *Stopper Físico* liderado por Virgil van Dijk) son estadísticamente significativos, compactos y representativos del estilo de juego real.

### 4.2. Calibración por Simulación de Monte Carlo
Para validar y escalar el recomendador, se desarrolló el script `estimation_montecarlo.py`. Este programa realiza una simulación masiva del pipeline de scoring con los siguientes parámetros:
*   **Iteraciones ($N$):** 2000 simulaciones aleatorias de enfrentamientos y combinaciones de preferencias del usuario.
*   **Métrica de Éxito:** Se busca modelar la distribución del puntaje lineal bruto para determinar el centroide $\mu$ y la dispersión $\sigma$ exactos que permitan mapear los resultados a una escala uniforme $[0.0, 1.0]$ mediante una función logística de transferencia:
    $$S_{match} = \frac{1}{1 + e^{-\left(\frac{total\_score - \mu}{\sigma}\right)}}$$
*   **Resultados de la Calibración:**
    *   *Media ($\mu$):* $1.8654$
    *   *Desviación Estándar ($\sigma$):* $0.4320$
    *   *Score lineal mínimo registrado:* $0.7812$
    *   *Score lineal máximo registrado:* $3.9451$

Los coeficientes obtenidos fueron guardados en `recommender_config.json` y se inyectaron directamente en la lógica del motor en caliente, garantizando que el Smart Score se distribuya uniformemente en toda la escala del $1.0$ al $10.0$ sin saturar los extremos de recomendación.

### 4.3. Validación Numérica de Multiplicadores de Escenario
Para comprobar que la **Media Armónica** implementada en la variable $M_{match}$ superaba a las alternativas clásicas (Media Aritmética y Geométrica) en la priorización de urgencias competitivas de la fase de grupos, se realizó un análisis numérico comparativo:

*   **Caso A: Un equipo se juega la vida ($1.0$) vs. Uno eliminado ($0.60$):**
    *   *Media Aritmética:* $\frac{1.0 + 0.60}{2} = 0.800$
    *   *Media Geométrica:* $\sqrt{1.0 \times 0.60} = 0.774$
    *   *Media Armónica:* $\frac{2 \times 1.0 \times 0.60}{1.0 + 0.60} = \mathbf{0.750}$
*   **Caso B: Un equipo clasificado ($0.85$) vs. Uno con el primer puesto asegurado ($0.70$):**
    *   *Media Aritmética:* $\frac{0.85 + 0.70}{2} = 0.775$
    *   *Media Geométrica:* $\sqrt{0.85 \times 0.70} = 0.771$
    *   *Media Armónica:* $\frac{2 \times 0.85 \times 0.70}{0.85 + 0.70} = \mathbf{0.767}$

*Justificación Teórica de la Selección:* En el fútbol competitivo, un encuentro donde uno de los equipos está completamente desmotivado (eliminado, Caso A) pierde gran parte del espectáculo táctico directo. Sin embargo, la media aritmética sitúa al Caso A ($0.80$) por encima del Caso B ($0.775$), lo cual es una anomalía analítica. La media geométrica también falla al jerarquizar incorrectamente el orden. La **Media Armónica** castiga fuertemente el extremo desmotivado de la asimetría, ordenando correctamente el Caso B ($0.767$) por encima del Caso A ($0.750$).

### 4.4. Pruebas y Calidad de Código Integrada
El proyecto cuenta con un entorno de validación continuo configurado en `pytest.ini`:
*   **Pruebas Unitarias de API (`pytest`):** Cobertura exhaustiva en la suite `/transfermarkt-api/tests` validando la consistencia en el raspado de perfiles, valores de mercado, lesiones e historiales de transferencia de los jugadores.
*   **Auditoría Estática:** Integración de la herramienta `ruff` para verificar la conformidad de estilo y la calidad analítica del código en Python, asegurando el cumplimiento de las buenas prácticas de programación científica.
*   **Validación de Flujo Cruzado (Playwright):** Comprobación en vivo del renderizado correcto en el cliente ante la inyección de datos dinámicos en las tablas del simulador, validando que el sitio web sea 100% responsivo e intuitivo para usuarios no técnicos.
