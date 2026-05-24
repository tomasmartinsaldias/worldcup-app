// utils.js
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
  } catch(e) {
    return isoStr;
  }
}
