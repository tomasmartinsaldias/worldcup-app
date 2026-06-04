// state.js
let appData = null;
let activeTab = localStorage.getItem('activeTab') || 'recommender';
let selectedCountryCode = null;
let userPreferences = {
  favoriteTeam: '',
  matchStyle: 'all', // 'all', 'closed', 'chaotic'
  favoritePlayers: [],
  preferredTime: [], // array of 'morning', 'afternoon', 'evening'
  tacticalVector: { defensa: 0.0, posesion: 0.0, ritmo: 0.0, ancho: 0.0 },
  spectacleWeight: 0.5,
  // dramaBonus: -1 (no gusta fricción) | 0 (indiferente) | +1 (gusta fricción)
  // Controla si el FriccionScore suma o resta al SmartScore final
  dramaBonus: 0
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
    
    // Fetch players_final.json for fallback faces
    let finalPhotosData = [];
    try {
      const finalRes = await fetch(`../data/data_frontend/players_final.json?t=${new Date().getTime()}`);
      if (finalRes.ok) finalPhotosData = await finalRes.json();
    } catch (e) {
      console.error("Could not fetch players_final.json", e);
    }
    
    state.appData.photoIndex = {};
    const robustNormalise = str => {
      if (!str) return '';
      return str
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .replace(/\u00f8/gi, 'o').replace(/\u00f0/gi, 'd').replace(/\u00fe/gi, 'th')
        .replace(/\u00e6/gi, 'ae').replace(/\u0142/gi, 'l').replace(/\u00df/gi, 'ss').replace(/\u0153/gi, 'oe')
        .replace(/[^\x00-\x7F]/g, '')
        .toLowerCase().trim();
    };
    
    state.appData.clusters = {
      Goalkeepers: [], Centerbacks: [], Fullbacks: [], Midfielders: [], Wingers: [], Strikers: []
    };
    const posMap = {
      'Goalkeeper': 'Goalkeepers', 'Midfielder': 'Midfielders', 'Striker': 'Strikers',
      'Centerbacks': 'Centerbacks', 'Fullbacks': 'Fullbacks', 'Wingers': 'Wingers'
    };

    // Process finalPhotosData
    finalPhotosData.forEach(p => {
      if (p.NAME && p._URL) {
        const n = robustNormalise(p.NAME);
        if (n) {
          state.appData.photoIndex[n] = p._URL;
          const parts = n.split(' ');
          if (parts.length > 1) {
            const short = robustNormalise(`${parts[0][0]}. ${parts[parts.length - 1]}`);
            state.appData.photoIndex[short] = p._URL;
          }
        }
      }
      
      if (p.Posicion && posMap[p.Posicion]) {
        state.appData.clusters[posMap[p.Posicion]].push({
          long_name: p.NAME,
          overall: p.Overall,
          cluster_id: p.Cluster_id,
          photoUrl: p._URL,
        });
      }
    });

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
