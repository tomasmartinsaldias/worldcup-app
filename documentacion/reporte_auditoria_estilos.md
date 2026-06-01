# Reporte de Auditoría de Estilo de Juego (Alineado por Contexto)

Auditoría de los vectores de estilo generados por IA frente a las estadísticas reales de Sofascore normalizadas mediante el Coeficiente de Dificultad ($C_{dif}$) para 7 países.

## Fórmulas y Composición con Normalización de Calendario

- **Posesión (`posesion`)**: `% de Posesión` con penalización de `-0.2 * Centros Largos` multiplicada por $C_{dif}$.
- **Defensa (`defensa`)**: `20% Relación de Pases Campo Rival/Propio` * $C_{dif}$ + `30% Despejes / Cdif (Invertido)` + `50% Tackles / Cdif (Invertido)`.
- **Ritmo (`ritmo`)**: `33% Tiros Totales` * $C_{dif}$ + `33% Pérdidas de Balón / Cdif` + `34% Contragolpes` * $C_{dif}$.
- **Ancho (`ancho`)**: `80% Centros Intentados` * $C_{dif}$ + `20% Relación de Centros/Pases` * $C_{dif}$.

Todas las componentes fueron normalizadas al rango `[-1, 1]` tras la calibración de dificultad.

## Tabla Comparativa: IA vs Sofascore Real Ajustado

| Selección | Componente | Valor IA | Valor Sofascore (Ajustado) | Error Absoluto |
| --- | --- | --- | --- | --- |
| Alemania | `defensa` | +0.85 | +0.79 | 0.06 |
| Alemania | `posesion` | +0.80 | +1.00 | 0.20 |
| Alemania | `ritmo` | +0.75 | -0.01 | 0.76 |
| Alemania | `ancho` | +0.15 | +0.91 | 0.76 |
| Argentina | `defensa` | +0.50 | +0.30 | 0.20 |
| Argentina | `posesion` | +0.80 | +0.69 | 0.11 |
| Argentina | `ritmo` | -0.30 | -0.46 | 0.16 |
| Argentina | `ancho` | -0.70 | -1.00 | 0.30 |
| España | `defensa` | +0.80 | +0.66 | 0.14 |
| España | `posesion` | +0.85 | +0.60 | 0.25 |
| España | `ritmo` | +0.40 | +0.44 | 0.04 |
| España | `ancho` | +0.90 | +0.50 | 0.40 |
| Francia | `defensa` | -0.35 | +1.00 | 1.35 |
| Francia | `posesion` | -0.15 | +0.63 | 0.78 |
| Francia | `ritmo` | +0.85 | +0.95 | 0.10 |
| Francia | `ancho` | +0.50 | +1.00 | 0.50 |
| Jordania | `defensa` | -0.70 | -1.00 | 0.30 |
| Jordania | `posesion` | -0.60 | -1.00 | 0.40 |
| Jordania | `ritmo` | +0.70 | +0.80 | 0.10 |
| Jordania | `ancho` | +0.40 | +0.25 | 0.15 |
| Panamá | `defensa` | -0.20 | +0.48 | 0.68 |
| Panamá | `posesion` | +0.30 | +0.61 | 0.31 |
| Panamá | `ritmo` | +0.10 | -1.00 | 1.10 |
| Panamá | `ancho` | +0.50 | -0.01 | 0.51 |
| Senegal | `defensa` | +0.10 | -0.12 | 0.22 |
| Senegal | `posesion` | -0.25 | +0.02 | 0.27 |
| Senegal | `ritmo` | +0.55 | +1.00 | 0.45 |
| Senegal | `ancho` | +0.60 | +0.49 | 0.11 |

## Resumen de Errores por Componente

| Componente | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) | Correlación Spearman (ρ) |
| --- | --- | --- | --- |
| `defensa` | 0.4219 | 0.5956 | +0.3571 |
| `posesion` | 0.3319 | 0.3871 | +0.5714 |
| `ritmo` | 0.3880 | 0.5403 | +0.6071 |
| `ancho` | 0.3896 | 0.4414 | +0.2500 |

**Error Medio Global (MAE):** `0.3829`
**Error Cuadrático Medio Global (RMSE):** `0.4978`
**Correlación de Spearman Promedio:** `0.4464`
