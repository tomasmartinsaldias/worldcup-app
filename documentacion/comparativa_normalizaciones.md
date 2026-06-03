# Comparativa de Normalizaciones de Estilo de Juego: Cdif (Mediana) vs Mconf (Confederación)

Este documento presenta la comparación entre la normalización por Coeficiente de Dificultad ($C_{dif}$) basada en la mediana de rivales históricos y el algoritmo propuesto de **Ajuste Métrico por Confederación ($M_{conf}$)** para equilibrar los perfiles tácticos reales de SofaScore.

## 1. Medias de Control y Multiplicadores por Confederación ($M_{conf}$)

El multiplicador regional se define como $M_{conf} = \frac{\mu_{global}}{\mu_{conf}}$, castigando las estadísticas infladas por rivales débiles en la región y premiando aquellas logradas en zonas más competitivas.

| Confederación | Posesión: Media (Mconf) | Ancho: Media (Mconf) | Ritmo: Media (Mconf) | Defensa: Media (Mconf) |
| --- | --- | --- | --- | --- |
| **AFC** | 0.5275 (1.04) | 0.1029 (0.87) | 25.8289 (1.00) | 0.2948 (1.15) |
| **CAF** | 0.5207 (1.05) | 0.1021 (0.88) | 25.3469 (1.02) | 0.2979 (1.14) |
| **CONCACAF** | 0.5380 (1.02) | 0.0955 (0.94) | 22.8471 (1.13) | 0.2929 (1.16) |
| **CONMEBOL** | 0.5192 (1.06) | 0.0755 (1.19) | 20.6983 (1.25) | 0.3144 (1.08) |
| **UEFA** | 0.5937 (0.92) | 0.0773 (1.16) | 29.2794 (0.88) | 0.4145 (0.82) |

## 2. Comparativa Detallada de Vectores por Selección (47 Países)

