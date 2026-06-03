with open('data/eliminatorias-2026/Squad Standard Stats 2025 Gold Cup.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for line in lines:
    if line.strip():
        print(repr(line))
