// state.js
let appData = null;
let activeTab = localStorage.getItem('activeTab') || 'recommender';
let selectedCountryCode = null;
let userPreferences = {
  favoriteTeam: '',
  matchStyle: 'all', // 'all', 'closed', 'chaotic'
  favoritePlayers: [],
  preferredTime: [], // array of 'morning', 'afternoon', 'evening'
  tacticalVector: { defensa: 0.0, posesion: 0.0, ritmo: 0.0, ancho: 0.0 },
  spectacleWeight: 0.5,
  // dramaBonus: -1 (no gusta fricción) | 0 (indiferente) | +1 (gusta fricción)
  // Controla si el FriccionScore suma o resta al SmartScore final
  dramaBonus: 0
};

export async function loadData() {
  try {
    const [mainRes, logosRes, estiloRes, arquetiposRes, photosRes, gkRes, cbRes, fbRes, midRes, wingRes, stRes] = await Promise.all([
      fetch(`data/wc2026_data.json?t=${new Date().getTime()}`),
      fetch(`data/club_logos.json?t=${new Date().getTime()}`),
      fetch(`data/estilos-de-juego/selecciones_estilo?t=${new Date().getTime()}`),
      fetch(`data/estilos-de-juego/arquetipos?t=${new Date().getTime()}`),
      fetch(`data/players_photos.json?t=${new Date().getTime()}`),
      fetch(`data/clustering_maps/kmeans_goalkeepers_arquetipos.json?t=${new Date().getTime()}`),
      fetch(`data/clustering_maps/kmeans_centerbacks_arquetipos.json?t=${new Date().getTime()}`),
      fetch(`data/clustering_maps/kmeans_fullbacks_arquetipos.json?t=${new Date().getTime()}`),
      fetch(`data/clustering_maps/kmeans_midfielders_arquetipos.json?t=${new Date().getTime()}`),
      fetch(`data/clustering_maps/kmeans_wingers_arquetipos.json?t=${new Date().getTime()}`),
      fetch(`data/clustering_maps/kmeans_strikers_arquetipos.json?t=${new Date().getTime()}`)
    ]);
    state.appData = await mainRes.json();
    state.appData.clubLogos = await logosRes.json();

    const estiloData = await estiloRes.json();
    const arquetiposData = await arquetiposRes.json();
    state.appData.estilos = estiloData.response;
    state.appData.arquetipos = arquetiposData.archetypes;

    const clusters = await Promise.all([gkRes.json(), cbRes.json(), fbRes.json(), midRes.json(), wingRes.json(), stRes.json()]);
    state.appData.clusters = {
      Goalkeepers: clusters[0],
      Centerbacks: clusters[1],
      Fullbacks: clusters[2],
      Midfielders: clusters[3],
      Wingers: clusters[4],
      Strikers: clusters[5]
    };

    const photosData = await photosRes.json();
    state.appData.photoIndex = {};
    const normalise = str => str ? str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim() : "";
    photosData.forEach(p => {
      const n = normalise(p.n);
      const fn = normalise(p.fn);
      if (fn) state.appData.photoIndex[fn] = p.p;
      if (n && !state.appData.photoIndex[n]) state.appData.photoIndex[n] = p.p;

      // Add a fallback for names like "S. Giménez" mapping to "Santiago Giménez"
      const parts = fn.split(' ');
      if (parts.length > 1) {
        const short = normalise(`${parts[0][0]}. ${parts[parts.length - 1]}`);
        if (!state.appData.photoIndex[short]) state.appData.photoIndex[short] = p.p;
      }
    });

    // Map estilos to teams
    mapTeamEstilos(state.appData);

    console.log('Main data loaded:', state.appData);
  } catch (err) {
    console.error('Error loading data:', err);
  }
}

function mapTeamEstilos(appData) {
  if (!appData || !appData.teams || !appData.estilos) return;
  const normalise = str => str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();

  const estiloMap = {};
  appData.estilos.forEach(item => {
    estiloMap[normalise(item.equipo)] = item;
  });

  Object.values(appData.teams).forEach(team => {
    const key = normalise(team.name);
    if (estiloMap[key]) {
      team.tactical_vector = estiloMap[key].vector;
      team.analisis_tactico = estiloMap[key].analisis_tactico;
    } else {
      // Fallback
      team.tactical_vector = { defensa: 0.0, posesion: 0.0, ritmo: 0.0, ancho: 0.0 };
      team.analisis_tactico = "";
    }
  });
}

let simulatedScores = JSON.parse(localStorage.getItem('simulatedScores') || '{}');
let teamElos = {};
let teamStatuses = {};

export function getSimulatedScores() {
  return simulatedScores;
}

export function saveSimulatedScore(matchNumber, homeScore, awayScore) {
  if (homeScore === null || awayScore === null || homeScore === "" || awayScore === "") {
    delete simulatedScores[matchNumber];
  } else {
    simulatedScores[matchNumber] = {
      home: parseInt(homeScore),
      away: parseInt(awayScore)
    };
  }
  localStorage.setItem('simulatedScores', JSON.stringify(simulatedScores));
  recalculateTournamentState();
}

