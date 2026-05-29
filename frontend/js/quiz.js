import { state } from './state.js';
import { filterMatches, sortMatchesList, renderMatches } from './ui/matches.js';

// ---- Data para el Quiz (Clubs y Jugadores hardcodeados como indica el prompt) ----
const TOP_CLUBS = [
  "Real Madrid", "Barcelona", "Atletico Madrid", "Manchester City", "Arsenal", 
  "Liverpool", "Manchester United", "Chelsea", "Tottenham", "Bayern Munich", 
  "Borussia Dortmund", "Bayer Leverkusen", "PSG", "Juventus", "Inter Milan", 
  "AC Milan", "Napoli", "Roma", "River Plate", "Boca Juniors", "Flamengo", 
  "Palmeiras", "Inter Miami", "LA Galaxy", "Al Nassr", "Al Hilal"
].sort();

const TOP_PLAYERS = [
  "Lionel Messi", "Kylian Mbappé", "Erling Haaland", "Vinicius Jr", "Jude Bellingham",
  "Rodri", "Kevin De Bruyne", "Lautaro Martinez", "Robert Lewandowski", "Mohamed Salah",
  "Neymar Jr", "Pedri", "Gavi", "Lamine Yamal", "Phil Foden", "Bukayo Saka",
  "Harry Kane", "Antoine Griezmann", "Emiliano Martinez", "Alisson", "Ederson",
  "Virgil van Dijk", "Ruben Dias", "Antonio Rudiger", "Federico Valverde", "Jamal Musiala"
].sort();

const SUGGESTED_TEAMS = ['ARG', 'BRA', 'ESP', 'FRA', 'GER'];

// ---- Estado del Quiz ----
let quizState = {
  currentQuestion: 0,
  answers: {
    teams: [],
    timeSlots: [],
    viewingHabit: '',
    clubs: [],
    players: [],
    matchTraits: []
  }
};

const TOTAL_QUESTIONS = 6;

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
    if (quizState.currentQuestion === TOTAL_QUESTIONS - 1) {
      finishQuiz();
    } else {
      nextQuestion();
    }
  });
  btnSkip.addEventListener('click', () => {
    if (quizState.currentQuestion === TOTAL_QUESTIONS - 1) {
      finishQuiz();
    } else {
      nextQuestion();
    }
  });
  btnClose.addEventListener('click', closeQuiz);

  // Init Question logic
  initQ2(); // Horarios
  initQ3(); // Frecuencia
  initQ4(); // Clubes
  initQ5(); // Jugadores
  initQ6(); // Características
}

function openQuiz() {
  quizState.currentQuestion = 0;
  // Reset answers if needed, for now we keep them or start fresh
  quizState.answers = { teams: [], timeSlots: [], viewingHabit: '', clubs: [], players: [], matchTraits: [] };
  
  // Q1 needs state.appData so we init it here when opening
  initQ1();
  
  updateQuizUI();
  overlay.classList.add('active');
}

function closeQuiz() {
  overlay.classList.remove('active');
}

function finishQuiz() {
  // Map quiz answers to recommender preferences
  
  // 1. Favorite team (take the first one if multiple)
  if (quizState.answers.teams.length > 0) {
    state.userPreferences.favoriteTeam = quizState.answers.teams[0];
    const select = document.getElementById('pref-team');
    if (select) select.value = state.userPreferences.favoriteTeam;
  }

  // 2. Time slots
  if (quizState.answers.timeSlots.length > 0) {
    // Map quiz time slots to the existing select options
    // The existing options are 'morning', 'afternoon', 'evening'
    // Quiz has 'morning', 'early_afternoon', 'late_afternoon', 'evening'
    const mappedTimes = new Set();
    quizState.answers.timeSlots.forEach(t => {
      if (t === 'morning') mappedTimes.add('morning');
      if (t === 'early_afternoon' || t === 'late_afternoon') mappedTimes.add('afternoon');
      if (t === 'evening') mappedTimes.add('evening');
    });
    state.userPreferences.preferredTime = Array.from(mappedTimes);
    
    const timeSelect = document.getElementById('pref-time');
    if (timeSelect) {
      Array.from(timeSelect.options).forEach(opt => {
        opt.selected = state.userPreferences.preferredTime.includes(opt.value);
      });
    }
  }

  // 3. Match traits -> Match Style
  if (quizState.answers.matchTraits.length > 0) {
    let style = 'all';
    const traits = quizState.answers.matchTraits;
    // Simple heuristic
    if (traits.includes('tactico') || traits.includes('faltas') || traits.includes('parejos') || traits.includes('posesion')) {
      style = 'closed';
    }
    if (traits.includes('goleada') || traits.includes('goles') || traits.includes('accion')) {
      style = 'chaotic';
    }
    state.userPreferences.matchStyle = style;
    const styleSelect = document.getElementById('pref-style');
    if (styleSelect) styleSelect.value = style;
  }

  // 4. Players
  if (quizState.answers.players.length > 0) {
    state.userPreferences.favoritePlayers = quizState.answers.players;
    const playersInput = document.getElementById('pref-players');
    if (playersInput) playersInput.value = quizState.answers.players.join(', ');
  }

  // Recalculate
  if (state.appData && state.appData.matches) {
    import('./scoring.js').then(module => {
      state.appData.matches.forEach(m => {
        m.smartScore = module.calculateSmartScore(m, state.appData.teams);
      });
      sortMatchesList(document.getElementById('sort-matches')?.value || 'interest-desc');
      renderMatches();
    });
  }

  closeQuiz();
}

