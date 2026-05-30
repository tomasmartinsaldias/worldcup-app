Plan de Implementación: Score de Espectáculo Ajustado por Oponente

La decisión de avanzar con la recolección empírica total exige un pipeline de datos estrictamente procedimental para evitar que la asimetría de los torneos contamine el recomendador. Al mantener los datos crudos de Nueva Zelanda, la penalización matemática sobre la OFC debe ser exacta para evitar falsos positivos.

Aquí tenés el diagrama de arquitectura para implementar la variable espectaculo_base antes de escribir el código del frontend/backend:
Fase 1: Extracción Estructurada de Oponentes

    Paso 1: Extracción y Limpieza (La Trampa de las Unidades)

De la sábana de Sofascore, las métricas que nos interesan para el espectáculo son:

    Matches (Partidos): 6   

    Big chances per game (Ocasiones claras): 4.2   

    Counter attacks (Contraataques): 6   

    Fouls per game (Faltas): 12   

El diagnóstico del error: Big chances y Fouls son promedios por partido, pero Counter attacks (6) es el total acumulado del torneo. Si sumás un promedio a un total (4.2+6), estás contaminando el vector. Debés homogeneizar todo a "Por Partido" (PG).

    Contraataques_PG=66​=1.0

Paso 2: Cálculo del ICE Bruto (Sraw​)

Ahora que las unidades son consistentes, aplicamos la ecuación base. Para evitar que las faltas arrojen puntajes negativos que destruyan la escala, el factor de penalización debe ser proporcional (por ejemplo, ponderando las faltas a un 20% de su valor nominal).

La ecuación algorítmica:
ICEp​=OC+(α×CA)+(β×Drama)
El beta del drama queda ajustable por el usuario en la interfaz, seguramente mediante una pregunta de si le gustan los aprtidos con roce o es fair play.
Paso 3: Aplicación del Coeficiente de Dificultad (Cdif​)
Cdif​=1−(211/Rmed​​)
Utilizamos la mediana de sus rivales en la copa que jugó. Esos datos estan en international-results/results.
Al score bruto se li multiplica por este coeficiente

Paso 4: Normalización Final

Se normaliza cada componente con un min max scaling.

Fase 3: Caso Nueva Zelanda​.

    Tratamiento de Nueva Zelanda (OFC): Se utilizan sus datos de la eliminatoria oceánica (altamente inflados por el dominio regional), no los datos de SOFASCORE que son más granulares. Al aplicar el Cdif​ derivado de rivales como Tahití o Islas Salomón (rankings muy bajos), el coeficiente aplastará matemáticamente el dato crudo. Esto es algebraicamente correcto y previene que el sistema la clasifique erróneamente como una selección de alto espectáculo a nivel mundial.

Fase 4: Normalización e Inyección

    La salida del JSON quedaría:
    {
  "id": "alemania",
  "tactica": {
    "defensa": 0.85,
    "posesion": 0.80,
    "ritmo": 0.75,
    "ancho": 0.15
  },
  "espectaculo_params": {
    "ocasiones_norm": 0.82,
    "contra_norm": 0.30,
    "drama_norm": 0.45
  }
}