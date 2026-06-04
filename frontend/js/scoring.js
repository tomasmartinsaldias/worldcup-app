import { state } from './state.js';

// ==========================================
// CONFIGURACIÓN DE PARÁMETROS Y COEFICIENTES
// Modifica estos valores para calibrar el Score de Espectáculo (ICE)
// ==========================================
export const ICE_CONFIG = {
  alpha: 0.5,        // Ponderación de contraataques (CA_norm)
  gamma: 0.5,        // Coeficiente de amplificación de vulnerabilidad
  ICE_min: 0.1,      // Límite inferior para la escala lineal
  T_SCALE: 0.65,     // Factor de escala para el Techo Dinámico T
  // Hiperparámetros de la curva sigmoide para pBrecha usando puntos Elo
  P_MAX: 0.60,       // Techo máximo de penalización por brecha de calidad
  R_MID: 350,        // Punto de inflexión: 350 puntos de diferencia Elo → penalización = P_MAX/2
  K_STEEPNESS: 0.01,  // Pendiente de la curva adaptada a la escala de puntos Elo
  // Hiperparámetros de la función asintótica de estrellas
  B_MAX: 0.15,       // Límite superior de empuje por estrellas (15%)
  K_SAT: 5           // Saturación: N = 5 estrellas → 50% del bonus máximo (7.5%)
};

// Default keys for tactical game style cosine similarity comparison
const TACTICAL_KEYS = ['defensa', 'posesion', 'ritmo', 'ancho'];

/**
 * Calculates cosine similarity between two vectors.
 * Unified to support both fixed tactical keys and dynamic user preference vectors.
 */
export function calculateCosineSimilarity(v1, v2, keys = TACTICAL_KEYS) {
  if (!v1 || !v2) return 0;
  
  let dotProduct = 0;
  let norm1Sq = 0;
  let norm2Sq = 0;
  
  for (let i = 0; i < keys.length; i++) {
    const k = keys[i];
    const val1 = v1[k] || 0;
    const val2 = v2[k] || 0;
    dotProduct += val1 * val2;
    norm1Sq += val1 * val1;
    norm2Sq += val2 * val2;
  }
  
  if (norm1Sq === 0 || norm2Sq === 0) return 0;
  return dotProduct / (Math.sqrt(norm1Sq) * Math.sqrt(norm2Sq));
}

/**
 * Helper to analyze player squad characteristics in a single iteration.
 * Optimizes CPU time and avoids redundant array traversals.
 */
function analyzeSquad(team, userPreferences) {
  let stars = 0;
  let favPlayersBonus = 0;
  let favClubBonus = 0;
  let totalAge = 0;
  let ageCount = 0;

  if (team && team.squad) {
    const favPlayers = userPreferences?.favoritePlayers || [];
    const favClubs = userPreferences?.favoriteClubs || [];
    
    for (let i = 0; i < team.squad.length; i++) {
      const p = team.squad[i];
      if (p.is_star_player) {
        stars++;
      }
      if (favPlayers.includes(p.name)) {
        favPlayersBonus += 0.4;
      }
      if (p.club && favClubs.includes(p.club)) {
        favClubBonus += 0.15;
      }
      if (p.age) {
        totalAge += p.age;
        ageCount++;
      }
    }
  }

  return { stars, favPlayersBonus, favClubBonus, totalAge, ageCount };
}

export function calculatePlaystyleScore(vectorA, vectorB, vectorU, lambdaVal = 0.1) {
  const simA = calculateCosineSimilarity(vectorA, vectorU);
  const simB = calculateCosineSimilarity(vectorB, vectorU);

  const matchPrincipal = Math.max(simA, simB);
  const interaccion = Math.min(simA, simB) * lambdaVal;

  return matchPrincipal + interaccion;
}

/**
 * Calculates the Friction Score (Fricción) for a match.
 * Based purely on the average drama_norm (faltas + tarjetas) of both teams.
 * This is a static property of the match — the user's dramaBonus controls
 * whether it helps or hurts their SmartScore (see calculateSmartScore).
 * @returns {number} score in [1.0, 10.0]
 */
export function calculateFriccionScore(match, teams) {
  if (match.home_team.is_placeholder || match.away_team.is_placeholder) return 5.0;

  const home = teams[match.home_team.fifa_code];
  const away = teams[match.away_team.fifa_code];
  if (!home || !away) return 5.0;

  const hParams = home.espectaculo_params || { drama_norm: 0.5 };
  const aParams = away.espectaculo_params || { drama_norm: 0.5 };

  const dramaMatch = ((hParams.drama_norm ?? 0.5) + (aParams.drama_norm ?? 0.5)) / 2;
  // Scale [0,1] → [1,10]
  return parseFloat((1.0 + 9.0 * dramaMatch).toFixed(1));
}

