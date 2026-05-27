import { state } from './state.js';
import { calculateSmartScore } from './recommender.js?v=2';
import { renderMatches, filterMatches, sortMatchesList } from './ui/matches.js?v=2';
import { renderGroups } from './ui/groups.js?v=2';
import { renderCountries, filterTeams, closeSquadDetails, openCountrySquad } from './ui/squads.js?v=2';
import { renderUnresolved } from './ui/unresolved.js?v=2';
import { closeModal } from './ui/modal.js';
import { openPlayerProfile } from './ui/player_profile.js';

window.openCountrySquad = openCountrySquad;
window.openPlayerProfile = openPlayerProfile;

document.addEventListener('DOMContentLoaded', () => {
  setupTabListeners();
  loadData();
  
  const savedSort = localStorage.getItem('sort-matches');
  if (savedSort) document.getElementById('sort-matches').value = savedSort;
  
  // Filter and Search Listeners
  document.getElementById('search-matches').addEventListener('input', filterMatches);
  document.getElementById('filter-stage').addEventListener('change', filterMatches);
  document.getElementById('filter-region').addEventListener('change', filterMatches);
  document.getElementById('sort-matches').addEventListener('change', (e) => {
      localStorage.setItem('sort-matches', e.target.value);
      filterMatches();
  });
  
  document.getElementById('search-teams').addEventListener('input', filterTeams);
  document.getElementById('back-to-countries-btn').addEventListener('click', closeSquadDetails);
  
  document.getElementById('close-modal-btn').addEventListener('click', closeModal);
  document.getElementById('h2h-modal').addEventListener('click', (e) => {
    if (e.target.id === 'h2h-modal') closeModal();
  });
  
  setupPreferenceListeners();
});

function setupTabListeners() {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      switchTab(targetTab);
    });
  });
  
  document.getElementById('app-logo').addEventListener('click', (e) => {
    e.preventDefault();
    switchTab('recommender');
  });
  
  // Initial tab set from state
  switchTab(state.activeTab);
}

function switchTab(tabName) {
  state.activeTab = tabName;
  
  document.querySelectorAll('.nav-btn').forEach(btn => {
    if (btn.getAttribute('data-tab') === tabName) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
  
  document.querySelectorAll('.tab-panel').forEach(panel => {
    panel.classList.remove('active');
  });
  
  const squadDetailsView = document.getElementById('squad-details-view');
  squadDetailsView.classList.remove('active');
  
  if (tabName === 'squads' && state.selectedCountryCode !== null) {
    squadDetailsView.classList.add('active');
  } else {
    const targetPanel = document.getElementById(`tab-${tabName}`);
    if (targetPanel) targetPanel.classList.add('active');
  }
}

async function loadData() {
  const container = document.getElementById('matches-container');
  // Loading skeleton state
  container.innerHTML = `<div class="skeleton-loader">
    <div class="skeleton-card"></div>
    <div class="skeleton-card"></div>
    <div class="skeleton-card"></div>
  </div>`;
  
  try {
    const response = await fetch('../data/wc2026_data.json?t=' + new Date().getTime());
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    state.appData = await response.json();
    populateTeamPreference();
    
    state.appData.matches.forEach(m => {
      m.smartScore = calculateSmartScore(m, state.appData.teams);
    });
    
    sortMatchesList(document.getElementById('sort-matches').value || 'interest-desc');
    
    renderMatches();
    renderGroups();
    renderCountries();
    renderUnresolved();
    
  } catch (error) {
    console.error("No se pudieron cargar los datos del Mundial:", error);
    container.innerHTML = `
      <div class="error-state-card">
        <i class="fa-solid fa-server-slash error-icon"></i>
        <h3>Error de Conexión</h3>
        <p>No se pudo cargar el archivo local de datos.</p>
        <button onclick="location.reload()" class="retry-btn">Reintentar</button>
      </div>`;
  }
}

// Make globally available what index.html onclick needs
window.switchTab = switchTab;

function populateTeamPreference() {
  const select = document.getElementById('pref-team');
  if (!select || !state.appData || !state.appData.teams) return;
  
  const teams = Object.values(state.appData.teams)
    .filter(t => !t.is_placeholder)
    .sort((a, b) => a.name.localeCompare(b.name));
    
  teams.forEach(t => {
    const opt = document.createElement('option');
    opt.value = t.fifa_code;
    opt.textContent = t.name;
    select.appendChild(opt);
  });
}

function setupPreferenceListeners() {
  const teamSelect = document.getElementById('pref-team');
  const styleSelect = document.getElementById('pref-style');
  const timeSelect = document.getElementById('pref-time');
  const playersInput = document.getElementById('pref-players');

  const updatePreferences = () => {
    state.userPreferences.favoriteTeam = teamSelect.value;
    state.userPreferences.matchStyle = styleSelect.value;
    state.userPreferences.preferredTime = Array.from(timeSelect.selectedOptions).map(o => o.value);
    state.userPreferences.favoritePlayers = playersInput.value.split(',').map(s => s.trim()).filter(s => s);
    
    // Recalculate scores
    if (state.appData && state.appData.matches) {
      state.appData.matches.forEach(m => {
        m.smartScore = calculateSmartScore(m, state.appData.teams);
      });
      sortMatchesList(document.getElementById('sort-matches').value || 'interest-desc');
      renderMatches();
    }
  };

  if (teamSelect) teamSelect.addEventListener('change', updatePreferences);
  if (styleSelect) styleSelect.addEventListener('change', updatePreferences);
  if (timeSelect) timeSelect.addEventListener('change', updatePreferences);
  if (playersInput) playersInput.addEventListener('input', updatePreferences);
}
