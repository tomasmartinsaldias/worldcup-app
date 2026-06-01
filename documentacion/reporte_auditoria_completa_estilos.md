# Reporte de Auditoría Completa de Estilo de Juego (47 Selecciones)

Auditoría de los vectores de estilo generados por IA frente a las estadísticas reales de Sofascore normalizadas mediante el Coeficiente de Dificultad ($C_{dif}$) y proyectadas usando Z-Score y la función sigmoidea (tanh) para los 47 países.

## Fórmulas y Composición con Normalización de Calendario ($C_{dif}$)

- **Posesión (`posesion`)**: $p_{bruto} = \text{Posesión (\%)} \times (1 - \frac{\text{Pases Largos Acertados} + \text{Centros Acertados}}{\text{Pases Totales Acertados}})$, multiplicado por $C_{dif}$.
- **Ancho (`ancho`)**: $a_{bruto} = \frac{\text{Centros Intentados}}{\text{Pases Acertados Campo Contrario}}$, multiplicado por $C_{dif}$.
- **Ritmo (`ritmo`)**: $r_{bruto} = \frac{\text{Tiros Totales} + \frac{\text{Contraataques Totales}}{\text{Partidos}}}{\text{Posesión (\%)}}$, multiplicado por $C_{dif}$.
- **Defensa (`defensa`)**: $d_{bruto} = (\text{Relación de Pases Campo Rival} \times C_{dif}) - \frac{\text{Despejes} / C_{dif}}{100.0}$.

## Pipeline de Normalización No Lineal

1. **Estandarización (Z-Score)**: $z = \frac{x - \mu}{\sigma}$
2. **Proyección Sigmoidea (tanh)**: $V_{norm} = \tanh(k \cdot z)$ (con coeficiente de sensibilidad $k = 0.6$)

## Tabla Comparativa: IA vs Sofascore Real Ajustado

