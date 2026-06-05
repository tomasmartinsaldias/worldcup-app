import io

# Fix draft.js
with io.open('frontend/js/draft.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Fix normalise in draft.js
old_func = """  const normalise = str => str ? str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim() : "";"""

new_func = """  const robustNormalise = str => {
    if (!str) return '';
    return str
      .normalize('NFD')
      .replace(/[\\u0300-\\u036f]/g, '')
      .replace(/\\u00f8/gi, 'o').replace(/\\u00f0/gi, 'd').replace(/\\u00fe/gi, 'th')
      .replace(/\\u00e6/gi, 'ae').replace(/\\u0142/gi, 'l').replace(/\\u00df/gi, 'ss').replace(/\\u0153/gi, 'oe')
      .replace(/[^\\x00-\\x7F]/g, '')
      .toLowerCase().trim();
  };"""

text = text.replace(old_func, new_func)

text = text.replace('normalise(name)', 'robustNormalise(name)')
text = text.replace('normalise(parts[0][0]', 'robustNormalise(parts[0][0]')
text = text.replace('normalise(parts[0] +', 'robustNormalise(parts[0] +')
text = text.replace('normalise(parts[parts.length - 1])', 'robustNormalise(parts[parts.length - 1])')

# 2. Fix cosine similarity mapping in draft.js
old_map = """  // Map normalized feature values (~0.15) to [-1, 1] range.
  let ritmo = (avgPace - 0.15) * 15;
  let posesion = (avgPassing - 0.15) * 15;
  let defensa = (avgDefending - 0.15) * 15;"""

new_map = """  // Map standardized feature values (mean 0, std 1) to approximately [-1, 1] range.
  let ritmo = avgPace / 3;
  let posesion = avgPassing / 3;
  let defensa = avgDefending / 3;"""
text = text.replace(old_map, new_map)

with io.open('frontend/js/draft.js', 'w', encoding='utf-8') as f:
    f.write(text)

# Fix state.js
with io.open('frontend/js/state.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Append players_final.json fetch
old_fetch = """    const photosData = await photosRes.json();
    state.appData.photoIndex = {};"""

new_fetch = """    const photosData = await photosRes.json();
    
    // Fetch players_final.json for fallback faces
    let finalPhotosData = [];
    try {
      const finalRes = await fetch(`data/data_frontend/players_final.json?t=${new Date().getTime()}`);
      if (finalRes.ok) finalPhotosData = await finalRes.json();
    } catch (e) {
      console.error("Could not fetch players_final.json", e);
    }
    
    state.appData.photoIndex = {};"""
text = text.replace(old_fetch, new_fetch)

old_loop = """      const parts = fn.split(' ');
      if (parts.length > 1) {
        const short = robustNormalise(`${parts[0][0]}. ${parts[parts.length - 1]}`);
        if (!state.appData.photoIndex[short]) state.appData.photoIndex[short] = p.p;
      }
    });"""

new_loop = """      const parts = fn.split(' ');
      if (parts.length > 1) {
        const short = robustNormalise(`${parts[0][0]}. ${parts[parts.length - 1]}`);
        if (!state.appData.photoIndex[short]) state.appData.photoIndex[short] = p.p;
      }
    });
    
    // Process finalPhotosData
    finalPhotosData.forEach(p => {
      if (p.NAME && p._URL) {
        const n = robustNormalise(p.NAME);
        if (n && !state.appData.photoIndex[n]) {
          state.appData.photoIndex[n] = p._URL;
        }
      }
    });"""
text = text.replace(old_loop, new_loop)

with io.open('frontend/js/state.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updates applied via Python.")
