import json
import math

def run():
    data = json.load(open('data/wc2026_data.json', encoding='utf-8'))
    teams = data['teams']
    matches = data['matches']

    alpha = 0.5
    dramaBeta = 0.2
    ICE_min = 0.1
    P_MAX = 0.60
    R_MID = 35
    K_STEEPNESS = 0.1
    T = 0.65 * (2.0 + alpha + dramaBeta)

    results = []
    for m in matches:
        if m['home_team'].get('is_placeholder') or m['away_team'].get('is_placeholder'):
            continue
        h_code = m['home_team']['fifa_code']
        a_code = m['away_team']['fifa_code']
        home = teams[h_code]
        away = teams[a_code]
        
        hParams = home.get('espectaculo_params', {'ocasiones_norm': 0.5, 'contra_norm': 0.5, 'drama_norm': 0.5, 'vuln_norm': 0.5})
        aParams = away.get('espectaculo_params', {'ocasiones_norm': 0.5, 'contra_norm': 0.5, 'drama_norm': 0.5, 'vuln_norm': 0.5})
        
        ocMatch = (hParams.get('ocasiones_norm', 0.5) + aParams.get('ocasiones_norm', 0.5)) / 2
        caMatch = (hParams.get('contra_norm', 0.5) + aParams.get('contra_norm', 0.5)) / 2
        dramaMatch = (hParams.get('drama_norm', 0.5) + aParams.get('drama_norm', 0.5)) / 2
        vulnMatch = (hParams.get('vuln_norm', 0.5) + aParams.get('vuln_norm', 0.5)) / 2
        
        rHome = home.get('metrics', {}).get('fifa_ranking', 60)
        rAway = away.get('metrics', {}).get('fifa_ranking', 60)
        
        rankingDiff = abs(rHome - rAway)
        pBrecha = P_MAX / (1 + math.exp(-K_STEEPNESS * (rankingDiff - R_MID)))
        
        gamma = 0.5
        ice = ((ocMatch * (1 + gamma * vulnMatch)) + (alpha * caMatch) + (dramaBeta * dramaMatch)) * (1 - pBrecha)
        
        T = 0.60 * (1.5 + alpha + dramaBeta)
        score_base = 1 + 9 * ((max(ICE_min, min(ice, T)) - ICE_min) / (T - ICE_min))
        
        homeStars = len([p for p in home.get('squad', []) if p.get('is_star_player')])
        awayStars = len([p for p in away.get('squad', []) if p.get('is_star_player')])
        starCount = homeStars + awayStars
        
        B_MAX = 0.12
        K_SAT = 5
        bonusPct = B_MAX * (starCount / (starCount + K_SAT)) if starCount > 0 else 0
        spectacleScore = score_base * (1 + bonusPct)
        spectacleScore = min(max(spectacleScore, 1.0), 10.0)
        
        results.append({
            'match': f"{home['name']} vs {away['name']}",
            'rankingDiff': rankingDiff,
            'pBrecha': pBrecha,
            'ice': ice,
            'score_base': score_base,
            'starCount': starCount,
            'spectacleScore': spectacleScore
        })

    # Sort by spectacleScore descending
    for idx, r in enumerate(sorted(results, key=lambda x: x['spectacleScore'], reverse=True)):
        print(f"{idx+1:02d}: {r['match']}: final={r['spectacleScore']:.1f} (base={r['score_base']:.1f}, stars={r['starCount']})")

if __name__ == '__main__':
    run()
