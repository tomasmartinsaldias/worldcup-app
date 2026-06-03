import json
import os
import sys

# Set encoding to utf-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

for filename in os.listdir('data/clustering_maps'):
    if not filename.endswith('_arquetipos.json'):
        continue
    pos = filename.split('_')[1]
    filepath = os.path.join('data/clustering_maps', filename)
    with open(filepath, encoding='utf-8') as f:
        players = json.load(f)
    
    clusters = {}
    for p in players:
        cid = p['cluster_id']
        if cid not in clusters:
            clusters[cid] = []
        clusters[cid].append(p)
        
    print(f"=== {pos} ===")
    for cid in sorted(clusters.keys()):
        members = clusters[cid]
        rep = max(members, key=lambda p: p.get('overall', 0))
        # Get some sample names
        samples = sorted(members, key=lambda p: p.get('overall', 0), reverse=True)[:5]
        samples_str = ", ".join([f"{p['long_name']} ({p.get('overall')})" for p in samples])
        print(f"  Cluster {cid}: Rep = {rep['long_name']} (overall {rep.get('overall')}), Size = {len(members)}")
        print(f"    Examples: {samples_str}")
