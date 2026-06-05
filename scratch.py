import json
import math
import numpy as np

# Load files
with open('frontend/data/wc2026_data.json', 'r', encoding='utf-8') as f:
    wc_data = json.load(f)

with open('frontend/data/estilos-de-juego/selecciones_estilo', 'r', encoding='utf-8') as f:
    selecciones_estilo = json.load(f)

with open('frontend/data/estilos-de-juego/arquetipos', 'r', encoding='utf-8') as f:
    arquetipos_data = json.load(f)

# Mock state/preferences
userPreferences = {
    "favoriteTeams": ["ARG"],
    "favoritePlayers": ["Lionel Messi"],
    "favoriteClubs": [],
    "w_espectaculo": 5,
    "w_tactica": 5,
    "w_afectivo": 5,
    "w_friccion": 0,
    "frictionPreference": "indiferente",
    "tacticalVector": {"defensa": 0.5, "posesion": 0.5, "ritmo": 0.5, "ancho": 0.5}  # From draft
}

teams = wc_data['teams']

# Map team styles like in main.js
normalise_str = lambda s: s.lower().strip()
fifaToSpanish = { "ARG": "argentina", "BRA": "brasil", "FRA": "francia", "GER": "alemania", "ESP": "espana" } # simplified
estiloMap = {normalise_str(item['equipo']): item for item in selecciones_estilo['response']}

for code, team in teams.items():
    key = fifaToSpanish.get(code) or normalise_str(team['name'])
    if key in estiloMap:
        team['tactical_vector'] = estiloMap[key]['vector']
    else:
        team['tactical_vector'] = {"defensa": 0.0, "posesion": 0.0, "ritmo": 0.0, "ancho": 0.0}

# Scoring Functions mirroring scoring.js

ICE_CONFIG = {
  "alpha": 0.5,
  "gamma": 0.5,
  "ICE_min": 0.1,
  "T_SCALE": 0.65,
  "P_MAX": 0.60,
  "R_MID": 350,
  "K_STEEPNESS": 0.01,
  "B_MAX": 0.15,
  "K_SAT": 5
}

def calculateCosineSimilarity(v1, v2):
    keys = ['defensa', 'posesion', 'ritmo', 'ancho']
    dotProduct = 0
    norm1Sq = 0
    norm2Sq = 0
    for k in keys:
        val1 = v1.get(k, 0)
        val2 = v2.get(k, 0)
        dotProduct += val1 * val2
        norm1Sq += val1 * val1
        norm2Sq += val2 * val2
    if norm1Sq == 0 or norm2Sq == 0:
        return 0
    return dotProduct / (math.sqrt(norm1Sq) * math.sqrt(norm2Sq))

def getTeamMaxMarketValue(team):
    squad = team.get('squad', [])
    if not squad: return 0
    return max([p.get('market_value_eur', 0) for p in squad])

def getSeleccionTotalMinutes(teamCode):
    if teamCode == 'CAN': return 360
    if teamCode in ['MEX', 'USA']: return 540
    conmebol = ['ARG', 'BRA', 'URU', 'COL', 'ECU', 'PAR', 'CHI', 'VEN', 'BOL', 'PER']
    if teamCode in conmebol: return 18 * 90
    return 10 * 90

def calculatePJuego(player, teamCode, teamMaxVal):
    if player.get('is_star_player') and not player.get('is_injured', False):
        return 1.0
    mins = player.get('minutes_recent', 0)
    if mins and mins > 0:
        totalMins = getSeleccionTotalMinutes(teamCode)
        return min(1.0, mins / totalMins)
    if teamMaxVal and teamMaxVal > 0:
        return min(1.0, player.get('market_value_eur', 0) / teamMaxVal)
    return 0.0

def calculateSSel(homeCode, awayCode):
    favTeams = userPreferences.get('favoriteTeams', [])
    if not favTeams: return 0.0
    primary = favTeams[0]
    secondary = favTeams[1:]
    I_p = 1 if primary and (homeCode == primary or awayCode == primary) else 0
    n_m = sum([1 for code in secondary if code and (homeCode == code or awayCode == code)])
    if I_p == 1: return 1.0
    if n_m > 0: return min(1.0, 0.5 * n_m)
    return 0.0

def calculateSJug(homeTeam, awayTeam):
    favPlayers = userPreferences.get('favoritePlayers', [])
    if not favPlayers: return 0.0
    
    # Simple check for matches with favorite players
    J_d = 0.0
    
    def process(team):
        nonlocal J_d
        squad = team.get('squad', [])
        max_val = getTeamMaxMarketValue(team)
        for p in squad:
            p_name_norm = normalise_str(p['name'])
            is_fav = any(normalise_str(fp) == p_name_norm or normalise_str(fp) in p_name_norm for fp in favPlayers)
            if is_fav:
                J_d += calculatePJuego(p, team['fifa_code'], max_val)
                
    process(homeTeam)
    process(awayTeam)
    
    term_d = math.log1p(J_d) / math.log(2.0)
    return min(1.0, term_d)

