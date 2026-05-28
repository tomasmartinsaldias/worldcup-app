import { state } from '../state.js';
import { createFlagElement } from '../utils.js';

export function openPlayerProfile(teamCode, playerId) {
  const team = state.appData.teams[teamCode];
  if (!team) return;

  const player = team.squad.find(p => p.id === playerId);
  if (!player) return;

  const modal = document.getElementById('player-modal');
  modal.classList.add('active');

  // Header Title
  document.getElementById('player-modal-name-header').textContent = player.name;

  // National Team Block
  const ntFlagContainer = document.getElementById('player-modal-nt-flag');
  ntFlagContainer.innerHTML = '';
  const flag = createFlagElement(team); // Reuse the SVG/emoji logic from squads
  if (typeof flag === 'string') {
    ntFlagContainer.innerHTML = flag;
  } else {
    ntFlagContainer.appendChild(flag);
  }
  document.getElementById('player-modal-nt-name').textContent = team.name;

  // Club Block & Logo API
  const clubName = player.club || '';
  document.getElementById('player-modal-club-name').textContent = clubName || 'Agente Libre';
  
  // Create a dedicated icon container if it doesn't exist, replacing the static shield icon
  let clubIconContainer = document.getElementById('player-modal-club-icon');
  if (!clubIconContainer) {
    const parent = document.getElementById('player-modal-club-name').parentElement.previousElementSibling;
    parent.id = 'player-modal-club-icon';
    clubIconContainer = parent;
  }
  
  if (clubName && clubName !== 'Agente Libre') {
    let logoUrl = null;
    if (state.appData.clubLogos) {
      logoUrl = state.appData.clubLogos[clubName] || state.appData.clubLogos[clubName.toLowerCase()];
    }

    if (logoUrl) {
      clubIconContainer.innerHTML = `<img src="${logoUrl}" style="width: 100%; height: 100%; object-fit: contain;">`;
      clubIconContainer.style.background = 'transparent';
    } else {
      const initial = clubName.charAt(0).toUpperCase();
      clubIconContainer.innerHTML = `<div style="width:100%; height:100%; display:flex; align-items:center; justify-content:center; font-weight:bold; color:white; background:linear-gradient(135deg, var(--fifa-blue), var(--accent-cyan)); font-size:1.2rem;">${initial}</div>`;
      clubIconContainer.style.background = 'transparent';
    }
  } else {
    clubIconContainer.innerHTML = '<i class="fa-solid fa-shield-halved" style="color:#666"></i>';
    clubIconContainer.style.background = '#e0e0e0';
  }

  // Key Stats
  document.getElementById('player-modal-age-val').textContent = player.age ? player.age : '-';
  document.getElementById('player-modal-pos-val').textContent = player.position || '-';
  document.getElementById('player-modal-pos-val').title = player.position || '';
  document.getElementById('player-modal-country-val').textContent = team.name;
  
  const val = player.market_value_eur ? `${player.market_value_eur.toFixed(1)}` : '-';
  document.getElementById('player-modal-market-val').textContent = val;

  document.getElementById('player-modal-caps-val').textContent = player.caps !== null ? player.caps : '-';
  document.getElementById('player-modal-goals-val').textContent = player.goals !== null ? player.goals : '-';

  // Dynamic Form Rating (Sofascore style)
  let ratingVal = 6.5; // default fallback
  
  if (player.minutes_recent && player.minutes_recent > 0) {
    const p90 = 90.0 / player.minutes_recent;
    const xG90 = (player.xG_intl || 0) * p90;
    const sca90 = (player.sca_intl || 0) * p90;
    const gca90 = (player.gca_intl || 0) * p90;
    const progP90 = (player.progressive_passes_intl || 0) * p90;
    const progC90 = (player.progressive_carries_intl || 0) * p90;
    
    let baseScore = 6.0;
    let performance = 0;
    
    const pos = (player.position || '').toLowerCase();
    if (pos.includes('delantero') || pos.includes('forward') || pos.includes('atacante')) {
      performance = (xG90 * 2.0) + (gca90 * 1.5) + (sca90 * 0.2);
    } else if (pos.includes('centrocampista') || pos.includes('midfielder')) {
      performance = (sca90 * 0.4) + (progP90 * 0.15) + (gca90 * 1.0) + (progC90 * 0.1);
    } else if (pos.includes('defensa') || pos.includes('defender')) {
      performance = (progC90 * 0.2) + (progP90 * 0.2) + (sca90 * 0.3);
    } else if (pos.includes('portero') || pos.includes('goalkeeper')) {
      // Goalkeepers use market value and caps as a proxy for form/quality if efficiency is missing or 0
      let gkBase = 1.0;
      if (player.market_value_eur) gkBase += Math.min(player.market_value_eur / 20.0, 1.5);
      if (player.caps) gkBase += Math.min(player.caps / 50.0, 1.0);
      performance = player.efficiency_score ? (player.efficiency_score * 3) : gkBase;
    } else {
      performance = (xG90 * 0.5) + (sca90 * 0.2) + (progP90 * 0.1);
    }
    
    // Add efficiency bonus (derived from external rating or API)
    const effBonus = player.efficiency_score !== null ? (player.efficiency_score * 1.5) : 0;
    
    ratingVal = baseScore + performance + effBonus;
  } else if (player.efficiency_score !== null) {
    // Fallback if no minutes are available
    ratingVal = player.efficiency_score * 4 + 5.5;
  }

  ratingVal = Math.min(Math.max(ratingVal, 5.0), 9.9);
  let ratingStr = ratingVal.toFixed(1);
  const ratingBox = document.getElementById('player-modal-rating-val');
  ratingBox.textContent = ratingStr;
  
  if (ratingVal >= 7.0) {
    ratingBox.style.color = '#4ade80'; // Green text
  } else if (ratingVal < 6.0) {
    ratingBox.style.color = '#f87171'; // Red text
  } else {
    ratingBox.style.color = '#facc15'; // Yellow text
  }
}

export function closePlayerProfile() {
  const modal = document.getElementById('player-modal');
  modal.classList.remove('active');
}

// Bind close event globally
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('close-player-modal-btn').addEventListener('click', closePlayerProfile);
  document.getElementById('player-modal').addEventListener('click', (e) => {
    if (e.target.id === 'player-modal') closePlayerProfile();
  });
});