| Selección | Código | Componente | Estadística Bruta (Cruda) | Vector con Mediana ($C_{dif}$) | Vector con Confed ($M_{conf}$) | Diferencia (Delta) |
| --- | --- | --- | --- | --- | --- | --- |
| Algeria | `ALG` | `posesion` | 0.4982 | -0.4539 | -0.1819 | +0.2720 |
| Algeria | `ALG` | `defensa` | 0.1745 | -0.6581 | -0.6627 | -0.0046 |
| Algeria | `ALG` | `ritmo` | 24.0458 | -0.3275 | -0.1685 | +0.1590 |
| Algeria | `ALG` | `ancho` | 0.1108 | +0.3549 | +0.1788 | -0.1761 |
| Argentina | `ARG` | `posesion` | 0.6077 | +0.4169 | +0.6202 | +0.2034 |
| Argentina | `ARG` | `defensa` | 0.3633 | +0.2490 | +0.2910 | +0.0420 |
| Argentina | `ARG` | `ritmo` | 19.4227 | -0.5245 | -0.2015 | +0.3230 |
| Argentina | `ARG` | `ancho` | 0.0413 | -0.8129 | -0.7477 | +0.0652 |
| Australia | `AUS` | `posesion` | 0.4984 | -0.3571 | -0.2310 | +0.1262 |
| Australia | `AUS` | `defensa` | 0.3373 | -0.0251 | +0.2704 | +0.2955 |
| Australia | `AUS` | `ritmo` | 25.0000 | -0.1494 | -0.1060 | +0.0434 |
| Australia | `AUS` | `ancho` | 0.0969 | +0.1440 | -0.1244 | -0.2684 |
| Austria | `AUT` | `posesion` | 0.6087 | +0.4645 | +0.1072 | -0.3573 |
| Austria | `AUT` | `defensa` | 0.3663 | +0.2144 | -0.2203 | -0.4347 |
| Austria | `AUT` | `ritmo` | 22.3950 | -0.2364 | -0.6524 | -0.4160 |
| Austria | `AUT` | `ancho` | 0.0748 | -0.2469 | -0.0689 | +0.1780 |
| Belgium | `BEL` | `posesion` | 0.6393 | +0.6096 | +0.3159 | -0.2937 |
| Belgium | `BEL` | `defensa` | 0.5389 | +0.7483 | +0.5210 | -0.2273 |
| Belgium | `BEL` | `ritmo` | 33.8473 | +0.7531 | +0.4755 | -0.2776 |
| Belgium | `BEL` | `ancho` | 0.0740 | -0.2557 | -0.0896 | +0.1661 |
| Bosnia and Herzegovina | `BIH` | `posesion` | 0.4652 | -0.4540 | -0.7264 | -0.2724 |
| Bosnia and Herzegovina | `BIH` | `defensa` | 0.2049 | -0.5629 | -0.7502 | -0.1873 |
| Bosnia and Herzegovina | `BIH` | `ritmo` | 34.2685 | +0.6883 | +0.5116 | -0.1767 |
| Bosnia and Herzegovina | `BIH` | `ancho` | 0.1147 | +0.5707 | +0.7752 | +0.2046 |
| Brazil | `BRA` | `posesion` | 0.5923 | +0.4899 | +0.5364 | +0.0465 |
| Brazil | `BRA` | `defensa` | 0.3473 | +0.3000 | +0.1987 | -0.1013 |
| Brazil | `BRA` | `ritmo` | 19.6099 | -0.4281 | -0.1726 | +0.2555 |
| Brazil | `BRA` | `ancho` | 0.0657 | -0.3999 | -0.2691 | +0.1308 |
| Canada | `CAN` | `posesion` | 0.5487 | +0.0533 | +0.0844 | +0.0311 |
| Canada | `CAN` | `defensa` | 0.4951 | +0.5853 | +0.8691 | +0.2838 |
| Canada | `CAN` | `ritmo` | 21.3913 | -0.3846 | -0.2081 | +0.1765 |
| Canada | `CAN` | `ancho` | 0.1119 | +0.5606 | +0.3523 | -0.2083 |
| Côte d'Ivoire | `CIV` | `posesion` | 0.5713 | -0.1578 | +0.3916 | +0.5494 |
| Côte d'Ivoire | `CIV` | `defensa` | 0.3375 | -0.2173 | +0.2505 | +0.4678 |
| Côte d'Ivoire | `CIV` | `ritmo` | 29.2359 | +0.0893 | +0.4689 | +0.3796 |
| Côte d'Ivoire | `CIV` | `ancho` | 0.1119 | +0.3306 | +0.2014 | -0.1292 |
| DR Congo | `COD` | `posesion` | 0.4046 | -0.7802 | -0.7396 | +0.0406 |
| DR Congo | `COD` | `defensa` | 0.2377 | -0.6398 | -0.3705 | +0.2693 |
| DR Congo | `COD` | `ritmo` | 32.7586 | +0.3830 | +0.7484 | +0.3654 |
| DR Congo | `COD` | `ancho` | 0.1218 | +0.5070 | +0.3890 | -0.1180 |
| Colombia | `COL` | `posesion` | 0.5291 | +0.0850 | +0.0808 | -0.0042 |
| Colombia | `COL` | `defensa` | 0.3562 | +0.2728 | +0.2504 | -0.0224 |
| Colombia | `COL` | `ritmo` | 26.6628 | +0.2565 | +0.7421 | +0.4857 |
| Colombia | `COL` | `ancho` | 0.0843 | +0.0380 | +0.2445 | +0.2064 |
| Cabo Verde | `CPV` | `posesion` | 0.5445 | -0.3078 | +0.1920 | +0.4997 |
| Cabo Verde | `CPV` | `defensa` | 0.4021 | +0.0402 | +0.5873 | +0.5471 |
| Cabo Verde | `CPV` | `ritmo` | 21.9554 | -0.5302 | -0.4166 | +0.1136 |
| Cabo Verde | `CPV` | `ancho` | 0.0987 | +0.0304 | -0.0724 | -0.1028 |
| Croatia | `CRO` | `posesion` | 0.6557 | +0.6854 | +0.4175 | -0.2679 |
| Croatia | `CRO` | `defensa` | 0.4463 | +0.5303 | +0.1465 | -0.3838 |
| Croatia | `CRO` | `ritmo` | 34.0714 | +0.7747 | +0.4949 | -0.2798 |
| Croatia | `CRO` | `ancho` | 0.0942 | +0.2772 | +0.4375 | +0.1603 |
| Curaçao | `CUR` | `posesion` | 0.4920 | -0.5912 | -0.3488 | +0.2424 |
| Curaçao | `CUR` | `defensa` | 0.1517 | -0.7621 | -0.7296 | +0.0325 |
| Curaçao | `CUR` | `ritmo` | 14.8355 | -0.8577 | -0.8218 | +0.0359 |
| Curaçao | `CUR` | `ancho` | 0.0966 | -0.0874 | +0.0265 | +0.1139 |
| Czech Republic | `CZE` | `posesion` | 0.5101 | -0.2872 | -0.5365 | -0.2493 |
| Czech Republic | `CZE` | `defensa` | 0.3270 | -0.2097 | -0.3854 | -0.1757 |
| Czech Republic | `CZE` | `ritmo` | 29.4756 | +0.2902 | +0.0222 | -0.2680 |
| Czech Republic | `CZE` | `ancho` | 0.1298 | +0.7408 | +0.8960 | +0.1552 |
| Ecuador | `ECU` | `posesion` | 0.4904 | -0.1407 | -0.2320 | -0.0914 |
| Ecuador | `ECU` | `defensa` | 0.3070 | +0.0808 | -0.0452 | -0.1260 |
| Ecuador | `ECU` | `ritmo` | 21.3740 | -0.2867 | +0.1078 | +0.3945 |
| Ecuador | `ECU` | `ancho` | 0.0725 | -0.2602 | -0.0841 | +0.1761 |
| Egypt | `EGY` | `posesion` | 0.4569 | -0.6121 | -0.4788 | +0.1332 |
| Egypt | `EGY` | `defensa` | 0.1181 | -0.8412 | -0.8216 | +0.0196 |
| Egypt | `EGY` | `ritmo` | 22.1414 | -0.4765 | -0.3963 | +0.0802 |
| Egypt | `EGY` | `ancho` | 0.0800 | -0.3278 | -0.4323 | -0.1045 |
| England | `ENG` | `posesion` | 0.7191 | +0.8316 | +0.7160 | -0.1156 |
| England | `ENG` | `defensa` | 0.6214 | +0.8679 | +0.7447 | -0.1232 |
| England | `ENG` | `ritmo` | 26.5793 | +0.2099 | -0.2965 | -0.5064 |
| England | `ENG` | `ancho` | 0.0510 | -0.6971 | -0.6209 | +0.0762 |
| Spain | `ESP` | `posesion` | 0.6766 | +0.7614 | +0.5332 | -0.2282 |
| Spain | `ESP` | `defensa` | 0.5357 | +0.7637 | +0.5100 | -0.2537 |
| Spain | `ESP` | `ritmo` | 34.4681 | +0.8015 | +0.5281 | -0.2734 |
| Spain | `ESP` | `ancho` | 0.0463 | -0.7468 | -0.6947 | +0.0521 |
| France | `FRA` | `posesion` | 0.6551 | +0.7353 | +0.4143 | -0.3210 |
| France | `FRA` | `defensa` | 0.6042 | +0.8746 | +0.7069 | -0.1677 |
| France | `FRA` | `ritmo` | 34.0146 | +0.8075 | +0.4900 | -0.3175 |
| France | `FRA` | `ancho` | 0.0538 | -0.6298 | -0.5712 | +0.0587 |
| Germany | `GER` | `posesion` | 0.7025 | +0.8448 | +0.6531 | -0.1918 |
| Germany | `GER` | `defensa` | 0.3755 | +0.3847 | -0.1792 | -0.5639 |
| Germany | `GER` | `ritmo` | 24.8634 | +0.1206 | -0.4621 | -0.5827 |
| Germany | `GER` | `ancho` | 0.0640 | -0.4342 | -0.3505 | +0.0837 |
| Ghana | `GHA` | `posesion` | 0.4896 | -0.5302 | -0.2488 | +0.2814 |
| Ghana | `GHA` | `defensa` | 0.4317 | +0.2236 | +0.6990 | +0.4753 |
| Ghana | `GHA` | `ritmo` | 22.0981 | -0.5118 | -0.4011 | +0.1108 |
| Ghana | `GHA` | `ancho` | 0.1187 | +0.4597 | +0.3327 | -0.1270 |
| Haiti | `HAI` | `posesion` | 0.4277 | -0.7669 | -0.7030 | +0.0639 |
| Haiti | `HAI` | `defensa` | 0.3098 | -0.3736 | +0.1108 | +0.4843 |
| Haiti | `HAI` | `ritmo` | 26.5659 | -0.2526 | +0.4927 | +0.7452 |
| Haiti | `HAI` | `ancho` | 0.1614 | +0.8647 | +0.9009 | +0.0362 |
| IR Iran | `IRN` | `posesion` | 0.5363 | -0.1549 | +0.0708 | +0.2256 |
| IR Iran | `IRN` | `defensa` | 0.2628 | -0.2810 | -0.2065 | +0.0745 |
| IR Iran | `IRN` | `ritmo` | 29.9600 | +0.3257 | +0.4855 | +0.1598 |
| IR Iran | `IRN` | `ancho` | 0.1207 | +0.6190 | +0.3535 | -0.2654 |
| Iraq | `IRQ` | `posesion` | 0.4543 | -0.6165 | -0.5310 | +0.0856 |
| Iraq | `IRQ` | `defensa` | 0.2145 | -0.6151 | -0.4814 | +0.1337 |
| Iraq | `IRQ` | `ritmo` | 23.5656 | -0.3614 | -0.2826 | +0.0788 |
| Iraq | `IRQ` | `ancho` | 0.1420 | +0.8012 | +0.6705 | -0.1307 |
| Jordan | `JOR` | `posesion` | 0.3677 | -0.8004 | -0.8591 | -0.0587 |
| Jordan | `JOR` | `defensa` | 0.1055 | -0.8164 | -0.8444 | -0.0280 |
| Jordan | `JOR` | `ritmo` | 36.9048 | +0.7729 | +0.8899 | +0.1170 |
| Jordan | `JOR` | `ancho` | 0.1288 | +0.7295 | +0.4912 | -0.2383 |
| Japan | `JPN` | `posesion` | 0.6003 | +0.2907 | +0.5276 | +0.2369 |
| Japan | `JPN` | `defensa` | 0.3900 | +0.2753 | +0.5523 | +0.2770 |
| Japan | `JPN` | `ritmo` | 20.8333 | -0.4598 | -0.5657 | -0.1059 |
| Japan | `JPN` | `ancho` | 0.0684 | -0.4564 | -0.6148 | -0.1583 |
| South Korea | `KOR` | `posesion` | 0.6617 | +0.5158 | +0.7941 | +0.2783 |
| South Korea | `KOR` | `defensa` | 0.4259 | +0.3660 | +0.6941 | +0.3281 |
| South Korea | `KOR` | `ritmo` | 23.6867 | -0.2566 | -0.2682 | -0.0117 |
| South Korea | `KOR` | `ancho` | 0.0844 | -0.1396 | -0.3656 | -0.2260 |
| Saudi Arabia | `KSA` | `posesion` | 0.6073 | +0.2523 | +0.5673 | +0.3150 |
| Saudi Arabia | `KSA` | `defensa` | 0.2984 | -0.2307 | +0.0235 | +0.2541 |
| Saudi Arabia | `KSA` | `ritmo` | 23.0769 | -0.3145 | -0.3392 | -0.0247 |
| Saudi Arabia | `KSA` | `ancho` | 0.0972 | +0.1658 | -0.1167 | -0.2825 |
| Morocco | `MAR` | `posesion` | 0.5335 | -0.2032 | +0.1041 | +0.3073 |
| Morocco | `MAR` | `defensa` | 0.3489 | -0.0709 | +0.3184 | +0.3893 |
| Morocco | `MAR` | `ritmo` | 27.9710 | +0.1121 | +0.3303 | +0.2182 |
| Morocco | `MAR` | `ancho` | 0.1024 | +0.2488 | +0.0055 | -0.2433 |
| Mexico | `MEX` | `posesion` | 0.5811 | +0.2735 | +0.3280 | +0.0545 |
| Mexico | `MEX` | `defensa` | 0.2715 | -0.2017 | -0.1395 | +0.0622 |
| Mexico | `MEX` | `ritmo` | 23.9651 | -0.1153 | +0.1608 | +0.2761 |
| Mexico | `MEX` | `ancho` | 0.0720 | -0.3404 | -0.4821 | -0.1417 |
| Netherlands | `NED` | `posesion` | 0.6398 | +0.6243 | +0.3193 | -0.3049 |
| Netherlands | `NED` | `defensa` | 0.4999 | +0.6796 | +0.3769 | -0.3027 |
| Netherlands | `NED` | `ritmo` | 26.8769 | +0.2536 | -0.2655 | -0.5191 |
| Netherlands | `NED` | `ancho` | 0.0626 | -0.5005 | -0.3842 | +0.1164 |
| Norway | `NOR` | `posesion` | 0.5511 | -0.0118 | -0.2964 | -0.2847 |
| Norway | `NOR` | `defensa` | 0.4197 | +0.3443 | +0.0242 | -0.3201 |
| Norway | `NOR` | `ritmo` | 38.3043 | +0.8421 | +0.7706 | -0.0715 |
| Norway | `NOR` | `ancho` | 0.0706 | -0.4243 | -0.1835 | +0.2408 |
| Panama | `PAN` | `posesion` | 0.6214 | +0.3774 | +0.5782 | +0.2008 |
| Panama | `PAN` | `defensa` | 0.2947 | -0.0826 | +0.0120 | +0.0945 |
| Panama | `PAN` | `ritmo` | 26.5152 | +0.0560 | +0.4871 | +0.4311 |
| Panama | `PAN` | `ancho` | 0.0678 | -0.4767 | -0.5505 | -0.0737 |
| Paraguay | `PAR` | `posesion` | 0.4042 | -0.5580 | -0.7366 | -0.1787 |
| Paraguay | `PAR` | `defensa` | 0.2288 | -0.1957 | -0.4807 | -0.2849 |
| Paraguay | `PAR` | `ritmo` | 15.6994 | -0.7037 | -0.6644 | +0.0393 |
| Paraguay | `PAR` | `ancho` | 0.0934 | +0.3199 | +0.4667 | +0.1467 |
| Portugal | `POR` | `posesion` | 0.6810 | +0.6984 | +0.5553 | -0.1431 |
| Portugal | `POR` | `defensa` | 0.5949 | +0.8085 | +0.6847 | -0.1238 |
| Portugal | `POR` | `ritmo` | 36.4656 | +0.8229 | +0.6716 | -0.1513 |
| Portugal | `POR` | `ancho` | 0.0629 | -0.5302 | -0.3780 | +0.1521 |
| Qatar | `QAT` | `posesion` | 0.5652 | -0.0207 | +0.2946 | +0.3153 |
| Qatar | `QAT` | `defensa` | 0.2705 | -0.3403 | -0.1573 | +0.1830 |
| Qatar | `QAT` | `ritmo` | 21.2072 | -0.4896 | -0.5322 | -0.0425 |
| Qatar | `QAT` | `ancho` | 0.1176 | +0.5551 | +0.2970 | -0.2581 |
| South Africa | `RSA` | `posesion` | 0.5985 | -0.0630 | +0.5622 | +0.6252 |
| South Africa | `RSA` | `defensa` | 0.2870 | -0.4656 | -0.0700 | +0.3955 |
| South Africa | `RSA` | `ritmo` | 24.8031 | -0.3376 | -0.0710 | +0.2666 |
| South Africa | `RSA` | `ancho` | 0.0854 | -0.2787 | -0.3369 | -0.0582 |
| Scotland | `SCO` | `posesion` | 0.4167 | -0.5588 | -0.8537 | -0.2949 |
| Scotland | `SCO` | `defensa` | 0.1715 | -0.5014 | -0.8105 | -0.3092 |
| Scotland | `SCO` | `ritmo` | 26.9202 | +0.2579 | -0.2609 | -0.5189 |
| Scotland | `SCO` | `ancho` | 0.1327 | +0.8580 | +0.9108 | +0.0529 |
| Senegal | `SEN` | `posesion` | 0.5779 | -0.0600 | +0.4361 | +0.4961 |
| Senegal | `SEN` | `defensa` | 0.3261 | -0.2683 | +0.1808 | +0.4491 |
| Senegal | `SEN` | `ritmo` | 28.4779 | +0.0749 | +0.3880 | +0.3131 |
| Senegal | `SEN` | `ancho` | 0.0836 | -0.2512 | -0.3689 | -0.1176 |
| Switzerland | `SUI` | `posesion` | 0.5774 | +0.2786 | -0.1165 | -0.3951 |
| Switzerland | `SUI` | `defensa` | 0.3463 | +0.1800 | -0.3066 | -0.4867 |
| Switzerland | `SUI` | `ritmo` | 19.2287 | -0.5294 | -0.8137 | -0.2843 |
| Switzerland | `SUI` | `ancho` | 0.0629 | -0.5172 | -0.3774 | +0.1398 |
| Sweden | `SWE` | `posesion` | 0.4799 | -0.3313 | -0.6731 | -0.3417 |
| Sweden | `SWE` | `defensa` | 0.3088 | -0.0973 | -0.4549 | -0.3576 |
| Sweden | `SWE` | `ritmo` | 19.5933 | -0.5255 | -0.7993 | -0.2738 |
| Sweden | `SWE` | `ancho` | 0.0760 | -0.2619 | -0.0364 | +0.2255 |
| Tunisia | `TUN` | `posesion` | 0.5321 | -0.2976 | +0.0928 | +0.3905 |
| Tunisia | `TUN` | `defensa` | 0.3150 | -0.2820 | +0.1106 | +0.3926 |
| Tunisia | `TUN` | `ritmo` | 19.9822 | -0.6173 | -0.6054 | +0.0119 |
| Tunisia | `TUN` | `ancho` | 0.1082 | +0.3010 | +0.1254 | -0.1756 |
| Turkey | `TUR` | `posesion` | 0.5208 | -0.0530 | -0.4798 | -0.4268 |
| Turkey | `TUR` | `defensa` | 0.2708 | -0.1783 | -0.5832 | -0.4048 |
| Turkey | `TUR` | `ritmo` | 27.0985 | +0.2264 | -0.2420 | -0.4684 |
| Turkey | `TUR` | `ancho` | 0.0662 | -0.4533 | -0.2978 | +0.1555 |
| Uruguay | `URU` | `posesion` | 0.4917 | -0.1561 | -0.2223 | -0.0663 |
| Uruguay | `URU` | `defensa` | 0.2837 | -0.0300 | -0.1856 | -0.1556 |
| Uruguay | `URU` | `ritmo` | 21.4210 | -0.2984 | +0.1152 | +0.4136 |
| Uruguay | `URU` | `ancho` | 0.0957 | +0.3184 | +0.5171 | +0.1987 |
| USA | `USA` | `posesion` | 0.5573 | +0.2407 | +0.1512 | -0.0895 |
| USA | `USA` | `defensa` | 0.2344 | -0.2353 | -0.3663 | -0.1310 |
| USA | `USA` | `ritmo` | 23.8095 | -0.0529 | +0.1387 | +0.1917 |
| USA | `USA` | `ancho` | 0.0630 | -0.4872 | -0.6212 | -0.1340 |
| Uzbekistan | `UZB` | `posesion` | 0.4569 | -0.6077 | -0.5157 | +0.0920 |
| Uzbekistan | `UZB` | `defensa` | 0.3486 | -0.1566 | +0.3373 | +0.4939 |
| Uzbekistan | `UZB` | `ritmo` | 28.2258 | +0.0592 | +0.2983 | +0.2391 |
| Uzbekistan | `UZB` | `ancho` | 0.0700 | -0.5132 | -0.5933 | -0.0801 |