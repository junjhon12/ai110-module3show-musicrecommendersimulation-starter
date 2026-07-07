from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import csv

GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 1.5
ACOUSTIC_BONUS = 0.5

# Shared bonuses/penalties that apply no matter which scoring mode is active.
POPULARITY_WEIGHT = 1.0
POPULARITY_PENALTY = 1.0
DECADE_WEIGHT = 0.75
MOOD_TAG_WEIGHT = 0.5
INSTRUMENTAL_WEIGHT = 0.5
EXPLICIT_PENALTY = 1.5


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
    instrumentalness: float = 0.0
    popularity: int = 50
    release_decade: str = ""
    mood_tags: List[str] = field(default_factory=list)
    explicit: bool = False
    vocal_style: str = "vocals"


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
    favorite_decade: Optional[str] = None
    mood_tag_preferences: List[str] = field(default_factory=list)
    min_popularity: int = 0
    prefers_instrumental: Optional[bool] = None
    allow_explicit: bool = True


def _shared_feature_bonuses(user: UserProfile, song: Song) -> Tuple[float, List[str]]:
    """Scores the Challenge 1 attributes (popularity, decade, mood tags, vocal style,
    explicit content) the same way regardless of which ScoringStrategy is active."""
    score = 0.0
    reasons = []

    pop_points = (song.popularity / 100.0) * POPULARITY_WEIGHT
    score += pop_points
    reasons.append(f"popularity ({pop_points:+.2f})")

    if user.min_popularity and song.popularity < user.min_popularity:
        score -= POPULARITY_PENALTY
        reasons.append(f"below popularity floor (-{POPULARITY_PENALTY:.1f})")

    if user.favorite_decade and song.release_decade == user.favorite_decade:
        score += DECADE_WEIGHT
        reasons.append(f"decade match (+{DECADE_WEIGHT:.1f})")

    if user.mood_tag_preferences:
        matched = sorted(set(song.mood_tags) & set(user.mood_tag_preferences))
        if matched:
            tag_points = MOOD_TAG_WEIGHT * len(matched)
            score += tag_points
            reasons.append(f"mood tags {matched} (+{tag_points:.1f})")

    if user.prefers_instrumental is not None and song.instrumentalness > 0.5:
        if user.prefers_instrumental:
            score += INSTRUMENTAL_WEIGHT
            reasons.append(f"instrumental bonus (+{INSTRUMENTAL_WEIGHT:.1f})")
        else:
            score -= INSTRUMENTAL_WEIGHT
            reasons.append(f"instrumental penalty (-{INSTRUMENTAL_WEIGHT:.1f})")

    if not user.allow_explicit and song.explicit:
        score -= EXPLICIT_PENALTY
        reasons.append(f"explicit content penalty (-{EXPLICIT_PENALTY:.1f})")

    return score, reasons


class ScoringStrategy(ABC):
    """Strategy pattern: each mode implements its own weighting recipe over the
    same Song/UserProfile data so Recommender can swap modes at runtime."""

    name: str = "base"

    @abstractmethod
    def score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        raise NotImplementedError


class GenreFirstStrategy(ScoringStrategy):
    """Locked baseline recipe: genre is the strongest, most stable taste signal."""

    name = "Genre-First"

    def score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
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

        bonus, bonus_reasons = _shared_feature_bonuses(user, song)
        score += bonus
        reasons += bonus_reasons
        return score, reasons


class MoodFirstStrategy(ScoringStrategy):
    """Leads with mood/vibe: a user who cares more about "how it feels right now"
    than genre labels. Mood tag overlap counts double compared to Genre-First."""

    name = "Mood-First"

    def score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []

        if song.mood == user.favorite_mood:
            score += GENRE_WEIGHT
            reasons.append(f"mood match (+{GENRE_WEIGHT:.1f})")

        if song.genre == user.favorite_genre:
            score += MOOD_WEIGHT
            reasons.append(f"genre match (+{MOOD_WEIGHT:.1f})")

        energy_points = (1 - abs(song.energy - user.target_energy)) * MOOD_WEIGHT
        score += energy_points
        reasons.append(f"energy close to target ({energy_points:+.1f})")

        if song.acousticness > 0.5 and user.likes_acoustic:
            score += ACOUSTIC_BONUS
            reasons.append(f"acoustic bonus (+{ACOUSTIC_BONUS:.1f})")

        bonus, bonus_reasons = _shared_feature_bonuses(user, song)
        # Mood tags matter more in this mode, so double their contribution.
        score += bonus
        reasons += bonus_reasons
        if user.mood_tag_preferences:
            matched = sorted(set(song.mood_tags) & set(user.mood_tag_preferences))
            if matched:
                extra = MOOD_TAG_WEIGHT * len(matched)
                score += extra
                reasons.append(f"mood-first tag emphasis (+{extra:.1f})")

        return score, reasons