export function calculateICEScore(match, teams) {
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
  const DRAMA_BETA_FIXED = 0.2;   // fixed — drama is no longer a user param

  // 1. La Fusión de Vectores (El Entorno del Partido)
  const ocMatch = (hParams.ocasiones_norm + aParams.ocasiones_norm) / 2;
  const caMatch = (hParams.contra_norm + aParams.contra_norm) / 2;
  const dramaMatch = (hParams.drama_norm + aParams.drama_norm) / 2;
  const vulnMatch = ((hParams.vuln_norm !== undefined ? hParams.vuln_norm : 0.5) + (aParams.vuln_norm !== undefined ? aParams.vuln_norm : 0.5)) / 2;

  // 2. Dynamic Elo Ratings (incorporating star player count as a structural modifier)
  let homeStars = 0;
  if (home.squad) {
    for (let i = 0; i < home.squad.length; i++) {
      if (home.squad[i].is_star_player) homeStars++;
    }
  }
  let awayStars = 0;
  if (away.squad) {
    for (let i = 0; i < away.squad.length; i++) {
      if (away.squad[i].is_star_player) awayStars++;
    }
  }

  const homeEloBase = (state.teamElos && state.teamElos[match.home_team.fifa_code]) || (home.metrics ? (home.metrics.elo_rating || 1500) : 1500);
  const awayEloBase = (state.teamElos && state.teamElos[match.away_team.fifa_code]) || (away.metrics ? (away.metrics.elo_rating || 1500) : 1500);
  
  const homeEloBoost = homeStars > 0 ? 100 * (homeStars / (homeStars + 5)) : 0;
  const awayEloBoost = awayStars > 0 ? 100 * (awayStars / (awayStars + 5)) : 0;
  
  const rHome = homeEloBase + homeEloBoost;
  const rAway = awayEloBase + awayEloBoost;

  // 3. Penalizador Asimétrico (Brecha de Competitividad) — Curva Sigmoide usando diferencia de Elo Base
  // La brecha competitiva pura depende de la paridad histórica, no de las estrellas del momento.
  const rankingDiff = Math.abs(homeEloBase - awayEloBase);
  const pBrecha = ICE_CONFIG.P_MAX / (1 + Math.exp(-ICE_CONFIG.K_STEEPNESS * (rankingDiff - ICE_CONFIG.R_MID)));

  // 4. Ecuación Estructural del ICE (estático — sin término drama variable)
  // El drama se calcula separadamente en calculateFriccionScore()
  const gamma = ICE_CONFIG.gamma;
  const ice = ((ocMatch * (1 + gamma * vulnMatch)) + (alpha * caMatch) + (DRAMA_BETA_FIXED * dramaMatch)) * (1 - pBrecha);

  // 5. Normalización Final a [1.0, 10.0] con Techo Dinámico (sin dramaBeta variable)
  const ICE_min = ICE_CONFIG.ICE_min;
  const T = ICE_CONFIG.T_SCALE * (1.5 + alpha + DRAMA_BETA_FIXED);
  let score = 1 + 9 * ((Math.max(ICE_min, Math.min(ice, T)) - ICE_min) / (T - ICE_min));
  
  // Factor de Calidad Absoluta basado en el Elo dinámico promedio de ambas selecciones
  const avgElo = (rHome + rAway) / 2;
  const qMatch = Math.max(0.60, Math.min(1.0, 0.60 + 0.40 * ((avgElo - 1600) / 500)));
  score = score * qMatch;

  // Stake multiplier based on qualification statuses (only for Group Stage)
  if (match.stage === 'Group Stage') {
    const statuses = state.teamStatuses || {};
    const hStatus = statuses[match.home_team.fifa_code] || 'PLAYING_FOR_LIFE';
    const aStatus = statuses[match.away_team.fifa_code] || 'PLAYING_FOR_LIFE';
    
    const statusMultipliers = {
      'PLAYING_FOR_LIFE': 1.0,
      'QUALIFIED': 0.85,
      'FIRST_PLACE_ASSURED': 0.70,
      'ELIMINATED': 0.60
    };
    
    const mHome = statusMultipliers[hStatus] || 1.0;
    const mAway = statusMultipliers[aStatus] || 1.0;
    const matchStakeMultiplier = (mHome + mAway) / 2;
    
    score = score * matchStakeMultiplier;
  }

  score = Math.min(Math.max(score, 1.0), 10.0);
  return parseFloat(score.toFixed(1));
}

