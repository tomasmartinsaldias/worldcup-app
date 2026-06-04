import os
import re
import json

DATA_DIR = '../data/selecciones-sofascore'
OUTPUT_FILE = '../data/selecciones_vectors.json'

def parse_txt_file(filepath):
    stats = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract team name (first line)
    match = re.search(r'^(.*?)(?:\s*\(.*?\))?:', content)
    if match:
        stats['name'] = match.group(1).strip()
    else:
        stats['name'] = os.path.basename(filepath).split('(')[0].strip()

    # Define regex patterns for metrics
    patterns = {
        'golesPartido': r'Goals per game:\s*([\d.]+)',
        'posesion': r'Ball possession:\s*([\d.]+)%',
        'regates': r'Succ\. dribbles per game:\s*([\d.]+)',
        'tirosPartido': r'Total shots per game:\s*([\d.]+)',
        'faltasPartido': r'Fouls per game:\s*([\d.]+)',
        'yellowCards': r'Yellow cards per game:\s*([\d.]+)',
        'redCards': r'Red cards:\s*([\d.]+)',
        'contraataques': r'Counter attacks:\s*([\d.]+)',
        'tackles': r'Tackles per game:\s*([\d.]+)',
        'interceptions': r'Interceptions per game:\s*([\d.]+)',
        'cleanSheets': r'Clean sheets:\s*([\d.]+)',
        'matches': r'Matches:\s*([\d.]+)',
        'duels': r'Duels won per game:\s*[\d.]+\s*\(([\d.]+)%\)'
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            stats[key] = float(match.group(1))
        else:
            stats[key] = 0.0 # Default if not found

    return stats

def main():
    data_dir = DATA_DIR
    output_file = OUTPUT_FILE
    if not os.path.exists(data_dir):
        print(f"Error: Directory {data_dir} not found.")
        # Try local path if running from root
        local_dir = './data/selecciones-sofascore'
        if os.path.exists(local_dir):
            data_dir = local_dir
            output_file = './data/selecciones_vectors.json'
        else:
            return

    raw_data = []
    for filename in os.listdir(data_dir):
        if filename.endswith('.txt'):
            filepath = os.path.join(data_dir, filename)
            raw_data.append(parse_txt_file(filepath))

    if not raw_data:
        print("No data found.")
        return

    # Calculate derived stats and find min/max for normalization
    min_max = {
        'golesPartido': {'min': float('inf'), 'max': float('-inf')},
        'posesion': {'min': float('inf'), 'max': float('-inf')},
        'regates': {'min': float('inf'), 'max': float('-inf')},
        'tirosPartido': {'min': float('inf'), 'max': float('-inf')},
        'faltasPartido': {'min': float('inf'), 'max': float('-inf')},
        'tarjetas': {'min': float('inf'), 'max': float('-inf')}, # yellow + red*2
        'contraataques_per_game': {'min': float('inf'), 'max': float('-inf')},
        'presionAlta': {'min': float('inf'), 'max': float('-inf')}, # tackles + interceptions
        'porteriaInvictaRatio': {'min': float('inf'), 'max': float('-inf')},
        'duelos': {'min': float('inf'), 'max': float('-inf')},
    }

    processed_data = []
    for d in raw_data:
        matches = d.get('matches', 1)
        matches = matches if matches > 0 else 1

        proc = {
            'name': d['name'],
            'golesPartido': d['golesPartido'],
            'posesion': d['posesion'],
            'regates': d['regates'],
            'tirosPartido': d['tirosPartido'],
            'faltasPartido': d['faltasPartido'],
            'tarjetas': d['yellowCards'] + (d['redCards'] / matches * 2), # Penalize red cards
            'contraataques_per_game': d['contraataques'] / matches,
            'presionAlta': d['tackles'] + d['interceptions'],
            'porteriaInvictaRatio': d['cleanSheets'] / matches,
            'duelos': d['duels']
        }
        processed_data.append(proc)

        # Update min/max
        for key in min_max.keys():
            if proc[key] < min_max[key]['min']: min_max[key]['min'] = proc[key]
            if proc[key] > min_max[key]['max']: min_max[key]['max'] = proc[key]

    # Normalize to [0, 1]
    final_vectors = {}
    for d in processed_data:
        vector = {}
        for key in min_max.keys():
            min_v = min_max[key]['min']
            max_v = min_max[key]['max']
            if max_v > min_v:
                vector[key] = (d[key] - min_v) / (max_v - min_v)
            else:
                vector[key] = 0.5 # Default if all values are the same

        # Mapping name to fifa_code would be ideal, but for now we key by name.
        # The frontend can normalize names to match.
        final_vectors[d['name']] = vector

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_vectors, f, indent=2, ensure_ascii=False)

    print(f"Successfully processed {len(final_vectors)} teams and wrote to {output_file}")

if __name__ == '__main__':
    main()
