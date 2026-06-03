import json
import os
import re

def check_mexico():
    with open('data/wc2026_data.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    json_teams = json_data.get('teams', {})
    mex_json = json_teams['MEX']['squad']
    mex_json_names = [p['name'] for p in mex_json]
    
    print("\n--- MEXICO IN JSON (APP) ---")
    print(len(mex_json_names), mex_json_names)

if __name__ == '__main__':
    check_mexico()