export function calculateSmartScore(match, teams, tacticalVector) {
  const ice = calculateICEScore(match, teams);

  if (match.home_team.is_placeholder || match.away_team.is_placeholder) {
    match.spectacleScore = ice;
    match.playstyleScore = 5.0;
    match.friccionScore = 5.0;
    return ice;
  }

  const home = teams[match.home_team.fifa_code];
  const away = teams[match.away_team.fifa_code];

  if (!home || !away) {
    match.spectacleScore = ice;
    match.playstyleScore = 5.0;
    match.friccionScore = 5.0;
    return ice;
  }

  // Single-pass squad analysis for both teams
  const homeAnalysis = analyzeSquad(home, state.userPreferences);
  const awayAnalysis = analyzeSquad(away, state.userPreferences);

  let spectacleScore = ice;

  // Playstyle Score — compara tacticalVector del usuario con los vectores tácticos de los equipos
  // El tacticalVector se configura directamente desde el quiz (Q6) o desde los sliders de Ajustes
  const vectorU = tacticalVector || state.userPreferences?.tacticalVector || { defensa: 0.0, posesion: 0.0, ritmo: 0.0, ancho: 0.0 };
  const vectorA = home.tactical_vector || { defensa: 0.0, posesion: 0.0, ritmo: 0.0, ancho: 0.0 };
  const vectorB = away.tactical_vector || { defensa: 0.0, posesion: 0.0, ritmo: 0.0, ancho: 0.0 };

  const isDefaultU = vectorU.defensa === 0 && vectorU.posesion === 0 && vectorU.ritmo === 0 && vectorU.ancho === 0;

  let playstyleScore;
  if (isDefaultU) {
    playstyleScore = spectacleScore;
  } else {
    const rawPlaystyle = calculatePlaystyleScore(vectorA, vectorB, vectorU);
    // Linear scale from [-1.1, 1.1] to [1.0, 10.0]
    playstyleScore = 1.0 + 9.0 * ((rawPlaystyle + 1.1) / 2.2);
    playstyleScore = Math.min(Math.max(playstyleScore, 1.0), 10.0);
  }

  // Combine spectacle and playstyle scores using user weight
  const wSpectacle = state.userPreferences?.spectacleWeight ?? 0.5;
  const wPlaystyle = 1.0 - wSpectacle;
  let combinedScore = wSpectacle * spectacleScore + wPlaystyle * playstyleScore;

  // ── Fricción ──────────────────────────────────────────────────────────────
  // FriccionScore es una propiedad estática del partido (drama_norm de ambos equipos).
  // dramaBonus determina el SIGNO del efecto en SmartScore:
  //   +1 → le gusta la fricción: partidos físicos suben en ranking
  //   -1 → no le gusta: partidos físicos bajan en ranking
  //    0 → indiferente: sin efecto
  const friccionScore = calculateFriccionScore(match, teams); // [1.0, 10.0]
  const dramaBonus = state.userPreferences?.dramaBonus ?? 0;
  if (dramaBonus !== 0) {
    const FRICCION_SCALE = 0.12; // impacto máximo: ±0.12 × 4.5 ≈ ±0.54 pts
    combinedScore += dramaBonus * FRICCION_SCALE * (friccionScore - 5.5);
  }

  // ── Bonuses por entidades favoritas ───────────────────────────────────────
  let bonus = 0;

  if (state.userPreferences?.favoriteTeams?.length > 0) {
    if (state.userPreferences.favoriteTeams.includes(match.home_team.fifa_code) ||
        state.userPreferences.favoriteTeams.includes(match.away_team.fifa_code)) {
      bonus += 2.5;
    }
  }

  const favPlayersBonus = homeAnalysis.favPlayersBonus + awayAnalysis.favPlayersBonus;
  const favClubBonus = homeAnalysis.favClubBonus + awayAnalysis.favClubBonus;
  const totalAge = homeAnalysis.totalAge + awayAnalysis.totalAge;
  const playersCount = homeAnalysis.ageCount + awayAnalysis.ageCount;

  bonus += Math.min(favPlayersBonus, 2.0);
  bonus += Math.min(favClubBonus, 1.5);

  // Age preference bonus
  let ageBonus = 0;
  if (playersCount > 0 && state.userPreferences?.agePreference !== undefined) {
    const avgAge = totalAge / playersCount;
    const mappedAge = Math.max(0, Math.min(100, (avgAge - 23) / 7 * 100));
    const ageDiff = Math.abs(mappedAge - state.userPreferences.agePreference);
    ageBonus = 0.5 - (ageDiff / 100);
  }
  bonus += ageBonus;

  combinedScore += bonus;
  combinedScore = Math.min(Math.max(combinedScore, 1.0), 10.0);

  match.spectacleScore = parseFloat(spectacleScore.toFixed(1));
  match.playstyleScore = parseFloat(playstyleScore.toFixed(1));
  match.friccionScore = parseFloat(friccionScore.toFixed(1));

  return parseFloat(combinedScore.toFixed(1));
}
