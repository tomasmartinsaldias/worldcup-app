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
      if(window.window.appState === 'quiz-fanatic') initFanaticStars();
    });

    function changeStarPattern() {
      // Al cambiar de pregunta, simplemente redibujamos un nuevo cielo estrellado al instante
      if(window.window.appState === 'quiz-fanatic') {
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

    function selectOption(btn) {
      const parent = btn.parentElement;
      const options = parent.querySelectorAll('.quiz-option');
      options.forEach(o => o.classList.remove('selected'));
      btn.classList.add('selected');
      
      const step = btn.closest('.quiz-step');
      const nextBtn = step.querySelector('.quiz-btn-next');
      nextBtn.disabled = false;
    }

    function nextQuizStep(nextStepNum) {
      const currentStep = document.querySelector('.quiz-step.active');
      currentStep.classList.remove('active');
      
      const nextStep = document.getElementById(`cq-step-${nextStepNum}`);
      if(nextStep) {
        nextStep.classList.add('active');
        document.getElementById('cq-step-text').innerText = `PASO ${nextStepNum} DE 3`;
        document.getElementById('cq-progress').style.width = `${(nextStepNum / 3) * 100}%`;
      }
    }

    function finishQuiz() {
      showRecommendations();
    }

    // --- RECOMENDACIONES ---
    function showRecommendations() {
      window.appState = 'transition';
      // Ocultar quizes
      const casualQuiz = document.getElementById('casual-quiz');
      if (casualQuiz) casualQuiz.classList.remove('visible');
      const fanaticQuiz = document.getElementById('fanatic-quiz');
      if (fanaticQuiz) fanaticQuiz.classList.remove('visible');
      
      setTimeout(() => {
        document.getElementById('recommendations-overlay').classList.add('visible');
        window.appState = 'recommendations';
        renderRecommendedCards();
      }, 500);
    }

    let cachedWcData = null;
    let allValidMatches = [];
    let showingAllRecs = false;

    function renderRecommendedCards() {
      const carousel = document.getElementById('recommendations-carousel');
      carousel.innerHTML = '<p>Cargando partidos recomendados...</p>';

      fetch('../data/wc2026_data.json')
        .then(res => res.json())
        .then(data => {
          cachedWcData = data;
          
          // Select valid matches
          allValidMatches = data.matches.filter(m => !m.home_team.is_placeholder && !m.away_team.is_placeholder);
          
          showingAllRecs = false;
          updateCarouselUI();
        })
        .catch(err => {
          console.error("Error fetching matches", err);
          carousel.innerHTML = '<p>Error al cargar recomendaciones.</p>';
        });
    }


    // Mapa de estadios → fotos reales (Wikimedia Commons, dominio público)
    const STADIUM_IMAGES = {
      'Estadio Azteca':          'https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Azteca_Stadium.jpg/800px-Azteca_Stadium.jpg',
      'Estadio Akron':           'https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Estadio_Akron_-_2018.jpg/800px-Estadio_Akron_-_2018.jpg',
      'Estadio BBVA':            'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Estadio_BBVA_Bancomer_durante_la_inauguraci%C3%B3n.jpg/800px-Estadio_BBVA_Bancomer_durante_la_inauguraci%C3%B3n.jpg',
      'MetLife Stadium':         'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/MetLife_Stadium_-_panoramio.jpg/800px-MetLife_Stadium_-_panoramio.jpg',
      'SoFi Stadium':            'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/SoFi_Stadium_aerial_view.jpg/800px-SoFi_Stadium_aerial_view.jpg',
      'AT&T Stadium':            'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/AT%26T_Stadium_-_Arlington%2C_TX.jpg/800px-AT%26T_Stadium_-_Arlington%2C_TX.jpg',
      'Hard Rock Stadium':       'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Hard_Rock_Stadium_-_2019.jpg/800px-Hard_Rock_Stadium_-_2019.jpg',
      'Mercedes-Benz Stadium':   'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Mercedes-Benz_Stadium.jpg/800px-Mercedes-Benz_Stadium.jpg',
      'Lumen Field':             'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Lumen_Field_aerial.jpg/800px-Lumen_Field_aerial.jpg',
      'NRG Stadium':             'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/NRG_Stadium_interior.jpg/800px-NRG_Stadium_interior.jpg',
      'Gillette Stadium':        'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/Gillette_Stadium_aerial.jpg/800px-Gillette_Stadium_aerial.jpg',
      "Levi's Stadium":          'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Levis_Stadium_2018.jpg/800px-Levis_Stadium_2018.jpg',
      'Lincoln Financial Field': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Lincoln_Financial_Field.jpg/800px-Lincoln_Financial_Field.jpg',
      'Arrowhead Stadium':       'https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Arrowhead_Stadium_Full.jpg/800px-Arrowhead_Stadium_Full.jpg',
      'BC Place':                'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/BC_Place_-_2011.jpg/800px-BC_Place_-_2011.jpg',
      'BMO Field':               'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/BMO_Field_2016_expansion.jpg/800px-BMO_Field_2016_expansion.jpg',
    };
    const STADIUM_FALLBACK = 'https://images.unsplash.com/photo-1522778119026-d647f0596c20?q=80&w=600&auto=format&fit=crop';

    function getStadiumImage(match) {
      const venue = match.stadium && match.stadium.venue_name;
      return STADIUM_IMAGES[venue] || STADIUM_FALLBACK;
    }

    function updateCarouselUI() {
      const carousel = document.getElementById('recommendations-carousel');
      carousel.innerHTML = '';
      
      const matchesToShow = showingAllRecs ? allValidMatches : allValidMatches.slice(0, 4);

      const explanations = [
        "Coincide con tu equipo favorito",
        "Similitud en estilo táctico",
        "Duelo de alta posesión",
        "Rivalidad histórica",
        "Partidazo asegurado",
        "Alta popularidad global"
      ];

      matchesToShow.forEach((match, index) => {
        const exp = explanations[index % explanations.length];
        const score = Math.max(70, 98 - (index % allValidMatches.length));
        const card = document.createElement('div');
        card.className = 'rec-card';
        card.innerHTML = `
          <div class="rec-bg" style="background-image: url('${getStadiumImage(match)}')"></div>
          <div class="rec-content">
            <div class="rec-score">${score}% AFINIDAD</div>
            <div style="font-size: 0.8rem; color: #ccc; margin-top: -2px; margin-bottom: 8px;">${exp}</div>
            <h3 class="rec-teams">${match.home_team.name} vs ${match.away_team.name}</h3>
            <p class="rec-type">${match.stage}</p>
            <p style="font-size:0.75rem; color:#aaa; margin-top:4px;"><i class="fa-solid fa-location-dot"></i> ${match.stadium ? match.stadium.venue_name + ', ' + match.stadium.city_name : ''}</p>
          </div>
        `;
        card.onclick = () => openMatchStats(match);
        carousel.appendChild(card);
      });
      
      // Duplicate for infinite scroll if showing all
      if (showingAllRecs) {
        matchesToShow.forEach((match, index) => {
          const exp = explanations[index % explanations.length];
          const score = Math.max(70, 98 - (index % allValidMatches.length));
          const card = document.createElement('div');
          card.className = 'rec-card';
          card.innerHTML = `
            <div class="rec-bg" style="background-image: url('${getStadiumImage(match)}')"></div>
            <div class="rec-content">
              <div class="rec-score">${score}% AFINIDAD</div>
              <div style="font-size: 0.8rem; color: #ccc; margin-top: -2px; margin-bottom: 8px;">${exp}</div>
              <h3 class="rec-teams">${match.home_team.name} vs ${match.away_team.name}</h3>
              <p class="rec-type">${match.stage}</p>
            </div>
          `;
          card.onclick = () => openMatchStats(match);
          carousel.appendChild(card);
        });
      }
    }

    let autoScrollInterval = null;
    let scrollSpeed = -1; 
    
    function startAutoScroll() {
      const carousel = document.getElementById('recommendations-carousel');
      stopAutoScroll();
      
      scrollSpeed = 1;

      autoScrollInterval = setInterval(() => {
        if (showingAllRecs && carousel.classList.contains('expanded-grid')) {
          carousel.scrollTop += scrollSpeed;
          
          // Infinite scroll logic
          const maxScroll = carousel.scrollHeight / 2;
          if (carousel.scrollTop >= maxScroll) {
            carousel.scrollTop -= maxScroll;
          } else if (carousel.scrollTop <= 0 && scrollSpeed < 0) {
            carousel.scrollTop += maxScroll;
          }
        }
      }, 20); // Faster tick for smoother movement
      
      carousel.onmousemove = (e) => {
        const rect = carousel.getBoundingClientRect();
        const y = e.clientY - rect.top;
        const height = rect.height;
        
        const normalizedY = (y / height) - 0.5; 
        
        if (Math.abs(normalizedY) < 0.1) {
          scrollSpeed = 0;
        } else {
          scrollSpeed = normalizedY * 20; // Much faster scaling
        }
      };
      
      carousel.onmouseleave = () => {
        scrollSpeed = -1; // Default moving up (scrolling to top)
      };
    }

    function stopAutoScroll() {
      if (autoScrollInterval) clearInterval(autoScrollInterval);
    }

    function toggleSeeMore() {
      showingAllRecs = !showingAllRecs;
      const carousel = document.getElementById('recommendations-carousel');
      
      // Smooth fade transition
      carousel.style.opacity = 0;
      
      setTimeout(() => {
        carousel.classList.toggle('expanded-grid', showingAllRecs);
        const btn = document.getElementById('btn-see-more');
        btn.innerText = showingAllRecs ? 'VER MENOS' : 'VER TODOS LOS PARTIDOS';
        
        updateCarouselUI();
        
        carousel.style.opacity = 1;
        
        if (showingAllRecs) {
          // Start at bottom if default is scroll up, but let's just start at top
          setTimeout(() => {
            if (showingAllRecs) startAutoScroll();
          }, 800);
        } else {
          stopAutoScroll();
          carousel.scrollTop = 0; // Reset scroll
        }
      }, 400); // Wait for fade out
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

      document.getElementById('stats-body-content').innerHTML = `
        <div class="stats-teams">
          <div class="stats-team-flag">
            <img src="${homeFlag}" onerror="this.src='../img/placeholder_flag.png'" alt="${match.home_team.name}">
            <p>${match.home_team.name}</p>
            <span>Grupo ${match.home_team.group}</span>
          </div>
          <div class="vs-badge">VS</div>
          <div class="stats-team-flag">
            <img src="${awayFlag}" onerror="this.src='../img/placeholder_flag.png'" alt="${match.away_team.name}">
            <p>${match.away_team.name}</p>
            <span>Grupo ${match.away_team.group}</span>
          </div>
        </div>

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
  