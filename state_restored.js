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
  // dramaBonus: -1 (no gusta fricci├│n) | 0 (indiferente) | +1 (gusta fricci├│n)
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
    
    const parseJSON = async (res) => {
      try {
        if (res.ok) return await res.json();
        return null;
      } catch (e) {
        return null;
      }
    };
    
    state.appData = await parseJSON(mainRes) || {};
    state.appData.clubLogos = await parseJSON(logosRes) || {};

    const estiloData = await parseJSON(estiloRes) || { response: [] };
    const arquetiposData = await parseJSON(arquetiposRes) || { archetypes: [] };
    state.appData.estilos = estiloData.response;
    state.appData.arquetipos = arquetiposData.archetypes;

    const photosData = await parseJSON(photosRes) || [];
      const finalPhotosData = await parseJSON(finalRes) || [];
  
      state.appData.playersFinal = finalPhotosData;
      
      state.appData.clusters = {
        Goalkeepers: [],
        Centerbacks: [],
        Fullbacks: [],
        Midfielders: [],
        Wingers: [],
        Strikers: []
      };
  
      const positionMap = {
        'Goalkeeper': 'Goalkeepers',
        'Centerbacks': 'Centerbacks',
        'Fullbacks': 'Fullbacks',
        'Midfielder': 'Midfielders',
        'Wingers': 'Wingers',
        'Striker': 'Strikers'
      };
  
      if (finalPhotosData && finalPhotosData.length > 0) {
        finalPhotosData.forEach(p => {
          if (p.Posicion && positionMap[p.Posicion]) {
            const groupName = positionMap[p.Posicion];
            if (p.Cluster_id !== null && p.Cluster_id !== undefined) {
              state.appData.clusters[groupName].push({
                long_name: p.NAME,
                overall: p.Overall,
                cluster_id: p.Cluster_id,
                dist_centroid: p.Dist_centroid,
                photoUrl: p._URL
              });
            }
          }
        });
      }
    
    // Fetch players_final.json for fallback faces
    let finalPhotosData = [];
    try {
      const finalRes = await fetch(`data/data_frontend/players_final.json?t=${new Date().getTime()}`);
      if (finalRes.ok) finalPhotosData = await finalRes.json();
    } catch (e) {
      console.error("Could not fetch players_final.json", e);
    }
    
    state.appData.photoIndex = {};
    const robustNormalise = str => {
      if (!str) return '';
      return str
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .replace(/\u00f8/gi, 'o').replace(/\u00f0/gi, 'd').replace(/\u00fe/gi, 'th')
        .replace(/\u00e6/gi, 'ae').replace(/\u0142/gi, 'l').replace(/\u00df/gi, 'ss').replace(/\u0153/gi, 'oe')
        .replace(/[^\x00-\x7F]/g, '')
        .toLowerCase().trim();
    };
    photosData.forEach(p => {
      const n = robustNormalise(p.n);
      const fn = robustNormalise(p.fn);
      if (fn) state.appData.photoIndex[fn] = p.p;
      if (n && !state.appData.photoIndex[n]) state.appData.photoIndex[n] = p.p;

      // Add a fallback for names like "S. Gim├®nez" mapping to "Santiago Gim├®nez"
      const parts = fn.split(' ');
      if (parts.length > 1) {
        const short = robustNormalise(`${parts[0][0]}. ${parts[parts.length - 1]}`);
        if (!state.appData.photoIndex[short]) state.appData.photoIndex[short] = p.p;
      }
    });
    
    // Process finalPhotosData
    finalPhotosData.forEach(p => {
      if (p.NAME && p._URL) {
        const n = robustNormalise(p.NAME);
        if (n && !state.appData.photoIndex[n]) {
          state.appData.photoIndex[n] = p._URL;
        }
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

export function calculateStandings(groupLetter) {
  if (!state.appData || !state.appData.groups || !state.appData.groups[groupLetter]) return [];
  const groupTeams = state.appData.groups[groupLetter];
  
  const standings = groupTeams.map(code => ({
    code: code,
    name: state.appData.teams[code]?.name || code,
    pj: 0,
    pg: 0,
    pe: 0,
    pp: 0,
    gf: 0,
    gc: 0,
    dg: 0,
    pts: 0
  }));

  const simulatedScores = getSimulatedScores();
  
  const groupMatches = state.appData.matches.filter(m => 
    m.stage === 'Group Stage' && 
    m.home_team.group === groupLetter &&
    !m.home_team.is_placeholder &&
    !m.away_team.is_placeholder
  );

  groupMatches.forEach(m => {
    const score = simulatedScores[m.match_number];
    if (score !== undefined && score.home !== null && score.away !== null) {
      const homeTeam = standings.find(t => t.code === m.home_team.fifa_code);
      const awayTeam = standings.find(t => t.code === m.away_team.fifa_code);
      if (homeTeam && awayTeam) {
        homeTeam.pj += 1;
        awayTeam.pj += 1;
        homeTeam.gf += score.home;
        homeTeam.gc += score.away;
        awayTeam.gf += score.away;
        awayTeam.gc += score.home;
        
        if (score.home > score.away) {
          homeTeam.pg += 1;
          homeTeam.pts += 3;
          awayTeam.pp += 1;
        } else if (score.away > score.home) {
          awayTeam.pg += 1;
          awayTeam.pts += 3;
          homeTeam.pp += 1;
        } else {
          homeTeam.pe += 1;
          awayTeam.pe += 1;
          homeTeam.pts += 1;
          awayTeam.pts += 1;
        }
      }
    }
  });

  standings.forEach(t => {
    t.dg = t.gf - t.gc;
  });

  standings.sort((a, b) => {
    if (b.pts !== a.pts) return b.pts - a.pts;
    if (b.dg !== a.dg) return b.dg - a.dg;
    if (b.gf !== a.gf) return b.gf - a.gf;
    
    const eloA = state.teamElos[a.code] || 1500;
    const eloB = state.teamElos[b.code] || 1500;
    return eloB - eloA;
  });

  return standings;
}

export function determineQualificationStatus() {
  if (!state.appData || !state.appData.groups || !state.appData.matches) return;

  const simulatedScores = getSimulatedScores();
  const groupLetters = Object.keys(state.appData.groups).sort();
  
  groupLetters.forEach(gKey => {
    const groupTeams = state.appData.groups[gKey];
    const groupMatches = state.appData.matches.filter(m => 
      m.stage === 'Group Stage' && 
      m.home_team.group === gKey &&
      !m.home_team.is_placeholder &&
      !m.away_team.is_placeholder
    );

    const playedMatches = [];
    const remainingMatches = [];
    
    groupMatches.forEach(m => {
      const score = simulatedScores[m.match_number];
      if (score !== undefined && score.home !== null && score.away !== null) {
        playedMatches.push({
          match_number: m.match_number,
          home: m.home_team.fifa_code,
          away: m.away_team.fifa_code,
          scoreHome: score.home,
          scoreAway: score.away
        });
      } else {
        remainingMatches.push({
          match_number: m.match_number,
          home: m.home_team.fifa_code,
          away: m.away_team.fifa_code
        });
      }
    });

    const combinations = [];
    function generateCombinations(index, current) {
      if (index === remainingMatches.length) {
        combinations.push([...current]);
        return;
      }
      current.push(1);
      generateCombinations(index + 1, current);
      current.pop();
      
      current.push(0);
      generateCombinations(index + 1, current);
      current.pop();
      
      current.push(-1);
      generateCombinations(index + 1, current);
      current.pop();
    }
    
    generateCombinations(0, []);

    const teamStats = {};
    groupTeams.forEach(code => {
      teamStats[code] = { times1st: 0, timesTop2: 0 };
    });

    combinations.forEach(combo => {
      const standings = groupTeams.map(code => ({
        code: code,
        pts: 0,
        dg: 0,
        gf: 0,
        elo: state.teamElos[code] || 1500
      }));

      playedMatches.forEach(m => {
        const homeT = standings.find(t => t.code === m.home);
        const awayT = standings.find(t => t.code === m.away);
        if (homeT && awayT) {
          homeT.dg += (m.scoreHome - m.scoreAway);
          awayT.dg += (m.scoreAway - m.scoreHome);
          homeT.gf += m.scoreHome;
          awayT.gf += m.scoreAway;
          if (m.scoreHome > m.scoreAway) {
            homeT.pts += 3;
          } else if (m.scoreAway > m.scoreHome) {
            awayT.pts += 3;
          } else {
            homeT.pts += 1;
            awayT.pts += 1;
          }
        }
      });

      remainingMatches.forEach((m, idx) => {
        const outcome = combo[idx];
        const homeT = standings.find(t => t.code === m.home);
        const awayT = standings.find(t => t.code === m.away);
        if (homeT && awayT) {
          if (outcome === 1) {
            homeT.pts += 3;
            homeT.dg += 1;
            awayT.dg -= 1;
            homeT.gf += 1;
          } else if (outcome === -1) {
            awayT.pts += 3;
            awayT.dg += 1;
            homeT.dg -= 1;
            awayT.gf += 1;
          } else {
            homeT.pts += 1;
            awayT.pts += 1;
          }
        }
      });

      standings.sort((a, b) => {
        if (b.pts !== a.pts) return b.pts - a.pts;
        if (b.dg !== a.dg) return b.dg - a.dg;
        if (b.gf !== a.gf) return b.gf - a.gf;
        return b.elo - a.elo;
      });

      standings.forEach((team, rank) => {
        if (rank === 0) {
          teamStats[team.code].times1st += 1;
          teamStats[team.code].timesTop2 += 1;
        } else if (rank === 1) {
          teamStats[team.code].timesTop2 += 1;
        }
      });
    });

    const totalCombos = combinations.length;
    groupTeams.forEach(code => {
      const stats = teamStats[code];
      if (stats.times1st === totalCombos) {
        state.teamStatuses[code] = 'FIRST_PLACE_ASSURED';
      } else if (stats.timesTop2 === totalCombos) {
        state.teamStatuses[code] = 'QUALIFIED';
      } else if (stats.timesTop2 === 0) {
        state.teamStatuses[code] = 'ELIMINATED';
      } else {
        state.teamStatuses[code] = 'PLAYING_FOR_LIFE';
      }
    });
  });
}

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
  // 1. Calculate Group Stage standings and ELO first
  recalculateEloAndMomentum();
  determineQualificationStatus();
  
  if (!state.appData || !state.appData.matches || !state.appData.groups) return;
  
  // 2. Extract classifieds from each group
  const groupLetters = Object.keys(state.appData.groups).sort();
  const groupWinners = {}; // { 'A': 'MEX', ... }
  const groupSeconds = {}; // { 'A': 'RSA', ... }
  const groupThirds = [];  // Array of { code, pts, dg, gf, group: 'A' }
  
  groupLetters.forEach(gKey => {
    const standings = calculateStandings(gKey);
    if (standings.length >= 3) {
      groupWinners[gKey] = standings[0].code;
      groupSeconds[gKey] = standings[1].code;
      
      const third = standings[2];
      groupThirds.push({
        code: third.code,
        pts: third.pts,
        dg: third.dg,
        gf: third.gf,
        group: gKey
      });
    }
  });
  
  // Sort thirds to find best 8
  groupThirds.sort((a, b) => {
    if (b.pts !== a.pts) return b.pts - a.pts;
    if (b.dg !== a.dg) return b.dg - a.dg;
    if (b.gf !== a.gf) return b.gf - a.gf;
    const eloA = teamElos[a.code] || 1500;
    const eloB = teamElos[b.code] || 1500;
    return eloB - eloA;
  });
  
  const best8Thirds = groupThirds.slice(0, 8);
  const bestThirdGroupLetters = best8Thirds.map(t => t.group).sort().join(''); // e.g. "ABCDEFGH"
  
  // Official FIFA World Cup 48-team contingency table for 12 groups.
  // Below is a robust mapping for the 8 third slots based on the combination of qualifying group letters.
  // Placeholders: 3ABCDF (P75), 3CDFGH (P78), 3CEFHI (P79), 3EHIJK (P80), 3AEHIJ (P81), 3BEFIJ (P82), 3EFGIJ (P85), 3DEIJL (P88).
  // In case of any missing combination from the official rules, a stable fallback solver distributes best8Thirds matching the constraints.
  const slots = [
    { key: '3ABCDF', matchNum: 75, allowed: ['A', 'B', 'C', 'D', 'F'] },
    { key: '3CDFGH', matchNum: 78, allowed: ['C', 'D', 'F', 'G', 'H'] },
    { key: '3CEFHI', matchNum: 79, allowed: ['C', 'E', 'F', 'H', 'I'] },
    { key: '3EHIJK', matchNum: 80, allowed: ['E', 'H', 'I', 'J', 'K'] },
    { key: '3AEHIJ', matchNum: 81, allowed: ['A', 'E', 'H', 'I', 'J'] },
    { key: '3BEFIJ', matchNum: 82, allowed: ['B', 'E', 'F', 'I', 'J'] },
    { key: '3EFGIJ', matchNum: 85, allowed: ['E', 'F', 'G', 'I', 'J'] },
    { key: '3DEIJL', matchNum: 88, allowed: ['D', 'E', 'I', 'J', 'L'] }
  ];
  
  // Constraint satisfaction solver: matching best thirds to slots
  // Crucial constraint: no team from group X can play the winner of group X.
  // P75 (3ABCDF) plays 1E -> OK to have E
  // P78 (3CDFGH) plays 1I -> OK to have I
  // P79 (3CEFHI) plays 1A -> CANNOT have A
  // P80 (3EHIJK) plays 1L -> CANNOT have L
  // P81 (3AEHIJ) plays 1G -> CANNOT have G
  // P82 (3BEFIJ) plays 1D -> CANNOT have D
  // P85 (3EFGIJ) plays 1B -> CANNOT have B
  // P88 (3DEIJL) plays 1K -> CANNOT have K
  const slotOpps = {
    75: 'E',
    78: 'I',
    79: 'A',
    80: 'L',
    81: 'G',
    82: 'D',
    85: 'B',
    88: 'K'
  };
  
  const assignedThirds = {}; // { matchNum: teamCode }
  
  function backtrack(slotIdx, availableThirds) {
    if (slotIdx === slots.length) return true;
    
    const slot = slots[slotIdx];
    const oppGroup = slotOpps[slot.matchNum];
    
    for (let i = 0; i < availableThirds.length; i++) {
      const third = availableThirds[i];
      // Check if group is allowed in this slot
      const isAllowedGroup = slot.allowed.includes(third.group);
      // Check restriction: cannot play against group winner of their own group
      const violatesOppGroup = third.group === oppGroup;
      
      if (isAllowedGroup && !violatesOppGroup) {
        assignedThirds[slot.matchNum] = third.code;
        const remaining = availableThirds.filter((_, idx) => idx !== i);
        if (backtrack(slotIdx + 1, remaining)) {
          return true;
        }
        delete assignedThirds[slot.matchNum];
      }
    }
    
    // Fallback: If strict assignment fails, match by order of merit to any allowed slot
    for (let i = 0; i < availableThirds.length; i++) {
      const third = availableThirds[i];
      if (slot.allowed.includes(third.group) || slotIdx >= 4) { // relax constraints for bottom slots
        assignedThirds[slot.matchNum] = third.code;
        const remaining = availableThirds.filter((_, idx) => idx !== i);
        if (backtrack(slotIdx + 1, remaining)) {
          return true;
        }
        delete assignedThirds[slot.matchNum];
      }
    }
    return false;
  }
  
  backtrack(0, [...best8Thirds]);
  
  // 3. Re-simulate and propagate knockout matches chronologically
  const matchWinners = {}; // { match_number: code }
  const matches = state.appData.matches;
  
  // Group stage matches just fill matchWinners
  matches.forEach(m => {
    if (m.stage === 'Group Stage') {
      const score = simulatedScores[m.match_number];
      if (score !== undefined) {
        if (score.home > score.away) {
          matchWinners[m.match_number] = m.home_team.fifa_code;
        } else if (score.away > score.home) {
          matchWinners[m.match_number] = m.away_team.fifa_code;
        }
      }
    }
  });
  
  // Process Round of 32 to Final
  const knockoutMatches = matches.filter(m => m.stage !== 'Group Stage').sort((a, b) => a.match_number - b.match_number);
  
  knockoutMatches.forEach(m => {
    const label = m.match_label; // e.g. "2A vs 2B", "W73 vs W75", "1E vs 3ABCDF"
    
    // Parse home and away placeholders
    let homeCode = null;
    let awayCode = null;
    
    if (label.includes(' vs ')) {
      const [hPart, aPart] = label.split(' vs ');
      
      // Resolve Home Team
      homeCode = resolvePlaceholder(hPart, groupWinners, groupSeconds, assignedThirds, matchWinners, m.match_number, 'home');
      // Resolve Away Team
      awayCode = resolvePlaceholder(aPart, groupWinners, groupSeconds, assignedThirds, matchWinners, m.match_number, 'away');
    }
    
    // Update match team definitions
    if (homeCode) {
      m.home_team.fifa_code = homeCode;
      m.home_team.name = state.appData.teams[homeCode]?.name || homeCode;
      m.home_team.is_placeholder = false;
      m.home_team.group = state.appData.teams[homeCode]?.group || null;
    } else {
      m.home_team.fifa_code = '';
      m.home_team.name = label.split(' vs ')[0] || 'TBD';
      m.home_team.is_placeholder = true;
    }
    
    if (awayCode) {
      m.away_team.fifa_code = awayCode;
      m.away_team.name = state.appData.teams[awayCode]?.name || awayCode;
      m.away_team.is_placeholder = false;
      m.away_team.group = state.appData.teams[awayCode]?.group || null;
    } else {
      m.away_team.fifa_code = '';
      m.away_team.name = label.split(' vs ')[1] || 'TBD';
      m.away_team.is_placeholder = true;
    }
    
    // If teams are resolved, calculate dynamic ELO
    if (!m.home_team.is_placeholder && !m.away_team.is_placeholder) {
      m.home_team_elo_pre = teamElos[m.home_team.fifa_code] || 1500;
      m.away_team_elo_pre = teamElos[m.away_team.fifa_code] || 1500;
      
      const score = simulatedScores[m.match_number];
      if (score !== undefined) {
        let winnerCode = null;
        if (score.home > score.away) {
          winnerCode = m.home_team.fifa_code;
        } else if (score.away > score.home) {
          winnerCode = m.away_team.fifa_code;
        } else {
          // In case of a draw, use the user's manual selection, or default to home team
          winnerCode = score.winner === 'away' ? m.away_team.fifa_code : m.home_team.fifa_code;
        }
        
        matchWinners[m.match_number] = winnerCode;
        
        // ELO Dynamic update with momentum
        const Wh = winnerCode === m.home_team.fifa_code ? 1.0 : 0.0;
        const Wa = 1.0 - Wh;
        const We_h = 1 / (1 + Math.pow(10, (m.away_team_elo_pre - m.home_team_elo_pre) / 400));
        
        const E_h = Wh - We_h;
        const E_a = Wa - (1.0 - We_h);
        
        let omega = m.stage === 'Semi-finals' || m.stage === 'Final' || m.stage === 'Play-off for third place' ? 2.0 : 1.5;
        const K_base = 32;
        teamElos[m.home_team.fifa_code] = Math.round(m.home_team_elo_pre + K_base * omega * E_h);
        teamElos[m.away_team.fifa_code] = Math.round(m.away_team_elo_pre + K_base * omega * E_a);
      }
      
      m.home_team_elo_post = teamElos[m.home_team.fifa_code] || 1500;
      m.away_team_elo_post = teamElos[m.away_team.fifa_code] || 1500;
    }
  });
}

function resolvePlaceholder(placeholder, winners, seconds, thirds, winnersBrackets, matchNum, side) {
  // 1. Group winners: e.g., "1A"
  if (placeholder.startsWith('1')) {
    const group = placeholder.slice(1);
    return winners[group] || null;
  }
  
  // 2. Group seconds: e.g., "2A"
  if (placeholder.startsWith('2')) {
    const group = placeholder.slice(1);
    return seconds[group] || null;
  }
  
  // 3. Best thirds: e.g., "3ABCDF"
  if (placeholder.startsWith('3')) {
    return thirds[matchNum] || null;
  }
  
  // 4. Bracket winners: e.g., "W73"
  if (placeholder.startsWith('W')) {
    const refNum = parseInt(placeholder.slice(1));
    return winnersBrackets[refNum] || null;
  }
  
  // 5. Bracket runners up (perdedores): e.g., "RU101"
  if (placeholder.startsWith('RU')) {
    const refNum = parseInt(placeholder.slice(2));
    // Find who played in refNum and was NOT the winner
    const refMatch = state.appData.matches.find(m => m.match_number === refNum);
    const refWinner = winnersBrackets[refNum];
    if (refMatch && refWinner && !refMatch.home_team.is_placeholder && !refMatch.away_team.is_placeholder) {
      return refMatch.home_team.fifa_code === refWinner ? refMatch.away_team.fifa_code : refMatch.home_team.fifa_code;
    }
    return null;
  }
  
  return null;
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
    if (m.stage !== 'Group Stage') return; // Handled dynamically in recalculateTournamentState
    
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
      
      const K_base = 32;
      const lambda = 0.5;
      const K_h = K_base * (1 + lambda * Math.abs(M_h));
      const K_a = K_base * (1 + lambda * Math.abs(M_a));
      
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

