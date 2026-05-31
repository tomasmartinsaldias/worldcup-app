import re

def main():
    # Read with latin-1 to see if we can decode the currency symbol correctly or bypass it
    with open("data/ranking_fifa.txt", 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if not line.strip(): continue
            parts = line.strip().split('\t')
            if len(parts) >= 5:
                val_str = parts[4].strip().lower()
                val_float = float(re.sub(r'[^0-9.]', '', val_str))
                print(f"Original: {val_str} -> Extracted: {val_float}")
                break

if __name__ == '__main__':
    main()
