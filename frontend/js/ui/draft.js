import { state } from '../state.js';
import { calculateCosineSimilarity } from '../scoring.js';

const CLUSTER_METADATA = {
  'Goalkeepers': {
    1: { name: 'Arquero Distribuidor / Ball-Playing', desc: 'El primer eslabón en la cadena de construcción de juego. Superioridad absoluta en técnica y frialdad táctica.' },
    2: { name: 'Arquero Físico / Shot-stopper Clásico', desc: 'Perfil reactivo tradicional. Dominan el arco por presencia física y reflejos, pero carecen de fundamentos técnicos con los pies.' },
    3: { name: 'Arquero Líbero / Sweeper Keeper', desc: 'Arqueros modernos orientados a la anticipación y el achique rápido. Ventaja masiva en movilidad y posicionamiento preventivo.' }
  },
  'Centerbacks': {
    1: { name: 'Central de Cobertura / Corrector', desc: 'Especialistas en defender a campo abierto y realizar coberturas en velocidad. Perfil atlético y de anticipación.' },
    2: { name: 'Central Físico / Stopper', desc: 'Especialistas en el duelo directo y el contacto. Dominan en potencia, fuerza y agresividad.' },
    3: { name: 'Central Creador / Líbero Técnico', desc: 'Defensores con una aportación ofensiva y de distribución inusual. Suelen ser zurdos o laterales reconvertidos.' }
  },
  'Fullbacks': {
    1: { name: 'Lateral Físico / Centralizado', desc: 'Laterales pesados, generalmente utilizados para cerrar la línea de 4 o dominar el juego aéreo. Fuerte presencia estática.' },
    2: { name: 'Lateral Invertido / Organizador', desc: 'Jugadores de banda con técnica de mediocampistas, que suelen interiorizar su posición aportando pases precisos.' },
    3: { name: 'Carrilero Largo / Profundo', desc: 'Perfiles de gran recorrido físico que actúan casi como extremos, con llegada directa al gol.' },
    4: { name: 'Lateral de Contención', desc: 'Defensores puros ubicados en la banda, fuertes en el 1v1 con velocidad y agilidad defensiva.' }
  },
  'Midfielders': {
    1: { name: 'Box-to-Box Físico', desc: 'Mediocampistas de ida y vuelta que dominan a través de la intensidad física, el recorrido y la recuperación activa.' },
    2: { name: 'Mediapunta Desequilibrante / Playmaker', desc: 'Jugadores de último tercio orientados al desborde, desequilibrio y la definición en espacios reducidos.' },
    3: { name: 'Pivote Defensivo / Ancla', desc: 'El balance táctico del equipo. Destructores de juego y dominadores del espacio central.' },
    4: { name: 'Organizador de Base / Regista', desc: 'Creadores de juego desde la primera línea, especialistas a balón parado con alta precisión técnica.' }
  },
  'Wingers': {
    1: { name: 'Extremo Rematador / Inside Forward', desc: 'Extremos con alma de centrodelantero, que pisan el área permanentemente para definir.' },
    2: { name: 'Extremo Creador / Desequilibrante', desc: 'Especialistas en el 1v1, ágiles, que buscan el desborde o el tiro con efecto.' },
    3: { name: 'Extremo de Recorrido / Carrilero Táctico', desc: 'Jugadores de banda con un despliegue defensivo masivo, útiles en esquemas de transiciones.' }
  },
  'Strikers': {
    1: { name: 'Delantero Objetivo / Target Man', desc: 'Puntos de referencia estáticos en el área, letales en el remate de primera intención y en el choque físico.' },
    2: { name: 'Delantero Presionador / Primer Defensor', desc: 'Atacantes de altísimo sacrificio táctico, diseñados para sistemas de presión alta.' },
    3: { name: 'Atacante Móvil / Segundo Delantero', desc: 'Delanteros que caen a bandas, rompen al espacio en carrera y generan sus propias oportunidades.' }
  }
};

const GROUP_QUESTIONS = {
  'Goalkeepers': '¿Qué tipo de arquero estás buscando?',
  'Centerbacks': '¿Qué perfil de defensor central necesitás?',
  'Fullbacks': '¿Cómo querés que jueguen tus laterales?',
  'Midfielders': '¿Qué función debe cumplir este mediocampista?',
  'Wingers': '¿Qué estilo de extremo preferís para esta banda?',
  'Strikers': '¿Qué tipo de delantero centro se adapta a tu táctica?'
};

const GROUP_IMAGES = {
  'Goalkeepers': { 1: 'gk_1.jpg', 2: 'gk_2.jpg', 3: 'gk_3.jpg' },
  'Centerbacks': { 1: 'cb_1.jpg', 2: 'cb_2.jpg', 3: 'cb_3.jpg' },
  'Fullbacks': { 1: 'fb_1.jpg', 2: 'fb_2.jpg', 3: 'fb_3.jpg', 4: 'fb_4.jpg' },
  'Midfielders': { 1: 'mid_1.jpg', 2: 'mid_2.jpg', 3: 'mid_3.jpg', 4: 'mid_4.jpg' },
  'Wingers': { 1: 'winger_1.jpg', 2: 'winger_2.jpg', 3: 'winger_3.jpg' },
  'Strikers': { 1: 'striker_1.jpg', 2: 'striker_2.jpg', 3: 'striker_3.jpg' }
};

