// Lógica del sistema Draft

window.draftState = {
  team: null,
  countries: [],
  players: []
};

let draftData = {
  teams: [],
  countries: [],
  players: []
};
window.draftData = draftData;

let isDraftLoaded = false;

// 1. Fetching Data
window.initDraftData = async function initDraftData() {
  if (isDraftLoaded) return;
  try {
    const [teamsRes, countriesRes, playersRes] = await Promise.all([
      fetch('data/data_frontend/teams.json'),
      fetch('data/data_frontend/countries.json'),
      fetch('data/data_frontend/players_final.json')
    ]);

    const checkRes = async (res) => {
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      const text = await res.text();
      try { return JSON.parse(text); } 
      catch (e) { throw new Error(`Invalid JSON: ${text.substring(0, 50)}...`); }
    };

    const teams = await checkRes(teamsRes);
    const countries = await checkRes(countriesRes);
    const players = await checkRes(playersRes);

    // Sort data
    draftData.teams = teams.sort((a, b) => a.team.localeCompare(b.team));
    draftData.countries = countries.sort((a, b) => a.country.localeCompare(b.country));
    draftData.players = players
      .filter(p => p.NAME && p.Overall) // Filter valid players
      .sort((a, b) => b.Overall - a.Overall);

    window.draftData = draftData;
    isDraftLoaded = true;
    renderDraftUI();
  } catch (error) {
    console.error("Error loading draft data. Ensure server is running at project root:", error);
  }
}


window.currentSearch = { teams: '', countries: '', players: '' };
window.currentPage = { teams: 1, countries: 1, players: 1 };
const itemsPerPage = 20;

window.filterDraft = function(type) {
  const query = document.getElementById(`search-${type}`).value.toLowerCase();
  window.currentSearch[type] = query;
  window.currentPage[type] = 1;
  if(type === 'teams') renderTeams();
  if(type === 'countries') renderCountries();
  if(type === 'players') renderPlayers();
};

window.changePage = function(type, delta) {
  window.currentPage[type] += delta;
  if(type === 'teams') renderTeams();
  if(type === 'countries') renderCountries();
  if(type === 'players') renderPlayers();
};

function updatePaginationUI(type, totalFiltered) {
  const totalPages = Math.ceil(totalFiltered / itemsPerPage) || 1;
  const container = document.getElementById(`pagination-${type}`);
  if(!container) return;
  const current = window.currentPage[type];
  
  container.innerHTML = `
    <button class="btn-pagination" onclick="changePage('${type}', -1)" ${current <= 1 ? 'disabled' : ''}>&lt;</button>
    <span class="pagination-info">${current} / ${totalPages}</span>
    <button class="btn-pagination" onclick="changePage('${type}', 1)" ${current >= totalPages ? 'disabled' : ''}>&gt;</button>
  `;
}

// 2. Rendering UI
function renderDraftUI() {
  renderTeams();
  renderCountries();
  renderPlayers();
}

function renderTeams() {
  const container = document.getElementById('draft-teams-grid');
  
  const query = window.currentSearch.teams;
  let filtered = draftData.teams;
  if(query) {
    filtered = filtered.filter(t => t.team.toLowerCase().includes(query));
  }
  
  updatePaginationUI('teams', filtered.length);
  const start = (window.currentPage.teams - 1) * itemsPerPage;
  const paginated = filtered.slice(start, start + itemsPerPage);

  let html = '';
  paginated.forEach((t) => {
    const originalIndex = draftData.teams.indexOf(t);
    const isSelected = draftState.team === originalIndex ? 'selected' : '';
    html += `
      <div class="draft-card ${isSelected}" data-type="team" data-id="${originalIndex}">

        <img src="${t.crest}" alt="${t.team}" loading="lazy" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='./img/placeholder_player.svg';">
        <span class="name">${t.team}</span>
      </div>
    `;
  });
  container.innerHTML = html;
}

function renderCountries() {
  const container = document.getElementById('draft-countries-grid');
  
  const query = window.currentSearch.countries;
  let filtered = draftData.countries;
  if(query) {
    filtered = filtered.filter(c => c.country.toLowerCase().includes(query));
  }
  
  updatePaginationUI('countries', filtered.length);
  const start = (window.currentPage.countries - 1) * itemsPerPage;
  const paginated = filtered.slice(start, start + itemsPerPage);

  let html = '';
  paginated.forEach((c) => {
    const originalIndex = draftData.countries.indexOf(c);
    const isSelected = draftState.countries.includes(originalIndex) ? 'selected' : '';
    html += `
      <div class="draft-card ${isSelected}" data-type="country" data-id="${originalIndex}">

        <img src="${c.flag_url}" alt="${c.country}" loading="lazy" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='./img/placeholder_player.svg';">
        <span class="name">${c.country}</span>
      </div>
    `;
  });
  container.innerHTML = html;
}

