import json
import os

def get_pos_category(p):
    pos = (p.get('position', '') or '').lower()
    if 'portero' in pos or 'goalkeeper' in pos: return 'GK'
    if 'delantero' in pos or 'extremo' in pos or 'atacante' in pos or 'forward' in pos or 'winger' in pos: return 'FWD'
    if 'centrocampista' in pos or 'medio' in pos or 'volante' in pos or 'pivote' in pos or 'midfielder' in pos: return 'MID'
    if 'defensa' in pos or 'lateral' in pos or 'central' in pos or 'carrilero' in pos or 'defender' in pos: return 'DEF'
    return 'MID'

def pick_best_for_roles(pool, roles, count):
    selected = []
    remaining_pool = list(pool)
    for role in roles:
        match_idx = -1
        for i, p in enumerate(remaining_pool):
            if p.get('exact_position') == role:
                match_idx = i
                break
        
        if match_idx >= 0:
            selected.append(remaining_pool.pop(match_idx))
        else:
            fallback_idx = -1
            clean_role = role.replace('B','').replace('M','').replace('W','')
            end_char = role[-1] if len(role) > 0 else ''
            
            for i, p in enumerate(remaining_pool):
                ep = p.get('exact_position') or ''
                if clean_role in ep or ep.endswith(end_char):
                    fallback_idx = i
                    break
            
            if fallback_idx >= 0:
                selected.append(remaining_pool.pop(fallback_idx))
            else:
                if len(remaining_pool) > 0:
                    selected.append(remaining_pool.pop(0))
                    
    while len(selected) < count and len(remaining_pool) > 0:
        selected.append(remaining_pool.pop(0))
        
    return selected

def audit_teams():
    with open('data/wc2026_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    KNOWN_FORMATIONS = {
      'ARG': '4-4-2', 'FRA': '4-2-3-1', 'BRA': '4-2-3-1', 'ENG': '4-2-3-1', 'ESP': '4-3-3',
      'GER': '4-2-3-1', 'POR': '4-3-3', 'BEL': '4-2-3-1', 'NED': '4-3-3', 'ITA': '4-3-3',
      'URU': '4-2-3-1', 'COL': '4-2-3-1', 'USA': '4-3-3', 'MEX': '4-3-3', 'JPN': '4-2-3-1',
      'MAR': '4-3-3', 'SEN': '4-3-3', 'KOR': '4-4-2', 'CRO': '4-3-3', 'SUI': '3-4-3',
      'ECU': '4-3-3'
    }

    DEF_ROLES = { 3: ['LCB', 'CB', 'RCB'], 4: ['LB', 'LCB', 'RCB', 'RB'], 5: ['LWB', 'LCB', 'CB', 'RCB', 'RWB'] }
    MID_ROLES = { 3: ['LCM', 'CDM', 'RCM'], 4: ['LM', 'LCM', 'RCM', 'RM'], 5: ['LM', 'LCM', 'CDM', 'RCM', 'RM'] }
    FWD_ROLES = { 1: ['ST'], 2: ['LS', 'RS'], 3: ['LW', 'ST', 'RW'] }

    output = []
    
    for code, team in data['teams'].items():
        if team.get('is_placeholder'): continue
        
        fifa_code = team.get('fifa_code') or code
        preferred = KNOWN_FORMATIONS.get(fifa_code, '4-3-3')
        slots = [int(x) for x in preferred.split('-')]
        need_def = slots[0] if len(slots)>0 else 4
        need_mid = slots[1] if len(slots)>1 else 3
        need_fwd = sum(slots[2:]) if len(slots)>2 else 3
        
        available = [p for p in team.get('squad', []) if not p.get('is_injured')]
        by_pos = {'GK': [], 'DEF': [], 'MID': [], 'FWD': []}
        
        for p in available:
            cat = get_pos_category(p)
            by_pos[cat].append(p)
            
        for k in by_pos:
            by_pos[k].sort(key=lambda x: x.get('market_value_eur') or 0, reverse=True)
            
        starters = []
        starters.extend(by_pos['GK'][:1])
        
        defs = pick_best_for_roles(by_pos['DEF'], DEF_ROLES.get(need_def, []), need_def)
        starters.extend(defs)
        
        mids = pick_best_for_roles(by_pos['MID'], MID_ROLES.get(need_mid, []), need_mid)
        starters.extend(mids)
        
        fwds = pick_best_for_roles(by_pos['FWD'], FWD_ROLES.get(need_fwd, []), need_fwd)
        starters.extend(fwds)
        
        output.append(f"=== {team['name']} ({preferred}) ===")
        output.append(f"GK: {starters[0]['name'] if len(starters)>0 else '-'}")
        output.append(f"DEF ({need_def}): " + ", ".join([f"{p['name']} ({p.get('exact_position') or '?'})" for p in defs]))
        output.append(f"MID ({need_mid}): " + ", ".join([f"{p['name']} ({p.get('exact_position') or '?'})" for p in mids]))
        output.append(f"FWD ({need_fwd}): " + ", ".join([f"{p['name']} ({p.get('exact_position') or '?'})" for p in fwds]))
        output.append("")

    with open('audit_output.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(output))

if __name__ == '__main__':
    audit_teams()
