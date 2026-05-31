import { state } from './state.js';

// ==========================================
// CONFIGURACIÓN DE PARÁMETROS Y COEFICIENTES
// Modifica estos valores para calibrar el Score de Espectáculo (ICE)
// ==========================================
export const ICE_CONFIG = {
  alpha: 0.5,        // Ponderación de contraataques (CA_norm)
  gamma: 0.5,        // Coeficiente de amplificación de vulnerabilidad
  ICE_min: 0.1,      // Límite inferior para la escala lineal
  T_SCALE: 0.75,     // Factor de escala para el Techo Dinámico T
  // Hiperparámetros de la curva sigmoide para pBrecha
  P_MAX: 0.60,       // Techo máximo de penalización por brecha de ranking
  R_MID: 40,         // Punto de inflexión: 40 puestos de diferencia → penalización = P_MAX/2
  K_STEEPNESS: 0.1,  // Pendiente de la curva (más alto = transición más brusca)
  // Hiperparámetros de la función asintótica de estrellas
  B_MAX: 0.15,       // Límite superior de empuje por estrellas (15%)
  K_SAT: 5           // Saturación: N = 5 estrellas → 50% del bonus máximo (7.5%)
};

export function calculateCosineSimilarity(v1, v2) {
  if (!v1 || !v2) return 0;
  const dotProduct = (v1.defensa * v2.defensa) + (v1.posesion * v2.posesion) + (v1.ritmo * v2.ritmo) + (v1.ancho * v2.ancho);
  const norm1 = Math.sqrt(v1.defensa ** 2 + v1.posesion ** 2 + v1.ritmo ** 2 + v1.ancho ** 2);
  const norm2 = Math.sqrt(v2.defensa ** 2 + v2.posesion ** 2 + v2.ritmo ** 2 + v2.ancho ** 2);
  if (norm1 === 0 || norm2 === 0) return 0;
  return dotProduct / (norm1 * norm2);
}

export function calculatePlaystyleScore(vectorA, vectorB, vectorU, lambdaVal = 0.1) {
  const simA = calculateCosineSimilarity(vectorA, vectorU);
  const simB = calculateCosineSimilarity(vectorB, vectorU);

  const matchPrincipal = Math.max(simA, simB);
  const interaccion = Math.min(simA, simB) * lambdaVal;

  return matchPrincipal + interaccion;
}

export function calculateICEScore(match, teams, dramaBeta = 0.2) {
  if (match.home_team.is_placeholder || match.away_team.is_placeholder) {
    return 5.0; // default for playoff TBD matches
  }

  const home = teams[match.home_team.fifa_code];
  const away = teams[match.away_team.fifa_code];

  if (!home || !away) {
    return 5.0;
  }

  const hParams = home.espectaculo_params || { ocasiones_norm: 0.5, contra_norm: 0.5, drama_norm: 0.5, vuln_norm: 0.5 };
  const aParams = away.espectaculo_params || { ocasiones_norm: 0.5, contra_norm: 0.5, drama_norm: 0.5, vuln_norm: 0.5 };

  const alpha = ICE_CONFIG.alpha; // weight for counter attacks

  // 1. La Fusión de Vectores (El Entorno del Partido)
  const ocMatch = (hParams.ocasiones_norm + aParams.ocasiones_norm) / 2;
  const caMatch = (hParams.contra_norm + aParams.contra_norm) / 2;
  const dramaMatch = (hParams.drama_norm + aParams.drama_norm) / 2;
  const vulnMatch = ((hParams.vuln_norm !== undefined ? hParams.vuln_norm : 0.5) + (aParams.vuln_norm !== undefined ? aParams.vuln_norm : 0.5)) / 2;

  // 2. Rankings FIFA
  const rHome = home.metrics ? (home.metrics.fifa_ranking || 60) : 60;
  const rAway = away.metrics ? (away.metrics.fifa_ranking || 60) : 60;

  // 3. Penalizador Asimétrico (Brecha FIFA) — Curva Sigmoide
  // Brechas pequeñas (<15) apenas penalizan; inflexión en R_MID puestos; techo en P_MAX
  const rankingDiff = Math.abs(rHome - rAway);
  const pBrecha = ICE_CONFIG.P_MAX / (1 + Math.exp(-ICE_CONFIG.K_STEEPNESS * (rankingDiff - ICE_CONFIG.R_MID)));

  // 4. Ecuación Final del Sistema (ICEmatch) con Amplificador de Vulnerabilidad
  const gamma = ICE_CONFIG.gamma;
  const ice = ((ocMatch * (1 + gamma * vulnMatch)) + (alpha * caMatch) + (dramaBeta * dramaMatch)) * (1 - pBrecha);

  // 5. Normalización Final a [1.0, 10.0] con Techo Dinámico
  const ICE_min = ICE_CONFIG.ICE_min;
  // El máximo valor teórico posible bajo la nueva ecuación es: OCmax * (1 + gamma * Vmax) + alpha * CAmax + dramaBeta * DramaMax
  // Con OC=1, V=1, CA=1, Drama=1: 1 * (1 + 0.5) + alpha + dramaBeta = 1.5 + alpha + dramaBeta
  const T = ICE_CONFIG.T_SCALE * (1.5 + alpha + dramaBeta); // Techo dinámico proporcional al valor teórico máximo (ajustado para conservar distribución amplia)
  let score = 1 + 9 * ((Math.max(ICE_min, Math.min(ice, T)) - ICE_min) / (T - ICE_min));
  score = Math.min(Math.max(score, 1.0), 10.0);
  return parseFloat(score.toFixed(1));
}

