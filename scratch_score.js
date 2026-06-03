const fs = require('fs');

const data = JSON.parse(fs.readFileSync('data/wc2026_data.json', 'utf8'));
const sofascore = JSON.parse(fs.readFileSync('data/selecciones_vectors.json', 'utf8'));

// Find Colombia and Portugal
const teams = data.teams;
let col = null, por = null;

for (const code in teams) {
    if (teams[code].name === 'Colombia') col = teams[code];
    if (teams[code].name === 'Portugal') por = teams[code];
}

console.log("Colombia:", col ? col.fifa_code : 'not found');
console.log("Portugal:", por ? por.fifa_code : 'not found');

if (col && por) {
    const rHome = col.metrics ? col.metrics.fifa_ranking : 60;
    const rAway = por.metrics ? por.metrics.fifa_ranking : 60;
    console.log("FIFA Rankings:", rHome, rAway);
    
    console.log("Stars Colombia:", col.squad ? col.squad.filter(p => p.is_star_player).length : 0);
    console.log("Stars Portugal:", por.squad ? por.squad.filter(p => p.is_star_player).length : 0);
    
    console.log("Espectaculo Colombia:", col.espectaculo_params);
    console.log("Espectaculo Portugal:", por.espectaculo_params);
}
