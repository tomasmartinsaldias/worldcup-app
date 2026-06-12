import { state, recalculateTournamentState } from './futstate.js';
import { calculateSmartScore } from './scoring.js';

/**
 * Maps survey slider values and question answers to userPreferences
 * that the scoring engine can consume.
 *
 * @param {Object} surveyResults - Raw data collected from the survey UI
 * @param {string} surveyResults.userType - 'casual' | 'intermedio' | 'fanatico'
 * @param {string|null} surveyResults.passion - Slider 0-100 (Impacto de la derrota)
 * @param {string|null} surveyResults.friction - Slider 0-100 (Patadas vs Fluido)
 * @param {string|null} surveyResults.goals - Slider 0-100 (Cerrado vs Festival)
 * @param {string|null} surveyResults.tactics - Slider 0-100 (DT vs Talento individual)
 * @param {string|null} surveyResults.q1_player_loyalty - 'none'|'less'|'always'
 * @param {string|null} surveyResults.q2_team_loyalty - 'spectacle'|'neutral'|'team_always'
 * @param {string[]} surveyResults.favoritePlayers - Player names
 * @param {string|null} surveyResults.favoriteTeam - Club name
 * @param {string[]} surveyResults.supportedNations - FIFA codes
 */
export function mapSurveyToPreferences(surveyResults) {
  const passion = parseInt(surveyResults.passion) || 50;
  const friction = parseInt(surveyResults.friction) || 50;
  const goals = parseInt(surveyResults.goals) || 50;
  const tactics = parseInt(surveyResults.tactics) || 50;
  const isCasual = surveyResults.userType === 'casual';

  // 1. Passion → w_afectivo (continuous mapping from 2.0 to 10.0)
  const w_afectivo = parseFloat((2.0 + 8.0 * (passion / 100)).toFixed(1));

  // 2. Friction → frictionPreference (discretized boundary) + w_friccion (continuous weight capped at 4.0)
  let frictionPreference = 'indiferente';
  if (friction < 45) {
    frictionPreference = 'trabado';
  } else if (friction > 55) {
    frictionPreference = 'fair_play';
  }
  const w_friccion = parseFloat((4.0 * (Math.abs(friction - 50) / 50)).toFixed(1));

  // 3. Goals → w_espectaculo (continuous mapping from 2.0 to 10.0)
  let w_espectaculo = 2.0 + 8.0 * (goals / 100);

  // 4. Q2 adjustments to espectaculo and seleccion weights (Restored)
  let w_afectivo_seleccion = 4.0;
  if (surveyResults.q2_team_loyalty === 'team_always') {
    w_afectivo_seleccion = 7.0;
    w_espectaculo = Math.max(1.0, w_espectaculo - 1.0);
  } else if (surveyResults.q2_team_loyalty === 'spectacle') {
    w_afectivo_seleccion = 2.0;
    w_espectaculo = Math.min(10.0, w_espectaculo + 1.0);
  }
  w_espectaculo = parseFloat(w_espectaculo.toFixed(1));

  // 4.5. Neutral Interest Slider -> w_entretenimiento (continuous mapping from 2.0 to 10.0)
  const neutralInterest = parseInt(surveyResults.neutralInterest) || 50;
  const w_entretenimiento = parseFloat((2.0 + 8.0 * (neutralInterest / 100)).toFixed(1));

  // 5. Q1 → w_afectivo_jugador (player loyalty)
  let w_afectivo_jugador = 3.0;
  if (surveyResults.q1_player_loyalty === 'always') {
    w_afectivo_jugador = 5.0;
  } else if (surveyResults.q1_player_loyalty === 'none') {
    w_afectivo_jugador = 1.0;
  }

  // 6. Tactics slider → w_tactica_estilo vs w_tactica_cluster
  let w_tactica_estilo = 5.0;
  let w_tactica_cluster = 5.0;
  let w_tactica = 5.0;

  if (!isCasual) {
    w_tactica = parseFloat((2.0 + 8.0 * (tactics / 100)).toFixed(1));
    w_tactica_estilo = parseFloat((10.0 * (1.0 - tactics / 100)).toFixed(1));
    w_tactica_cluster = parseFloat((10.0 * (tactics / 100)).toFixed(1));
  } else {
    // Casual: no clustering at all, no tactical weight at all
    w_tactica_cluster = 0.0;
    w_tactica = 0.0;
  }

  // Build preferences object
  const prefs = {
    w_entretenimiento,
    w_espectaculo,
    w_tactica,
    w_afectivo,
    w_friccion,
    frictionPreference,
    friction,
    w_tactica_estilo,
    w_tactica_cluster,
    w_afectivo_club: 3,
    w_afectivo_seleccion,
    w_afectivo_jugador,
    favoriteTeams: surveyResults.supportedNations ? surveyResults.supportedNations.map(nation => {
      if (!state.appData || !state.appData.teams) return nation;
      const teamEntry = Object.values(state.appData.teams).find(t => t.name.toLowerCase() === nation.toLowerCase());
      return teamEntry ? teamEntry.fifa_code : nation;
    }) : [],
    favoriteClubs: surveyResults.favoriteTeam ? [surveyResults.favoriteTeam] : [],
    favoritePlayers: surveyResults.favoritePlayers || [],
    draftedClusters: isCasual ? [] : (state.userPreferences?.draftedClusters || []),
    tacticalVector: state.userPreferences?.tacticalVector || { defensa: 0, posesion: 0, ritmo: 0, ancho: 0 },
    availableTimeRanges: surveyResults.availableTimeRanges || { morning: false, noon: false, afternoon: false, night: false },
  };

  if (window.customWeights) {
    Object.assign(prefs, window.customWeights);
  }

  return prefs;
}

