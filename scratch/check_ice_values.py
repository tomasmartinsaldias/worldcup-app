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
        
        ice = ((ocMatch + vulnMatch) + (alpha * caMatch) + (dramaBeta * dramaMatch)) * (1 - pBrecha)
        
        score_base = 1 + 9 * ((max(ICE_min, min(ice, T)) - ICE_min) / (T - ICE_min))
        
        gamma = 0.15
        homeStars = len([p for p in home.get('squad', []) if p.get('is_star_player')])
        awayStars = len([p for p in away.get('squad', []) if p.get('is_star_player')])
        starCount = homeStars + awayStars
        spectacleScore = score_base + (gamma * starCount)
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
    results.sort(key=lambda x: x['spectacleScore'], reverse=True)
    for r in results[:20]:
        print(f"{r['match']}: base={r['score_base']:.2f}, stars={r['starCount']}, final={r['spectacleScore']:.2f}, ice={r['ice']:.3f}, pBrecha={r['pBrecha']:.3f}")

if __name__ == '__main__':
    run()
