import { state } from './futstate.js';
import { calculateSmartScore } from './scoring.js';

function startQuiz(level) {
  if(level === 'casual') {
    window.appState = 'transition';
    document.getElementById('spectator-selection').classList.remove('visible');
    setTimeout(() => {
      document.getElementById('casual-quiz').classList.add('visible');
      window.appState = 'quiz-casual';
    }, 500);
  } else if(level === 'intermedio') {
    window.appState = 'transition';
    document.getElementById('spectator-selection').classList.remove('visible');
    setTimeout(() => {
      if (typeof window.openDraftOverlay === 'function') {
        window.openDraftOverlay();
      }
      window.appState = 'draft';
    }, 500);
  } else if(level === 'fanatico') {
    window.appState = 'transition';
    document.getElementById('spectator-selection').classList.remove('visible');
    setTimeout(() => {
      document.getElementById('draft-template').classList.remove('hidden');
      document.getElementById('draft-template').classList.add('visible');
      window.appState = 'draft';
      if (window.startDraft) window.startDraft(true);
    }, 500);
  }
}

// --- LÓGICA FANÁTICO ---
const fanaticCanvas = document.getElementById('fanatic-stars');
let fctx = null;
let fWidth, fHeight;

if (fanaticCanvas) {
  fctx = fanaticCanvas.getContext('2d');
}

function initFanaticStars() {
  if (!fanaticCanvas) return;
  fWidth = window.innerWidth;
  fHeight = window.innerHeight;
  fanaticCanvas.width = fWidth;
  fanaticCanvas.height = fHeight;
  
  fctx.clearRect(0, 0, fWidth, fHeight);
  
  // Estrellas fijas dibujadas una sola vez (0 lag)
  for(let i=0; i<150; i++) {
    const x = Math.random() * fWidth;
    const y = Math.random() * fHeight;
    const size = Math.random() * 1.5 + 0.5;
    const opacity = Math.random() * 0.7 + 0.3;
    
    fctx.beginPath();
    fctx.arc(x, y, size, 0, Math.PI * 2);
    fctx.fillStyle = `rgba(255, 255, 255, ${opacity})`;
    
    // Solo algunas brillan sutilmente para no sobrecargar el renderizado
    if (Math.random() > 0.8) {
      fctx.shadowBlur = 8;
      fctx.shadowColor = '#0A58FF'; // Toque azul neón
    } else {
      fctx.shadowBlur = 0;
    }
    
    fctx.fill();
    fctx.shadowBlur = 0;
  }
}

window.addEventListener('resize', () => {
  if(window.appState === 'quiz-fanatic') initFanaticStars();
});

function changeStarPattern() {
  // Al cambiar de pregunta, simplemente redibujamos un nuevo cielo estrellado al instante
  if(window.appState === 'quiz-fanatic') {
    initFanaticStars();
  }
}