/**
 * Generates ranked match recommendations using the scoring engine.
 * Iterates all valid matches, calculates SmartScore, and returns sorted list.
 *
 * @param {Object} userPreferences - Mapped preferences from mapSurveyToPreferences
 * @returns {Array} Sorted array of { match, score, explanation }
 */
export function generateRecommendations(userPreferences) {
  if (!state.appData || !state.appData.matches || !state.appData.teams) {
    console.error('[Recommender] appData not loaded');
    return [];
  }

  // Ensure tournament state (knockout matches, positions, ELOs) is fully updated based on simulated scores
  if (typeof recalculateTournamentState === 'function') {
    recalculateTournamentState();
  }

  // Apply preferences to state so scoring functions can read them
  Object.assign(state.userPreferences, userPreferences);

  const teams = state.appData.teams;
  const tacticalVector = userPreferences.tacticalVector;
  
  const timeRanges = userPreferences.availableTimeRanges || {
    morning: false, noon: false, afternoon: false, night: false
  };
  
  // If no time ranges selected, assume available all day
  const hasTimeConstraint = Object.values(timeRanges).some(v => v === true);

  const simulatedScores = (window.getSimulatedScores ? window.getSimulatedScores() : null) || {};

  // Helper to check if a stage is fully simulated
  const isStageFullySimulated = (startMatch, endMatch) => {
    for (let i = startMatch; i <= endMatch; i++) {
      if (simulatedScores[i] === undefined) return false;
    }
    return true;
  };

  const groupStageFullySimulated = isStageFullySimulated(1, 72);
  const r32FullySimulated = isStageFullySimulated(73, 88);
  const r16FullySimulated = isStageFullySimulated(89, 96);
  const qfFullySimulated = isStageFullySimulated(97, 100);
  const sfFullySimulated = isStageFullySimulated(101, 102);

  const scored = [];

  state.appData.matches.forEach(match => {
    const num = match.match_number;
    
    // Skip knockout rounds if preceding stage isn't fully simulated
    if (num >= 73 && num <= 88 && !groupStageFullySimulated) return;
    if (num >= 89 && num <= 96 && !r32FullySimulated) return;
    if (num >= 97 && num <= 100 && !r16FullySimulated) return;
    if (num >= 101 && num <= 102 && !qfFullySimulated) return;
    if (num >= 103 && num <= 104 && !sfFullySimulated) return;

    if (match.home_team.is_placeholder || match.away_team.is_placeholder) return;

    // Skip matches that are already simulated (played)
    if (simulatedScores[match.match_number] !== undefined) return;

    // Skip matches in the past (already played) based on user's current local time
    if (match.kickoff_at) {
      let dateStr = match.kickoff_at.replace(' ', 'T');
      if (dateStr.length === 22) dateStr += ':00'; // Append minutes to timezone if missing
      const dateObj = new Date(dateStr);
      if (!isNaN(dateObj.getTime()) && dateObj < new Date()) {
        return; // Skip matches whose kickoff time has already passed
      }
    }

    const score = calculateSmartScore(match, teams, tacticalVector);
    const explanation = getMatchExplanation(match, userPreferences, teams);
    
    // Check time availability
    let outOfSchedule = false;
    if (hasTimeConstraint && match.kickoff_at) {
      // Format "2026-07-03 18:00:00-04" -> "2026-07-03T18:00:00-04:00" for strict ISO parsing
      let dateStr = match.kickoff_at.replace(' ', 'T');
      if (dateStr.length === 22) dateStr += ':00'; // Append minutes to timezone if missing
      
      const dateObj = new Date(dateStr);
      if (!isNaN(dateObj.getTime())) {
        const h = dateObj.getHours(); // Local timezone hour
        let inRange = false;
        if (timeRanges.morning && h >= 8 && h < 12) inRange = true;
        if (timeRanges.noon && h >= 12 && h < 16) inRange = true;
        if (timeRanges.afternoon && h >= 16 && h < 20) inRange = true;
        if (timeRanges.night && (h >= 20 || h < 8)) inRange = true; // Night catches 20:00 to 07:59
        
        if (!inRange) {
          outOfSchedule = true;
        }
      }
    }

    scored.push({ match, score, explanation, outOfSchedule });
  });

  // Sort descending by score
  scored.sort((a, b) => b.score - a.score);

  return scored;
}

