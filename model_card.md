# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatch 1.0**

---

## 2. Intended Use  

VibeMatch takes one user's stated taste (favorite genre, favorite mood, target energy, whether they like acoustic songs) and ranks a fixed 20-song catalog to surface the 5 songs that best match that taste. It assumes the user can describe their taste in those four terms and that their taste is fixed for the session — it does not learn from listening history or skips. This is a classroom exploration of content-based filtering, not a production recommender: the catalog is small and hand-authored, so it is meant to demonstrate how scoring and ranking logic works, not to actually recommend music to real listeners.

---

## 3. How the Model Works  

Think of each song as a little profile card: genre, mood, how energetic it feels, and how "acoustic" (unplugged/organic) it sounds. The user also fills out a card: their favorite genre, favorite mood, how much energy they want, and whether they like acoustic songs. VibeMatch compares the two cards and hands out points: 2 points if the genres match, 1 point if the moods match, and up to 1.5 points based on how close the song's energy is to the energy the user asked for (an exact match earns the full 1.5, and the points shrink the further apart they are). If the song is heavily acoustic, it gets a small half-point bonus or penalty depending on whether the user said they like acoustic music. Every song in the catalog gets scored this way, then they're sorted highest to lowest and the top 5 are shown, each with a plain-English list of why it scored the way it did. The only change from the starter logic was documented in the README/AI interactions: the genre/mood/energy/acoustic weighting itself is the "recipe" we built and tuned, not something inherited unmodified from a template.

---

## 4. Data  

The catalog (`data/songs.csv`) has 20 songs across roughly 15 different genres (pop, lofi, rock, ambient, jazz, synthwave, indie pop, metal, r&b, country, folk, edm, blues, reggae, classical), so most genres are represented by only one or two songs. Moods range from happy, chill, intense, energetic, and moody to sad, angry, romantic, nostalgic, melancholic, and calm. The catalog was expanded from a smaller starter set to add genre/mood variety and an `instrumentalness` column (for songs with little or no vocals, like the classical remix). What's missing: there's no representation of lyrical content, cultural or language context, or artist popularity, and because each genre has so few entries, the catalog can't really represent *variety within* a genre (e.g., "chill pop" vs. "upbeat pop").

---

## 5. Strengths  

For users whose taste maps cleanly onto one genre and one mood — the "Chill Lofi" profile (genre=lofi, mood=chill, energy=0.35, likes_acoustic=True) is the clearest example — the top results feel exactly right: `Library Rain` and `Midnight Coding` are both lofi, chill, low-energy, and acoustic, so they sweep every scoring category and land at #1 and #2 with a wide score gap over anything else. The continuous energy-closeness scoring (instead of a simple high/low bucket) also does its job well — for "Deep Intense Rock" (energy=0.95), the ranking correctly favors `Storm Runner` (energy 0.91) over lower-energy rock-adjacent songs, tracking energy as a spectrum rather than a category. The acoustic bonus/penalty is a nice light touch: it nudges the ranking without ever overriding genre or mood.

---

## 6. Limitations and Bias 

The clearest weakness I found through testing is a **genre-scarcity filter bubble**: because `GENRE_WEIGHT` (2.0) is the single largest scoring component and most genres in the 20-song catalog have only one representative, a user whose favorite genre happens to be a rare one (e.g. classical, edm, metal) gets that one song crowned the top recommendation almost by default, regardless of whether its mood or energy actually fits. This showed up directly in the "Calm but Angry" adversarial test: the profile asked for `genre=classical, mood=angry, energy=0.15`, and `Moonlight Sonata Remix` won #1 purely on the genre match plus energy closeness — the "angry" mood was never satisfied by anything (classical has only that one song and it's tagged "calm"), but the recommender has no way to say "no good match exists for this mood," so it silently ranks best-available as if it were a great fit. A related bias appeared in the "Energetic but Sad" test: no pop song in the catalog is tagged "sad," so the `mood` preference contributed exactly 0 points to every candidate and the final ranking was driven entirely by genre and energy — the user's stated mood was effectively ignored without any indication to them that it happened. The system can also unintentionally favor prolific artists: three of the four "pop" songs in the catalog are by Neon Echo, so any pop-genre profile returns a top-5 list dominated by one artist, which is an artist-level filter bubble rather than a genre-level one. Finally, the energy-gap calculation treats "energy" as the only spectrum-scored feature — tempo, valence, and danceability exist in the data but are never used, so two songs with wildly different moods can tie on energy and be ranked as equally good matches.

