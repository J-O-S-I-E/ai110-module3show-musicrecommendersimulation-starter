"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # --- TASTE PROFILE (Step 2) ---
    # This profile targets a "chill lofi study session" listener.
    #
    # INLINE CRITIQUE — Can this profile differentiate "intense rock" from "chill lofi"?
    #
    # YES — here's why each feature contributes:
    #   genre:              "lofi" vs "rock" → direct categorical split, strong signal
    #   mood:               "chill" vs "intense" → another direct split, doubles the categorical weight
    #   target_energy:      0.38 vs ~0.91 for rock → huge numeric gap, reliable separator
    #   target_acousticness: 0.75 vs ~0.10 for rock → largest numeric spread in the dataset
    #   target_tempo:       76 vs ~152 BPM for rock → 2× difference, clear boundary
    #
    # POTENTIAL WEAKNESS — is the profile too narrow?
    #   • Using all five features TOGETHER creates a tight cluster around lofi/chill songs.
    #     Songs that match 4/5 features but differ on one (e.g., an acoustic indie ballad)
    #     might score nearly as well as true lofi — so "too narrow" isn't the risk here.
    #   • The real risk is the OPPOSITE: weighting every feature equally could cause
    #     a high-acousticness country song (acousticness=0.74) to outscore a lofi track
    #     that nails every other dimension. Feature weights matter more than count.
    #   • valence and danceability are intentionally omitted — they overlap heavily with
    #     mood and energy and would add noise without improving separation.
    #
    # VERDICT: Five features is sufficient for clean rock-vs-lofi separation.
    #          The next design decision is HOW each feature is scored (exact match vs
    #          weighted distance), not whether to add more features.
    user_prefs = {
        "genre":               "lofi",   # categorical — exact or fuzzy match
        "mood":                "chill",  # categorical — exact or fuzzy match
        "target_energy":       0.38,     # 0–1 scale; lofi sits at 0.35–0.42
        "target_acousticness": 0.75,     # 0–1 scale; lofi sits at 0.71–0.86
        "target_tempo":        76,       # BPM; lofi sits at 72–80
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()
