"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "energetic", "energy": 0.9, "likes_acoustic": False},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.95, "likes_acoustic": False},
    # Adversarial / conflicting profiles (high energy paired with a sad/calm mood)
    "Energetic but Sad": {"genre": "pop", "mood": "sad", "energy": 0.9, "likes_acoustic": False},
    "Calm but Angry": {"genre": "classical", "mood": "angry", "energy": 0.15, "likes_acoustic": True},
}


def run_profile(name: str, user_prefs: dict, songs) -> None:
    recommendations = recommend_songs(user_prefs, songs, k=5)

    print(f"\n=== Profile: {name} ({user_prefs}) ===\n")
    for rank, (song, score, reasons) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} ({song['artist']}) - Score: {score:.2f}")
        print(f"   Because: {', '.join(reasons)}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for name, user_prefs in PROFILES.items():
        run_profile(name, user_prefs, songs)


if __name__ == "__main__":
    main()