---

## 7. Evaluation  

I tested five profiles through `src/main.py`: three "normal" tastes (**High-Energy Pop**, **Chill Lofi**, **Deep Intense Rock**) and two AI-suggested adversarial profiles with internally conflicting preferences (**Energetic but Sad** — high energy pop but a sad mood, and **Calm but Angry** — very low energy classical but an angry mood), meant to stress-test what happens when a user's stated mood doesn't match their stated genre/energy.

```
=== Profile: High-Energy Pop ({'genre': 'pop', 'mood': 'energetic', 'energy': 0.9, 'likes_acoustic': False}) ===

1. Heartbeat Overdrive (Neon Echo) - Score: 4.47
   Because: genre match (+2.0), mood match (+1.0), energy match (+1.5)
2. Gym Hero (Max Pulse) - Score: 3.46
   Because: genre match (+2.0), energy match (+1.5)
3. Sunrise City (Neon Echo) - Score: 3.38
   Because: genre match (+2.0), energy match (+1.4)
4. Neon Pulse (DJ Kairo) - Score: 2.42
   Because: mood match (+1.0), energy match (+1.4)
5. Storm Runner (Voltline) - Score: 1.48
   Because: energy match (+1.5)
```

```
=== Profile: Chill Lofi ({'genre': 'lofi', 'mood': 'chill', 'energy': 0.35, 'likes_acoustic': True}) ===

1. Library Rain (Paper Lanterns) - Score: 5.00
   Because: genre match (+2.0), mood match (+1.0), energy match (+1.5), acoustic bonus (+0.5)
2. Midnight Coding (LoRoom) - Score: 4.89
   Because: genre match (+2.0), mood match (+1.0), energy match (+1.4), acoustic bonus (+0.5)
3. Focus Flow (LoRoom) - Score: 3.92
   Because: genre match (+2.0), energy match (+1.4), acoustic bonus (+0.5)
4. Spacewalk Thoughts (Orbit Bloom) - Score: 2.90
   Because: mood match (+1.0), energy match (+1.4), acoustic bonus (+0.5)
5. Coffee Shop Stories (Slow Stereo) - Score: 1.97
   Because: energy match (+1.5), acoustic bonus (+0.5)
```

```
=== Profile: Deep Intense Rock ({'genre': 'rock', 'mood': 'intense', 'energy': 0.95, 'likes_acoustic': False}) ===

1. Storm Runner (Voltline) - Score: 4.44
   Because: genre match (+2.0), mood match (+1.0), energy match (+1.4)
2. Gym Hero (Max Pulse) - Score: 2.47
   Because: mood match (+1.0), energy match (+1.5)
3. Neon Pulse (DJ Kairo) - Score: 1.50
   Because: energy match (+1.5)
4. Broken Halo (Rust & Rain) - Score: 1.47
   Because: energy match (+1.5)
5. Heartbeat Overdrive (Neon Echo) - Score: 1.40
   Because: energy match (+1.4)
```

```
=== Profile: Energetic but Sad ({'genre': 'pop', 'mood': 'sad', 'energy': 0.9, 'likes_acoustic': False}) ===

1. Heartbeat Overdrive (Neon Echo) - Score: 3.47
   Because: genre match (+2.0), energy match (+1.5)
2. Gym Hero (Max Pulse) - Score: 3.46
   Because: genre match (+2.0), energy match (+1.5)
3. Sunrise City (Neon Echo) - Score: 3.38
   Because: genre match (+2.0), energy match (+1.4)
4. Storm Runner (Voltline) - Score: 1.48
   Because: energy match (+1.5)
5. Neon Pulse (DJ Kairo) - Score: 1.43
   Because: energy match (+1.4)
```

