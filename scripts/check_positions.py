import json

data = json.load(open('data/wc2026_data.json', encoding='utf-8'))
for code in ['ESP', 'FRA', 'JPN', 'BRA']:
    if code in data['teams']:
        team = data['teams'][code]
        print(f"--- {team['name']} ---")
        squad = sorted(team['squad'], key=lambda x: x.get('market_value_eur') or 0, reverse=True)[:6]
        for p in squad:
            print(f"{p['name']}: {p.get('exact_position')}")
