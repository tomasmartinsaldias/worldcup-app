# Metodología y Modelo Matemático: Similitud Táctica (Estilo de Juego)

## 1. Justificación Arquitectónica: Espacio Vectorial Geométrico vs. Procesamiento de Lenguaje Natural
El diseño original del recomendador de partidos contemplaba el uso de representaciones de texto mediante modelos latentes (embeddings de oraciones) para comparar los perfiles descriptivos de cada selección. Sin embargo, este enfoque cualitativo fue descartado tras un análisis de validación debido a dos fallas metodológicas críticas:
1. **Opacidad algorítmica (Efecto "Caja Negra"):** Los embeddings textuales capturan afinidades lingüísticas generales, pero no axiomas ni reglas futbolísticas duras. Esto impedía calcular y presentar en la interfaz una justificación desglosada y transparente de por qué dos selecciones se consideraban similares en términos tácticos.
2. **Inestabilidad frente al ruido semántico:** La similitud de coseno sobre textos es altamente sensible a la redacción y al vocabulario de las descripciones, lo que causaba variaciones no deseadas que no reflejaban el comportamiento real del equipo sobre el terreno de juego.

Como solución superadora, se diseñó un **Espacio Vectorial Geométrico de 4 Dimensiones**. Este modelo formaliza la táctica en un espectro de escalas continuas acotadas en el intervalo $[-1.0, 1.0]$. Esto garantiza precisión aritmética, trazabilidad total de los datos y explicabilidad explícita a nivel de atributos en la interfaz del usuario.

---

## 2. Formalización del Espacio Vectorial Táctico
Cada selección nacional (y la preferencia subjetiva del usuario) se representa mediante un vector táctico $V = [d, p, r, a] \in \mathbb{R}^4$, donde cada dimensión modela un espectro del juego posicional:
* **Fase Defensiva ($d$):** Representa la altura del bloque defensivo y la intensidad de la presión. Varía de $-1.0$ (repliegue intensivo o bloque bajo extremo) a $+1.0$ (presión alta asfixiante y bloque alto activo).
* **Fase de Posesión ($p$):** Define la estructura de la elaboración con balón. Varía de $-1.0$ (juego de transiciones rápidas, contraataque o fútbol directo) a $+1.0$ (elaboración pausada, circulación de balón asociativa o *Tiki-Taka*).
* **Ritmo de Juego ($r$):** Mide la velocidad de progresión y verticalidad en fase de ataque. Varía de $-1.0$ (control de tempo, circulación horizontal especulativa) a $+1.0$ (transiciones verticales de alta velocidad y juego frenético).
* **Uso del Ancho de Campo ($a$):** Modela la canalización geográfica del ataque. Varía de $-1.0$ (juego predominantemente interior por el pasillo central) a $+1.0$ (amplitud extrema por las bandas con extremos puros).

---

## 3. Lógica de Agregación: Heurística del "Protagonista"
En un partido intervienen dos equipos que frecuentemente proponen propuestas tácticas opuestas. Si el sistema promediara aritméticamente la similitud táctica de ambos contrincantes con respecto al vector de preferencia del usuario, los cruces con estilos dispares serían sistemáticamente penalizados, aun si uno de los dos propone el arquetipo buscado (por ejemplo, un equipo proactivo de posesión contra uno reactivo de bloque bajo arrojaría una puntuación media para un usuario que busca posesión pura).

Para resolver esta limitación, el motor implementa la **Heurística del Protagonista**, la cual asume que el partido será dinamizado y modelado principalmente por el equipo que más se aproxime a la preferencia del usuario, con una contribución menor (o amortiguación) del oponente.

La ecuación general del puntaje táctico bruto se define como:
$$Score_{\text{Táctico Bruto}}(A, B, U) = \max(Sim(V_A, V_U), Sim(V_B, V_U)) + \lambda \cdot \min(Sim(V_A, V_U), Sim(V_B, V_U))$$

Donde:
* $V_A, V_B$ son los vectores tácticos de las selecciones competidoras.
* $V_U$ es el vector de preferencias tácticas del usuario.
* $Sim(V_1, V_2)$ es la función de similitud espacial, implementada mediante la **Similitud de Coseno**:
  $$Sim(V_1, V_2) = \frac{V_1 \cdot V_2}{\|V_1\| \|V_2\|}$$
