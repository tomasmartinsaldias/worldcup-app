// Mundial 2026 – Match Recommender & Squad Analytics Client Logic

let appData = null;
let activeTab = 'recommender';
let selectedCountryCode = null;

// Formula for Match Recommender interest score (0 to 10)
function calculateSmartScore(match, teams) {
  if (match.home_team.is_placeholder || match.away_team.is_placeholder) {
    return 5.0; // default for playoff TBD matches
  }
  
  const home = teams[match.home_team.fifa_code];
  const away = teams[match.away_team.fifa_code];
  
  if (!home || !away || !home.metrics || !away.metrics) {
    return 6.0;
  }
  
  // 1. Squad Value (0 to 2.5 points)
  const combVal = (home.metrics.market_value_eur || 0) + (away.metrics.market_value_eur || 0);
  const valScore = Math.min((combVal / 850.0) * 2.5, 2.5); // Max points at 850M+ combined
  
  // 2. Global Popularity (0 to 2.0 points)
  const avgPop = ((home.metrics.global_popularity_score || 50) + (away.metrics.global_popularity_score || 50)) / 2;
  const popScore = (avgPop / 100.0) * 2.0;
  
  // 3. Offensive Style (xG) (0 to 1.5 points)
  const avgXg = ((home.metrics.recent_xg_avg || 1.1) + (away.metrics.recent_xg_avg || 1.1)) / 2;
  const xgScore = Math.min((avgXg / 2.0) * 1.5, 1.5); // Max points at 2.0 xG
  
  // 4. Recent Performance / Current Form (0 to 1.5 points)
  const avgEff = ((home.metrics.efficiency_score_avg || 0.19) + (away.metrics.efficiency_score_avg || 0.19)) / 2;
  const effScore = Math.min((avgEff / 0.50) * 1.5, 1.5); // Max points at 0.50 average efficiency
  
  // 5. Historical Card/Friction Intensity (0 to 1.0 points)
  const combCards = ((home.metrics.cards_per_match_avg || 1.3) + (away.metrics.cards_per_match_avg || 1.3)) / 2;
  const cardsScore = Math.min((combCards / 2.4) * 1.0, 1.0); // Max points at 2.4 cards per match
  
  // 6. Star Player count (0 to 1.0 points)
  const homeStars = home.squad ? home.squad.filter(p => p.is_star_player).length : 0;
  const awayStars = away.squad ? away.squad.filter(p => p.is_star_player).length : 0;
  const starScore = Math.min(((homeStars + awayStars) / 8.0) * 1.0, 1.0); // Max points at 8 stars
  
  // Stage Bonus (0.5 for knockout)
  const stageBonus = (match.stage && match.stage !== 'Group Stage') ? 0.5 : 0;
  
  let finalScore = valScore + popScore + xgScore + effScore + cardsScore + starScore + stageBonus;
  finalScore = Math.min(Math.max(finalScore, 1.0), 10.0);
  return parseFloat(finalScore.toFixed(1));
}

// Format flags urls
function getFlagUrl(fifaCode) {
  if (!fifaCode) return '';
  // Fallback map for local assets or custom flag mapping
  return `https://images.tomas.me/flags/${fifaCode.toLowerCase()}.png`; 
}

// Fallback flag generator (visual text box)
function createFlagElement(team) {
  if (team.is_placeholder) {
    return `<div class="team-flag-placeholder"><i class="fa-solid fa-hourglass-half"></i></div>`;
  }
  // Try loading real flag image, fallback to placeholder if error
  const code = team.fifa_code;
  const flagUrl = `https://flagcdn.com/w40/${getCountryIsoCode(code)}.png`;
  return `<img src="${flagUrl}" class="team-flag-real" onerror="this.outerHTML='<div class=team-flag-placeholder>${code}</div>'">`;
}

