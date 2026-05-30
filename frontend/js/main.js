import { state } from './state.js';
import { calculateSmartScore } from './scoring.js';
import { renderMatches, filterMatches, sortMatchesList } from './ui/matches.js';
import { renderGroups } from './ui/groups.js';
import { renderCountries, filterTeams, closeSquadDetails, openCountrySquad } from './ui/squads.js';
import { renderUnresolved } from './ui/unresolved.js';
import { closeModal } from './ui/modal.js';
import { openPlayerProfile } from './ui/player_profile.js';
import { initQuiz } from './quiz.js';

window.openCountrySquad = openCountrySquad;
window.openPlayerProfile = openPlayerProfile;

document.addEventListener('DOMContentLoaded', () => {
  setupTabListeners();
  loadData();
  initQuiz();
  
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
  
  // Theme Toggle
  const themeToggleBtn = document.getElementById('btn-theme-toggle');
  if (themeToggleBtn) {
    const icon = themeToggleBtn.querySelector('i');
    if (localStorage.getItem('theme') === 'light') {
      document.body.classList.add('light-mode');
      icon.classList.replace('fa-sun', 'fa-moon');
    }
    themeToggleBtn.addEventListener('click', () => {
      document.body.classList.toggle('light-mode');
      if (document.body.classList.contains('light-mode')) {
        localStorage.setItem('theme', 'light');
        icon.classList.replace('fa-sun', 'fa-moon');
      } else {
        localStorage.setItem('theme', 'dark');
        icon.classList.replace('fa-moon', 'fa-sun');
      }
    });
  }
  
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
    panel.style.display = '';
  });
  
  const squadDetailsView = document.getElementById('squad-details-view');
  if (squadDetailsView) squadDetailsView.classList.remove('active');
  
  if (tabName === 'squads' && state.selectedCountryCode !== null) {
    if (squadDetailsView) squadDetailsView.classList.add('active');
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
    const [response, logosRes, estiloRes, arquetiposRes, photosRes] = await Promise.all([
      fetch('../data/wc2026_data.json?t=' + new Date().getTime()),
      fetch('data/club_logos.json?t=' + new Date().getTime()),
      fetch('../data/estilos-de-juego/selecciones_estilo?t=' + new Date().getTime()),
      fetch('../data/estilos-de-juego/arquetipos?t=' + new Date().getTime()),
      fetch('data/players_photos.json?t=' + new Date().getTime())
    ]);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    state.appData = await response.json();
    try {
      state.appData.clubLogos = await logosRes.json();
    } catch(e) {
      console.warn("Could not parse club logos", e);
      state.appData.clubLogos = {};
    }
    
    try {
      const estiloData = await estiloRes.json();
      state.appData.estilos = estiloData.response;
    } catch(e) {
      console.error("Could not parse estilos", e);
      state.appData.estilos = [];
    }

    try {
      const arquetiposData = await arquetiposRes.json();
      state.appData.arquetipos = arquetiposData.archetypes;
    } catch(e) {
      console.error("Could not parse arquetipos", e);
      state.appData.arquetipos = [];
    }

    try {
      const photosData = await photosRes.json();
      state.appData.playersPhotos = photosData;
      state.appData.photoIndex = {};
      const robustNormalise = str => {
        if (!str) return '';
        return str
          .normalize('NFD')
          .replace(/[\u0300-\u036f]/g, '')
          .replace(/ø/gi, 'o').replace(/ð/gi, 'd').replace(/þ/gi, 'th')
          .replace(/æ/gi, 'ae').replace(/ł/gi, 'l').replace(/ß/gi, 'ss').replace(/œ/gi, 'oe')
          .replace(/[^\x00-\x7F]/g, '')
          .toLowerCase().trim();
      };
      photosData.forEach(p => {
        const n = robustNormalise(p.n);
        const fn = robustNormalise(p.fn);
        if (fn) state.appData.photoIndex[fn] = p.p;
        if (n && !state.appData.photoIndex[n]) state.appData.photoIndex[n] = p.p;
        const parts = fn.split(' ');
        if (parts.length > 1) {
            const short = parts[0][0] + '. ' + parts[parts.length-1];
            if (!state.appData.photoIndex[short]) state.appData.photoIndex[short] = p.p;
            const firstLast = parts[0] + ' ' + parts[parts.length-1];
            if (!state.appData.photoIndex[firstLast]) state.appData.photoIndex[firstLast] = p.p;
        }
      });
    } catch(e) {
      console.error("Could not parse players photos", e);
      state.appData.photoIndex = {};
      state.appData.playersPhotos = [];
    }

    // Map estilos to teams
    mapTeamEstilos(state.appData);
    
    populateTeamPreference();
    
    state.appData.matches.forEach(m => {
      m.smartScore = calculateSmartScore(m, state.appData.teams, state.userPreferences?.tacticalVector);
    });
    
    sortMatchesList(document.getElementById('sort-matches').value || 'interest-desc');
    
    renderMatches();
    renderGroups();
    renderCountries();
    renderUnresolved();
    
    // Initialize Tactical UI
    initTacticalUI();
    
  } catch (error) {
    console.error("No se pudieron cargar los datos del Mundial:", error);
    container.innerHTML = `
      <div class="error-state-card">
        <i class="fa-solid fa-server-slash error-icon"></i>
        <h3>Error de Conexión</h3>
        <p>No se pudo cargar el archivo local de datos o estilos de juego.</p>
        <button onclick="location.reload()" class="retry-btn">Reintentar</button>
      </div>`;
  }
}

