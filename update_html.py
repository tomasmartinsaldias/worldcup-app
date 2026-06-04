
with open('frontend/index.html', 'r') as f:
    lines = f.readlines()

out_lines = []
skip = False

for i, line in enumerate(lines):
    if '<div id="casual-quiz"' in line:
        skip = True
        # Insert the new generic quiz template here
        out_lines.append("""
  <!-- PLANTILLA GENÉRICA DE QUIZ (Simplificada) -->
  <div id="quiz-overlay" class="ui-overlay glass-overlay hidden">
    <div class="quiz-container">
      <div class="quiz-header">
        <div class="quiz-progress-bar"><div class="quiz-progress" id="quiz-progress"></div></div>
        <span id="quiz-step-text">PASO 1</span>
      </div>
      
      <div class="quiz-step active" id="generic-quiz-step">
        <h2 class="quiz-question" id="quiz-title">TÍTULO DE PREGUNTA</h2>
        <p class="quiz-desc" id="quiz-subtitle">Descripción genérica de la pregunta.</p>
        <div class="quiz-options" id="quiz-options-container">
          <!-- Opciones inyectadas por JS -->
        </div>
        <button class="quiz-btn-next" id="quiz-btn-next" onclick="nextGenericQuizStep()" disabled>CONTINUAR</button>
      </div>
    </div>
  </div>

  <!-- PLANTILLA ESTÁTICA DEL DRAFT -->
  <div id="draft-template" class="ui-overlay glass-overlay hidden">
    <div class="quiz-container fanatic-container">
      <div class="hero-section" style="text-align: center; margin-bottom: 2rem;">
        <h1 class="hero-title" style="font-size: 3rem; color: #ffffff; text-shadow: 0 0 20px rgba(10, 88, 255, 0.8);">FUT DRAFT (PLANTILLA)</h1>
        <p class="hero-desc" style="color: #c0c0c0; font-size: 1.2rem;">Maqueta estática sin lógica pesada.</p>
      </div>

      <!-- Grid Visual Estático -->
      <div class="draft-static-grid">
        <div class="draft-placeholder-card"></div>
        <div class="draft-placeholder-card"></div>
        <div class="draft-placeholder-card"></div>
        <div class="draft-placeholder-card"></div>
        <div class="draft-placeholder-card"></div>
        <div class="draft-placeholder-card"></div>
        <div class="draft-placeholder-card"></div>
        <div class="draft-placeholder-card"></div>
        <div class="draft-placeholder-card"></div>
        <div class="draft-placeholder-card"></div>
        <div class="draft-placeholder-card"></div>
      </div>
      
      <div style="text-align: center; margin-top: 2rem;">
        <button class="quiz-btn-next" style="padding: 1rem 3rem; font-size: 1.2rem; opacity: 1;" onclick="finishDraftTemplate()">
          Ir a Recomendador
        </button>
      </div>
    </div>
  </div>
""")
    if '<!-- Match H2H Modal -->' in line:
        skip = False

    if '<!-- LÓGICA DE UI OVERLAYS -->' in line:
        # Before adding this line, we need to ensure we didn't miss the end of h2h-modal closing divs
        # In the original file, there were 2 stray closing divs before this line:
        #     </div>
        #   </div>
        # Since we skipped the opening of fanatic-quiz and casual-quiz, those closing divs are now orphaned and must be removed!
        # They are at the end of the `out_lines` if we just appended them.
        # Let's remove them.
        while True:
            if len(out_lines) > 0 and out_lines[-1].strip() == '</div>':
                out_lines.pop()
            elif len(out_lines) > 0 and out_lines[-1].strip() == '':
                out_lines.pop()
            else:
                break

    if not skip:
        out_lines.append(line)

with open('frontend/index.html', 'w') as f:
    f.writelines(out_lines)

print("Done")
