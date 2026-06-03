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
  'Fullbacks': { 1: 'fb_1.jpg', 2: 'fb_2.jpg', 3: 'fb_3.jpg' },
  'Midfielders': { 1: 'mid_1.jpg', 2: 'mid_2.jpg', 3: 'mid_3.jpg' },
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
  ]
};

let currentFormation = '4-3-3';
let draftedPlayers = {};
let currentActiveSlot = null;
let draftPhase = 0;

const FORMATIONS_HTML = `
  <div class="draft-controls" style="text-align: center;">
    <h3 style="color: var(--text-primary); margin-bottom: 2rem; font-size: 2.5rem; text-shadow: 0 4px 15px rgba(0,0,0,0.8); font-weight: 900;">Seleccioná tu Formación</h3>
    <div class="formation-cards-container" id="formation-cards-container">
      <div class="formation-card active" data-formation="4-3-3">
        <h4>4-3-3</h4>
        <div class="formation-pros-cons">
          <div class="formation-pro"><i class="fas fa-plus"></i> Juego Ofensivo</div>
          <div class="formation-pro"><i class="fas fa-plus"></i> Ataque por Bandas</div>
          <div class="formation-con"><i class="fas fa-minus"></i> Expuesto a contragolpes</div>
        </div>
      </div>
      <div class="formation-card" data-formation="4-4-2">
        <h4>4-4-2</h4>
        <div class="formation-pros-cons">
          <div class="formation-pro"><i class="fas fa-plus"></i> Equilibrio Defensivo</div>
          <div class="formation-pro"><i class="fas fa-plus"></i> Bloque Compacto</div>
          <div class="formation-con"><i class="fas fa-minus"></i> Inferioridad en el medio</div>
        </div>
      </div>
      <div class="formation-card" data-formation="3-5-2">
        <h4>3-5-2</h4>
        <div class="formation-pros-cons">
          <div class="formation-pro"><i class="fas fa-plus"></i> Superioridad en Medio</div>
          <div class="formation-pro"><i class="fas fa-plus"></i> Carrileros Profundos</div>
          <div class="formation-con"><i class="fas fa-minus"></i> Espalda Descubierta</div>
        </div>
      </div>
      <div class="formation-card" data-formation="4-2-3-1">
        <h4>4-2-3-1</h4>
        <div class="formation-pros-cons">
          <div class="formation-pro"><i class="fas fa-plus"></i> Doble Pivote Sólido</div>
          <div class="formation-pro"><i class="fas fa-plus"></i> Transiciones Rápidas</div>
          <div class="formation-con"><i class="fas fa-minus"></i> Dependencia del enganche</div>
        </div>
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
      const originalText = btn.innerHTML;
      btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Reiniciando...';
      btn.style.pointerEvents = 'none';
      btn.style.opacity = '0.8';
      
      setTimeout(() => {
        btn.innerHTML = originalText;
        btn.style.pointerEvents = 'auto';
        btn.style.opacity = '1';
        startDraft(true);
      }, 700);
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

export function startDraft(isInitial = false) {
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
        overlay.innerHTML = FORMATIONS_HTML;
        overlay.style.animation = 'relaxedFadeIn 1s cubic-bezier(0.22, 1, 0.36, 1) forwards';

        document.querySelectorAll('.formation-card').forEach((card, i) => {
          card.style.opacity = '0';
          card.style.animation = `smoothFadeInUp 1s cubic-bezier(0.22, 1, 0.36, 1) ${i * 0.25}s forwards`;

          card.addEventListener('click', (e) => {
            document.querySelectorAll('.formation-card').forEach(c => c.classList.remove('active'));
            const target = e.currentTarget;
            target.classList.add('active');
            currentFormation = target.dataset.formation;

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

  document.querySelectorAll('.draft-slot').forEach(el => {
    const group = el.dataset.group;
    if (activeGroups.includes(group)) {
      if (!draftedPlayers[el.dataset.id]) {
        el.classList.remove('locked');
        el.classList.add('highlighted');
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
}

function getPlayerPhoto(name) {
  if (!state.appData || !state.appData.photoIndex) return 'https://cdn.sofifa.net/players/notfound_0_120.png';

  const robustNormalise = str => {
    if (!str) return '';
    return str
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/ø/gi, 'o').replace(/ð/gi, 'd').replace(/þ/gi, 'th')
      .replace(/æ/gi, 'ae').replace(/ł/gi, 'l').replace(/ß/gi, 'ss').replace(/œ/gi, 'oe')
      .replace(/[^\x00-\x7F]/g, '')
      .toLowerCase().trim();
  };

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

  // Deep fallback: search the full array
  if (state.appData.playersPhotos) {
    const found = state.appData.playersPhotos.find(p => {
      const pN = robustNormalise(p.n);
      const pFn = robustNormalise(p.fn);
      // Try to match last names or full substrings
      return (pN && fn.includes(pN)) || (pFn && fn.includes(pFn)) || (pN && pN.includes(fn)) || (pFn && pFn.includes(fn));
    });
    if (found) return found.p;
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
    const imgName = (GROUP_IMAGES[groupName] && GROUP_IMAGES[groupName][clusterId])
      ? GROUP_IMAGES[groupName][clusterId]
      : 'default.jpg';
    const imgUrl = `assets/images/${imgName}`;

    const card = document.createElement('div');
    card.className = 'archetype-selection-card';
    card.innerHTML = `
      <div class="archetype-img-container" style="background: linear-gradient(to bottom, rgba(15,16,21,0) 0%, #0f1015 100%), url('${imgUrl}') center/cover;">
        <div class="archetype-badge">OPCIÓN 0${index + 1}</div>
      </div>
      <div class="archetype-info">
        <div class="archetype-subtitle">ESTILO ${groupName.slice(0, -1)}</div>
        <h4 class="archetype-title">${archetype.name}</h4>
        <p class="archetype-desc">${archetype.desc}</p>
      </div>
    `;

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
  const shuffled = players.sort(() => 0.5 - Math.random());
  const selected = shuffled.slice(0, 3);

  selected.forEach((player, index) => {
    const photoUrl = getPlayerPhoto(player.long_name);

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
  const photoUrl = getPlayerPhoto(player.long_name);

  const slotEl = document.querySelector(`.draft-slot[data-id="${currentActiveSlot}"]`);
  if (slotEl) {
    slotEl.classList.add('filled');
    slotEl.classList.add('stamp-anim'); // Apply stamp animation
    setTimeout(() => slotEl.classList.remove('stamp-anim'), 600); // Remove after animation so hover works
    slotEl.style.border = 'none';
    slotEl.style.background = 'transparent';
    slotEl.innerHTML = `
      <div class="fut-card-container">
        <div class="fut-card-top">
          <div class="fut-card-rating">
            <span class="fut-card-pos">${currentActiveSlot.toUpperCase().replace(/[0-9]/g, '')}</span>
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

  // Calculate Tactical Vector based on the 11 drafted players
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

  // Map normalized feature values (~0.15) to [-1, 1] range.
  let ritmo = (avgPace - 0.15) * 15;
  let posesion = (avgPassing - 0.15) * 15;
  let defensa = (avgDefending - 0.15) * 15;

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
  }

  const explanationText = document.getElementById('draft-tactical-explanation');

  if (bestArch) {
    resultBadge.textContent = `${bestArch.title} (${Math.round(bestSim * 100)}% match)`;
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
