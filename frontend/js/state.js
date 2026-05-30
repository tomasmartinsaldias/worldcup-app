// state.js
let appData = null;
let activeTab = localStorage.getItem('activeTab') || 'recommender';
let selectedCountryCode = null;
let userPreferences = {
  favoriteTeam: '',
  matchStyle: 'all', // 'all', 'closed', 'chaotic'
  favoritePlayers: [],
  preferredTime: [], // array of 'morning', 'afternoon', 'evening'
  tacticalVector: { defensa: 0.0, posesion: 0.0, ritmo: 0.0, ancho: 0.0 }
};

export async function loadData() {
  try {
    const [mainRes, logosRes, estiloRes, arquetiposRes] = await Promise.all([
      fetch(`data/wc2026_data.json?t=${new Date().getTime()}`),
      fetch(`data/club_logos.json?t=${new Date().getTime()}`),
      fetch(`data/estilos-de-juego/selecciones_estilo?t=${new Date().getTime()}`),
      fetch(`data/estilos-de-juego/arquetipos?t=${new Date().getTime()}`)
    ]);
    state.appData = await mainRes.json();
    state.appData.clubLogos = await logosRes.json();
    
    const estiloData = await estiloRes.json();
    const arquetiposData = await arquetiposRes.json();
    state.appData.estilos = estiloData.response;
    state.appData.arquetipos = arquetiposData.archetypes;
    
    // Map estilos to teams
    mapTeamEstilos(state.appData);
    
    console.log('Main data loaded:', state.appData);
  } catch (err) {
    console.error('Error loading data:', err);
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
      // Fallback
      team.tactical_vector = { defensa: 0.0, posesion: 0.0, ritmo: 0.0, ancho: 0.0 };
      team.analisis_tactico = "";
    }
  });
}

export const state = {
  get appData() { return appData; },
  set appData(val) { appData = val; },
  get activeTab() { return activeTab; },
  set activeTab(val) { 
    activeTab = val; 
    localStorage.setItem('activeTab', val);
  },
  get selectedCountryCode() { return selectedCountryCode; },
  set selectedCountryCode(val) { selectedCountryCode = val; },
  get userPreferences() { return userPreferences; },
  set userPreferences(val) { userPreferences = val; }
};
