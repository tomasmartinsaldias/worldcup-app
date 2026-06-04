import re

with open('/Users/franmonti/Documents/Austral/worldcup-app/frontend/js/draft.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Add state
state_injection = """
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
"""

content = content.replace("// 2. Rendering UI", state_injection + "\n// 2. Rendering UI")

# Fix renderTeams
teams_func = """function renderTeams() {
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
    html += `
      <div class="draft-card" data-type="team" data-id="${originalIndex}">
        <img src="${t.crest}" alt="${t.team}" loading="lazy">
        <span class="name">${t.team}</span>
      </div>
    `;
  });
  container.innerHTML = html;
}"""

content = re.sub(r'function renderTeams\(\) \{[\s\S]*?container\.innerHTML = html;\n\}', teams_func, content)

# Fix renderCountries
countries_func = """function renderCountries() {
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
    html += `
      <div class="draft-card" data-type="country" data-id="${originalIndex}">
        <img src="${c.flag_url}" alt="${c.country}" loading="lazy">
        <span class="name">${c.country}</span>
      </div>
    `;
  });
  container.innerHTML = html;
}"""

content = re.sub(r'function renderCountries\(\) \{[\s\S]*?container\.innerHTML = html;\n\}', countries_func, content)

# Fix renderPlayers
players_func = """function renderPlayers() {
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
    const imgUrl = p._URL || '../img/placeholder_player.png';
    html += `
      <div class="draft-card" data-type="player" data-id="${originalIndex}">
        <div class="overall">${p.Overall}</div>
        <img src="${imgUrl}" alt="${p.NAME}" loading="lazy">
        <span class="name">${p.NAME}</span>
      </div>
    `;
  });
  container.innerHTML = html;
}"""

content = re.sub(r'function renderPlayers\(\) \{[\s\S]*?container\.innerHTML = html;\n\}', players_func, content)


with open('/Users/franmonti/Documents/Austral/worldcup-app/frontend/js/draft.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated draft.js")