function mapTeamEstilos(appData) {
  if (!appData || !appData.teams || !appData.estilos) return;
  const normalise = str => str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
  
  const estiloMap = {};
  appData.estilos.forEach(item => {
    estiloMap[normalise(item.equipo)] = item;
  });
  
  Object.values(appData.teams).forEach(team => {
    const key = normalise(team.name);
    if (estiloMap[key]) {
      team.tactical_vector = estiloMap[key].vector;
      team.analisis_tactico = estiloMap[key].analisis_tactico;
    } else {
      team.tactical_vector = { defensa: 0.0, posesion: 0.0, ritmo: 0.0, ancho: 0.0 };
      team.analisis_tactico = "";
    }
  });
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
    recalculateAndRender();
  };

  if (teamSelect) teamSelect.addEventListener('change', updatePreferences);
  if (styleSelect) styleSelect.addEventListener('change', updatePreferences);
  if (timeSelect) timeSelect.addEventListener('change', updatePreferences);
  if (playersInput) playersInput.addEventListener('input', updatePreferences);
}

let currentArchetypeIndex = 0;

function initTacticalUI() {
  const btnOpenTactical = document.getElementById('btn-open-tactical');
  const btnBackToRecommender = document.getElementById('back-to-recommender-btn');
  
  if (btnOpenTactical) {
    btnOpenTactical.addEventListener('click', () => {
      switchTab('tactical');
      renderArchetypeSlide();
    });
  }
  
  if (btnBackToRecommender) {
    btnBackToRecommender.addEventListener('click', () => {
      switchTab('recommender');
    });
  }

  // Toggle internal views: Arquetipos vs Ser el DT
  const btnTacticalCasual = document.getElementById('btn-tactical-casual');
  const btnTacticalAnalyst = document.getElementById('btn-tactical-analyst');
  const viewTacticalCasual = document.getElementById('view-tactical-casual');
  const viewTacticalAnalyst = document.getElementById('view-tactical-analyst');

  if (btnTacticalCasual && btnTacticalAnalyst) {
    btnTacticalCasual.addEventListener('click', () => {
      btnTacticalCasual.classList.add('active');
      btnTacticalCasual.style.background = 'var(--wc-red)';
      btnTacticalCasual.style.color = '#ffffff';
      btnTacticalAnalyst.classList.remove('active');
      btnTacticalAnalyst.style.background = 'transparent';
      btnTacticalAnalyst.style.color = 'var(--text-secondary)';
      
      viewTacticalCasual.style.display = 'block';
      viewTacticalAnalyst.style.display = 'none';
    });

    btnTacticalAnalyst.addEventListener('click', () => {
      btnTacticalAnalyst.classList.add('active');
      btnTacticalAnalyst.style.background = 'var(--wc-red)';
      btnTacticalAnalyst.style.color = '#ffffff';
      btnTacticalCasual.classList.remove('active');
      btnTacticalCasual.style.background = 'transparent';
      btnTacticalCasual.style.color = 'var(--text-secondary)';
      
      viewTacticalAnalyst.style.display = 'block';
      viewTacticalCasual.style.display = 'none';
      syncSliders(state.userPreferences.tacticalVector);
    });
  }

  // Connect Carousel Arrows
  const prevArrows = document.querySelectorAll('#carousel-prev-btn');
  const nextArrows = document.querySelectorAll('#carousel-next-btn');

  prevArrows.forEach(arrow => {
    arrow.addEventListener('click', () => {
      const arquetipos = state.appData?.arquetipos;
      if (!arquetipos || arquetipos.length === 0) return;
      currentArchetypeIndex = (currentArchetypeIndex - 1 + arquetipos.length) % arquetipos.length;
      renderArchetypeSlide();
    });
  });

  nextArrows.forEach(arrow => {
    arrow.addEventListener('click', () => {
      const arquetipos = state.appData?.arquetipos;
      if (!arquetipos || arquetipos.length === 0) return;
      currentArchetypeIndex = (currentArchetypeIndex + 1) % arquetipos.length;
      renderArchetypeSlide();
    });
  });

  // Select archetype button in Carousel
  const btnSelectArchetype = document.getElementById('btn-select-archetype');
  if (btnSelectArchetype) {
    btnSelectArchetype.addEventListener('click', () => {
      const arquetipos = state.appData?.arquetipos;
      if (!arquetipos || arquetipos.length === 0) return;
      const arch = arquetipos[currentArchetypeIndex];
      
      state.userPreferences.tacticalVector = { ...arch.vector };
      recalculateAndRender();
      switchTab('recommender');
    });
  }

  // Custom DT Apply Button
  const btnApplyCustom = document.getElementById('btn-apply-custom-tactical');
  if (btnApplyCustom) {
    btnApplyCustom.addEventListener('click', () => {
      recalculateAndRender();
      switchTab('recommender');
    });
  }

  // Connect Sliders (DT Tab)
  const sliders = ['defensa', 'posesion', 'ritmo', 'ancho'];
  sliders.forEach(key => {
    const slider = document.getElementById(`slider-${key}-tab`);
    const valText = document.getElementById(`val-${key}-tab`);
    
    if (slider) {
      slider.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        state.userPreferences.tacticalVector[key] = val;
        
        let desc = '';
        if (key === 'defensa') {
          if (val > 0.4) desc = 'Presión Alta';
          else if (val < -0.4) desc = 'Bloque Bajo';
          else desc = 'Bloque Medio';
        } else if (key === 'posesion') {
          if (val > 0.4) desc = 'Posesión Tiki-Taka';
          else if (val < -0.4) desc = 'Contragolpe Directo';
          else desc = 'Equilibrada';
        } else if (key === 'ritmo') {
          if (val > 0.4) desc = 'Frenético Vertical';
          else if (val < -0.4) desc = 'Control Pausado';
          else desc = 'Normal';
        } else if (key === 'ancho') {
          if (val > 0.4) desc = 'Exclusivo Bandas';
          else if (val < -0.4) desc = 'Pasillo Central';
          else desc = 'Equilibrado';
        }
        valText.textContent = `${desc} (${val > 0 ? '+' : ''}${val.toFixed(1)})`;
      });
    }
  });
}

