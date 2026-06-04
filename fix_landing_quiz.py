import re

with open('frontend/js/landing-quiz.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the startQuiz block
start_quiz_pattern = re.compile(r'function startQuiz\(level\) \{.*?\n    \}', re.DOTALL)
new_start_quiz = """function startQuiz(level) {
      if(level === 'casual') {
        window.appState = 'transition';
        document.getElementById('spectator-selection').classList.remove('visible');
        setTimeout(() => {
          document.getElementById('casual-quiz').classList.add('visible');
          window.appState = 'quiz-casual';
        }, 500);
      } else if(level === 'intermedio') {
        window.appState = 'transition';
        document.getElementById('spectator-selection').classList.remove('visible');
        setTimeout(() => {
          if (typeof window.openDraftOverlay === 'function') {
            window.openDraftOverlay();
          }
          window.appState = 'draft';
        }, 500);
      } else if(level === 'fanatico') {
        window.appState = 'transition';
        document.getElementById('spectator-selection').classList.remove('visible');
        setTimeout(() => {
          document.getElementById('draft-template').classList.remove('hidden');
          document.getElementById('draft-template').classList.add('visible');
          window.appState = 'draft';
          if (window.startDraft) window.startDraft(true);
        }, 500);
      }
    }"""
content = start_quiz_pattern.sub(new_start_quiz, content)

with open('frontend/js/landing-quiz.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated landing-quiz.js")
