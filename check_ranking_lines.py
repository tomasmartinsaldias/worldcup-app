with open('data/ranking_fifa.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in [15, 21, 29, 64]:
    print(f"Line {i+1} raw: {repr(lines[i])}")
    print(f"Line {i+1} split by \\t: {lines[i].strip().split('\t')}")
