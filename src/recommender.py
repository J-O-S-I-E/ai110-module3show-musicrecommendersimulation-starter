"""
Music Recommender — Scoring Logic
===================================

ALGORITHM RECIPE (balanced mode, max 9.0 pts)
----------------------------------------------
Feature               Max Pts   Type        Notes
--------------------  --------  ----------  -----------------------------------
genre match            2.0      binary      14 genres — highest specificity
mood match             1.5      binary      12 moods, cross-genre overlap
energy similarity      1.0      continuous  0-1 scale; linear distance
acousticness sim.      1.0      continuous  0-1 scale; linear distance
tempo similarity       0.5      continuous  normalized to 120 BPM dataset range
popularity sim.        0.5      continuous  0-100 scale; linear distance
decade similarity      0.5      continuous  penalty per decade away from target
mood tag overlap       1.0      set-based   proportion of desired tags present
lyrical complexity     0.5      continuous  0-1 scale; linear distance
live feel similarity   0.5      continuous  0-1 scale; linear distance
--------------------  --------  ----------  -----------------------------------
TOTAL MAX:             9.0

SCORING MODES (Challenge 2 — Strategy Pattern)
-----------------------------------------------
Each mode is a weight dictionary that rescales feature contributions.
Pass mode="genre_first" to recommend_songs to shift the recipe.
  balanced      — default, all features weighted as above
  genre_first   — doubles genre weight, halves continuous features
  mood_first    — triples mood weight, doubles mood_tags weight
  energy_focused — maximises energy/acousticness/tempo, ignores era
  discovery     — minimises genre/popularity, rewards sonic surprise

DIVERSITY PENALTY (Challenge 3)
--------------------------------
When diversity_penalty=True, songs by an artist already present in the
selected top-k receive a 30% score reduction. This prevents the list from
being dominated by a single artist in catalogs with many songs per artist.

VISUAL OUTPUT (Challenge 4)
-----------------------------
format_table() uses tabulate when available, falling back to aligned ASCII.
"""

import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Data classes (backward-compatible: new Song fields have defaults)
# ---------------------------------------------------------------------------

@dataclass
class Song:
    """Represents a song and all its attributes, including the five new advanced fields."""
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
    # Advanced fields (Challenge 1) — defaults keep existing tests passing
    popularity: int = 50
    decade: int = 2020
    mood_tags: str = ""
    lyrical_complexity: float = 0.5
    live_feel: float = 0.5


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
# Scoring constants — balanced mode defaults
# ---------------------------------------------------------------------------
WEIGHT_GENRE             = 2.0   # binary: exact genre match
WEIGHT_MOOD              = 1.5   # binary: exact mood match
WEIGHT_ENERGY            = 1.0   # continuous: perfect energy match
WEIGHT_ACOUSTICNESS      = 1.0   # continuous: perfect acousticness match
WEIGHT_TEMPO             = 0.5   # continuous: perfect tempo match
WEIGHT_POPULARITY        = 0.5   # continuous: closeness to target popularity
WEIGHT_DECADE            = 0.5   # continuous: proximity to preferred decade
WEIGHT_MOOD_TAGS         = 1.0   # set-based: proportion of desired tags present
WEIGHT_LYRICAL_COMPLEXITY= 0.5   # continuous: closeness to target complexity
WEIGHT_LIVE_FEEL         = 0.5   # continuous: closeness to target live feel
TEMPO_RANGE              = 120.0 # dataset BPM span (178 - 58)


# ---------------------------------------------------------------------------
# CHALLENGE 2 — Scoring Mode Strategy Pattern
# ---------------------------------------------------------------------------

