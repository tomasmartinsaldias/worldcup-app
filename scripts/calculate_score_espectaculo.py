import os
import re
import sqlite3
import statistics
import pandas as pd

# Spanish translation helper to map Sofascore files to FIFA codes
SPANISH_TO_FIFA = {
    'alemania': 'GER', 'arabia saudita': 'KSA', 'argelia': 'ALG', 'argentina': 'ARG',
    'australia': 'AUS', 'austria': 'AUT', 'bosnia y herzegovina': 'BIH', 'brasil': 'BRA',
    'belgica': 'BEL', 'cabo verde': 'CPV', 'canada': 'CAN', 'catar': 'QAT',
    'colombia': 'COL', 'corea del sur': 'KOR', 'costa de marfil': 'CIV', 'croacia': 'CRO',
    'curazao': 'CUR', 'ecuador': 'ECU', 'egipto': 'EGY', 'escocia': 'SCO',
    'espana': 'ESP', 'estados unidos': 'USA', 'francia': 'FRA', 'ghana': 'GHA',
    'haiti': 'HAI', 'inglaterra': 'ENG', 'irak': 'IRQ', 'iran': 'IRN',
    'japon': 'JPN', 'jordania': 'JOR', 'marruecos': 'MAR', 'mexico': 'MEX',
    'noruega': 'NOR', 'panama': 'PAN', 'paraguay': 'PAR', 'paises bajos': 'NED',
    'portugal': 'POR', 'republica checa': 'CZE', 'republica democratica del congo': 'COD',
    'senegal': 'SEN', 'sudafrica': 'RSA', 'suecia': 'SWE', 'suiza': 'SUI',
    'turquia': 'TUR', 'tunez': 'TUN', 'uruguay': 'URU', 'uzbekistan': 'UZB',
    'nueva zelanda': 'NZL'
}

def normalize_name(text):
    """Normalize names for uniform comparison."""
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    char_map = {
        'ı': 'i', 'ğ': 'g', 'ş': 's', 'ç': 'c', 'ö': 'o', 'ü': 'u',
        'ñ': 'n', 'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ã': 'a', 'õ': 'o', 'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
        'í': 'i', 'í': 'i', 'ć': 'c', 'š': 's', 'ž': 'z', 'đ': 'd'
    }
    for k, v in char_map.items():
        text = text.replace(k, v)
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())


def add_column_if_not_exists(cursor, table, col, col_type):
    """Utility to safely add database columns if they don't already exist."""
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type};")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            pass
        else:
            raise e


def load_team_mappings(cursor):
    """Load mappings and build lookup dictionaries for team names and codes."""
    cursor.execute("SELECT fifa_code, wc2026_name, historical_name, intl_results_name FROM team_mappings;")
    mappings = []
    code_to_names = {}
    name_to_code = {}

    for row in cursor.fetchall():
        fifa_code, wc, hist, intl = row
        mappings.append({
            "fifa_code": fifa_code,
            "wc2026_name": wc,
            "historical_name": hist,
            "intl_results_name": intl
        })
        code_to_names[fifa_code] = {
            "wc": wc,
            "hist": hist,
            "intl": intl
        }

        # Populate lookup map with all name variants
        for name in [wc, hist, intl]:
            if name:
                name_to_code[normalize_name(name)] = fifa_code

    # Manual overrides/additions
    name_to_code[normalize_name("United States")] = "USA"
    name_to_code[normalize_name("Côte d'Ivoire")] = "CIV"
    name_to_code[normalize_name("DR Congo")] = "COD"
    name_to_code[normalize_name("Curaçao")] = "CUR"

    return code_to_names, name_to_code


