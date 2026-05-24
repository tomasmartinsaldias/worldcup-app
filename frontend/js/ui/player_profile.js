import { state } from '../state.js';

let radarChart = null;

export function openPlayerProfile(teamCode, playerId) {
  const team = state.appData.teams[teamCode];
  if (!team) return;

  const player = team.squad.find(p => p.id === playerId);
  if (!player) return;

  const modal = document.getElementById('player-modal');
  modal.classList.add('active');

  // Basic Info
  const parts = player.name.split(' ');
  const initials = parts.length > 1 ? parts[0][0] + parts[parts.length-1][0] : parts[0].substring(0, 2);
  
  document.getElementById('player-modal-photo').innerHTML = `<span>${initials.toUpperCase()}</span>`;
  document.getElementById('player-modal-name').textContent = player.name;
  document.getElementById('player-modal-club').textContent = player.club || 'Agente Libre';
  document.getElementById('player-modal-age').innerHTML = `<i class="fa-solid fa-calendar"></i> ${player.age || 'N/A'} años`;
  document.getElementById('player-modal-pos').innerHTML = `<i class="fa-solid fa-shirt"></i> ${player.position || 'N/A'}`;

  // Market Value
  const val = player.market_value_eur ? `${player.market_value_eur.toFixed(1)} M€` : 'N/A';
  document.getElementById('player-modal-val').textContent = val;

  // Rating Sofascore
  let ratingVal = player.efficiency_score !== null ? (player.efficiency_score * 4 + 5.5) : 6.5;
  let ratingStr = ratingVal.toFixed(1);
  const ratingBox = document.getElementById('player-modal-rating');
  ratingBox.textContent = ratingStr;
  
  if (ratingVal >= 7.0) {
    ratingBox.style.backgroundColor = '#2e7d32'; // Green
    ratingBox.style.color = '#fff';
  } else if (ratingVal < 6.0) {
    ratingBox.style.backgroundColor = '#c62828'; // Red
    ratingBox.style.color = '#fff';
  } else {
    ratingBox.style.backgroundColor = '#fbc02d'; // Yellow
    ratingBox.style.color = '#333';
  }

  // Draw Radar Chart
  drawRadarChart(player, ratingVal);
}

export function closePlayerProfile() {
  const modal = document.getElementById('player-modal');
  modal.classList.remove('active');
}

function drawRadarChart(player, ratingVal) {
  const ctx = document.getElementById('playerRadarChart').getContext('2d');
  
  if (radarChart) {
    radarChart.destroy();
  }

  // Calculate stats deterministically based on real data
  const base = ratingVal * 10; // 65 - 95
  
  let atk = base;
  let def = base;
  let pas = base;
  let phy = base;
  let tac = base;

  const pos = (player.position || '').toLowerCase();
  if (pos.includes('delantero') || pos.includes('ataque')) {
    atk += 15; def -= 25; pas += 5;
  } else if (pos.includes('defensa') || pos.includes('central') || pos.includes('lateral')) {
    atk -= 20; def += 20; phy += 10; tac += 5;
  } else if (pos.includes('medio') || pos.includes('centro') || pos.includes('pivote')) {
    pas += 20; tac += 15; atk -= 5;
  } else if (pos.includes('portero')) {
    atk = 15; def = 85; pas = 60; phy = 70; tac = 85;
  }

  // Apply actual statistics modifiers (Deterministic)
  const goals = player.goals || 0;
  const assists = player.assists_recent || 0;
  const minutes = player.minutes_recent || 0;
  const caps = player.caps || 0;
  
  // Attack is influenced by actual goals scored
  if (goals > 0) atk += Math.min(goals * 2, 20);
  
  // Passing is influenced by recent assists
  if (assists > 0) pas += Math.min(assists * 5, 20);
  
  // Physicality scales with minutes played recently
  if (minutes > 0) phy += Math.min(minutes / 100, 15);
  else phy -= 10; // Penalize physicality if 0 minutes
  
  // Tactics/Experience scales with international caps
  if (caps > 0) tac += Math.min(caps / 5, 15);

  // Hard Cap min 30, max 99 (No Math.random used)
  const cap = (v) => Math.min(Math.max(v, 30), 99);

  const data = {
    labels: ['Ataque', 'Técnica/Pase', 'Defensa', 'Físico', 'Táctica'],
    datasets: [{
      label: 'Atributos Generales',
      data: [cap(atk), cap(pas), cap(def), cap(phy), cap(tac)],
      fill: true,
      backgroundColor: 'rgba(211, 32, 42, 0.2)',
      borderColor: 'rgb(211, 32, 42)',
      pointBackgroundColor: 'rgb(211, 32, 42)',
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: 'rgb(211, 32, 42)'
    }]
  };

  const config = {
    type: 'radar',
    data: data,
    options: {
      elements: {
        line: {
          borderWidth: 2
        }
      },
      scales: {
        r: {
          angleLines: {
            display: true
          },
          suggestedMin: 30,
          suggestedMax: 100
        }
      },
      plugins: {
        legend: { display: false }
      }
    },
  };

  radarChart = new Chart(ctx, config);
}

// Bind close event globally
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('close-player-modal-btn').addEventListener('click', closePlayerProfile);
  document.getElementById('player-modal').addEventListener('click', (e) => {
    if (e.target.id === 'player-modal') closePlayerProfile();
  });
});
