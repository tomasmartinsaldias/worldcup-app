let currentSurveyType = 'casual';
let currentStep = 1;

window.openSurvey = function(type) {
  currentSurveyType = type;
  window.appState = 'survey';

  // Hide the selection overlay
  document.getElementById('spectator-selection').classList.remove('visible');
  
  const survey = document.getElementById('antigravity-survey');
  survey.setAttribute('data-theme', type);
  survey.classList.remove('hidden');
  survey.classList.add('visible');
  
  const tacticsSlider = document.getElementById('tactics-slider-wrapper');
  if (tacticsSlider) {
    tacticsSlider.style.display = type === 'casual' ? 'none' : 'block';
  }
  
  if (window.initDraftData) {
    window.initDraftData();
  }

  // Reset to step 1
  changeSurveyStep(1);
};

window.surveyGoBack = function() {
  if (currentStep > 1) {
    changeSurveyStep(currentStep - 1);
  } else {
    // Go back to level selection
    changeSurveyStep(0);
  }
};

window.surveyGoNext = function() {
  const totalSteps = 7;
  if (currentStep < totalSteps) {
    changeSurveyStep(currentStep + 1);
  } else {
    // Last step: finish survey
    if (typeof window.finishSurvey === 'function') {
      window.finishSurvey();
    }
  }
};

window.nextSurveyStep = function(stepIndex) {
  changeSurveyStep(stepIndex);
};

window.prevSurveyStep = function(stepIndex) {
  changeSurveyStep(stepIndex);
};

function changeSurveyStep(stepIndex) {
  if (stepIndex === 0) {
    document.getElementById('antigravity-survey').classList.remove('visible');
    document.getElementById('antigravity-survey').classList.add('hidden');
    document.getElementById('spectator-selection').classList.add('visible');
    return;
  }

  currentStep = stepIndex;

  // Actualizar texto y comportamiento del botón Siguiente
  const nextBtn = document.getElementById('survey-btn-next-global');
  if (nextBtn) {
    if (currentStep === 7) {
      nextBtn.textContent = 'CALCULAR MI DESTINO';
      nextBtn.classList.add('btn-glow-pulse');
    } else {
      nextBtn.textContent = 'CONTINUAR';
      nextBtn.classList.remove('btn-glow-pulse');
    }
  }

  document.querySelectorAll('.survey-step').forEach(step => {
    step.classList.remove('active');
  });
  
  const targetStep = document.getElementById(`survey-step-${stepIndex}`);
  if (targetStep) {
    targetStep.classList.add('active');
  }
  
  const totalSteps = 7;
  const progressPercent = (stepIndex / totalSteps) * 100;
  document.getElementById('survey-progress').style.width = `${progressPercent}%`;
  document.getElementById('survey-step-text').innerText = `PASO ${stepIndex} DE ${totalSteps}`;
}

window.selectVisualOption = function(questionId, value, element) {
  // Guardar valor
  window.surveyData = window.surveyData || {};
  window.surveyData[questionId] = value;

  // Actualizar UI
  const parent = element.closest('.visual-options-grid');
  parent.querySelectorAll('.visual-card').forEach(el => el.classList.remove('selected'));
  element.classList.add('selected');
};