```
=== Profile: Calm but Angry ({'genre': 'classical', 'mood': 'angry', 'energy': 0.15, 'likes_acoustic': True}) ===

1. Moonlight Sonata Remix (Aria Vantablack) - Score: 3.92
   Because: genre match (+2.0), energy match (+1.4), acoustic bonus (+0.5)
2. Quiet Grief (Delta Moss) - Score: 1.90
   Because: energy match (+1.4), acoustic bonus (+0.5)
3. Spacewalk Thoughts (Orbit Bloom) - Score: 1.80
   Because: energy match (+1.3), acoustic bonus (+0.5)
4. Rainy Window Blues (Delta Moss) - Score: 1.77
   Because: energy match (+1.3), acoustic bonus (+0.5)
5. Golden Hour Fields (Wren Calloway) - Score: 1.73
   Because: energy match (+1.2), acoustic bonus (+0.5)
```

**Comparing outputs in plain language:** The High-Energy Pop and Deep Intense Rock profiles both successfully pull toward fast, loud songs, but for very different genres — pop energy anthems for one, distorted rock/metal-adjacent tracks for the other — which shows the genre weight is doing real work to keep those two tastes apart even though they share similar energy levels. The Chill Lofi profile is the strongest result: it correctly shifts toward low-energy, acoustic, chill-tagged songs, and the acoustic bonus visibly nudges every one of its top 5 (something the other two profiles never get, since they set `likes_acoustic: False`).

The two adversarial profiles are where it gets interesting. **Energetic but Sad** asked for a "sad" mood but the recommender doesn't actually have a sad-and-poppy song to offer — no pop song in the catalog is tagged "sad" — so the mood term quietly contributes nothing, and the list ends up identical in spirit to plain High-Energy Pop. In plain terms: a gym-style, high-energy pop song (`Heartbeat Overdrive`) keeps showing up for someone who typed "sad" because the recommender can only match moods that already exist on a song of that genre — it has no way to find or blend in "melancholy pop" if that combination isn't in the catalog, so it falls back to matching whatever it can (genre and energy) and stays silent about the part it couldn't satisfy. **Calm but Angry** showed the same pattern from the other direction: because classical only has one song and it's tagged "calm" rather than "angry," that one song still wins #1 purely by having no competition in its genre, even though its mood is the opposite of what was requested. Neither result is "wrong" given the math, but both are surprising if you expected the system to notice and flag a conflicting or unsatisfiable request — it doesn't; it just does its best with the terms that happen to line up.

---

## 8. Future Work  

I'd add a diversity cap (e.g., no more than 2 songs by the same artist in the top 5) to fix the Neon Echo repetition problem, and a secondary/negative preference field (e.g. `secondary_genres` or `avoid_genres`) so users aren't limited to one genre and one mood. I'd also want the recommender to detect and flag "no good match" situations — e.g. if the best available song for a mood scores 0 on that dimension, say so explicitly instead of silently ranking it as if the mood fit. Bringing in the unused `tempo_bpm`, `valence`, and `danceability` columns as additional scored dimensions would also let the system distinguish songs that currently tie on genre/mood/energy.

---

## 9. Personal Reflection  

Building and stress-testing this made it obvious how much a recommender's "personality" comes down to a handful of weight numbers — doubling energy and halving genre in my experiment was enough to let a completely different-genre song (an EDM track) climb into the top 5 for a rock listener, purely because it happened to be loud. What surprised me most was the adversarial testing: I expected the system to either "break" or produce obviously nonsensical output when given conflicting preferences like "energetic but sad," but instead it did something subtler and arguably more concerning — it quietly dropped the part of the request it couldn't satisfy and presented a confident, seemingly complete answer anyway. That changed how I think about real recommendation apps: a system doesn't have to crash or return garbage to mislead a user, it just has to stay silent about the constraints it gave up on.
