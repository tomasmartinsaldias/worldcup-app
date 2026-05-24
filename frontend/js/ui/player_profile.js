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

  // Generate some realistic fake stats based on position and rating if we don't have detailed FBref data
  // In a real app, these would come directly from the JSON.
  const base = ratingVal * 10; // 65 - 95
  
  let atk = base;
  let def = base;
  let pas = base;
  let phy = base;
  let tac = base;

  const pos = (player.position || '').toLowerCase();
  if (pos.includes('delantero') || pos.includes('ataque')) {
    atk += 10; def -= 20; pas += 5;
  } else if (pos.includes('defensa') || pos.includes('central')) {
    atk -= 20; def += 15; phy += 10;
  } else if (pos.includes('medio') || pos.includes('centro')) {
    pas += 15; tac += 10; atk -= 5;
  } else if (pos.includes('portero')) {
    atk = 10; def = 85; pas = 60; phy = 70; tac = 80;
  }

  // Cap at 99
  const cap = (v) => Math.min(Math.max(v + (Math.random()*10 - 5), 40), 99);

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