// Mapear FIFA Code a ISO 3166-1 alpha-2 para flagcdn
function getCountryIsoCode(fifaCode) {
  const mapping = {
    'ARG': 'ar', 'BRA': 'br', 'FRA': 'fr', 'ENG': 'gb-eng', 'ESP': 'es', 'GER': 'de', 'POR': 'pt',
    'URU': 'uy', 'NED': 'nl', 'CRO': 'hr', 'JPN': 'jp', 'USA': 'us', 'MEX': 'mx', 'MAR': 'ma',
    'COL': 'co', 'BEL': 'be', 'NOR': 'no', 'SEN': 'sn', 'EGY': 'eg', 'SWE': 'se', 'KOR': 'kr',
    'TUR': 'tr', 'SUI': 'ch', 'CAN': 'ca', 'ECU': 'ec', 'AUT': 'at', 'ALG': 'dz', 'CIV': 'ci',
    'SCO': 'gb-sct', 'AUS': 'au', 'GHA': 'gh', 'KSA': 'sa', 'PAR': 'py', 'CZE': 'cz', 'COD': 'cd',
    'BIH': 'ba', 'CPV': 'cv', 'TUN': 'tn', 'IRQ': 'iq', 'RSA': 'za', 'UZB': 'uz', 'QAT': 'qa',
    'NZL': 'nz', 'JOR': 'jo', 'PAN': 'pa', 'HAI': 'ht', 'CUR': 'cw', 'POL': 'pl', 'SRB': 'rs',
    'CMR': 'cm', 'CRC': 'cr', 'DEN': 'dk', 'WAL': 'gb-wls'
  };
  return mapping[fifaCode] || 'un';
}

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  setupTabListeners();
  loadData();
  
  // Filter and Search Listeners
  document.getElementById('search-matches').addEventListener('input', filterMatches);
  document.getElementById('filter-stage').addEventListener('change', filterMatches);
  document.getElementById('filter-region').addEventListener('change', filterMatches);
  document.getElementById('sort-matches').addEventListener('change', filterMatches);
  
  document.getElementById('search-teams').addEventListener('input', filterTeams);
  document.getElementById('back-to-countries-btn').addEventListener('click', closeSquadDetails);
  
  // Modal Close Listeners
  document.getElementById('close-modal-btn').addEventListener('click', closeModal);
  document.getElementById('h2h-modal').addEventListener('click', (e) => {
    if (e.target.id === 'h2h-modal') closeModal();
  });
});

// Tab Switching Lógic
function setupTabListeners() {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      switchTab(targetTab);
    });
  });
  
  document.getElementById('app-logo').addEventListener('click', (e) => {
    e.preventDefault();
    switchTab('recommender');
  });
}