const formations = {
  '4-3-3': [
    { id: 'gk', pos: 'GK', group: 'Goalkeepers', top: '50%', left: '15%' },
    { id: 'lb', pos: 'LB', group: 'Fullbacks', top: '15%', left: '35%' },
    { id: 'cb1', pos: 'CB', group: 'Centerbacks', top: '38%', left: '30%' },
    { id: 'cb2', pos: 'CB', group: 'Centerbacks', top: '62%', left: '30%' },
    { id: 'rb', pos: 'RB', group: 'Fullbacks', top: '85%', left: '35%' },
    { id: 'cm1', pos: 'CM', group: 'Midfielders', top: '35%', left: '55%' },
    { id: 'cm2', pos: 'CM', group: 'Midfielders', top: '65%', left: '55%' },
    { id: 'cam', pos: 'CAM', group: 'Midfielders', top: '50%', left: '65%' },
    { id: 'lw', pos: 'LW', group: 'Wingers', top: '20%', left: '85%' },
    { id: 'st', pos: 'ST', group: 'Strikers', top: '50%', left: '90%' },
    { id: 'rw', pos: 'RW', group: 'Wingers', top: '80%', left: '85%' }
  ],
  '4-4-2': [
    { id: 'gk', pos: 'GK', group: 'Goalkeepers', top: '50%', left: '15%' },
    { id: 'lb', pos: 'LB', group: 'Fullbacks', top: '15%', left: '35%' },
    { id: 'cb1', pos: 'CB', group: 'Centerbacks', top: '38%', left: '30%' },
    { id: 'cb2', pos: 'CB', group: 'Centerbacks', top: '62%', left: '30%' },
    { id: 'rb', pos: 'RB', group: 'Fullbacks', top: '85%', left: '35%' },
    { id: 'lm', pos: 'LM', group: 'Wingers', top: '15%', left: '60%' },
    { id: 'cm1', pos: 'CM', group: 'Midfielders', top: '38%', left: '55%' },
    { id: 'cm2', pos: 'CM', group: 'Midfielders', top: '62%', left: '55%' },
    { id: 'rm', pos: 'RM', group: 'Wingers', top: '85%', left: '60%' },
    { id: 'st1', pos: 'ST', group: 'Strikers', top: '38%', left: '85%' },
    { id: 'st2', pos: 'ST', group: 'Strikers', top: '62%', left: '85%' }
  ],
  '3-5-2': [
    { id: 'gk', pos: 'GK', group: 'Goalkeepers', top: '50%', left: '15%' },
    { id: 'cb1', pos: 'CB', group: 'Centerbacks', top: '20%', left: '30%' },
    { id: 'cb2', pos: 'CB', group: 'Centerbacks', top: '50%', left: '28%' },
    { id: 'cb3', pos: 'CB', group: 'Centerbacks', top: '80%', left: '30%' },
    { id: 'lm', pos: 'LM', group: 'Wingers', top: '15%', left: '55%' },
    { id: 'cm1', pos: 'CM', group: 'Midfielders', top: '40%', left: '55%' },
    { id: 'cm2', pos: 'CM', group: 'Midfielders', top: '60%', left: '55%' },
    { id: 'rm', pos: 'RM', group: 'Wingers', top: '85%', left: '55%' },
    { id: 'cam', pos: 'CAM', group: 'Midfielders', top: '50%', left: '70%' },
    { id: 'st1', pos: 'ST', group: 'Strikers', top: '38%', left: '85%' },
    { id: 'st2', pos: 'ST', group: 'Strikers', top: '62%', left: '85%' }
  ],
  '4-2-3-1': [
    { id: 'gk', pos: 'GK', group: 'Goalkeepers', top: '50%', left: '15%' },
    { id: 'lb', pos: 'LB', group: 'Fullbacks', top: '15%', left: '35%' },
    { id: 'cb1', pos: 'CB', group: 'Centerbacks', top: '38%', left: '30%' },
    { id: 'cb2', pos: 'CB', group: 'Centerbacks', top: '62%', left: '30%' },
    { id: 'rb', pos: 'RB', group: 'Fullbacks', top: '85%', left: '35%' },
    { id: 'cdm1', pos: 'CDM', group: 'Midfielders', top: '38%', left: '50%' },
    { id: 'cdm2', pos: 'CDM', group: 'Midfielders', top: '62%', left: '50%' },
    { id: 'lam', pos: 'CAM', group: 'Midfielders', top: '20%', left: '70%' },
    { id: 'cam', pos: 'CAM', group: 'Midfielders', top: '50%', left: '68%' },
    { id: 'ram', pos: 'CAM', group: 'Midfielders', top: '80%', left: '70%' },
    { id: 'st', pos: 'ST', group: 'Strikers', top: '50%', left: '90%' }
  ],
  '4-3-2-1': [
    { id: 'gk', pos: 'GK', group: 'Goalkeepers', top: '50%', left: '15%' },
    { id: 'lb', pos: 'LB', group: 'Fullbacks', top: '15%', left: '35%' },
    { id: 'cb1', pos: 'CB', group: 'Centerbacks', top: '38%', left: '30%' },
    { id: 'cb2', pos: 'CB', group: 'Centerbacks', top: '62%', left: '30%' },
    { id: 'rb', pos: 'RB', group: 'Fullbacks', top: '85%', left: '35%' },
    { id: 'cm1', pos: 'CM', group: 'Midfielders', top: '25%', left: '55%' },
    { id: 'cm2', pos: 'CM', group: 'Midfielders', top: '50%', left: '50%' },
    { id: 'cm3', pos: 'CM', group: 'Midfielders', top: '75%', left: '55%' },
    { id: 'lam', pos: 'CAM', group: 'Midfielders', top: '35%', left: '70%' },
    { id: 'ram', pos: 'CAM', group: 'Midfielders', top: '65%', left: '70%' },
    { id: 'st', pos: 'ST', group: 'Strikers', top: '50%', left: '85%' }
  ],
  '2-3-1': [
    { id: 'gk', pos: 'GK', group: 'Goalkeepers', top: '50%', left: '15%' },
    { id: 'cb1', pos: 'CB', group: 'Centerbacks', top: '30%', left: '30%' },
    { id: 'cb2', pos: 'CB', group: 'Centerbacks', top: '70%', left: '30%' },
    { id: 'cm1', pos: 'CM', group: 'Midfielders', top: '20%', left: '55%' },
    { id: 'cm2', pos: 'CM', group: 'Midfielders', top: '50%', left: '50%' },
    { id: 'cm3', pos: 'CM', group: 'Midfielders', top: '80%', left: '55%' },
    { id: 'st', pos: 'ST', group: 'Strikers', top: '50%', left: '85%' }
  ],
  '3-2-1': [
    { id: 'gk', pos: 'GK', group: 'Goalkeepers', top: '50%', left: '15%' },
    { id: 'cb1', pos: 'CB', group: 'Centerbacks', top: '20%', left: '30%' },
    { id: 'cb2', pos: 'CB', group: 'Centerbacks', top: '50%', left: '28%' },
    { id: 'cb3', pos: 'CB', group: 'Centerbacks', top: '80%', left: '30%' },
    { id: 'cm1', pos: 'CM', group: 'Midfielders', top: '35%', left: '55%' },
    { id: 'cm2', pos: 'CM', group: 'Midfielders', top: '65%', left: '55%' },
    { id: 'st', pos: 'ST', group: 'Strikers', top: '50%', left: '85%' }
  ],
  '2-2-2': [
    { id: 'gk', pos: 'GK', group: 'Goalkeepers', top: '50%', left: '15%' },
    { id: 'cb1', pos: 'CB', group: 'Centerbacks', top: '30%', left: '30%' },
    { id: 'cb2', pos: 'CB', group: 'Centerbacks', top: '70%', left: '30%' },
    { id: 'cm1', pos: 'CM', group: 'Midfielders', top: '30%', left: '55%' },
    { id: 'cm2', pos: 'CM', group: 'Midfielders', top: '70%', left: '55%' },
    { id: 'st1', pos: 'ST', group: 'Strikers', top: '30%', left: '85%' },
    { id: 'st2', pos: 'ST', group: 'Strikers', top: '70%', left: '85%' }
  ]
};

window.currentDraftMode = '11v11';

let currentFormation = '4-3-3';
let currentArchetype = null;
let draftedPlayers = {};
let currentActiveSlot = null;
let draftPhase = 0;

