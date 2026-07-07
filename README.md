# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommenders like Spotify or YouTube generally combine two strategies. **Collaborative filtering** predicts what a user will like based on patterns across *many users'* behavior — skips, likes, playlist co-occurrence — essentially "listeners like you also played X." It needs a large audience and struggles with new users or new items that have no history yet ("cold start"). **Content-based filtering** instead predicts preferences from the *attributes of the items themselves* (genre, tempo, mood, energy) matched against one user's own taste profile — it works even with a single user and no interaction history.

This project only has a 10-song catalog and one `UserProfile` per run, with no multi-user interaction data, so it implements **content-based filtering**: songs are recommended by matching song attributes directly against a user's stated preferences.

**Features used** (from `data/songs.csv`, mapped onto `Song`):

- `genre` — matched against `UserProfile.favorite_genre`
- `mood` — matched against `UserProfile.favorite_mood`
- `energy` — scored by *closeness* to `UserProfile.target_energy`
- `acousticness` — checked against `UserProfile.likes_acoustic`

(`tempo_bpm`, `valence`, and `danceability` also exist in the CSV but aren't modeled by `UserProfile` yet — good candidates for a future experiment.)

**Scoring rule (per song):**

- Categorical matches are binary: full points if `song.genre == user.favorite_genre`, else zero, and the same for mood. Genre is weighted higher than mood (e.g. 2.0 vs 1.0) since it's the stronger taste signal.
- The numeric `energy` feature is scored by *closeness to target*, not by raw magnitude — a user who wants medium energy shouldn't get the highest-energy song in the catalog. The rule is `closeness = 1 - abs(song.energy - user.target_energy)`, scaled by a weight (e.g. 1.5), so a song with `energy` equal to the target scores highest and the score falls off symmetrically as it drifts away.
- `acousticness` acts as a smaller bonus/penalty: a bonus if `likes_acoustic` is true and the song's acousticness is high, a small penalty otherwise — weighted lower than genre/mood since it's a softer preference.
- The total score is the weighted sum of these components, and `explain_recommendation` reports which components contributed (e.g. "genre match (+2.0), energy close to target (+1.2)").

**Scoring vs. ranking:** scoring is a *per-song* operation — given one song and one user profile, produce a single number (and reasons why). Ranking is a *list-level* operation — score every song in the catalog, sort descending, and take the top `k`. The system needs both: scoring alone doesn't decide an order, and ranking has nothing to sort until every song has a score.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