function nextFanaticStep(currentStepNum, btn) {
  if(btn) btn.classList.add('fq-selected');
  
  setTimeout(() => {
    const currentStep = document.getElementById(`fq-step-${currentStepNum}`);
    if(currentStep) currentStep.classList.remove('active');
    
    const nextStepNum = currentStepNum + 1;
    const nextStep = document.getElementById(`fq-step-${nextStepNum}`);
    
    if(nextStep) {
      nextStep.classList.add('active');
      document.getElementById('fq-step-text').innerText = `PASO ${nextStepNum} DE 5`;
      document.getElementById('fq-progress').style.width = `${(nextStepNum / 5) * 100}%`;
      
      changeStarPattern();
    } else {
      showRecommendations();
    }
  }, 500);
}

    // --- RECOMENDACIONES ---
    window.showRecommendations = async function() {
      window.appState = 'transition';
      
      const survey = document.getElementById('antigravity-survey');
      if (survey) survey.classList.remove('visible');
      const draftOverlay = document.getElementById('draft-template');
      if (draftOverlay) {
        draftOverlay.classList.remove('visible');
        draftOverlay.classList.add('hidden');
      }
      
      setTimeout(async () => {
        document.getElementById('recommendations-overlay').classList.add('visible');
        window.appState = 'recommendations';
        await renderRecommendedCards();
      }, 500);
    }

    let cachedWcData = null;
    let allValidMatches = [];
    window.scoredMatches = [];
    let showingAllRecs = false;

    async function renderRecommendedCards() {
      const container = document.getElementById('recommendations-list');
      if (container) {
        container.innerHTML = '<p style="text-align:center; font-family:Outfit; margin-top:50px;">⚽ Analizando tu perfil...</p>';
      }

      try {
        const { mapSurveyToPreferences, generateRecommendations } = await import('./recommender.js');
        
        // Ensure data is loaded
        if (!cachedWcData) {
          const res = await fetch('data/wc2026_data.json');
          cachedWcData = await res.json();
        }
        allValidMatches = cachedWcData.matches.filter(m => !m.home_team.is_placeholder && !m.away_team.is_placeholder);

        const rawResults = window.surveyRawResults || { userType: 'casual' };
        const prefs = mapSurveyToPreferences(rawResults);
        console.log('[Recommender] Preferences mapped:', prefs);

        const scored = generateRecommendations(prefs);
        window.scoredMatches = scored;
        
        renderCategorizedResults();
      } catch (err) {
        console.error("Error generating recommendations", err);
        const container = document.getElementById('recommendations-list');
        if (container) {
          container.innerHTML = '<p>Error al calcular recomendaciones. Por favor reintenta.</p>';
        }
      }
    }


    // Mapa de estadios → fotos locales
    const STADIUM_IMAGES = {
      'Estadio Azteca':          'img/stadiums/Estadio_Azteca.jpg',
      'Estadio Akron':           'img/stadiums/Estadio_Akron.jpg',
      'Estadio BBVA':            'img/stadiums/Estadio_BBVA.jpg',
      'MetLife Stadium':         'img/stadiums/MetLife_Stadium.jpg',
      'SoFi Stadium':            'img/stadiums/SoFi_Stadium.jpg',
      'AT&T Stadium':            'img/stadiums/ATandT_Stadium.jpg',
      'Hard Rock Stadium':       'img/stadiums/Hard_Rock_Stadium.jpg',
      'Mercedes-Benz Stadium':   'img/stadiums/Mercedes-Benz_Stadium.jpg',
      'Lumen Field':             'img/stadiums/Lumen_Field.jpg',
      'NRG Stadium':             'img/stadiums/NRG_Stadium.jpg',
      'Gillette Stadium':        'img/stadiums/Gillette_Stadium.jpg',
      "Levi's Stadium":          'https://images.unsplash.com/photo-1522778119026-d647f0596c20?q=80&w=600&auto=format&fit=crop',
      'Lincoln Financial Field': 'img/stadiums/Lincoln_Financial_Field.jpg',
      'Arrowhead Stadium':       'img/stadiums/Arrowhead_Stadium.jpg',
      'BC Place':                'https://images.unsplash.com/photo-1522778119026-d647f0596c20?q=80&w=600&auto=format&fit=crop',
      'BMO Field':               'https://images.unsplash.com/photo-1522778119026-d647f0596c20?q=80&w=600&auto=format&fit=crop',
    };
    const STADIUM_FALLBACK = 'https://images.unsplash.com/photo-1522778119026-d647f0596c20?q=80&w=600&auto=format&fit=crop';

    function getStadiumImage(match) {
      const venue = match.stadium && match.stadium.venue_name;
      return STADIUM_IMAGES[venue] || STADIUM_FALLBACK;
    }
    function renderCategorizedResults() {
      const container = document.getElementById('recommendations-list');
      container.innerHTML = '';
      
      const imperdible = [];
      const valeLaPena = [];
      const resumen = [];

      window.scoredMatches.forEach(item => {
        const pct = Math.min(100, Math.round(item.score * 10));
        
        if (pct >= 80) {
          imperdible.push(item);
        } else if (pct >= 50) {
          valeLaPena.push(item);
        } else {
          resumen.push(item);
        }
      });

      const buildCard = (item) => {
        const { match, score, explanation } = item;
        const displayScore = Math.min(100, Math.round(score * 10));
        const extraClass = item.outOfSchedule ? ' out-of-schedule-card' : '';
        return `
          <div class="rec-card${extraClass}" onclick="openMatchStatsById('${match.id}')">
            <div class="rec-bg" style="background-image: url('${getStadiumImage(match)}')"></div>
            <div class="rec-content">
              <div class="rec-score">${displayScore}% AFINIDAD</div>
              <div style="font-size: 0.8rem; color: #ccc; margin-top: -2px; margin-bottom: 8px;">${explanation}</div>
              <h3 class="rec-teams">${match.home_team.name} vs ${match.away_team.name}</h3>
              <p class="rec-type">${match.stage}</p>
              <p style="font-size:0.75rem; color:#aaa; margin-top:4px;"><i class="fa-solid fa-location-dot"></i> ${match.stadium ? match.stadium.venue_name + ', ' + match.stadium.city_name : ''}</p>
              ${item.outOfSchedule ? '<p style="font-size:0.75rem; color:#ff8888; margin-top:4px;"><i class="fa-solid fa-clock"></i> Fuera de tu horario</p>' : ''}
            </div>
          </div>
        `;
      };

      const addSection = (title, icon, items, className) => {
        if (items.length === 0) return;
        const section = document.createElement('div');
        section.className = `category-section ${className}`;
        
        const gridHtml = items.map(buildCard).join('');
        
        section.innerHTML = `
          <h3 class="category-title"><i class="${icon}"></i> ${title}</h3>
          <div class="matches-grid">
            ${gridHtml}
          </div>
        `;
        container.appendChild(section);
      };

      addSection('Imperdible', 'fa-solid fa-fire', imperdible, 'section-imperdible');
      addSection('Vale la pena', 'fa-solid fa-thumbs-up', valeLaPena, 'section-valelapena');
      addSection('Para ver el resumen', 'fa-solid fa-tv', resumen, 'section-resumen');
    }

    function openMatchStats(match) {
  document.getElementById('stats-modal-overlay').classList.add('visible');
  document.getElementById('stats-title').innerHTML = `Partido #${match.match_number} &bull; ${match.stage}`;
  
  const homeFifa = match.home_team.fifa_code;
  const awayFifa = match.away_team.fifa_code;
  const homeFlag = `https://flagcdn.com/w80/${getCountryIsoCode(homeFifa)}.png`;
  const awayFlag = `https://flagcdn.com/w80/${getCountryIsoCode(awayFifa)}.png`;

  // H2H Logic
  const h2h = match.h2h || { total_matches: 0, home_wins: 0, away_wins: 0, draws: 0 };
  const totalH2H = h2h.total_matches > 0 ? h2h.total_matches : 1;
  const homePct = Math.round((h2h.home_wins / totalH2H) * 100);
  const drawPct = Math.round((h2h.draws / totalH2H) * 100);
  const awayPct = Math.round((h2h.away_wins / totalH2H) * 100);

  // Metrics Logic (Safe Fallback)
  const tDataHome = cachedWcData?.teams?.[homeFifa]?.metrics || {};
  const tDataAway = cachedWcData?.teams?.[awayFifa]?.metrics || {};

  const formatVal = (v) => v !== undefined ? v : 'N/A';
  
  const mHome = {
    val: tDataHome.market_value_eur || 100,
    xg: tDataHome.recent_xg_avg || 1.0,
    pos: tDataHome.recent_possession_avg || 50,
    pop: tDataHome.global_popularity_score || 50
  };
  
  const mAway = {
    val: tDataAway.market_value_eur || 100,
    xg: tDataAway.recent_xg_avg || 1.0,
    pos: tDataAway.recent_possession_avg || 50,
    pop: tDataAway.global_popularity_score || 50
  };

  const computeBar = (a, b) => {
    const sum = a + b || 1;
    return [(a/sum)*100, (b/sum)*100];
  };

  const [valA, valB] = computeBar(mHome.val, mAway.val);
  const [xgA, xgB] = computeBar(mHome.xg, mAway.xg);
  const [popA, popB] = computeBar(mHome.pop, mAway.pop);

  // Calculate Segmented Score Breakdown HTML dynamically
  const bd = match.scoreBreakdown;
  let breakdownHtml = '';
  if (bd) {
    const segments = [];
    if (bd.W_ent > 0 && bd.val_entretenimiento > 0) {
      segments.push({
        name: 'Entretenimiento',
        class: 'ent',
        weight: bd.W_ent,
        val: bd.val_entretenimiento,
        color: '#e74c3c',
        icon: '🍿',
        details: [
          { label: 'Espectáculo (ICE)', val: bd.entertainment.val_espectaculo, w: bd.entertainment.w_esp },
          { label: 'Fricción', val: bd.entertainment.val_friccion, w: bd.entertainment.w_fric }
        ]
      });
    }
    if (bd.W_tec > 0 && bd.val_tactica > 0) {
      segments.push({
        name: 'Táctica',
        class: 'tac',
        weight: bd.W_tec,
        val: bd.val_tactica,
        color: '#0088ff',
        icon: '🧠',
        details: [
          { label: 'Estilo de Juego', val: bd.tactical.val_estilo, w: bd.tactical.w_style },
          ...(bd.tactical.w_cluster > 0 ? [{ label: 'Borrador (Cluster)', val: bd.tactical.val_cluster, w: bd.tactical.w_cluster }] : [])
        ]
      });
    }
    if (bd.W_af > 0 && bd.val_afectivo > 0) {
      segments.push({
        name: 'Afectivo',
        class: 'afec',
        weight: bd.W_af,
        val: bd.val_afectivo,
        color: '#f5d061',
        icon: '❤️',
        details: [
          ...(bd.affective.w_club > 0 ? [{ label: 'Club Favorito', val: bd.affective.val_club, w: bd.affective.w_club }] : []),
          ...(bd.affective.w_sel > 0 ? [{ label: 'Selección Favorita', val: bd.affective.val_sel, w: bd.affective.w_sel }] : []),
          ...(bd.affective.w_jug > 0 ? [{ label: 'Jugador Favorito', val: bd.affective.val_jug, w: bd.affective.w_jug }] : [])
        ]
      });
    }

    const activeWeightSum = segments.reduce((sum, s) => sum + s.weight, 0);
    if (segments.length > 0) {
      const barSegmentsHtml = segments.map(s => {
        const percent = activeWeightSum > 0 ? (s.weight / activeWeightSum) * 100 : 0;
        return `
          <div class="bar-segment ${s.class}" style="width: ${percent}%; background: ${s.color}; position: relative;">
            <span class="segment-label">${s.icon} ${Math.round(percent)}%</span>
            
            <div class="segment-tooltip">
              <div class="tooltip-header">
                <strong>${s.name}</strong>
                <span>Score: ${s.val.toFixed(1)}/10</span>
              </div>
              <div class="tooltip-divider"></div>
              <div class="tooltip-micro-list">
                ${s.details.map(d => `
                  <div class="tooltip-micro-item">
                    <span>${d.label} (peso ${d.w}):</span>
                    <strong>${d.val.toFixed(1)}/10</strong>
                  </div>
                `).join('')}
              </div>
            </div>
          </div>
        `;
      }).join('');

      const legendHtml = segments.map(s => `
        <div class="legend-item">
          <span class="legend-color-dot" style="background: ${s.color};"></span>
          <span>${s.name}: <strong>${s.val.toFixed(1)}/10</strong></span>
        </div>
      `).join('');

      breakdownHtml = `
        <div class="score-breakdown-container">
          <div class="score-breakdown-header">
            <h4>AFINIDAD DE SCORE: <span class="affinity-number">${(match.smartScore).toFixed(1)} / 10</span></h4>
          </div>
          
          <div class="segmented-bar">
            ${barSegmentsHtml}
          </div>
          
          <div class="segmented-bar-legend">
            ${legendHtml}
          </div>
        </div>
      `;
    }
  }

  document.getElementById('stats-body-content').innerHTML = `
    <div class="stats-teams">
      <div class="stats-team-flag">
        <img src="${homeFlag}" onerror="this.src='./img/placeholder_flag.png'" alt="${match.home_team.name}">
        <p>${match.home_team.name}</p>
        <span>Grupo ${match.home_team.group}</span>
      </div>
      <div class="vs-badge">VS</div>
      <div class="stats-team-flag">
        <img src="${awayFlag}" onerror="this.src='./img/placeholder_flag.png'" alt="${match.away_team.name}">
        <p>${match.away_team.name}</p>
        <span>Grupo ${match.away_team.group}</span>
      </div>
    </div>

    ${breakdownHtml}

    <div class="modal-grid">
      <div class="h2h-box">
        <div class="h2h-title"><i class="fa-solid fa-clock-rotate-left"></i> HISTORIAL CARA A CARA (H2H) GENERAL</div>
        <div class="h2h-stats">
          <div class="h2h-stat"><strong>${h2h.total_matches}</strong><span style="color:#aaa;">PARTIDOS</span></div>
          <div class="h2h-stat"><strong style="color:#2e8b57">${h2h.home_wins}</strong><span style="color:#2e8b57">VICTORIAS ${homeFifa}</span></div>
          <div class="h2h-stat"><strong style="color:#aaa">${h2h.draws}</strong><span style="color:#aaa">EMPATES</span></div>
          <div class="h2h-stat"><strong style="color:#e24a4a">${h2h.away_wins}</strong><span style="color:#e24a4a">VICTORIAS ${awayFifa}</span></div>
        </div>
        ${h2h.total_matches > 0 ? `
          <div class="h2h-bar">
            <div class="h2h-green" style="width: ${homePct}%">${homePct > 10 ? homePct+'%' : ''}</div>
            <div class="h2h-gray" style="width: ${drawPct}%">${drawPct > 10 ? drawPct+'%' : ''}</div>
            <div class="h2h-red" style="width: ${awayPct}%">${awayPct > 10 ? awayPct+'%' : ''}</div>
          </div>
        ` : '<p style="text-align:center; font-size:0.8rem; color:#666;">No hay enfrentamientos previos.</p>'}
      </div>

      <div class="h2h-title" style="margin-top: 1rem;"><i class="fa-solid fa-chart-simple"></i> COMPARATIVA DE MÉTRICAS RECIENTES</div>
      
      <div class="metrics-grid">
        <!-- Valor -->
        <div class="metric-card">
          <div class="metric-title">VALOR DE PLANTILLA (M€)</div>
          <div class="metric-values">
            <span class="metric-val-a">${mHome.val}M€</span>
            <span class="metric-val-b">${mAway.val}M€</span>
          </div>
          <div class="metric-bar-container">
            <div class="metric-bar-a" style="width: ${valA}%"></div>
            <div class="metric-bar-b" style="width: ${valB}%"></div>
          </div>
        </div>

        <!-- XG -->
        <div class="metric-card">
          <div class="metric-title">PROMEDIO GOLES ESPERADOS (XG)</div>
          <div class="metric-values">
            <span class="metric-val-a">${mHome.xg.toFixed(2)}</span>
            <span class="metric-val-b">${mAway.xg.toFixed(2)}</span>
          </div>
          <div class="metric-bar-container">
            <div class="metric-bar-a" style="width: ${xgA}%"></div>
            <div class="metric-bar-b" style="width: ${xgB}%"></div>
          </div>
        </div>

        <!-- Posesion -->
        <div class="metric-card">
          <div class="metric-title">PORCENTAJE DE POSESIÓN</div>
          <div class="metric-values">
            <span class="metric-val-a">${mHome.pos.toFixed(1)}%</span>
            <span style="font-size: 0.8rem; color: #555; align-self: center;">VS</span>
            <span class="metric-val-b">${mAway.pos.toFixed(1)}%</span>
          </div>
        </div>

        <!-- Popularidad -->
        <div class="metric-card">
          <div class="metric-title">POPULARIDAD GLOBAL</div>
          <div class="metric-values">
            <span class="metric-val-a">${mHome.pop}</span>
            <span class="metric-val-b">${mAway.pop}</span>
          </div>
          <div class="metric-bar-container">
            <div class="metric-bar-a" style="width: ${popA}%"></div>
            <div class="metric-bar-b" style="width: ${popB}%"></div>
          </div>
        </div>
      </div>
    </div>
  `;
}

