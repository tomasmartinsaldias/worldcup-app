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
    card.addEventListener('click', () => openCountrySquad(t.fifa_code, 'squads'));
    
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
export function openCountrySquad(code, origin = 'squads') {
  sessionStorage.setItem('squad_origin', origin);
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

  const confirmedBadge = t.is_confirmed_squad 
    ? `<span style="background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.3); color: #4ade80; font-size: 0.8rem; padding: 0.2rem 0.5rem; border-radius: 6px; display: inline-flex; align-items: center; gap: 0.25rem; font-weight: 600; vertical-align: middle;"><i class="fa-solid fa-circle-check"></i> Oficial</span>`
    : `<span style="background: rgba(251, 191, 36, 0.15); border: 1px solid rgba(251, 191, 36, 0.3); color: #fbbf24; font-size: 0.8rem; padding: 0.2rem 0.5rem; border-radius: 6px; display: inline-flex; align-items: center; gap: 0.25rem; font-weight: 600; vertical-align: middle;"><i class="fa-solid fa-circle-question"></i> Probable</span>`;

  summaryContainer.innerHTML = `
    <div class="squad-header-title">
      ${createFlagElement(t)}
      <div>
        <h2 style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">${t.name} ${confirmedBadge}</h2>
        <p style="color: var(--text-secondary); font-size: 0.95rem; font-weight: 500;">
          FIFA Code: ${t.fifa_code} &bull; Grupo: ${t.group || 'N/A'}
        </p>
        <p style="color: var(--accent-gold); font-size: 0.9rem; font-weight: 600; margin-top: 0.25rem;">
          DT: ${t.manager || 'No Asignado'}
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
      <div class="stat-item" title="Racha invicta actual en partidos internacionales">
        <div class="stat-val green">${t.metrics?.current_unbeaten_streak !== undefined ? `${t.metrics.current_unbeaten_streak} Part.` : 'N/A'}</div>
        <div class="stat-lbl">Racha Invicta</div>
      </div>
      <div class="stat-item" title="Récord de victorias, empates y derrotas en los últimos 10 partidos">
        <div class="stat-val" style="font-size: 0.95rem; padding: 0.3rem 0;">
          ${t.metrics?.win_rate_last_10 !== undefined && t.metrics?.win_rate_last_10 !== null ? `${Math.round(t.metrics.win_rate_last_10 * 10)}V / ${Math.round(t.metrics.draw_rate_last_10 * 10)}E / ${Math.round(t.metrics.loss_rate_last_10 * 10)}D` : 'N/A'}
        </div>
        <div class="stat-lbl">Récord (V/E/D)</div>
      </div>
      <div class="stat-item" title="Goles marcados vs encajados promedio en los últimos 10 partidos">
        <div class="stat-val" style="font-size: 0.95rem; padding: 0.3rem 0;">
          ${t.metrics?.goals_scored_avg_last_10 !== undefined && t.metrics?.goals_scored_avg_last_10 !== null ? `${t.metrics.goals_scored_avg_last_10.toFixed(1)} / ${t.metrics.goals_conceded_avg_last_10.toFixed(1)}` : 'N/A'}
        </div>
        <div class="stat-lbl">Goles Prom. (F/C)</div>
      </div>
      <div class="stat-item" style="min-width: 140px;" title="Rival más fuerte derrotado en los últimos 20 encuentros">
        <div class="stat-val gold" style="font-size: 0.85rem; padding: 0.35rem 0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
          ${t.metrics?.top_opponent_beaten || 'N/A'}
        </div>
        <div class="stat-lbl">Top Rival Vencido</div>
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
  const origin = sessionStorage.getItem('squad_origin') || 'squads';
  window.switchTab(origin);
}

function renderLineup(team) {
  const container = document.getElementById('squad-lineup-container');
  if (!container) return;
  
  if (!team.squad || team.squad.length === 0) {
    container.innerHTML = '<div style="color: white; text-align: center; margin: auto;">Sin datos para la alineación</div>';
    return;
  }

  // Formaciones preferidas conocidas por selección (basadas en historial reciente)
  const KNOWN_FORMATIONS = {
    'ARG': '4-4-2', 'BRA': '4-2-3-1', 'FRA': '4-3-3', 'ENG': '4-3-3',
    'ESP': '4-3-3', 'GER': '4-2-3-1', 'POR': '4-3-3', 'ITA': '4-3-3',
    'NED': '4-3-3', 'BEL': '4-3-3', 'URU': '4-4-2', 'COL': '4-2-3-1',
    'MEX': '4-3-3', 'USA': '4-3-3', 'CAN': '4-2-3-1', 'JAP': '4-2-3-1',
    'MAR': '4-1-4-1', 'SEN': '4-3-3', 'NGA': '4-3-3', 'EGY': '4-2-3-1',
    'AUS': '4-3-3', 'KOR': '4-2-3-1', 'CRO': '4-3-3', 'SUI': '3-4-3',
    'DEN': '4-3-3', 'SWE': '4-4-2', 'POL': '4-2-3-1', 'SRB': '3-4-3',
    'ECU': '4-3-3', 'VEN': '4-3-3', 'BOL': '4-4-2', 'PAR': '4-3-3',
    'PER': '4-3-3', 'CHI': '4-3-3',
  };

  // Helper: categoriza la posición de un jugador
  const getPosCategory = (p) => {
     let pos = (p.position || '').toLowerCase();
     if(pos.includes('portero') || pos.includes('arquero') || pos.includes('goalkeeper')) return 'GK';
     if(pos.includes('delantero') || pos.includes('extremo') || pos.includes('atacante') || pos.includes('forward') || pos.includes('winger')) return 'FWD';
     if(pos.includes('centrocampista') || pos.includes('medio') || pos.includes('volante') || pos.includes('pivote') || pos.includes('midfielder')) return 'MID';
     if(pos.includes('defensa') || pos.includes('lateral') || pos.includes('central') || pos.includes('carrilero') || pos.includes('defender')) return 'DEF';
     return 'MID'; // fallback
  };

  const getPosOrder = (cat) => {
     if(cat === 'GK') return 1; if(cat === 'DEF') return 2;
     if(cat === 'MID') return 3; if(cat === 'FWD') return 4;
     return 5;
  };

  const lineup = team.last_known_lineup;
  let startingNames = lineup ? lineup.starting_xi : [];
  let startingPlayers = [];

  // Si hay alineación oficial, usarla
  if (startingNames.length > 0) {
      startingNames.forEach(name => {
          const p = team.squad.find(s => s.name === name);
          if (p) startingPlayers.push(p);
      });
  }

  // --- FALLBACK: elegir 11 jugadores respetando la formación preferida del equipo ---
  if (startingPlayers.length < 11) {
      const fifa_code = team.fifa_code || '';
      const preferredFormation = KNOWN_FORMATIONS[fifa_code] || '4-3-3';
      const formSlots = preferredFormation.split('-').map(Number); // ej: [4,4,2]
      const needDef = formSlots[0] || 4;
      const needMid = formSlots[1] || 3;
      const needFwd = formSlots.slice(2).reduce((a,b)=>a+b, 0) || 3;

      // Separar plantel disponible por posición, ordenado por valor de mercado
      const available = [...team.squad].filter(p => !p.is_injured);
      const byPos = { GK: [], DEF: [], MID: [], FWD: [] };
      available.forEach(p => { const cat = getPosCategory(p); if(byPos[cat]) byPos[cat].push(p); });
      Object.values(byPos).forEach(arr => arr.sort((a,b) => (b.market_value_eur||0)-(a.market_value_eur||0)));

      startingPlayers = [];
      startingPlayers.push(...byPos['GK'].slice(0, 1));   // 1 arquero
      startingPlayers.push(...byPos['DEF'].slice(0, needDef));
      startingPlayers.push(...byPos['MID'].slice(0, needMid));
      startingPlayers.push(...byPos['FWD'].slice(0, needFwd));

      // Si alguna posición no tiene suficientes jugadores, completar con lo que haya
      if (startingPlayers.length < 11) {
          const used = new Set(startingPlayers.map(p => p.name));
          const extra = available.filter(p => !used.has(p.name))
                                 .sort((a,b) => (b.market_value_eur||0)-(a.market_value_eur||0));
          while (startingPlayers.length < 11 && extra.length > 0) startingPlayers.push(extra.shift());
      }

      // La formación string viene de la preferida
      var formationStr = preferredFormation;
  } else {
      var formationStr = lineup ? lineup.formation : '4-3-3';
  }

  startingPlayers.sort((a,b) => getPosOrder(getPosCategory(a)) - getPosOrder(getPosCategory(b)));

  const SLOT_COORDS = {
      'GK': { x: 50, y: 5 },
      'RB': { x: 85, y: 20 }, 'RCB': { x: 65, y: 15 }, 'CB': { x: 50, y: 15 }, 'LCB': { x: 35, y: 15 }, 'LB': { x: 15, y: 20 },
      'RWB': { x: 90, y: 35 }, 'LWB': { x: 10, y: 35 },
      'CDM': { x: 50, y: 35 }, 'RDM': { x: 65, y: 35 }, 'LDM': { x: 35, y: 35 },
      'CM': { x: 50, y: 50 }, 'RCM': { x: 65, y: 50 }, 'LCM': { x: 35, y: 50 },
      'RM': { x: 85, y: 60 }, 'LM': { x: 15, y: 60 },
      'CAM': { x: 50, y: 70 }, 'RAM': { x: 68, y: 70 }, 'LAM': { x: 32, y: 70 },
      'RW': { x: 85, y: 80 }, 'LW': { x: 15, y: 80 },
      'ST': { x: 50, y: 85 }, 'CF': { x: 50, y: 85 }, 'RS': { x: 65, y: 85 }, 'LS': { x: 35, y: 85 },
      'RF': { x: 70, y: 80 }, 'LF': { x: 30, y: 80 }
  };

  const FORMATION_SLOTS = {
      '4-3-3': ['GK', 'RB', 'RCB', 'LCB', 'LB', 'CDM', 'RCM', 'LCM', 'RW', 'ST', 'LW'],
      '4-4-2': ['GK', 'RB', 'RCB', 'LCB', 'LB', 'RM', 'RCM', 'LCM', 'LM', 'RS', 'LS'],
      '4-2-3-1': ['GK', 'RB', 'RCB', 'LCB', 'LB', 'RDM', 'LDM', 'RM', 'CAM', 'LM', 'ST'],
      '3-4-2-1': ['GK', 'RCB', 'CB', 'LCB', 'RM', 'RCM', 'LCM', 'LM', 'RAM', 'LAM', 'ST'],
      '3-4-3': ['GK', 'RCB', 'CB', 'LCB', 'RM', 'RCM', 'LCM', 'LM', 'RW', 'ST', 'LW'],
      '4-1-4-1': ['GK', 'RB', 'RCB', 'LCB', 'LB', 'CDM', 'RM', 'RCM', 'LCM', 'LM', 'ST'],
      '3-5-2': ['GK', 'RCB', 'CB', 'LCB', 'RWB', 'RDM', 'LDM', 'LWB', 'CAM', 'RS', 'LS'],
      '5-4-1': ['GK', 'RWB', 'RCB', 'CB', 'LCB', 'LWB', 'RM', 'RCM', 'LCM', 'LM', 'ST'],
      '5-3-2': ['GK', 'RWB', 'RCB', 'CB', 'LCB', 'LWB', 'RCM', 'CM', 'LCM', 'RS', 'LS'],
  };

  let targetSlots = FORMATION_SLOTS[formationStr] || FORMATION_SLOTS['4-3-3'];
  let availableSlots = [...targetSlots];
  
  let assignedPlayers = [];
  
  startingPlayers.forEach(p => {
      let prefPos = (p.exact_position || '').toUpperCase();
      let assignedSlot = null;
      
      if (availableSlots.includes(prefPos)) {
          assignedSlot = prefPos;
      } else {
          let cat = getPosCategory(p);
          let candidates = [];
          if (cat === 'GK') candidates = availableSlots.filter(s => s === 'GK');
          else if (cat === 'DEF') candidates = availableSlots.filter(s => s.includes('B'));
          else if (cat === 'MID') candidates = availableSlots.filter(s => s.includes('M'));
          else if (cat === 'FWD') candidates = availableSlots.filter(s => s.includes('S') || s.includes('F') || s.includes('W') || s.includes('T'));
          
          if (candidates.length > 0) {
              assignedSlot = candidates[0];
          } else {
              assignedSlot = availableSlots[0];
          }
      }
      
      if (assignedSlot) {
          availableSlots = availableSlots.filter(s => s !== assignedSlot);
          assignedPlayers.push({ player: p, slot: assignedSlot });
      }
  });

  const createPlayerHTML = (p, label, num) => {
    if (!p) return '';
    const lastName = p.name.split(' ').pop();
    let ratingVal = p.efficiency_score !== null ? (p.efficiency_score * 4 + 5.5) : 6.5; 
    let rating = ratingVal.toFixed(1);
    
    let ratingClass = 'rating-yellow';
    if (ratingVal >= 7.0) ratingClass = 'rating-green';
    else if (ratingVal < 6.0) ratingClass = 'rating-red';

    const parts = p.name.split(' ');
    const initials = parts.length > 1 ? parts[0][0] + parts[parts.length-1][0] : parts[0].substring(0, 2);
    
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

  container.innerHTML = ''; // Limpiamos primero

  // Add formation badge
  const badge = document.createElement('div');
  badge.style.cssText = 'position: absolute; top: 1rem; right: 1rem; background: rgba(255,255,255,0.2); padding: 4px 8px; border-radius: 4px; font-weight: bold; color: white; font-size: 0.8rem; border: 1px solid rgba(255,255,255,0.3); z-index: 10; font-family: var(--font-primary);';
  badge.textContent = `Formación: ${formationStr}`;
  container.appendChild(badge);

  // Assign numbers (1 to 11) for display based on Y coordinate to be somewhat realistic
  assignedPlayers.sort((a,b) => SLOT_COORDS[a.slot].y - SLOT_COORDS[b.slot].y);
  
  assignedPlayers.forEach((item, index) => {
      let coords = SLOT_COORDS[item.slot] || { x: 50, y: 50 };
      
      const playerWrapper = document.createElement('div');
      playerWrapper.style.position = 'absolute';
      playerWrapper.style.left = `${coords.x}%`;
      playerWrapper.style.bottom = `${coords.y}%`;
      playerWrapper.style.transform = 'translate(-50%, 50%)'; // Center precisely on coordinate
      playerWrapper.style.zIndex = '10';
      
      let num = index + 1;
      playerWrapper.innerHTML = createPlayerHTML(item.player, item.slot, num);
      container.appendChild(playerWrapper);
  });
}
