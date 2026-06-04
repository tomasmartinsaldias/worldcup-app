
with open('frontend/index.html', 'r') as f:
    lines = f.readlines()

out_lines = []
skip = False

replacement_js = """
    // --- LÓGICA DE PLANTILLAS SIMPLIFICADAS ---

    const quizQuestions = [
      {
        title: "PREGUNTA DE EJEMPLO",
        desc: "Descripción de prueba para la plantilla.",
        options: ["Opción A", "Opción B", "Opción C", "Opción D"]
      }
      // Añade más preguntas aquí en el futuro
    ];
    let currentQuestionIndex = 0;

    function startQuiz(level) {
      appState = 'transition';
      document.getElementById('spectator-selection').classList.remove('visible');
      
      setTimeout(() => {
        if(level === 'casual') {
          appState = 'quiz-casual';
          document.getElementById('quiz-overlay').classList.remove('hidden');
          loadGenericQuestion(0);
        } else if(level === 'fanatico') {
          appState = 'quiz-fanatic';
          document.getElementById('draft-template').classList.remove('hidden');
        }
      }, 500);
    }

    function loadGenericQuestion(index) {
      if (index >= quizQuestions.length) {
        finishGenericQuiz();
        return;
      }
      
      const q = quizQuestions[index];
      document.getElementById('quiz-step-text').innerText = `PASO ${index + 1} DE ${quizQuestions.length}`;
      document.getElementById('quiz-progress').style.width = `${((index + 1) / quizQuestions.length) * 100}%`;
      
      document.getElementById('quiz-title').innerText = q.title;
      document.getElementById('quiz-subtitle').innerText = q.desc;
      
      const optionsContainer = document.getElementById('quiz-options-container');
      optionsContainer.innerHTML = '';
      
      q.options.forEach(opt => {
        const btn = document.createElement('button');
        btn.className = 'quiz-option';
        btn.innerText = opt;
        btn.onclick = () => selectGenericOption(btn);
        optionsContainer.appendChild(btn);
      });
      
      document.getElementById('quiz-btn-next').disabled = true;
    }

    function selectGenericOption(btn) {
      const parent = btn.parentElement;
      const options = parent.querySelectorAll('.quiz-option');
      options.forEach(o => o.classList.remove('selected'));
      btn.classList.add('selected');
      
      document.getElementById('quiz-btn-next').disabled = false;
    }

    function nextGenericQuizStep() {
      currentQuestionIndex++;
      loadGenericQuestion(currentQuestionIndex);
    }

    function finishGenericQuiz() {
      alert("¡Quiz completado! (Plantilla base)");
      // Redirigir o volver al inicio
      document.getElementById('quiz-overlay').classList.add('hidden');
      returnToHomepage();
    }

    function finishDraftTemplate() {
      alert("¡FUT Draft Completado! (Plantilla base)");
      document.getElementById('draft-template').classList.add('hidden');
      returnToHomepage();
    }
"""

for i, line in enumerate(lines):
    if 'function startQuiz(level)' in line:
        skip = True
        out_lines.append(replacement_js)
    if 'function finishQuiz()' in line:
        # we will skip until the closing brace of finishQuiz()
        pass

    if skip and line.strip() == '// 1. CONFIGURACIÓN BÁSICA DE THREE.JS':
        # we skipped too far? No, the closing script tag is before this
        pass

    if skip and line.strip() == '</script>':
        # the closing script tag. We stop skipping here.
        skip = False
        out_lines.append(line)
        continue

    if not skip:
        out_lines.append(line)

with open('frontend/index.html', 'w') as f:
    f.writelines(out_lines)

print("JS Update Done")
