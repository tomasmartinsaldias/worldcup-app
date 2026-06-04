let currentSurveyType = 'casual';

window.openSurvey = function(type) {
  currentSurveyType = type;
  window.appState = 'survey';

  // Hide the selection overlay
  document.getElementById('spectator-selection').classList.remove('visible');
  
  // Show survey overlay
  const survey = document.getElementById('antigravity-survey');
  survey.classList.remove('hidden');
  survey.classList.add('visible');
  
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
  
  const progressPercent = (stepIndex / 3) * 100;
  document.getElementById('survey-progress').style.width = `${progressPercent}%`;
  document.getElementById('survey-step-text').innerText = `PASO ${stepIndex} DE 3`;
}

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
  const results = {
    userType: currentSurveyType,
    passion: document.getElementById('slider-passion').value,
    friction: document.getElementById('slider-friction').value,
    goals: document.getElementById('slider-goals').value,
    balance: document.getElementById('slider-balance').value,
    players: document.getElementById('slider-players').value,
    team: document.getElementById('slider-team').value
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
