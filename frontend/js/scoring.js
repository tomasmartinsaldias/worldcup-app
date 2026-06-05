import { state } from './futstate.js';

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

function getTeamMaxMarketValue(team) {
  if (!team || !team.squad || team.squad.length === 0) return 0;
  return Math.max(...team.squad.map(p => p.market_value_eur || 0));
}

function robustNormalise(str) {
  if (!str) return '';
  return str
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/\u00f8/gi, 'o').replace(/\u00f0/gi, 'd').replace(/\u00fe/gi, 'th')
    .replace(/\u00e6/gi, 'ae').replace(/\u0142/gi, 'l').replace(/\u00df/gi, 'ss').replace(/\u0153/gi, 'oe')
    .replace(/[^\x00-\x7F]/g, '')
    .toLowerCase().trim();
}

export function findClusterPlayer(playerName) {
  if (!state.appData || !state.appData.clusters) return null;
  const targetNorm = robustNormalise(playerName);
  const targetParts = targetNorm.split(/\s+/).filter(p => p.length > 0);
  
  if (targetParts.length === 0) return null;
  
  const groups = ['Goalkeepers', 'Centerbacks', 'Fullbacks', 'Midfielders', 'Wingers', 'Strikers'];
  for (let i = 0; i < groups.length; i++) {
    const groupName = groups[i];
    const list = state.appData.clusters[groupName];
    if (!list) continue;
    for (let j = 0; j < list.length; j++) {
      const cp = list[j];
      const longNorm = robustNormalise(cp.long_name);
      
      // 1. Direct match or substring match
      if (longNorm === targetNorm || longNorm.includes(targetNorm) || targetNorm.includes(longNorm)) {
        return { cp, groupName };
      }
      
      // 2. Parts match: check if every part in targetParts matches a part in longNorm (supporting initials)
      const candidateParts = longNorm.split(/\s+/);
      let matchCount = 0;
      let lastCheckedIndex = -1;
      
      for (let pIdx = 0; pIdx < targetParts.length; pIdx++) {
        const tp = targetParts[pIdx];
        const isInitial = tp.length === 1 || (tp.length === 2 && tp[1] === '.');
        const cleanTp = isInitial ? tp[0] : tp;
        
        for (let k = lastCheckedIndex + 1; k < candidateParts.length; k++) {
          const cpPart = candidateParts[k];
          if (isInitial) {
            if (cpPart.startsWith(cleanTp)) {
              matchCount++;
              lastCheckedIndex = k;
              break;
            }
          } else {
            if (cpPart === cleanTp || cpPart.includes(cleanTp)) {
              matchCount++;
              lastCheckedIndex = k;
              break;
            }
          }
        }
      }
      
      if (matchCount === targetParts.length) {
        return { cp, groupName };
      }
    }
  }
  return null;
}

export function getSeleccionTotalMinutes(teamCode) {
  if (teamCode === 'CAN') return 360;
  if (teamCode === 'MEX' || teamCode === 'USA') return 540;
  const conmebol = ['ARG', 'BRA', 'URU', 'COL', 'ECU', 'PAR', 'CHI', 'VEN', 'BOL', 'PER'];
  if (conmebol.includes(teamCode)) return 18 * 90; // 1620
  return 10 * 90; // 900
}

export function calculatePJuego(player, teamCode, teamMaxVal) {
  // Injured players contribute nothing to the score
  if (player.is_injured) {
    return 0.0;
  }
  if (player.is_star_player && !player.is_injured) {
    return 1.0;
  }
  if (player.minutes_recent !== undefined && player.minutes_recent !== null && player.minutes_recent > 0) {
    const totalMins = getSeleccionTotalMinutes(teamCode);
    const nEquipo = totalMins / 90;
    const nTitular = player.starts_recent || 0;
    const mJugados = player.minutes_recent || 0;
    
    const densityTerm = Math.min(1.0, mJugados / (nEquipo * 90));
    const iph = 0.7 * (nTitular / nEquipo) + 0.3 * densityTerm;
    
    // Sigmoid function: pJuego = 1 / (1 + e^-10(IPH - 0.55))
    const pJuego = 1 / (1 + Math.exp(-10 * (iph - 0.55)));
    return pJuego;
  }
  if (teamMaxVal && teamMaxVal > 0) {
    return Math.min(1.0, (player.market_value_eur || 0) / teamMaxVal);
  }
  return 0.0;
}

