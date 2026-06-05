const fs = require('fs');
let code = fs.readFileSync('frontend/js/landing-quiz.js', 'utf-8');

const startStr = '    function renderCategorizedResults() {';
const endStr = '    function openMatchStats(match) {';

const startIndex = code.indexOf(startStr);
const endIndex = code.indexOf(endStr);

if (startIndex === -1 || endIndex === -1) {
  console.log('Not found');
  process.exit(1);
}

const newBlock = `    function renderCategorizedResults() {
      const container = document.getElementById('recommendations-list');
      container.innerHTML = '';
      
      const imperdible = [];
      const valeLaPena = [];
      const resumen = [];
      const fueraHorario = [];

      window.scoredMatches.forEach(item => {
        if (item.outOfSchedule) {
          fueraHorario.push(item);
        } else {
          // Normalize score to percentage
          const pct = Math.min(100, Math.round(item.score * 10));
          if (pct >= 80) imperdible.push(item);
          else if (pct >= 50) valeLaPena.push(item);
          else resumen.push(item);
        }
      });

      const buildCard = (item) => {
        const { match, score, explanation } = item;
        const displayScore = Math.min(100, Math.round(score * 10));
        return \`
          <div class="rec-card" onclick="openMatchStatsById('\${match.id}')">
            <div class="rec-bg" style="background-image: url('\${getStadiumImage(match)}')"></div>
            <div class="rec-content">
              <div class="rec-score">\${displayScore}% AFINIDAD</div>
              <div style="font-size: 0.8rem; color: #ccc; margin-top: -2px; margin-bottom: 8px;">\${explanation}</div>
              <h3 class="rec-teams">\${match.home_team.name} vs \${match.away_team.name}</h3>
              <p class="rec-type">\${match.stage}</p>
              <p style="font-size:0.75rem; color:#aaa; margin-top:4px;"><i class="fa-solid fa-location-dot"></i> \${match.stadium ? match.stadium.venue_name + ', ' + match.stadium.city_name : ''}</p>
              \${item.outOfSchedule ? '<p style="font-size:0.75rem; color:#ff8888; margin-top:4px;"><i class="fa-solid fa-clock"></i> Fuera de tu horario</p>' : ''}
            </div>
          </div>
        \`;
      };

      const addSection = (title, icon, items, className) => {
        if (items.length === 0) return;
        const section = document.createElement('div');
        section.className = \`category-section \${className}\`;
        
        const gridHtml = items.map(buildCard).join('');
        
        section.innerHTML = \`
          <h3 class="category-title"><i class="\${icon}"></i> \${title}</h3>
          <div class="matches-grid">
            \${gridHtml}
          </div>
        \`;
        container.appendChild(section);
      };

      addSection('Imperdible', 'fa-solid fa-fire', imperdible, '');
      addSection('Vale la pena', 'fa-solid fa-thumbs-up', valeLaPena, '');
      addSection('Para ver el resumen', 'fa-solid fa-tv', resumen, '');
      addSection('Partidos fuera de horario', 'fa-solid fa-clock', fueraHorario, 'out-of-schedule');
    }

`;

code = code.substring(0, startIndex) + newBlock + code.substring(endIndex);
fs.writeFileSync('frontend/js/landing-quiz.js', code);
console.log('Fixed');
