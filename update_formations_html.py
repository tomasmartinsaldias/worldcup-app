import re

html_content = '''const FORMATIONS_HTML = `
  <style>
    .formation-card-title { color: #e74c3c; font-size: 1.3rem; font-weight: 900; text-transform: uppercase; margin-bottom: 0.1rem; font-family: 'Outfit', sans-serif; letter-spacing: 0px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .formation-card-subtitle { color: #ccc; font-size: 0.8rem; margin-bottom: 0.4rem; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .mini-pitch { width: 100%; height: 95px; border: 2px solid #e74c3c; border-radius: 8px; background: #1a3320; position: relative; overflow: hidden; flex-shrink: 0; margin: 0 auto 0.4rem auto; max-width: 220px; }
    .mini-pitch-line { position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: rgba(255,255,255,0.3); }
    .mini-pitch-circle { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); width: 25px; height: 25px; border: 1px solid rgba(255,255,255,0.3); border-radius: 50%; }
    .mini-pitch-arrow { position: absolute; left: 30%; top: 50%; transform: translateY(-50%); width: 40%; height: 3px; background: #2ecc71; z-index: 2; }
    .mini-pitch-arrow::after { content: ''; position: absolute; right: -6px; top: -3px; border-left: 6px solid #2ecc71; border-top: 4px solid transparent; border-bottom: 4px solid transparent; }
    .mini-dot { position: absolute; width: 8px; height: 8px; border-radius: 50%; background: #e74c3c; transform: translate(-50%, -50%); z-index: 3; box-shadow: 0 0 4px rgba(0,0,0,0.5); }
    .mini-dot.gk { background: #3498db; }
    .style-description { font-size: 0.75rem; color: #fff; margin-bottom: 0.4rem; line-height: 1.3; font-family: var(--font-secondary); }
    .metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.3rem; width: 100%; padding: 0; box-sizing: border-box; }
    .metric-item { display: flex; flex-direction: column; gap: 0.1rem; text-align: left; background: rgba(255,255,255,0.02); padding: 0.2rem 0.3rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05); box-sizing: border-box; overflow: hidden; }
    .metric-title { font-size: 0.6rem; font-weight: bold; color: var(--text-primary); font-family: var(--font-primary); }
    .metric-bar-bg { background: rgba(255,255,255,0.08); height: 4px; border-radius: 4px; overflow: hidden; margin: 0.1rem 0; width: 100%; }
    .metric-bar-fill { background: linear-gradient(90deg, #e74c3c 0%, #ff7979 100%); height: 100%; border-radius: 4px; box-shadow: 0 0 6px rgba(231,76,60,0.45); }
    .metric-labels { display: flex; justify-content: space-between; font-size: 0.5rem; color: var(--text-muted); font-family: var(--font-secondary); }
  </style>
  <div class="draft-controls" style="text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 0.5rem 0;">
    <h3 style="color: var(--text-primary); margin-bottom: 0.5rem; font-size: 1.5rem; text-shadow: 0 4px 8px rgba(0,0,0,0.8); font-weight: 900;">Seleccioná tu Estilo de Juego</h3>
    <div class="carousel-wrapper">
      <button class="carousel-btn prev" id="carousel-prev" style="top: 45%;">&#10094;</button>
      <div class="carousel-viewport">
        <div class="formation-cards-container" id="formation-cards-container">
'''

