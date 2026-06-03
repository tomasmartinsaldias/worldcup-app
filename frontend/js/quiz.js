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
    clubs: [],
    players: [],
    friccion: null,
    agePreference: null
  }
};

const TOTAL_QUESTIONS = 7; // 6 questions + 1 results screen

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
  initQ5(); // Fricción (categorías → dramaBonus)
  initQ6(); // Age preference
}

function openQuiz() {
  quizState.currentQuestion = 0;
  quizState.answers = {
    teams: [], timeSlots: [],
    clubs: [], players: [],
    friccion: null, agePreference: null
  };

  // Extract entities from loaded data (once)
  if (allPlayersList.length === 0) extractAllEntities();

  // Initialize questions
  initQ1(); // Teams
  initQ3(); // Clubs
  initQ4(); // Players

  updateQuizUI();
  overlay.classList.add('active');
}

function closeQuiz() {
  overlay.classList.remove('active');
}

// ==========================================
// APLICAR PREFERENCIAS AL SISTEMA DE SCORING
// ==========================================
/**
 * Aplica las respuestas del quiz directamente a state.userPreferences.
 * Ya no se genera un quizVector separado; cada pregunta configura el parámetro
 * correspondiente del sistema de scoring existente.
 */
function applyQuizToState() {
  const ans = quizState.answers;

  // Q5: Fricción categórica → dramaBonus con signo
  if (ans.friccion !== null) {
    const dramaMap = { dislike: -1, neutral: 0, like: 1 };
    state.userPreferences.dramaBonus = dramaMap[ans.friccion] ?? 0;
  }

  // Q6: Age preference
  if (ans.agePreference !== null) {
    state.userPreferences.agePreference = ans.agePreference;
  }
}

let quizRadarChart = null;

function showResults() {
  // Aplicar preferencias al estado ANTES de mostrar resultados
  applyQuizToState();
  state.userPreferences.favoriteTeams = quizState.answers.teams;
  state.userPreferences.favoritePlayers = quizState.answers.players;
  state.userPreferences.favoriteClubs = quizState.answers.clubs;

  // Pre-calculate affinity for matches to show Top 5
  if (state.appData && state.appData.matches) {
    import('./scoring.js').then(module => {
      state.appData.matches.forEach(m => {
        m.smartScore = module.calculateSmartScore(m, state.appData.teams, state.userPreferences.tacticalVector);
      });

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
  // Aplicar preferencias al sistema de scoring
  applyQuizToState();

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

  if (state.appData && state.appData.matches) {
    import('./scoring.js').then(module => {
      state.appData.matches.forEach(m => {
        m.smartScore = module.calculateSmartScore(m, state.appData.teams, state.userPreferences.tacticalVector);
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
    case 2: isValid = quizState.answers.emotion !== null && quizState.answers.emotion !== ''; break;
    case 3: isValid = quizState.answers.clubs.length > 0; break;
    case 4: isValid = quizState.answers.players.length > 0; break;
    case 5: isValid = true; break; // friction choice is always valid
    case 6: isValid = true; break; // age preference slider is always valid
    case 7: isValid = true; break; // results screen
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
// Q3: CLUBS (with logos from club_logos.json)
// ==========================================
function initQ3() {
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
        renderSelectedQ3();
        renderGrid(searchInput.value);
        validateCurrentQuestion();
      });

      container.appendChild(card);
    });

    if (filterText && visible.length === 0) {
      container.innerHTML = '<div style="grid-column:1/-1; text-align:center; color:var(--text-muted); padding:1rem;">Sin resultados</div>';
    }
  };

  const renderSelectedQ3 = () => {
    selectedContainer.innerHTML = '';
    quizState.answers.clubs.forEach(clubName => {
      const chip = document.createElement('div');
      chip.className = 'quiz-chip';
      chip.innerHTML = `${clubName} <span class="quiz-chip__remove"><i class="fa-solid fa-xmark"></i></span>`;
      chip.addEventListener('click', () => {
        quizState.answers.clubs = quizState.answers.clubs.filter(c => c !== clubName);
        renderSelectedQ3();
        renderGrid(searchInput.value);
        validateCurrentQuestion();
      });
      selectedContainer.appendChild(chip);
    });
  };

  searchInput.addEventListener('input', (e) => renderGrid(e.target.value));
  renderGrid();
  renderSelectedQ3();
}

// ==========================================
// Q4: PLAYERS (with photos from players_photos.json)
// ==========================================
function initQ4() {
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
    quizState.answers.players.forEach(name => {
      const chip = document.createElement('div');
      chip.className = 'quiz-chip';
      chip.innerHTML = `${name} <span class="quiz-chip__remove"><i class="fa-solid fa-xmark"></i></span>`;
      chip.addEventListener('click', () => {
        quizState.answers.players = quizState.answers.players.filter(n => n !== name);
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
// Q6: FRICCIÓN (opciones categóricas → dramaBonus)
// ==========================================
function initQ6() {
  const options = document.querySelectorAll('#quiz-q6 .quiz-radio-option');
  options.forEach(opt => {
    opt.addEventListener('click', () => {
      options.forEach(o => o.classList.remove('selected'));
      opt.classList.add('selected');
      quizState.answers.friccion = opt.getAttribute('data-value');
      validateCurrentQuestion();
    });
  });
}

// ==========================================
// Q7: JUVENTUD VS EXPERIENCIA
// ==========================================
function initQ7() {
  const slider = document.getElementById('quiz-slider-age');
  if (slider) {
    slider.addEventListener('input', (e) => {
      quizState.answers.agePreference = parseInt(e.target.value);
      validateCurrentQuestion();
    });
  }
}
