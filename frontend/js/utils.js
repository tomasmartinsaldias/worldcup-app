import { state } from './state.js';

export function getCountryIsoCode(fifaCode) {
  const mapping = {
    'ARG': 'ar', 'BRA': 'br', 'FRA': 'fr', 'ENG': 'gb-eng', 'ESP': 'es', 'GER': 'de', 'POR': 'pt',
    'URU': 'uy', 'NED': 'nl', 'CRO': 'hr', 'JPN': 'jp', 'USA': 'us', 'MEX': 'mx', 'MAR': 'ma',
    'COL': 'co', 'BEL': 'be', 'NOR': 'no', 'SEN': 'sn', 'EGY': 'eg', 'SWE': 'se', 'KOR': 'kr',
    'TUR': 'tr', 'SUI': 'ch', 'CAN': 'ca', 'ECU': 'ec', 'AUT': 'at', 'ALG': 'dz', 'CIV': 'ci',
    'SCO': 'gb-sct', 'AUS': 'au', 'GHA': 'gh', 'KSA': 'sa', 'PAR': 'py', 'CZE': 'cz', 'COD': 'cd',
    'BIH': 'ba', 'CPV': 'cv', 'TUN': 'tn', 'IRQ': 'iq', 'RSA': 'za', 'UZB': 'uz', 'QAT': 'qa',
    'NZL': 'nz', 'JOR': 'jo', 'PAN': 'pa', 'HAI': 'ht', 'CUR': 'cw', 'POL': 'pl', 'SRB': 'rs',
    'CMR': 'cm', 'CRC': 'cr', 'DEN': 'dk', 'WAL': 'gb-wls'
  };
  return mapping[fifaCode] || 'un';
}

export function getFlagUrl(fifaCode) {
  if (!fifaCode) return '';
  return `https://images.tomas.me/flags/${fifaCode.toLowerCase()}.png`;
}

export function createFlagElement(team) {
  if (team.is_placeholder) {
    return `<div class="team-flag-placeholder"><i class="fa-solid fa-hourglass-half"></i></div>`;
  }
  const code = team.fifa_code;
  const flagUrl = `https://flagcdn.com/w40/${getCountryIsoCode(code)}.png`;
  return `<img src="${flagUrl}" class="team-flag-real" onerror="this.outerHTML='<div class=team-flag-placeholder>${code}</div>'">`;
}

export function formatKickoff(isoStr) {
  if (!isoStr) return 'TBD';
  try {
    const d = new Date(isoStr);
    return d.toLocaleString('es-ES', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) + ' hs';
  } catch (e) {
    return isoStr;
  }
}

// Manual overrides: name as it appears in wc2026_data.json -> name as it appears in players_photos.json fn field
const PHOTO_OVERRIDES = {
  'erling braut haaland': 'Erling Braut Håland',
  'martin odegaard': 'Martin Ødegaard',
  'marko arnautovic': 'Marko Arnautović',
  'dominik livakovic': 'Dominik Livaković',
  'noni madueke': 'Chukwunonso Tristan Madueke',
  'ollie watkins': 'Oliver George Arthur Watkins',
  'james rodriguez': 'James Rodríguez',
  'florian grillitsch': 'Florian Grillitsch',
  'michael gregoritsch': 'Michael Gregoritsch',
  'rayan ait-nouri': 'Rayan Aït-Nouri',
  'leo ostigard': 'Leo Skiri Østigård',
  'orjan haskjold nyland': 'Ørjan Nyland',
  'jorge carrascal': 'Jorge Daniel Carrascal Díaz',
  'willer ditta': 'Willer Alexander Ditta Domínguez',
  'yohan mojica': 'Yohan Steven Mojica Palacio',
  'camilo vargas': 'Camilo Andrés Vargas Mojica',
};

function robustNormalise(str) {
  if (!str) return '';
  return str
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')   // remove combining accents
    .replace(/ø/gi, 'o')
    .replace(/ð/gi, 'd')
    .replace(/þ/gi, 'th')
    .replace(/æ/gi, 'ae')
    .replace(/ł/gi, 'l')
    .replace(/ß/gi, 'ss')
    .replace(/œ/gi, 'oe')
    .replace(/[^\x00-\x7F]/g, '')     // strip any remaining non-ASCII
    .toLowerCase()
    .trim();
}

export function getPlayerPhotoUrl(playerName) {
  if (!playerName || !state.appData || !state.appData.photoIndex) {
    return null;
  }
  const normName = robustNormalise(playerName);

  // 1. Direct index lookup
  if (state.appData.photoIndex[normName]) {
    return state.appData.photoIndex[normName];
  }

  // 2. Manual override lookup
  if (PHOTO_OVERRIDES[normName] && state.appData.playersPhotos) {
    const overrideName = robustNormalise(PHOTO_OVERRIDES[normName]);
    const match = state.appData.playersPhotos.find(p => robustNormalise(p.fn || '') === overrideName);
    if (match) {
      state.appData.photoIndex[normName] = match.p;
      return match.p;
    }
  }

  // 3. Fuzzy fallback: all tokens must appear in fn
  if (state.appData.playersPhotos && state.appData.playersPhotos.length > 0) {
    const tokens = normName.split(' ').filter(t => t.length > 1);
    const match = state.appData.playersPhotos.find(p => {
      const fn = robustNormalise(p.fn || '');
      return tokens.every(t => fn.includes(t));
    });
    if (match) {
      state.appData.photoIndex[normName] = match.p;
      return match.p;
    }
  }

  return null;
}