styles = [
    {
        'id': 'tiki_taka', 'formation': '4-3-3', 'title': 'Tiki-Taka', 'subtitle': 'Juego de Posición',
        'desc': 'Monopolio del balón, pases cortos, paciencia para desorganizar, uso de toda la cancha y presión asfixiante.',
        'dots': '<div class="mini-dot gk" style="left:8%; top:50%;"></div><div class="mini-dot" style="left:20%; top:20%;"></div><div class="mini-dot" style="left:20%; top:40%;"></div><div class="mini-dot" style="left:20%; top:60%;"></div><div class="mini-dot" style="left:20%; top:80%;"></div><div class="mini-dot" style="left:40%; top:30%;"></div><div class="mini-dot" style="left:35%; top:50%;"></div><div class="mini-dot" style="left:40%; top:70%;"></div><div class="mini-dot" style="left:60%; top:25%;"></div><div class="mini-dot" style="left:65%; top:50%;"></div><div class="mini-dot" style="left:60%; top:75%;"></div>',
        'bars': [('Defensa', 95, 'Bloque Bajo', 'Presión Alta'), ('Posesión', 95, 'Contra Rápida', 'Tiki-Taka'), ('Ritmo de Juego', 15, 'Pausado', 'Frenético'), ('Amplitud', 90, 'Pasillo Central', 'Exclusivo Bandas')]
    },
    {
        'id': 'catenaccio', 'formation': '3-5-2', 'title': 'Catenaccio Moderno', 'subtitle': 'Muro y Contragolpe',
        'desc': 'Solidez defensiva, bloque bajo impenetrable y salidas verticales explosivas al espacio.',
        'dots': '<div class="mini-dot gk" style="left:8%; top:50%;"></div><div class="mini-dot" style="left:15%; top:30%;"></div><div class="mini-dot" style="left:15%; top:50%;"></div><div class="mini-dot" style="left:15%; top:70%;"></div><div class="mini-dot" style="left:30%; top:15%;"></div><div class="mini-dot" style="left:25%; top:35%;"></div><div class="mini-dot" style="left:25%; top:65%;"></div><div class="mini-dot" style="left:30%; top:85%;"></div><div class="mini-dot" style="left:35%; top:50%;"></div><div class="mini-dot" style="left:50%; top:40%;"></div><div class="mini-dot" style="left:50%; top:60%;"></div>',
        'bars': [('Defensa', 5, 'Bloque Bajo', 'Presión Alta'), ('Posesión', 10, 'Contra Rápida', 'Tiki-Taka'), ('Ritmo de Juego', 90, 'Pausado', 'Frenético'), ('Amplitud', 25, 'Pasillo Central', 'Exclusivo Bandas')]
    },
    {
        'id': 'gegenpressing', 'formation': '4-2-3-1', 'title': 'Gegenpressing', 'subtitle': 'Presión Asfixiante',
        'desc': 'Presión alta agresiva tras pérdida, robo e inmediatez ofensiva a máxima velocidad.',
        'dots': '<div class="mini-dot gk" style="left:8%; top:50%;"></div><div class="mini-dot" style="left:30%; top:20%;"></div><div class="mini-dot" style="left:25%; top:40%;"></div><div class="mini-dot" style="left:25%; top:60%;"></div><div class="mini-dot" style="left:30%; top:80%;"></div><div class="mini-dot" style="left:45%; top:35%;"></div><div class="mini-dot" style="left:45%; top:65%;"></div><div class="mini-dot" style="left:60%; top:25%;"></div><div class="mini-dot" style="left:65%; top:50%;"></div><div class="mini-dot" style="left:60%; top:75%;"></div><div class="mini-dot" style="left:80%; top:50%;"></div>',
        'bars': [('Defensa', 95, 'Bloque Bajo', 'Presión Alta'), ('Posesión', 35, 'Contra Rápida', 'Tiki-Taka'), ('Ritmo de Juego', 95, 'Pausado', 'Frenético'), ('Amplitud', 65, 'Pasillo Central', 'Exclusivo Bandas')]
    },
    {
        'id': 'asociativo', 'formation': '4-3-2-1', 'title': 'Asociativo', 'subtitle': 'Sociedad Central',
        'desc': 'Posesión y talento interior. Mediocampistas tocando en corto por el medio y marcando los tiempos.',
        'dots': '<div class="mini-dot gk" style="left:8%; top:50%;"></div><div class="mini-dot" style="left:20%; top:20%;"></div><div class="mini-dot" style="left:20%; top:40%;"></div><div class="mini-dot" style="left:20%; top:60%;"></div><div class="mini-dot" style="left:20%; top:80%;"></div><div class="mini-dot" style="left:40%; top:30%;"></div><div class="mini-dot" style="left:35%; top:50%;"></div><div class="mini-dot" style="left:40%; top:70%;"></div><div class="mini-dot" style="left:60%; top:35%;"></div><div class="mini-dot" style="left:60%; top:65%;"></div><div class="mini-dot" style="left:75%; top:50%;"></div>',
        'bars': [('Defensa', 65, 'Bloque Bajo', 'Presión Alta'), ('Posesión', 85, 'Contra Rápida', 'Tiki-Taka'), ('Ritmo de Juego', 30, 'Pausado', 'Frenético'), ('Amplitud', 5, 'Pasillo Central', 'Exclusivo Bandas')]
    },
    {
        'id': 'directo', 'formation': '4-4-2', 'title': 'Fútbol Directo', 'subtitle': 'La Vía Directa',
        'desc': 'Juego directo. Pelotazos largos, disputa de segundas jugadas y ataque puro por las bandas para centros.',
        'dots': '<div class="mini-dot gk" style="left:8%; top:50%;"></div><div class="mini-dot" style="left:20%; top:20%;"></div><div class="mini-dot" style="left:20%; top:40%;"></div><div class="mini-dot" style="left:20%; top:60%;"></div><div class="mini-dot" style="left:20%; top:80%;"></div><div class="mini-dot" style="left:45%; top:20%;"></div><div class="mini-dot" style="left:45%; top:40%;"></div><div class="mini-dot" style="left:45%; top:60%;"></div><div class="mini-dot" style="left:45%; top:80%;"></div><div class="mini-dot" style="left:65%; top:35%;"></div><div class="mini-dot" style="left:65%; top:65%;"></div>',
        'bars': [('Defensa', 30, 'Bloque Bajo', 'Presión Alta'), ('Posesión', 5, 'Contra Rápida', 'Tiki-Taka'), ('Ritmo de Juego', 75, 'Pausado', 'Frenético'), ('Amplitud', 95, 'Pasillo Central', 'Exclusivo Bandas')]
    }
]

