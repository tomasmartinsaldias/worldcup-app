with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Resolve Conflict 1
c1_target = """<<<<<<< HEAD
      <div class="spectator-card card-intermedio" onclick="window.location.href = 'app.html'">
=======
      <div class="spectator-card card-intermedio" onclick="startQuiz('intermedio')">
>>>>>>> 5d09402b2555daaa52c1c3c1746a92099d370859"""
c1_replacement = """      <div class="spectator-card card-intermedio" onclick="window.location.href = 'app.html'">"""

if c1_target in content:
    content = content.replace(c1_target, c1_replacement)
    print("Conflict 1 resolved")
else:
    # Alternative format (different whitespace/line endings)
    print("Conflict 1 not found by exact string, checking line splits...")

# Resolve Conflict 2
c2_target = """<<<<<<< HEAD
  <!-- PLANTILLA ESTÁTICA DEL DRAFT -->
  <div id="draft-template" class="ui-overlay glass-overlay hidden">
    <div class="quiz-container fanatic-container">
      <div class="hero-section" style="text-align: center; margin-bottom: 2rem;">
        <h2 class="hero-title" style="font-size: 3rem; color: #ffffff; text-shadow: 0 0 20px rgba(10, 88, 255, 0.8);">FUT DRAFT (PLANTILLA)</h2>
        <p class="hero-desc" style="color: #c0c0c0; font-size: 1.2rem;">Maqueta estática sin lógica pesada.</p>
      </div>
=======
  <div id="fanatic-quiz" class="ui-overlay hidden fq-flow">
    
  </div>
>>>>>>> 5d09402b2555daaa52c1c3c1746a92099d370859"""
c2_replacement = """  <div id="fanatic-quiz" class="ui-overlay hidden fq-flow">
    
  </div>"""

if c2_target in content:
    content = content.replace(c2_target, c2_replacement)
    print("Conflict 2 resolved")
else:
    print("Conflict 2 not found by exact string")

# Resolve Conflict 3 (using regex or search-and-replace)
# Let's search from "<<<<<<< HEAD" to ">>>>>>> 5d09402b2555daaa52c1c3c1746a92099d370859" in the script section
import re
pattern = re.compile(r'<<<<<<< HEAD\s+<script>.*?<\/script>\s+=======\s+<script src="js/landing-main\.js"><\/script>\s+<script src="js/landing-quiz\.js"><\/script>\s+<script src="js/particles\.js"><\/script>\s+>>>>>>> [a-f0-9]+', re.DOTALL)

if pattern.search(content):
    content = pattern.sub('<script src="js/landing-main.js"></script>\n  <script src="js/landing-quiz.js"></script>\n  <script src="js/particles.js"></script>', content)
    print("Conflict 3 resolved")
else:
    print("Conflict 3 not found by regex pattern")

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
