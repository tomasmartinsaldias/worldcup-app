const fs = require('fs');
const path = require('path');

const indexPath = path.join(__dirname, 'index.html');
let html = fs.readFileSync(indexPath, 'utf-8');

html = html.replace(/<button class="quiz-btn-next" onclick="nextSurveyStep\((\d+)\)">(.*?)<\/button>/g, (match, nextStepStr, text) => {
  const nextStep = parseInt(nextStepStr, 10);
  const currentStep = nextStep - 1;
  
  // For step 1, we might not want a back button, or maybe a back button to close the quiz?
  // Let's only add back button for step >= 2
  if (currentStep >= 2) {
    const prevStep = currentStep - 1;
    return `<div class="quiz-nav-buttons">
          <button class="quiz-btn-prev" onclick="prevSurveyStep(${prevStep})"><i class="fa-solid fa-arrow-left"></i></button>
          <button class="quiz-btn-next" onclick="nextSurveyStep(${nextStep})">${text}</button>
        </div>`;
  } else {
    // Just wrap step 1 for consistency in styling
    return `<div class="quiz-nav-buttons">
          <button class="quiz-btn-next" onclick="nextSurveyStep(${nextStep})">${text}</button>
        </div>`;
  }
});

// Also handle the final step which might call finishSurvey()
html = html.replace(/<button class="quiz-btn-next" onclick="finishSurvey\(\)">(.*?)<\/button>/g, (match, text) => {
  // Hardcode prev step as 6, since 7 is the last step
  return `<div class="quiz-nav-buttons">
          <button class="quiz-btn-prev" onclick="prevSurveyStep(6)"><i class="fa-solid fa-arrow-left"></i></button>
          <button class="quiz-btn-next" onclick="finishSurvey()">${text}</button>
        </div>`;
});

fs.writeFileSync(indexPath, html, 'utf-8');
console.log('Done replacing buttons');
