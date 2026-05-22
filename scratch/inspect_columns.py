import soccerdata as sd
fb = sd.FBref(leagues="Big 5 European Leagues Combined", seasons="2023-2024")

print("--- Playing Time Table ---")
try:
    df_playing_time = fb.read_player_season_stats(stat_type="playing_time")
    cols = df_playing_time.columns.tolist()
    print("Columns:", cols)
    prog_cols = [c for c in cols if "prog" in str(c).lower() or "prg" in str(c).lower()]
    print("Potential progressive pass columns:", prog_cols)
except Exception as e:
    print("Error loading playing_time:", e)

print("\n--- Misc Table ---")
try:
    df_misc = fb.read_player_season_stats(stat_type="misc")
    cols = df_misc.columns.tolist()
    print("Columns:", cols)
    card_cols = [c for c in cols if "crd" in str(c).lower() or "card" in str(c).lower()]
    print("Potential card columns:", card_cols)
except Exception as e:
    print("Error loading misc:", e)
