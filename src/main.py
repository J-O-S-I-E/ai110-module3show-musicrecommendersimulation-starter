"""
Command line runner for the Music Recommender Simulation.

Run with:
    python -m src.main          (from project root)
    python src/main.py          (also works)

Challenges implemented
----------------------
1. Advanced features  — 5 new columns in songs.csv (popularity, decade,
                        mood_tags, lyrical_complexity, live_feel) with
                        dedicated scoring rules in recommender.py
2. Scoring modes      — genre_first / mood_first / energy_focused / discovery
                        via SCORING_MODES strategy dict in recommender.py
3. Diversity penalty  — repeat-artist songs lose 30% of their score
4. Visual table       — tabulate-formatted output (ASCII fallback included)
"""

import sys
import os
import copy

sys.path.insert(0, os.path.dirname(__file__))

import recommender as rec
from recommender import load_songs, recommend_songs, format_table, SCORING_MODES

WIDTH = 70


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def section(title: str) -> None:
    """Print a bold section divider."""
    print()
    print("=" * WIDTH)
    print(f"  {title}")
    print("=" * WIDTH)


def subsection(title: str) -> None:
    """Print a lighter subsection divider."""
    print()
    print(f"  -- {title} --")
    print()


def print_table(recommendations: list, mode_name: str = "balanced") -> None:
    """Render recommendations as a tabulate table and print it."""
    print(format_table(recommendations, mode_name=mode_name, max_reasons=3))


# ---------------------------------------------------------------------------
# Taste profiles (extended with Challenge 1 advanced features)
# ---------------------------------------------------------------------------

PROFILE_POP = {
    "name":                       "High-Energy Pop",
    "genre":                      "pop",
    "mood":                       "happy",
    "target_energy":              0.82,
    "target_acousticness":        0.18,
    "target_tempo":               120,
    # Advanced (Challenge 1)
    "target_popularity":          80,
    "preferred_decade":           2020,
    "desired_tags":               ["euphoric", "uplifting", "bright"],
    "target_lyrical_complexity":  0.35,
    "target_live_feel":           0.15,
}

PROFILE_LOFI = {
    "name":                       "Chill Lofi Study Session",
    "genre":                      "lofi",
    "mood":                       "chill",
    "target_energy":              0.38,
    "target_acousticness":        0.75,
    "target_tempo":               76,
    # Advanced (Challenge 1)
    "target_popularity":          60,
    "preferred_decade":           2020,
    "desired_tags":               ["cozy", "focused", "dreamy"],
    "target_lyrical_complexity":  0.10,
    "target_live_feel":           0.70,
}

PROFILE_ROCK = {
    "name":                       "Deep Intense Rock",
    "genre":                      "rock",
    "mood":                       "intense",
    "target_energy":              0.90,
    "target_acousticness":        0.10,
    "target_tempo":               150,
    # Advanced (Challenge 1)
    "target_popularity":          70,
    "preferred_decade":           2010,
    "desired_tags":               ["powerful", "aggressive", "triumphant"],
    "target_lyrical_complexity":  0.50,
    "target_live_feel":           0.50,
}

PROFILE_SAD_HEADBANGER = {
    "name":                       "ADVERSARIAL: Sad Headbanger",
    "genre":                      "metal",
    "mood":                       "sad",
    "target_energy":              0.95,
    "target_acousticness":        0.05,
    "target_tempo":               170,
    # Advanced — desired tags conflict with available metal tags
    "target_popularity":          50,
    "preferred_decade":           2010,
    "desired_tags":               ["dark", "desolate", "haunting"],
    "target_lyrical_complexity":  0.40,
    "target_live_feel":           0.40,
}

PROFILE_NO_GENRE = {
    "name":                       "ADVERSARIAL: Genre-Less",
    "mood":                       "happy",
    "target_energy":              0.75,
    "target_acousticness":        0.50,
    "target_tempo":               100,
    # Advanced
    "target_popularity":          70,
    "preferred_decade":           2010,
    "desired_tags":               ["hopeful", "breezy"],
    "target_lyrical_complexity":  0.60,
    "target_live_feel":           0.50,
}

