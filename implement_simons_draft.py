import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add link to draft.css
if 'href="draft.css"' not in html:
    html = html.replace('<link rel="stylesheet" href="css/components.css?v=2">', '<link rel="stylesheet" href="css/components.css?v=2">\n  <link rel="stylesheet" href="draft.css">')

# Add intermedio onclick
if 'onclick="startQuiz(\'intermedio\')"' not in html:
    html = html.replace('<div class="spectator-card card-intermedio">', '<div class="spectator-card card-intermedio" onclick="startQuiz(\'intermedio\')">')

# Add draft-template HTML before the closing script tags if not exists
draft_html = """
  <!-- SIMON'S FUT DRAFT -->
  <div id="draft-template" class="ui-overlay hidden draft-flow" style="z-index: 101;">
    <div class="quiz-container draft-container" style="width: 95%; max-width: 1200px; height: 85vh; background: rgba(10, 12, 16, 0.95); border: 1px solid rgba(0, 136, 255, 0.5); border-radius: 16px; padding: 2rem; box-shadow: 0 20px 50px rgba(0,0,0,0.8), 0 0 30px rgba(0, 26, 255, 0.2) inset; display: flex; flex-direction: column; position: relative; overflow: hidden;">
      <div class="quiz-header" style="margin-bottom: 1rem; z-index: 10; display: flex; justify-content: flex-start; align-items: center; gap: 3rem;">
        <span style="font-size: 1.5rem; color: #0088ff; font-family: 'Outfit'; font-weight: bold; letter-spacing: 2px; text-shadow: 0 0 10px rgba(0, 136, 255, 0.5);">FUT DRAFT MUNDIALISTA</span>
      </div>
      <div id="pitch-container" class="pitch-container" style="flex-grow: 1; position: relative; display: flex; align-items: center; justify-content: center; border-radius: 12px; overflow: hidden;">
      </div>
      <div id="draft-modal" class="ui-overlay hidden" style="z-index: 100; position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: 16px; background: rgba(0,0,0,0.85);">
        <div class="draft-options-panel" style="background: rgba(10, 12, 16, 0.95); backdrop-filter: blur(10px); padding: 2rem; border-radius: 12px; width: 95%; max-width: 1000px; text-align: center; border: 1px solid rgba(0, 136, 255, 0.5); max-height: 90%; overflow-y: auto;">
          <h2 id="draft-modal-title" style="color: white; margin-bottom: 2rem; font-family: 'Outfit';"></h2>
          <div id="draft-options-container" class="draft-options-grid"></div>
        </div>
      </div>
      <div id="draft-summary-banner" class="draft-summary-hidden" style="position: absolute; bottom: 0; left: 0; width: 100%; background: linear-gradient(to top, rgba(0, 10, 25, 0.98) 40%, transparent); padding: 3rem 2rem 2rem; text-align: center; color: white; border-bottom-left-radius: 16px; border-bottom-right-radius: 16px; z-index: 50;">
        <h2 style="font-family: 'Outfit'; font-size: 2.5rem; margin-bottom: 1rem;">Estilo: <span id="draft-tactical-result" style="color: #0088ff; text-shadow: 0 0 15px rgba(0, 136, 255, 0.6);"></span></h2>
        <p id="draft-tactical-explanation" style="font-size: 1.1rem; max-width: 800px; margin: 0 auto 2rem; color: #ccc;"></p>
        <div style="display: flex; gap: 1rem; justify-content: center; align-items: center;">
          <button id="btn-restart-draft" class="quiz-btn-next" style="width: auto; padding: 1rem 3rem; background: linear-gradient(135deg, #0088ff 0%, #004488 100%); color: #fff; border: 1px solid #00aaff; border-radius: 8px;">Reiniciar</button>
          <button class="quiz-btn-next" onclick="returnToHomepage()" style="width: auto; padding: 1rem 3rem; background: linear-gradient(135deg, #0088ff 0%, #004488 100%); color: #fff; border: 1px solid #00aaff; border-radius: 8px;">Salir</button>
        </div>
      </div>
    </div>
  </div>
"""
if 'id="draft-template"' not in html:
    html = html.replace('<!-- LÓGICA DE UI OVERLAYS -->', draft_html + '\n  <!-- LÓGICA DE UI OVERLAYS -->')

# Add Simon's script at the end
script_html = """
  <script type="module" charset="utf-8">
    import { loadData } from './js/state.js';
    import { initDraft, startDraft } from './js/ui/draft.js';
    loadData();
    window.startDraft = startDraft;
    document.addEventListener('DOMContentLoaded', () => {
      initDraft();
    });
  </script>
</body>
"""
if 'import { loadData }' not in html:
    html = html.replace('</body>', script_html)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated index.html")