SCORING_MODES: Dict[str, Dict[str, float]] = {
    "balanced": {
        # Default: all features weighted at design values (max 9.0 pts)
        "genre": 2.0, "mood": 1.5, "energy": 1.0,
        "acousticness": 1.0, "tempo": 0.5,
        "popularity": 0.5, "decade": 0.5,
        "mood_tags": 1.0, "lyrical_complexity": 0.5, "live_feel": 0.5,
    },
    "genre_first": {
        # Genre dominates; continuous features are background signals
        "genre": 4.0, "mood": 1.5, "energy": 0.5,
        "acousticness": 0.5, "tempo": 0.25,
        "popularity": 0.25, "decade": 0.25,
        "mood_tags": 0.5, "lyrical_complexity": 0.0, "live_feel": 0.25,
    },
    "mood_first": {
        # Mood and mood-tags together dominate; genre is a weaker tiebreaker
        "genre": 1.0, "mood": 3.0, "energy": 0.75,
        "acousticness": 0.75, "tempo": 0.25,
        "popularity": 0.25, "decade": 0.25,
        "mood_tags": 2.0, "lyrical_complexity": 0.25, "live_feel": 0.25,
    },
    "energy_focused": {
        # Sonic intensity features dominate; era and lyrics are ignored
        "genre": 1.0, "mood": 0.75, "energy": 2.5,
        "acousticness": 1.5, "tempo": 1.0,
        "popularity": 0.25, "decade": 0.0,
        "mood_tags": 0.5, "lyrical_complexity": 0.0, "live_feel": 0.5,
    },
    "discovery": {
        # Low genre/popularity weight encourages cross-genre sonic matches
        "genre": 0.5, "mood": 1.0, "energy": 1.5,
        "acousticness": 1.5, "tempo": 0.75,
        "popularity": 0.0, "decade": 0.0,
        "mood_tags": 1.5, "lyrical_complexity": 0.5, "live_feel": 1.0,
    },
}


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """
    Load songs from a CSV file; cast all numeric fields so math works downstream.
    Handles both the original 10-column format and the extended 15-column format.
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"]           = int(row["id"])
            row["energy"]       = float(row["energy"])
            row["tempo_bpm"]    = float(row["tempo_bpm"])
            row["valence"]      = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            # Advanced fields — only present in extended CSV
            if "popularity" in row:
                row["popularity"]         = int(row["popularity"])
                row["decade"]             = int(row["decade"])
                row["lyrical_complexity"] = float(row["lyrical_complexity"])
                row["live_feel"]          = float(row["live_feel"])
                # mood_tags stays as a plain string; callers split on ","
            songs.append(row)
    return songs


def score_song(
    user_prefs: Dict,
    song: Dict,
    weights: Optional[Dict[str, float]] = None,
) -> Tuple[float, List[str]]:
    """
    Score a single song against the user's taste profile and return
    (total_score, reasons) where reasons is a list of human-readable strings
    describing every awarded point, e.g. "genre match (+2.0)".

    The optional weights dict lets callers override the default (balanced) recipe.
    Any key absent from weights defaults to the balanced-mode value so callers
    can supply partial overrides safely.

    Max score depends on which user_prefs keys are present and the active weights.
    Balanced max: 9.0 pts across 10 features.
    """
    w = SCORING_MODES["balanced"].copy()
    if weights:
        w.update(weights)

    score = 0.0
    reasons: List[str] = []

    # --- Binary categorical matches ---
    if song.get("genre", "").lower() == user_prefs.get("genre", "").lower():
        pts = w["genre"]
        score += pts
        reasons.append(f"genre match (+{pts})")

    if song.get("mood", "").lower() == user_prefs.get("mood", "").lower():
        pts = w["mood"]
        score += pts
        reasons.append(f"mood match (+{pts})")

    # --- Continuous: energy (0-1, no normalization needed) ---
    if "target_energy" in user_prefs:
        pts = (1.0 - abs(song["energy"] - user_prefs["target_energy"])) * w["energy"]
        score += pts
        reasons.append(f"energy similarity (+{pts:.2f})")

    # --- Continuous: acousticness (0-1, no normalization needed) ---
    if "target_acousticness" in user_prefs:
        pts = (1.0 - abs(song["acousticness"] - user_prefs["target_acousticness"])) * w["acousticness"]
        score += pts
        reasons.append(f"acousticness similarity (+{pts:.2f})")

    # --- Continuous: tempo (normalized by 120 BPM dataset range) ---
    if "target_tempo" in user_prefs:
        pts = max(0.0, 1.0 - abs(song["tempo_bpm"] - user_prefs["target_tempo"]) / TEMPO_RANGE) * w["tempo"]
        score += pts
        reasons.append(f"tempo similarity (+{pts:.2f})")

    # --- CHALLENGE 1: Advanced features ---

    # Popularity — continuous similarity on 0-100 scale
    if "target_popularity" in user_prefs and "popularity" in song:
        pts = (1.0 - abs(song["popularity"] - user_prefs["target_popularity"]) / 100.0) * w["popularity"]
        score += pts
        reasons.append(f"popularity similarity (+{pts:.2f})")

    # Decade — graduated penalty per decade away from target
    if "preferred_decade" in user_prefs and "decade" in song:
        decades_away = abs(int(song["decade"]) - int(user_prefs["preferred_decade"])) / 10
        pts = max(0.0, 1.0 - decades_away * 0.3) * w["decade"]
        score += pts
        reasons.append(f"era match {song['decade']}s (+{pts:.2f})")

    # Mood tags — proportion of desired tags that appear in the song's tag string
    if "desired_tags" in user_prefs and "mood_tags" in song:
        desired = set(t.strip().lower() for t in user_prefs["desired_tags"])
        present = set(t.strip().lower() for t in song["mood_tags"].split(","))
        overlap = len(desired & present)
        if desired:
            pts = (overlap / len(desired)) * w["mood_tags"]
            score += pts
            matched = desired & present
            reasons.append(f"mood tags {sorted(matched)} (+{pts:.2f})")

    # Lyrical complexity — continuous similarity on 0-1 scale
    if "target_lyrical_complexity" in user_prefs and "lyrical_complexity" in song:
        pts = (1.0 - abs(song["lyrical_complexity"] - user_prefs["target_lyrical_complexity"])) * w["lyrical_complexity"]
        score += pts
        reasons.append(f"lyrical complexity (+{pts:.2f})")

    # Live feel — continuous similarity on 0-1 scale
    if "target_live_feel" in user_prefs and "live_feel" in song:
        pts = (1.0 - abs(song["live_feel"] - user_prefs["target_live_feel"])) * w["live_feel"]
        score += pts
        reasons.append(f"live feel (+{pts:.2f})")

    return round(score, 3), reasons


# ---------------------------------------------------------------------------
# CHALLENGE 3 — Diversity Penalty
# ---------------------------------------------------------------------------

def _apply_diversity_penalty(
    ranked: List[Tuple[Dict, float, List[str]]],
    penalty: float = 0.70,
) -> List[Tuple[Dict, float, List[str]]]:
    """
    Reduce the score of any song whose artist already appears earlier in the
    ranked list. Applied after initial scoring so the original score drives the
    first selection, and only duplicates are penalised.

    penalty=0.70 means a repeat artist's score is multiplied by 0.70 (30% off).
    Returns a re-sorted list with the adjusted scores and updated reason lists.
    """
    seen_artists: set = set()
    adjusted: List[Tuple[Dict, float, List[str]]] = []

    for song, score, reasons in ranked:
        artist = song.get("artist", "")
        if artist in seen_artists:
            new_score = round(score * penalty, 3)
            new_reasons = reasons + [f"diversity penalty x{penalty} (artist repeat)"]
            adjusted.append((song, new_score, new_reasons))
        else:
            seen_artists.add(artist)
            adjusted.append((song, score, reasons))

    return sorted(adjusted, key=lambda x: x[1], reverse=True)


# ---------------------------------------------------------------------------
# Main recommendation entry point
# ---------------------------------------------------------------------------

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = "balanced",
    diversity_penalty: bool = False,
) -> List[Tuple[Dict, float, List[str]]]:
    """
    Score every song in the catalog, apply optional mode weights and diversity
    penalty, then return the top k results sorted highest-to-lowest.

    Parameters
    ----------
    user_prefs       : taste profile dict (genre, mood, target_energy, …)
    songs            : list of song dicts from load_songs()
    k                : number of results to return
    mode             : one of "balanced", "genre_first", "mood_first",
                       "energy_focused", "discovery"  (Challenge 2)
    diversity_penalty: if True, repeat-artist songs lose 30% of their score
                       (Challenge 3)

    Return format: [(song_dict, score, reasons), ...]

    --- sorted() vs .sort() ---
    sorted() returns a NEW list and does not mutate the input. .sort() mutates
    in-place and returns None. We use sorted() so the caller's songs list is
    untouched and we can chain the result directly into a slice.
    """
    weights = SCORING_MODES.get(mode, SCORING_MODES["balanced"])

    # Score every song; * unpacks (score, reasons) into a flat 3-tuple
    scored = [(song, *score_song(user_prefs, song, weights)) for song in songs]

    # Sort by score, highest first
    ranked = sorted(scored, key=lambda entry: entry[1], reverse=True)

    # Optionally demote repeat artists (Challenge 3)
    if diversity_penalty:
        ranked = _apply_diversity_penalty(ranked)

    return ranked[:k]


# ---------------------------------------------------------------------------
# CHALLENGE 4 — Visual Summary Table
# ---------------------------------------------------------------------------

def format_table(
    recommendations: List[Tuple[Dict, float, List[str]]],
    mode_name: str = "balanced",
    max_reasons: int = 3,
) -> str:
    """
    Format top-k recommendations as a readable table.

    Uses the tabulate library when available; falls back to aligned ASCII.
    max_reasons controls how many scoring reasons are shown per row.
    """
    rows = []
    for rank, (song, score, reasons) in enumerate(recommendations, 1):
        reason_str = " | ".join(reasons[:max_reasons])
        if len(reasons) > max_reasons:
            reason_str += f" (+{len(reasons) - max_reasons} more)"
        rows.append([
            f"#{rank}",
            song["title"],
            song["artist"],
            f"{song['genre']} / {song['mood']}",
            f"{score:.2f}",
            reason_str,
        ])

    headers = ["Rank", "Title", "Artist", "Genre / Mood", "Score", "Top Reasons"]

    try:
        from tabulate import tabulate
        return tabulate(rows, headers=headers, tablefmt="simple", maxcolwidths=[4, 22, 18, 20, 7, 50])
    except ImportError:
        # Pure-ASCII fallback — fixed-width columns
        col_widths = [5, 24, 20, 22, 7, 52]
        sep = "  ".join("-" * w for w in col_widths)
        header_row = "  ".join(h.ljust(w) for h, w in zip(headers, col_widths))
        lines = [header_row, sep]
        for row in rows:
            lines.append("  ".join(str(c).ljust(w) for c, w in zip(row, col_widths)))
        return "\n".join(lines)
