const fs = require('fs');

let html = fs.readFileSync('frontend/index.html', 'utf-8');

// First, we must shift the IDs and nextSurveyStep values up by 1 for all steps
for (let i = 6; i >= 1; i--) {
  html = html.replace(`id="survey-step-${i}"`, `id="survey-step-${i+1}"`);
  html = html.replace(`nextSurveyStep(${i+1})`, `nextSurveyStep(${i+2})`);
  html = html.replace(`prevSurveyStep(${i})`, `prevSurveyStep(${i+1})`);
  html = html.replace(`prevSurveyStep(${i-1})`, `prevSurveyStep(${i})`);
}

// But wait, my manual replacements might overlap and cause issues. Let's do it safer.
// Let's just use regex with functions.

let cleanHtml = fs.readFileSync('frontend/index.html', 'utf-8');

cleanHtml = cleanHtml.replace(/id="survey-step-(\d+)"/g, (match, step) => {
  return `id="survey-step-${parseInt(step) + 1}"`;
});

cleanHtml = cleanHtml.replace(/nextSurveyStep\((\d+)\)/g, (match, step) => {
  return `nextSurveyStep(${parseInt(step) + 1})`;
});

cleanHtml = cleanHtml.replace(/prevSurveyStep\((\d+)\)/g, (match, step) => {
  return `prevSurveyStep(${parseInt(step) + 1})`;
});

// Now we need to insert the missing Step 1 right before the NEW survey-step-2
const step1Html = `
      <!-- Paso 1: Disponibilidad Horaria -->
      <div class="quiz-step survey-step active" id="survey-step-1">
        <h2 class="quiz-question">DISPONIBILIDAD HORARIA</h2>
        <p class="quiz-desc">¿En qué momentos del día tienes disponibilidad para ver los partidos? Selecciona todos los que apliquen.</p>
        
        <div class="time-range-grid">
          <div class="time-range-card" onclick="toggleTimeRange('morning', this)">
            <i class="fa-solid fa-sun"></i>
            <span>Mañana</span>
            <small>08:00 - 12:00</small>
          </div>
          <div class="time-range-card" onclick="toggleTimeRange('noon', this)">
            <i class="fa-solid fa-mug-hot"></i>
            <span>Mediodía</span>
            <small>12:00 - 16:00</small>
          </div>
          <div class="time-range-card" onclick="toggleTimeRange('afternoon', this)">
            <i class="fa-solid fa-cloud-sun"></i>
            <span>Tarde</span>
            <small>16:00 - 20:00</small>
          </div>
          <div class="time-range-card" onclick="toggleTimeRange('night', this)">
            <i class="fa-solid fa-moon"></i>
            <span>Noche</span>
            <small>20:00 - 00:00</small>
          </div>
        </div>

        <div class="draft-nav" style="display: flex; justify-content: space-between; margin-top: 2rem;">
          <button class="btn-back-minimal" style="position:relative; top:0; left:0; display:inline-flex;"
            onclick="prevSurveyStep(0)">ATRÁS</button>
          <button class="quiz-btn-next" onclick="nextSurveyStep(2)">CONTINUAR</button>
        </div>
      </div>

`;

// Find the start of the old step 1 (now step 2)
// The old step 1 starts with <!-- Paso 1: Pasión vs Espectáculo -->
const insertionPoint = cleanHtml.indexOf('<!-- Paso 1: Pasión vs Espectáculo -->');
if (insertionPoint !== -1) {
  cleanHtml = cleanHtml.slice(0, insertionPoint) + step1Html + cleanHtml.slice(insertionPoint);
} else {
  // If comment is different
  const fallbackPoint = cleanHtml.indexOf('<div class="quiz-step survey-step active" id="survey-step-2">');
  cleanHtml = cleanHtml.slice(0, fallbackPoint) + step1Html + cleanHtml.slice(fallbackPoint);
}

// Ensure the new step 2 does NOT have the 'active' class
cleanHtml = cleanHtml.replace('<div class="quiz-step survey-step active" id="survey-step-2">', '<div class="quiz-step survey-step" id="survey-step-2">');

// Update total steps text from "PASO 1 DE 6" to "PASO 1 DE 7" or similar
cleanHtml = cleanHtml.replace('id="survey-step-text">PASO 1 DE 3<', 'id="survey-step-text">PASO 1 DE 7<');

// Also fix finishSurvey button to make sure it doesn't have an incremented step. Wait, finishSurvey doesn't have an argument.

fs.writeFileSync('frontend/index.html', cleanHtml);
console.log('Restored missing step 1');