for s in styles:
    active = ' active' if s['id'] == 'tiki_taka' else ''
    html_content += f'''
        <!-- {s['id'].upper()} -->
        <div class="formation-card{active}" data-formation="{s['formation']}" data-archetype="{s['id']}">
          <h4 class="formation-card-title">{s['title']}</h4>
          <p class="formation-card-subtitle">{s['subtitle']}</p>
          <div class="mini-pitch">
            <div class="mini-pitch-line"></div><div class="mini-pitch-circle"></div><div class="mini-pitch-arrow"></div>
            {s['dots']}
          </div>
          <p class="style-description">{s['desc']}</p>
          <div style="height: 1px; background: rgba(255,255,255,0.1); margin-bottom: 0.3rem; width: 100%;"></div>
          <div class="metrics-grid">
'''
    for b in s['bars']:
        html_content += f'''
            <div class="metric-item">
              <div class="metric-title">{b[0]}</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: {b[1]}%;"></div>
              </div>
              <div class="metric-labels"><span>{b[2]}</span><span>{b[3]}</span></div>
            </div>
'''
    html_content += f'''
          </div>
        </div>
'''

html_content += '''
        </div>
      </div>
      <button class="carousel-btn next" id="carousel-next" style="top: 45%;">&#10095;</button>
      <div class="carousel-dots" id="carousel-dots">
        <div class="carousel-dot active" data-index="0"></div>
        <div class="carousel-dot" data-index="1"></div>
        <div class="carousel-dot" data-index="2"></div>
        <div class="carousel-dot" data-index="3"></div>
        <div class="carousel-dot" data-index="4"></div>
      </div>
    </div>
  </div>
`;
'''

with open('c:/Users/user/Downloads/app_mundial/worldcup-app/frontend/js/ui/draft.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'const FORMATIONS_HTML = `.*?`;', html_content.strip(), content, flags=re.DOTALL)

with open('c:/Users/user/Downloads/app_mundial/worldcup-app/frontend/js/ui/draft.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated draft.js successfully!")
