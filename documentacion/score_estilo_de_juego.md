Metodología e Implementación: Módulo de Similitud Táctica (Estilo de Juego)
1. Documentación Metodológica (Para el Informe PDF)
1.1. Justificación Arquitectónica: Vectores Numéricos vs. Procesamiento de Lenguaje Natural

El diseño inicial del recomendador contemplaba el uso de embeddings generados a partir de descripciones textuales para capturar el estilo de juego de cada selección. Sin embargo, este enfoque fue descartado tras someterlo a validación analítica debido a dos sesgos críticos:

    Opacidad algorítmica (Caja Negra): Los modelos de lenguaje procesan semántica general, no heurística futbolística. Justificar una recomendación basándose en la distancia coseno de vectores latentes de texto impide explicarle al usuario final qué variable táctica generó la similitud.

    Sensibilidad al ruido sintáctico: La similitud matemática dependía de la redacción de los párrafos en lugar de los conceptos subyacentes.

Como solución superadora, se diseñó un Espacio Vectorial Geométrico de 4 Dimensiones. Este modelo convierte la táctica en escalas numéricas continuas [−1.0,1.0], garantizando precisión matemática, trazabilidad absoluta y explicabilidad directa en la interfaz de usuario.
1.2. Definición del Espacio Vectorial Táctico

Cada equipo (y la preferencia del usuario) se representa como un vector V=[d,p,r,a], donde cada dimensión modela un espectro del juego:

    Fase Defensiva (d): Desde −1.0 (Bloque bajo extremo, repliegue en área propia) hasta 1.0 (Presión alta asfixiante).

    Fase de Posesión (p): Desde −1.0 (Juego directo, transiciones largas y contragolpe) hasta 1.0 (Elaboración paciente, Tiki-taka).

    Ritmo de Juego (r): Desde −1.0 (Control pausado, circulación horizontal) hasta 1.0 (Frenético, verticalidad constante).

    Uso del Ancho (a): Desde −1.0 (Juego interior, embudo por el pasillo central) hasta 1.0 (Ataque exclusivo por bandas, extremos puros).

1.3. Lógica de Agregación: Heurística del "Protagonista"

En un partido interactúan dos equipos con estilos frecuentemente antagónicos. Si el sistema promediara la similitud de ambos equipos respecto a la preferencia del usuario, los choques de estilos divergentes serían penalizados (ej. un equipo de posesión vs. un equipo de bloque bajo daría una similitud media).

Para evitar esto, la arquitectura utiliza una función máxima (max), garantizando que si al menos uno de los equipos ejecuta el arquetipo deseado, el partido obtenga un puntaje alto. La ecuación base de afinidad se define como:
Score_Estilo(A,B,U)=max(Sim(A,U),Sim(B,U))+λ×min(Sim(A,U),Sim(B,U))

Donde:

    A,B: Vectores tácticos de los equipos.

    U: Vector de preferencia del usuario.

    Sim: Función de similitud (ej. Similitud Coseno o Distancia Euclidiana Invertida).

    λ: Coeficiente condicional de interacción. Premia o castiga la simetría táctica (ej. un valor positivo si el usuario busca partidos rotos de alto ritmo y ambos equipos lo proponen; un valor negativo si ambos proponen un bloque bajo especulativo).

"La imputación de variables tácticas se fundamenta en la literatura reciente sobre el uso de Modelos de Lenguaje Grande (LLMs) como evaluadores analíticos en entornos 'zero-shot'. Como demuestran Chowdhury y Caragea (2025), es metodológicamente viable utilizar un LLM mediante prompting estructurado (ej. forzando la descomposición de pensamientos) para evaluar lógicas complejas y extraer de dichas evaluaciones un puntaje escalar continuo (scalar score) que guíe el cálculo algorítmico posterior. En nuestro caso, la extracción de este puntaje continuo se optimiza forzando tipados de punto flotante en el output (JSON Constraining), permitiendo mapear la inferencia táctica cualitativa del modelo directamente sobre el espacio vectorial [-1.0, 1.0]."

2. Implementación Técnica (Para el Repositorio de Código)
2.1. Ingesta de Datos: Inferencia Restringida mediante LLM

Dado que las métricas avanzadas no están disponibles para todas las confederaciones, se utiliza un LLM como motor de inferencia analítica para poblar la matriz de 48×4. Para suprimir la alucinación estadística, se implementa JSON Constraining y Chain of Thought.

Prompt de Extracción (System Prompt):
Plaintext

Actúa como un analista táctico de fútbol de élite. Tu tarea es mapear el estilo de juego de las selecciones nacionales clasificadas al Mundial 2026 a un vector matemático de 4 dimensiones. 

RESTRICCIONES ESTRICTAS:
- Tienes prohibido inventar información. 
- Si un equipo pertenece a una confederación menor, asume empíricamente su postura táctica habitual cuando enfrenta a potencias (generalmente bloque bajo y contragolpe).

ESPACIO VECTORIAL (Escala -1.0 a 1.0):
1. Fase Defensiva: -1.0 (Bloque bajo extremo) a 1.0 (Presión alta asfixiante).
2. Fase de Posesión: -1.0 (Contragolpe directo, salto de líneas) a 1.0 (Posesión monopólica).
3. Ritmo: -1.0 (Pausado, control horizontal) a 1.0 (Frenético, transiciones rápidas).
4. Ancho: -1.0 (Juego interiorizado) a 1.0 (Ataque exclusivo por bandas).

Debes devolver ÚNICAMENTE un objeto JSON válido con la siguiente estructura exacta:
{
  "equipo": "Nombre del Equipo",
  "analisis_tactico": "Justificación de 2 líneas fundamentando por qué se eligen los valores.",
  "vector": {
    "defensa": 0.0,
    "posesion": 0.0,
    "ritmo": 0.0,
    "ancho": 0.0
  }
}

2.2. Cálculo de Similitud en Backend

Para medir la afinidad, se recomienda normalizar los vectores y utilizar Similitud Coseno espacial en Python.
Python

from scipy.spatial.distance import cosine

def calcular_similitud_estilo(vector_usuario, vector_equipo):
    # La similitud coseno en scipy devuelve la distancia (0 a 2). 
    # Para convertirla a similitud (1 a -1), se resta de 1.
    return 1 - cosine(vector_usuario, vector_equipo)

def score_estilo_partido(vector_a, vector_b, vector_u, lambda_val=0.1):
    sim_a = calcular_similitud_estilo(vector_u, vector_a)
    sim_b = calcular_similitud_estilo(vector_u, vector_b)
    
    match_principal = max(sim_a, sim_b)
    interaccion = min(sim_a, sim_b) * lambda_val
    
    return match_principal + interaccion

2.3. Arquitectura del Frontend (Demo Interactiva)

Para cumplir con el criterio de evaluación de "experiencia clara e intuitiva independientemente del perfil técnico", la configuración del vector del usuario U se bifurca en dos niveles de profundidad:

    Modo Casual (Presets): Tarjetas seleccionables con arquetipos históricos que inyectan vectores estáticos hardcodeados en el backend.

        Ejemplo: Botón "Tiki-Taka" inyecta [0.6, 0.9, -0.4, 0.5].

        Ejemplo: Botón "Catenaccio y Contraataque" inyecta [-0.9, -0.8, 0.5, 0.0].

    Modo Analista (Sliders): Interfaz de 4 controles deslizables para que el usuario determine el valor numérico exacto (oculto tras lenguaje natural).

        Ejemplo de UI: "¿Dónde prefieres recuperar el balón?" [Área Propia <---> Área Rival].