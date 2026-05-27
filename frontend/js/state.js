// state.js
let appData = null;
let activeTab = localStorage.getItem('activeTab') || 'recommender';
let selectedCountryCode = null;
let userPreferences = {
  favoriteTeam: '',
  matchStyle: 'all', // 'all', 'closed', 'chaotic'
  favoritePlayers: [],
  preferredTime: [] // array of 'morning', 'afternoon', 'evening'
};

export async function loadData() {
  try {
    const [mainRes, logosRes] = await Promise.all([
      fetch(`data/wc2026_data.json?t=${new Date().getTime()}`),
      fetch(`data/club_logos.json?t=${new Date().getTime()}`)
    ]);
    state.appData = await mainRes.json();
    state.appData.clubLogos = await logosRes.json();
    console.log('Main data loaded:', state.appData);
    console.log('Club logos loaded:', Object.keys(state.appData.clubLogos).length);
  } catch (err) {
    console.error('Error loading data:', err);
  }
}

export const state = {
  get appData() { return appData; },
  set appData(val) { appData = val; },
  get activeTab() { return activeTab; },
  set activeTab(val) { 
    activeTab = val; 
    localStorage.setItem('activeTab', val);
  },
  get selectedCountryCode() { return selectedCountryCode; },
  set selectedCountryCode(val) { selectedCountryCode = val; },
  get userPreferences() { return userPreferences; },
  set userPreferences(val) { userPreferences = val; }
};
