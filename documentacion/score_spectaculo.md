Metodología: Índice de Competitividad y Espectáculo (ICE)

1. Justificación Analítica
El atractivo de un encuentro no se reduce a la suma bruta de goles, sino que es una propiedad emergente de la interacción táctica y técnica entre dos equipos. Para modelar el "espectáculo" de manera empírica y mitigar el sesgo de calidad histórica entre diferentes confederaciones, se diseñó el Índice de Competitividad y Espectáculo (ICE).

Este modelo abandona las métricas de goles absolutos para aislar la verdadera capacidad de generación de peligro (excluyendo penales), incorporar la vulnerabilidad defensiva (fomentando la detección de partidos "rotos" o de ida y vuelta) y cuantificar la fricción o tensión narrativa del juego. Finalmente, el volumen nominal resultante es ajustado por la paridad jerárquica de los contendientes.

2. Definición Matemática
El modelo se compone de dos cálculos. En primera instancia, se define el Volumen de Espectáculo Individual (V) para cada equipo, normalizado a valores por 90 minutos:
V=(Gnp​)+(α×Gc​)+(β×Drama)

Donde:

    Gnp​: Goles a favor sin contabilizar penales (Non-Penalty Goals).

    Gc​: Goles en contra. Se pondera con un factor de reducción α (por ejemplo, 0.5) para sumar valor a los partidos de áreas abiertas, evitando que el modelo premie de forma desproporcionada a los equipos netamente goleados.

    Drama: Componente de tensión del partido que agrupa faltas severas y situaciones de área penal (calculado empíricamente como suma de tarjetas y penales sancionados). Se modera mediante un factor β (por ejemplo, 0.2) para que aporte peso cualitativo sin dominar a la métrica estricta de juego.

En segunda instancia, se proyecta el atractivo del cruce directo evaluando la función final ICE:
ICE(A,B)=(VA​+VB​​)/(1+ln(∣RA​−RB​∣+1))

Donde:

    VA​,VB​: Volumen de espectáculo calculado para los equipos A y B.

    RA​,RB​: Posición actual en el Ranking FIFA de los equipos A y B.

3. Comportamiento del Modelo (Tratamiento de Sesgos y Ruido)

    Filtrado de Ruido Estático: Al reemplazar los goles totales por Gnp​, el modelo castiga estadísticamente a los equipos que inflan sus promedios ofensivos mediante penales, priorizando la creación de juego en movimiento.

    Recompensa de Fragilidad: La inclusión del factor Gc​ en el numerador asegura que un equipo que gana promediando marcadores de 4-2 obtenga un volumen de espectáculo superior a uno que gana sistemáticamente 2-0.

    Penalización por Asimetría: El denominador con transformación logarítmica actúa como un regulador estructural contra el sesgo de confederación. Si los equipos presentan un volumen ofensivo nominalmente alto por provenir de eliminatorias con oposición de bajo nivel (resultando en rankings >80), un eventual cruce mundialista contra una potencia (ranking <10) disparará el valor del denominador. Esto comprime el puntaje final ICE, reclasificando correctamente el partido como un evento de tensión competitiva nula ("Para ver el resumen").