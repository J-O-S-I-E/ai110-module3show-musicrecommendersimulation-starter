"""
Command line runner for the Music Recommender Simulation.

Run with:
    python -m src.main          (from project root)
    python src/main.py          (also works)
"""

import sys
import os
import copy

# Make `import recommender` resolve correctly regardless of how this file is
# invoked (python src/main.py  vs  python -m src.main).
sys.path.insert(0, os.path.dirname(__file__))

import recommender as rec
from recommender import load_songs, recommend_songs


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

WIDTH = 62

def print_header(profile_name: str) -> None:
    """Print a bordered section header labelled with the active taste profile name."""
    print("=" * WIDTH)
    print(f"  Music Recommender | {profile_name}")
    print("=" * WIDTH)

def print_recommendations(recommendations: list) -> None:
    """Print each ranked result with its title, artist, genre, score, and scoring reasons."""
    for rank, (song, score, reasons) in enumerate(recommendations, start=1):
        print(f"\n  [{rank}]  {song['title']}")
        print(f"        Artist : {song['artist']}")
        print(f"        Genre  : {song['genre']}  |  Mood: {song['mood']}")
        print(f"        Score  : {score:.2f} / 6.0")
        print(f"        Why    :")
        for reason in reasons:
            print(f"                 + {reason}")

def print_footer() -> None:
    """Print a divider line to visually separate profile result blocks."""
    print()
    print("-" * WIDTH)
    print()


# ---------------------------------------------------------------------------
# Taste profiles
# ---------------------------------------------------------------------------

# --- Standard profiles ---

PROFILE_POP = {
    "name":                "High-Energy Pop",
    "genre":               "pop",
    "mood":                "happy",
    "target_energy":       0.82,
    "target_acousticness": 0.18,
    "target_tempo":        120,
}

PROFILE_LOFI = {
    "name":                "Chill Lofi Study Session",
    "genre":               "lofi",
    "mood":                "chill",
    "target_energy":       0.38,
    "target_acousticness": 0.75,
    "target_tempo":        76,
}

PROFILE_ROCK = {
    "name":                "Deep Intense Rock",
    "genre":               "rock",
    "mood":                "intense",
    "target_energy":       0.90,
    "target_acousticness": 0.10,
    "target_tempo":        150,
}

# --- Adversarial / edge-case profiles ---

# Conflicting preferences: genre=metal (angry/intense) vs mood=sad.
# No metal+sad song exists in the catalog — designed to reveal whether the
# system gracefully handles a preference that cannot be fully satisfied.
PROFILE_SAD_HEADBANGER = {
    "name":                "ADVERSARIAL: Sad Headbanger (genre vs mood conflict)",
    "genre":               "metal",
    "mood":                "sad",
    "target_energy":       0.95,
    "target_acousticness": 0.05,
    "target_tempo":        170,
}

# No genre key at all — only numeric features and mood.
# Tests whether the system degrades gracefully when the strongest
# categorical signal (genre, worth +2.0) is absent.
PROFILE_NO_GENRE = {
    "name":                "ADVERSARIAL: Genre-Less (numeric features only)",
    "mood":                "happy",
    "target_energy":       0.75,
    "target_acousticness": 0.50,
    "target_tempo":        100,
}


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_profile(profile: dict, songs: list, k: int = 5) -> None:
    """Score and print the top k recommendations for a single taste profile dict."""
    # Work on a copy so pop/restore doesn't mutate the module-level constant.
    prefs = copy.copy(profile)
    name = prefs.pop("name")
    recommendations = recommend_songs(prefs, songs, k=k)

    print_header(name)
    print_recommendations(recommendations)
    print_footer()


def run_weight_experiment(profile: dict, songs: list, k: int = 5) -> None:
    """
    Run one profile under an experimental weight configuration:
      genre weight halved  (2.0 -> 1.0)
      energy weight doubled (1.0 -> 2.0)
    Max score stays 6.0. Restores original weights after the run.

    Purpose: reveal whether genre dominance is masking better cross-genre
    matches that score well on continuous features alone.
    """
    # Save originals
    orig_genre  = rec.WEIGHT_GENRE
    orig_energy = rec.WEIGHT_ENERGY

    # Apply experiment
    rec.WEIGHT_GENRE  = 1.0   # halved
    rec.WEIGHT_ENERGY = 2.0   # doubled  (max still 6.0 total)

    prefs = copy.copy(profile)
    name = prefs.pop("name")
    recommendations = recommend_songs(prefs, songs, k=k)

    print_header(f"EXPERIMENT | {name} | genre x0.5, energy x2.0")
    print_recommendations(recommendations)
    print_footer()

    # Restore
    rec.WEIGHT_GENRE  = orig_genre
    rec.WEIGHT_ENERGY = orig_energy


def main() -> None:
    """Entry point: load the catalog and run recommendations for each taste profile."""
    songs = load_songs("data/songs.csv")
    print(f"\nLoaded {len(songs)} songs from catalog.\n")

    # --- Standard profiles ---
    run_profile(PROFILE_POP,   songs, k=5)
    run_profile(PROFILE_LOFI,  songs, k=5)
    run_profile(PROFILE_ROCK,  songs, k=5)

    # --- Adversarial profiles ---
    run_profile(PROFILE_SAD_HEADBANGER, songs, k=5)
    run_profile(PROFILE_NO_GENRE,       songs, k=5)

    # --- Weight-shift experiment (on Rock profile to make the contrast clear) ---
    run_weight_experiment(PROFILE_ROCK, songs, k=5)


if __name__ == "__main__":
    main()
