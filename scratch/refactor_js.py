import os
import re
import shutil

base_dir = r"c:\Users\user\Downloads\app_mundial\worldcup-app\frontend"
js_dir = os.path.join(base_dir, "js")
ui_dir = os.path.join(js_dir, "ui")

os.makedirs(ui_dir, exist_ok=True)

with open(os.path.join(base_dir, "app.js"), "r", encoding="utf-8") as f:
    app_js = f.read()

# Utils
utils_js = """// utils.js
export function getCountryIsoCode(fifaCode) {
  const mapping = {
    'ARG': 'ar', 'BRA': 'br', 'FRA': 'fr', 'ENG': 'gb-eng', 'ESP': 'es', 'GER': 'de', 'POR': 'pt',
    'URU': 'uy', 'NED': 'nl', 'CRO': 'hr', 'JPN': 'jp', 'USA': 'us', 'MEX': 'mx', 'MAR': 'ma',
    'COL': 'co', 'BEL': 'be', 'NOR': 'no', 'SEN': 'sn', 'EGY': 'eg', 'SWE': 'se', 'KOR': 'kr',
    'TUR': 'tr', 'SUI': 'ch', 'CAN': 'ca', 'ECU': 'ec', 'AUT': 'at', 'ALG': 'dz', 'CIV': 'ci',
    'SCO': 'gb-sct', 'AUS': 'au', 'GHA': 'gh', 'KSA': 'sa', 'PAR': 'py', 'CZE': 'cz', 'COD': 'cd',
    'BIH': 'ba', 'CPV': 'cv', 'TUN': 'tn', 'IRQ': 'iq', 'RSA': 'za', 'UZB': 'uz', 'QAT': 'qa',
    'NZL': 'nz', 'JOR': 'jo', 'PAN': 'pa', 'HAI': 'ht', 'CUR': 'cw', 'POL': 'pl', 'SRB': 'rs',
    'CMR': 'cm', 'CRC': 'cr', 'DEN': 'dk', 'WAL': 'gb-wls'
  };
  return mapping[fifaCode] || 'un';
}

export function getFlagUrl(fifaCode) {
  if (!fifaCode) return '';
  return `https://images.tomas.me/flags/${fifaCode.toLowerCase()}.png`; 
}

export function createFlagElement(team) {
  if (team.is_placeholder) {
    return `<div class="team-flag-placeholder"><i class="fa-solid fa-hourglass-half"></i></div>`;
  }
  const code = team.fifa_code;
  const flagUrl = `https://flagcdn.com/w40/${getCountryIsoCode(code)}.png`;
  return `<img src="${flagUrl}" class="team-flag-real" onerror="this.outerHTML='<div class=team-flag-placeholder>${code}</div>'">`;
}

export function formatKickoff(isoStr) {
  if (!isoStr) return 'TBD';
  try {
    const d = new Date(isoStr);
    return d.toLocaleString('es-ES', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) + ' hs';
  } catch(e) {
    return isoStr;
  }
}
"""
with open(os.path.join(js_dir, "utils.js"), "w", encoding="utf-8") as f:
    f.write(utils_js)

# Recommender
recommender_js = """// recommender.js
export function calculateSmartScore(match, teams) {
  if (match.home_team.is_placeholder || match.away_team.is_placeholder) {
    return 5.0; // default for playoff TBD matches
  }
  
  const home = teams[match.home_team.fifa_code];
  const away = teams[match.away_team.fifa_code];
  
  if (!home || !away || !home.metrics || !away.metrics) {
    return 6.0;
  }
  
  // 1. Squad Value (0 to 2.5 points)
  const combVal = (home.metrics.market_value_eur || 0) + (away.metrics.market_value_eur || 0);
  const valScore = Math.min((combVal / 850.0) * 2.5, 2.5);
  
  // 2. Global Popularity (0 to 2.0 points)
  const avgPop = ((home.metrics.global_popularity_score || 50) + (away.metrics.global_popularity_score || 50)) / 2;
  const popScore = (avgPop / 100.0) * 2.0;
  
  // 3. Offensive Style (xG) (0 to 1.5 points)
  const avgXg = ((home.metrics.recent_xg_avg || 1.1) + (away.metrics.recent_xg_avg || 1.1)) / 2;
  const xgScore = Math.min((avgXg / 2.0) * 1.5, 1.5);
  
  // 4. Recent Performance / Current Form (0 to 1.5 points)
  const avgEff = ((home.metrics.efficiency_score_avg || 0.19) + (away.metrics.efficiency_score_avg || 0.19)) / 2;
  const effScore = Math.min((avgEff / 0.50) * 1.5, 1.5);
  
  // 5. Historical Card/Friction Intensity (0 to 1.0 points)
  const combCards = ((home.metrics.cards_per_match_avg || 1.3) + (away.metrics.cards_per_match_avg || 1.3)) / 2;
  const cardsScore = Math.min((combCards / 2.4) * 1.0, 1.0);
  
  // 6. Star Player count (0 to 1.0 points)
  const homeStars = home.squad ? home.squad.filter(p => p.is_star_player).length : 0;
  const awayStars = away.squad ? away.squad.filter(p => p.is_star_player).length : 0;
  const starScore = Math.min(((homeStars + awayStars) / 8.0) * 1.0, 1.0);
  
  // Stage Bonus (0.5 for knockout)
  const stageBonus = (match.stage && match.stage !== 'Group Stage') ? 0.5 : 0;
  
  let finalScore = valScore + popScore + xgScore + effScore + cardsScore + starScore + stageBonus;
  finalScore = Math.min(Math.max(finalScore, 1.0), 10.0);
  return parseFloat(finalScore.toFixed(1));
}
"""
with open(os.path.join(js_dir, "recommender.js"), "w", encoding="utf-8") as f:
    f.write(recommender_js)