const FORMATIONS_HTML = `
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

        <!-- TIKI_TAKA -->
        <div class="formation-card active" data-formation="4-3-3" data-archetype="tiki_taka">
          <h4 class="formation-card-title">Tiki-Taka</h4>
          <p class="formation-card-subtitle">Juego de Posición</p>
          <div class="mini-pitch">
            <div class="mini-pitch-line"></div><div class="mini-pitch-circle"></div><div class="mini-pitch-arrow"></div>
            <div class="mini-dot gk" style="left:8%; top:50%;"></div><div class="mini-dot" style="left:20%; top:20%;"></div><div class="mini-dot" style="left:20%; top:40%;"></div><div class="mini-dot" style="left:20%; top:60%;"></div><div class="mini-dot" style="left:20%; top:80%;"></div><div class="mini-dot" style="left:40%; top:30%;"></div><div class="mini-dot" style="left:35%; top:50%;"></div><div class="mini-dot" style="left:40%; top:70%;"></div><div class="mini-dot" style="left:60%; top:25%;"></div><div class="mini-dot" style="left:65%; top:50%;"></div><div class="mini-dot" style="left:60%; top:75%;"></div>
          </div>
          <p class="style-description">Monopolio del balón, pases cortos, paciencia para desorganizar, uso de toda la cancha y presión asfixiante.</p>
          <div style="height: 1px; background: rgba(255,255,255,0.1); margin-bottom: 0.3rem; width: 100%;"></div>
          <div class="metrics-grid">

            <div class="metric-item">
              <div class="metric-title">Defensa</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 95%;"></div>
              </div>
              <div class="metric-labels"><span>Bloque Bajo</span><span>Presión Alta</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Posesión</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 95%;"></div>
              </div>
              <div class="metric-labels"><span>Contra Rápida</span><span>Tiki-Taka</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Ritmo de Juego</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 15%;"></div>
              </div>
              <div class="metric-labels"><span>Pausado</span><span>Frenético</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Amplitud</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 90%;"></div>
              </div>
              <div class="metric-labels"><span>Pasillo Central</span><span>Exclusivo Bandas</span></div>
            </div>

          </div>
        </div>

        <!-- CATENACCIO -->
        <div class="formation-card" data-formation="3-5-2" data-archetype="catenaccio">
          <h4 class="formation-card-title">Catenaccio Moderno</h4>
          <p class="formation-card-subtitle">Muro y Contragolpe</p>
          <div class="mini-pitch">
            <div class="mini-pitch-line"></div><div class="mini-pitch-circle"></div><div class="mini-pitch-arrow"></div>
            <div class="mini-dot gk" style="left:8%; top:50%;"></div><div class="mini-dot" style="left:15%; top:30%;"></div><div class="mini-dot" style="left:15%; top:50%;"></div><div class="mini-dot" style="left:15%; top:70%;"></div><div class="mini-dot" style="left:30%; top:15%;"></div><div class="mini-dot" style="left:25%; top:35%;"></div><div class="mini-dot" style="left:25%; top:65%;"></div><div class="mini-dot" style="left:30%; top:85%;"></div><div class="mini-dot" style="left:35%; top:50%;"></div><div class="mini-dot" style="left:50%; top:40%;"></div><div class="mini-dot" style="left:50%; top:60%;"></div>
          </div>
          <p class="style-description">Solidez defensiva, bloque bajo impenetrable y salidas verticales explosivas al espacio.</p>
          <div style="height: 1px; background: rgba(255,255,255,0.1); margin-bottom: 0.3rem; width: 100%;"></div>
          <div class="metrics-grid">

            <div class="metric-item">
              <div class="metric-title">Defensa</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 5%;"></div>
              </div>
              <div class="metric-labels"><span>Bloque Bajo</span><span>Presión Alta</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Posesión</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 10%;"></div>
              </div>
              <div class="metric-labels"><span>Contra Rápida</span><span>Tiki-Taka</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Ritmo de Juego</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 90%;"></div>
              </div>
              <div class="metric-labels"><span>Pausado</span><span>Frenético</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Amplitud</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 25%;"></div>
              </div>
              <div class="metric-labels"><span>Pasillo Central</span><span>Exclusivo Bandas</span></div>
            </div>

          </div>
        </div>

        <!-- GEGENPRESSING -->
        <div class="formation-card" data-formation="4-2-3-1" data-archetype="gegenpressing">
          <h4 class="formation-card-title">Gegenpressing</h4>
          <p class="formation-card-subtitle">Presión Asfixiante</p>
          <div class="mini-pitch">
            <div class="mini-pitch-line"></div><div class="mini-pitch-circle"></div><div class="mini-pitch-arrow"></div>
            <div class="mini-dot gk" style="left:8%; top:50%;"></div><div class="mini-dot" style="left:30%; top:20%;"></div><div class="mini-dot" style="left:25%; top:40%;"></div><div class="mini-dot" style="left:25%; top:60%;"></div><div class="mini-dot" style="left:30%; top:80%;"></div><div class="mini-dot" style="left:45%; top:35%;"></div><div class="mini-dot" style="left:45%; top:65%;"></div><div class="mini-dot" style="left:60%; top:25%;"></div><div class="mini-dot" style="left:65%; top:50%;"></div><div class="mini-dot" style="left:60%; top:75%;"></div><div class="mini-dot" style="left:80%; top:50%;"></div>
          </div>
          <p class="style-description">Presión alta agresiva tras pérdida, robo e inmediatez ofensiva a máxima velocidad.</p>
          <div style="height: 1px; background: rgba(255,255,255,0.1); margin-bottom: 0.3rem; width: 100%;"></div>
          <div class="metrics-grid">

            <div class="metric-item">
              <div class="metric-title">Defensa</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 95%;"></div>
              </div>
              <div class="metric-labels"><span>Bloque Bajo</span><span>Presión Alta</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Posesión</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 35%;"></div>
              </div>
              <div class="metric-labels"><span>Contra Rápida</span><span>Tiki-Taka</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Ritmo de Juego</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 95%;"></div>
              </div>
              <div class="metric-labels"><span>Pausado</span><span>Frenético</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Amplitud</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 65%;"></div>
              </div>
              <div class="metric-labels"><span>Pasillo Central</span><span>Exclusivo Bandas</span></div>
            </div>

          </div>
        </div>

        <!-- ASOCIATIVO -->
        <div class="formation-card" data-formation="4-3-2-1" data-archetype="asociativo">
          <h4 class="formation-card-title">Asociativo</h4>
          <p class="formation-card-subtitle">Sociedad Central</p>
          <div class="mini-pitch">
            <div class="mini-pitch-line"></div><div class="mini-pitch-circle"></div><div class="mini-pitch-arrow"></div>
            <div class="mini-dot gk" style="left:8%; top:50%;"></div><div class="mini-dot" style="left:20%; top:20%;"></div><div class="mini-dot" style="left:20%; top:40%;"></div><div class="mini-dot" style="left:20%; top:60%;"></div><div class="mini-dot" style="left:20%; top:80%;"></div><div class="mini-dot" style="left:40%; top:30%;"></div><div class="mini-dot" style="left:35%; top:50%;"></div><div class="mini-dot" style="left:40%; top:70%;"></div><div class="mini-dot" style="left:60%; top:35%;"></div><div class="mini-dot" style="left:60%; top:65%;"></div><div class="mini-dot" style="left:75%; top:50%;"></div>
          </div>
          <p class="style-description">Posesión y talento interior. Mediocampistas tocando en corto por el medio y marcando los tiempos.</p>
          <div style="height: 1px; background: rgba(255,255,255,0.1); margin-bottom: 0.3rem; width: 100%;"></div>
          <div class="metrics-grid">

            <div class="metric-item">
              <div class="metric-title">Defensa</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 65%;"></div>
              </div>
              <div class="metric-labels"><span>Bloque Bajo</span><span>Presión Alta</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Posesión</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 85%;"></div>
              </div>
              <div class="metric-labels"><span>Contra Rápida</span><span>Tiki-Taka</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Ritmo de Juego</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 30%;"></div>
              </div>
              <div class="metric-labels"><span>Pausado</span><span>Frenético</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Amplitud</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 5%;"></div>
              </div>
              <div class="metric-labels"><span>Pasillo Central</span><span>Exclusivo Bandas</span></div>
            </div>

          </div>
        </div>

        <!-- DIRECTO -->
        <div class="formation-card" data-formation="4-4-2" data-archetype="directo">
          <h4 class="formation-card-title">Fútbol Directo</h4>
          <p class="formation-card-subtitle">La Vía Directa</p>
          <div class="mini-pitch">
            <div class="mini-pitch-line"></div><div class="mini-pitch-circle"></div><div class="mini-pitch-arrow"></div>
            <div class="mini-dot gk" style="left:8%; top:50%;"></div><div class="mini-dot" style="left:20%; top:20%;"></div><div class="mini-dot" style="left:20%; top:40%;"></div><div class="mini-dot" style="left:20%; top:60%;"></div><div class="mini-dot" style="left:20%; top:80%;"></div><div class="mini-dot" style="left:45%; top:20%;"></div><div class="mini-dot" style="left:45%; top:40%;"></div><div class="mini-dot" style="left:45%; top:60%;"></div><div class="mini-dot" style="left:45%; top:80%;"></div><div class="mini-dot" style="left:65%; top:35%;"></div><div class="mini-dot" style="left:65%; top:65%;"></div>
          </div>
          <p class="style-description">Juego directo. Pelotazos largos, disputa de segundas jugadas y ataque puro por las bandas para centros.</p>
          <div style="height: 1px; background: rgba(255,255,255,0.1); margin-bottom: 0.3rem; width: 100%;"></div>
          <div class="metrics-grid">

            <div class="metric-item">
              <div class="metric-title">Defensa</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 30%;"></div>
              </div>
              <div class="metric-labels"><span>Bloque Bajo</span><span>Presión Alta</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Posesión</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 5%;"></div>
              </div>
              <div class="metric-labels"><span>Contra Rápida</span><span>Tiki-Taka</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Ritmo de Juego</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 75%;"></div>
              </div>
              <div class="metric-labels"><span>Pausado</span><span>Frenético</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Amplitud</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 95%;"></div>
              </div>
              <div class="metric-labels"><span>Pasillo Central</span><span>Exclusivo Bandas</span></div>
            </div>

          </div>
        </div>

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

const FORMATIONS_HTML_7V7 = `
  <style>
    .formation-card-title { color: #e74c3c; font-size: 1.3rem; font-weight: 900; text-transform: uppercase; margin-bottom: 0.1rem; font-family: 'Outfit', sans-serif; letter-spacing: 0px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .formation-card-subtitle { color: #ccc; font-size: 0.8rem; margin-bottom: 0.4rem; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .mini-pitch { width: 100%; height: 95px; border: 2px solid #e74c3c; border-radius: 8px; background: #1a3320; position: relative; overflow: hidden; flex-shrink: 0; margin: 0 auto 0.4rem auto; max-width: 220px; }
    .mini-pitch-line { position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: rgba(255,255,255,0.3); }
    .mini-pitch-circle { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); width: 25px; height: 25px; border: 1px solid rgba(255,255,255,0.3); border-radius: 50%; }
    .mini-pitch-arrow { position: absolute; left: 30%; top: 50%; transform: translateY(-50%); width: 40%; height: 3px; background: #2ecc71; z-index: 2; }
    .mini-pitch-arrow::after { content: ''; position: absolute; right: -6px; top: -3px; border-left: 6px solid #2ecc71; border-top: 4px solid transparent; border-bottom: 4px solid transparent; }
    .mini-dot { position: absolute; width: 10px; height: 10px; border-radius: 50%; background: #e74c3c; transform: translate(-50%, -50%); z-index: 3; box-shadow: 0 0 4px rgba(0,0,0,0.5); }
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
    <h3 style="color: var(--text-primary); margin-bottom: 0.5rem; font-size: 1.5rem; text-shadow: 0 4px 8px rgba(0,0,0,0.8); font-weight: 900;">Fútbol 7: Seleccioná tu Estilo</h3>
    <div class="carousel-wrapper">
      <button class="carousel-btn prev" id="carousel-prev" style="top: 45%;">&#10094;</button>
      <div class="carousel-viewport">
        <div class="formation-cards-container" id="formation-cards-container">

        <!-- TIKI_TAKA -->
        <div class="formation-card active" data-formation="2-3-1" data-archetype="tiki_taka">
          <h4 class="formation-card-title">Tiki-Taka</h4>
          <p class="formation-card-subtitle">Juego de Posición</p>
          <div class="mini-pitch">
            <div class="mini-pitch-line"></div><div class="mini-pitch-circle"></div><div class="mini-pitch-arrow"></div>
            <div class="mini-dot gk" style="left:8%; top:50%;"></div><div class="mini-dot" style="left:25%; top:30%;"></div><div class="mini-dot" style="left:25%; top:70%;"></div><div class="mini-dot" style="left:50%; top:20%;"></div><div class="mini-dot" style="left:45%; top:50%;"></div><div class="mini-dot" style="left:50%; top:80%;"></div><div class="mini-dot" style="left:75%; top:50%;"></div>
          </div>
          <p class="style-description">Monopolio del balón, pases cortos, paciencia para desorganizar, uso de toda la cancha y presión asfixiante.</p>
          <div style="height: 1px; background: rgba(255,255,255,0.1); margin-bottom: 0.3rem; width: 100%;"></div>
          <div class="metrics-grid">

            <div class="metric-item">
              <div class="metric-title">Defensa</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 95%;"></div>
              </div>
              <div class="metric-labels"><span>Bloque Bajo</span><span>Presión Alta</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Posesión</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 95%;"></div>
              </div>
              <div class="metric-labels"><span>Contra Rápida</span><span>Tiki-Taka</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Ritmo de Juego</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 15%;"></div>
              </div>
              <div class="metric-labels"><span>Pausado</span><span>Frenético</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Amplitud</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 90%;"></div>
              </div>
              <div class="metric-labels"><span>Pasillo Central</span><span>Exclusivo Bandas</span></div>
            </div>

          </div>
        </div>

        <!-- CATENACCIO -->
        <div class="formation-card" data-formation="3-2-1" data-archetype="catenaccio">
          <h4 class="formation-card-title">Catenaccio Moderno</h4>
          <p class="formation-card-subtitle">Muro y Contragolpe</p>
          <div class="mini-pitch">
            <div class="mini-pitch-line"></div><div class="mini-pitch-circle"></div><div class="mini-pitch-arrow"></div>
            <div class="mini-dot gk" style="left:8%; top:50%;"></div><div class="mini-dot" style="left:25%; top:20%;"></div><div class="mini-dot" style="left:25%; top:50%;"></div><div class="mini-dot" style="left:25%; top:80%;"></div><div class="mini-dot" style="left:50%; top:35%;"></div><div class="mini-dot" style="left:50%; top:65%;"></div><div class="mini-dot" style="left:75%; top:50%;"></div>
          </div>
          <p class="style-description">Solidez defensiva, bloque bajo impenetrable y salidas verticales explosivas al espacio.</p>
          <div style="height: 1px; background: rgba(255,255,255,0.1); margin-bottom: 0.3rem; width: 100%;"></div>
          <div class="metrics-grid">

            <div class="metric-item">
              <div class="metric-title">Defensa</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 5%;"></div>
              </div>
              <div class="metric-labels"><span>Bloque Bajo</span><span>Presión Alta</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Posesión</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 10%;"></div>
              </div>
              <div class="metric-labels"><span>Contra Rápida</span><span>Tiki-Taka</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Ritmo de Juego</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 90%;"></div>
              </div>
              <div class="metric-labels"><span>Pausado</span><span>Frenético</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Amplitud</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 25%;"></div>
              </div>
              <div class="metric-labels"><span>Pasillo Central</span><span>Exclusivo Bandas</span></div>
            </div>

          </div>
        </div>

        <!-- GEGENPRESSING -->
        <div class="formation-card" data-formation="3-2-1" data-archetype="gegenpressing">
          <h4 class="formation-card-title">Gegenpressing</h4>
          <p class="formation-card-subtitle">Presión Asfixiante</p>
          <div class="mini-pitch">
            <div class="mini-pitch-line"></div><div class="mini-pitch-circle"></div><div class="mini-pitch-arrow"></div>
            <div class="mini-dot gk" style="left:8%; top:50%;"></div><div class="mini-dot" style="left:25%; top:20%;"></div><div class="mini-dot" style="left:25%; top:50%;"></div><div class="mini-dot" style="left:25%; top:80%;"></div><div class="mini-dot" style="left:50%; top:35%;"></div><div class="mini-dot" style="left:50%; top:65%;"></div><div class="mini-dot" style="left:75%; top:50%;"></div>
          </div>
          <p class="style-description">Presión alta agresiva tras pérdida, robo e inmediatez ofensiva a máxima velocidad.</p>
          <div style="height: 1px; background: rgba(255,255,255,0.1); margin-bottom: 0.3rem; width: 100%;"></div>
          <div class="metrics-grid">

            <div class="metric-item">
              <div class="metric-title">Defensa</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 95%;"></div>
              </div>
              <div class="metric-labels"><span>Bloque Bajo</span><span>Presión Alta</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Posesión</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 35%;"></div>
              </div>
              <div class="metric-labels"><span>Contra Rápida</span><span>Tiki-Taka</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Ritmo de Juego</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 95%;"></div>
              </div>
              <div class="metric-labels"><span>Pausado</span><span>Frenético</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Amplitud</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 65%;"></div>
              </div>
              <div class="metric-labels"><span>Pasillo Central</span><span>Exclusivo Bandas</span></div>
            </div>

          </div>
        </div>

        <!-- ASOCIATIVO -->
        <div class="formation-card" data-formation="2-3-1" data-archetype="asociativo">
          <h4 class="formation-card-title">Asociativo</h4>
          <p class="formation-card-subtitle">Sociedad Central</p>
          <div class="mini-pitch">
            <div class="mini-pitch-line"></div><div class="mini-pitch-circle"></div><div class="mini-pitch-arrow"></div>
            <div class="mini-dot gk" style="left:8%; top:50%;"></div><div class="mini-dot" style="left:25%; top:30%;"></div><div class="mini-dot" style="left:25%; top:70%;"></div><div class="mini-dot" style="left:50%; top:20%;"></div><div class="mini-dot" style="left:45%; top:50%;"></div><div class="mini-dot" style="left:50%; top:80%;"></div><div class="mini-dot" style="left:75%; top:50%;"></div>
          </div>
          <p class="style-description">Posesión y talento interior. Mediocampistas tocando en corto por el medio y marcando los tiempos.</p>
          <div style="height: 1px; background: rgba(255,255,255,0.1); margin-bottom: 0.3rem; width: 100%;"></div>
          <div class="metrics-grid">

            <div class="metric-item">
              <div class="metric-title">Defensa</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 65%;"></div>
              </div>
              <div class="metric-labels"><span>Bloque Bajo</span><span>Presión Alta</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Posesión</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 85%;"></div>
              </div>
              <div class="metric-labels"><span>Contra Rápida</span><span>Tiki-Taka</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Ritmo de Juego</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 30%;"></div>
              </div>
              <div class="metric-labels"><span>Pausado</span><span>Frenético</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Amplitud</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 5%;"></div>
              </div>
              <div class="metric-labels"><span>Pasillo Central</span><span>Exclusivo Bandas</span></div>
            </div>

          </div>
        </div>

        <!-- DIRECTO -->
        <div class="formation-card" data-formation="2-2-2" data-archetype="directo">
          <h4 class="formation-card-title">Fútbol Directo</h4>
          <p class="formation-card-subtitle">La Vía Directa</p>
          <div class="mini-pitch">
            <div class="mini-pitch-line"></div><div class="mini-pitch-circle"></div><div class="mini-pitch-arrow"></div>
            <div class="mini-dot gk" style="left:8%; top:50%;"></div><div class="mini-dot" style="left:25%; top:30%;"></div><div class="mini-dot" style="left:25%; top:70%;"></div><div class="mini-dot" style="left:50%; top:30%;"></div><div class="mini-dot" style="left:50%; top:70%;"></div><div class="mini-dot" style="left:75%; top:30%;"></div><div class="mini-dot" style="left:75%; top:70%;"></div>
          </div>
          <p class="style-description">Juego directo. Pelotazos largos, disputa de segundas jugadas y ataque puro por las bandas para centros.</p>
          <div style="height: 1px; background: rgba(255,255,255,0.1); margin-bottom: 0.3rem; width: 100%;"></div>
          <div class="metrics-grid">

            <div class="metric-item">
              <div class="metric-title">Defensa</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 30%;"></div>
              </div>
              <div class="metric-labels"><span>Bloque Bajo</span><span>Presión Alta</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Posesión</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 5%;"></div>
              </div>
              <div class="metric-labels"><span>Contra Rápida</span><span>Tiki-Taka</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Ritmo de Juego</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 75%;"></div>
              </div>
              <div class="metric-labels"><span>Pausado</span><span>Frenético</span></div>
            </div>

            <div class="metric-item">
              <div class="metric-title">Amplitud</div>
              <div class="metric-bar-bg">
                <div class="metric-bar-fill" style="width: 95%;"></div>
              </div>
              <div class="metric-labels"><span>Pasillo Central</span><span>Exclusivo Bandas</span></div>
            </div>

          </div>
        </div>

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

export function initDraft() {
  const btnRestart = document.getElementById('btn-restart-draft');
  const btnApply = document.getElementById('btn-apply-draft-tactics');
  const closeModalBtn = document.getElementById('close-draft-modal-btn');

  if (btnRestart) {
    btnRestart.addEventListener('click', (e) => {
      const btn = e.currentTarget;
      btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Reiniciando...';
      btn.style.pointerEvents = 'none';
      btn.style.opacity = '0.7';

      const pitch = document.getElementById('pitch-container');
      const summary = document.getElementById('draft-summary-banner');

      // Step 1: fade out everything in the draft container
      const draftContainer = pitch ? pitch.parentElement : null;
      if (draftContainer) {
        draftContainer.style.transition = 'opacity 0.5s ease';
        draftContainer.style.opacity = '0';
      }

      // Step 2: after fade-out, show loading overlay, then restart
      setTimeout(() => {
        // Inject full-screen loading overlay on top of pitch
        if (pitch) {
          pitch.innerHTML = '';
        }
        if (summary) {
          summary.classList.add('draft-summary-hidden');
        }

        // Create loading screen
        const loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'draft-restart-loading';
        loadingOverlay.style.cssText = `
          position: absolute; top: 0; left: 0; width: 100%; height: 100%;
          background: rgba(5, 8, 18, 0.97); z-index: 999;
          display: flex; flex-direction: column;
          align-items: center; justify-content: center;
          border-radius: 16px; opacity: 0;
          transition: opacity 0.4s ease;
        `;
        loadingOverlay.innerHTML = `
          <div style="text-align:center;">
            <div style="font-size:3.5rem; margin-bottom:1.5rem; animation: spinAnim 1.2s linear infinite; display:inline-block;">⚽</div>
            <div style="font-family:'Outfit',sans-serif; font-size:1.6rem; font-weight:700; color:#fff; letter-spacing:2px; margin-bottom:0.5rem;">
              Reiniciando Draft
            </div>
            <div id="restart-dots" style="font-family:'Outfit',sans-serif; font-size:1.6rem; color:#0088ff; letter-spacing:4px; min-height:2rem;"></div>
          </div>
        `;

        document.getElementById('draft-template').appendChild(loadingOverlay);
        // Fade in overlay
        requestAnimationFrame(() => { requestAnimationFrame(() => { loadingOverlay.style.opacity = '1'; }); });

        // Animate dots
        let dotCount = 0;
        const dotsEl = document.getElementById('restart-dots');
        const dotsInterval = setInterval(() => {
          dotCount = (dotCount + 1) % 4;
          if (dotsEl) dotsEl.textContent = '●'.repeat(dotCount) + '○'.repeat(3 - dotCount);
        }, 300);

        // Fade main container back in slowly while overlay is up
        if (draftContainer) {
          draftContainer.style.opacity = '1';
        }

        // Step 3: after 1.6s, fade out overlay and launch fresh draft
        setTimeout(() => {
          clearInterval(dotsInterval);
          loadingOverlay.style.opacity = '0';
          setTimeout(() => {
            loadingOverlay.remove();
            btn.innerHTML = '<i class="fa-solid fa-rotate-right"></i> Reiniciar';
            btn.style.pointerEvents = 'auto';
            btn.style.opacity = '1';
            startDraft(true);
          }, 400);
        }, 1600);

      }, 550);
    });
  }

  if (btnApply) {
    btnApply.addEventListener('click', () => {
      if (window.applyDraftTactics) {
        window.applyDraftTactics(state.userPreferences.tacticalVector);
      } else {
        document.querySelector('.nav-btn[data-tab="recommender"]').click();
      }
    });
  }

  if (closeModalBtn) {
    closeModalBtn.addEventListener('click', () => {
      document.getElementById('draft-modal').classList.remove('active');
    });
  }
}

export function startDraft(isInitial = false, type = null) {
  if (type) window.currentDraftMode = type;
  
  if (window.currentDraftMode === '7v7' && !['2-3-1', '3-2-1', '2-2-2'].includes(currentFormation)) {
    currentFormation = '2-3-1';
  } else if (window.currentDraftMode === '11v11' && !['4-3-3', '4-4-2', '3-5-2', '4-2-3-1', '4-3-2-1'].includes(currentFormation)) {
    currentFormation = '4-3-3';
  }

  draftedPlayers = {};
  currentActiveSlot = null;
  draftPhase = 0;

  document.getElementById('draft-summary-banner').classList.add('draft-summary-hidden');

  const pitch = document.getElementById('pitch-container');
  if (!pitch) return;

  pitch.innerHTML = `
    <div class="pitch-lines-overlay">
      <div class="pitch-center-line"></div>
      <div class="pitch-center-circle"></div>
      <div class="pitch-penalty-area left">
        <div class="pitch-goal-area"></div>
        <div class="pitch-penalty-arc"></div>
      </div>
      <div class="pitch-penalty-area right">
        <div class="pitch-goal-area"></div>
        <div class="pitch-penalty-arc"></div>
      </div>
    </div>
  `;

  const layout = formations[currentFormation];
  layout.forEach(slot => {
    const el = document.createElement('div');
    el.className = 'draft-slot';
    el.style.top = slot.top;
    el.style.left = slot.left;
    el.dataset.id = slot.id;
    el.dataset.group = slot.group;
    // Start invisible for sequential reveal
    el.style.opacity = '0';
    el.style.transform = 'translate(-50%, -50%) scale(0.6)';
    el.style.filter = 'blur(8px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s cubic-bezier(0.2,0.8,0.2,1), filter 0.6s ease';

    el.innerHTML = `
      <div class="draft-slot-pos">${slot.pos}</div>
    `;

    el.addEventListener('click', () => openDraftOptions(slot.id, slot.group));
    pitch.appendChild(el);
  });

  if (isInitial) {
    const overlay = document.createElement('div');
    overlay.className = 'draft-start-overlay';
    overlay.id = 'draft-start-overlay';
    overlay.innerHTML = `<button class="btn-start-draft" id="btn-start-draft-overlay">Empezar FUT Draft</button>`;
    pitch.appendChild(overlay);

    document.getElementById('btn-start-draft-overlay').addEventListener('click', () => {
      const btn = document.getElementById('btn-start-draft-overlay');
      btn.style.transition = 'all 0.4s ease';
      btn.style.opacity = '0';
      btn.style.transform = 'scale(0.9)';

      setTimeout(() => {
        overlay.innerHTML = window.currentDraftMode === '7v7' ? FORMATIONS_HTML_7V7 : FORMATIONS_HTML;
        overlay.style.animation = 'relaxedFadeIn 1s cubic-bezier(0.22, 1, 0.36, 1) forwards';

        const container = document.getElementById('formation-cards-container');
        const cards = document.querySelectorAll('.formation-card');
        let currentIndex = 0;
        let slideInterval;

        const updateCarousel = () => {
          container.style.transform = `translateX(-${currentIndex * 100}%)`;
          cards.forEach((c, i) => {
            if (i === currentIndex) c.classList.add('active');
            else c.classList.remove('active');
          });
          const dots = document.querySelectorAll('.carousel-dot');
          dots.forEach((d, i) => {
            if (i === currentIndex) d.classList.add('active');
            else d.classList.remove('active');
          });
        };

        const nextSlide = () => {
          currentIndex = (currentIndex + 1) % cards.length;
          updateCarousel();
        };

        const prevSlide = () => {
          currentIndex = (currentIndex - 1 + cards.length) % cards.length;
          updateCarousel();
        };

        const dots = document.querySelectorAll('.carousel-dot');
        dots.forEach((dot, index) => {
          dot.addEventListener('click', () => {
            clearInterval(slideInterval);
            currentIndex = index;
            updateCarousel();
            slideInterval = setInterval(nextSlide, 3000);
          });
        });

        document.getElementById('carousel-next').addEventListener('click', () => {
          clearInterval(slideInterval);
          nextSlide();
          slideInterval = setInterval(nextSlide, 3000);
        });

        document.getElementById('carousel-prev').addEventListener('click', () => {
          clearInterval(slideInterval);
          prevSlide();
          slideInterval = setInterval(nextSlide, 3000);
        });

        slideInterval = setInterval(nextSlide, 3000);

        const carouselWrapper = document.querySelector('.carousel-wrapper');
        if (carouselWrapper) {
          carouselWrapper.addEventListener('mouseenter', () => clearInterval(slideInterval));
          carouselWrapper.addEventListener('mouseleave', () => {
            clearInterval(slideInterval);
            slideInterval = setInterval(nextSlide, 3000);
          });
        }

        cards.forEach((card, i) => {
          card.style.opacity = '0';
          card.style.animation = `smoothFadeInUp 1s cubic-bezier(0.22, 1, 0.36, 1) ${i * 0.1}s forwards`;

          card.addEventListener('click', (e) => {
            clearInterval(slideInterval);
            const target = e.currentTarget;
            currentFormation = target.dataset.formation;
            currentArchetype = target.dataset.archetype;

            overlay.style.transition = 'opacity 0.4s ease';
            overlay.style.opacity = '0';
            setTimeout(() => {
              startDraft(false); // Restart with the chosen formation and begin draft
            }, 400);
          });
        });
      }, 400);
    });
  } else {
    // Wait for overlay fade then begin sequential reveal
    setTimeout(() => {
      beginDraft();
    }, 500);
  }

  updateDraftState();
}

function beginDraft() {
  draftPhase = 1;
  const overlay = document.getElementById('draft-start-overlay');
  if (overlay) {
    overlay.style.transition = 'opacity 0.6s ease';
    overlay.style.opacity = '0';
    setTimeout(() => overlay.remove(), 600);
  }
  updateDraftState();

  const slots = document.querySelectorAll('.draft-slot');
  slots.forEach((el, index) => {
    setTimeout(() => {
      el.style.opacity = '1';
      el.style.transform = 'translate(-50%, -50%) scale(1)';
      el.style.filter = 'blur(0px)';
    }, 150 * index);
  });
}

function updateDraftState() {
  if (draftPhase === 0) {
    document.querySelectorAll('.draft-slot').forEach(el => el.classList.add('locked'));
    return;
  }

  const layout = formations[currentFormation];

  const isGroupDrafted = (groups) => {
    const slotsInGroup = layout.filter(s => groups.includes(s.group));
    return slotsInGroup.every(s => draftedPlayers[s.id]);
  };

  if (draftPhase === 1 && isGroupDrafted(['Goalkeepers'])) {
    draftPhase = 2;
  }
  if (draftPhase === 2 && isGroupDrafted(['Centerbacks', 'Fullbacks'])) {
    draftPhase = 3;
  }
  if (draftPhase === 3 && isGroupDrafted(['Midfielders'])) {
    draftPhase = 4;
  }

  let activeGroups = [];
  if (draftPhase === 1) activeGroups = ['Goalkeepers'];
  if (draftPhase === 2) activeGroups = ['Centerbacks', 'Fullbacks'];
  if (draftPhase === 3) activeGroups = ['Midfielders'];
  if (draftPhase === 4) activeGroups = ['Wingers', 'Strikers'];

  let hasHighlighted = false;
  document.querySelectorAll('.draft-slot').forEach(el => {
    const group = el.dataset.group;
    if (activeGroups.includes(group)) {
      if (!draftedPlayers[el.dataset.id]) {
        el.classList.remove('locked');
        el.classList.add('highlighted');
        hasHighlighted = true;
      } else {
        el.classList.remove('highlighted');
        el.classList.remove('locked');
      }
    } else {
      el.classList.remove('highlighted');
      if (!draftedPlayers[el.dataset.id]) {
        el.classList.add('locked');
      }
    }
  });

  const pitch = document.getElementById('pitch-container');
  if (pitch) {
    pitch.classList.add('draft-active-mode');
  }
}

const robustNormalise = str => {
  if (!str) return '';
  return str
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/\u00f8/gi, 'o').replace(/\u00f0/gi, 'd').replace(/\u00fe/gi, 'th')
    .replace(/\u00e6/gi, 'ae').replace(/\u0142/gi, 'l').replace(/\u00df/gi, 'ss').replace(/\u0153/gi, 'oe')
    .replace(/[^\x00-\x7F]/g, '')
    .toLowerCase().trim();
};

function getPlayerPhoto(name) {
  if (!state.appData || !state.appData.photoIndex) return 'https://cdn.sofifa.net/players/notfound_0_120.png';

  const fn = robustNormalise(name);
  if (state.appData.photoIndex[fn]) return state.appData.photoIndex[fn];

  const parts = fn.split(' ');
  if (parts.length > 1) {
    const short = robustNormalise(parts[0][0] + '. ' + parts[parts.length - 1]);
    if (state.appData.photoIndex[short]) return state.appData.photoIndex[short];

    const firstLast = robustNormalise(parts[0] + ' ' + parts[parts.length - 1]);
    if (state.appData.photoIndex[firstLast]) return state.appData.photoIndex[firstLast];

    const lastOnly = robustNormalise(parts[parts.length - 1]);
    if (state.appData.photoIndex[lastOnly]) return state.appData.photoIndex[lastOnly];
  }

  return 'https://cdn.sofifa.net/players/notfound_0_120.png';
}

function openDraftOptions(slotId, groupName) {
  const el = document.querySelector(`.draft-slot[data-id="${slotId}"]`);
  if (el && el.classList.contains('locked')) return;

  currentActiveSlot = slotId;
  const modal = document.getElementById('draft-modal');
  const container = document.getElementById('draft-options-container');
  const title = document.getElementById('draft-modal-title');

  const question = GROUP_QUESTIONS[groupName] || `Seleccioná tu ${groupName}`;
  title.textContent = question;
  container.innerHTML = '';
  modal.classList.add('active');

  if (!state.appData || !state.appData.clusters || !state.appData.clusters[groupName]) {
    container.innerHTML = 'Error: Datos de clusters no cargados.';
    return;
  }

  const metadata = CLUSTER_METADATA[groupName];
  if (!metadata) return;

  Object.keys(metadata).forEach((clusterId, index) => {
    const archetype = metadata[clusterId];
    const wrapper = document.createElement('div');
    wrapper.style.animation = `smoothFadeInUp 1.6s cubic-bezier(0.22, 1, 0.36, 1) ${index * 0.3}s both`;
    const imgBaseName = (GROUP_IMAGES[groupName] && GROUP_IMAGES[groupName][clusterId])
      ? GROUP_IMAGES[groupName][clusterId].split('.')[0]
      : 'default';

    const card = document.createElement('div');
    card.className = 'archetype-selection-card';
    card.innerHTML = `
      <div class="archetype-img-container">
        <div class="archetype-badge">OPCIÓN 0${index + 1}</div>
      </div>
      <div class="archetype-info">
        <div class="archetype-subtitle">ESTILO ${groupName.slice(0, -1)}</div>
        <h4 class="archetype-title">${archetype.name}</h4>
        <p class="archetype-desc">${archetype.desc}</p>
      </div>
    `;

    const imgContainer = card.querySelector('.archetype-img-container');
    const exts = ['jpg', 'png', 'jpeg', 'webp'];
    let extIdx = 0;
    const tryNextExt = () => {
      if (extIdx >= exts.length) {
        imgContainer.style.background = `linear-gradient(to bottom, rgba(15,16,21,0) 0%, #0f1015 100%), url('assets/images/default.jpg') top center/cover no-repeat`;
        return;
      }
      const testImg = new Image();
      testImg.onload = () => {
        imgContainer.style.background = `linear-gradient(to bottom, rgba(15,16,21,0) 0%, #0f1015 100%), url('${testImg.src}') top center/cover no-repeat`;
      };
      testImg.onerror = () => {
        extIdx++;
        tryNextExt();
      };
      testImg.src = `assets/images/${imgBaseName}.${exts[extIdx]}`;
    };
    tryNextExt();

    card.addEventListener('click', () => showPlayersForArchetype(slotId, groupName, clusterId));
    wrapper.appendChild(card);
    container.appendChild(wrapper);
  });
}

function showPlayersForArchetype(slotId, groupName, clusterId) {
  const container = document.getElementById('draft-options-container');
  const title = document.getElementById('draft-modal-title');
  const metadata = CLUSTER_METADATA[groupName][clusterId];

  title.innerHTML = `Opciones para <span style="color: var(--accent-gold);">${metadata.name}</span>`;
  container.innerHTML = '';

  const players = state.appData.clusters[groupName].filter(p => p.cluster_id == clusterId);

  // Sort descending by overall (handling missing overalls as 0)
  const sorted = players.sort((a, b) => (b.overall || 0) - (a.overall || 0));

  // Take top 10 players
  const top10 = sorted.slice(0, 10);

  // Shuffle the top 10
  const shuffled = top10.sort(() => 0.5 - Math.random());

  // Select 3 to display
  const selected = shuffled.slice(0, 3);

  selected.forEach((player, index) => {
    const photoUrl = player.photoUrl || getPlayerPhoto(player.long_name);

    const wrapper = document.createElement('div');
    wrapper.style.animation = `smoothFadeInUp 2.5s cubic-bezier(0.22, 1, 0.36, 1) ${index * 0.5}s both`;

    const card = document.createElement('div');
    card.className = 'fut-card-large';
    card.innerHTML = `
      <div class="fut-card-large-top">
        <div class="fut-card-large-pos">${slotId.toUpperCase().replace(/[0-9]/g, '')}</div>
      </div>
      <img src="${photoUrl}" class="fut-card-large-face" onerror="this.src='https://cdn.sofifa.net/players/notfound_0_120.png'" alt="Face">
      <div class="fut-card-large-bottom">
        <div class="fut-card-large-name" title="${player.long_name}">${player.long_name.split(' ').slice(-1).join('')}</div>
      </div>
    `;

    card.addEventListener('click', () => selectPlayer(player));
    wrapper.appendChild(card);
    container.appendChild(wrapper);
  });
}

function selectPlayer(player) {
  draftedPlayers[currentActiveSlot] = player;
  const photoUrl = player.photoUrl || getPlayerPhoto(player.long_name);

  const slotEl = document.querySelector(`.draft-slot[data-id="${currentActiveSlot}"]`);
  if (slotEl) {
    slotEl.classList.add('filled');
    slotEl.classList.add('stamp-anim'); // Apply stamp animation
    setTimeout(() => slotEl.classList.remove('stamp-anim'), 600); // Remove after animation so hover works
    slotEl.style.border = 'none';
    slotEl.style.background = 'transparent';
    slotEl.innerHTML = `
      <div class="fut-card-container">
        <div class="fut-card-top" style="padding: 10px 10px 0 10px;">
          <div class="fut-card-rating" style="align-items: flex-start;">
            <span class="fut-card-pos" style="font-size: 0.6rem;">${currentActiveSlot.toUpperCase().replace(/[0-9]/g, '')}</span>
          </div>
        </div>
        <img src="${photoUrl}" class="fut-card-face" onerror="this.src='https://cdn.sofifa.net/players/notfound_0_120.png'">
        <div class="fut-card-bottom">
          <div class="fut-card-name" title="${player.long_name}">${player.long_name.split(' ').slice(-1).join('')}</div>
        </div>
      </div>
    `;
  }

  document.getElementById('draft-modal').classList.remove('active');

  updateDraftState();
  checkDraftCompletion();
}

function checkDraftCompletion() {
  const layout = formations[currentFormation];
  if (Object.keys(draftedPlayers).length === layout.length) {
    completeDraft();
  }
}

function completeDraft() {
  const summary = document.getElementById('draft-summary-banner');
  const resultBadge = document.getElementById('draft-tactical-result');

  summary.classList.remove('draft-summary-hidden');
  summary.classList.add('show-summary-anim'); // Apply slide down animation

  const archetypes = state.appData.arquetipos;
  let bestArch = null;

  if (archetypes && currentArchetype) {
    bestArch = archetypes.find(a => a.id === currentArchetype);
  }
  if (!bestArch && archetypes && archetypes.length > 0) {
    bestArch = archetypes[0];
  }

  const explanationText = document.getElementById('draft-tactical-explanation');

  // Push drafted players to favoritePlayers so the recommender can find them
  state.userPreferences.favoritePlayers = Object.values(draftedPlayers).map(p => p.long_name);

  if (bestArch) {
    resultBadge.textContent = `${bestArch.title}`;
    state.userPreferences.tacticalVector = bestArch.vector;

    if (explanationText) {
      const ritmoDesc = draftedVector.ritmo > 0.1 ? 'alto ritmo y transiciones rápidas' : (draftedVector.ritmo < -0.1 ? 'juego pausado y de control' : 'ritmo equilibrado');
      const posDesc = draftedVector.posesion > 0.1 ? 'buen toque y visión' : (draftedVector.posesion < -0.1 ? 'estilo más directo' : 'posesión balanceada');
      const defDesc = draftedVector.defensa > 0.1 ? 'mucha agresividad en la recuperación' : (draftedVector.defensa < -0.1 ? 'solidez en bloque bajo' : 'esfuerzo defensivo estándar');
      const anchoDesc = draftedVector.ancho > 0 ? 'aprovechando las bandas' : 'concentrando el juego por el centro';

      explanationText.innerHTML = `Tus jugadores promedian características de <b>${ritmoDesc}</b>, <b>${posDesc}</b>, y <b>${defDesc}</b>. Combinado con tu formación ${currentFormation} (<b>${anchoDesc}</b>), esto encaja perfectamente con la filosofía del <b>${bestArch.title}</b>.`;
    }
  } else {
    resultBadge.textContent = "Estilo Mixto";
    state.userPreferences.tacticalVector = draftedVector;
    if (explanationText) {
      explanationText.innerHTML = `Tus jugadores tienen características muy variadas que no encajan en un arquetipo puro. Jugaremos con un Estilo Mixto.`;
    }
  }
}
