import io

with io.open('frontend/js/state.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the entire loadData function with a safe one that builds clusters from players_final.json
safe_loadData = """export async function loadData() {
  try {
    const parseJSON = async (res) => {
      try {
        if (res && res.ok) return await res.json();
        return null;
      } catch (e) {
        return null;
      }
    };

    const [mainRes, logosRes, estiloRes, arquetiposRes, photosRes, finalRes] = await Promise.all([
      fetch(`data/wc2026_data.json?t=${new Date().getTime()}`).catch(() => null),
      fetch(`data/club_logos.json?t=${new Date().getTime()}`).catch(() => null),
      fetch(`data/estilos-de-juego/selecciones_estilo?t=${new Date().getTime()}`).catch(() => null),
      fetch(`data/estilos-de-juego/arquetipos?t=${new Date().getTime()}`).catch(() => null),
      fetch(`data/players_photos.json?t=${new Date().getTime()}`).catch(() => null),
      fetch(`data/data_frontend/players_final.json?t=${new Date().getTime()}`).catch(() => null)
    ]);

    state.appData = await parseJSON(mainRes) || {};
    state.appData.clubLogos = await parseJSON(logosRes) || {};

    const estiloData = await parseJSON(estiloRes) || { response: [] };
    const arquetiposData = await parseJSON(arquetiposRes) || { archetypes: [] };
    state.appData.estilos = estiloData.response;
    state.appData.arquetipos = arquetiposData.archetypes;

    const photosData = await parseJSON(photosRes) || [];
    const finalPhotosData = await parseJSON(finalRes) || [];

    state.appData.playersFinal = finalPhotosData;
    
    // Group clusters from players_final.json
    state.appData.clusters = {
      Goalkeepers: [],
      Centerbacks: [],
      Fullbacks: [],
      Midfielders: [],
      Wingers: [],
      Strikers: []
    };

    const positionMap = {
      'Goalkeeper': 'Goalkeepers',
      'Centerbacks': 'Centerbacks',
      'Fullbacks': 'Fullbacks',
      'Midfielder': 'Midfielders',
      'Wingers': 'Wingers',
      'Striker': 'Strikers'
    };

    if (finalPhotosData && finalPhotosData.length > 0) {
      finalPhotosData.forEach(p => {
        if (p.Posicion && positionMap[p.Posicion]) {
          const groupName = positionMap[p.Posicion];
          if (p.Cluster_id !== null && p.Cluster_id !== undefined) {
            state.appData.clusters[groupName].push({
              long_name: p.NAME,
              overall: p.Overall,
              cluster_id: p.Cluster_id,
              dist_centroid: p.Dist_centroid,
              photoUrl: p._URL
            });
          }
        }
      });
    }

    state.appData.photoIndex = {};
    const robustNormalise = str => {
      if (!str) return '';
      return str
        .normalize('NFD')
        .replace(/[\\u0300-\\u036f]/g, '')
        .replace(/\\u00f8/gi, 'o').replace(/\\u00f0/gi, 'd').replace(/\\u00fe/gi, 'th')
        .replace(/\\u00e6/gi, 'ae').replace(/\\u0142/gi, 'l').replace(/\\u00df/gi, 'ss').replace(/\\u0153/gi, 'oe')
        .replace(/[^\\x00-\\x7F]/g, '')
        .toLowerCase().trim();
    };
    photosData.forEach(p => {
      const n = robustNormalise(p.n);
      const fn = robustNormalise(p.fn);
      if (fn) state.appData.photoIndex[fn] = p.p;
      if (n && !state.appData.photoIndex[n]) state.appData.photoIndex[n] = p.p;

      const parts = fn.split(' ');
      if (parts.length > 1) {
        const short = robustNormalise(`${parts[0][0]}. ${parts[parts.length - 1]}`);
        if (!state.appData.photoIndex[short]) state.appData.photoIndex[short] = p.p;
      }
    });

    finalPhotosData.forEach(p => {
      if (p.NAME && p._URL) {
        const n = robustNormalise(p.NAME);
        if (n && !state.appData.photoIndex[n]) {
          state.appData.photoIndex[n] = p._URL;
        }
      }
    });

    mapTeamEstilos(state.appData);
    console.log('Main data loaded:', state.appData);
  } catch (err) {
    console.error('Error loading data:', err);
  }
}"""

import re
text = re.sub(r'export async function loadData\(\) \{.*?\n\}\n\nfunction mapTeamEstilos', safe_loadData + '\n\nfunction mapTeamEstilos', text, flags=re.DOTALL)

with io.open('frontend/js/state.js', 'w', encoding='utf-8') as f:
    f.write(text)
print('state.js updated securely!')
