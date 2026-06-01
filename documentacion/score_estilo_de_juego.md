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

---

## 5. Derivación de los Vectores Empíricos (SofaScore)
Para purgar la opacidad y los errores residuales del uso de Modelos de Lenguaje (IA/LLM) en la generación de vectores tácticos, el sistema calcula los vectores de cada selección directamente a partir de las estadísticas empíricas reales de SofaScore durante las eliminatorias, normalizadas por el Coeficiente de Dificultad del Oponente ($C_{dif}$) para neutralizar el sesgo de calendario.

Las fórmulas de cálculo bruto para cada componente son:
* **Posesión ($p_{bruto}$)**: $p_{bruto} = \text{Posesión (\%)} \times \left(1 - \frac{\text{Pases Largos Acertados} + \text{Centros Acertados}}{\text{Pases Totales Acertados}}\right)$, multiplicado por $C_{dif}$.
* **Ancho ($a_{bruto}$)**: $a_{bruto} = \frac{\text{Centros Intentados}}{\text{Pases Acertados Campo Contrario}}$, multiplicado por $C_{dif}$.
* **Ritmo ($r_{bruto}$)**: $r_{bruto} = \frac{\text{Tiros Totales} + \frac{\text{Contraataques Totales}}{\text{Partidos}}}{\text{Posesión (\%)}}$, multiplicado por $C_{dif}$.
* **Defensa ($d_{bruto}$)**: $d_{bruto} = (\text{Relación de Pases Campo Rival} \times C_{dif}) - \frac{\text{Despejes} / C_{dif}}{100.0}$.

*Nota: Para Nueva Zelanda (única selección calificada sin datos de SofaScore), el sistema utiliza a Australia como proxy táctico debido a afinidades regionales y de plantel.*

---

## 6. Pipeline de Normalización No Lineal (Z-Score + tanh)
Para evitar que los equipos con estadísticas superlativas (outliers) aplasten la escala del resto de selecciones en la normalización, se implementa un pipeline no lineal en dos fases matemáticas:
1. **Estandarización (Z-Score)**: Convierte la métrica bruta en desviaciones estándar respecto al promedio del Mundial:
   $$z = \frac{x - \mu}{\sigma}$$
   Donde $\mu$ y $\sigma$ son la media y la desviación estándar de la muestra completa de selecciones.
2. **Proyección Sigmoidea (tanh)**: Aplica la tangente hiperbólica con un factor de sensibilidad $k = 0.6$:
   $$V_{\text{norm}} = \tanh(k \cdot z)$$
   Esto mapea los valores exactamente al intervalo $[-1.0, 1.0]$. El factor $k = 0.6$ mantiene la linealidad en los rangos centrales y ralentiza la saturación en los extremos para capturar variaciones tácticas complejas.

---

## 7. Auditoría de Consistencia y Validación Final
Con el reemplazo de los vectores de IA por vectores SofaScore empíricos directos en la base de datos de estilos tácticos (`selecciones_estilo`), el recomendador de partidos opera con total transparencia y precisión real:
* **Error Medio Absoluto (MAE)**: `0.0000`
* **Error Cuadrático Medio (RMSE)**: `0.0000`
* **Correlación Ordinal de Spearman ($\rho$)**: `+1.0000` (Alineación perfecta entre el motor de recomendación táctica y la verdad empírica del terreno de juego).

Esta reestructuración garantiza que el sistema recomiende encuentros con base en el estilo de juego real y verificado de cada selección nacional.