def calculateICEScore(match, home, away):
    hParams = home.get('espectaculo_params', {"ocasiones_norm": 0.5, "contra_norm": 0.5, "drama_norm": 0.5, "vuln_norm": 0.5})
    aParams = away.get('espectaculo_params', {"ocasiones_norm": 0.5, "contra_norm": 0.5, "drama_norm": 0.5, "vuln_norm": 0.5})
    
    ocMatch = (hParams.get('ocasiones_norm', 0.5) + aParams.get('ocasiones_norm', 0.5)) / 2
    caMatch = (hParams.get('contra_norm', 0.5) + aParams.get('contra_norm', 0.5)) / 2
    vulnMatch = (hParams.get('vuln_norm', 0.5) + aParams.get('vuln_norm', 0.5)) / 2
    
    homeEloBase = home.get('metrics', {}).get('elo_rating', 1500)
    awayEloBase = away.get('metrics', {}).get('elo_rating', 1500)
    
    rankingDiff = abs(homeEloBase - awayEloBase)
    pBrecha = ICE_CONFIG['P_MAX'] / (1 + math.exp(-ICE_CONFIG['K_STEEPNESS'] * (rankingDiff - ICE_CONFIG['R_MID'])))
    
    gamma = ICE_CONFIG['gamma']
    alpha = ICE_CONFIG['alpha']
    ice = ((ocMatch * (1 + gamma * vulnMatch)) + (alpha * caMatch)) * (1 - pBrecha)
    
    ICE_min = ICE_CONFIG['ICE_min']
    T = ICE_CONFIG['T_SCALE'] * (1.5 + alpha)
    score = 1 + 9 * ((max(ICE_min, min(ice, T)) - ICE_min) / (T - ICE_min))
    
    avgElo = (homeEloBase + awayEloBase) / 2
    qMatch = max(0.60, min(1.0, 0.60 + 0.40 * ((avgElo - 1400) / 700)))
    score = score * qMatch
    
    if match['stage'] == 'Group Stage':
        score = score * 1.0 # default stake
        
    return min(max(score, 1.0), 10.0)

def simulate_match_score(match):
    home_code = match['home_team']['fifa_code']
    away_code = match['away_team']['fifa_code']
    
    home = teams.get(home_code)
    away = teams.get(away_code)
    if not home or not away: return None
    
    ice = calculateICEScore(match, home, away)
    
    vectorA = home.get('tactical_vector', {"defensa": 0, "posesion": 0, "ritmo": 0, "ancho": 0})
    vectorB = away.get('tactical_vector', {"defensa": 0, "posesion": 0, "ritmo": 0, "ancho": 0})
    vectorU = userPreferences['tacticalVector']
    
    simA = calculateCosineSimilarity(vectorA, vectorU)
    simB = calculateCosineSimilarity(vectorB, vectorU)
    rawPlaystyle = max(simA, simB) + 0.1 * min(simA, simB)
    playstyleScore = 10.0 * ((rawPlaystyle + 1.1) / 2.2)
    playstyleScore = min(max(playstyleScore, 0.0), 10.0)
    
    s_club = 0.0
    s_sel = calculateSSel(home_code, away_code)
    s_jug = calculateSJug(home, away)
    
    # Check if this specific match has any affective relevance
    has_affective_relevance = (s_sel > 0 or s_jug > 0 or s_club > 0)
    
    # Calculate s_afectivo
    s_afectivo = (0.4 * s_sel + 0.3 * s_jug) / 0.7 * 10.0 if has_affective_relevance else 0.0
    
    w_esp = userPreferences['w_espectaculo']
    w_tac = userPreferences['w_tactica']
    w_afec = userPreferences['w_afectivo'] if has_affective_relevance else 0
    
    w_sum = w_esp + w_tac + w_afec
    
    combinedScore = (w_esp/w_sum * ice) + (w_tac/w_sum * playstyleScore)
    if has_affective_relevance:
        combinedScore += (w_afec/w_sum * s_afectivo)
    
    return {
        "teams": f"{home['name']} vs {away['name']}",
        "ice_spectacle": round(ice, 2),
        "playstyle": round(playstyleScore, 2),
        "s_sel": round(s_sel, 2),
        "s_jug": round(s_jug, 2),
        "s_afectivo": round(s_afectivo, 2),
        "combined": round(combinedScore, 2)
    }

# Run simulation for Argentina matches
print("Argentina matches in tournament:")
for match in wc_data['matches']:
    if match['home_team']['fifa_code'] == 'ARG' or match['away_team']['fifa_code'] == 'ARG':
        res = simulate_match_score(match)
        if res:
            print(res)

print("\nOther match (e.g. GER vs SCO):")
for match in wc_data['matches']:
    if match['home_team']['fifa_code'] == 'GER' and match['away_team']['fifa_code'] == 'SCO':
        res = simulate_match_score(match)
        if res:
            print(res)
