from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 1.5
ACOUSTIC_BONUS = 0.5


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
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
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Scores one Song against a UserProfile, returning (score, reasons)."""
        score = 0.0
        reasons = []

        if song.genre == user.favorite_genre:
            score += GENRE_WEIGHT
            reasons.append(f"genre match (+{GENRE_WEIGHT:.1f})")

        if song.mood == user.favorite_mood:
            score += MOOD_WEIGHT
            reasons.append(f"mood match (+{MOOD_WEIGHT:.1f})")

        energy_points = (1 - abs(song.energy - user.target_energy)) * ENERGY_WEIGHT
        score += energy_points
        reasons.append(f"energy close to target ({energy_points:+.1f})")

        if song.acousticness > 0.5:
            if user.likes_acoustic:
                score += ACOUSTIC_BONUS
                reasons.append(f"acoustic bonus (+{ACOUSTIC_BONUS:.1f})")
            else:
                score -= ACOUSTIC_BONUS
                reasons.append(f"acoustic penalty (-{ACOUSTIC_BONUS:.1f})")

        return score, reasons

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Ranks self.songs against a UserProfile and returns the top k Songs."""
        scored = [(self._score(user, song)[0], song) for song in self.songs]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [song for _, song in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable explanation of why a song scored the way it did."""
        score, reasons = self._score(user, song)
        return f"Score {score:.2f}: " + ", ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Loads songs from a CSV file into a list of dicts with numeric fields cast to float/int."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            if "instrumentalness" in row:
                row["instrumentalness"] = float(row["instrumentalness"])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores a single song dict against user_prefs, returning (score, reasons)."""
    score = 0.0
    reasons = []

    if song["genre"] == user_prefs.get("genre"):
        score += GENRE_WEIGHT
        reasons.append(f"genre match (+{GENRE_WEIGHT:.1f})")

    if song["mood"] == user_prefs.get("mood"):
        score += MOOD_WEIGHT
        reasons.append(f"mood match (+{MOOD_WEIGHT:.1f})")

    target_energy = user_prefs.get("energy", 0.5)
    energy_points = (1 - abs(song["energy"] - target_energy)) * ENERGY_WEIGHT
    score += energy_points
    reasons.append(f"energy match ({energy_points:+.1f})")

    likes_acoustic = user_prefs.get("likes_acoustic")
    if likes_acoustic is not None and song["acousticness"] > 0.5:
        if likes_acoustic:
            score += ACOUSTIC_BONUS
            reasons.append(f"acoustic bonus (+{ACOUSTIC_BONUS:.1f})")
        else:
            score -= ACOUSTIC_BONUS
            reasons.append(f"acoustic penalty (-{ACOUSTIC_BONUS:.1f})")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, List[str]]]:
    """Scores every song against user_prefs and returns the top k as (song, score, reasons)."""
    scored = [(song, *score_song(user_prefs, song)) for song in songs]
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
