import { state } from '../state.js';
import { createFlagElement } from '../utils.js';

// 3. Render Countries / Squads Selection Tab
export function renderCountries() {
  const container = document.getElementById('countries-container');
  if (!state.appData || !state.appData.teams) return;
  
  const searchVal = document.getElementById('search-teams').value.toLowerCase();
  
  // Filter real teams
  const filtered = Object.values(state.appData.teams).filter(t => {
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

export function filterTeams() {
  renderCountries();
}

// 4. Open Squad Details Sub-tab
export function openCountrySquad(code) {
  window.switchTab('squads');
  state.selectedCountryCode = code;
  const t = state.appData.teams[code];
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
  // Render Probable Lineup
  renderLineup(t);
  
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
      
      row.style.cursor = 'pointer';
      row.onclick = () => window.openPlayerProfile(code, p.id);
      
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

export function closeSquadDetails() {
  state.selectedCountryCode = null;
  document.getElementById('squad-details-view').classList.remove('active');
  document.getElementById('tab-squads').classList.add('active');
}

function renderLineup(team) {
  const container = document.getElementById('squad-lineup-container');
  if (!container) return;
  
  if (!team.squad || team.squad.length === 0) {
    container.innerHTML = '<div style="color: white; text-align: center; margin: auto;">Sin datos para la alineación</div>';
    return;
  }

  // Sort available players by market_value
  const sorted = [...team.squad].filter(p => !p.is_injured).sort((a, b) => {
    return (b.market_value_eur || 0) - (a.market_value_eur || 0);
  });

  const goalkeepers = sorted.filter(p => p.position && p.position.toLowerCase().includes('portero'));
  const defenders = sorted.filter(p => p.position && p.position.toLowerCase().includes('defensa'));
  const midfielders = sorted.filter(p => p.position && (p.position.toLowerCase().includes('centro') || p.position.toLowerCase().includes('medio')));
  const forwards = sorted.filter(p => p.position && p.position.toLowerCase().includes('delantero'));

  // 4-3-3 formation base
  let gk = goalkeepers.slice(0, 1);
  let defs = defenders.slice(0, 4);
  let mids = midfielders.slice(0, 3);
  let fwds = forwards.slice(0, 3);

  // Fill gaps if missing specific positions
  const selectedIds = new Set([...gk, ...defs, ...mids, ...fwds].map(p => p.id));
  let remainingNeeded = 11 - selectedIds.size;
  if (remainingNeeded > 0) {
    const extra = sorted.filter(p => !selectedIds.has(p.id)).slice(0, remainingNeeded);
    mids = [...mids, ...extra]; // shove extras in midfield visually
  }

  // If no GK, just put a generic one visually
  if (gk.length === 0) {
    if (mids.length > 0) gk = [mids.pop()];
    else if (defs.length > 0) gk = [defs.pop()];
  }

  const createPlayerHTML = (p, num) => {
    if (!p) return '';
    const lastName = p.name.split(' ').pop();
    // Simulate rating from efficiency (0-1) to Sofascore (1-10)
    let ratingVal = p.efficiency_score !== null ? (p.efficiency_score * 4 + 5.5) : 6.5; 
    let rating = ratingVal.toFixed(1);
    
    let ratingClass = 'rating-yellow';
    if (ratingVal >= 7.0) ratingClass = 'rating-green';
    else if (ratingVal < 6.0) ratingClass = 'rating-red';

    const parts = p.name.split(' ');
    const initials = parts.length > 1 ? parts[0][0] + parts[parts.length-1][0] : parts[0].substring(0, 2);

    // Escape name for string passing
    const safeName = p.name.replace(/'/g, "\\'");
    
    return `
      <div class="sofascore-player" title="${p.name} - ${p.club}" onclick="window.openPlayerProfile('${team.fifa_code}', ${p.id})">
        <div class="sofa-photo-circle">
          <span>${initials.toUpperCase()}</span>
          <div class="sofa-rating-badge ${ratingClass}">${rating}</div>
        </div>
        <div class="sofa-player-name">
          <span class="sofa-player-num">${num}</span> ${lastName}
        </div>
      </div>
    `;
  };

  const renderRow = (players, startNum) => {
    if (!players || players.length === 0) return '';
    return `<div class="lineup-row">
      ${players.map((p, i) => createPlayerHTML(p, startNum + i)).join('')}
    </div>`;
  };

  container.innerHTML = `
    ${renderRow(fwds, 9)}
    ${renderRow(mids, 6)}
    ${renderRow(defs, 2)}
    ${renderRow(gk, 1)}
  `;
}
