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
    clubIconContainer.innerHTML = '<i class="fa-solid fa-spinner fa-spin" style="color:#666"></i>';
    clubIconContainer.style.background = 'transparent';
    fetch(`https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t=${encodeURIComponent(clubName)}`)
      .then(res => res.json())
      .then(data => {
        if (data.teams && data.teams[0] && data.teams[0].strBadge) {
           clubIconContainer.innerHTML = `<img src="${data.teams[0].strBadge}/preview" style="width: 100%; height: 100%; object-fit: contain;">`;
        } else {
           clubIconContainer.innerHTML = '<i class="fa-solid fa-shield-halved" style="color:#666"></i>';
           clubIconContainer.style.background = '#e0e0e0';
        }
      })
      .catch(() => {
        clubIconContainer.innerHTML = '<i class="fa-solid fa-shield-halved" style="color:#666"></i>';
        clubIconContainer.style.background = '#e0e0e0';
      });
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

  // Rating Sofascore
  let ratingVal = player.efficiency_score !== null ? (player.efficiency_score * 4 + 5.5) : 6.5;
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

