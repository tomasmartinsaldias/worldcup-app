import { state } from './state.js';
import { filterMatches, sortMatchesList, renderMatches } from './ui/matches.js';
import { getPlayerPhotoUrl, getCountryIsoCode } from './utils.js';

// ---- Suggested teams shown first ----
const SUGGESTED_TEAMS = ['ARG', 'BRA', 'ESP', 'FRA', 'GER'];

// ---- Estado del Quiz ----
let quizState = {
  currentQuestion: 0,
  answers: {
    teams: [],
    timeSlots: [],
    emotion: '',
    clubs: [],
    players: [],
    possession: 50,
    intensity: 50,
    agePreference: 50   // 0 = youth, 100 = experience
  }
};

const TOTAL_QUESTIONS = 9; // 8 questions + 1 results screen

// ---- Cached entity lists (extracted once from appData) ----
let allClubsList = [];
let allPlayersList = [];

function extractAllEntities() {
  if (!state.appData || !state.appData.teams) return;
  const clubsSet = new Map();
  const playersArr = [];

  Object.values(state.appData.teams).forEach(team => {
    if (team.is_placeholder || !team.squad) return;
    team.squad.forEach(p => {
      // Collect players
      playersArr.push({
        name: p.name,
        club: p.club || '',
        position: p.position || '',
        teamCode: team.fifa_code,
        teamName: team.name,
        isStar: p.is_star_player,
        age: p.age || 0,
        marketValue: p.market_value_eur || 0
      });
      // Collect clubs
      if (p.club && !clubsSet.has(p.club)) {
        clubsSet.set(p.club, { name: p.club, playerCount: 1 });
      } else if (p.club) {
        clubsSet.get(p.club).playerCount++;
      }
    });
  });

  // Sort players by market value (stars first), then alphabetically
  allPlayersList = playersArr.sort((a, b) => {
    if (a.isStar && !b.isStar) return -1;
    if (!a.isStar && b.isStar) return 1;
    return (b.marketValue || 0) - (a.marketValue || 0);
  });

  // Sort clubs by player count (popular first)
  allClubsList = Array.from(clubsSet.values()).sort((a, b) => b.playerCount - a.playerCount);
}

// ---- Referencias UI ----
let overlay, btnBack, btnNext, btnSkip, btnClose, stepIndicator, progressFill;

export function initQuiz() {
  overlay = document.getElementById('quiz-overlay');
  btnBack = document.getElementById('quiz-btn-back');
  btnNext = document.getElementById('quiz-btn-next');
  btnSkip = document.getElementById('quiz-btn-skip');
  btnClose = document.getElementById('quiz-btn-close');
  stepIndicator = document.getElementById('quiz-step-indicator');
  progressFill = document.getElementById('quiz-progress-fill');

  // Trigger Open
  const btnOpen = document.getElementById('btn-open-quiz');
  if (btnOpen) {
    btnOpen.addEventListener('click', openQuiz);
  }

  // Navigation
  btnBack.addEventListener('click', prevQuestion);
  btnNext.addEventListener('click', () => {
    if (quizState.currentQuestion === TOTAL_QUESTIONS - 2) {
      showResults();
    } else if (quizState.currentQuestion === TOTAL_QUESTIONS - 1) {
      finishQuiz();
    } else {
      nextQuestion();
    }
  });
  btnSkip.addEventListener('click', () => {
    if (quizState.currentQuestion === TOTAL_QUESTIONS - 2) {
      showResults();
    } else if (quizState.currentQuestion === TOTAL_QUESTIONS - 1) {
      finishQuiz();
    } else {
      nextQuestion();
    }
  });
  btnClose.addEventListener('click', closeQuiz);

  // Init Question logic
  initQ2(); // Horarios
  initQ3(); // Emocion
  initQ6(); // Posesion
  initQ7(); // Intensidad
  initQ8(); // Age preference
}

function openQuiz() {
  quizState.currentQuestion = 0;
  quizState.answers = {
    teams: [], timeSlots: [], emotion: '',
    clubs: [], players: [],
    possession: 50, intensity: 50, agePreference: 50
  };

  // Extract entities from loaded data (once)
  if (allPlayersList.length === 0) extractAllEntities();

  // Q1 needs state.appData so we init it here when opening
  initQ1();
  initQ4();
  initQ5();

  updateQuizUI();
  overlay.classList.add('active');
}