export function clearAllSimulatedScores() {
  simulatedScores = {};
  localStorage.removeItem('simulatedScores');
  recalculateTournamentState();
}

export function recalculateTournamentState() {
  recalculateEloAndMomentum();
  determineQualificationStatus();
}

export function calculateStandings(groupLetter) {
  if (!state.appData || !state.appData.groups || !state.appData.groups[groupLetter]) {
    return [];
  }
  
  const teamCodes = state.appData.groups[groupLetter];
  const standings = teamCodes.map(code => {
    return {
      code,
      name: state.appData.teams[code]?.name || code,
      pj: 0, pg: 0, pe: 0, pp: 0, gf: 0, gc: 0, dg: 0, pts: 0
    };
  });
  
  const standingsMap = {};
  standings.forEach(t => standingsMap[t.code] = t);
  
  const matches = state.appData.matches.filter(m => 
    m.stage === 'Group Stage' && 
    m.home_team.group === groupLetter && 
    !m.home_team.is_placeholder && 
    !m.away_team.is_placeholder
  );
  
  matches.forEach(m => {
    const score = simulatedScores[m.match_number];
    if (score !== undefined) {
      const h = standingsMap[m.home_team.fifa_code];
      const a = standingsMap[m.away_team.fifa_code];
      if (h && a) {
        h.pj++;
        a.pj++;
        h.gf += score.home;
        h.gc += score.away;
        a.gf += score.away;
        a.gc += score.home;
        h.dg = h.gf - h.gc;
        a.dg = a.gf - a.gc;
        if (score.home > score.away) {
          h.pg++;
          h.pts += 3;
          a.pp++;
        } else if (score.home < score.away) {
          a.pg++;
          a.pts += 3;
          h.pp++;
        } else {
          h.pe++;
          h.pts += 1;
          a.pe++;
          a.pts += 1;
        }
      }
    }
  });
  
  standings.sort((a, b) => {
    if (b.pts !== a.pts) return b.pts - a.pts;
    if (b.dg !== a.dg) return b.dg - a.dg;
    if (b.gf !== a.gf) return b.gf - a.gf;
    const eloA = teamElos[a.code] || 1500;
    const eloB = teamElos[b.code] || 1500;
    if (eloB !== eloA) return eloB - eloA;
    return a.name.localeCompare(b.name);
  });
  
  return standings;
}

export function determineQualificationStatus() {
  if (!state.appData || !state.appData.groups) return;
  
  teamStatuses = {};
  const groupLetters = Object.keys(state.appData.groups);
  
  groupLetters.forEach(gLetter => {
    const teamCodes = state.appData.groups[gLetter];
    const groupMatches = state.appData.matches.filter(m => 
      m.stage === 'Group Stage' && 
      m.home_team.group === gLetter && 
      !m.home_team.is_placeholder && 
      !m.away_team.is_placeholder
    );
    
    const played = [];
    const unplayed = [];
    groupMatches.forEach(m => {
      if (simulatedScores[m.match_number] !== undefined) {
        played.push({
          match_number: m.match_number,
          home: m.home_team.fifa_code,
          away: m.away_team.fifa_code,
          goals_home: simulatedScores[m.match_number].home,
          goals_away: simulatedScores[m.match_number].away
        });
      } else {
        unplayed.push({
          home: m.home_team.fifa_code,
          away: m.away_team.fifa_code
        });
      }
    });
    
    const teamStats = {};
    teamCodes.forEach(code => {
      teamStats[code] = {
        ranks: { 1: 0, 2: 0, 3: 0, 4: 0 },
        maxPointsIn3rd: -1
      };
    });
    
    const k = unplayed.length;
    const totalComb = Math.pow(3, k);
    
    for (let c = 0; c < totalComb; c++) {
      const tempPlayed = [...played];
      let tempVal = c;
      for (let i = 0; i < k; i++) {
        const outcome = tempVal % 3;
        tempVal = Math.floor(tempVal / 3);
        
        let gh = 0, ga = 0;
        if (outcome === 0) { gh = 2; ga = 0; }
        else if (outcome === 1) { gh = 1; ga = 1; }
        else { gh = 0; ga = 2; }
        
        tempPlayed.push({
          home: unplayed[i].home,
          away: unplayed[i].away,
          goals_home: gh,
          goals_away: ga
        });
      }
      
      const standings = teamCodes.map(code => ({
        code,
        name: state.appData.teams[code]?.name || code,
        pts: 0, dg: 0, gf: 0
      }));
      
      const stMap = {};
      standings.forEach(t => stMap[t.code] = t);
      
      tempPlayed.forEach(m => {
        const h = stMap[m.home];
        const a = stMap[m.away];
        if (h && a) {
          h.gf += m.goals_home;
          h.gc = (h.gc || 0) + m.goals_away;
          a.gf += m.goals_away;
          a.gc = (a.gc || 0) + m.goals_home;
          h.dg = h.gf - h.gc;
          a.dg = a.gf - a.gc;
          if (m.goals_home > m.goals_away) {
            h.pts += 3;
          } else if (m.goals_home < m.goals_away) {
            a.pts += 3;
          } else {
            h.pts += 1;
            a.pts += 1;
          }
        }
      });
      
      standings.sort((a, b) => {
        if (b.pts !== a.pts) return b.pts - a.pts;
        if (b.dg !== a.dg) return b.dg - a.dg;
        if (b.gf !== a.gf) return b.gf - a.gf;
        const eloA = teamElos[a.code] || 1500;
        const eloB = teamElos[b.code] || 1500;
        return eloB - eloA;
      });
      
      standings.forEach((t, index) => {
        const rank = index + 1;
        teamStats[t.code].ranks[rank]++;
        if (rank === 3) {
          teamStats[t.code].maxPointsIn3rd = Math.max(teamStats[t.code].maxPointsIn3rd, t.pts);
        }
      });
    }
    
    teamCodes.forEach(code => {
      const stats = teamStats[code];
      const always1 = stats.ranks[1] === totalComb;
      const alwaysTop2 = (stats.ranks[1] + stats.ranks[2]) === totalComb;
      const always4 = stats.ranks[4] === totalComb;
      const alwaysBottom = always4 || ((stats.ranks[3] + stats.ranks[4]) === totalComb && stats.maxPointsIn3rd < 3);
      
      if (always1) {
        teamStatuses[code] = 'FIRST_PLACE_ASSURED';
      } else if (alwaysTop2) {
        teamStatuses[code] = 'QUALIFIED';
      } else if (alwaysBottom) {
        teamStatuses[code] = 'ELIMINATED';
      } else {
        teamStatuses[code] = 'PLAYING_FOR_LIFE';
      }
    });
  });
}

