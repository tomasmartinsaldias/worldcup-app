export function calculateICEScore(match, teams) {
  if (match.home_team.is_placeholder || match.away_team.is_placeholder) {
    return 5.0; // default for playoff TBD matches
  }

  const home = teams[match.home_team.fifa_code];
  const away = teams[match.away_team.fifa_code];

  if (!home || !away || !home.metrics || !away.metrics) {
    return 5.0;
  }

  const hMetrics = home.metrics;
  const aMetrics = away.metrics;

  // ==========================================
  // COEFICIENTES Y PARÁMETROS CONFIGURABLES
  // ==========================================
  const alpha = 0.5;        // Ponderación de goles en contra (Gc)
  const beta = 0.125;         // Ponderación de tarjetas + penales (Drama)

  const rankImpact = 0.6;   // Atenuador de la diferencia de ranking (menor valor = ranking menos punitivo)
  const T = 3.7;            // Techo Empírico (Un poco más alto que el partido con más puntaje)
  // ==========================================

  // 1. Rankings FIFA
  const rHome = hMetrics.fifa_ranking || 60;
  const rAway = aMetrics.fifa_ranking || 60;

  // 2. Volumen de Espectáculo Individual (V)
  const gnpHome = hMetrics.gnp_per_90 !== null ? hMetrics.gnp_per_90 : 1.1;
  const gnpAway = aMetrics.gnp_per_90 !== null ? aMetrics.gnp_per_90 : 1.1;

  const gcHome = hMetrics.gc_per_90 !== null ? hMetrics.gc_per_90 : 1.1;
  const gcAway = aMetrics.gc_per_90 !== null ? aMetrics.gc_per_90 : 1.1;

  const dramaHome = hMetrics.drama_per_90 !== null ? hMetrics.drama_per_90 : 2.5;
  const dramaAway = aMetrics.drama_per_90 !== null ? aMetrics.drama_per_90 : 2.5;

  const vHome = gnpHome + (alpha * gcHome) + (beta * dramaHome);
  const vAway = gnpAway + (alpha * gcAway) + (beta * dramaAway);

  // 3. Fórmula ICE(A,B)
  const rankingDiff = Math.abs(rHome - rAway);
  // Dividimos usando el logaritmo atenuado por rankImpact
  const ice = (vHome + vAway) / (1 + rankImpact * Math.log(rankingDiff + 1));

  // 4. Normalización Lineal con Clipping (Techo Empírico)
  // Mapeamos el rango de interés real [1.2, 2.8] al rango legible [1.0, 10.0]
  const ICE_min = 1.2;
  let score = 1 + 9 * ((Math.max(ICE_min, Math.min(ice, T)) - ICE_min) / (T - ICE_min));
  score = Math.min(Math.max(score, 1.0), 10.0);
  return parseFloat(score.toFixed(1));
}

export function calculateSmartScore(match, teams) {
  const ice = calculateICEScore(match, teams);

  if (match.home_team.is_placeholder || match.away_team.is_placeholder) {
    return ice;
  }

  const home = teams[match.home_team.fifa_code];
  const away = teams[match.away_team.fifa_code];

  if (!home || !away) {
    return ice;
  }

  // Coeficiente configurable para jugadores estrella
  const gamma = 0.15;

  const homeStars = home.squad ? home.squad.filter(p => p.is_star_player).length : 0;
  const awayStars = away.squad ? away.squad.filter(p => p.is_star_player).length : 0;
  const starCount = homeStars + awayStars;

  let finalScore = ice + (gamma * starCount);
  finalScore = Math.min(Math.max(finalScore, 1.0), 10.0);
  return parseFloat(finalScore.toFixed(1));
}

export function calculateFormRating(player) {
  let ratingVal = 6.5; // default fallback

  if (player.minutes_recent && player.minutes_recent > 0) {
    const p90 = 90.0 / player.minutes_recent;
    const xG90 = (player.xG_intl || 0) * p90;
    const sca90 = (player.sca_intl || 0) * p90;
    const gca90 = (player.gca_intl || 0) * p90;
    const progP90 = (player.progressive_passes_intl || 0) * p90;
    const progC90 = (player.progressive_carries_intl || 0) * p90;

    let baseScore = 6.0;
    let performance = 0;

    const pos = (player.position || '').toLowerCase();
    if (pos.includes('delantero') || pos.includes('forward') || pos.includes('atacante')) {
      performance = (xG90 * 2.0) + (gca90 * 1.5) + (sca90 * 0.2);
    } else if (pos.includes('centrocampista') || pos.includes('midfielder')) {
      performance = (sca90 * 0.4) + (progP90 * 0.15) + (gca90 * 1.0) + (progC90 * 0.1);
    } else if (pos.includes('defensa') || pos.includes('defender')) {
      performance = (progC90 * 0.2) + (progP90 * 0.2) + (sca90 * 0.3);
    } else if (pos.includes('portero') || pos.includes('goalkeeper')) {
      let gkBase = 1.0;
      if (player.market_value_eur) gkBase += Math.min(player.market_value_eur / 20.0, 1.5);
      if (player.caps) gkBase += Math.min(player.caps / 50.0, 1.0);
      performance = player.efficiency_score ? (player.efficiency_score * 3) : gkBase;
    } else {
      performance = (xG90 * 0.5) + (sca90 * 0.2) + (progP90 * 0.1);
    }

    const effBonus = player.efficiency_score !== null ? (player.efficiency_score * 1.5) : 0;
    ratingVal = baseScore + performance + effBonus;
  } else if (player.efficiency_score !== null) {
    ratingVal = player.efficiency_score * 4 + 5.5;
  }

  return Math.min(Math.max(ratingVal, 5.0), 9.9);
}
