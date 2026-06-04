let currentSurveyType = 'casual';

window.openSurvey = function(type) {
  currentSurveyType = type;
  window.appState = 'survey';

  // Hide the selection overlay
  document.getElementById('spectator-selection').classList.remove('visible');
  
  const survey = document.getElementById('antigravity-survey');
  survey.setAttribute('data-theme', type);
  survey.classList.remove('hidden');
  survey.classList.add('visible');
  
  if (window.initDraftData) {
    window.initDraftData();
  }

  // Reset to step 1
  changeSurveyStep(1);
};

window.nextSurveyStep = function(stepIndex) {
  changeSurveyStep(stepIndex);
};

window.prevSurveyStep = function(stepIndex) {
  changeSurveyStep(stepIndex);
};

function changeSurveyStep(stepIndex) {
  document.querySelectorAll('.survey-step').forEach(step => {
    step.classList.remove('active');
  });
  
  const targetStep = document.getElementById(`survey-step-${stepIndex}`);
  if (targetStep) {
    targetStep.classList.add('active');
  }
  
  const totalSteps = 6;
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
    if (val < 20) text = "Solo importa ganar. El juego bonito es secundario.";
    else if (val < 40) text = "Prefiero ganar, pero que no sea aburrido.";
    else if (val < 60) text = "Equilibrio perfecto entre pasión y buen juego.";
    else if (val < 80) text = "Quiero ver show, goles y lujos.";
    else text = "Fútbol espectáculo total, sin importar el resultado.";
  }
  
  textBox.innerText = text;
};

window.finishSurvey = function() {
  window.surveyData = window.surveyData || {};
  const draftResults = window.draftState || { team: null, countries: [], players: [] };

  const results = {
    userType: currentSurveyType,
    passion: document.getElementById('slider-passion') ? document.getElementById('slider-passion').value : null,
    friction: document.getElementById('slider-friction') ? document.getElementById('slider-friction').value : null,
    goals: document.getElementById('slider-goals') ? document.getElementById('slider-goals').value : null,
    balance: document.getElementById('slider-balance') ? document.getElementById('slider-balance').value : null,
    q1_player_loyalty: window.surveyData['q1'] || null,
    q2_team_loyalty: window.surveyData['q2'] || null,
    fav_player: draftResults.players,
    fav_team: draftResults.team,
    supported_nations: draftResults.countries
  };
  
  console.log("Encuesta finalizada. Datos del recomendador Antigravity:", results);
  
  // Aquí podemos mostrar las recomendaciones, pero por ahora mostramos un alert
  alert("¡Encuesta Completada! Revisar consola para ver el JSON generado.\nSe conectará con las recomendaciones en el siguiente paso.");
  
  // Para propósitos del demo, podemos enviarlo de vuelta al homepage
  if(window.returnToHomepage) {
    window.returnToHomepage();
  } else {
    document.getElementById('antigravity-survey').classList.remove('visible');
    setTimeout(() => {
        document.getElementById('antigravity-survey').classList.add('hidden');
    }, 500);
  }
};
