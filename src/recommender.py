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
        """Store the song catalog that this recommender will rank against."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs for the given user profile (not yet implemented)."""
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a plain-language explanation of why song was recommended to user."""
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


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against the user's taste profile.

    Returns (total_score, reasons) where reasons is a human-readable list
    explaining every point awarded, e.g.:
        ["genre match (+2.0)", "mood match (+1.5)", "energy similarity (+0.96)"]

    Scoring recipe (max 6.0 points):
      +2.0        genre match        binary — exact string comparison
      +1.5        mood match         binary — exact string comparison
      +0.0–+1.0   energy proximity   continuous: (1 - |song - target|) * 1.0
      +0.0–+1.0   acousticness       continuous: (1 - |song - target|) * 1.0
      +0.0–+0.5   tempo proximity    continuous: (1 - |song - target| / 120) * 0.5
    """
    score = 0.0
    reasons: List[str] = []

    # --- Binary matches: full points or nothing ---
    if song.get("genre", "").lower() == user_prefs.get("genre", "").lower():
        score += WEIGHT_GENRE
        reasons.append(f"genre match (+{WEIGHT_GENRE})")

    if song.get("mood", "").lower() == user_prefs.get("mood", "").lower():
        score += WEIGHT_MOOD
        reasons.append(f"mood match (+{WEIGHT_MOOD})")

    # --- Continuous similarity: energy (0–1 scale, no normalization needed) ---
    if "target_energy" in user_prefs:
        energy_pts = (1.0 - abs(song["energy"] - user_prefs["target_energy"])) * WEIGHT_ENERGY
        score += energy_pts
        reasons.append(f"energy similarity (+{energy_pts:.2f})")

    # --- Continuous similarity: acousticness (0–1 scale, no normalization needed) ---
    if "target_acousticness" in user_prefs:
        acoustic_pts = (1.0 - abs(song["acousticness"] - user_prefs["target_acousticness"])) * WEIGHT_ACOUSTICNESS
        score += acoustic_pts
        reasons.append(f"acousticness similarity (+{acoustic_pts:.2f})")

    # --- Continuous similarity: tempo (normalized by 120 BPM dataset range) ---
    if "target_tempo" in user_prefs:
        tempo_pts = max(0.0, 1.0 - abs(song["tempo_bpm"] - user_prefs["target_tempo"]) / TEMPO_RANGE) * WEIGHT_TEMPO
        score += tempo_pts
        reasons.append(f"tempo similarity (+{tempo_pts:.2f})")

    return round(score, 3), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, List[str]]]:
    """
    Scores every song in the catalog, ranks them highest-to-lowest, and
    returns the top k results.

    Return format: [(song_dict, score, reasons), ...]
    where reasons is the List[str] produced by score_song.
    Required by src/main.py

    --- sorted() vs .sort() ---
    list.sort()  mutates the list IN PLACE and returns None.
                 Using it here would destroy the caller's original songs list
                 and give us nothing to return.
    sorted()     leaves the input untouched and returns a NEW sorted list.
                 It also accepts any iterable (lists, generators, zip objects),
                 making it the right tool whenever the sorted result is a
                 separate value rather than a replacement for the original.
    """
    # score_song returns (score, reasons); the * unpacks that pair inline so
    # each element is already the flat 3-tuple (song, score, reasons) we need.
    scored = [(song, *score_song(user_prefs, song)) for song in songs]

    # Sort by score (index 1), highest first. sorted() does not touch `scored`.
    ranked = sorted(scored, key=lambda entry: entry[1], reverse=True)

    # Slice to the top k results.
    return ranked[:k]
