import { state } from '../state.js';
import { createFlagElement, formatKickoff } from '../utils.js';
import { openH2HModal } from './modal.js';

// Sorting logic
export function sortMatchesList(criterion) {
  if (!state.appData || !state.appData.matches) return;
  
  if (criterion === 'interest-desc') {
    state.appData.matches.sort((a, b) => b.smartScore - a.smartScore || a.match_number - b.match_number);
  } else if (criterion === 'match-asc') {
    state.appData.matches.sort((a, b) => a.match_number - b.match_number);
  } else if (criterion === 'value-desc') {
    state.appData.matches.sort((a, b) => {
      const vA = getCombinedValue(a);
      const vB = getCombinedValue(b);
      return vB - vA || a.match_number - b.match_number;
    });
  } else if (criterion === 'cards-desc') {
    state.appData.matches.sort((a, b) => {
      const cA = getCombinedCards(a);
      const cB = getCombinedCards(b);
      return cB - cA || a.match_number - b.match_number;
    });
  }
}

export function getCombinedValue(match) {
  if (match.home_team.is_placeholder || match.away_team.is_placeholder) return 0;
  const home = state.appData.teams[match.home_team.fifa_code];
  const away = state.appData.teams[match.away_team.fifa_code];
  return ((home?.metrics?.market_value_eur || 0) + (away?.metrics?.market_value_eur || 0));
}

export function getCombinedCards(match) {
  if (match.home_team.is_placeholder || match.away_team.is_placeholder) return 0;
  const home = state.appData.teams[match.home_team.fifa_code];
  const away = state.appData.teams[match.away_team.fifa_code];
  return ((home?.metrics?.cards_per_match_avg || 1.3) + (away?.metrics?.cards_per_match_avg || 1.3));
}

// 1. Render Matches List
export function renderMatches() {
  const container = document.getElementById('matches-container');
  if (!state.appData || !state.appData.matches) return;
  
  const searchVal = document.getElementById('search-matches').value.toLowerCase();
  const stageFilter = document.getElementById('filter-stage').value;
  const regionFilter = document.getElementById('filter-region').value;
  
  // Filter matches
  const filtered = state.appData.matches.filter(m => {
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
      injuredCount += state.appData.teams[m.home_team.fifa_code]?.squad.filter(p => p.is_injured).length || 0;
    }
    if (!m.away_team.is_placeholder) {
      injuredCount += state.appData.teams[m.away_team.fifa_code]?.squad.filter(p => p.is_injured).length || 0;
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
        <div class="team-row" onclick="event.stopPropagation(); if(!${m.home_team.is_placeholder}) window.openCountrySquad('${m.home_team.fifa_code}', 'recommender')">
          ${flagHome}
          <span class="team-name ${m.home_team.is_placeholder ? 'placeholder-name' : ''}">${m.home_team.name}</span>
        </div>
        <div class="team-row" onclick="event.stopPropagation(); if(!${m.away_team.is_placeholder}) window.openCountrySquad('${m.away_team.fifa_code}', 'recommender')">
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

export function filterMatches() {
  const sortSelect = document.getElementById('sort-matches').value;
  sortMatchesList(sortSelect);
  renderMatches();
}


