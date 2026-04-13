"""
Music Recommender — Scoring Logic Design
=========================================

ALGORITHM RECIPE
----------------
Each song is scored against the user's taste profile using a weighted point system.
Points are then summed; the top-k songs by total score are returned.

  Feature            Max Points   Type        Rationale
  -----------------  ----------   ----------  ----------------------------------------
  genre match        +2.0         binary      14 unique genres → highly specific signal
  mood match         +1.5         binary      12 moods but cross-genre (chill = lofi
                                              AND ambient AND jazz) → slightly less
                                              specific than genre
  energy similarity  +1.0         continuous  0–1 scale; rock ≈ 0.91, lofi ≈ 0.38
                                              → 0.53 gap, strong separator
  acousticness sim.  +1.0         continuous  0–1 scale; rock ≈ 0.10, lofi ≈ 0.75
                                              → 0.65 gap, LARGEST numeric separator
  tempo similarity   +0.5         continuous  58–178 BPM range; correlates with energy
                                              so half-weighted to avoid double-counting
  -----------------  ----------
  TOTAL MAX SCORE:   +6.0

Continuous features use: similarity = 1.0 - |song_value - target_value| / max_range
so a perfect match = full points, largest possible gap = 0 points.

TEMPO NORMALIZATION: divided by 120 (the dataset span: 178 - 58 = 120 BPM) so it
lives on the same 0–1 scale as energy and acousticness before applying the 0.5 cap.
"""

import csv
from typing import List, Dict, Tuple

# ---------------------------------------------------------------------------
# Data classes kept for test compatibility
# ---------------------------------------------------------------------------
from dataclasses import dataclass


@dataclass
class Song:
    """Represents a song and its attributes. Required by tests/test_recommender.py"""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a user's taste preferences. Required by tests/test_recommender.py"""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """OOP implementation of the recommendation logic. Required by tests/test_recommender.py"""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"


# ---------------------------------------------------------------------------
# Scoring constants (finalized recipe)
# ---------------------------------------------------------------------------
WEIGHT_GENRE        = 2.0   # binary: exact genre match
WEIGHT_MOOD         = 1.5   # binary: exact mood match
WEIGHT_ENERGY       = 1.0   # continuous: max awarded for perfect energy match
WEIGHT_ACOUSTICNESS = 1.0   # continuous: max awarded for perfect acousticness match
WEIGHT_TEMPO        = 0.5   # continuous: max awarded for perfect tempo match
TEMPO_RANGE         = 120.0 # dataset BPM span (178 - 58), used to normalize tempo


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file and returns a list of dictionaries.
    Numeric fields (energy, tempo_bpm, valence, danceability, acousticness)
    are cast to float; id is cast to int.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"]            = int(row["id"])
            row["energy"]        = float(row["energy"])
            row["tempo_bpm"]     = float(row["tempo_bpm"])
            row["valence"]       = float(row["valence"])
            row["danceability"]  = float(row["danceability"])
            row["acousticness"]  = float(row["acousticness"])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, str]:
    """
    Scores a single song against the user's taste profile.

    Returns (total_score, explanation_string).

    Scoring recipe (max 6.0 points):
      +2.0  genre match         (binary)
      +1.5  mood match          (binary)
      +0–1.0  energy proximity  (continuous, linear)
      +0–1.0  acousticness      (continuous, linear)
      +0–0.5  tempo proximity   (continuous, normalized to 120 BPM range)
    """
    score = 0.0
    reasons: List[str] = []

    # --- Categorical matches (binary) ---
    if song.get("genre", "").lower() == user_prefs.get("genre", "").lower():
        score += WEIGHT_GENRE
        reasons.append(f"genre match ({song['genre']})")

    if song.get("mood", "").lower() == user_prefs.get("mood", "").lower():
        score += WEIGHT_MOOD
        reasons.append(f"mood match ({song['mood']})")

    # --- Continuous similarity: energy ---
    if "target_energy" in user_prefs:
        energy_sim = 1.0 - abs(song["energy"] - user_prefs["target_energy"])
        energy_pts = energy_sim * WEIGHT_ENERGY
        score += energy_pts
        reasons.append(f"energy {song['energy']:.2f}~{user_prefs['target_energy']:.2f} (+{energy_pts:.2f})")

    # --- Continuous similarity: acousticness ---
    if "target_acousticness" in user_prefs:
        acoustic_sim = 1.0 - abs(song["acousticness"] - user_prefs["target_acousticness"])
        acoustic_pts = acoustic_sim * WEIGHT_ACOUSTICNESS
        score += acoustic_pts
        reasons.append(f"acousticness {song['acousticness']:.2f}~{user_prefs['target_acousticness']:.2f} (+{acoustic_pts:.2f})")

    # --- Continuous similarity: tempo (normalized by dataset range) ---
    if "target_tempo" in user_prefs:
        tempo_sim = max(0.0, 1.0 - abs(song["tempo_bpm"] - user_prefs["target_tempo"]) / TEMPO_RANGE)
        tempo_pts = tempo_sim * WEIGHT_TEMPO
        score += tempo_pts
        reasons.append(f"tempo {song['tempo_bpm']:.0f}~{user_prefs['target_tempo']:.0f} BPM (+{tempo_pts:.2f})")

    explanation = " | ".join(reasons) if reasons else "no matching features"
    return round(score, 3), explanation


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Scores all songs against user_prefs, then returns the top-k by score.

    Return format: [(song_dict, score, explanation), ...]
    Required by src/main.py
    """
    scored = [score_song(user_prefs, song) for song in songs]
    ranked = sorted(zip(songs, scored), key=lambda x: x[1][0], reverse=True)
    return [(song, score, explanation) for song, (score, explanation) in ranked[:k]]
