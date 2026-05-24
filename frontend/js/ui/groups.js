import { state } from '../state.js';
import { createFlagElement } from '../utils.js';
import { openCountrySquad } from './squads.js';

// 2. Render Groups Tab
export function renderGroups() {
  const container = document.getElementById('groups-container');
  if (!state.appData || !state.appData.groups) return;
  
  container.innerHTML = '';
  
  // Groups are A to L
  const sortedGroupKeys = Object.keys(state.appData.groups).sort();
  
  sortedGroupKeys.forEach(gKey => {
    const card = document.createElement('div');
    card.className = 'group-card';
    
    let teamItemsHtml = '';
    state.appData.groups[gKey].forEach(code => {
      const t = state.appData.teams[code];
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