# State
state_js = """// state.js
let appData = null;
let activeTab = localStorage.getItem('activeTab') || 'recommender';
let selectedCountryCode = null;

export const state = {
  get appData() { return appData; },
  set appData(val) { appData = val; },
  get activeTab() { return activeTab; },
  set activeTab(val) { 
    activeTab = val; 
    localStorage.setItem('activeTab', val);
  },
  get selectedCountryCode() { return selectedCountryCode; },
  set selectedCountryCode(val) { selectedCountryCode = val; }
};
"""
with open(os.path.join(js_dir, "state.js"), "w", encoding="utf-8") as f:
    f.write(state_js)

# Match module (re-implementing the original logic for simplicity, getting exact blocks from app.js)
import re

def extract_block(js, start_marker, end_marker):
    start_idx = js.find(start_marker)
    end_idx = js.find(end_marker, start_idx) if end_marker else len(js)
    if start_idx == -1: return ""
    return js[start_idx:end_idx]

matches_block = extract_block(app_js, "// Sorting logic", "// 2. Render Groups Tab")
groups_block = extract_block(app_js, "// 2. Render Groups Tab", "// 3. Render Countries / Squads Selection Tab")
squads_block = extract_block(app_js, "// 3. Render Countries / Squads Selection Tab", "// 5. Render Unresolved Players List Tab")
unresolved_block = extract_block(app_js, "// 5. Render Unresolved Players List Tab", "// 6. H2H Modal Management")
modal_block = extract_block(app_js, "// 6. H2H Modal Management", "function closeModal()")
if modal_block:
    # also add closeModal function
    close_idx = app_js.find("function closeModal()")
    close_end = app_js.find("}", close_idx) + 1
    modal_block += app_js[close_idx:close_end]

# Transform matches to use imports
matches_code = f"""import {{ state }} from '../state.js';
import {{ createFlagElement, formatKickoff }} from '../utils.js';
import {{ openH2HModal }} from './modal.js';

{matches_block.replace("appData", "state.appData").replace("function renderMatches", "export function renderMatches").replace("function filterMatches", "export function filterMatches").replace("function sortMatchesList", "export function sortMatchesList").replace("function getCombinedValue", "export function getCombinedValue").replace("function getCombinedCards", "export function getCombinedCards")}
"""
with open(os.path.join(ui_dir, "matches.js"), "w", encoding="utf-8") as f:
    f.write(matches_code)

# Transform groups
groups_code = f"""import {{ state }} from '../state.js';
import {{ createFlagElement }} from '../utils.js';
import {{ openCountrySquad }} from './squads.js';

{groups_block.replace("appData", "state.appData").replace("function renderGroups", "export function renderGroups")}
"""
with open(os.path.join(ui_dir, "groups.js"), "w", encoding="utf-8") as f:
    f.write(groups_code)

# Transform squads
squads_code = f"""import {{ state }} from '../state.js';
import {{ createFlagElement }} from '../utils.js';

{squads_block.replace("appData", "state.appData").replace("function renderCountries", "export function renderCountries").replace("function filterTeams", "export function filterTeams").replace("function openCountrySquad", "export function openCountrySquad").replace("function closeSquadDetails", "export function closeSquadDetails")}
"""
with open(os.path.join(ui_dir, "squads.js"), "w", encoding="utf-8") as f:
    f.write(squads_code)

# Transform unresolved
unresolved_code = f"""import {{ state }} from '../state.js';

{unresolved_block.replace("appData", "state.appData").replace("function renderUnresolved", "export function renderUnresolved")}
"""
with open(os.path.join(ui_dir, "unresolved.js"), "w", encoding="utf-8") as f:
    f.write(unresolved_code)

# Transform modal
modal_code = f"""import {{ state }} from '../state.js';
import {{ createFlagElement }} from '../utils.js';
import {{ getCombinedValue }} from './matches.js';

{modal_block.replace("appData", "state.appData").replace("function openH2HModal", "export function openH2HModal").replace("function closeModal", "export function closeModal")}
"""
with open(os.path.join(ui_dir, "modal.js"), "w", encoding="utf-8") as f:
    f.write(modal_code)

# Main
main_code = """import { state } from './state.js';
import { calculateSmartScore } from './recommender.js';
import { renderMatches, filterMatches, sortMatchesList } from './ui/matches.js';
import { renderGroups } from './ui/groups.js';
import { renderCountries, filterTeams, closeSquadDetails } from './ui/squads.js';
import { renderUnresolved } from './ui/unresolved.js';
import { closeModal } from './ui/modal.js';

document.addEventListener('DOMContentLoaded', () => {
  setupTabListeners();
  loadData();
  
  // Restore filters from localStorage if exist
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
    const response = await fetch('../data/wc2026_data.json');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    state.appData = await response.json();
    
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
"""
with open(os.path.join(js_dir, "main.js"), "w", encoding="utf-8") as f:
    f.write(main_code)

print("JS Refactor Completed")
