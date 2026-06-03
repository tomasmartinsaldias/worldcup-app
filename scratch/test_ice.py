import json
import math

def calculateICEScore(match, teams, dramaBeta=0.2):
    home = teams[match['home_team']['fifa_code']]
    away = teams[match['away_team']['fifa_code']]
    hParams = home.get('espectaculo_params') or {'ocasiones_norm': 0.5, 'contra_norm': 0.5, 'drama_norm': 0.5, 'vuln_norm': 0.5}
    aParams = away.get('espectaculo_params') or {'ocasiones_norm': 0.5, 'contra_norm': 0.5, 'drama_norm': 0.5, 'vuln_norm': 0.5}
    alpha = 0.5
    
    ocMatch = (hParams['ocasiones_norm'] + aParams['ocasiones_norm']) / 2
    caMatch = (hParams['contra_norm'] + aParams['contra_norm']) / 2
    dramaMatch = (hParams['drama_norm'] + aParams['drama_norm']) / 2
    vulnMatch = (hParams.get('vuln_norm', 0.5) + aParams.get('vuln_norm', 0.5)) / 2
    
    rHome = home.get('metrics', {}).get('fifa_ranking') or 60
    rAway = away.get('metrics', {}).get('fifa_ranking') or 60
    
    rankingDiff = abs(rHome - rAway)
    rankImpact = 0.6
    pBrecha = 1.0 - (1.0 / (1.0 + rankImpact * math.log(rankingDiff + 1.0)))
    
    ice = ((ocMatch + vulnMatch) + (alpha * caMatch) + (dramaBeta * dramaMatch)) * (1.0 - pBrecha)
    
    ICE_min = 0.1
    T = 0.35 * (2.0 + alpha + dramaBeta) # 0.35 * 2.7 = 0.945
    
    score = 1.0 + 9.0 * ((max(ICE_min, min(ice, T)) - ICE_min) / (T - ICE_min))
    score = min(max(score, 1.0), 10.0)
    return round(score, 1), round(ice, 3), round(pBrecha, 3), rHome, rAway

def main():
    data = json.load(open('data/wc2026_data.json', encoding='utf-8'))
    teams = data['teams']
    
    print("--- TOP MATCHES SPECTACLE SCORES ---")
    count = 0
    for m in data['matches']:
        if not m['home_team']['is_placeholder'] and not m['away_team']['is_placeholder']:
            score, ice, pBrecha, rHome, rAway = calculateICEScore(m, teams)
            print(f"{m['home_team']['name']} (Rank {rHome}) vs {m['away_team']['name']} (Rank {rAway}): Score = {score}, ICE = {ice}, pBrecha = {pBrecha}")
            count += 1
            if count >= 30:
                break

if __name__ == '__main__':
    main()