def load_fifa_rankings(ranking_path, code_to_names, name_to_code):
    """Parse and build helper function to query FIFA Rankings."""
    rankings_dict = {}
    if os.path.exists(ranking_path):
        with open(ranking_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    try:
                        rank_val = int(parts[0].strip())
                        nation_raw = parts[1].strip()
                        nation_words = nation_raw.split()

                        # Handle duplicate words (e.g. "Germany Germany")
                        if len(nation_words) >= 2 and nation_words[0] == nation_words[1]:
                            nation_name = nation_words[0]
                        else:
                            nation_name = nation_raw

                        rankings_dict[normalize_name(nation_name)] = rank_val
                    except ValueError:
                        continue

    def get_fifa_rank(team_name):
        norm = normalize_name(team_name)
        if norm in rankings_dict:
            return rankings_dict[norm]
        # Substring lookup
        for k, v in rankings_dict.items():
            if norm in k or k in norm:
                return v
        # Try mapped name variants
        code = name_to_code.get(norm)
        if code and code in code_to_names:
            for name in code_to_names[code].values():
                if name:
                    n2 = normalize_name(name)
                    if n2 in rankings_dict:
                        return rankings_dict[n2]
        return 100 # default fallback

    return get_fifa_rank




def extract_sofascore_metrics(sofascore_dir):
    """Extract metric keys from raw Sofascore team statistics files."""
    raw_stats = {}

    for filename in os.listdir(sofascore_dir):
        if not filename.endswith(".txt"):
            continue

        if "(" in filename:
            parts = filename.split("(")
            country_name_sp = parts[0].strip()
            tournament_in_fn = parts[1].split(")")[0].replace(".txt", "").strip()
        else:
            country_name_sp = filename.replace(".txt", "").strip()
            tournament_in_fn = "Unknown"

        fifa_code = SPANISH_TO_FIFA.get(normalize_name(country_name_sp))
        if not fifa_code:
            print(f"Warning: Could not map Spanish country name '{country_name_sp}' to FIFA code")
            continue

        filepath = os.path.join(sofascore_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        def find_metric(pattern, default=0.0):
            m = re.search(pattern, content, re.IGNORECASE)
            return float(m.group(1)) if m else default

        matches = find_metric(r"Matches:\s*(\d+)", 6.0)
        big_chances_pg = find_metric(r"Big chances per game:\s*([\d\.]+)", 1.5)
        counter_attacks = find_metric(r"Counter attacks:\s*(\d+)", 3.0)
        fouls_pg = find_metric(r"Fouls per game:\s*([\d\.]+)", 10.0)
        goals_conceded_pg = find_metric(r"Goals conceded per game:\s*([\d\.]+)", 1.0)
        yellow_cards_pg = find_metric(r"Yellow cards per game:\s*([\d\.]+)", 1.5)
        red_cards = find_metric(r"Red cards:\s*(\d+)", 0.0)

        # Normalization to per-game basis
        counter_attacks_pg = counter_attacks / matches if matches > 0 else 0.5
        cards_pg = yellow_cards_pg + (red_cards / matches if matches > 0 else 0.0)

        raw_stats[fifa_code] = {
            "matches": matches,
            "oc_raw": big_chances_pg,
            "ca_raw": counter_attacks_pg,
            "drama_raw": fouls_pg,
            "vuln_raw": goals_conceded_pg,
            "cards_pg": cards_pg,
            "tournament_fn": tournament_in_fn
        }

    return raw_stats


def impute_nzl_stats(raw_stats):
    """Impute metrics for NZL (New Zealand) using a dynamic global friction ratio."""
    total_fouls_pg = sum(stats["drama_raw"] for stats in raw_stats.values())
    total_cards_pg = sum(stats["cards_pg"] for stats in raw_stats.values())

    r_friccion = total_fouls_pg / total_cards_pg if total_cards_pg > 0 else 6.5
    print(f"Global Friction Ratio (Rfriccion): {r_friccion:.3f}")

    nz_cards_pg = 0.2 # (1 Yellow, 0 Red cards) / 5 matches
    nz_fouls_pg = nz_cards_pg * r_friccion
    print(f"Inferred NZL fouls per game: {nz_fouls_pg:.3f}")

    raw_stats["NZL"] = {
        "matches": 5.0,
        "oc_raw": 5.6, # Gnp = (29 - 1) / 5 = 5.6
        "ca_raw": 0.2,
        "drama_raw": nz_fouls_pg,
        "vuln_raw": 0.2, # Gc = 1 / 5 = 0.2
        "cards_pg": nz_cards_pg,
        "tournament_fn": "OFC Qualifiers"
    }


def calculate_tournament_difficulty(raw_stats, results_df_recent, code_to_names, name_to_code, get_fifa_rank):
    """Calculate tournament difficulty factor (Cdif) for each team."""
    adjusted_stats = {}

    for code, stats in raw_stats.items():
        intl_name = None
        if code in code_to_names:
            intl_name = code_to_names[code]["intl"]
        else:
            for k, v in name_to_code.items():
                if v == code:
                    intl_name = k
                    break

        if not intl_name and code in code_to_names:
            intl_name = code_to_names[code]["wc"]

        tournament_fn = stats["tournament_fn"]

        # Determine appropriate tournament category filters
        if "World Cup Qual" in tournament_fn or "OFC" in tournament_fn:
            tournaments = ['FIFA World Cup qualification']
        elif "Arab Cup" in tournament_fn:
            tournaments = ['Arab Cup']
        elif "Africa Cup of Nations" in tournament_fn:
            tournaments = ['African Cup of Nations', 'African Cup of Nations qualification']
        elif "Asian Cup" in tournament_fn:
            tournaments = ['AFC Asian Cup']
        elif "Gold Cup" in tournament_fn:
            tournaments = ['Gold Cup', 'CONCACAF Nations League']
        else:
            tournaments = ['FIFA World Cup qualification', 'Friendly']

        # Filter matching results
        team_matches = results_df_recent[
            ((results_df_recent['home_team'] == intl_name) | (results_df_recent['away_team'] == intl_name)) &
            (results_df_recent['tournament'].isin(tournaments))
        ]

        opponents = []
        for _, row in team_matches.iterrows():
            opp = row['away_team'] if row['home_team'] == intl_name else row['home_team']
            if opp != intl_name:
                opponents.append(opp)

        # Resolve opponent ranks
        ranks = [get_fifa_rank(opp) for opp in opponents]

        # Fallback values by confederation if no historical ranks are available
        if not ranks:
            if code in ['GER', 'FRA', 'ENG', 'ESP', 'POR', 'ITA', 'CRO', 'BEL', 'NED']:
                ranks = [40, 50, 60]
            elif code in ['ARG', 'BRA', 'URU', 'COL', 'ECU', 'PAR']:
                ranks = [30, 40, 50]
            elif code in ['USA', 'MEX', 'CAN', 'PAN', 'HAI', 'CUR']:
                ranks = [80, 90, 100]
            elif code in ['NZL']:
                ranks = [151, 153, 154, 157, 160]
            else:
                ranks = [100, 110, 120]

        rmed = statistics.median(ranks)

        # SOVEREIGN ALGEBRAIC FORMULA: Softer Cdif formula to avoid double-penalizing UEFA teams
        cdif = 1.0 - 0.5 * ((rmed - 1.0) / 209.0)
        cdif = max(0.1, min(1.0, cdif))

        # SOVEREIGN ALGEBRAIC FORMULA: division for drama and vulnerability
        adjusted_stats[code] = {
            "oc_adj": stats["oc_raw"] * cdif,
            "ca_adj": stats["ca_raw"] * cdif,
            "drama_adj": stats["drama_raw"] / cdif,
            "vuln_adj": stats["vuln_raw"] / cdif,
            "cdif": cdif,
            "rmed": rmed
        }

    return adjusted_stats




def normalize_and_winsorize(adjusted_stats):
    """Normalize using 95th percentile Winsorization scaling."""
    oc_vals = [s["oc_adj"] for s in adjusted_stats.values()]
    ca_vals = [s["ca_adj"] for s in adjusted_stats.values()]
    drama_vals = [s["drama_adj"] for s in adjusted_stats.values()]
    vuln_vals = [s["vuln_adj"] for s in adjusted_stats.values()]

    cap_oc = pd.Series(oc_vals).quantile(0.95)
    cap_ca = pd.Series(ca_vals).quantile(0.95)
    cap_drama = pd.Series(drama_vals).quantile(0.95)
    cap_vuln = pd.Series(vuln_vals).quantile(0.95)

    print(f"Percentile 95 Caps - OC: {cap_oc:.3f}, CA: {cap_ca:.3f}, Drama: {cap_drama:.3f}, Vuln: {cap_vuln:.3f}")

    # Clipped ranges
    min_oc, max_oc = min(min(v, cap_oc) for v in oc_vals), cap_oc
    min_ca, max_ca = min(min(v, cap_ca) for v in ca_vals), cap_ca
    min_drama, max_drama = min(min(v, cap_drama) for v in drama_vals), cap_drama
    min_vuln, max_vuln = min(min(v, cap_vuln) for v in vuln_vals), cap_vuln

    final_params = {}
    for code, adj in adjusted_stats.items():
        oc_c = min(adj["oc_adj"], cap_oc)
        ca_c = min(adj["ca_adj"], cap_ca)
        drama_c = min(adj["drama_adj"], cap_drama)
        vuln_c = min(adj["vuln_adj"], cap_vuln)

        oc_norm = (oc_c - min_oc) / (max_oc - min_oc) if max_oc != min_oc else 0.5
        ca_norm = (ca_c - min_ca) / (max_ca - min_ca) if max_ca != min_ca else 0.5
        drama_norm = (drama_c - min_drama) / (max_drama - min_drama) if max_drama != min_drama else 0.5

        # SOVEREIGN ALGEBRAIC FORMULA: Vulnerability floor of 0.20
        vuln_norm = 0.2 + 0.8 * ((vuln_c - min_vuln) / (max_vuln - min_vuln)) if max_vuln != min_vuln else 0.5

        final_params[code] = {
            "ocasiones_norm": round(oc_norm, 3),
            "contra_norm": round(ca_norm, 3),
            "drama_norm": round(drama_norm, 3),
            "vuln_norm": round(vuln_norm, 3),
            "cdif": round(adj["cdif"], 3),
            "rmed": adj["rmed"]
        }

    return final_params


def update_database(db_path, final_params):
    """Persist normalized parameters into the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    add_column_if_not_exists(cursor, "scraped_team_metrics", "ocasiones_norm", "REAL")
    add_column_if_not_exists(cursor, "scraped_team_metrics", "contra_norm", "REAL")
    add_column_if_not_exists(cursor, "scraped_team_metrics", "drama_norm", "REAL")
    add_column_if_not_exists(cursor, "scraped_team_metrics", "vuln_norm", "REAL")
    conn.commit()

    for code, p in final_params.items():
        cursor.execute("""
            UPDATE scraped_team_metrics
            SET ocasiones_norm = ?,
                contra_norm = ?,
                drama_norm = ?,
                vuln_norm = ?
            WHERE fifa_code = ?;
        """, (p["ocasiones_norm"], p["contra_norm"], p["drama_norm"], p["vuln_norm"], code))

    conn.commit()
    conn.close()


def get_confederation_by_tournament(tournament_fn):
    tourn = str(tournament_fn).lower()
    if "conmebol" in tourn:
        return "CONMEBOL_WCQ"
    elif "uefa" in tourn:
        return "UEFA_WCQ"
    elif "africa" in tourn:
        return "AFCON"
    elif "ofc" in tourn:
        return "OFC_QUAL"
    elif "gold cup" in tourn or "concacaf" in tourn:
        return "GOLD_CUP"
    elif "arab" in tourn:
        return "ARAB_CUP"
    elif "afc" in tourn or "asian" in tourn:
        return "ASIAN_CUP"
    else:
        return "OTHER"


def adjust_raw_stats_by_confederation(raw_stats):
    """
    Applies empirical Baseline Alignment (Alineación de Medias) to remove regional
    confederation biases from raw offensive metrics (ocasiones y contraataques).
    """
    # 1. Map each team to its confederation
    team_confederations = {}
    for code, stats in raw_stats.items():
        team_confederations[code] = get_confederation_by_tournament(stats["tournament_fn"])

    # 2. Calculate global means
    all_ocs = [s["oc_raw"] for s in raw_stats.values()]
    all_cas = [s["ca_raw"] for s in raw_stats.values()]

    mean_oc_global = sum(all_ocs) / len(all_ocs) if all_ocs else 2.5
    mean_ca_global = sum(all_cas) / len(all_cas) if all_cas else 1.0

    print("\n--- Baseline Alignment (Empirical Means) ---")
    print(f"Global Mean - OC: {mean_oc_global:.3f}, CA: {mean_ca_global:.3f}")

    # 3. Calculate confederation means
    conf_stats = {} # conf -> {'oc_sum': 0, 'ca_sum': 0, 'count': 0}
    for code, stats in raw_stats.items():
        conf = team_confederations[code]
        if conf not in conf_stats:
            conf_stats[conf] = {'oc_sum': 0.0, 'ca_sum': 0.0, 'count': 0}
        conf_stats[conf]['oc_sum'] += stats["oc_raw"]
        conf_stats[conf]['ca_sum'] += stats["ca_raw"]
        conf_stats[conf]['count'] += 1

    # Calculate multipliers
    multipliers = {} # conf -> {'oc_mult': float, 'ca_mult': float}
    for conf, cstats in conf_stats.items():
        count = cstats['count']
        mean_oc_conf = cstats['oc_sum'] / count if count > 0 else mean_oc_global
        mean_ca_conf = cstats['ca_sum'] / count if count > 0 else mean_ca_global

        # Multiplier = global_mean / conf_mean
        oc_mult = mean_oc_global / mean_oc_conf if mean_oc_conf > 0 else 1.0
        ca_mult = mean_ca_global / mean_ca_conf if mean_ca_conf > 0 else 1.0

        # Limit the multipliers to avoid extreme edge cases (e.g. 0.5 to 2.0)
        oc_mult = max(0.5, min(2.0, oc_mult))
        ca_mult = max(0.5, min(2.0, ca_mult))

        multipliers[conf] = {'oc_mult': oc_mult, 'ca_mult': ca_mult}
        print(f"  Confederation {conf} (N={count}):")
        print(f"    Mean OC: {mean_oc_conf:.3f} -> Multiplier: {oc_mult:.3f}")
        print(f"    Mean CA: {mean_ca_conf:.3f} -> Multiplier: {ca_mult:.3f}")

    # 4. Apply multipliers to raw stats
    for code, stats in raw_stats.items():
        conf = team_confederations[code]
        mults = multipliers[conf]
        stats["oc_raw"] *= mults['oc_mult']
        stats["ca_raw"] *= mults['ca_mult']


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "data", "worldcup_combined.db")
    results_path = os.path.join(base_dir, "data", "international-results", "results.csv")
    ranking_path = os.path.join(base_dir, "data", "ranking_fifa.txt")
    sofascore_dir = os.path.join(base_dir, "data", "selecciones-sofascore")

    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    # Connect and extract mappings
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    code_to_names, name_to_code = load_team_mappings(cursor)
    conn.close()

    # Load rankings
    print("Loading FIFA rankings...")
    get_fifa_rank = load_fifa_rankings(ranking_path, code_to_names, name_to_code)

    # Load results
    print("Loading match results...")
    results_df = pd.read_csv(results_path)
    results_df['date'] = pd.to_datetime(results_df['date'])
    results_df_recent = results_df[results_df['date'] >= '2023-01-01']

    # Extract Sofascore raw metrics
    print("Extracting Sofascore metrics...")
    raw_stats = extract_sofascore_metrics(sofascore_dir)

    # Impute missing NZL stats using Global Friction Ratio
    impute_nzl_stats(raw_stats)

    # Adjust raw stats by confederation to remove regional biases
    adjust_raw_stats_by_confederation(raw_stats)

    # Compute Cdif adjustments
    print("Calculating Cdif for each team...")
    adjusted_stats = calculate_tournament_difficulty(raw_stats, results_df_recent, code_to_names, name_to_code, get_fifa_rank)

    # Normalize with 95th Percentile Winsorization
    print("Normalizing metrics with 95th percentile clipping...")
    final_params = normalize_and_winsorize(adjusted_stats)

    # Persist back to the DB
    print("Saving parameters to database...")
    update_database(db_path, final_params)
    print("Database successfully updated with new spectacle parameters!")

    # Print verify summary
    for c in ["GER", "ARG", "NZL"]:
        if c in final_params:
            print(f"\n{c} Final Parameters:")
            print(f"  ocasiones_norm: {final_params[c]['ocasiones_norm']}")
            print(f"  contra_norm: {final_params[c]['contra_norm']}")
            print(f"  drama_norm: {final_params[c]['drama_norm']}")
            print(f"  vuln_norm: {final_params[c]['vuln_norm']}")
            print(f"  Cdif: {final_params[c]['cdif']}")



if __name__ == "__main__":
    main()