function switchTab(tabName) {
  activeTab = tabName;
  
  // Update nav buttons
  document.querySelectorAll('.nav-btn').forEach(btn => {
    if (btn.getAttribute('data-tab') === tabName) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
  
  // Update sections visibility
  document.querySelectorAll('.tab-panel').forEach(panel => {
    panel.classList.remove('active');
  });
  
  const squadDetailsView = document.getElementById('squad-details-view');
  squadDetailsView.classList.remove('active');
  
  if (tabName === 'squads' && selectedCountryCode !== null) {
    squadDetailsView.classList.add('active');
  } else {
    const targetPanel = document.getElementById(`tab-${tabName}`);
    if (targetPanel) targetPanel.classList.add('active');
  }
}

// Load dataset
async function loadData() {
  try {
    const response = await fetch('../data/wc2026_data.json');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    appData = await response.json();
    
    // Precalculate Recommender Scores
    appData.matches.forEach(m => {
      m.smartScore = calculateSmartScore(m, appData.teams);
    });
    
    // Sort matches originally by smartScore descending
    sortMatchesList('interest-desc');
    
    // Render everything
    renderMatches();
    renderGroups();
    renderCountries();
    renderUnresolved();
    
  } catch (error) {
    console.error("No se pudieron cargar los datos del Mundial:", error);
    document.getElementById('matches-container').innerHTML = `
      <div class="no-history-msg" style="color: var(--accent-red)">
        <i class="fa-solid fa-circle-exclamation" style="font-size: 2rem; margin-bottom: 1rem;"></i><br>
        Error al cargar los datos en tiempo real.<br>
        Asegúrate de ejecutar primero la ingesta de datos con "populate_data.py" y exportar con "export_to_json.py".
      </div>`;
  }
}

// Sorting logic
function sortMatchesList(criterion) {
  if (!appData || !appData.matches) return;
  
  if (criterion === 'interest-desc') {
    appData.matches.sort((a, b) => b.smartScore - a.smartScore || a.match_number - b.match_number);
  } else if (criterion === 'match-asc') {
    appData.matches.sort((a, b) => a.match_number - b.match_number);
  } else if (criterion === 'value-desc') {
    appData.matches.sort((a, b) => {
      const vA = getCombinedValue(a);
      const vB = getCombinedValue(b);
      return vB - vA || a.match_number - b.match_number;
    });
  } else if (criterion === 'cards-desc') {
    appData.matches.sort((a, b) => {
      const cA = getCombinedCards(a);
      const cB = getCombinedCards(b);
      return cB - cA || a.match_number - b.match_number;
    });
  }
}

function getCombinedValue(match) {
  if (match.home_team.is_placeholder || match.away_team.is_placeholder) return 0;
  const home = appData.teams[match.home_team.fifa_code];
  const away = appData.teams[match.away_team.fifa_code];
  return ((home?.metrics?.market_value_eur || 0) + (away?.metrics?.market_value_eur || 0));
}

function getCombinedCards(match) {
  if (match.home_team.is_placeholder || match.away_team.is_placeholder) return 0;
  const home = appData.teams[match.home_team.fifa_code];
  const away = appData.teams[match.away_team.fifa_code];
  return ((home?.metrics?.cards_per_match_avg || 1.3) + (away?.metrics?.cards_per_match_avg || 1.3));
}

// 1. Render Matches List
function renderMatches() {
  const container = document.getElementById('matches-container');
  if (!appData || !appData.matches) return;
  
  const searchVal = document.getElementById('search-matches').value.toLowerCase();
  const stageFilter = document.getElementById('filter-stage').value;
  const regionFilter = document.getElementById('filter-region').value;
  
  // Filter matches
  const filtered = appData.matches.filter(m => {
    // Search filter
    const matchesSearch = 
      m.match_label.toLowerCase().includes(searchVal) ||
      m.home_team.name.toLowerCase().includes(searchVal) ||
      m.away_team.name.toLowerCase().includes(searchVal) ||
      (m.stadium && m.stadium.venue_name.toLowerCase().includes(searchVal)) ||
      (m.stadium && m.stadium.city_name.toLowerCase().includes(searchVal)) ||
      (m.home_team.group && `grupo ${m.home_team.group.toLowerCase()}`.includes(searchVal));
      
    // Stage filter
    let matchesStage = true;
    if (stageFilter === 'Group Stage') {
      matchesStage = m.stage === 'Group Stage';
    } else if (stageFilter === 'Knockout') {
      matchesStage = m.stage !== 'Group Stage';
    }
    
    // Region filter
    let matchesRegion = true;
    if (regionFilter !== 'all' && m.stadium) {
      matchesRegion = m.stadium.region_cluster === regionFilter;
    }
    
    return matchesSearch && matchesStage && matchesRegion;
  });
  
  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="no-history-msg" style="grid-column: 1 / -1;">
        No se encontraron partidos para los criterios seleccionados.
      </div>`;
    return;
  }
  
  container.innerHTML = '';
  filtered.forEach(m => {
    const card = document.createElement('div');
    card.className = 'match-card';
    card.addEventListener('click', () => openH2HModal(m));
    
    // Combined squad value
    const combVal = getCombinedValue(m);
    const combValStr = combVal > 0 ? `${combVal.toFixed(1)}M€` : 'N/A';
    
    // Star badge based on smartScore
    let interestClass = 'low-interest';
    if (m.smartScore >= 8.0) interestClass = 'high-interest';
    else if (m.smartScore >= 6.0) interestClass = 'medium-interest';
    
    // Count injured players in squad
    let injuredCount = 0;
    if (!m.home_team.is_placeholder) {
      injuredCount += appData.teams[m.home_team.fifa_code]?.squad.filter(p => p.is_injured).length || 0;
    }
    if (!m.away_team.is_placeholder) {
      injuredCount += appData.teams[m.away_team.fifa_code]?.squad.filter(p => p.is_injured).length || 0;
    }
    
    const flagHome = createFlagElement(m.home_team);
    const flagAway = createFlagElement(m.away_team);
    
    const groupLabel = m.home_team.group ? `Grupo ${m.home_team.group}` : 'Eliminatoria';
    
    card.innerHTML = `
      <div class="match-card-header">
        <span class="match-badge">Partido #${m.match_number} &bull; ${m.stage}</span>
        <span class="match-date-time"><i class="fa-regular fa-clock"></i> ${formatKickoff(m.kickoff_at)}</span>
      </div>
      
      <div class="match-teams">
        <div class="team-row">
          ${flagHome}
          <span class="team-name ${m.home_team.is_placeholder ? 'placeholder-name' : ''}">${m.home_team.name}</span>
        </div>
        <div class="team-row">
          ${flagAway}
          <span class="team-name ${m.away_team.is_placeholder ? 'placeholder-name' : ''}">${m.away_team.name}</span>
        </div>
      </div>
      
      <div class="interest-indicator">
        <div class="interest-ring ${interestClass}">${m.smartScore}</div>
        <div class="interest-label">Recomendado</div>
      </div>
      
      <div class="match-metrics-preview">
        ${combVal > 0 ? `
          <div class="metric-pill value" title="Valor de plantilla combinado">
            <i class="fa-solid fa-coins"></i> ${combValStr}
          </div>` : ''}
        ${!m.home_team.is_placeholder && !m.away_team.is_placeholder ? `
          <div class="metric-pill cards" title="Tarjetas amarillas/rojas promedio combinadas">
            <i class="fa-solid fa-copy"></i> Hist. Fricción: ${getCombinedCards(m).toFixed(2)}
          </div>` : ''}
        ${injuredCount > 0 ? `
          <div class="metric-pill injured" title="Jugadores lesionados o bajas confirmadas">
            <i class="fa-solid fa-user-slash"></i> Bajas: ${injuredCount}
          </div>` : ''}
      </div>
      
      <div class="match-venue">
        <i class="fa-solid fa-location-dot"></i>
        <span>${m.stadium ? `${m.stadium.venue_name}, ${m.stadium.city_name} (${m.stadium.region_cluster})` : 'Estadio TBD'}</span>
      </div>
    `;
    
    container.appendChild(card);
  });
}

function filterMatches() {
  const sortSelect = document.getElementById('sort-matches').value;
  sortMatchesList(sortSelect);
  renderMatches();
}

function formatKickoff(isoStr) {
  if (!isoStr) return 'TBD';
  try {
    const d = new Date(isoStr);
    return d.toLocaleString('es-ES', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) + ' hs';
  } catch(e) {
    return isoStr;
  }
}

// 2. Render Groups Tab
function renderGroups() {
  const container = document.getElementById('groups-container');
  if (!appData || !appData.groups) return;
  
  container.innerHTML = '';
  
  // Groups are A to L
  const sortedGroupKeys = Object.keys(appData.groups).sort();
  
  sortedGroupKeys.forEach(gKey => {
    const card = document.createElement('div');
    card.className = 'group-card';
    
    let teamItemsHtml = '';
    appData.groups[gKey].forEach(code => {
      const t = appData.teams[code];
      if (t) {
        const flag = createFlagElement(t);
        const mval = t.metrics?.market_value_eur;
        const valText = mval ? `${mval.toFixed(1)}M€` : 'N/A';
        teamItemsHtml += `
          <div class="group-team-item" onclick="openCountrySquad('${code}')">
            <div class="group-team-left">
              ${flag}
              <span>${t.name}</span>
            </div>
            <div class="group-team-value" title="Valor del plantel probable">${valText}</div>
          </div>
        `;
      }
    });
    
    card.innerHTML = `
      <div class="group-header">
        <span>Grupo ${gKey}</span>
        <i class="fa-solid fa-folder-open" style="font-size: 0.95rem; color: var(--text-muted)"></i>
      </div>
      <div class="group-teams-list">
        ${teamItemsHtml}
      </div>
    `;
    
    container.appendChild(card);
  });
}

// 3. Render Countries / Squads Selection Tab
function renderCountries() {
  const container = document.getElementById('countries-container');
  if (!appData || !appData.teams) return;
  
  const searchVal = document.getElementById('search-teams').value.toLowerCase();
  
  // Filter real teams
  const filtered = Object.values(appData.teams).filter(t => {
    if (t.is_placeholder) return false;
    
    const searchMatch = 
      t.name.toLowerCase().includes(searchVal) ||
      t.fifa_code.toLowerCase().includes(searchVal) ||
      (t.group && `grupo ${t.group.toLowerCase()}`.includes(searchVal));
      
    return searchMatch;
  });
  
  // Sort alphabetically by name
  filtered.sort((a, b) => a.name.localeCompare(b.name));
  
  if (filtered.length === 0) {
    container.innerHTML = `<div class="no-history-msg">No se encontraron selecciones.</div>`;
    return;
  }
  
  container.innerHTML = '';
  filtered.forEach(t => {
    const card = document.createElement('div');
    card.className = 'country-card';
    card.addEventListener('click', () => openCountrySquad(t.fifa_code));
    
    const flag = createFlagElement(t);
    const mval = t.metrics?.market_value_eur;
    const valText = mval ? `${mval.toFixed(1)}` : '0';
    
    card.innerHTML = `
      <div class="country-info-left">
        ${flag}
        <div>
          <div class="country-name-title">${t.name} (${t.fifa_code})</div>
          <div class="country-group-badge">Grupo ${t.group || 'N/A'}</div>
        </div>
      </div>
      <div class="country-value-badge">
        <div class="country-value-number">${valText}M€</div>
        <div class="country-value-lbl">Valor Plantel</div>
      </div>
    `;
    
    container.appendChild(card);
  });
}

function filterTeams() {
  renderCountries();
}

// 4. Open Squad Details Sub-tab
function openCountrySquad(code) {
  selectedCountryCode = code;
  const t = appData.teams[code];
  if (!t) return;
  
  // Switch to details layout
  document.getElementById('tab-squads').classList.remove('active');
  const squadDetailsView = document.getElementById('squad-details-view');
  squadDetailsView.classList.add('active');
  
  // Populate summary statistics
  const summaryContainer = document.getElementById('squad-header-container');
  const mval = t.metrics?.market_value_eur;
  const valText = mval ? `${mval.toFixed(1)} M€` : 'N/A';
  
  const starsList = t.squad.filter(p => p.is_star_player).map(p => p.name).slice(0, 3).join(', ');
  const starsText = starsList ? starsList : 'Ninguno';
  const injuredCount = t.squad.filter(p => p.is_injured).length;
  
  summaryContainer.innerHTML = `
    <div class="squad-header-title">
      ${createFlagElement(t)}
      <div>
        <h2>${t.name}</h2>
        <p style="color: var(--text-secondary); font-size: 0.95rem; font-weight: 500;">
          FIFA Code: ${t.fifa_code} &bull; Grupo: ${t.group || 'N/A'}
        </p>
      </div>
    </div>
    
    <div class="squad-header-stats">
      <div class="stat-item">
        <div class="stat-val gold">${valText}</div>
        <div class="stat-lbl">Valor de Plantel</div>
      </div>
      <div class="stat-item">
        <div class="stat-val">${t.metrics?.recent_xg_avg?.toFixed(2) || 'N/A'}</div>
        <div class="stat-lbl">Goles Esperados (xG)</div>
      </div>
      <div class="stat-item">
        <div class="stat-val">${t.metrics?.recent_possession_avg ? t.metrics.recent_possession_avg.toFixed(1) + '%' : 'N/A'}</div>
        <div class="stat-lbl">Posesión Prom.</div>
      </div>
      <div class="stat-item">
        <div class="stat-val purple">${t.metrics?.cards_per_match_avg?.toFixed(2) || 'N/A'}</div>
        <div class="stat-lbl">Tarjetas por Part.</div>
      </div>
      <div class="stat-item" style="min-width: 140px;" title="Estrellas clave en la plantilla">
        <div class="stat-val gold" style="font-size: 0.95rem; padding: 0.3rem 0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${starsText}</div>
        <div class="stat-lbl">Jugadores Clave</div>
      </div>
      <div class="stat-item" title="Bajas médicas o lesionados en el plantel probable">
        <div class="stat-val ${injuredCount > 0 ? 'purple' : ''}" style="color: ${injuredCount > 0 ? 'var(--accent-red)' : ''}">${injuredCount}</div>
        <div class="stat-lbl">Bajas / Lesionados</div>
      </div>
    </div>
  `;
  
  // Populate player table
  const tbody = document.getElementById('players-table-body');
  tbody.innerHTML = '';
  
  if (!t.squad || t.squad.length === 0) {
    tbody.innerHTML = `<tr><td colspan="11" style="text-align: center; color: var(--text-muted);">No se encontraron jugadores probables para esta selección.</td></tr>`;
  } else {
    t.squad.forEach(p => {
      const row = document.createElement('tr');
      
      const starIcon = p.is_star_player ? `<i class="fa-solid fa-star star-badge" title="Estrella"></i>` : '';
      const injuredBadge = p.is_injured ? `<span class="injured-badge" title="Lesionado / Baja para el próximo partido">Lesionado</span>` : '';
      
      let valText = 'N/A';
      if (p.market_value_eur !== null) {
        valText = `${p.market_value_eur.toFixed(1)} M€`;
      }
      

      let efficiencyBadge = '';
      if (p.efficiency_score !== null) {
        let cat = 'efficiency-average';
        if (p.efficiency_score >= 0.40) cat = 'efficiency-excellent';
        else if (p.efficiency_score >= 0.15) cat = 'efficiency-good';
        efficiencyBadge = `<span class="player-stat-badge ${cat}">${p.efficiency_score.toFixed(2)}</span>`;
      } else {
        efficiencyBadge = '<span class="player-unresolved-label">N/A</span>';
      }
      
      let cardBar = '';
      if (p.cards_propensity !== null) {
        let cat = 'safe';
        if (p.cards_propensity > 0.20) cat = 'danger';
        else if (p.cards_propensity > 0.10) cat = 'warning';
        
        cardBar = `
          <div style="display: flex; align-items: center; gap: 0.5rem;" title="Propensión a tarjetas: ${p.cards_propensity.toFixed(2)}">
            <span style="font-size: 0.8rem; font-weight:600; width: 30px;">${p.cards_propensity.toFixed(2)}</span>
            <div class="card-prop-bar-container">
              <div class="card-prop-bar ${cat}" style="width: ${Math.min(p.cards_propensity * 400, 100)}%"></div>
            </div>
          </div>
        `;
      } else {
        cardBar = '<span class="player-unresolved-label">N/A</span>';
      }
      
      row.innerHTML = `
        <td>
          <div class="player-name-cell">
            <span class="player-name-val">${p.name}</span>
            ${starIcon}
            ${injuredBadge}
          </div>
        </td>
        <td><span class="player-club-cell">${p.position}</span></td>
        <td><span class="player-club-cell">${p.club}</span></td>
        <td style="font-weight: 500;">${p.age || 'N/A'}</td>
        <td>${p.caps !== null ? p.caps : 'N/A'}</td>
        <td>${p.goals !== null ? p.goals : 'N/A'}</td>
        <td style="font-weight: 500;">${p.minutes_recent !== null ? p.minutes_recent : 'N/A'}</td>
        <td style="font-weight: 500;">${p.assists_recent !== null ? p.assists_recent : 'N/A'}</td>
        <td>${efficiencyBadge}</td>
        <td class="player-val-cell">${valText}</td>
        <td>${cardBar}</td>
      `;
      
      tbody.appendChild(row);
    });
  }
}

function closeSquadDetails() {
  selectedCountryCode = null;
  document.getElementById('squad-details-view').classList.remove('active');
  document.getElementById('tab-squads').classList.add('active');
}

// 5. Render Unresolved Players List Tab
function renderUnresolved() {
  const container = document.getElementById('unresolved-list-container');
  const countBadge = document.getElementById('unresolved-count-badge');
  if (!appData) return;
  
  // Collect unresolved players from Wikipedia/API results
  const unresolvedList = [];
  
  // Note: we can look into all teams and their squads to see if there are players with null values, 
  // but since we also want the Wikipedia original stats and specific reason, we will fetch from teams or mock database representation.
  // Actually, we can fetch all players with resolved === false if exported, or let's scan all squads for players with NULL values!
  // But wait, the python exporter could export scraped_unresolved_players or we can just scan squads for players where market_value_eur is NULL.
  // Wait, let's look at how squads are set up. If a player is unresolved, his market_val is null.
  // Let's list those.
  
  Object.values(appData.teams).forEach(t => {
    if (t.is_placeholder || !t.squad) return;
    t.squad.forEach(p => {
      if (p.market_value_eur === null && p.sofascore_rating === null) {
        unresolvedList.push({
          name: p.name,
          country: t.name,
          fifa_code: t.fifa_code,
          position: p.position,
          club: p.club,
          age: p.age,
          caps: p.caps,
          goals: p.goals,
          reason: "No matched candidate was resolved on local Transfermarkt API (nationality/age/name filter mismatch)"
        });
      }
    });
  });
  
  countBadge.textContent = `${unresolvedList.length} Registros`;
  
  if (unresolvedList.length === 0) {
    container.innerHTML = `
      <div class="no-history-msg">
        No hay registros de jugadores no resueltos. Todos los convocados de Wikipedia se vincularon con éxito en la API.
      </div>`;
    return;
  }
  
  container.innerHTML = '';
  
  // Render top 50 to avoid overloading
  const limit = unresolvedList.slice(0, 50);
  
  limit.forEach(p => {
    const div = document.createElement('div');
    div.className = 'unresolved-item';
    
    div.innerHTML = `
      <div class="unresolved-item-title">
        <span>${p.name}</span>
        <span class="injured-badge" style="background: rgba(251, 191, 36, 0.1); border-color: rgba(251, 191, 36, 0.2); color: var(--accent-gold); font-size: 0.6rem;">Null Metrics</span>
      </div>
      <div class="unresolved-item-meta">
        Selección: <strong>${p.country} (${p.fifa_code})</strong> &bull; Posición: ${p.position} &bull; Club: ${p.club} &bull; Edad: ${p.age} &bull; Partidos: ${p.caps || 0} &bull; Goles: ${p.goals || 0}
      </div>
      <div class="unresolved-item-reason">
        <strong>Motivo de Integridad:</strong> ${p.reason}
      </div>
    `;
    container.appendChild(div);
  });
  
  if (unresolvedList.length > 50) {
    const moreDiv = document.createElement('div');
    moreDiv.style.textAlign = 'center';
    moreDiv.style.color = 'var(--text-muted)';
    moreDiv.style.padding = '1rem';
    moreDiv.innerHTML = `y ${unresolvedList.length - 50} jugadores no resueltos más.`;
    container.appendChild(moreDiv);
  }
}

// 6. H2H Modal Management
function openH2HModal(match) {
  const modal = document.getElementById('h2h-modal');
  modal.classList.add('active');
  
  // Set basic details
  document.getElementById('modal-match-title').textContent = `Partido #${match.match_number} &bull; ${match.stage}`;
  document.getElementById('modal-match-score').textContent = match.smartScore.toFixed(1);
  
  // Set rank interest (out of 104 matches)
  if (appData && appData.matches) {
    const rank = appData.matches.findIndex(m => m.match_number === match.match_number) + 1;
    document.getElementById('modal-match-rank').textContent = `#${rank}`;
  }
  
  // Combined squad value
  const combVal = getCombinedValue(match);
  document.getElementById('modal-squad-comb-val').textContent = combVal > 0 ? `${combVal.toFixed(1)} M€` : 'N/A';
  
  // Set teams blocks in VS
  const homeBlock = document.getElementById('modal-team-home');
  const awayBlock = document.getElementById('modal-team-away');
  
  const homeTeamInfo = appData.teams[match.home_team.fifa_code];
  const awayTeamInfo = appData.teams[match.away_team.fifa_code];
  
  homeBlock.innerHTML = `
    ${createFlagElement(match.home_team)}
    <div class="modal-team-name">${match.home_team.name}</div>
    ${match.home_team.group ? `<div style="font-size:0.75rem; color:var(--text-secondary);">Grupo ${match.home_team.group}</div>` : ''}
  `;
  
  awayBlock.innerHTML = `
    ${createFlagElement(match.away_team)}
    <div class="modal-team-name">${match.away_team.name}</div>
    ${match.away_team.group ? `<div style="font-size:0.75rem; color:var(--text-secondary);">Grupo ${match.away_team.group}</div>` : ''}
  `;
  
  // Set labels on Wins counts
  document.getElementById('h2h-home-lbl').textContent = `Victoria ${match.home_team.name}`;
  document.getElementById('h2h-away-lbl').textContent = `Victoria ${match.away_team.name}`;
  
  // Compare values
  if (homeTeamInfo && awayTeamInfo && !match.home_team.is_placeholder && !match.away_team.is_placeholder) {
    const valHome = homeTeamInfo.metrics?.market_value_eur;
    const valAway = awayTeamInfo.metrics?.market_value_eur;
    
    document.getElementById('comp-val-mkt-home').textContent = valHome ? `${valHome.toFixed(1)}M€` : 'N/A';
    document.getElementById('comp-val-mkt-away').textContent = valAway ? `${valAway.toFixed(1)}M€` : 'N/A';
    
    document.getElementById('comp-val-xg-home').textContent = homeTeamInfo.metrics?.recent_xg_avg?.toFixed(2) || 'N/A';
    document.getElementById('comp-val-xg-away').textContent = awayTeamInfo.metrics?.recent_xg_avg?.toFixed(2) || 'N/A';
    
    document.getElementById('comp-val-poss-home').textContent = homeTeamInfo.metrics?.recent_possession_avg ? homeTeamInfo.metrics.recent_possession_avg.toFixed(1) + '%' : 'N/A';
    document.getElementById('comp-val-poss-away').textContent = awayTeamInfo.metrics?.recent_possession_avg ? awayTeamInfo.metrics.recent_possession_avg.toFixed(1) + '%' : 'N/A';
    
    document.getElementById('comp-val-pop-home').textContent = homeTeamInfo.metrics?.global_popularity_score?.toFixed(0) || 'N/A';
    document.getElementById('comp-val-pop-away').textContent = awayTeamInfo.metrics?.global_popularity_score?.toFixed(0) || 'N/A';
    
    // Set general H2H statistics
    const h2h = match.h2h;
    document.getElementById('h2h-total-games').textContent = h2h.total_matches;
    document.getElementById('h2h-home-wins').textContent = h2h.home_wins;
    document.getElementById('h2h-draws').textContent = h2h.draws;
    document.getElementById('h2h-away-wins').textContent = h2h.away_wins;
    
    // Update distribution chart widths
    if (h2h.total_matches > 0) {
      const wHome = (h2h.home_wins / h2h.total_matches) * 100;
      const wDraw = (h2h.draws / h2h.total_matches) * 100;
      const wAway = (h2h.away_wins / h2h.total_matches) * 100;
      
      document.getElementById('h2h-bar-home-w').style.width = `${wHome}%`;
      document.getElementById('h2h-bar-home-w').textContent = wHome > 15 ? `${wHome.toFixed(0)}%` : '';
      
      document.getElementById('h2h-bar-draws-w').style.width = `${wDraw}%`;
      document.getElementById('h2h-bar-draws-w').textContent = wDraw > 15 ? `${wDraw.toFixed(0)}%` : '';
      
      document.getElementById('h2h-bar-away-w').style.width = `${wAway}%`;
      document.getElementById('h2h-bar-away-w').textContent = wAway > 15 ? `${wAway.toFixed(0)}%` : '';
    } else {
      document.getElementById('h2h-bar-home-w').style.width = '33%';
      document.getElementById('h2h-bar-home-w').textContent = '';
      document.getElementById('h2h-bar-draws-w').style.width = '34%';
      document.getElementById('h2h-bar-draws-w').textContent = '';
      document.getElementById('h2h-bar-away-w').style.width = '33%';
      document.getElementById('h2h-bar-away-w').textContent = '';
    }
    
    // Render Fjelstul WC H2H metrics
    const wcH2hSummary = document.getElementById('modal-wc-h2h-summary');
    wcH2hSummary.innerHTML = `
      <div>
        <div class="h2h-summary-val" style="color: var(--accent-gold);">${h2h.wc_matches}</div>
        <div class="h2h-summary-lbl">Partidos en Mundiales</div>
      </div>
      <div>
        <div class="h2h-summary-val" style="color: var(--accent-cyan);">${h2h.wc_home_wins}</div>
        <div class="h2h-summary-lbl">Victorias ${match.home_team.name}</div>
      </div>
      <div>
        <div class="h2h-summary-val" style="color: var(--text-secondary);">${h2h.wc_draws}</div>
        <div class="h2h-summary-lbl">Empates</div>
      </div>
      <div>
        <div class="h2h-summary-val" style="color: var(--accent-gold);">${h2h.wc_away_wins}</div>
        <div class="h2h-summary-lbl">Victorias ${match.away_team.name}</div>
      </div>
    `;
    
    // Render past games list
    const pastContainer = document.getElementById('h2h-past-matches-container');
    pastContainer.innerHTML = '';
    
    if (!h2h.last_matches || h2h.last_matches.length === 0) {
      pastContainer.innerHTML = `<div class="no-history-msg">No hay registros de enfrentamientos directos previos.</div>`;
    } else {
      h2h.last_matches.forEach(pm => {
        const item = document.createElement('div');
        item.className = 'history-match-item';
        
        item.innerHTML = `
          <div class="history-match-left">
            <span class="history-date">${pm.date}</span>
            <span class="history-tourn" title="${pm.tournament}">${pm.tournament}</span>
            <span class="history-teams">${pm.home_team} vs ${pm.away_team}</span>
          </div>
          <span class="history-score">${pm.score}</span>
        `;
        pastContainer.appendChild(item);
      });
    }
    
  } else {
    // If playoff placeholders
    document.getElementById('comp-val-mkt-home').textContent = 'N/A';
    document.getElementById('comp-val-mkt-away').textContent = 'N/A';
    document.getElementById('comp-val-xg-home').textContent = 'N/A';
    document.getElementById('comp-val-xg-away').textContent = 'N/A';
    document.getElementById('comp-val-poss-home').textContent = 'N/A';
    document.getElementById('comp-val-poss-away').textContent = 'N/A';
    document.getElementById('comp-val-pop-home').textContent = 'N/A';
    document.getElementById('comp-val-pop-away').textContent = 'N/A';
    
    document.getElementById('h2h-total-games').textContent = '0';
    document.getElementById('h2h-home-wins').textContent = '0';
    document.getElementById('h2h-draws').textContent = '0';
    document.getElementById('h2h-away-wins').textContent = '0';
    
    document.getElementById('h2h-bar-home-w').style.width = '33%';
    document.getElementById('h2h-bar-draws-w').style.width = '34%';
    document.getElementById('h2h-bar-away-w').style.width = '33%';
    
    document.getElementById('modal-wc-h2h-summary').innerHTML = '<div class="no-history-msg" style="width:100%;">Pendiente de clasificación de equipos (Playoffs TBD)</div>';
    document.getElementById('h2h-past-matches-container').innerHTML = '<div class="no-history-msg">No aplica para partidos eliminatorios TBD.</div>';
  }
}

function closeModal() {
  document.getElementById('h2h-modal').classList.remove('active');
}
