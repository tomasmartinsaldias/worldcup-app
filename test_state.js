const fs = require('fs');

global.fetch = async (url) => {
  return { ok: true, json: async () => ({}) };
};
global.localStorage = { getItem: () => null };

let stateJs = fs.readFileSync('./frontend/js/state.js', 'utf8');
stateJs = stateJs.replace(/export /g, '');
eval(stateJs);

(async () => {
  await loadData();
  console.log("CLUSTERS:", state.appData.clusters ? Object.keys(state.appData.clusters) : 'null');
})();
