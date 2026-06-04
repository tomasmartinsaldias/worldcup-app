import os
import sqlite3
import pandas as pd

def get_k_factor(tournament):
    """
    Returns the K-factor (weight) of a match based on the tournament type
    according to standard World Football Elo principles.
    """
    tourn = str(tournament).lower()
    if 'world cup' in tourn and 'qualifying' not in tourn and 'qualification' not in tourn:
        return 60
    elif 'copa américa' in tourn or 'euro' in tourn or 'african cup' in tourn or 'asian cup' in tourn or 'gold cup' in tourn:
        return 50
    elif 'qualification' in tourn or 'qualifying' in tourn or 'nations league' in tourn:
        return 40
    elif 'friendly' in tourn:
        return 20
    else:
        return 30

def get_goal_margin_multiplier(home_score, away_score):
    """
    Returns the goal margin multiplier (G) to adjust for high-scoring margins.
    """
    diff = abs(home_score - away_score)
    if diff <= 1:
        return 1.0
    elif diff == 2:
        return 1.5
    elif diff == 3:
        return 1.75
    else:
        return 1.75 + (diff - 3) / 8.0

def calculate_elo(results_csv_path):
    """
    Sequentially processes the chronological history of international results
    to calculate dynamic Elo ratings for all teams.
    """
    df = pd.read_csv(results_csv_path)
    df['date'] = pd.to_datetime(df['date'])
    # Sort chronologically to preserve state dependency (Markovian chain)
    df = df.sort_values('date').reset_index(drop=True)

    # Initialize all teams at 1500 base Elo
    elo_ratings = {}

    # Process matches one by one
    for idx, row in df.iterrows():
        t_home = row['home_team']
        t_away = row['away_team']
        hs = row['home_score']
        as_ = row['away_score']
        tournament = row['tournament']
        neutral = row['neutral']

        # Skip if goals are not numbers
        if pd.isna(hs) or pd.isna(as_):
            continue

        # Get or initialize Elo values
        r_home = elo_ratings.get(t_home, 1500.0)
        r_away = elo_ratings.get(t_away, 1500.0)

        # Home advantage adjustment (+100 Elo points for home team if not neutral)
        r_home_adj = r_home + (0.0 if neutral else 100.0)

        # Calculate expected outcomes (We)
        we_home = 1.0 / (1.0 + 10.0 ** ((r_away - r_home_adj) / 400.0))
        we_away = 1.0 - we_home

        # Actual outcome (W)
        if hs > as_:
            w_home, w_away = 1.0, 0.0
        elif hs < as_:
            w_home, w_away = 0.0, 1.0
        else:
            w_home, w_away = 0.5, 0.5

        # K-factor and Goal Margin Multiplier (G)
        k = get_k_factor(tournament)
        g = get_goal_margin_multiplier(hs, as_)

        # Update ratings
        elo_ratings[t_home] = r_home + k * g * (w_home - we_home)
        elo_ratings[t_away] = r_away + k * g * (w_away - we_away)

    return elo_ratings

def update_database_with_elo(db_path, elo_ratings):
    """
    Maps calculated team names to FIFA codes, saves the Elo ratings into SQLite,
    and stores all 333 teams in historical_elo_ratings.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Create and populate historical_elo_ratings table for all teams
    cursor.execute("DROP TABLE IF EXISTS historical_elo_ratings;")
    cursor.execute("""
        CREATE TABLE historical_elo_ratings (
            team_name TEXT PRIMARY KEY,
            elo_rating REAL
        );
    """)

    elo_rows = [(name, round(val, 1)) for name, val in elo_ratings.items()]
    cursor.executemany("""
        INSERT INTO historical_elo_ratings (team_name, elo_rating)
        VALUES (?, ?);
    """, elo_rows)
    print(f"Stored {len(elo_rows)} team ratings in 'historical_elo_ratings' table.")

    # 2. Add column to scraped_team_metrics if not exists
    try:
        cursor.execute("ALTER TABLE scraped_team_metrics ADD COLUMN elo_rating REAL;")
    except sqlite3.OperationalError:
        # Already exists
        pass

    # Get mappings
    cursor.execute("SELECT fifa_code, intl_results_name, wc2026_name FROM team_mappings;")
    mappings = cursor.fetchall()

    updated_count = 0
    print("\n--- Mapping Elo Ratings to FIFA Codes ---")
    for code, intl_name, wc_name in mappings:
        elo_val = None

        # Try finding the rating in our dict using mapped name variants
        for name in [intl_name, wc_name]:
            if name in elo_ratings:
                elo_val = elo_ratings[name]
                break

        # Fallback substring match if exact match fails
        if elo_val is None and intl_name:
            for k, v in elo_ratings.items():
                if intl_name.lower() in k.lower() or k.lower() in intl_name.lower():
                    elo_val = v
                    break

        # Update SQLite if found
        if elo_val is not None:
            cursor.execute("""
                UPDATE scraped_team_metrics
                SET elo_rating = ?
                WHERE fifa_code = ?;
            """, (round(elo_val, 1), code))
            updated_count += 1
            print(f"  {code} ({intl_name or wc_name}): {elo_val:.1f}")
        else:
            print(f"  Warning: No Elo rating found for {code} ({intl_name or wc_name})")

    conn.commit()
    conn.close()
    print(f"\nSuccessfully updated {updated_count} team Elo ratings in database.")


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_path = os.path.join(base_dir, "data", "international-results", "results.csv")
    db_path = os.path.join(base_dir, "data", "worldcup_combined.db")

    print("Starting Elo calculations over historical data...")
    ratings = calculate_elo(results_path)
    print(f"Calculated Elo ratings for {len(ratings)} unique national teams.")

    update_database_with_elo(db_path, ratings)
