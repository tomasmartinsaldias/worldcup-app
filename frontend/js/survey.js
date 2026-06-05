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
    if (val < 20) text = "A los 5 minutos ya estoy pensando en otra cosa.";
    else if (val < 40) text = "Me da bronca un rato, pero no me quita el sueño.";
    else if (val < 60) text = "Me duele bastante, pero trato de que no me arruine el día.";
    else if (val < 80) text = "Quedo cruzado de mal humor todo el fin de semana.";
    else text = "No quiero hablar con nadie, me arruina la semana entera.";
  }
  
  textBox.innerText = text;
};

window.finishSurvey = function() {
  window.surveyData = window.surveyData || {};
  const draftResults = window.draftState || { team: null, countries: [], players: [] };

  // Map indices back to actual names/codes to prevent TypeErrors in scoring engine
  let favClub = null;
  let favPlayers = [];
  let favNations = [];

  const nameToFifa = {
    "mexico": "MEX", "south africa": "RSA", "south korea": "KOR", "czech republic": "CZE", "canada": "CAN", 
    "bosnia and herzegovina": "BIH", "qatar": "QAT", "switzerland": "SUI", "brazil": "BRA", "morocco": "MAR", 
    "haiti": "HAI", "scotland": "SCO", "usa": "USA", "paraguay": "PAR", "australia": "AUS", "turkey": "TUR", 
    "germany": "GER", "curaçao": "CUW", "cote d'ivoire": "CIV", "côte d'ivoire": "CIV", "ecuador": "ECU", 
    "netherlands": "NED", "japan": "JPN", "sweden": "SWE", "tunisia": "TUN", "belgium": "BEL", "egypt": "EGY", 
    "ir iran": "IRN", "new zealand": "NZL", "spain": "ESP", "cabo verde": "CPV", "saudi arabia": "KSA", 
    "uruguay": "URU", "france": "FRA", "senegal": "SEN", "dr congo": "COD", "norway": "NOR", "argentina": "ARG", 
    "algeria": "ALG", "austria": "AUT", "jordan": "JOR", "portugal": "POR", "iraq": "IRQ", "uzbekistan": "UZB", 
    "colombia": "COL", "england": "ENG", "croatia": "CRO", "ghana": "GHA", "panama": "PAN"
  };

  if (window.draftData) {
    if (draftResults.team !== null && window.draftData.teams[draftResults.team]) {
      favClub = window.draftData.teams[draftResults.team].team;
    }
    if (draftResults.players && draftResults.players.length > 0) {
      favPlayers = draftResults.players.map(idx => {
        return window.draftData.players[idx] ? window.draftData.players[idx].NAME : null;
      }).filter(Boolean);
    }
    if (draftResults.countries && draftResults.countries.length > 0) {
      favNations = draftResults.countries.map(idx => {
        const countryObj = window.draftData.countries[idx];
        if (!countryObj) return null;
        const nameNorm = countryObj.country.toLowerCase().trim();
        return nameToFifa[nameNorm] || countryObj.country.toUpperCase().substring(0, 3);
      }).filter(Boolean);
    }
  }

  const results = {
    userType: currentSurveyType,
    passion: document.getElementById('slider-passion') ? document.getElementById('slider-passion').value : null,
    friction: document.getElementById('slider-friction') ? document.getElementById('slider-friction').value : null,
    goals: document.getElementById('slider-goals') ? document.getElementById('slider-goals').value : null,
    tactics: document.getElementById('slider-tactics') ? document.getElementById('slider-tactics').value : null,
    balance: document.getElementById('slider-balance') ? document.getElementById('slider-balance').value : null,
    q1_player_loyalty: window.surveyData['q1'] || null,
    q2_team_loyalty: window.surveyData['q2'] || null,
    fav_player: favPlayers,
    fav_team: favClub,
    supported_nations: favNations
  };
  
  console.log("Encuesta finalizada. Datos del recomendador Antigravity:", results);
  
  if (window.state && window.state.userPreferences) {
    const prefs = window.state.userPreferences;
    if (results.passion !== null) {
      prefs.w_afectivo = Math.round(parseInt(results.passion) / 10);
    }
    if (results.friction !== null) {
      const fricVal = parseInt(results.friction);
      prefs.w_friccion = Math.round(fricVal / 10);
      if (fricVal < 40) {
        prefs.frictionPreference = 'tenso';
      } else if (fricVal > 60) {
        prefs.frictionPreference = 'fair_play';
      } else {
        prefs.frictionPreference = 'indiferente';
      }
    }
    if (results.goals !== null) {
      prefs.w_espectaculo = Math.round(parseInt(results.goals) / 10);
    }
    if (results.tactics !== null) {
      prefs.w_tactica = Math.round(parseInt(results.tactics) / 10);
    }
    prefs.w_entretenimiento = Math.round((prefs.w_espectaculo + prefs.w_friccion) / 2);
    prefs.favoriteTeams = results.supported_nations || [];
    prefs.favoriteClubs = results.fav_team ? [results.fav_team] : [];
    prefs.favoritePlayers = results.fav_player || [];
  }

  // Aquí podemos mostrar las recomendaciones, pero por ahora mostramos un alert
  console.log("¡Encuesta Completada! Ajustes guardados en el estado.");
  
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