window.updateSliderText = function(sliderId, value) {
  const textBox = document.getElementById(`text-${sliderId}`);
  if (!textBox) return;

  const val = parseInt(value);
  let text = '';

  if (sliderId === 'passion') {
    if (val < 20) text = "A los 5 minutos ya estoy pensando en otra cosa.";
    else if (val < 40) text = "Me da bronca un rato, pero no me quita el sueño.";
    else if (val < 60) text = "Me duele bastante, pero trato de que no me arruine el día.";
    else if (val < 80) text = "Quedo cruzado de mal humor todo el fin de semana.";
    else text = "No quiero hablar con nadie, me arruina la semana entera.";
  } else if (sliderId === 'neutral-interest') {
    if (val < 20) text = "Solo miro si juega mi equipo o si hay una final súper importante.";
    else if (val < 40) text = "Si no juegan los míos, prefiero hacer otra cosa.";
    else if (val < 60) text = "Si el partido promete ser entretenido, me quedo viéndolo.";
    else if (val < 80) text = "Cualquier partido del mundial me sirve para engancharme.";
    else text = "Veo absolutamente todo, juegue quien juegue.";
  } else if (sliderId === 'friction') {
    if (val < 20) text = "Fútbol físico, trabado, mucha intensidad y rose.";
    else if (val < 40) text = "Un juego con roce pero sin cortar demasiado el ritmo.";
    else if (val < 60) text = "Indiferente, lo físico y lo lírico importan por igual.";
    else if (val < 80) text = "Juego limpio y fluido, con ritmo y pocas faltas.";
    else text = "Fútbol lírico total, sin cortes y muy dinámico.";
  } else if (sliderId === 'goals') {
    if (val < 20) text = "Ajedrez táctico absoluto, partidos muy cerrados de pocos goles.";
    else if (val < 40) text = "Partidos disputados, donde un gol vale oro.";
    else if (val < 60) text = "Equilibrio entre solidez defensiva y ambición ofensiva.";
    else if (val < 80) text = "Juego abierto, propuestas ofensivas con llegadas.";
    else text = "Festival ofensivo constante, palo a palo sin defensas.";
  } else if (sliderId === 'tactics') {
    if (val < 20) text = "La pizarra del DT decide todo, orden estricto.";
    else if (val < 40) text = "Sistemas tácticos marcados pero con libertad individual.";
    else if (val < 60) text = "Equilibrio entre el plan del DT y la rebeldía del jugador.";
    else if (val < 80) text = "Fútbol de asociación y libertad para el talento.";
    else text = "Improvisación pura, que el talento individual resuelva solo.";
  }
  
  textBox.innerText = text;
};

window.selectedTimeRanges = {
  morning: false,
  noon: false,
  afternoon: false,
  night: false
};

window.toggleTimeRange = function(range, element) {
  window.selectedTimeRanges[range] = !window.selectedTimeRanges[range];
  if (window.selectedTimeRanges[range]) {
    element.classList.add('selected');
  } else {
    element.classList.remove('selected');
  }
};

window.finishSurvey = function() {
  window.surveyData = window.surveyData || {};
  const draftResults = window.draftState || { team: null, countries: [], players: [] };
  const data = window.draftData || { teams: [], countries: [], players: [] };

  // Resolve indices to actual names/codes using draftData
  const resolvedPlayers = (draftResults.players || []).map(idx => data.players[idx]?.NAME).filter(Boolean);
  const resolvedTeam = draftResults.team !== null && data.teams[draftResults.team] ? data.teams[draftResults.team].team : null;
  const resolvedCountries = (draftResults.countries || []).map(idx => data.countries[idx]?.country).filter(Boolean);

  const results = {
    userType: currentSurveyType,
    passion: document.getElementById('slider-passion') ? document.getElementById('slider-passion').value : null,
    neutralInterest: document.getElementById('slider-neutral-interest') ? document.getElementById('slider-neutral-interest').value : null,
    friction: document.getElementById('slider-friction') ? document.getElementById('slider-friction').value : null,
    goals: document.getElementById('slider-goals') ? document.getElementById('slider-goals').value : null,
    tactics: document.getElementById('slider-tactics') ? document.getElementById('slider-tactics').value : null,
    balance: document.getElementById('slider-balance') ? document.getElementById('slider-balance').value : null,
    q1_player_loyalty: window.surveyData['q1'] || null,
    q2_team_loyalty: window.surveyData['q2'] || null,
    favoritePlayers: resolvedPlayers,
    favoriteTeam: resolvedTeam,
    supportedNations: resolvedCountries,
    availableTimeRanges: window.selectedTimeRanges
  };

  
  window.surveyRawResults = results; // Save for recommender.js
  localStorage.setItem('savedSurveyResults', JSON.stringify(results));
  console.log("Encuesta finalizada. Datos guardados en window.surveyRawResults y localStorage:", results);
  
  document.getElementById('antigravity-survey').classList.remove('visible');
  setTimeout(() => {
    document.getElementById('antigravity-survey').classList.add('hidden');
    
    if (currentSurveyType === 'fanatico') {
      if (window.startDraft) {
        document.getElementById('draft-template').classList.remove('hidden');
        document.getElementById('draft-template').classList.add('visible');
        window.startDraft(true, '11v11');
      }
    } else if (currentSurveyType === 'intermedio') {
      if (window.startDraft) {
        document.getElementById('draft-template').classList.remove('hidden');
        document.getElementById('draft-template').classList.add('visible');
        window.startDraft(true, '7v7');
      }
    } else {
      // Para casual o por defecto
      if(typeof window.showRecommendations === 'function') {
        window.showRecommendations();
      } else if(window.returnToHomepage) {
        window.returnToHomepage();
      }
    }
  }, 500);
};
