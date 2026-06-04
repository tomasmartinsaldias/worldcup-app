import io
import re

with io.open('frontend/js/ui/draft.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add currentArchetype definition
if 'let currentArchetype = null;' not in text:
    text = text.replace("let currentFormation = '4-3-3';", "let currentFormation = '4-3-3';\nlet currentArchetype = null;")

# 2. Replace FORMATIONS_HTML with STYLES_HTML
formations_html_old = text[text.find('const FORMATIONS_HTML = `'):text.find('`;', text.find('const FORMATIONS_HTML = `')) + 2]

styles_html_new = """const FORMATIONS_HTML = `
  <div class="draft-controls" style="text-align: center;">
    <h3 style="color: var(--text-primary); margin-bottom: 2rem; font-size: 2.5rem; text-shadow: 0 4px 15px rgba(0,0,0,0.8); font-weight: 900;">Seleccioná tu Estilo de Juego</h3>
    <div class="formation-cards-container" id="formation-cards-container">
      <div class="formation-card active" data-formation="4-3-3" data-archetype="tiki_taka">
        <h4>Tiki-Taka <br><small style="color: var(--accent-gold); font-size: 1.2rem;">(4-3-3)</small></h4>
        <div class="formation-pros-cons">
          <div class="formation-pro"><i class="fas fa-plus"></i> Juego de Posición</div>
          <div class="formation-pro"><i class="fas fa-plus"></i> Monopolio del balón</div>
        </div>
      </div>
      <div class="formation-card" data-formation="3-5-2" data-archetype="catenaccio">
        <h4>Catenaccio <br><small style="color: var(--accent-gold); font-size: 1.2rem;">(3-5-2)</small></h4>
        <div class="formation-pros-cons">
          <div class="formation-pro"><i class="fas fa-plus"></i> Muro Defensivo</div>
          <div class="formation-pro"><i class="fas fa-plus"></i> Contragolpe Letal</div>
        </div>
      </div>
      <div class="formation-card" data-formation="4-2-3-1" data-archetype="gegenpressing">
        <h4>Gegenpressing <br><small style="color: var(--accent-gold); font-size: 1.2rem;">(4-2-3-1)</small></h4>
        <div class="formation-pros-cons">
          <div class="formation-pro"><i class="fas fa-plus"></i> Presión Asfixiante</div>
          <div class="formation-pro"><i class="fas fa-plus"></i> Transición Rápida</div>
        </div>
      </div>
      <div class="formation-card" data-formation="4-4-2" data-archetype="asociativo">
        <h4>Fútbol Sudamericano <br><small style="color: var(--accent-gold); font-size: 1.2rem;">(4-4-2)</small></h4>
        <div class="formation-pros-cons">
          <div class="formation-pro"><i class="fas fa-plus"></i> Sociedad Central</div>
          <div class="formation-pro"><i class="fas fa-plus"></i> Toque en Corto</div>
        </div>
      </div>
    </div>
  </div>
`;"""

text = text.replace(formations_html_old, styles_html_new)

# 3. Update the click listener logic for formation cards
click_listener_old = """          document.querySelectorAll('.formation-card').forEach(card => {
            card.addEventListener('click', (e) => {
              document.querySelectorAll('.formation-card').forEach(c => c.classList.remove('active'));
              card.classList.add('active');
              currentFormation = card.dataset.formation;
            });
          });"""

click_listener_new = """          document.querySelectorAll('.formation-card').forEach(card => {
            card.addEventListener('click', (e) => {
              document.querySelectorAll('.formation-card').forEach(c => c.classList.remove('active'));
              card.classList.add('active');
              currentFormation = card.dataset.formation;
              currentArchetype = card.dataset.archetype;
            });
          });"""
text = text.replace(click_listener_old, click_listener_new)

# Make sure to set currentArchetype initially
init_btn_old = """      btnApply.onclick = () => {
        overlay.style.animation = 'relaxedFadeOut 0.5s cubic-bezier(0.22, 1, 0.36, 1) forwards';"""
init_btn_new = """      btnApply.onclick = () => {
        const activeCard = document.querySelector('.formation-card.active');
        if (activeCard) {
            currentFormation = activeCard.dataset.formation;
            currentArchetype = activeCard.dataset.archetype;
        }
        overlay.style.animation = 'relaxedFadeOut 0.5s cubic-bezier(0.22, 1, 0.36, 1) forwards';"""
text = text.replace(init_btn_old, init_btn_new)


# 4. Remove calculation from completeDraft
calc_old = """  // Calculate Tactical Vector based on the 11 drafted players
  // Indices from FC26 normalized numeric_cols: 3=pace, 4=passing, 7=defending, 8=physic
  let avgPace = 0, avgPassing = 0, avgDefending = 0;

  const players = Object.values(draftedPlayers);
  players.forEach(p => {
    if (p.position_vector && p.position_vector.length >= 8) {
      avgPace += p.position_vector[3];
      avgPassing += p.position_vector[4];
      avgDefending += p.position_vector[7];
    }
  });

  avgPace /= players.length;
  avgPassing /= players.length;
  avgDefending /= players.length;

  // Map standardized feature values (mean 0, std 1) to approximately [-1, 1] range.
  let ritmo = avgPace / 3;
  let posesion = avgPassing / 3;
  let defensa = avgDefending / 3;

  // Ancho is heavily dictated by formation choice
  let ancho = 0;
  if (currentFormation === '4-3-3') ancho = 0.8;
  else if (currentFormation === '4-4-2') ancho = 0.4;
  else if (currentFormation === '3-5-2') ancho = 0.2;
  else if (currentFormation === '4-2-3-1') ancho = -0.2;

  ritmo = Math.max(-1, Math.min(1, ritmo));
  posesion = Math.max(-1, Math.min(1, posesion));
  defensa = Math.max(-1, Math.min(1, defensa));

  const draftedVector = { defensa, posesion, ritmo, ancho };

  // Find closest archetype
  const archetypes = state.appData.arquetipos;
  let bestArch = null;
  let bestSim = -2;

  if (archetypes) {
    archetypes.forEach(arch => {
      const sim = calculateCosineSimilarity(draftedVector, arch.vector);
      if (sim > bestSim) {
        bestSim = sim;
        bestArch = arch;
      }
    });
  }"""

calc_new = """  const archetypes = state.appData.arquetipos;
  let bestArch = null;

  if (archetypes && currentArchetype) {
    bestArch = archetypes.find(a => a.id === currentArchetype);
  }
  if (!bestArch && archetypes && archetypes.length > 0) {
    bestArch = archetypes[0];
  }"""

text = text.replace(calc_old, calc_new)

# Also update the display text because we removed draftedVector
display_old = """    if (explanationText) {
      const ritmoDesc = draftedVector.ritmo > 0.1 ? 'alto ritmo y transiciones rápidas' : (draftedVector.ritmo < -0.1 ? 'juego pausado y de control' : 'ritmo equilibrado');
      const defDesc = draftedVector.defensa > 0.1 ? 'presión alta' : (draftedVector.defensa < -0.1 ? 'bloque bajo y repliegue' : 'presión media');
      
      explanationText.innerHTML = `
        <strong style="color: var(--accent-gold); font-size: 1.1rem;">Tu equipo tiene alma de ${bestArch.title}.</strong><br><br>
        Basado en los perfiles elegidos, tu equipo naturalmente tenderá a jugar con <strong>${ritmoDesc}</strong>, apostando por <strong>${defDesc}</strong>.<br><br>
        Este estilo de juego será clave para las recomendaciones en el Modo Recomendar Partidos.
      `;
    }"""

display_new = """    if (explanationText) {
      explanationText.innerHTML = `
        <strong style="color: var(--accent-gold); font-size: 1.1rem;">Tu equipo tiene alma de ${bestArch.title}.</strong><br><br>
        Has elegido un estilo táctico que define la identidad de tu equipo en la cancha.<br><br>
        Este estilo de juego será clave para las recomendaciones en el Modo Recomendar Partidos.
      `;
    }"""
text = text.replace(display_old, display_new)

# And remove the % match text since it's exactly the selected archetype
result_old = "resultBadge.textContent = `${bestArch.title} (${Math.round(bestSim * 100)}% match) pueda`"
# Actually the code was:
result_old2 = "resultBadge.textContent = `${bestArch.title} (${Math.round(bestSim * 100)}% match)`;"
result_new2 = "resultBadge.textContent = `${bestArch.title}`;"
text = text.replace(result_old2, result_new2)


with io.open('frontend/js/ui/draft.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Done")
