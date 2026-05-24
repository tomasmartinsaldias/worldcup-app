import { state } from '../state.js';
import { createFlagElement } from '../utils.js';
import { getCombinedValue } from './matches.js';

// 6. H2H Modal Management
export function openH2HModal(match) {
  const modal = document.getElementById('h2h-modal');
  modal.classList.add('active');
  
  // Set basic details
  document.getElementById('modal-match-title').textContent = `Partido #${match.match_number} &bull; ${match.stage}`;
  document.getElementById('modal-match-score').textContent = match.smartScore.toFixed(1);
  
  // Set rank interest (out of 104 matches)
  if (state.appData && state.appData.matches) {
    const rank = state.appData.matches.findIndex(m => m.match_number === match.match_number) + 1;
    document.getElementById('modal-match-rank').textContent = `#${rank}`;
  }
  
  // Combined squad value
  const combVal = getCombinedValue(match);
  document.getElementById('modal-squad-comb-val').textContent = combVal > 0 ? `${combVal.toFixed(1)} M€` : 'N/A';
  
  // Set teams blocks in VS
  const homeBlock = document.getElementById('modal-team-home');
  const awayBlock = document.getElementById('modal-team-away');
  
  const homeTeamInfo = state.appData.teams[match.home_team.fifa_code];
  const awayTeamInfo = state.appData.teams[match.away_team.fifa_code];
  
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

export function closeModal() {
  document.getElementById('h2h-modal').classList.remove('active');
}