// Helper flag iso mapping simple (would normally be full map)
function getCountryIsoCode(fifaCode) {
  const map = { 'ARG': 'ar', 'FRA': 'fr', 'BRA': 'br', 'ENG': 'gb-eng', 'ESP': 'es', 'GER': 'de', 'MEX': 'mx', 'USA': 'us', 'NOR': 'no', 'SEN': 'sn' };
  return map[fifaCode] || fifaCode.toLowerCase().substring(0, 2);
}

function closeMatchStats() {
  document.getElementById('stats-modal-overlay').classList.remove('visible');
}

function openMatchStatsById(id) {
  const item = (window.scoredMatches || []).find(item => String(item.match.id) === String(id));
  if (item) {
    const match = item.match;
    match.smartScore = item.score;
    openMatchStats(match);
  } else {
    const match = allValidMatches.find(m => String(m.id) === String(id));
    if (match) {
      openMatchStats(match);
    } else {
      console.error("Match not found for ID:", id);
    }
  }
}

// Bind to window to allow HTML inline onclick attributes to find them
window.startQuiz = startQuiz;
window.nextFanaticStep = nextFanaticStep;
window.openMatchStats = openMatchStats;
window.openMatchStatsById = openMatchStatsById;
window.closeMatchStats = closeMatchStats;
  
