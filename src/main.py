"""
Command line runner for the Music Recommender Simulation.

Usage:
    python -m src.main                        # Genre-First mode, no diversity
    python -m src.main --mode mood             # Mood-First mode
    python -m src.main --mode energy --diversify
    python -m src.main --all-modes             # run every mode for comparison

Modes are implemented as a Strategy pattern in recommender.py
(GenreFirstStrategy, MoodFirstStrategy, EnergyFocusedStrategy) so new modes
can be added without touching Recommender itself.
"""

import argparse

from tabulate import tabulate

from src.recommender import (
    UserProfile,
    Recommender,
    GenreFirstStrategy,
    MoodFirstStrategy,
    EnergyFocusedStrategy,
    load_songs_as_objects,
)

STRATEGIES = {
    "genre": GenreFirstStrategy(),
    "mood": MoodFirstStrategy(),
    "energy": EnergyFocusedStrategy(),
}

PROFILES = {
    "High-Energy Pop": UserProfile(
        favorite_genre="pop", favorite_mood="energetic", target_energy=0.9,
        likes_acoustic=False, favorite_decade="2020s", min_popularity=60,
    ),
    "Chill Lofi": UserProfile(
        favorite_genre="lofi", favorite_mood="chill", target_energy=0.35,
        likes_acoustic=True, mood_tag_preferences=["focused", "cozy"],
    ),
    "Deep Intense Rock": UserProfile(
        favorite_genre="rock", favorite_mood="intense", target_energy=0.95,
        likes_acoustic=False, prefers_instrumental=False,
    ),
    # Adversarial / conflicting profiles (high energy paired with a sad/calm mood)
    "Energetic but Sad": UserProfile(
        favorite_genre="pop", favorite_mood="sad", target_energy=0.9, likes_acoustic=False,
    ),
    "Calm but Angry": UserProfile(
        favorite_genre="classical", favorite_mood="angry", target_energy=0.15,
        likes_acoustic=True, prefers_instrumental=True,
    ),
}


def print_recommendations(name: str, user: UserProfile, songs, strategy, diversify: bool) -> None:
    recommender = Recommender(songs, strategy=strategy)
    results = recommender.recommend(user, k=5, diversify=diversify)

    rows = []
    for rank, song in enumerate(results, start=1):
        score, reasons = strategy.score(user, song)
        rows.append([rank, song.title, song.artist, song.genre, f"{score:.2f}", ", ".join(reasons)])

    header = f"Profile: {name}  |  Mode: {strategy.name}  |  Diversify: {diversify}"
    print(f"\n=== {header} ===")
    print(tabulate(rows, headers=["#", "Title", "Artist", "Genre", "Score", "Why"], tablefmt="grid"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Music Recommender Simulation CLI")
    parser.add_argument("--mode", choices=STRATEGIES.keys(), default="genre",
                         help="Scoring strategy to use (default: genre)")
    parser.add_argument("--all-modes", action="store_true",
                         help="Run every scoring mode for each profile, for comparison")
    parser.add_argument("--diversify", action="store_true",
                         help="Apply artist/genre diversity penalty to avoid filter bubbles")
    args = parser.parse_args()

    songs = load_songs_as_objects("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    modes_to_run = list(STRATEGIES.values()) if args.all_modes else [STRATEGIES[args.mode]]

    for name, user in PROFILES.items():
        for strategy in modes_to_run:
            print_recommendations(name, user, songs, strategy, args.diversify)


if __name__ == "__main__":
    main()
