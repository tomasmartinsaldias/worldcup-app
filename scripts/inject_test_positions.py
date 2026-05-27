import json
import os

JSON_PATH = 'data/wc2026_data.json'
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Japan (3-4-2-1)
jap_map = {
    'Zion Suzuki': 'GK',
    'Kō Itakura': 'RCB',
    'Tsuyoshi Watanabe': 'CB',
    'Hiroki Itō': 'LCB',
    'Wataru Endō': 'RCM',
    'Ao Tanaka': 'RCM',
    'Hidemasa Morita': 'LCM',
    'Daichi Kamada': 'LCM',
    'Ritsu Dōan': 'RM',
    'Keito Nakamura': 'LM',
    'Takefusa Kubo': 'RAM',
    'Takumi Minamino': 'LAM',
    'Ayase Ueda': 'ST',
    'Kaishu Sano': 'CM',
    'Yuito Suzuki': 'ST'
}

# Argentina (4-4-2)
arg_map = {
    'Emiliano Martínez': 'GK',
    'Nahuel Molina': 'RB',
    'Cristian Romero': 'RCB',
    'Lisandro Martínez': 'LCB',
    'Nicolás Tagliafico': 'LB',
    'Valentín Barco': 'LB',
    'Rodrigo De Paul': 'RM',
    'Enzo Fernández': 'RCM',
    'Alexis Mac Allister': 'LCM',
    'Nicolás González': 'LM',
    'Lionel Messi': 'RS',
    'Lautaro Martínez': 'LS',
    'Julián Alvarez': 'ST',
    'Nico Paz': 'CAM',
    'Exequiel Palacios': 'CM',
    'Marcos Senesi': 'CB'
}

# Morocco (4-1-4-1)
mar_map = {
    'Achraf Hakimi': 'RB',
    'Yassine Bounou': 'GK',
    'Noussair Mazraoui': 'LB',
    'Nayef Aguerd': 'LCB',
    'Romain Saïss': 'RCB',
    'Sofyan Amrabat': 'CDM',
    'Azzedine Ounahi': 'RCM',
    'Hakim Ziyech': 'RM',
    'Brahim Díaz': 'CAM',
    'Youssef En-Nesyri': 'ST'
}

for code, team in data['teams'].items():
    if code == 'JPN':
        for p in team.get('squad', []):
            if p['name'] in jap_map: p['exact_position'] = jap_map[p['name']]
    elif code == 'ARG':
        for p in team.get('squad', []):
            if p['name'] in arg_map: p['exact_position'] = arg_map[p['name']]
    elif code == 'MAR':
        for p in team.get('squad', []):
            if p['name'] in mar_map: p['exact_position'] = mar_map[p['name']]

with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("Test positions injected successfully.")
