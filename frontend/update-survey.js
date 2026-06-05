const fs = require('fs');
let html = fs.readFileSync('frontend/index.html', 'utf-8');

// Replace survey-step-6 -> 7
html = html.replace(/survey-step-6/g, 'survey-step-7');
html = html.replace(/nextSurveyStep\(6\)/g, 'nextSurveyStep(7)');
html = html.replace(/prevSurveyStep\(5\)/g, 'prevSurveyStep(6)');

// Replace survey-step-5 -> 6
html = html.replace(/survey-step-5/g, 'survey-step-6');
html = html.replace(/nextSurveyStep\(5\)/g, 'nextSurveyStep(6)');
html = html.replace(/prevSurveyStep\(4\)/g, 'prevSurveyStep(5)');

// Replace survey-step-4 -> 5
html = html.replace(/survey-step-4/g, 'survey-step-5');
html = html.replace(/nextSurveyStep\(4\)/g, 'nextSurveyStep(5)');
html = html.replace(/prevSurveyStep\(3\)/g, 'prevSurveyStep(4)');

// Replace survey-step-3 -> 4
html = html.replace(/survey-step-3/g, 'survey-step-4');
html = html.replace(/nextSurveyStep\(3\)/g, 'nextSurveyStep(4)');
html = html.replace(/prevSurveyStep\(2\)/g, 'prevSurveyStep(3)');

// Replace survey-step-2 -> 3
html = html.replace(/survey-step-2/g, 'survey-step-3');
html = html.replace(/nextSurveyStep\(2\)/g, 'nextSurveyStep(3)');
html = html.replace(/prevSurveyStep\(1\)/g, 'prevSurveyStep(2)');

// Replace survey-step-1 -> 2
html = html.replace(/survey-step-1/g, 'survey-step-2');

// We need to inject survey-step-1
const newStep = `
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

        <button class="quiz-btn-next" onclick="nextSurveyStep(2)">CONTINUAR</button>
      </div>

`;

// Insert the new step
html = html.replace('<!-- Paso 1: Pasión vs Espectáculo -->', newStep + '      <!-- Paso 2: Pasión vs Espectáculo -->');

// Update survey total steps in PASO 1 DE x
html = html.replace('PASO 1 DE 3', 'PASO 1 DE 4');

fs.writeFileSync('frontend/index.html', html);
console.log('index.html modified successfully.');