# Artist-repeat catalog demo — only used for diversity penalty demonstration
PROFILE_NEON_ECHO_FAN = {
    "name":    "Neon Echo Fan (diversity demo)",
    "genre":   "synthwave",
    "mood":    "moody",
    "target_energy":       0.78,
    "target_acousticness": 0.20,
    "target_tempo":        114,
}


# ---------------------------------------------------------------------------
# Runners
# ---------------------------------------------------------------------------

def run_table(profile: dict, songs: list, k: int = 5,
              mode: str = "balanced", diversity_penalty: bool = False) -> None:
    """Score a profile, then render the result as a tabulate table."""
    prefs = copy.copy(profile)
    name  = prefs.pop("name")
    diversity_tag = " + diversity penalty" if diversity_penalty else ""
    section(f"{name}  [{mode}{diversity_tag}]")
    recs = recommend_songs(prefs, songs, k=k, mode=mode,
                           diversity_penalty=diversity_penalty)
    print_table(recs, mode_name=mode)


def run_mode_comparison(profile: dict, songs: list, k: int = 5) -> None:
    """Run the same profile under all five scoring modes side-by-side."""
    prefs = copy.copy(profile)
    name  = prefs.pop("name")
    section(f"MODE COMPARISON | {name}")
    for mode in SCORING_MODES:
        subsection(f"Mode: {mode}")
        recs = recommend_songs(prefs, songs, k=k, mode=mode)
        print_table(recs, mode_name=mode)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point: demonstrate all four challenges across multiple profiles."""
    songs = load_songs("data/songs.csv")
    print(f"\nLoaded {len(songs)} songs from catalog  "
          f"({len(songs[0])} features per song with advanced columns).\n")

    # ------------------------------------------------------------------
    # CHALLENGE 1 + 4: Extended profiles with advanced features, table view
    # ------------------------------------------------------------------
    section("CHALLENGE 1 + 4 | Advanced Features + Visual Table")
    print("\n  Five new features scored: popularity, decade, mood_tags,")
    print("  lyrical_complexity, live_feel.  Max score raised from 6.0 to 9.0.")

    run_table(PROFILE_POP,  songs, mode="balanced")
    run_table(PROFILE_LOFI, songs, mode="balanced")
    run_table(PROFILE_ROCK, songs, mode="balanced")

    # ------------------------------------------------------------------
    # CHALLENGE 2: Mode comparison — same Rock profile, all five modes
    # ------------------------------------------------------------------
    run_mode_comparison(PROFILE_ROCK, songs, k=5)

    # ------------------------------------------------------------------
    # CHALLENGE 3: Diversity penalty demo
    # Neon Echo appears in both #1 (Sunrise City) and #8 (Night Drive Loop).
    # Without penalty: both can appear. With penalty: the second is pushed down.
    # ------------------------------------------------------------------
    section("CHALLENGE 3 | Diversity Penalty Demo")
    print("\n  Profile targets synthwave/moody. Neon Echo has two songs in")
    print("  the catalog (Night Drive Loop + Sunrise City). Watch them compete.\n")

    subsection("Without diversity penalty")
    prefs_div = copy.copy(PROFILE_NEON_ECHO_FAN)
    prefs_div.pop("name")
    recs_no_div = recommend_songs(prefs_div, songs, k=5, diversity_penalty=False)
    print_table(recs_no_div)

    subsection("With diversity penalty (repeat artist loses 30%)")
    recs_div = recommend_songs(prefs_div, songs, k=5, diversity_penalty=True)
    print_table(recs_div)

    # ------------------------------------------------------------------
    # Adversarial profiles
    # ------------------------------------------------------------------
    section("ADVERSARIAL PROFILES")
    run_table(PROFILE_SAD_HEADBANGER, songs, mode="balanced")
    run_table(PROFILE_NO_GENRE,       songs, mode="balanced")

    print()


if __name__ == "__main__":
    main()