function updateQuizUI() {
  // Update step
  stepIndicator.textContent = `Pregunta ${quizState.currentQuestion + 1} de ${TOTAL_QUESTIONS}`;
  progressFill.style.width = `${((quizState.currentQuestion + 1) / TOTAL_QUESTIONS) * 100}%`;

  // Update back button
  btnBack.disabled = quizState.currentQuestion === 0;

  // Update next button
  btnNext.textContent = quizState.currentQuestion === TOTAL_QUESTIONS - 1 ? 'Finalizar' : 'Siguiente \u2192';
  
  validateCurrentQuestion();

  // Show correct question panel
  document.querySelectorAll('.quiz-question').forEach((q, index) => {
    if (index === quizState.currentQuestion) {
      q.classList.add('active');
    } else {
      q.classList.remove('active');
    }
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
    case 2: isValid = quizState.answers.viewingHabit !== ''; break;
    case 3: isValid = quizState.answers.clubs.length > 0; break;
    case 4: isValid = quizState.answers.players.length > 0; break;
    case 5: isValid = quizState.answers.matchTraits.length > 0; break;
  }
  btnNext.disabled = !isValid;
}

// ==========================================
// Q1: TEAMS
// ==========================================
function initQ1() {
  const container = document.getElementById('quiz-teams-container');
  const searchInput = document.getElementById('quiz-search-teams');
  const selectedContainer = document.getElementById('quiz-selected-teams-container');
  
  if (!container || !state.appData || !state.appData.teams) return;
  
  container.innerHTML = '';
  
  const allTeams = Object.values(state.appData.teams)
    .filter(t => !t.is_placeholder)
    .sort((a, b) => a.name.localeCompare(b.name));

  const renderTags = (filterText = '') => {
    container.innerHTML = '';
    
    // Sort logic: Suggested first, then alphabetical. If filtering, just alphabetical match
    let visibleTeams = allTeams.filter(t => t.name.toLowerCase().includes(filterText.toLowerCase()));
    
    if (filterText === '') {
      const suggested = visibleTeams.filter(t => SUGGESTED_TEAMS.includes(t.fifa_code));
      const others = visibleTeams.filter(t => !SUGGESTED_TEAMS.includes(t.fifa_code));
      visibleTeams = [...suggested, ...others];
    }

    visibleTeams.forEach(t => {
      const isSelected = quizState.answers.teams.includes(t.fifa_code);
      const isSuggested = SUGGESTED_TEAMS.includes(t.fifa_code);
      
      const tag = document.createElement('div');
      tag.className = `quiz-tag ${isSelected ? 'selected' : ''} ${isSuggested ? 'suggested' : ''}`;
      // Basic flag emoji logic using country code if available, else standard fallback
      let flag = "🎯";
      if (t.flag_url) {
        // use an image or just icon
        tag.innerHTML = `<img src="${t.flag_url}" style="width:16px;height:12px;border-radius:2px"> ${t.name}`;
      } else {
        tag.textContent = t.name;
      }

      tag.addEventListener('click', () => {
        if (isSelected) {
          quizState.answers.teams = quizState.answers.teams.filter(code => code !== t.fifa_code);
        } else {
          quizState.answers.teams.push(t.fifa_code);
        }
        renderSelectedQ1();
        renderTags(searchInput.value);
        validateCurrentQuestion();
      });

      container.appendChild(tag);
    });
  };

  const renderSelectedQ1 = () => {
    selectedContainer.innerHTML = '';
    quizState.answers.teams.forEach(code => {
      const t = state.appData.teams[code];
      if(!t) return;
      const chip = document.createElement('div');
      chip.className = 'quiz-chip';
      chip.innerHTML = `${t.name} <span class="quiz-chip__remove"><i class="fa-solid fa-xmark"></i></span>`;
      chip.addEventListener('click', () => {
        quizState.answers.teams = quizState.answers.teams.filter(c => c !== code);
        renderSelectedQ1();
        renderTags(searchInput.value);
        validateCurrentQuestion();
      });
      selectedContainer.appendChild(chip);
    });
  };

  searchInput.addEventListener('input', (e) => renderTags(e.target.value));
  
  renderTags();
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
// Q3: VIEWING HABIT
// ==========================================
function initQ3() {
  const options = document.querySelectorAll('#quiz-q3 .quiz-radio-option');
  options.forEach(opt => {
    opt.addEventListener('click', () => {
      options.forEach(o => o.classList.remove('selected'));
      opt.classList.add('selected');
      quizState.answers.viewingHabit = opt.getAttribute('data-value');
      validateCurrentQuestion();
      // Auto advance
      setTimeout(() => nextQuestion(), 300);
    });
  });
}

// ==========================================
// Q4: CLUBS
// ==========================================
function initQ4() {
  initSearchableList(
    TOP_CLUBS, 
    'quiz-search-clubs', 
    'quiz-clubs-container', 
    'quiz-selected-clubs-container', 
    'clubs'
  );
}

// ==========================================
// Q5: PLAYERS
// ==========================================
function initQ5() {
  initSearchableList(
    TOP_PLAYERS, 
    'quiz-search-players', 
    'quiz-players-container', 
    'quiz-selected-players-container', 
    'players'
  );
}

// ==========================================
// Q6: MATCH TRAITS
// ==========================================
function initQ6() {
  const tags = document.querySelectorAll('#quiz-traits-container .quiz-tag');
  const counterSpan = document.querySelector('#quiz-trait-counter span');
  const MAX_TRAITS = 3;

  tags.forEach(tag => {
    tag.addEventListener('click', () => {
      const val = tag.getAttribute('data-value');
      const isSelected = quizState.answers.matchTraits.includes(val);

      if (isSelected) {
        quizState.answers.matchTraits = quizState.answers.matchTraits.filter(v => v !== val);
        tag.classList.remove('selected');
      } else {
        if (quizState.answers.matchTraits.length < MAX_TRAITS) {
          quizState.answers.matchTraits.push(val);
          tag.classList.add('selected');
        }
      }

      // Update counter UI
      const count = quizState.answers.matchTraits.length;
      counterSpan.textContent = `seleccionaste ${count}`;
      
      // Disable others if max reached
      if (count >= MAX_TRAITS) {
        tags.forEach(t => {
          if (!t.classList.contains('selected')) t.classList.add('disabled');
        });
      } else {
        tags.forEach(t => t.classList.remove('disabled'));
      }

      validateCurrentQuestion();
    });
  });
}

// ==========================================
// HELPER: Searchable List
// ==========================================
function initSearchableList(items, searchId, containerId, selectedContainerId, stateKey) {
  const container = document.getElementById(containerId);
  const searchInput = document.getElementById(searchId);
  const selectedContainer = document.getElementById(selectedContainerId);

  const renderTags = (filterText = '') => {
    container.innerHTML = '';
    const visibleItems = items.filter(i => i.toLowerCase().includes(filterText.toLowerCase()));
    
    visibleItems.forEach(item => {
      const isSelected = quizState.answers[stateKey].includes(item);
      const tag = document.createElement('div');
      tag.className = `quiz-tag ${isSelected ? 'selected' : ''}`;
      tag.textContent = item;

      tag.addEventListener('click', () => {
        if (isSelected) {
          quizState.answers[stateKey] = quizState.answers[stateKey].filter(v => v !== item);
        } else {
          quizState.answers[stateKey].push(item);
        }
        renderSelected();
        renderTags(searchInput.value);
        validateCurrentQuestion();
      });

      container.appendChild(tag);
    });
  };

  const renderSelected = () => {
    selectedContainer.innerHTML = '';
    quizState.answers[stateKey].forEach(item => {
      const chip = document.createElement('div');
      chip.className = 'quiz-chip';
      chip.innerHTML = `${item} <span class="quiz-chip__remove"><i class="fa-solid fa-xmark"></i></span>`;
      chip.addEventListener('click', () => {
        quizState.answers[stateKey] = quizState.answers[stateKey].filter(v => v !== item);
        renderSelected();
        renderTags(searchInput.value);
        validateCurrentQuestion();
      });
      selectedContainer.appendChild(chip);
    });
  };

  searchInput.addEventListener('input', (e) => renderTags(e.target.value));
  renderTags();
  renderSelected();
}