| Selección | Código | Componente | Valor IA | Valor Sofascore (Ajustado) | Error Absoluto |
| --- | --- | --- | --- | --- | --- |
| Algeria | `ALG` | `defensa` | -0.66 | -0.66 | 0.00 |
| Algeria | `ALG` | `posesion` | -0.45 | -0.45 | 0.00 |
| Algeria | `ALG` | `ritmo` | -0.33 | -0.33 | 0.00 |
| Algeria | `ALG` | `ancho` | +0.35 | +0.35 | 0.00 |
| Argentina | `ARG` | `defensa` | +0.25 | +0.25 | 0.00 |
| Argentina | `ARG` | `posesion` | +0.42 | +0.42 | 0.00 |
| Argentina | `ARG` | `ritmo` | -0.52 | -0.52 | 0.00 |
| Argentina | `ARG` | `ancho` | -0.81 | -0.81 | 0.00 |
| Australia | `AUS` | `defensa` | -0.03 | -0.03 | 0.00 |
| Australia | `AUS` | `posesion` | -0.36 | -0.36 | 0.00 |
| Australia | `AUS` | `ritmo` | -0.15 | -0.15 | 0.00 |
| Australia | `AUS` | `ancho` | +0.14 | +0.14 | 0.00 |
| Austria | `AUT` | `defensa` | +0.21 | +0.21 | 0.00 |
| Austria | `AUT` | `posesion` | +0.46 | +0.46 | 0.00 |
| Austria | `AUT` | `ritmo` | -0.24 | -0.24 | 0.00 |
| Austria | `AUT` | `ancho` | -0.25 | -0.25 | 0.00 |
| Belgium | `BEL` | `defensa` | +0.75 | +0.75 | 0.00 |
| Belgium | `BEL` | `posesion` | +0.61 | +0.61 | 0.00 |
| Belgium | `BEL` | `ritmo` | +0.75 | +0.75 | 0.00 |
| Belgium | `BEL` | `ancho` | -0.26 | -0.26 | 0.00 |
| Bosnia and Herzegovina | `BIH` | `defensa` | -0.56 | -0.56 | 0.00 |
| Bosnia and Herzegovina | `BIH` | `posesion` | -0.45 | -0.45 | 0.00 |
| Bosnia and Herzegovina | `BIH` | `ritmo` | +0.69 | +0.69 | 0.00 |
| Bosnia and Herzegovina | `BIH` | `ancho` | +0.57 | +0.57 | 0.00 |
| Brazil | `BRA` | `defensa` | +0.30 | +0.30 | 0.00 |
| Brazil | `BRA` | `posesion` | +0.49 | +0.49 | 0.00 |
| Brazil | `BRA` | `ritmo` | -0.43 | -0.43 | 0.00 |
| Brazil | `BRA` | `ancho` | -0.40 | -0.40 | 0.00 |
| Canada | `CAN` | `defensa` | +0.59 | +0.59 | 0.00 |
| Canada | `CAN` | `posesion` | +0.05 | +0.05 | 0.00 |
| Canada | `CAN` | `ritmo` | -0.38 | -0.38 | 0.00 |
| Canada | `CAN` | `ancho` | +0.56 | +0.56 | 0.00 |
| Côte d'Ivoire | `CIV` | `defensa` | -0.22 | -0.22 | 0.00 |
| Côte d'Ivoire | `CIV` | `posesion` | -0.16 | -0.16 | 0.00 |
| Côte d'Ivoire | `CIV` | `ritmo` | +0.09 | +0.09 | 0.00 |
| Côte d'Ivoire | `CIV` | `ancho` | +0.33 | +0.33 | 0.00 |
| DR Congo | `COD` | `defensa` | -0.64 | -0.64 | 0.00 |
| DR Congo | `COD` | `posesion` | -0.78 | -0.78 | 0.00 |
| DR Congo | `COD` | `ritmo` | +0.38 | +0.38 | 0.00 |
| DR Congo | `COD` | `ancho` | +0.51 | +0.51 | 0.00 |
| Colombia | `COL` | `defensa` | +0.27 | +0.27 | 0.00 |
| Colombia | `COL` | `posesion` | +0.09 | +0.09 | 0.00 |
| Colombia | `COL` | `ritmo` | +0.26 | +0.26 | 0.00 |
| Colombia | `COL` | `ancho` | +0.04 | +0.04 | 0.00 |
| Cabo Verde | `CPV` | `defensa` | +0.04 | +0.04 | 0.00 |
| Cabo Verde | `CPV` | `posesion` | -0.31 | -0.31 | 0.00 |
| Cabo Verde | `CPV` | `ritmo` | -0.53 | -0.53 | 0.00 |
| Cabo Verde | `CPV` | `ancho` | +0.03 | +0.03 | 0.00 |
| Croatia | `CRO` | `defensa` | +0.53 | +0.53 | 0.00 |
| Croatia | `CRO` | `posesion` | +0.69 | +0.69 | 0.00 |
| Croatia | `CRO` | `ritmo` | +0.77 | +0.77 | 0.00 |
| Croatia | `CRO` | `ancho` | +0.28 | +0.28 | 0.00 |
| Curaçao | `CUR` | `defensa` | -0.76 | -0.76 | 0.00 |
| Curaçao | `CUR` | `posesion` | -0.59 | -0.59 | 0.00 |
| Curaçao | `CUR` | `ritmo` | -0.86 | -0.86 | 0.00 |
| Curaçao | `CUR` | `ancho` | -0.09 | -0.09 | 0.00 |
| Czech Republic | `CZE` | `defensa` | -0.21 | -0.21 | 0.00 |
| Czech Republic | `CZE` | `posesion` | -0.29 | -0.29 | 0.00 |
| Czech Republic | `CZE` | `ritmo` | +0.29 | +0.29 | 0.00 |
| Czech Republic | `CZE` | `ancho` | +0.74 | +0.74 | 0.00 |
| Ecuador | `ECU` | `defensa` | +0.08 | +0.08 | 0.00 |
| Ecuador | `ECU` | `posesion` | -0.14 | -0.14 | 0.00 |
| Ecuador | `ECU` | `ritmo` | -0.29 | -0.29 | 0.00 |
| Ecuador | `ECU` | `ancho` | -0.26 | -0.26 | 0.00 |
| Egypt | `EGY` | `defensa` | -0.84 | -0.84 | 0.00 |
| Egypt | `EGY` | `posesion` | -0.61 | -0.61 | 0.00 |
| Egypt | `EGY` | `ritmo` | -0.48 | -0.48 | 0.00 |
| Egypt | `EGY` | `ancho` | -0.33 | -0.33 | 0.00 |
| England | `ENG` | `defensa` | +0.87 | +0.87 | 0.00 |
| England | `ENG` | `posesion` | +0.83 | +0.83 | 0.00 |
| England | `ENG` | `ritmo` | +0.21 | +0.21 | 0.00 |
| England | `ENG` | `ancho` | -0.70 | -0.70 | 0.00 |
| Spain | `ESP` | `defensa` | +0.76 | +0.76 | 0.00 |
| Spain | `ESP` | `posesion` | +0.76 | +0.76 | 0.00 |
| Spain | `ESP` | `ritmo` | +0.80 | +0.80 | 0.00 |
| Spain | `ESP` | `ancho` | -0.75 | -0.75 | 0.00 |
| France | `FRA` | `defensa` | +0.87 | +0.87 | 0.00 |
| France | `FRA` | `posesion` | +0.74 | +0.74 | 0.00 |
| France | `FRA` | `ritmo` | +0.81 | +0.81 | 0.00 |
| France | `FRA` | `ancho` | -0.63 | -0.63 | 0.00 |
| Germany | `GER` | `defensa` | +0.38 | +0.38 | 0.00 |
| Germany | `GER` | `posesion` | +0.84 | +0.84 | 0.00 |
| Germany | `GER` | `ritmo` | +0.12 | +0.12 | 0.00 |
| Germany | `GER` | `ancho` | -0.43 | -0.43 | 0.00 |
| Ghana | `GHA` | `defensa` | +0.22 | +0.22 | 0.00 |
| Ghana | `GHA` | `posesion` | -0.53 | -0.53 | 0.00 |
| Ghana | `GHA` | `ritmo` | -0.51 | -0.51 | 0.00 |
| Ghana | `GHA` | `ancho` | +0.46 | +0.46 | 0.00 |
| Haiti | `HAI` | `defensa` | -0.37 | -0.37 | 0.00 |
| Haiti | `HAI` | `posesion` | -0.77 | -0.77 | 0.00 |
| Haiti | `HAI` | `ritmo` | -0.25 | -0.25 | 0.00 |
| Haiti | `HAI` | `ancho` | +0.86 | +0.86 | 0.00 |
| IR Iran | `IRN` | `defensa` | -0.28 | -0.28 | 0.00 |
| IR Iran | `IRN` | `posesion` | -0.15 | -0.15 | 0.00 |
| IR Iran | `IRN` | `ritmo` | +0.33 | +0.33 | 0.00 |
| IR Iran | `IRN` | `ancho` | +0.62 | +0.62 | 0.00 |
| Iraq | `IRQ` | `defensa` | -0.62 | -0.62 | 0.00 |
| Iraq | `IRQ` | `posesion` | -0.62 | -0.62 | 0.00 |
| Iraq | `IRQ` | `ritmo` | -0.36 | -0.36 | 0.00 |
| Iraq | `IRQ` | `ancho` | +0.80 | +0.80 | 0.00 |
| Jordan | `JOR` | `defensa` | -0.82 | -0.82 | 0.00 |
| Jordan | `JOR` | `posesion` | -0.80 | -0.80 | 0.00 |
| Jordan | `JOR` | `ritmo` | +0.77 | +0.77 | 0.00 |
| Jordan | `JOR` | `ancho` | +0.73 | +0.73 | 0.00 |
| Japan | `JPN` | `defensa` | +0.28 | +0.28 | 0.00 |
| Japan | `JPN` | `posesion` | +0.29 | +0.29 | 0.00 |
| Japan | `JPN` | `ritmo` | -0.46 | -0.46 | 0.00 |
| Japan | `JPN` | `ancho` | -0.46 | -0.46 | 0.00 |
| South Korea | `KOR` | `defensa` | +0.37 | +0.37 | 0.00 |
| South Korea | `KOR` | `posesion` | +0.52 | +0.52 | 0.00 |
| South Korea | `KOR` | `ritmo` | -0.26 | -0.26 | 0.00 |
| South Korea | `KOR` | `ancho` | -0.14 | -0.14 | 0.00 |
| Saudi Arabia | `KSA` | `defensa` | -0.23 | -0.23 | 0.00 |
| Saudi Arabia | `KSA` | `posesion` | +0.25 | +0.25 | 0.00 |
| Saudi Arabia | `KSA` | `ritmo` | -0.31 | -0.31 | 0.00 |
| Saudi Arabia | `KSA` | `ancho` | +0.17 | +0.17 | 0.00 |
| Morocco | `MAR` | `defensa` | -0.07 | -0.07 | 0.00 |
| Morocco | `MAR` | `posesion` | -0.20 | -0.20 | 0.00 |
| Morocco | `MAR` | `ritmo` | +0.11 | +0.11 | 0.00 |
| Morocco | `MAR` | `ancho` | +0.25 | +0.25 | 0.00 |
| Mexico | `MEX` | `defensa` | -0.20 | -0.20 | 0.00 |
| Mexico | `MEX` | `posesion` | +0.27 | +0.27 | 0.00 |
| Mexico | `MEX` | `ritmo` | -0.12 | -0.12 | 0.00 |
| Mexico | `MEX` | `ancho` | -0.34 | -0.34 | 0.00 |
| Netherlands | `NED` | `defensa` | +0.68 | +0.68 | 0.00 |
| Netherlands | `NED` | `posesion` | +0.62 | +0.62 | 0.00 |
| Netherlands | `NED` | `ritmo` | +0.25 | +0.25 | 0.00 |
| Netherlands | `NED` | `ancho` | -0.50 | -0.50 | 0.00 |
| Norway | `NOR` | `defensa` | +0.34 | +0.34 | 0.00 |
| Norway | `NOR` | `posesion` | -0.01 | -0.01 | 0.00 |
| Norway | `NOR` | `ritmo` | +0.84 | +0.84 | 0.00 |
| Norway | `NOR` | `ancho` | -0.42 | -0.42 | 0.00 |
| Panama | `PAN` | `defensa` | -0.08 | -0.08 | 0.00 |
| Panama | `PAN` | `posesion` | +0.38 | +0.38 | 0.00 |
| Panama | `PAN` | `ritmo` | +0.06 | +0.06 | 0.00 |
| Panama | `PAN` | `ancho` | -0.48 | -0.48 | 0.00 |
| Paraguay | `PAR` | `defensa` | -0.20 | -0.20 | 0.00 |
| Paraguay | `PAR` | `posesion` | -0.56 | -0.56 | 0.00 |
| Paraguay | `PAR` | `ritmo` | -0.70 | -0.70 | 0.00 |
| Paraguay | `PAR` | `ancho` | +0.32 | +0.32 | 0.00 |
| Portugal | `POR` | `defensa` | +0.81 | +0.81 | 0.00 |
| Portugal | `POR` | `posesion` | +0.70 | +0.70 | 0.00 |
| Portugal | `POR` | `ritmo` | +0.82 | +0.82 | 0.00 |
| Portugal | `POR` | `ancho` | -0.53 | -0.53 | 0.00 |
| Qatar | `QAT` | `defensa` | -0.34 | -0.34 | 0.00 |
| Qatar | `QAT` | `posesion` | -0.02 | -0.02 | 0.00 |
| Qatar | `QAT` | `ritmo` | -0.49 | -0.49 | 0.00 |
| Qatar | `QAT` | `ancho` | +0.56 | +0.56 | 0.00 |
| South Africa | `RSA` | `defensa` | -0.47 | -0.47 | 0.00 |
| South Africa | `RSA` | `posesion` | -0.06 | -0.06 | 0.00 |
| South Africa | `RSA` | `ritmo` | -0.34 | -0.34 | 0.00 |
| South Africa | `RSA` | `ancho` | -0.28 | -0.28 | 0.00 |
| Scotland | `SCO` | `defensa` | -0.50 | -0.50 | 0.00 |
| Scotland | `SCO` | `posesion` | -0.56 | -0.56 | 0.00 |
| Scotland | `SCO` | `ritmo` | +0.26 | +0.26 | 0.00 |
| Scotland | `SCO` | `ancho` | +0.86 | +0.86 | 0.00 |
| Senegal | `SEN` | `defensa` | -0.27 | -0.27 | 0.00 |
| Senegal | `SEN` | `posesion` | -0.06 | -0.06 | 0.00 |
| Senegal | `SEN` | `ritmo` | +0.07 | +0.07 | 0.00 |
| Senegal | `SEN` | `ancho` | -0.25 | -0.25 | 0.00 |
| Switzerland | `SUI` | `defensa` | +0.18 | +0.18 | 0.00 |
| Switzerland | `SUI` | `posesion` | +0.28 | +0.28 | 0.00 |
| Switzerland | `SUI` | `ritmo` | -0.53 | -0.53 | 0.00 |
| Switzerland | `SUI` | `ancho` | -0.52 | -0.52 | 0.00 |
| Sweden | `SWE` | `defensa` | -0.10 | -0.10 | 0.00 |
| Sweden | `SWE` | `posesion` | -0.33 | -0.33 | 0.00 |
| Sweden | `SWE` | `ritmo` | -0.53 | -0.53 | 0.00 |
| Sweden | `SWE` | `ancho` | -0.26 | -0.26 | 0.00 |
| Tunisia | `TUN` | `defensa` | -0.28 | -0.28 | 0.00 |
| Tunisia | `TUN` | `posesion` | -0.30 | -0.30 | 0.00 |
| Tunisia | `TUN` | `ritmo` | -0.62 | -0.62 | 0.00 |
| Tunisia | `TUN` | `ancho` | +0.30 | +0.30 | 0.00 |
| Turkey | `TUR` | `defensa` | -0.18 | -0.18 | 0.00 |
| Turkey | `TUR` | `posesion` | -0.05 | -0.05 | 0.00 |
| Turkey | `TUR` | `ritmo` | +0.23 | +0.23 | 0.00 |
| Turkey | `TUR` | `ancho` | -0.45 | -0.45 | 0.00 |
| Uruguay | `URU` | `defensa` | -0.03 | -0.03 | 0.00 |
| Uruguay | `URU` | `posesion` | -0.16 | -0.16 | 0.00 |
| Uruguay | `URU` | `ritmo` | -0.30 | -0.30 | 0.00 |
| Uruguay | `URU` | `ancho` | +0.32 | +0.32 | 0.00 |
| USA | `USA` | `defensa` | -0.24 | -0.24 | 0.00 |
| USA | `USA` | `posesion` | +0.24 | +0.24 | 0.00 |
| USA | `USA` | `ritmo` | -0.05 | -0.05 | 0.00 |
| USA | `USA` | `ancho` | -0.49 | -0.49 | 0.00 |
| Uzbekistan | `UZB` | `defensa` | -0.16 | -0.16 | 0.00 |
| Uzbekistan | `UZB` | `posesion` | -0.61 | -0.61 | 0.00 |
| Uzbekistan | `UZB` | `ritmo` | +0.06 | +0.06 | 0.00 |
| Uzbekistan | `UZB` | `ancho` | -0.51 | -0.51 | 0.00 |

## Resumen de Errores por Componente

| Componente | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) | Correlación Spearman (ρ) |
| --- | --- | --- | --- |
| `defensa` | 0.0000 | 0.0000 | +1.0000 |
| `posesion` | 0.0000 | 0.0000 | +1.0000 |
| `ritmo` | 0.0000 | 0.0000 | +1.0000 |
| `ancho` | 0.0000 | 0.0000 | +1.0000 |

**Error Medio Global (MAE):** `0.0000`
**Error Cuadrático Medio Global (RMSE):** `0.0000`
**Correlación de Spearman Promedio:** `1.0000`
