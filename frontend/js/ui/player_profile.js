import { state } from '../state.js';
import { calculateFormRating } from '../scoring.js';
import { createFlagElement, getPlayerPhotoUrl } from '../utils.js';

export function openPlayerProfile(teamCode, playerId) {
  const team = state.appData.teams[teamCode];
  if (!team) return;

  const player = team.squad.find(p => p.id === playerId);
  if (!player) return;

  const modal = document.getElementById('player-modal');
  modal.classList.add('active');

  // Header Title
  const photoUrl = getPlayerPhotoUrl(player.name);
  const photoHtml = photoUrl ? `<img src="${photoUrl}" referrerpolicy="no-referrer" style="width: 54px; height: 54px; border-radius: 50%; object-fit: cover; margin-right: 1rem; vertical-align: middle; border: 2px solid #e5e7eb; display: inline-block;" onerror="this.style.display='none'">` : '';
  document.getElementById('player-modal-name-header').innerHTML = `<div style="display: flex; align-items: center;">${photoHtml}<span>${player.name}</span></div>`;

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

