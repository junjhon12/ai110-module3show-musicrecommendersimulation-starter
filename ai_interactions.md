# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Push the recommender further with four stretch challenges in one pass: (1) add 5+ new song attributes to `data/songs.csv` and wire them into scoring, (2) add multiple toggleable scoring modes in `main.py`, (3) add a diversity/fairness penalty so one artist or genre can't flood the top-5, and (4) format the CLI output as a readable table that still shows the score reasons.

**Prompts used:**

- "Explore the current project structure — read data/songs.csv, src/recommender.py, src/main.py, ai_interactions.md, tests/test_recommender.py, requirements.txt, and README.md — before making changes."
- "Add 5+ new complex attributes to songs.csv (popularity 0-100, release decade, detailed mood tags, explicit flag, vocal style) and update recommender.py so the scoring recipe accounts for them, without breaking the existing Song/UserProfile dataclasses that tests/test_recommender.py constructs with the old fields."
- "Attach recommender.py — suggest a modular design pattern (Strategy pattern) so I can support Genre-First, Mood-First, and Energy-Focused scoring modes that main.py can toggle between via a CLI flag, without duplicating the per-song scoring logic three times."
- "Write a rule that penalizes a song's final score if its artist or genre is already heavily represented in the top K list being built, so recommendations don't turn into a filter bubble of one artist."
- "Suggest a way to format the top recommendations using tabulate, and make sure the table's Why column still shows the same human-readable reasons string that explain_recommendation produces — don't drop that data for the sake of a cleaner table."

**What did the agent generate or change?**

- `data/songs.csv`: added `popularity`, `release_decade`, `mood_tags` (semicolon-separated tags like `nostalgic;wistful`), `explicit`, and `vocal_style` columns for all 20 songs.
- `src/recommender.py`: extended `Song` and `UserProfile` with new optional/default fields (backward compatible with the old constructor calls in tests), added a `_shared_feature_bonuses()` helper that scores popularity, decade match, mood-tag overlap, instrumental preference, and an explicit-content penalty, added a `ScoringStrategy` ABC plus three concrete strategies (`GenreFirstStrategy`, `MoodFirstStrategy`, `EnergyFocusedStrategy`), changed `Recommender` to hold a swappable `strategy` and delegate scoring to it, and added a diversity re-ranking option (`recommend(..., diversify=True)`) that greedily re-scores remaining candidates each round using running artist/genre counts. Added `load_songs_as_objects()` to build `Song` objects straight from the CSV for the new OOP/Strategy pipeline, and kept the original dict-based `load_songs`/`score_song`/`recommend_songs` functions untouched for backward compatibility.
- `src/main.py`: rewritten to build `UserProfile` objects (some exercising the new decade/mood-tag/instrumental/popularity-floor preferences), added `argparse` flags `--mode {genre,mood,energy}`, `--all-modes`, and `--diversify`, and replaced the plain `print()` output with a `tabulate` grid table showing rank, title, artist, genre, score, and the "Why" reasons string per song.
- `requirements.txt`: added `tabulate`.

**What did I verify or fix manually?**

- Ran `pytest` after the dataclass changes to confirm the two existing tests in `tests/test_recommender.py` still pass unmodified — this only works because the new `Song`/`UserProfile` fields were added *after* the required fields with defaults, so old positional/keyword construction still works.
- The agent's first table used `tablefmt="fancy_grid"`, which uses Unicode box-drawing characters; running `python -m src.main` on this Windows terminal (cp1252 codepage) raised `UnicodeEncodeError`. Fixed by switching to `tablefmt="grid"` (plain ASCII), then re-ran the CLI to confirm the table prints cleanly.
- Manually ran `python -m src.main --mode genre`, `--mode mood`, `--mode energy`, and `--mode genre --diversify` to confirm the three modes actually produce different rankings/reasons, and confirmed the diversify flag visibly moves a second Neon Echo song down out of the top-3 for the "High-Energy Pop" profile, letting a different artist (DJ Kairo) surface earlier — this is the concrete "before/after" evidence that the fairness penalty works, not just that the code runs without errors.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

Strategy pattern.

**How did AI help you brainstorm or implement it?**

I described the problem — three different scoring "recipes" that need to share the same Song/UserProfile data and the same `Recommender.recommend()`/`explain_recommendation()` call sites, without copy-pasting the ranking/sorting logic three times or writing a long if/elif chain inside `_score()`. The AI suggested the Strategy pattern specifically because the *thing that varies* (how a song is weighted) is cleanly separable from the *thing that stays fixed* (collecting scores across the catalog, sorting, slicing to top-k, and building the diversity-adjusted ranking) — that fixed part now lives once in `Recommender.recommend()` regardless of which strategy is plugged in. It proposed an abstract `ScoringStrategy` base class with a single `score(user, song) -> (float, reasons)` method, three concrete subclasses that each set different weights on the same feature set, and a small shared helper function for the new attributes (popularity, decade, mood tags, instrumental/vocal preference) so all three strategies would benefit from Challenge 1's features without triplicating that logic too.

**How does the pattern appear in your final code?**

`src/recommender.py`: `ScoringStrategy` (abstract base with `score()`), `GenreFirstStrategy`, `MoodFirstStrategy`, and `EnergyFocusedStrategy` (concrete strategies, each reweighting genre/mood/energy differently). `Recommender.__init__` takes a `strategy` argument and stores it on `self.strategy`; `Recommender.set_strategy()` allows swapping at runtime; `_score()` and `explain_recommendation()` both delegate to `self.strategy.score(...)` instead of containing their own scoring math. `src/main.py` picks the active strategy from a `STRATEGIES` dict keyed by the `--mode` CLI flag (or loops over all of them with `--all-modes`) and passes it straight into `Recommender(songs, strategy=...)` — adding a fourth mode later only means writing one new `ScoringStrategy` subclass, with no changes to `Recommender` or `main.py`'s table-printing code.
