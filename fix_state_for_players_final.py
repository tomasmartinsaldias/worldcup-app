import io
import re

with io.open('frontend/js/state.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Remove the 6 fetch calls for kmeans_ maps
text = re.sub(r'\s*fetch\(`\.\./data/clustering_maps/kmeans_[^`]+`\),?', '', text)

# 2. Adjust Promise.all destruction
# Before: const [mainRes, logosRes, estiloRes, arquetiposRes, photosRes, gkRes, cbRes, fbRes, midRes, wingRes, stRes] = await Promise.all([
text = re.sub(r'const \[mainRes, logosRes, estiloRes, arquetiposRes, photosRes, gkRes, cbRes, fbRes, midRes, wingRes, stRes\]', 
              r'const [mainRes, logosRes, estiloRes, arquetiposRes, photosRes]', text)

# 3. Remove the old clustering assignment
old_clusters_assignment = r'const clusters = await Promise.all\(\[gkRes, cbRes, fbRes, midRes, wingRes, stRes\].map\(async p => await parseJSON\(await p\)\)\);\s*state\.appData\.clusters = \{\s*Goalkeepers: clusters\[0\],\s*Centerbacks: clusters\[1\],\s*Fullbacks: clusters\[2\],\s*Midfielders: clusters\[3\],\s*Wingers: clusters\[4\],\s*Strikers: clusters\[5\]\s*\};\s*const photosData = await parseJSON\(photosRes\) \|\| \[\];'

new_clusters_assignment = """const photosData = await parseJSON(photosRes) || [];"""

text = re.sub(old_clusters_assignment, new_clusters_assignment, text)

# 4. Modify playersFinal logic to populate clusters
old_finalPhotos_logic = r'state\.appData\.playersFinal = finalPhotosData;\s*state\.appData\.photoIndex = \{\};'

new_finalPhotos_logic = """    state.appData.playersFinal = finalPhotosData;
    state.appData.photoIndex = {};

    // Build clusters from players_final.json
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
    }"""

text = re.sub(old_finalPhotos_logic, new_finalPhotos_logic, text)

with io.open('frontend/js/state.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("state.js modified successfully.")
