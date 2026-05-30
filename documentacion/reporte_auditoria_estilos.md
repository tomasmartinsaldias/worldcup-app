# Reporte de Auditoría de Estilo de Juego

Auditoría de los vectores de estilo generados por IA frente a las estadísticas reales de Sofascore para 7 países.

## Fórmulas y Composición Utilizadas

- **Posesión (`posesion`)**: `% de Posesión` con penalización de `-0.2 * Centros Largos Completados por partido` (para penalizar juego directo/salteo).
- **Defensa (`defensa`)**: Combinación de `20% Relación de Pases Campo Rival/Propio` + `30% Despejes por partido (Invertido)` + `50% Tackles por partido (Invertido)` (un bloque alto realiza menos intervenciones bajas y mantiene el juego arriba).
- **Ritmo (`ritmo`)**: Combinación de `33% Tiros Totales por partido` + `33% Pérdidas de Balón por partido` + `34% Contragolpes por partido` (refleja verticalidad e inmediatez de finalización).
- **Ancho (`ancho`)**: Combinación de `80% Centros Intentados por partido` + `20% Relación de Centros/Pases Totales` (mide amplitud de bandas y frecuencia de centros).

Todas las componentes fueron normalizadas al rango `[-1, 1]` usando la fórmula:
$$X_{norm} = 2 \times \left(\frac{X - X_{min}}{X_{max} - X_{min}}\right) - 1$$

## Tabla Comparativa: IA vs Sofascore Real

| Selección | Componente | Valor IA | Valor Sofascore (Norm) | Error Absoluto |
| --- | --- | --- | --- | --- |
| Alemania | `defensa` | +0.85 | +0.75 | 0.10 |
| Alemania | `posesion` | +0.80 | +1.00 | 0.20 |
| Alemania | `ritmo` | +0.75 | -0.02 | 0.77 |
| Alemania | `ancho` | +0.15 | +0.86 | 0.71 |
| Argentina | `defensa` | +0.50 | +0.09 | 0.41 |
| Argentina | `posesion` | +0.80 | +0.38 | 0.42 |
| Argentina | `ritmo` | -0.30 | -0.34 | 0.04 |
| Argentina | `ancho` | -0.70 | -1.00 | 0.30 |
| España | `defensa` | +0.80 | +0.77 | 0.03 |
| España | `posesion` | +0.85 | +0.80 | 0.05 |
| España | `ritmo` | +0.40 | +0.36 | 0.04 |
| España | `ancho` | +0.90 | +0.66 | 0.24 |
| Francia | `defensa` | -0.35 | +1.00 | 1.35 |
| Francia | `posesion` | -0.15 | +0.70 | 0.85 |
| Francia | `ritmo` | +0.85 | +0.92 | 0.07 |
| Francia | `ancho` | +0.50 | +1.00 | 0.50 |
| Jordania | `defensa` | -0.70 | -1.00 | 0.30 |
| Jordania | `posesion` | -0.60 | -1.00 | 0.40 |
| Jordania | `ritmo` | +0.70 | +0.97 | 0.27 |
| Jordania | `ancho` | +0.40 | +0.21 | 0.19 |
| Panamá | `defensa` | -0.20 | +0.36 | 0.56 |
| Panamá | `posesion` | +0.30 | +0.45 | 0.15 |
| Panamá | `ritmo` | +0.10 | -1.00 | 1.10 |
| Panamá | `ancho` | +0.50 | -0.09 | 0.59 |
| Senegal | `defensa` | +0.10 | +0.10 | 0.00 |
| Senegal | `posesion` | -0.25 | +0.26 | 0.51 |
| Senegal | `ritmo` | +0.55 | +1.00 | 0.45 |
| Senegal | `ancho` | +0.60 | +0.70 | 0.10 |

## Resumen de Errores por Componente

| Componente | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) |
| --- | --- | --- |
| `defensa` | 0.3917 | 0.5860 |
| `posesion` | 0.3664 | 0.4424 |
| `ritmo` | 0.3912 | 0.5461 |
| `ancho` | 0.3758 | 0.4298 |

**Error Medio Global (MAE):** `0.3813`
**Error Cuadrático Medio Global (RMSE):** `0.5055`