export function calculateSClub(homeTeam, awayTeam, userPreferences) {
  const favClubs = userPreferences?.favoriteClubs || [];
  if (favClubs.length === 0) return 0.0;
  
  let xPartido = 0.0;
  const processTeam = (team) => {
    if (!team || !team.squad) return;
    const maxVal = getTeamMaxMarketValue(team);
    for (let i = 0; i < team.squad.length; i++) {
      const p = team.squad[i];
      if (p.club && favClubs.includes(p.club)) {
        xPartido += calculatePJuego(p, team.fifa_code, maxVal);
      }
    }
  };
  
  processTeam(homeTeam);
  processTeam(awayTeam);
  
  const Z_club = 5.0; 
  return Math.min(1.0, Math.log(1.0 + xPartido) / Math.log(1.0 + Z_club));
}

export function calculateSSel(homeCode, awayCode, userPreferences) {
  const favTeams = userPreferences?.favoriteTeams || [];
  if (favTeams.length === 0) return 0.0;
  
  const primary = favTeams[0];
  const secondary = favTeams.slice(1, 4);
  
  let I_p = 0;
  if (primary && (homeCode === primary || awayCode === primary)) {
    I_p = 1;
  }
  
  let n_m = 0;
  secondary.forEach(code => {
    if (code && (homeCode === code || awayCode === code)) {
      n_m++;
    }
  });
  
  if (I_p === 1) {
    return 1.0;
  }
  if (n_m > 0) {
    return Math.min(1.0, 0.5 * n_m);
  }
  return 0.0;
}

export function calculateSCluster(homeTeam, awayTeam, userPreferences) {
  const draftedClusters = userPreferences?.draftedClusters || [];
  if (draftedClusters.length === 0) return 0.0;
  
  // 1. Calculate centroids dynamically for each cluster in each active group
  const centroids = {};
  const groups = ['Goalkeepers', 'Centerbacks', 'Fullbacks', 'Midfielders', 'Wingers', 'Strikers'];
  
  groups.forEach(groupName => {
    const list = state.appData.clusters?.[groupName];
    if (!list) return;
    
    centroids[groupName] = {};
    const totals = {};
    const counts = {};
    
    list.forEach(p => {
      const cid = p.cluster_id;
      if (!p.position_vector) return;
      if (!totals[cid]) {
        totals[cid] = new Array(p.position_vector.length).fill(0);
        counts[cid] = 0;
      }
      for (let i = 0; i < p.position_vector.length; i++) {
        totals[cid][i] += p.position_vector[i];
      }
      counts[cid]++;
    });
    
    Object.keys(totals).forEach(cid => {
      centroids[groupName][cid] = totals[cid].map(sum => sum / counts[cid]);
    });
  });
  
  // Helper to calculate Euclidean distance
  const getDistance = (v1, v2) => {
    let sum = 0;
    const len = Math.min(v1.length, v2.length);
    for (let i = 0; i < len; i++) {
      const diff = v1[i] - v2[i];
      sum += diff * diff;
    }
    return Math.sqrt(sum);
  };
  
  let J_draft = 0.0;
  const a = 3.0; // Decay rate
  
  const processTeam = (team) => {
    if (!team || !team.squad) return;
    const maxVal = getTeamMaxMarketValue(team);
    
    team.squad.forEach(p => {
      const pRes = findClusterPlayer(p.name);
      if (pRes) {
        const { cp, groupName } = pRes;
        const isDrafted = draftedClusters.some(dc => dc.groupName === groupName && dc.clusterId == cp.cluster_id);
        if (isDrafted) {
          const centroid = centroids[groupName]?.[cp.cluster_id];
          if (centroid && cp.position_vector) {
            const dist = getDistance(cp.position_vector, centroid);
            const contribution = Math.max(0.0, Math.min(1.0, (Math.exp(-a * dist) - Math.exp(-a)) / (1.0 - Math.exp(-a))));
            const pJuego = calculatePJuego(p, team.fifa_code, maxVal);
            J_draft += contribution * pJuego;
          }
        }
      }
    });
  };
  
  processTeam(homeTeam);
  processTeam(awayTeam);
  
  // Normalize J_draft: using log1p and normalizing over Z_draft = 5.0
  return Math.min(1.0, Math.log1p(J_draft) / Math.log(1.0 + 5.0));
}