/**
 * Generates a human-readable explanation of WHY a match was recommended.
 * Checks which scoring component contributed most.
 */
function getMatchExplanation(match, userPref, teams) {
  const homeCode = match.home_team.fifa_code;
  const awayCode = match.away_team.fifa_code;
  const homeName = match.home_team.name;
  const awayName = match.away_team.name;

  // Check if user's favorite nation is playing
  const favTeams = userPref.favoriteTeams || [];
  if (favTeams.includes(homeCode)) return `Juega tu selección: ${homeName}`;
  if (favTeams.includes(awayCode)) return `Juega tu selección: ${awayName}`;

  // Check spectacle score
  const spectacle = match.spectacleScore || 0;
  const playstyle = match.playstyleScore || 0;
  const friccion = match.friccionScore || 0;

  // Check favorite players
  const favPlayers = userPref.favoritePlayers || [];
  if (favPlayers.length > 0) {
    const home = teams[homeCode];
    const away = teams[awayCode];
    const allSquad = [
      ...(home?.squad || []).map(p => p.name),
      ...(away?.squad || []).map(p => p.name)
    ];

    const normalise = s => s?.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim() || '';

    for (const fav of favPlayers) {
      const favNorm = normalise(fav);
      const found = allSquad.find(name => {
        const nameNorm = normalise(name);
        return nameNorm.includes(favNorm) || favNorm.includes(nameNorm);
      });
      if (found) return `Jugador favorito en cancha: ${fav}`;
    }
  }

  // Check favorite club players
  const favClubs = userPref.favoriteClubs || [];
  if (favClubs.length > 0) {
    const home = teams[homeCode];
    const away = teams[awayCode];
    let clubCount = 0;
    [home, away].forEach(team => {
      if (team?.squad) {
        team.squad.forEach(p => {
          if (p.club && favClubs.includes(p.club)) clubCount++;
        });
      }
    });
    if (clubCount > 0) return `${clubCount} jugador${clubCount > 1 ? 'es' : ''} de tu club favorito`;
  }

  // Fallback to dominant score component
  if (spectacle >= playstyle && spectacle >= friccion) {
    if (spectacle >= 7) return 'Partidazo de alto voltaje asegurado';
    if (spectacle >= 5) return 'Buen potencial de espectáculo';
    return 'Partido equilibrado';
  }

  if (playstyle >= spectacle && playstyle >= friccion) {
    return 'Estilo táctico afín a tu perfil';
  }

  if (friccion >= 5) {
    const pref = userPref.frictionPreference;
    if (pref === 'trabado') return 'Duelo intenso y fricción garantizada';
    if (pref === 'fair_play') return 'Juego limpio y técnica';
  }

  return 'Recomendado por tu perfil';
}