function closeQuiz() {
  overlay.classList.remove('active');
}

// ==========================================
// VECTOR CALCULATION
// ==========================================
function calculateUserVector() {
  const ans = quizState.answers;
  let vector = {
    golesPartido: 0.5,
    posesion: ans.possession / 100,
    regates: 0.5,
    tirosPartido: 0.5,
    faltasPartido: 0.5,
    tarjetas: 0.5,
    contraataques_per_game: 0.5,
    presionAlta: 0.5,
    porteriaInvictaRatio: 0.5,
    duelos: 0.5
  };

  // Adjust from emotion (Q3)
  switch(ans.emotion) {
    case 'goleada':
      vector.golesPartido = 1.0;
      vector.tirosPartido = 0.9;
      vector.porteriaInvictaRatio = 0.1;
      break;
    case 'tactico':
      vector.golesPartido = 0.2;
      vector.porteriaInvictaRatio = 0.9;
      vector.presionAlta = 0.8;
      break;
    case 'frenetico':
      vector.contraataques_per_game = 1.0;
      vector.tirosPartido = 0.8;
      vector.posesion = 0.3;
      break;
    case 'estrellas':
      vector.regates = 1.0;
      vector.duelos = 0.7;
      break;
    case 'fisico':
      vector.faltasPartido = 1.0;
      vector.tarjetas = 1.0;
      vector.duelos = 1.0;
      vector.presionAlta = 0.9;
      break;
  }

  // Adjust from intensity (Q7)
  const int = ans.intensity / 100;
  vector.faltasPartido = (vector.faltasPartido + int) / 2;
  vector.tarjetas = (vector.tarjetas + int) / 2;
  vector.duelos = (vector.duelos + int) / 2;

  state.userPreferences.quizVector = vector;

  // Set dramaBeta preference
  let dramaBeta = 0.2;
  if(ans.emotion === 'fisico') dramaBeta += 0.3;
  dramaBeta += (ans.intensity - 50) / 100 * 0.4;
  state.userPreferences.dramaBeta = Math.min(1.0, Math.max(0.0, dramaBeta));

  return vector;
}

let quizRadarChart = null;