function renderArchetypeSlide() {
  const arquetipos = state.appData?.arquetipos;
  if (!arquetipos || arquetipos.length === 0) return;
  
  const arch = arquetipos[currentArchetypeIndex];
  
  document.getElementById('carousel-title').textContent = arch.title || arch.name;
  document.getElementById('carousel-subtitle').textContent = arch.subtitle || '';
  document.getElementById('carousel-desc').textContent = arch.description;
  
  const svgMap = {
    tiki_taka: `
      <svg viewBox="0 0 100 60" style="width: 100%; height: 100%;">
        <rect width="100" height="60" fill="#1e3a27" />
        <line x1="50" y1="0" x2="50" y2="60" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
        <circle cx="50" cy="30" r="12" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
        <path d="M 30,30 L 45,15 L 60,30 L 45,45 Z" fill="none" stroke="#fbbf24" stroke-dasharray="2,2" stroke-width="1.5"/>
        <circle cx="30" cy="30" r="3" fill="#ef4444"/>
        <circle cx="45" cy="15" r="3" fill="#ef4444"/>
        <circle cx="60" cy="30" r="3" fill="#ef4444"/>
        <circle cx="45" cy="45" r="3" fill="#ef4444"/>
        <circle cx="43" cy="27" r="2.2" fill="#ffffff"/>
      </svg>
    `,
    catenaccio: `
      <svg viewBox="0 0 100 60" style="width: 100%; height: 100%;">
        <rect width="100" height="60" fill="#1e3a27" />
        <line x1="50" y1="0" x2="50" y2="60" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
        <circle cx="50" cy="30" r="12" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
        <circle cx="15" cy="15" r="3" fill="#ef4444"/>
        <circle cx="12" cy="25" r="3" fill="#ef4444"/>
        <circle cx="12" cy="35" r="3" fill="#ef4444"/>
        <circle cx="15" cy="45" r="3" fill="#ef4444"/>
        <circle cx="8" cy="30" r="3.5" fill="#3b82f6"/>
        <path d="M 20,30 L 80,30" fill="none" stroke="#22c55e" stroke-width="2" marker-end="url(#arrow-cat)"/>
        <defs>
          <marker id="arrow-cat" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#22c55e"/>
          </marker>
        </defs>
      </svg>
    `,
    gegenpressing: `
      <svg viewBox="0 0 100 60" style="width: 100%; height: 100%;">
        <rect width="100" height="60" fill="#1e3a27" />
        <line x1="50" y1="0" x2="50" y2="60" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
        <circle cx="50" cy="30" r="12" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
        <circle cx="70" cy="20" r="3" fill="#ef4444"/>
        <circle cx="72" cy="30" r="3" fill="#ef4444"/>
        <circle cx="70" cy="40" r="3" fill="#ef4444"/>
        <circle cx="78" cy="30" r="3" fill="#3b82f6"/>
        <path d="M 67,22 L 75,28" fill="none" stroke="#fbbf24" stroke-width="1.5"/>
        <path d="M 69,30 L 75,30" fill="none" stroke="#fbbf24" stroke-width="1.5"/>
        <path d="M 67,38 L 75,32" fill="none" stroke="#fbbf24" stroke-width="1.5"/>
      </svg>
    `,
    asociativo: `
      <svg viewBox="0 0 100 60" style="width: 100%; height: 100%;">
        <rect width="100" height="60" fill="#1e3a27" />
        <line x1="50" y1="0" x2="50" y2="60" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
        <circle cx="50" cy="30" r="12" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
        <circle cx="45" cy="25" r="3" fill="#ef4444"/>
        <circle cx="50" cy="35" r="3" fill="#ef4444"/>
        <circle cx="55" cy="22" r="3" fill="#ef4444"/>
        <path d="M 45,25 C 48,30 47,32 50,35 C 52,32 53,26 55,22 Z" fill="none" stroke="#fbbf24" stroke-width="1"/>
      </svg>
    `,
    directo: `
      <svg viewBox="0 0 100 60" style="width: 100%; height: 100%;">
        <rect width="100" height="60" fill="#1e3a27" />
        <line x1="50" y1="0" x2="50" y2="60" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
        <circle cx="50" cy="30" r="12" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
        <path d="M 20,30 Q 50,55 85,45" fill="none" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="3,3"/>
        <path d="M 20,30 Q 50,5 85,15" fill="none" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="3,3"/>
        <circle cx="20" cy="30" r="3" fill="#ef4444"/>
        <circle cx="85" cy="45" r="3" fill="#ef4444"/>
        <circle cx="85" cy="15" r="3" fill="#ef4444"/>
        <path d="M 85,15 L 80,30" fill="none" stroke="#ef4444" stroke-width="1.5"/>
      </svg>
    `
  };

  const dynamicGraphicContainer = document.getElementById('archetype-graphic-container');
  if (dynamicGraphicContainer) {
    dynamicGraphicContainer.innerHTML = svgMap[arch.id] || `
      <div style="font-size: 3.5rem; text-shadow: 0 0 10px rgba(251,191,36,0.3);">⚽</div>
    `;
  }
  
  const metricsContainer = document.getElementById('carousel-vector-metrics');
  if (metricsContainer) {
    metricsContainer.innerHTML = '';
    
    const dimensions = [
      { key: 'defensa', label: 'Defensa', low: 'Bloque Bajo', high: 'Presión Alta' },
      { key: 'posesion', label: 'Posesión', low: 'Contra Rápida', high: 'Tiki-Taka' },
      { key: 'ritmo', label: 'Ritmo de Juego', low: 'Pausado', high: 'Frenético' },
      { key: 'ancho', label: 'Amplitud', low: 'Pasillo Central', high: 'Exclusivo Bandas' }
    ];
    
    dimensions.forEach(dim => {
      const val = arch.vector[dim.key];
      const pct = ((val + 1.0) / 2.0) * 100;
      
      const metricItem = document.createElement('div');
      metricItem.style.cssText = 'display: flex; flex-direction: column; gap: 0.25rem; text-align: left; background: rgba(255,255,255,0.01); padding: 0.5rem 0.8rem; border-radius: 12px; border: 1px solid var(--border-glass);';
      metricItem.innerHTML = `
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: bold; color: var(--text-primary); font-family: var(--font-primary);">
          <span>${dim.label}</span>
          <span style="color: var(--accent-gold);">${val > 0 ? '+' : ''}${val.toFixed(1)}</span>
        </div>
        <div style="background: rgba(255,255,255,0.04); height: 6px; border-radius: 4px; overflow: hidden; margin: 0.2rem 0;">
          <div style="background: linear-gradient(90deg, var(--accent-gold) 0%, #fb923c 100%); height: 100%; width: ${pct}%; border-radius: 4px; box-shadow: 0 0 10px rgba(251,191,36,0.45);"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.65rem; color: var(--text-muted); font-family: var(--font-secondary);">
          <span>${dim.low}</span>
          <span>${dim.high}</span>
        </div>
      `;
      metricsContainer.appendChild(metricItem);
    });
  }
}