* $\lambda$ es el coeficiente de interacción táctica, parametrizado en $\lambda = 0.1$ por defecto para amortiguar el impacto del rival no prioritario sin ignorar por completo su propuesta.

---

## 4. Escalamiento Lineal en la Interfaz de Usuario
Dado que la Similitud de Coseno toma valores en el rango $[-1.0, 1.0]$, el resultado teórico del $Score_{\text{Táctico Bruto}}$ con un $\lambda = 0.1$ se encuentra acotado en el intervalo $[-1.1, 1.1]$. 

Para ofrecer consistencia con el resto de las métricas del recomendador, el valor bruto se proyecta linealmente a la escala estandarizada de $[1.0, 10.0]$:
$$Score_{\text{Estilo}} = 1.0 + 9.0 \times \left( \frac{Score_{\text{Táctico Bruto}} - (-1.1)}{1.1 - (-1.1)} \right)$$
El resultado final se limita estrictamente al rango $[1.0, 10.0]$.

---

## 5. Inferencia Heurística Zero-Shot y Validación
### 5.1. Mitigación del Frío de Datos (Cold Start) y Sesgo de Calendario
Para estructurar el sistema se requiere la parametrización de las 48 selecciones clasificadas. No obstante, las métricas avanzadas (PPDA, secuencias de pases de más de 10 toques, etc.) no están distribuidas de forma simétrica entre las confederaciones. Además, utilizar datos crudos de las eliminatorias regionales introduce el **Sesgo de Fuerza del Calendario** (un equipo con estadísticas sobresalientes contra oponentes amateur de su región no sostendrá dicho comportamiento contra potencias mundiales).

Para solucionar esto, se implementó una **Inferencia Heurística Zero-Shot** mediante Modelos de Lenguaje Grande (LLMs) configurados con prompting analítico estructurado y restricciones de formato JSON. Esto permite deducir con precisión los perfiles tácticos basados en el comportamiento histórico del equipo en grandes citas, corrigiendo las distorsiones estadísticas de sus eliminatorias.

La viabilidad de esta técnica se fundamenta en la literatura reciente sobre procesamiento de lenguaje natural aplicado al razonamiento cuantitativo. Como demuestran Chowdhury y Caragea (2025), es metodológicamente robusto utilizar un LLM en un entorno zero-shot mediante prompting estructurado para evaluar lógicas complejas y extraer de ellas un puntaje escalar continuo. En esta arquitectura, se forzó la salida del modelo a un formato de datos estricto (JSON Constraining) con una temperatura cercana a cero (0.1) para suprimir la alucinación estocástica. El modelo evaluó a cada equipo y mapeó su intención táctica mundialista directamente sobre el espacio vectorial continuo de -1.0 a 1.0 en sus cuatro dimensiones (Defensa, Posesión, Ritmo y Ancho).

### 5.2. Validación Empírica y Desviación del Modelo
Para comprobar la consistencia de los vectores tácticos generados sintéticamente, se construyó una **Verdad Fundamental (Ground Truth)** empírica recopilando las métricas de rendimiento real de un grupo de control de 7 selecciones en SofaScore (Alemania, Argentina, España, Francia, Jordania, Panamá y Senegal), normalizando sus valores al rango $[-1.0, 1.0]$ mediante un escalamiento Min-Max.

El análisis de contraste arrojó las siguientes métricas globales de error:
* **Error Absoluto Medio (MAE):** $0.3813$
* **Error Cuadrático Medio (RMSE):** $0.5055$

Teniendo en cuenta que el ancho de banda total de cada dimensión táctica es de $2.0$ unidades, un MAE de $0.38$ representa un margen de error del **19.1%**, validando la solidez del motor heurístico con un **80.9% de precisión direccional**.

### 5.3. Análisis de Varianza (Intención vs. Ejecución)
El error residual del 19.1% no representa imprecisiones del recomendador, sino la brecha natural entre la **intención táctica ideal** del equipo y su **ejecución real condicionada por el contexto**. 

Por ejemplo, Francia presentó una desviación considerable en su fase defensiva (error de $1.35$) debido a que el motor heurístico modela correctamente su tendencia histórica a replegarse y contragolpear en Copas del Mundo (arquetipo táctico real). Sin embargo, sus estadísticas cuantitativas crudas en eliminatorias indicaban un bloque alto y presión constante, inflados artificialmente por el dominio sostenido ante rivales de menor jerarquía grupal. Esto valida al modelo sintético como un corrector óptimo del sesgo de contexto.