function renderPlayers() {
  const container = document.getElementById('draft-players-grid');
  
  const query = window.currentSearch.players;
  let filtered = draftData.players;
  if(query) {
    filtered = filtered.filter(p => p.NAME.toLowerCase().includes(query));
  }
  
  updatePaginationUI('players', filtered.length);
  const start = (window.currentPage.players - 1) * itemsPerPage;
  const paginated = filtered.slice(start, start + itemsPerPage);

  let html = '';
  paginated.forEach((p) => {
    const originalIndex = draftData.players.indexOf(p);
    const isSelected = draftState.players.includes(originalIndex) ? 'selected' : '';
    const imgUrl = p._URL || './img/placeholder_player.svg';
    html += `
      <div class="draft-card ${isSelected}" data-type="player" data-id="${originalIndex}">

        <div class="overall">${p.Overall}</div>
        <img src="${imgUrl}" alt="${p.NAME}" loading="lazy" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='./img/placeholder_player.svg';">
        <span class="name">${p.NAME}</span>
      </div>
    `;
  });
  container.innerHTML = html;
}

// 3. Event Delegation for Selection
document.addEventListener('DOMContentLoaded', () => {
  const grids = ['draft-teams-grid', 'draft-countries-grid', 'draft-players-grid'];
  
  grids.forEach(gridId => {
    const grid = document.getElementById(gridId);
    if (!grid) return;
    
    grid.addEventListener('click', (e) => {
      const card = e.target.closest('.draft-card');
      if (!card) return;
      
      const type = card.dataset.type;
      const id = parseInt(card.dataset.id);
      
      handleSelection(type, id, card);
    });
  });
});

function handleSelection(type, id, cardElement) {
  if (type === 'team') {
    // Max 1
    if (draftState.team === id) {
      // Deselect
      draftState.team = null;
      cardElement.classList.remove('selected');
    } else {
      // Select new, deselect old
      if (draftState.team !== null) {
        const oldCard = document.querySelector(`#draft-teams-grid .draft-card[data-id="${draftState.team}"]`);
        if (oldCard) oldCard.classList.remove('selected');
      }
      draftState.team = id;
      cardElement.classList.add('selected');
    }
  } 
  else if (type === 'country') {
    // Max 4
    const index = draftState.countries.indexOf(id);
    if (index > -1) {
      // Deselect
      draftState.countries.splice(index, 1);
      cardElement.classList.remove('selected');
    } else {
      // Try to select
      if (draftState.countries.length >= 4) {
        triggerShake(cardElement);
      } else {
        draftState.countries.push(id);
        cardElement.classList.add('selected');
      }
    }
  }
  else if (type === 'player') {
    // Max 6
    const index = draftState.players.indexOf(id);
    if (index > -1) {
      // Deselect
      draftState.players.splice(index, 1);
      cardElement.classList.remove('selected');
    } else {
      // Try to select
      if (draftState.players.length >= 6) {
        triggerShake(cardElement);
      } else {
        draftState.players.push(id);
        cardElement.classList.add('selected');
      }
    }
  }
}

function triggerShake(element) {
  element.classList.remove('shake');
  // Trigger reflow to restart animation
  void element.offsetWidth;
  element.classList.add('shake');
}

// 4. Navigation Logic
window.nextDraftStep = function(stepIndex) {
  changeDraftStep(stepIndex);
}

window.prevDraftStep = function(stepIndex) {
  changeDraftStep(stepIndex);
}

function changeDraftStep(stepIndex) {
  // Hide all
  document.querySelectorAll('.draft-step').forEach(step => {
    step.classList.remove('active');
  });
  
  // Show target
  const targetStep = document.getElementById(`draft-step-${stepIndex}`);
  if (targetStep) {
    targetStep.classList.add('active');
  }
  
  // Update progress bar
  const progressPercent = (stepIndex / 3) * 100;
  document.getElementById('draft-progress').style.width = `${progressPercent}%`;
  document.getElementById('draft-step-text').innerText = `PASO ${stepIndex} DE 3`;
}

window.finishDraft = function() {
  console.log("Draft Finalizado:", draftState);
  
  // Just show an alert for now or proceed to something else
  // To avoid reflows and stuttering, we just log and close
  if(window.returnToHomepage) {
    window.returnToHomepage();
  } else {
    document.getElementById('draft-overlay').classList.remove('visible');
  }
  
  alert("Draft finalizado con éxito! Revisa la consola para ver tu selección.");
}

// Function to open draft (can be attached to a button in the future)
window.openDraftOverlay = function() {
  initDraftData();
  if(window.appState !== undefined) {
    window.appState = 'draft';
  }
  
  // Hide other possible overlays
  const rec = document.getElementById('recommendations-overlay');
  if(rec) rec.classList.add('hidden');
  
  const casual = document.getElementById('casual-quiz');
  if(casual) casual.classList.remove('visible');
  
  const fanatic = document.getElementById('fanatic-quiz');
  if(fanatic) fanatic.classList.remove('visible');
  
  document.querySelector('.hero-ui').classList.add('fade-out');
  
  const overlay = document.getElementById('draft-overlay');
  overlay.classList.remove('hidden');
  overlay.classList.add('visible');
  changeDraftStep(1); // Reset to step 1
}

// End of futdraft.js