function syncSliders(vector) {
  const sliders = ['defensa', 'posesion', 'ritmo', 'ancho'];
  sliders.forEach(key => {
    const slider = document.getElementById(`slider-${key}-tab`);
    const valText = document.getElementById(`val-${key}-tab`);
    if (slider && valText) {
      const val = vector[key];
      slider.value = val;
      
      let desc = '';
      if (key === 'defensa') {
        if (val > 0.4) desc = 'Presión Alta';
        else if (val < -0.4) desc = 'Bloque Bajo';
        else desc = 'Bloque Medio';
      } else if (key === 'posesion') {
        if (val > 0.4) desc = 'Posesión Tiki-Taka';
        else if (val < -0.4) desc = 'Contragolpe Directo';
        else desc = 'Equilibrada';
      } else if (key === 'ritmo') {
        if (val > 0.4) desc = 'Frenético Vertical';
        else if (val < -0.4) desc = 'Control Pausado';
        else desc = 'Normal';
      } else if (key === 'ancho') {
        if (val > 0.4) desc = 'Exclusivo Bandas';
        else if (val < -0.4) desc = 'Pasillo Central';
        else desc = 'Equilibrado';
      }
      valText.textContent = `${desc} (${val > 0 ? '+' : ''}${val.toFixed(1)})`;
    }
  });
}

function recalculateAndRender() {
  if (state.appData && state.appData.matches) {
    state.appData.matches.forEach(m => {
      m.smartScore = calculateSmartScore(m, state.appData.teams, state.userPreferences?.tacticalVector);
    });
    sortMatchesList(document.getElementById('sort-matches').value || 'interest-desc');
    renderMatches();
  }
}
