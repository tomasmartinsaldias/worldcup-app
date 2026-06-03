import sqlite3, unicodedata

def normalize_name(text):
    if not isinstance(text, str): return ""
    text = text.lower().strip()
    text = text.replace("?", "i")
    char_map = {
        'ı': 'i', 'ğ': 'g', 'ş': 's', 'ç': 'c', 'ö': 'o', 'ü': 'u',
        'ñ': 'n', 'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ã': 'a', 'õ': 'o', 'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
    }
    for k, v in char_map.items():
        text = text.replace(k, v)
    text = unicodedata.normalize('NFD', text)
    text = "".join([c for c in text if 'a' <= c <= 'z' or c == ' '])
    text = " ".join(text.split())
    return text

def main():
    conn = sqlite3.connect("data/worldcup_combined.db")
    cursor = conn.cursor()
    cursor.execute("SELECT fifa_code, wc2026_name, historical_name, intl_results_name FROM team_mappings;")
    for code, wc, hist, intl in cursor.fetchall():
        if code in ('USA', 'CAN', 'TUR', 'BIH'):
            print(f"Code: {code} -> WC: {wc} (Norm: {normalize_name(wc)}), Hist: {hist} (Norm: {normalize_name(hist)}), Intl: {intl} (Norm: {normalize_name(intl)})")
    conn.close()

if __name__ == '__main__':
    main()