export function calculateSJug(homeTeam, awayTeam, userPreferences) {
  // Traditional favorite players logic
  const favPlayers = userPreferences?.favoritePlayers || [];
  if (favPlayers.length === 0) return 0.0;
  
  const resolvedFavs = [];
  favPlayers.forEach(fpName => {
    const res = findClusterPlayer(fpName);
    if (res) {
      resolvedFavs.push({
        name: fpName,
        vector: res.cp.position_vector,
        groupName: res.groupName
      });
    }
  });
  
  let J_d = 0.0;
  let J_s = 0.0;
  const epsilon = 0.1; 
  
  const processTeam = (team) => {
    if (!team || !team.squad) return;
    const maxVal = getTeamMaxMarketValue(team);
    
    for (let i = 0; i < team.squad.length; i++) {
      const p = team.squad[i];
      const pNameNorm = robustNormalise(p.name);
      const isDirectFav = favPlayers.some(fp => robustNormalise(fp) === pNameNorm);
      const pJuego = calculatePJuego(p, team.fifa_code, maxVal);
      
      if (isDirectFav) {
        J_d += pJuego;
      } else if (resolvedFavs.length > 0) {
        const pRes = findClusterPlayer(p.name);
        if (pRes) {
          let maxSim = 0.0;
          resolvedFavs.forEach(rf => {
            if (rf.groupName === pRes.groupName) {
              const v1 = rf.vector || [];
              const v2 = pRes.cp.position_vector || [];
              let distSq = 0.0;
              const len = Math.min(v1.length, v2.length);
              for (let k = 0; k < len; k++) {
                const diff = v1[k] - v2[k];
                distSq += diff * diff;
              }
              const dist = Math.sqrt(distSq);
              const sim = 1.0 / (dist + epsilon);
              if (sim > maxSim) maxSim = sim;
            }
          });
          J_s += maxSim * pJuego;
        }
      }
    }
  };
  
  processTeam(homeTeam);
  processTeam(awayTeam);
  
  const lambdaVal = 0.5;
  const term_d = Math.log1p(J_d) / Math.log(2.0);
  const term_s = lambdaVal * Math.log1p(J_s);
  const score = term_d + term_s;
  return Math.min(1.0, score);
}

export function calculatePlaystyleScore(vectorA, vectorB, vectorU, lambdaVal = 0.1) {
  const simA = calculateCosineSimilarity(vectorA, vectorU);
  const simB = calculateCosineSimilarity(vectorB, vectorU);

  const matchPrincipal = Math.max(simA, simB);
  const interaccion = Math.min(simA, simB) * lambdaVal;

  return matchPrincipal + interaccion;
}

export function calculateFriccionScore(match, teams) {
  if (match.home_team.is_placeholder || match.away_team.is_placeholder) return 5.0;

  const home = teams[match.home_team.fifa_code];
  const away = teams[match.away_team.fifa_code];
  if (!home || !away) return 5.0;

  const hParams = home.espectaculo_params || { drama_norm: 0.5 };
  const aParams = away.espectaculo_params || { drama_norm: 0.5 };

  const dramaMatch = ((hParams.drama_norm ?? 0.5) + (aParams.drama_norm ?? 0.5)) / 2;
  return parseFloat((1.0 + 9.0 * dramaMatch).toFixed(1));
}

