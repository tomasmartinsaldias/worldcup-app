import { state, getSimulatedScores, saveSimulatedScore, clearAllSimulatedScores, recalculateTournamentState, calculateStandings } from '../state.js';
import { createFlagElement } from '../utils.js';

let selectedGroupFilter = 'all'; // 'all' or 'A'-'L'

export function renderResults() {
  const container = document.getElementById('tab-results');
  if (!container || !state.appData) return;

  // Render HTML structure if not already present
  if (!container.querySelector('.results-layout-wrapper')) {
    container.innerHTML = `
      <div class="hero-section">
        <div class="hero-tag">Resultados y Simulación</div>
        <h2 class="hero-title">Simulador de Fase de Grupos</h2>
        <p class="hero-desc">Carga marcadores para actualizar posiciones, ELO dinámico con momentum (EMA) y multiplicadores de espectáculo en tiempo real.</p>
      </div>

      <div class="results-layout-wrapper">
        <div class="results-controls-bar" style="display: flex; justify-content: space-between; align-items: center; background: rgba(18, 18, 26, 0.65); border: 1px solid var(--border-glass); padding: 1.2rem 1.8rem; border-radius: 16px; margin-bottom: 2rem; flex-wrap: wrap; gap: 1rem;">
          <div class="results-stats" id="results-stats-container" style="color: var(--text-secondary); font-size: 0.9rem; font-family: var(--font-secondary); font-weight: 500;">
            Cargando estadísticas de simulación...
          </div>
          <div class="results-actions" style="display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center;">
            <button class="btn-mundial btn-mundial--green" id="btn-simulate-j1" style="padding: 0.6rem 1.2rem; display: inline-flex; align-items: center; gap: 0.4rem; border-radius: 50px; font-size: 0.85rem; font-weight: bold; cursor: pointer;">
              Simular J1
            </button>
            <button class="btn-mundial btn-mundial--green" id="btn-simulate-j2" style="padding: 0.6rem 1.2rem; display: inline-flex; align-items: center; gap: 0.4rem; border-radius: 50px; font-size: 0.85rem; font-weight: bold; cursor: pointer;">
              Simular J2
            </button>
            <button class="btn-mundial btn-mundial--green" id="btn-simulate-j3" style="padding: 0.6rem 1.2rem; display: inline-flex; align-items: center; gap: 0.4rem; border-radius: 50px; font-size: 0.85rem; font-weight: bold; cursor: pointer;">
              Simular J3
            </button>
            <button class="btn-mundial btn-mundial--green" id="btn-simulate-remaining" style="padding: 0.6rem 1.2rem; display: inline-flex; align-items: center; gap: 0.4rem; border-radius: 50px; font-size: 0.85rem; font-weight: bold; cursor: pointer; background: var(--accent-cyan); border-color: var(--accent-cyan); color: #000;">
              <i class="fa-solid fa-wand-magic-sparkles"></i> Simular Restantes
            </button>
            <button class="btn-mundial btn-mundial--outline" id="btn-reset-simulator" style="padding: 0.6rem 1.2rem; border-color: rgba(232, 35, 26, 0.4); color: var(--wc-red); display: inline-flex; align-items: center; gap: 0.4rem; border-radius: 50px; font-size: 0.85rem; font-weight: bold; cursor: pointer;">
              <i class="fa-solid fa-trash-can"></i> Limpiar
            </button>
          </div>
        </div>

        <div class="results-group-selector" style="display: flex; gap: 0.4rem; margin-bottom: 2rem; overflow-x: auto; padding-bottom: 0.6rem; scrollbar-width: thin;">
          <button class="btn-mundial btn-mundial--outline group-filter-btn active" data-group="all" style="padding: 0.5rem 1.2rem; font-size: 0.8rem; border-radius: 50px; font-weight: 700;">Todos los Grupos</button>
          ${'ABCDEFGHIJKL'.split('').map(g => `
            <button class="btn-mundial btn-mundial--outline group-filter-btn" data-group="${g}" style="padding: 0.5rem 1rem; font-size: 0.8rem; border-radius: 50px; font-weight: 700;">Grupo ${g}</button>
          `).join('')}
        </div>

        <div class="results-groups-list" id="results-groups-grid" style="display: flex; flex-direction: column; gap: 3rem;">
          <!-- Inyectado por JS -->
        </div>
      </div>
    `;

    // Bind event listeners
    document.getElementById('btn-simulate-j1').addEventListener('click', () => simulateRound(1));
    document.getElementById('btn-simulate-j2').addEventListener('click', () => simulateRound(2));
    document.getElementById('btn-simulate-j3').addEventListener('click', () => simulateRound(3));
    document.getElementById('btn-simulate-remaining').addEventListener('click', simulateRemainingMatches);
    document.getElementById('btn-reset-simulator').addEventListener('click', () => {
      if (confirm('¿Estás seguro de que quieres borrar todos los marcadores simulados?')) {
        clearAllSimulatedScores();
        if (window.recalculateAndRender) window.recalculateAndRender();
        renderResults();
      }
    });

    container.querySelectorAll('.group-filter-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        container.querySelectorAll('.group-filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        selectedGroupFilter = btn.getAttribute('data-group');
        renderGroupsContent();
      });
    });
  }

  updateStatsBar();
  renderGroupsContent();
}

