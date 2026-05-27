import json

data = json.load(open('data/wc2026_data.json', encoding='utf-8'))
team = data['teams']['ARG']

def getPosCategory(p):
    pos = (p.get('position') or '').lower()
    if 'portero' in pos or 'arquero' in pos or 'goalkeeper' in pos: return 'GK'
    if 'delantero' in pos or 'extremo' in pos or 'atacante' in pos or 'forward' in pos or 'winger' in pos: return 'FWD'
    if 'centrocampista' in pos or 'medio' in pos or 'volante' in pos or 'pivote' in pos or 'midfielder' in pos: return 'MID'
    if 'defensa' in pos or 'lateral' in pos or 'central' in pos or 'carrilero' in pos or 'defender' in pos: return 'DEF'
    return 'MID'

available = [p for p in team['squad'] if not p.get('is_injured')]
byPos = {'GK': [], 'DEF': [], 'MID': [], 'FWD': []}
for p in available:
    byPos[getPosCategory(p)].append(p)

for cat in byPos:
    byPos[cat].sort(key=lambda p: p.get('market_value_eur') or 0, reverse=True)

def pickBestForRoles(pool, roles, count):
    selected = []
    remainingPool = pool.copy()
    for role in roles:
        match_idx = -1
        for i, p in enumerate(remainingPool):
            if p.get('exact_position') == role:
                match_idx = i
                break
        if match_idx >= 0:
            selected.append(remainingPool.pop(match_idx))
        else:
            fallback_idx = -1
            clean_role = role.replace('B','').replace('M','').replace('W','')
            for i, p in enumerate(remainingPool):
                exact = p.get('exact_position') or ''
                if clean_role in exact or exact.endswith(role[-1:]):
                    fallback_idx = i
                    break
            if fallback_idx >= 0:
                selected.append(remainingPool.pop(fallback_idx))
            else:
                if remainingPool:
                    selected.append(remainingPool.pop(0))
    while len(selected) < count and remainingPool:
        selected.append(remainingPool.pop(0))
    return selected

defenders = pickBestForRoles(byPos['DEF'], ['LB', 'LCB', 'RCB', 'RB'], 4)
print("Defenders selected:", [(d['name'], d.get('exact_position'), d.get('market_value_eur')) for d in defenders])