export function calculateICEScore(match, teams) {
  if (match.home_team.is_placeholder || match.away_team.is_placeholder) {
    return 5.0; 
  }

  const home = teams[match.home_team.fifa_code];
  const away = teams[match.away_team.fifa_code];

  if (!home || !away) {
    return 5.0;
  }

  const hParams = home.espectaculo_params || { ocasiones_norm: 0.5, contra_norm: 0.5, drama_norm: 0.5, vuln_norm: 0.5 };
  const aParams = away.espectaculo_params || { ocasiones_norm: 0.5, contra_norm: 0.5, drama_norm: 0.5, vuln_norm: 0.5 };

  const alpha = ICE_CONFIG.alpha; 

  const ocMatch = (hParams.ocasiones_norm + aParams.ocasiones_norm) / 2;
  const caMatch = (hParams.contra_norm + aParams.contra_norm) / 2;
  const vulnMatch = ((hParams.vuln_norm !== undefined ? hParams.vuln_norm : 0.5) + (aParams.vuln_norm !== undefined ? aParams.vuln_norm : 0.5)) / 2;

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
  
  const homeEloBoost = homeStars > 0 ? 200 * (homeStars / (homeStars + 3)) : 0;
  const awayEloBoost = awayStars > 0 ? 200 * (awayStars / (awayStars + 3)) : 0;
  
  const rHome = homeEloBase + homeEloBoost;
  const rAway = awayEloBase + awayEloBoost;

  const rankingDiff = Math.abs(homeEloBase - awayEloBase);
  const pBrecha = ICE_CONFIG.P_MAX / (1 + Math.exp(-ICE_CONFIG.K_STEEPNESS * (rankingDiff - ICE_CONFIG.R_MID)));

  const gamma = ICE_CONFIG.gamma;
  const ice = ((ocMatch * (1 + gamma * vulnMatch)) + (alpha * caMatch)) * (1 - pBrecha);

  const ICE_min = ICE_CONFIG.ICE_min;
  const T = ICE_CONFIG.T_SCALE * (1.5 + alpha);
  let score = 1 + 9 * ((Math.max(ICE_min, Math.min(ice, T)) - ICE_min) / (T - ICE_min));
  
  const avgElo = (rHome + rAway) / 2;
  const qMatch = Math.max(0.60, Math.min(1.0, 0.60 + 0.40 * ((avgElo - 1400) / 700)));
  score = score * qMatch;

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
    const matchStakeMultiplier = (2 * mHome * mAway) / (mHome + mAway);
    
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

  const userPref = state.userPreferences || {};

  const w_ent = userPref.w_entretenimiento ?? 5;
  const w_tac = userPref.w_tactica ?? 5;
  const w_afec = userPref.w_afectivo ?? 5;
  
  const w_esp = userPref.w_espectaculo ?? 5;
  const w_fric = userPref.w_friccion ?? 5;

  const vectorU = tacticalVector || userPref.tacticalVector || { defensa: 0.0, posesion: 0.0, ritmo: 0.0, ancho: 0.0 };
  const isDefaultU = vectorU.defensa === 0 && vectorU.posesion === 0 && vectorU.ritmo === 0 && vectorU.ancho === 0;

  const hasFavTeams = Array.isArray(userPref.favoriteTeams) && userPref.favoriteTeams.length > 0;
  const hasFavClubs = Array.isArray(userPref.favoriteClubs) && userPref.favoriteClubs.length > 0;
  const hasFavPlayers = Array.isArray(userPref.favoritePlayers) && userPref.favoritePlayers.length > 0;
  const hasDraftedClusters = Array.isArray(userPref.draftedClusters) && userPref.draftedClusters.length > 0;

  // Compute dramaMatch normalized [0, 1]
  const hParams = home.espectaculo_params || { drama_norm: 0.5 };
  const aParams = away.espectaculo_params || { drama_norm: 0.5 };
  const dramaMatch = ((hParams.drama_norm ?? 0.5) + (aParams.drama_norm ?? 0.5)) / 2;

  // Activation and transformation for friction component (needed for UI display only)
  const frictionPreference = userPref.frictionPreference || 'indiferente';
  let x_fric = dramaMatch;
  if (frictionPreference === 'fair_play') {
    x_fric = 1.0 - dramaMatch;
  }
  const displayFriccionScore = 1.0 + 9.0 * x_fric;

  // Pre-calculate affective scores to see if this match has any relevant favorites
  const s_club = calculateSClub(home, away, userPref);
  const s_sel = calculateSSel(match.home_team.fifa_code, match.away_team.fifa_code, userPref);
  const s_jug = calculateSJug(home, away, userPref);
  
  const hasMatchAffective = s_club > 0 || s_sel > 0 || s_jug > 0;

  const spectacleScore = ice; 

  const vectorA = home.tactical_vector || { defensa: 0.0, posesion: 0.0, ritmo: 0.0, ancho: 0.0 };
  const vectorB = away.tactical_vector || { defensa: 0.0, posesion: 0.0, ritmo: 0.0, ancho: 0.0 };

  const s_style = isDefaultU ? spectacleScore : (() => {
    const rawPlaystyle = calculatePlaystyleScore(vectorA, vectorB, vectorU);
    const score = 10.0 * ((rawPlaystyle + 1.1) / 2.2);
    return Math.min(Math.max(score, 0.0), 10.0);
  })();

  const s_cluster = calculateSCluster(home, away, userPref);

  let playstyleScore = s_style;
  if (hasDraftedClusters) {
    const w_style = userPref.w_tactica_estilo ?? 5;
    const w_cluster = userPref.w_tactica_cluster ?? 5;
    const total_tactica_w = w_style + w_cluster;
    if (total_tactica_w > 0) {
      playstyleScore = (w_style * s_style + w_cluster * (s_cluster * 10.0)) / total_tactica_w;
    }
  }

  // 1. Pesos Macro normalizados (3 componentes principales):
  const w_sum = w_ent + w_tac + w_afec;
  const W_ent = w_sum > 0 ? w_ent / w_sum : 0.3333;
  const W_tec = w_sum > 0 ? w_tac / w_sum : 0.3333;
  const W_af = w_sum > 0 ? w_afec / w_sum : 0.3333;

  // 2. Micro componente de Entretenimiento (Espectáculo + Fricción):
  const w_ent_sub_sum = w_esp + w_fric;
  const x_ent = w_ent_sub_sum > 0 ? (w_esp * spectacleScore + w_fric * displayFriccionScore) / w_ent_sub_sum : spectacleScore;

  // 3. Componente Afectiva:
  const m_club = hasFavClubs ? 1 : 0;
  const m_sel = hasFavTeams ? 1 : 0;
  const m_jug = hasFavPlayers ? 1 : 0;

  const w_club_sub = userPref.w_afectivo_club ?? 3;
  const w_sel_sub = userPref.w_afectivo_seleccion ?? 4;
  const w_jug_sub = userPref.w_afectivo_jugador ?? 3;

  const sub_sum = (m_club * w_club_sub) + (m_sel * w_sel_sub) + (m_jug * w_jug_sub);
  let s_afectivo = 0.0;
  if (sub_sum > 0) {
    const x_af = ((m_club * w_club_sub * s_club) + (m_sel * w_sel_sub * s_sel) + (m_jug * w_jug_sub * s_jug)) / sub_sum;
    s_afectivo = x_af * 10.0;
  }

  // 4. Score Final: Norma L2 tridimensional con pesos estables
  const combinedScore = Math.sqrt(
    W_ent * Math.pow(x_ent, 2) +
    W_tec * Math.pow(playstyleScore, 2) +
    W_af * Math.pow(s_afectivo, 2)
  );

  match.spectacleScore = parseFloat(spectacleScore.toFixed(1));
  match.playstyleScore = parseFloat(playstyleScore.toFixed(1));
  match.friccionScore = parseFloat(displayFriccionScore.toFixed(1));

  match.scoreBreakdown = {
    w_sum,
    W_ent,
    W_tec,
    W_af,
    val_entretenimiento: parseFloat(x_ent.toFixed(1)),
    val_tactica: parseFloat(playstyleScore.toFixed(1)),
    val_afectivo: parseFloat(s_afectivo.toFixed(1)),
    entertainment: {
      w_esp,
      w_fric,
      val_espectaculo: parseFloat(spectacleScore.toFixed(1)),
      val_friccion: parseFloat(displayFriccionScore.toFixed(1))
    },
    tactical: {
      w_style: userPref.w_tactica_estilo ?? 5,
      w_cluster: hasDraftedClusters ? (userPref.w_tactica_cluster ?? 5) : 0,
      val_estilo: parseFloat(s_style.toFixed(1)),
      val_cluster: hasDraftedClusters ? parseFloat((s_cluster * 10.0).toFixed(1)) : 0
    },
    affective: {
      w_club: hasFavClubs ? w_club_sub : 0,
      w_sel: hasFavTeams ? w_sel_sub : 0,
      w_jug: hasFavPlayers ? w_jug_sub : 0,
      val_club: parseFloat((s_club * 10.0).toFixed(1)),
      val_sel: parseFloat((s_sel * 10.0).toFixed(1)),
      val_jug: parseFloat((s_jug * 10.0).toFixed(1))
    }
  };

  let score = combinedScore;
  const rawFriction = userPref.friction ?? 50;
  const fMultiplier = (Math.abs(rawFriction - 50) / 50) * 0.3;
  if (fMultiplier > 0) {
    const isCleanPlay = rawFriction > 50;
    const effect = isCleanPlay ? (0.5 - dramaMatch) : (dramaMatch - 0.5);
    const bonus = 2 * effect * fMultiplier;
    score += bonus;
  }

  return parseFloat(Math.min(10.0, Math.max(1.0, score)).toFixed(1));
}