class EnergyFocusedStrategy(ScoringStrategy):
    """Leads with energy closeness (workout/focus playlists): genre and mood become
    tie-breakers instead of the primary signal."""

    name = "Energy-Focused"

    def score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []

        energy_points = (1 - abs(song.energy - user.target_energy)) * (ENERGY_WEIGHT * 2)
        score += energy_points
        reasons.append(f"energy close to target ({energy_points:+.1f})")

        if song.genre == user.favorite_genre:
            score += MOOD_WEIGHT * 0.5
            reasons.append(f"genre match (+{MOOD_WEIGHT * 0.5:.1f})")

        if song.mood == user.favorite_mood:
            score += MOOD_WEIGHT * 0.5
            reasons.append(f"mood match (+{MOOD_WEIGHT * 0.5:.1f})")

        if song.acousticness > 0.5 and not user.likes_acoustic:
            score -= ACOUSTIC_BONUS
            reasons.append(f"acoustic penalty (-{ACOUSTIC_BONUS:.1f})")

        bonus, bonus_reasons = _shared_feature_bonuses(user, song)
        score += bonus
        reasons += bonus_reasons
        return score, reasons


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song], strategy: Optional[ScoringStrategy] = None):
        self.songs = songs
        self.strategy = strategy or GenreFirstStrategy()

    def set_strategy(self, strategy: ScoringStrategy) -> None:
        self.strategy = strategy

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Scores one Song against a UserProfile, returning (score, reasons)."""
        return self.strategy.score(user, song)

    def recommend(
        self,
        user: UserProfile,
        k: int = 5,
        diversify: bool = False,
        artist_penalty: float = 0.75,
        genre_penalty: float = 0.4,
    ) -> List[Song]:
        """Ranks self.songs against a UserProfile and returns the top k Songs.

        When diversify=True, applies a greedy fairness re-ranking: each time a
        song is picked, its artist and genre counts go up, and future
        candidates from that same artist/genre are penalized before the next
        pick is chosen. This stops one artist/genre from flooding the top k.
        """
        scored = [(self._score(user, song)[0], song) for song in self.songs]

        if not diversify:
            scored.sort(key=lambda pair: pair[0], reverse=True)
            return [song for _, song in scored[:k]]

        remaining = list(scored)
        selected: List[Song] = []
        artist_counts: Dict[str, int] = {}
        genre_counts: Dict[str, int] = {}

        while remaining and len(selected) < k:
            best_index = 0
            best_adjusted = None
            for i, (base_score, song) in enumerate(remaining):
                penalty = (
                    artist_counts.get(song.artist, 0) * artist_penalty
                    + genre_counts.get(song.genre, 0) * genre_penalty
                )
                adjusted = base_score - penalty
                if best_adjusted is None or adjusted > best_adjusted:
                    best_adjusted = adjusted
                    best_index = i

            _, chosen_song = remaining.pop(best_index)
            selected.append(chosen_song)
            artist_counts[chosen_song.artist] = artist_counts.get(chosen_song.artist, 0) + 1
            genre_counts[chosen_song.genre] = genre_counts.get(chosen_song.genre, 0) + 1

        return selected

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable explanation of why a song scored the way it did."""
        score, reasons = self._score(user, song)
        return f"[{self.strategy.name}] Score {score:.2f}: " + ", ".join(reasons)


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
            if "popularity" in row:
                row["popularity"] = int(row["popularity"])
            if "explicit" in row:
                row["explicit"] = str(row["explicit"]).strip().lower() in ("true", "1", "yes")
            if "mood_tags" in row:
                row["mood_tags"] = [t.strip() for t in row["mood_tags"].split(";") if t.strip()]
            songs.append(row)
    return songs


def load_songs_as_objects(csv_path: str) -> List[Song]:
    """Loads songs from a CSV file directly into Song objects for the OOP/Strategy path."""
    songs = []
    for row in load_songs(csv_path):
        songs.append(Song(
            id=row["id"],
            title=row["title"],
            artist=row["artist"],
            genre=row["genre"],
            mood=row["mood"],
            energy=row["energy"],
            tempo_bpm=row["tempo_bpm"],
            valence=row["valence"],
            danceability=row["danceability"],
            acousticness=row["acousticness"],
            instrumentalness=row.get("instrumentalness", 0.0),
            popularity=row.get("popularity", 50),
            release_decade=row.get("release_decade", ""),
            mood_tags=row.get("mood_tags", []),
            explicit=row.get("explicit", False),
            vocal_style=row.get("vocal_style", "vocals"),
        ))
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
