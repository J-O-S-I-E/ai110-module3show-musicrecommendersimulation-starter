"""
Command line runner for the Music Recommender Simulation.

Run with:
    python -m src.main          (from project root)
    python src/main.py          (also works)
"""

import sys
import os

# Make `import recommender` resolve correctly regardless of how this file is
# invoked (python src/main.py  vs  python -m src.main).
sys.path.insert(0, os.path.dirname(__file__))

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

PROFILE_LOFI = {
    "name":                "Chill Lofi Study Session",
    "genre":               "lofi",
    "mood":                "chill",
    "target_energy":       0.38,
    "target_acousticness": 0.75,
    "target_tempo":        76,
}

PROFILE_POP = {
    "name":                "Upbeat Pop (default verification profile)",
    "genre":               "pop",
    "mood":                "happy",
    "target_energy":       0.82,
    "target_acousticness": 0.18,
    "target_tempo":        120,
}


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_profile(profile: dict, songs: list, k: int = 5) -> None:
    """Score and print the top k recommendations for a single taste profile dict."""
    # Strip the display-only "name" key before passing to recommend_songs
    name = profile.pop("name")
    recommendations = recommend_songs(profile, songs, k=k)
    profile["name"] = name          # restore so the dict stays intact

    print_header(name)
    print_recommendations(recommendations)
    print_footer()


def main() -> None:
    """Entry point: load the catalog and run recommendations for each taste profile."""
    songs = load_songs("data/songs.csv")
    print(f"\nLoaded {len(songs)} songs from catalog.\n")

    run_profile(PROFILE_POP,  songs, k=5)
    run_profile(PROFILE_LOFI, songs, k=5)


if __name__ == "__main__":
    main()