export function calculateSmartScore(match, teams, tacticalVector) {
  const dramaBeta = state.userPreferences?.dramaBeta !== undefined ? state.userPreferences.dramaBeta : 0.2;
  const ice = calculateICEScore(match, teams, dramaBeta);

  if (match.home_team.is_placeholder || match.away_team.is_placeholder) {
    match.spectacleScore = ice;
    match.playstyleScore = 5.0;
    return ice;
  }

  const home = teams[match.home_team.fifa_code];
  const away = teams[match.away_team.fifa_code];

  if (!home || !away) {
    match.spectacleScore = ice;
    match.playstyleScore = 5.0;
    return ice;
  }

  const homeStars = home.squad ? home.squad.filter(p => p.is_star_player).length : 0;
  const awayStars = away.squad ? away.squad.filter(p => p.is_star_player).length : 0;
  const starCount = homeStars + awayStars;

  // Bonus asintótico: Bmax * (N / (N + K))
  const bonusPct = starCount > 0 ? ICE_CONFIG.B_MAX * (starCount / (starCount + ICE_CONFIG.K_SAT)) : 0;
  let spectacleScore = ice * (1 + bonusPct);
  spectacleScore = Math.min(Math.max(spectacleScore, 1.0), 10.0);

  // Playstyle Score
  const vectorU = tacticalVector || { defensa: 0.0, posesion: 0.0, ritmo: 0.0, ancho: 0.0 };
  const vectorA = home.tactical_vector || { defensa: 0.0, posesion: 0.0, ritmo: 0.0, ancho: 0.0 };
  const vectorB = away.tactical_vector || { defensa: 0.0, posesion: 0.0, ritmo: 0.0, ancho: 0.0 };

  const isDefaultU = vectorU.defensa === 0 && vectorU.posesion === 0 && vectorU.ritmo === 0 && vectorU.ancho === 0;

  let playstyleScore;
  if (isDefaultU) {
    playstyleScore = spectacleScore;
  } else {
    const rawPlaystyle = calculatePlaystyleScore(vectorA, vectorB, vectorU);

    // Linear scale from [-1.1, 1.1] to [1.0, 10.0]
    const minVal = -1.1;
    const maxVal = 1.1;
    playstyleScore = 1.0 + 9.0 * ((rawPlaystyle - minVal) / (maxVal - minVal));
    playstyleScore = Math.min(Math.max(playstyleScore, 1.0), 10.0);
  }

  // Combine spectacle and playstyle scores using custom user weights
  const wSpectacle = state.userPreferences?.spectacleWeight !== undefined ? state.userPreferences.spectacleWeight : 0.7;
  const wPlaystyle = 1.0 - wSpectacle;
  let combinedScore = wSpectacle * spectacleScore + wPlaystyle * playstyleScore;
  combinedScore = Math.min(Math.max(combinedScore, 1.0), 10.0);

  match.spectacleScore = parseFloat(spectacleScore.toFixed(1));
  match.playstyleScore = parseFloat(playstyleScore.toFixed(1));

  return parseFloat(combinedScore.toFixed(1));
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