function updateStatsBar() {
  const statsContainer = document.getElementById('results-stats-container');
  if (!statsContainer || !state.appData) return;

  const simulatedScores = getSimulatedScores();
  const totalMatches = state.appData.matches.length;
  const playedCount = Object.keys(simulatedScores).length;

  let totalGoals = 0;
  Object.values(simulatedScores).forEach(score => {
    totalGoals += (score.home || 0) + (score.away || 0);
  });

  const avgGoals = playedCount > 0 ? (totalGoals / playedCount).toFixed(2) : '0.00';

  statsContainer.innerHTML = `
    <span style="margin-right: 1.5rem;"><i class="fa-solid fa-circle-play" style="color: var(--accent-cyan); margin-right: 4px;"></i> Simulados: <strong>${playedCount} / ${totalMatches}</strong></span>
    <span><i class="fa-solid fa-soccer-ball" style="color: var(--accent-gold); margin-right: 4px;"></i> Goles Totales: <strong>${totalGoals}</strong> (Promedio: <strong>${avgGoals}</strong>)</span>
  `;
}

function renderGroupsContent() {
  const grid = document.getElementById('results-groups-grid');
  if (!grid || !state.appData || !state.appData.groups) return;

  // Save the currently focused element's details to restore focus later
  const activeEl = document.activeElement;
  let focusedMatch = null;
  let focusedTeam = null;
  if (activeEl && activeEl.classList.contains('sim-score-input')) {
    focusedMatch = activeEl.getAttribute('data-match');
    focusedTeam = activeEl.getAttribute('data-team');
  }

  grid.innerHTML = '';
  const simulatedScores = getSimulatedScores();

  const groupKeys = Object.keys(state.appData.groups).sort();
  const filteredKeys = selectedGroupFilter === 'all' ? groupKeys : [selectedGroupFilter];

  filteredKeys.forEach(gKey => {
    const groupCard = document.createElement('div');
    groupCard.className = 'results-group-card';
    groupCard.style.cssText = 'background: rgba(12, 12, 16, 0.4); border: 1px solid var(--border-glass); border-radius: 20px; padding: 2rem; display: flex; flex-direction: column; gap: 2rem; box-shadow: 0 8px 32px rgba(0,0,0,0.4);';

    // Calculate dynamic standings
    const standings = calculateStandings(gKey);

    // Render Standings Table
    let tableRowsHtml = standings.map((team, idx) => {
      const elo = state.teamElos[team.code] || 1500;
      const status = state.teamStatuses[team.code] || 'PLAYING_FOR_LIFE';
      
      let statusBadge = '';
      if (status === 'FIRST_PLACE_ASSURED') {
        statusBadge = `<span class="status-pill status-1st" style="background: rgba(251, 191, 36, 0.15); border: 1px solid rgba(251, 191, 36, 0.3); color: var(--accent-gold); padding: 2px 8px; border-radius: 50px; font-size: 0.65rem; font-weight: bold;">1° Asegurado</span>`;
      } else if (status === 'QUALIFIED') {
        statusBadge = `<span class="status-pill status-ok" style="background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.3); color: #4ade80; padding: 2px 8px; border-radius: 50px; font-size: 0.65rem; font-weight: bold;">Clasificado</span>`;
      } else if (status === 'ELIMINATED') {
        statusBadge = `<span class="status-pill status-out" style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #f87171; padding: 2px 8px; border-radius: 50px; font-size: 0.65rem; font-weight: bold;">Eliminado</span>`;
      } else {
        statusBadge = `<span class="status-pill status-fighting" style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); color: var(--text-secondary); padding: 2px 8px; border-radius: 50px; font-size: 0.65rem; font-weight: bold;">En pelea</span>`;
      }

      const teamData = state.appData.teams[team.code] || {};
      const flag = createFlagElement(teamData);

      let rowHighlightStyle = '';
      if (idx < 2) {
        rowHighlightStyle = 'background: rgba(34, 197, 94, 0.02);';
      } else if (status === 'ELIMINATED') {
        rowHighlightStyle = 'background: rgba(239, 68, 68, 0.01); opacity: 0.65;';
      }

      return `
        <tr style="${rowHighlightStyle} border-bottom: 1px solid rgba(255,255,255,0.02); transition: background 0.3s;">
          <td style="padding: 0.8rem 0.5rem; text-align: center; font-weight: bold; color: ${idx < 2 ? 'var(--accent-gold)' : 'var(--text-muted)'};">${idx + 1}</td>
          <td style="padding: 0.8rem 0.5rem; display: flex; align-items: center; gap: 0.6rem; font-weight: 600;">
            ${flag}
            <span>${team.name}</span>
          </td>
          <td style="padding: 0.8rem 0.5rem; text-align: center;">${team.pj}</td>
          <td style="padding: 0.8rem 0.5rem; text-align: center; color: #4ade80;">${team.pg}</td>
          <td style="padding: 0.8rem 0.5rem; text-align: center; color: var(--text-muted);">${team.pe}</td>
          <td style="padding: 0.8rem 0.5rem; text-align: center; color: #f87171;">${team.pp}</td>
          <td style="padding: 0.8rem 0.5rem; text-align: center; font-size: 0.85rem;">${team.gf}:${team.gc}</td>
          <td style="padding: 0.8rem 0.5rem; text-align: center; font-weight: bold; color: ${team.dg >= 0 ? '#4ade80' : '#f87171'}">${team.dg > 0 ? '+' : ''}${team.dg}</td>
          <td style="padding: 0.8rem 0.5rem; text-align: center; font-weight: 800; color: #ffffff; font-size: 1rem;">${team.pts}</td>
          <td style="padding: 0.8rem 0.5rem; text-align: center; font-weight: 700; color: var(--accent-cyan); font-size: 0.9rem;">${elo}</td>
          <td style="padding: 0.8rem 0.5rem; text-align: center;">${statusBadge}</td>
        </tr>
      `;
    }).join('');

    const standingsTableHtml = `
      <div style="overflow-x: auto; border-radius: 12px; border: 1px solid var(--border-glass);">
        <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem; text-align: left; background: rgba(0, 0, 0, 0.25);">
          <thead>
            <tr style="background: rgba(255,255,255,0.02); border-bottom: 1.5px solid var(--border-glass); color: var(--text-muted); font-weight: bold;">
              <th style="padding: 0.8rem 0.5rem; text-align: center; width: 40px;">#</th>
              <th style="padding: 0.8rem 0.5rem;">Equipo</th>
              <th style="padding: 0.8rem 0.5rem; text-align: center; width: 40px;">PJ</th>
              <th style="padding: 0.8rem 0.5rem; text-align: center; width: 40px;">PG</th>
              <th style="padding: 0.8rem 0.5rem; text-align: center; width: 40px;">PE</th>
              <th style="padding: 0.8rem 0.5rem; text-align: center; width: 40px;">PP</th>
              <th style="padding: 0.8rem 0.5rem; text-align: center; width: 60px;">Goles</th>
              <th style="padding: 0.8rem 0.5rem; text-align: center; width: 40px;">DG</th>
              <th style="padding: 0.8rem 0.5rem; text-align: center; width: 50px;">Pts</th>
              <th style="padding: 0.8rem 0.5rem; text-align: center; width: 70px;">ELO</th>
              <th style="padding: 0.8rem 0.5rem; text-align: center; width: 120px;">Estado</th>
            </tr>
          </thead>
          <tbody>
            ${tableRowsHtml}
          </tbody>
        </table>
      </div>
    `;

    // Find group matches
    const groupMatches = state.appData.matches.filter(m => 
      m.stage === 'Group Stage' && 
      m.home_team.group === gKey && 
      !m.home_team.is_placeholder && 
      !m.away_team.is_placeholder
    ).sort((a, b) => a.match_number - b.match_number);

    // Render matches grid
    let matchesHtml = groupMatches.map(m => {
      const score = simulatedScores[m.match_number];
      const hStatus = state.teamStatuses[m.home_team.fifa_code] || 'PLAYING_FOR_LIFE';
      const aStatus = state.teamStatuses[m.away_team.fifa_code] || 'PLAYING_FOR_LIFE';

      // Stake Multiplier calculation
      const statusMultipliers = {
        'PLAYING_FOR_LIFE': 1.0,
        'QUALIFIED': 0.85,
        'FIRST_PLACE_ASSURED': 0.70,
        'ELIMINATED': 0.60
      };
      
      const mHome = statusMultipliers[hStatus] || 1.0;
      const mAway = statusMultipliers[aStatus] || 1.0;
      const matchStakeMultiplier = (mHome + mAway) / 2;

      let stakeClass = 'stake-normal';
      let stakeText = 'Normal';
      let stakeColor = 'var(--text-secondary)';
      if (matchStakeMultiplier >= 1.0) {
        stakeClass = 'stake-high';
        stakeText = 'Máxima Tensión';
        stakeColor = 'var(--accent-gold)';
      } else if (matchStakeMultiplier <= 0.75) {
        stakeClass = 'stake-low';
        stakeText = 'Bajo Interés';
        stakeColor = '#f87171';
      } else {
        stakeText = 'Moderado';
        stakeColor = 'var(--accent-cyan)';
      }

      // ELO change indicators
      let eloChangeHome = '';
      let eloChangeAway = '';
      if (score !== undefined && m.home_team_elo_post !== undefined && m.home_team_elo_pre !== undefined) {
        const diffH = m.home_team_elo_post - m.home_team_elo_pre;
        const diffA = m.away_team_elo_post - m.away_team_elo_pre;
        eloChangeHome = `<span style="font-size:0.7rem; margin-left: 5px; font-weight:bold; color: ${diffH >= 0 ? '#4ade80' : '#f87171'};">${diffH >= 0 ? '+' : ''}${diffH}</span>`;
        eloChangeAway = `<span style="font-size:0.7rem; margin-left: 5px; font-weight:bold; color: ${diffA >= 0 ? '#4ade80' : '#f87171'};">${diffA >= 0 ? '+' : ''}${diffA}</span>`;
      }

      const hTeamData = state.appData.teams[m.home_team.fifa_code] || {};
      const aTeamData = state.appData.teams[m.away_team.fifa_code] || {};
      const flagHome = createFlagElement(hTeamData);
      const flagAway = createFlagElement(aTeamData);

      return `
        <div class="results-match-row" style="background: rgba(255, 255, 255, 0.01); border: 1px solid var(--border-glass); border-radius: 12px; padding: 1rem 1.5rem; display: flex; align-items: center; justify-content: space-between; transition: all 0.3s; gap: 1rem; flex-wrap: wrap;">
          <div style="flex: 1; min-width: 150px; display: flex; flex-direction: column; gap: 0.2rem;">
            <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: bold; text-transform: uppercase;">Partido #${m.match_number}</span>
            <span style="font-size: 0.8rem; color: var(--text-secondary); font-family: var(--font-secondary);"><i class="fa-solid fa-map-location-dot" style="margin-right: 4px; font-size: 0.75rem;"></i> ${m.stadium?.venue_name || 'TBD'}</span>
          </div>

          <!-- Team Home -->
          <div style="flex: 2; min-width: 160px; display: flex; align-items: center; justify-content: flex-end; gap: 0.8rem; text-align: right;">
            <div style="line-height: 1.2;">
              <div style="font-weight: 700; font-size: 0.95rem; color: #ffffff;">${m.home_team.name}</div>
              <div style="font-size: 0.75rem; color: var(--text-muted); font-family: var(--font-secondary);">ELO: <strong style="color: var(--accent-cyan);">${m.home_team_elo_pre || 1500}</strong>${eloChangeHome}</div>
            </div>
            ${flagHome}
          </div>

          <!-- Score Input Box -->
          <div style="display: flex; align-items: center; gap: 0.5rem; background: rgba(0, 0, 0, 0.3); border: 1.5px solid var(--border-glass); padding: 0.4rem 0.8rem; border-radius: 10px;">
            <input type="number" min="0" max="99" class="sim-score-input" data-match="${m.match_number}" data-team="home" value="${score !== undefined ? score.home : ''}" placeholder="-" style="width: 38px; background: transparent; border: none; text-align: center; color: #ffffff; font-weight: 800; font-size: 1.2rem; font-family: var(--font-primary); outline: none;">
            <span style="color: var(--border-glass); font-weight: bold;">:</span>
            <input type="number" min="0" max="99" class="sim-score-input" data-match="${m.match_number}" data-team="away" value="${score !== undefined ? score.away : ''}" placeholder="-" style="width: 38px; background: transparent; border: none; text-align: center; color: #ffffff; font-weight: 800; font-size: 1.2rem; font-family: var(--font-primary); outline: none;">
          </div>

          <!-- Team Away -->
          <div style="flex: 2; min-width: 160px; display: flex; align-items: center; justify-content: flex-start; gap: 0.8rem;">
            ${flagAway}
            <div style="line-height: 1.2;">
              <div style="font-weight: 700; font-size: 0.95rem; color: #ffffff;">${m.away_team.name}</div>
              <div style="font-size: 0.75rem; color: var(--text-muted); font-family: var(--font-secondary);">ELO: <strong style="color: var(--accent-cyan);">${m.away_team_elo_pre || 1500}</strong>${eloChangeAway}</div>
            </div>
          </div>

          <!-- Match Stakes -->
          <div style="flex: 1.2; min-width: 120px; text-align: right; display: flex; flex-direction: column; align-items: flex-end; gap: 0.2rem;">
            <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: bold;">Multiplicador</span>
            <span class="results-stake-badge ${stakeClass}" style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-glass); color: ${stakeColor}; padding: 2px 10px; border-radius: 50px; font-size: 0.75rem; font-weight: bold; font-family: var(--font-primary); display: inline-flex; align-items: center; gap: 4px;">
              <i class="fa-solid fa-scale-balanced" style="font-size:0.65rem;"></i> ${matchStakeMultiplier.toFixed(2)}x
            </span>
          </div>
        </div>
      `;
    }).join('');

    groupCard.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid var(--border-glass); padding-bottom: 1rem; margin-bottom: 0.5rem;">
        <h2 style="font-family: var(--font-primary); font-size: 1.8rem; font-weight: 900; color: #ffffff; text-transform: uppercase; letter-spacing: 0.05em; margin: 0;">Grupo ${gKey}</h2>
        <span style="font-size: 0.85rem; color: var(--text-muted); font-family: var(--font-secondary);"><i class="fa-solid fa-circle-nodes" style="color: var(--accent-gold); margin-right: 4px;"></i> Posiciones Dinámicas</span>
      </div>
      
      ${standingsTableHtml}
      
      <div style="display: flex; flex-direction: column; gap: 0.75rem; margin-top: 0.5rem;">
        <h3 style="font-family: var(--font-primary); font-size: 1rem; font-weight: 800; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;"><i class="fa-solid fa-calendar-days" style="color: var(--accent-cyan); margin-right: 6px;"></i> Calendario del Grupo</h3>
        ${matchesHtml}
      </div>
    `;

    grid.appendChild(groupCard);
  });

  // Bind inputs event listeners
  grid.querySelectorAll('.sim-score-input').forEach(input => {
    const handleScoreChange = (e) => {
      const mNum = parseInt(input.getAttribute('data-match'));
      const team = input.getAttribute('data-team');
      const val = input.value;

      // Find match and update
      const simulatedScores = getSimulatedScores();
      const current = simulatedScores[mNum] || { home: null, away: null };

      if (val === '') {
        current[team] = null;
      } else {
        current[team] = parseInt(val);
      }

      if (current.home === null || current.away === null || isNaN(current.home) || isNaN(current.away)) {
        saveSimulatedScore(mNum, null, null);
      } else {
        saveSimulatedScore(mNum, current.home, current.away);
      }

      if (window.recalculateAndRender) window.recalculateAndRender();
      updateStatsBar();
      renderGroupsContent();
    };

    input.addEventListener('change', handleScoreChange);
    input.addEventListener('input', handleScoreChange);

    // Prevent negative numbers and e/E keys
    input.addEventListener('keydown', (e) => {
      if (['e', 'E', '+', '-', '.'].includes(e.key)) {
        e.preventDefault();
      }
    });
  });

  // Restore focus if it was focused before redrawing
  if (focusedMatch && focusedTeam) {
    const newInput = grid.querySelector(`.sim-score-input[data-match="${focusedMatch}"][data-team="${focusedTeam}"]`);
    if (newInput) {
      newInput.focus();
    }
  }
}

function simulateRemainingMatches() {
  if (!state.appData || !state.appData.matches) return;

  const simulatedScores = getSimulatedScores();
  let count = 0;

  // Recalculate states to get initial updated ELOs
  recalculateTournamentState();

  const sortedMatches = [...state.appData.matches].sort((a, b) => a.match_number - b.match_number);

  sortedMatches.forEach(m => {
    if (m.home_team.is_placeholder || m.away_team.is_placeholder) return;
    if (simulatedScores[m.match_number] !== undefined) return; // Skip already played

    const hCode = m.home_team.fifa_code;
    const aCode = m.away_team.fifa_code;

    const eloH = state.teamElos[hCode] || 1500;
    const eloA = state.teamElos[aCode] || 1500;

    // Calculate win expectation as win probability weight
    const diff = (eloH - eloA) / 400;
    const We_h = 1 / (1 + Math.pow(10, -diff));

    // Base probabilities
    const P_draw = 0.26;
    const P_home = 0.74 * We_h;
    const P_away = 0.74 * (1.0 - We_h);

    const r = Math.random();

    let scoreHome = 0;
    let scoreAway = 0;

    if (r < P_home) {
      // Home win
      scoreHome = Math.floor(Math.random() * 3) + 1; // 1 to 3 goals
      scoreAway = Math.floor(Math.random() * scoreHome); // less than home score
    } else if (r < P_home + P_draw) {
      // Draw
      scoreHome = Math.floor(Math.random() * 3); // 0 to 2 goals
      scoreAway = scoreHome;
    } else {
      // Away win
      scoreAway = Math.floor(Math.random() * 3) + 1; // 1 to 3 goals
      scoreHome = Math.floor(Math.random() * scoreAway); // less than away score
    }

    // Save score (manually update simulatedScores local list and recalculate at the end for efficiency)
    simulatedScores[m.match_number] = {
      home: scoreHome,
      away: scoreAway
    };
    count++;
  });

  if (count > 0) {
    localStorage.setItem('simulatedScores', JSON.stringify(simulatedScores));
    recalculateTournamentState();
    if (window.recalculateAndRender) window.recalculateAndRender();
    renderResults();
    alert(`¡Simulados con éxito ${count} partidos restantes usando pesos ELO!`);
  } else {
    alert('Todos los partidos ya tienen marcadores cargados.');
  }
}

function simulateRound(roundNumber) {
  if (!state.appData || !state.appData.matches) return;

  const simulatedScores = getSimulatedScores();
  let count = 0;

  // Recalculate states to get initial updated ELOs
  recalculateTournamentState();

  const sortedMatches = [...state.appData.matches].sort((a, b) => a.match_number - b.match_number);

  // Define match bounds for the specified round (Jornada)
  let minMatch = 1;
  let maxMatch = 72;
  if (roundNumber === 1) {
    minMatch = 1;
    maxMatch = 24;
  } else if (roundNumber === 2) {
    minMatch = 25;
    maxMatch = 48;
  } else if (roundNumber === 3) {
    minMatch = 49;
    maxMatch = 72;
  }

  sortedMatches.forEach(m => {
    if (m.home_team.is_placeholder || m.away_team.is_placeholder) return;
    if (m.match_number < minMatch || m.match_number > maxMatch) return;
    if (simulatedScores[m.match_number] !== undefined) return; // Skip already played

    const hCode = m.home_team.fifa_code;
    const aCode = m.away_team.fifa_code;

    const eloH = state.teamElos[hCode] || 1500;
    const eloA = state.teamElos[aCode] || 1500;

    // Calculate win expectation as win probability weight
    const diff = (eloH - eloA) / 400;
    const We_h = 1 / (1 + Math.pow(10, -diff));

    // Base probabilities
    const P_draw = 0.26;
    const P_home = 0.74 * We_h;
    const P_away = 0.74 * (1.0 - We_h);

    const r = Math.random();

    let scoreHome = 0;
    let scoreAway = 0;

    if (r < P_home) {
      // Home win
      scoreHome = Math.floor(Math.random() * 3) + 1; // 1 to 3 goals
      scoreAway = Math.floor(Math.random() * scoreHome); // less than home score
    } else if (r < P_home + P_draw) {
      // Draw
      scoreHome = Math.floor(Math.random() * 3); // 0 to 2 goals
      scoreAway = scoreHome;
    } else {
      // Away win
      scoreAway = Math.floor(Math.random() * 3) + 1; // 1 to 3 goals
      scoreHome = Math.floor(Math.random() * scoreAway); // less than away score
    }

    // Save score
    simulatedScores[m.match_number] = {
      home: scoreHome,
      away: scoreAway
    };
    count++;
  });

  if (count > 0) {
    localStorage.setItem('simulatedScores', JSON.stringify(simulatedScores));
    recalculateTournamentState();
    if (window.recalculateAndRender) window.recalculateAndRender();
    renderResults();
    alert(`¡Simulados con éxito ${count} partidos de la Jornada ${roundNumber} usando pesos ELO!`);
  } else {
    alert(`Todos los partidos de la Jornada ${roundNumber} ya tienen marcadores cargados.`);
  }
}

