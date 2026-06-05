import { state, getSimulatedScores, fifaToSpanish } from '../futstate.js';
import { createFlagElement, formatKickoff } from '../utils.js';
import { openH2HModal } from './modal.js?v=5';

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
  const simulatedScores = getSimulatedScores();
  
  // Verify if all group stage matches (1 to 72) are simulated
  let groupMatchesPlayed = 0;
  for (let i = 1; i <= 72; i++) {
    if (simulatedScores[i] !== undefined) groupMatchesPlayed++;
  }
  const isGroupStageFinished = groupMatchesPlayed === 72;

  const filtered = state.appData.matches.filter(m => {
    // Exclude matches that already have a simulated result
    if (simulatedScores[m.match_number] !== undefined) return false;

    // Do not recommend knockout matches until the group stage is completely simulated
    if (m.stage !== 'Group Stage' && !isGroupStageFinished) return false;

    const spanishHome = (fifaToSpanish[m.home_team.fifa_code] || '').toLowerCase();
    const spanishAway = (fifaToSpanish[m.away_team.fifa_code] || '').toLowerCase();

    // Search filter
    const matchesSearch =
      m.match_label.toLowerCase().includes(searchVal) ||
      m.home_team.name.toLowerCase().includes(searchVal) ||
      m.away_team.name.toLowerCase().includes(searchVal) ||
      spanishHome.includes(searchVal) ||
      spanishAway.includes(searchVal) ||
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

  // Group matches into 3 tiers
  const tiers = {
    imperdible: { title: '<i class="fa-solid fa-fire"></i> Imperdible', class: 'tier-imperdible', matches: [] },
    valelapena: { title: '<i class="fa-solid fa-thumbs-up"></i> Vale la pena', class: 'tier-valelapena', matches: [] },
    resumen: { title: '<i class="fa-solid fa-tv"></i> Para ver el resumen', class: 'tier-resumen', matches: [] }
  };

  filtered.forEach(m => {
    if (m.smartScore >= 8.0) tiers.imperdible.matches.push(m);
    else if (m.smartScore >= 6.0) tiers.valelapena.matches.push(m);
    else tiers.resumen.matches.push(m);
  });

  // Render each tier if it has matches
  Object.keys(tiers).forEach(key => {
    const tier = tiers[key];
    if (tier.matches.length === 0) return;

    const section = document.createElement('div');
    section.className = `tier-section ${tier.class}`;

    const title = document.createElement('h3');
    title.className = 'tier-title';
    title.innerHTML = tier.title;
    section.appendChild(title);

    const grid = document.createElement('div');
    grid.className = `matches-grid grid-${key}`;

    const isCollapsible = (key === 'valelapena' || key === 'resumen') && tier.matches.length > 9;

    tier.matches.forEach((m, index) => {
      const card = document.createElement('div');
      card.className = `match-card match-card--${key}`;
      if (isCollapsible && index >= 9) {
        card.classList.add('hidden-match');
      }
      card.addEventListener('click', () => openH2HModal(m));

      const combVal = getCombinedValue(m);
      const combValStr = combVal > 0 ? `${combVal.toFixed(1)}M€` : 'N/A';

      let interestClass = 'low-interest';
      if (m.smartScore >= 8.0) interestClass = 'high-interest';
      else if (m.smartScore >= 6.0) interestClass = 'medium-interest';

      

      const flagHome = createFlagElement(m.home_team);
      const flagAway = createFlagElement(m.away_team);

      let explanation = "Juego Equilibrado<br><span style='font-size:0.55rem; font-weight:normal; opacity:0.8;'>(fuerzas muy parejas)</span>";
      if (m.h2h?.total_matches > 4) explanation = "Rivalidad Histórica<br><span style='font-size:0.55rem; font-weight:normal; opacity:0.8;'>(mucho historial entre ellos)</span>";
      else if (m.stage !== 'Group Stage') explanation = "Duelo Decisivo<br><span style='font-size:0.55rem; font-weight:normal; opacity:0.8;'>(partido de eliminación)</span>";
      else if (combVal > 1200) explanation = "Choque de Gigantes<br><span style='font-size:0.55rem; font-weight:normal; opacity:0.8;'>(planteles súper valiosos)</span>";
      else if (m.smartScore >= 8.5) explanation = "Duelo Imperdible<br><span style='font-size:0.55rem; font-weight:normal; opacity:0.8;'>(nota casi perfecta)</span>";
      else if (m.smartScore >= 7.0) explanation = "Alta Expectativa<br><span style='font-size:0.55rem; font-weight:normal; opacity:0.8;'>(muy recomendado)</span>";
      else if (combVal > 600) explanation = "Estrellas en Cancha<br><span style='font-size:0.55rem; font-weight:normal; opacity:0.8;'>(varias figuras en juego)</span>";

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
          <div class="interest-explanation" style="font-size:0.65rem; color:var(--accent-cyan); text-align:center; margin-top:4px; font-weight: bold; line-height: 1.1;">${explanation}</div>
        </div>
        <div class="match-metrics-preview">
          ${combVal > 0 ? `<div class="metric-pill value" title="Valor de plantilla combinado"><i class="fa-solid fa-coins"></i> ${combValStr}</div>` : ''}
          ${!m.home_team.is_placeholder && !m.away_team.is_placeholder ? `<div class="metric-pill cards" title="Tarjetas amarillas/rojas promedio combinadas"><i class="fa-solid fa-copy"></i> Fricción: ${getCombinedCards(m).toFixed(2)}</div>` : ''}
        </div>
        <div class="match-venue">
          <i class="fa-solid fa-location-dot"></i>
          <span>${m.stadium ? `${m.stadium.venue_name}, ${m.stadium.city_name}` : 'TBD'}</span>
        </div>
      `;
      grid.appendChild(card);
    });

    section.appendChild(grid);

    if (isCollapsible) {
      const btnContainer = document.createElement('div');
      btnContainer.className = 'view-more-container';
      const btn = document.createElement('button');
      btn.className = 'btn-mundial btn-mundial--outline btn-view-more';
      btn.innerHTML = `Ver más (${tier.matches.length - 10} restantes) <i class="fa-solid fa-chevron-down"></i>`;
      btn.onclick = () => {
        grid.querySelectorAll('.hidden-match').forEach(c => c.classList.remove('hidden-match'));
        btnContainer.style.display = 'none';
      };
      btnContainer.appendChild(btn);
      section.appendChild(btnContainer);
    }

    container.appendChild(section);
  });
}

export function filterMatches() {
  const sortSelect = document.getElementById('sort-matches').value;
  sortMatchesList(sortSelect);
  renderMatches();
}


