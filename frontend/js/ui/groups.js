import { state, calculateStandings } from '../futstate.js';
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
    card.style.cssText = 'padding: 1.25rem; background: rgba(18, 18, 26, 0.65); border: 1px solid var(--border-glass); border-radius: 16px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);';
    
    // Calculate dynamic standings
    const standings = calculateStandings(gKey);
    
    let rowsHtml = standings.map((team, idx) => {
      const t = state.appData.teams[team.code];
      const flag = t ? createFlagElement(t) : '';
      const status = state.teamStatuses[team.code] || 'PLAYING_FOR_LIFE';
      
      let rowStyle = '';
      if (idx < 2) {
        rowStyle = 'color: #ffffff;';
      } else if (status === 'ELIMINATED') {
        rowStyle = 'color: var(--text-muted); opacity: 0.7;';
      } else {
        rowStyle = 'color: var(--text-secondary);';
      }
      
      let statusDot = '';
      if (status === 'FIRST_PLACE_ASSURED') {
        statusDot = `<span title="Primer puesto asegurado" style="display:inline-block; width: 6px; height: 6px; border-radius:50%; background: var(--accent-gold); margin-left: 5px; box-shadow: 0 0 6px var(--accent-gold);"></span>`;
      } else if (status === 'QUALIFIED') {
        statusDot = `<span title="Clasificado" style="display:inline-block; width: 6px; height: 6px; border-radius:50%; background: #4ade80; margin-left: 5px; box-shadow: 0 0 6px #4ade80;"></span>`;
      } else if (status === 'ELIMINATED') {
        statusDot = `<span title="Eliminado" style="display:inline-block; width: 6px; height: 6px; border-radius:50%; background: #f87171; margin-left: 5px;"></span>`;
      }
      
      return `
        <tr style="${rowStyle} border-bottom: 1px solid rgba(255,255,255,0.02); cursor: pointer;" onclick="openCountrySquad('${team.code}', 'groups')">
          <td style="padding: 0.6rem 0.3rem; font-weight: bold; text-align: center;">${idx + 1}</td>
          <td style="padding: 0.6rem 0.3rem; display: flex; align-items: center; gap: 0.4rem; font-weight: 600;">
            ${flag}
            <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 110px;">${t ? t.name : team.code}</span>
            ${statusDot}
          </td>
          <td style="padding: 0.6rem 0.3rem; text-align: center;">${team.pj}</td>
          <td style="padding: 0.6rem 0.3rem; text-align: center; font-weight: bold; color: ${team.dg >= 0 ? '#4ade80' : '#f87171'};">${team.dg > 0 ? '+' : ''}${team.dg}</td>
          <td style="padding: 0.6rem 0.3rem; text-align: center; font-weight: 800; font-size: 0.95rem;">${team.pts}</td>
        </tr>
      `;
    }).join('');
    
    card.innerHTML = `
      <div class="group-header" style="margin-bottom: 0.75rem; display: flex; justify-content: space-between; align-items: center;">
        <span style="font-family: var(--font-primary); font-weight: 900; font-size: 1.15rem; color: #ffffff; text-transform: uppercase;">Grupo ${gKey}</span>
        <i class="fa-solid fa-circle-nodes" style="font-size: 0.85rem; color: var(--accent-gold);"></i>
      </div>
      <div class="group-table-wrapper">
        <table style="width: 100%; border-collapse: collapse; font-size: 0.78rem; text-align: left;">
          <thead>
            <tr style="color: var(--text-muted); font-weight: bold; border-bottom: 1px solid var(--border-glass);">
              <th style="padding: 0.4rem 0.3rem; text-align: center; width: 25px;">#</th>
              <th style="padding: 0.4rem 0.3rem;">Equipo</th>
              <th style="padding: 0.4rem 0.3rem; text-align: center; width: 25px;">PJ</th>
              <th style="padding: 0.4rem 0.3rem; text-align: center; width: 30px;">DG</th>
              <th style="padding: 0.4rem 0.3rem; text-align: center; width: 30px;">Pts</th>
            </tr>
          </thead>
          <tbody>
            ${rowsHtml}
          </tbody>
        </table>
      </div>
    `;
    
    container.appendChild(card);
  });
}