export function recalculateEloAndMomentum() {
  if (!state.appData || !state.appData.teams || !state.appData.matches) return;
  
  teamElos = {};
  const teamMomentums = {};
  
  Object.keys(state.appData.teams).forEach(code => {
    const t = state.appData.teams[code];
    teamElos[code] = t.metrics?.elo_rating || 1500;
    teamMomentums[code] = 0.0;
  });
  
  const matches = [...state.appData.matches].sort((a, b) => a.match_number - b.match_number);
  
  matches.forEach(m => {
    if (m.home_team.is_placeholder || m.away_team.is_placeholder) return;
    
    const hCode = m.home_team.fifa_code;
    const aCode = m.away_team.fifa_code;
    
    m.home_team_elo_pre = teamElos[hCode] || 1500;
    m.away_team_elo_pre = teamElos[aCode] || 1500;
    
    const score = simulatedScores[m.match_number];
    if (score !== undefined) {
      const hs = score.home;
      const as = score.away;
      
      const Wh = hs > as ? 1.0 : (hs === as ? 0.5 : 0.0);
      const Wa = 1.0 - Wh;
      
      const R_h = m.home_team_elo_pre;
      const R_a = m.away_team_elo_pre;
      
      const We_h = 1 / (1 + Math.pow(10, (R_a - R_h) / 400));
      const We_a = 1.0 - We_h;
      
      const E_h = Wh - We_h;
      const E_a = Wa - We_a;
      
      const alpha = 0.4;
      const M_h = alpha * E_h + (1 - alpha) * (teamMomentums[hCode] || 0.0);
      const M_a = alpha * E_a + (1 - alpha) * (teamMomentums[aCode] || 0.0);
      teamMomentums[hCode] = M_h;
      teamMomentums[aCode] = M_a;
      
      let omega = 1.0;
      if (m.stage === 'Group Stage') {
        omega = 1.0;
      } else if (m.stage === 'Semi-finals' || m.stage === 'Final' || m.stage === 'Play-off for third place') {
        omega = 2.0;
      } else {
        omega = 1.5;
      }
      
      const K_base = 32;
      const lambda = 0.5;
      const K_h = K_base * omega * (1 + lambda * Math.abs(M_h));
      const K_a = K_base * omega * (1 + lambda * Math.abs(M_a));
      
      teamElos[hCode] = Math.round(R_h + K_h * E_h);
      teamElos[aCode] = Math.round(R_a + K_a * E_a);
    }
    
    m.home_team_elo_post = teamElos[hCode] || 1500;
    m.away_team_elo_post = teamElos[aCode] || 1500;
  });
}

export const state = {
  get appData() { return appData; },
  set appData(val) { appData = val; },
  get activeTab() { return activeTab; },
  set activeTab(val) {
    activeTab = val;
    localStorage.setItem('activeTab', val);
  },
  get selectedCountryCode() { return selectedCountryCode; },
  set selectedCountryCode(val) { selectedCountryCode = val; },
  get userPreferences() { return userPreferences; },
  set userPreferences(val) { userPreferences = val; },
  get teamElos() { return teamElos; },
  get teamStatuses() { return teamStatuses; }
};
