import { state } from '../state.js';

// 5. Render Unresolved Players List Tab
export function renderUnresolved() {
  const container = document.getElementById('unresolved-list-container');
  const countBadge = document.getElementById('unresolved-count-badge');
  if (!state.appData) return;
  
  // Collect unresolved players from Wikipedia/API results
  const unresolvedList = [];
  
  // Note: we can look into all teams and their squads to see if there are players with null values, 
  // but since we also want the Wikipedia original stats and specific reason, we will fetch from teams or mock database representation.
  // Actually, we can fetch all players with resolved === false if exported, or let's scan all squads for players with NULL values!
  // But wait, the python exporter could export scraped_unresolved_players or we can just scan squads for players where market_value_eur is NULL.
  // Wait, let's look at how squads are set up. If a player is unresolved, his market_val is null.
  // Let's list those.
  
  Object.values(state.appData.teams).forEach(t => {
    if (t.is_placeholder || !t.squad) return;
    t.squad.forEach(p => {
      if (p.market_value_eur === null && p.sofascore_rating === null) {
        unresolvedList.push({
          name: p.name,
          country: t.name,
          fifa_code: t.fifa_code,
          position: p.position,
          club: p.club,
          age: p.age,
          caps: p.caps,
          goals: p.goals,
          reason: "No matched candidate was resolved on local Transfermarkt API (nationality/age/name filter mismatch)"
        });
      }
    });
  });
  
  countBadge.textContent = `${unresolvedList.length} Registros`;
  
  if (unresolvedList.length === 0) {
    container.innerHTML = `
      <div class="no-history-msg">
        No hay registros de jugadores no resueltos. Todos los convocados de Wikipedia se vincularon con éxito en la API.
      </div>`;
    return;
  }
  
  container.innerHTML = '';
  
  // Render top 50 to avoid overloading
  const limit = unresolvedList.slice(0, 50);
  
  limit.forEach(p => {
    const div = document.createElement('div');
    div.className = 'unresolved-item';
    
    div.innerHTML = `
      <div class="unresolved-item-title">
        <span>${p.name}</span>
        <span class="injured-badge" style="background: rgba(251, 191, 36, 0.1); border-color: rgba(251, 191, 36, 0.2); color: var(--accent-gold); font-size: 0.6rem;">Null Metrics</span>
      </div>
      <div class="unresolved-item-meta">
        Selección: <strong>${p.country} (${p.fifa_code})</strong> &bull; Posición: ${p.position} &bull; Club: ${p.club} &bull; Edad: ${p.age} &bull; Partidos: ${p.caps || 0} &bull; Goles: ${p.goals || 0}
      </div>
      <div class="unresolved-item-reason">
        <strong>Motivo de Integridad:</strong> ${p.reason}
      </div>
    `;
    container.appendChild(div);
  });
  
  if (unresolvedList.length > 50) {
    const moreDiv = document.createElement('div');
    moreDiv.style.textAlign = 'center';
    moreDiv.style.color = 'var(--text-muted)';
    moreDiv.style.padding = '1rem';
    moreDiv.innerHTML = `y ${unresolvedList.length - 50} jugadores no resueltos más.`;
    container.appendChild(moreDiv);
  }
}