function showResults() {
  const vector = calculateUserVector();

  // Create/Update radar chart
  const ctx = document.getElementById('quiz-radar-chart');
  if (ctx) {
    if (quizRadarChart) quizRadarChart.destroy();

    quizRadarChart = new Chart(ctx, {
      type: 'radar',
      data: {
        labels: ['Goles', 'Posesión', 'Regates', 'Intensidad', 'Faltas', 'Contraataques', 'Presión', 'Defensa'],
        datasets: [{
          label: 'Tu Perfil',
          data: [
            vector.golesPartido,
            vector.posesion,
            vector.regates,
            vector.duelos,
            (vector.faltasPartido + vector.tarjetas) / 2,
            vector.contraataques_per_game,
            vector.presionAlta,
            vector.porteriaInvictaRatio
          ].map(v => Math.round(v * 100)),
          backgroundColor: 'rgba(232, 35, 26, 0.25)',
          borderColor: 'rgba(232, 35, 26, 1)',
          borderWidth: 2,
          pointBackgroundColor: 'rgba(26, 122, 60, 1)',
          pointBorderColor: '#fff',
          pointRadius: 4,
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(26, 122, 60, 1)'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        scales: {
          r: {
            angleLines: { color: 'rgba(255, 255, 255, 0.08)' },
            grid: { color: 'rgba(255, 255, 255, 0.08)' },
            pointLabels: { color: 'rgba(255, 255, 255, 0.7)', font: { family: "'Barlow Condensed', sans-serif", size: 11 } },
            ticks: { display: false, min: 0, max: 100 }
          }
        },
        plugins: { legend: { display: false } }
      }
    });
  }

  // Pre-calculate affinity for matches to show Top 5
  if (state.appData && state.appData.matches) {
    import('./scoring.js').then(module => {
      // First, persist quiz choices to state so scoring can use them
      state.userPreferences.favoriteTeams = quizState.answers.teams;
      state.userPreferences.favoritePlayers = quizState.answers.players;
      state.userPreferences.favoriteClubs = quizState.answers.clubs;
      state.userPreferences.agePreference = quizState.answers.agePreference;

      // Calculate smart scores with all quiz bonuses
      state.appData.matches.forEach(m => {
        m.smartScore = module.calculateSmartScore(m, state.appData.teams, state.userPreferences?.tacticalVector);
      });

      // Sort by smartScore for top 5
      const sorted = [...state.appData.matches]
        .filter(m => !m.home_team?.is_placeholder && !m.away_team?.is_placeholder)
        .sort((a, b) => (b.smartScore || 0) - (a.smartScore || 0));
      const top5 = sorted.slice(0, 5);

      const listContainer = document.getElementById('quiz-affinity-list');
      if (listContainer) {
        listContainer.innerHTML = '';
        top5.forEach((m, i) => {
          const t1 = state.appData.teams[m.home_team?.fifa_code] || { name: m.home_team?.fifa_code || '?' };
          const t2 = state.appData.teams[m.away_team?.fifa_code] || { name: m.away_team?.fifa_code || '?' };
          const matchName = `${t1.name} vs ${t2.name}`;
          const score = (m.smartScore || 0).toFixed(1);

          listContainer.innerHTML += `
            <div class="quiz-affinity-item">
              <span class="quiz-affinity-rank">${i + 1}</span>
              <span class="quiz-affinity-name">${matchName}</span>
              <span class="quiz-affinity-score">${score}</span>
            </div>
          `;
        });
      }
    });
  }

  nextQuestion();
}

function finishQuiz() {
  // Persist quiz choices to user preferences
  if (quizState.answers.teams.length > 0) {
    state.userPreferences.favoriteTeam = quizState.answers.teams[0];
    state.userPreferences.favoriteTeams = quizState.answers.teams;
  }

  if (quizState.answers.timeSlots.length > 0) {
    const mappedTimes = new Set();
    quizState.answers.timeSlots.forEach(t => {
      if (t === 'morning') mappedTimes.add('morning');
      if (t === 'early_afternoon' || t === 'late_afternoon') mappedTimes.add('afternoon');
      if (t === 'evening') mappedTimes.add('evening');
    });
    state.userPreferences.preferredTime = Array.from(mappedTimes);
  }

  if (quizState.answers.players.length > 0) {
    state.userPreferences.favoritePlayers = quizState.answers.players;
  }

  if (quizState.answers.clubs.length > 0) {
    state.userPreferences.favoriteClubs = quizState.answers.clubs;
  }

  state.userPreferences.agePreference = quizState.answers.agePreference;

  if (state.appData && state.appData.matches) {
    import('./scoring.js').then(module => {
      state.appData.matches.forEach(m => {
        m.smartScore = module.calculateSmartScore(m, state.appData.teams, state.userPreferences?.tacticalVector);
      });
      sortMatchesList(document.getElementById('sort-matches')?.value || 'interest-desc');
      renderMatches();
    });
  }

  closeQuiz();
}

// ==========================================
// UI NAVIGATION
// ==========================================
function updateQuizUI() {
  if (quizState.currentQuestion === TOTAL_QUESTIONS - 1) {
    stepIndicator.textContent = "Tu Perfil Mundialista";
    progressFill.style.width = "100%";
    btnNext.textContent = "Ver Partidos \u2192";
    if (btnSkip) btnSkip.style.display = 'none';
  } else {
    stepIndicator.textContent = `Pregunta ${quizState.currentQuestion + 1} de ${TOTAL_QUESTIONS - 1}`;
    progressFill.style.width = `${((quizState.currentQuestion + 1) / (TOTAL_QUESTIONS - 1)) * 100}%`;
    btnNext.textContent = quizState.currentQuestion === TOTAL_QUESTIONS - 2 ? 'Ver Resultados' : 'Siguiente \u2192';
    if (btnSkip) btnSkip.style.display = 'inline-block';
  }

  btnBack.disabled = quizState.currentQuestion === 0;
  validateCurrentQuestion();

  document.querySelectorAll('.quiz-question').forEach((q, index) => {
    q.classList.toggle('active', index === quizState.currentQuestion);
  });
}

function prevQuestion() {
  if (quizState.currentQuestion > 0) {
    quizState.currentQuestion--;
    updateQuizUI();
  }
}

function nextQuestion() {
  if (quizState.currentQuestion < TOTAL_QUESTIONS - 1) {
    quizState.currentQuestion++;
    updateQuizUI();
  }
}

function validateCurrentQuestion() {
  let isValid = false;
  switch(quizState.currentQuestion) {
    case 0: isValid = quizState.answers.teams.length > 0; break;
    case 1: isValid = quizState.answers.timeSlots.length > 0; break;
    case 2: isValid = quizState.answers.emotion !== ''; break;
    case 3: isValid = quizState.answers.clubs.length > 0; break;
    case 4: isValid = quizState.answers.players.length > 0; break;
    case 5: isValid = true; break; // slider always valid
    case 6: isValid = true; break; // slider always valid
    case 7: isValid = true; break; // slider always valid
    case 8: isValid = true; break; // results screen
  }
  btnNext.disabled = !isValid;
}

// ==========================================
// Q1: TEAMS (with flags)
// ==========================================
function initQ1() {
  const container = document.getElementById('quiz-teams-container');
  const searchInput = document.getElementById('quiz-search-teams');
  const selectedContainer = document.getElementById('quiz-selected-teams-container');

  if (!container || !state.appData || !state.appData.teams) return;

  const allTeams = Object.values(state.appData.teams)
    .filter(t => !t.is_placeholder)
    .sort((a, b) => a.name.localeCompare(b.name));

  const renderGrid = (filterText = '') => {
    container.innerHTML = '';

    let visibleTeams = allTeams.filter(t =>
      t.name.toLowerCase().includes(filterText.toLowerCase()) ||
      t.fifa_code.toLowerCase().includes(filterText.toLowerCase())
    );

    if (filterText === '') {
      const suggested = visibleTeams.filter(t => SUGGESTED_TEAMS.includes(t.fifa_code));
      const others = visibleTeams.filter(t => !SUGGESTED_TEAMS.includes(t.fifa_code));
      visibleTeams = [...suggested, ...others];
    }

    visibleTeams.forEach(t => {
      const isSelected = quizState.answers.teams.includes(t.fifa_code);
      const isoCode = getCountryIsoCode(t.fifa_code);
      const flagUrl = `https://flagcdn.com/w80/${isoCode}.png`;

      const card = document.createElement('div');
      card.className = `quiz-entity-card ${isSelected ? 'selected' : ''}`;
      card.innerHTML = `
        <img class="quiz-entity-img quiz-entity-flag" src="${flagUrl}" alt="${t.name}"
             onerror="this.style.display='none'">
        <span class="quiz-entity-label">${t.name}</span>
        ${isSelected ? '<i class="fa-solid fa-circle-check quiz-entity-check"></i>' : ''}
      `;

      card.addEventListener('click', () => {
        if (isSelected) {
          quizState.answers.teams = quizState.answers.teams.filter(c => c !== t.fifa_code);
        } else {
          quizState.answers.teams.push(t.fifa_code);
        }
        renderSelectedQ1();
        renderGrid(searchInput.value);
        validateCurrentQuestion();
      });

      container.appendChild(card);
    });
  };

  const renderSelectedQ1 = () => {
    selectedContainer.innerHTML = '';
    quizState.answers.teams.forEach(code => {
      const t = state.appData.teams[code];
      if (!t) return;
      const isoCode = getCountryIsoCode(code);
      const flagUrl = `https://flagcdn.com/w40/${isoCode}.png`;
      const chip = document.createElement('div');
      chip.className = 'quiz-chip';
      chip.innerHTML = `<img src="${flagUrl}" style="width:16px;height:12px;border-radius:2px"> ${t.name} <span class="quiz-chip__remove"><i class="fa-solid fa-xmark"></i></span>`;
      chip.addEventListener('click', () => {
        quizState.answers.teams = quizState.answers.teams.filter(c => c !== code);
        renderSelectedQ1();
        renderGrid(searchInput.value);
        validateCurrentQuestion();
      });
      selectedContainer.appendChild(chip);
    });
  };

  searchInput.addEventListener('input', (e) => renderGrid(e.target.value));
  renderGrid();
  renderSelectedQ1();
}

// ==========================================
// Q2: TIME SLOTS
// ==========================================
function initQ2() {
  const options = document.querySelectorAll('#quiz-q2 .quiz-card-option');
  options.forEach(opt => {
    opt.addEventListener('click', () => {
      const val = opt.getAttribute('data-value');
      if (quizState.answers.timeSlots.includes(val)) {
        quizState.answers.timeSlots = quizState.answers.timeSlots.filter(v => v !== val);
        opt.classList.remove('selected');
      } else {
        quizState.answers.timeSlots.push(val);
        opt.classList.add('selected');
      }
      validateCurrentQuestion();
    });
  });
}

// ==========================================
// Q3: EMOTION
// ==========================================
function initQ3() {
  const options = document.querySelectorAll('#quiz-q3 .quiz-radio-option');
  options.forEach(opt => {
    opt.addEventListener('click', () => {
      options.forEach(o => o.classList.remove('selected'));
      opt.classList.add('selected');
      quizState.answers.emotion = opt.getAttribute('data-value');
      validateCurrentQuestion();
      setTimeout(() => nextQuestion(), 300);
    });
  });
}

// ==========================================
// Q4: CLUBS (with logos from club_logos.json)
// ==========================================
function initQ4() {
  const container = document.getElementById('quiz-clubs-container');
  const searchInput = document.getElementById('quiz-search-clubs');
  const selectedContainer = document.getElementById('quiz-selected-clubs-container');

  if (!container) return;

  const getClubLogo = (clubName) => {
    if (!state.appData || !state.appData.clubLogos) return null;
    return state.appData.clubLogos[clubName] || state.appData.clubLogos[clubName.toLowerCase()] || null;
  };

  const getInitials = (name) => {
    const parts = name.split(' ').filter(p => p.length > 0);
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return name.substring(0, 2).toUpperCase();
  };

  const renderGrid = (filterText = '') => {
    container.innerHTML = '';

    let visible = allClubsList;
    if (filterText) {
      visible = allClubsList.filter(c => c.name.toLowerCase().includes(filterText.toLowerCase()));
    }

    // Show top 40 max to avoid lag
    visible.slice(0, 40).forEach(club => {
      const isSelected = quizState.answers.clubs.includes(club.name);
      const logoUrl = getClubLogo(club.name);

      const card = document.createElement('div');
      card.className = `quiz-entity-card ${isSelected ? 'selected' : ''}`;

      const imgHtml = logoUrl
        ? `<img class="quiz-entity-img quiz-entity-logo" src="${logoUrl}" referrerpolicy="no-referrer" alt="${club.name}" onerror="this.outerHTML='<div class=\\'quiz-entity-initials\\'>${getInitials(club.name)}</div>'">`
        : `<div class="quiz-entity-initials">${getInitials(club.name)}</div>`;

      card.innerHTML = `
        ${imgHtml}
        <span class="quiz-entity-label">${club.name}</span>
        ${isSelected ? '<i class="fa-solid fa-circle-check quiz-entity-check"></i>' : ''}
      `;

      card.addEventListener('click', () => {
        if (isSelected) {
          quizState.answers.clubs = quizState.answers.clubs.filter(c => c !== club.name);
        } else {
          quizState.answers.clubs.push(club.name);
        }
        renderSelectedQ4();
        renderGrid(searchInput.value);
        validateCurrentQuestion();
      });

      container.appendChild(card);
    });

    if (filterText && visible.length === 0) {
      container.innerHTML = '<div style="grid-column:1/-1; text-align:center; color:var(--text-muted); padding:1rem;">Sin resultados</div>';
    }
  };

  const renderSelectedQ4 = () => {
    selectedContainer.innerHTML = '';
    quizState.answers.clubs.forEach(clubName => {
      const chip = document.createElement('div');
      chip.className = 'quiz-chip';
      chip.innerHTML = `${clubName} <span class="quiz-chip__remove"><i class="fa-solid fa-xmark"></i></span>`;
      chip.addEventListener('click', () => {
        quizState.answers.clubs = quizState.answers.clubs.filter(c => c !== clubName);
        renderSelectedQ4();
        renderGrid(searchInput.value);
        validateCurrentQuestion();
      });
      selectedContainer.appendChild(chip);
    });
  };

  searchInput.addEventListener('input', (e) => renderGrid(e.target.value));
  renderGrid();
  renderSelectedQ4();
}

// ==========================================
// Q5: PLAYERS (with photos from players_photos.json)
// ==========================================
function initQ5() {
  const container = document.getElementById('quiz-players-container');
  const searchInput = document.getElementById('quiz-search-players');
  const selectedContainer = document.getElementById('quiz-selected-players-container');

  if (!container) return;

  const getInitials = (name) => {
    const parts = name.split(' ').filter(p => p.length > 0);
    if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    return name.substring(0, 2).toUpperCase();
  };

  const renderGrid = (filterText = '') => {
    container.innerHTML = '';

    let visible = allPlayersList;
    if (filterText) {
      const lower = filterText.toLowerCase();
      visible = allPlayersList.filter(p =>
        p.name.toLowerCase().includes(lower) ||
        p.club.toLowerCase().includes(lower) ||
        p.teamName.toLowerCase().includes(lower)
      );
    } else {
      // Show stars first, top 40
      visible = allPlayersList.slice(0, 40);
    }

    visible.slice(0, 40).forEach(player => {
      const isSelected = quizState.answers.players.includes(player.name);
      const photoUrl = getPlayerPhotoUrl(player.name);

      const card = document.createElement('div');
      card.className = `quiz-entity-card quiz-entity-card--player ${isSelected ? 'selected' : ''}`;

      const imgHtml = photoUrl
        ? `<img class="quiz-entity-img quiz-entity-photo" src="${photoUrl}" referrerpolicy="no-referrer" alt="${player.name}" onerror="this.outerHTML='<div class=\\'quiz-entity-initials\\'>${getInitials(player.name)}</div>'">`
        : `<div class="quiz-entity-initials">${getInitials(player.name)}</div>`;

      const starIcon = player.isStar ? '<i class="fa-solid fa-star" style="color:var(--accent-gold);font-size:0.6rem;"></i>' : '';

      card.innerHTML = `
        ${imgHtml}
        <span class="quiz-entity-label">${player.name} ${starIcon}</span>
        <span class="quiz-entity-sub">${player.club}</span>
        ${isSelected ? '<i class="fa-solid fa-circle-check quiz-entity-check"></i>' : ''}
      `;

      card.addEventListener('click', () => {
        if (isSelected) {
          quizState.answers.players = quizState.answers.players.filter(n => n !== player.name);
        } else {
          quizState.answers.players.push(player.name);
        }
        renderSelectedQ5();
        renderGrid(searchInput.value);
        validateCurrentQuestion();
      });

      container.appendChild(card);
    });

    if (filterText && visible.length === 0) {
      container.innerHTML = '<div style="grid-column:1/-1; text-align:center; color:var(--text-muted); padding:1rem;">Sin resultados</div>';
    }
  };

  const renderSelectedQ5 = () => {
    selectedContainer.innerHTML = '';
    quizState.answers.players.forEach(name => {
      const chip = document.createElement('div');
      chip.className = 'quiz-chip';
      chip.innerHTML = `${name} <span class="quiz-chip__remove"><i class="fa-solid fa-xmark"></i></span>`;
      chip.addEventListener('click', () => {
        quizState.answers.players = quizState.answers.players.filter(n => n !== name);
        renderSelectedQ5();
        renderGrid(searchInput.value);
        validateCurrentQuestion();
      });
      selectedContainer.appendChild(chip);
    });
  };

  searchInput.addEventListener('input', (e) => renderGrid(e.target.value));
  renderGrid();
  renderSelectedQ5();
}

// ==========================================
// Q6: POSSESSION
// ==========================================
function initQ6() {
  const slider = document.getElementById('quiz-slider-possession');
  if (slider) {
    slider.addEventListener('input', (e) => {
      quizState.answers.possession = parseInt(e.target.value);
    });
  }
}

// ==========================================
// Q7: INTENSITY
// ==========================================
function initQ7() {
  const slider = document.getElementById('quiz-slider-intensity');
  if (slider) {
    slider.addEventListener('input', (e) => {
      quizState.answers.intensity = parseInt(e.target.value);
    });
  }
}

// ==========================================
// Q8: JUVENTUD VS EXPERIENCIA
// ==========================================
function initQ8() {
  const slider = document.getElementById('quiz-slider-age');
  if (slider) {
    slider.addEventListener('input', (e) => {
      quizState.answers.agePreference = parseInt(e.target.value);
    });
  }
}
