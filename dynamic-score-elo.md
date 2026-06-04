# Plan de Implementación: Simulador Dinámico de Posiciones, ELO y Stake Multiplier (Revisado)

Este plan describe la arquitectura y los cambios necesarios para hacer que la aplicación sea dinámica y reactiva a los resultados del mundial simulados por el usuario en tiempo real en el cliente.

## User Review Required

> [!IMPORTANT]
> **Separación de la Landing Page 3D y la Aplicación Principal:**
> La landing page en `index.html` se mantendrá intacta en cuanto a su diseño visual y lógica de orbes y copa.
> Crearemos **`frontend/app.html`** copiando el código de `old_index.html` para que sirva como la aplicación del recomendador aislada.
> Al finalizar el flujo de onboarding (Casual/Fanático) en `index.html`, redireccionaremos al usuario a `app.html` mediante `window.location.href = 'app.html'`.

> [!WARNING]
> **Simulación Dinámica de Clasificación en el Grupo:**
> Para determinar si un equipo está clasificado, eliminado o en la pelea, simularemos exhaustivamente los posibles escenarios restantes de su grupo (máximo 6 partidos por grupo en fase de grupos = $3^6 = 729$ combinaciones). Esto se ejecutará instantáneamente en el cliente, permitiendo clasificaciones exactas sin depender de servidores.

---

## Proposed Changes

### 1. Integración de la Redirección y Nuevo App File

#### [NEW] [app.html](file:///c:/Users/tomas/Desktop/proyectos/worldcup-app/frontend/app.html)
- Copiar `old_index.html` a `app.html` como la aplicación del recomendador principal.
- Modificar el menú de navegación (`nav-links`) en `app.html` para incluir un botón para la nueva pestaña:
  ```html
  <button class="nav-btn" data-tab="results">
    <i class="fa-solid fa-square-poll-horizontal"></i> Resultados
  </button>
  ```
- Insertar la sección del panel de resultados en `<main class="app-container">`:
  ```html
  <section id="tab-results" class="tab-panel">
    <!-- Contenido inyectado dinámicamente por results.js -->
  </section>
  ```

#### [MODIFY] [index.html](file:///c:/Users/tomas/Desktop/proyectos/worldcup-app/frontend/index.html)
- Modificar `finishGenericQuiz()` y `finishDraftTemplate()` en los scripts de `index.html` para redirigir al usuario:
  `window.location.href = 'app.html';`
- Agregar un enlace de redirección a `app.html` si el usuario selecciona "Intermedio" en la landing page.

### 2. Estado y Lógica del Torneo

#### [MODIFY] [state.js](file:///c:/Users/tomas/Desktop/proyectos/worldcup-app/frontend/js/state.js)
- Agregar un objeto `simulatedScores` para guardar las puntuaciones de partidos editadas por el usuario (ej: `{ match_number: { home: 2, away: 1 } }`).
- Implementar la función `calculateStandings(groupLetter)`:
  - Lee los partidos del grupo de `wc2026_data.json` y aplica los marcadores de `simulatedScores`.
  - Calcula puntos, diferencia de gol (DG) y goles a favor (GF).
- Implementar la función `determineQualificationStatus()`:
  - Corre una simulación recursiva rápida de todos los resultados restantes en cada grupo ($3^{\text{partidos restantes}}$).
  - Determina si un equipo siempre clasifica en el top 2 (`QUALIFIED`), siempre clasifica 1° (`FIRST_PLACE_ASSURED`), nunca clasifica (`ELIMINATED`), o varía según resultados (`PLAYING_FOR_LIFE`).
- Implementar `recalculateEloAndMomentum()`:
  - Inicializa los ELOs y momentums a partir de los datos base de los equipos.
  - Recorre los partidos en orden cronológico.
  - Si un partido tiene resultado simulado, calcula la expectativa $W_e$, el error de predicción $E = W - W_e$, actualiza el momentum $M_t = \alpha \cdot E_t + (1 - \alpha) \cdot M_{t-1}$, actualiza el ELO con $K_{dinámico} = K_{base} \cdot \Omega_{fase} \cdot (1 + \lambda \cdot |M_t|)$, y propaga los nuevos ELOs a los siguientes partidos.

### 3. Algoritmo de Recomendación

#### [MODIFY] [scoring.js](file:///c:/Users/tomas/Desktop/proyectos/worldcup-app/frontend/js/scoring.js)
- Modificar `calculateICEScore` para usar el ELO dinámico/actualizado de la simulación en lugar del estático del JSON.
- Aplicar el multiplicador de stakes del partido al Score Espectáculo final:
  - $M_{\text{match}} = (M_{\text{home}} + M_{\text{away}}) / 2$
  - Multiplicadores individuales: `PLAYING_FOR_LIFE` (1.0), `QUALIFIED` (0.85), `FIRST_PLACE_ASSURED` (0.7), `ELIMINATED` (0.6).
  - Para partidos de eliminación directa (knockout), ambos equipos se consideran en `PLAYING_FOR_LIFE` (1.0).

### 4. Interfaz de Usuario y Componentes

#### [NEW] [results.js](file:///c:/Users/tomas/Desktop/proyectos/worldcup-app/frontend/js/ui/results.js)
- Crear el componente de renderizado de la nueva pestaña **Resultados**.
- Mostrar la lista de partidos de fase de grupos y fases eliminatorias.
- Agregar campos de entrada de goles (`input type="number"`) elegantes para cada partido, que actualicen el estado en vivo al cambiar.
- Agregar una barra de control superior con botones para:
  - "Simular partidos restantes al azar" (usando el ELO dinámico para dar pesos de victoria).
  - "Reiniciar simulador" para borrar todos los goles cargados.
- Mostrar debajo de cada equipo su ELO actual y el estado de clasificación en vivo mediante insignias premium y luminosas.

#### [MODIFY] [groups.js](file:///c:/Users/tomas/Desktop/proyectos/worldcup-app/frontend/js/ui/groups.js)
- Modificar la pestaña **Grupos** para mostrar una tabla de posiciones real y dinámica (Pos, PJ, PG, PE, PP, GF, GC, DG, Pts) en lugar de una lista estática de nombres.
- Resaltar visualmente las filas de los equipos según su estado (brillo verde para clasificados, rojo tenue para eliminados, etc.).

#### [MODIFY] [main.js](file:///c:/Users/tomas/Desktop/proyectos/worldcup-app/frontend/js/main.js)
- Importar `renderResults` e integrar la pestaña de resultados en la navegación.
- Asegurar que al actualizar cualquier marcador se dispare una cadena de recalculación y re-renderizado de todas las vistas (Matches, Groups, Results).

### 5. Documentación

#### [MODIFY] [score_espectaculo.md](file:///c:/Users/tomas/Desktop/proyectos/worldcup-app/documentacion/score_espectaculo.md)
- Actualizar para documentar el factor dinámico de clasificación en el cálculo del score de espectáculo.

#### [MODIFY] [calculo_elo_historico.md](file:///c:/Users/tomas/Desktop/proyectos/worldcup-app/documentacion/calculo_elo_historico.md)
- Documentar el modelo de actualización dinámica de ELO a través de la fórmula EMA y el error de predicción en el transcurso de la copa.

---

## Verification Plan

### Manual Verification
- Levantar servidor web e ingresar a `app.html` o a `index.html` y completar la landing.
- Cargar resultados en la pestaña resultados y verificar la correcta recalculación del ELO, el orden del recomendador por Score Espectáculo y las posiciones dinámicas del grupo.
- Probar simulación aleatoria de la fase de grupos.
