# Model Card: VibeFinder 1.0

---

## 1. Model Name

**VibeFinder 1.0**

A content-based music recommender that scores every song in a catalog against
a user taste profile and returns the top-k matches with plain-language
explanations of exactly why each song was chosen.

---

## 2. Goal / Task

VibeFinder tries to answer one question: *given what a user says they like,
which songs in the catalog are the closest match?*

It does this by translating taste into numbers. A user says "I want lofi
music, chill mood, low energy, acoustic, slow tempo." The system turns that
into a point-scoring contest. Every song is judged against those preferences,
scored out of 6.0, and the top 5 winners are returned. The system does not
learn from behaviour — it only knows what the user explicitly tells it.

---

## 3. Algorithm Summary

Every song earns a score made of five ingredients. No code — just the idea:

**Genre bonus (+2.0 points, all or nothing)**
Does the song's genre label exactly match the user's preferred genre? If yes,
2 full points. If no, zero. This is the single biggest factor in the recipe.
A "lofi" song scores 2.0 for a lofi listener; a "rock" song scores 0.

**Mood bonus (+1.5 points, all or nothing)**
Same idea applied to mood. Does "chill" match "chill"? Full points. Does
"intense" match "chill"? Zero. No partial credit.

**Energy closeness (up to +1.0 points)**
Energy is a number between 0 and 1. The closer a song's energy is to what the
user wants, the more points it earns — smoothly, not all-or-nothing. A perfect
match gives 1.0 points. The most mismatched possible song gives 0.

**Acousticness closeness (up to +1.0 points)**
Exactly the same formula, applied to how acoustic versus electronic a song
sounds. High acousticness means an unplugged, natural sound; low acousticness
means heavily produced.

**Tempo closeness (up to +0.5 points)**
How close is the song's beats-per-minute to the user's target? Worth half as
much as energy because fast songs tend to also be high energy — scoring both
would count the same thing twice.

**Final score = sum of all five.** Maximum possible: 6.0 points. Songs are
sorted highest to lowest and the top 5 are returned with a list of exactly
which points were awarded.

---

## 4. Data Used

| Property | Value |
|---|---|
| Source file | `data/songs.csv` |
| Total songs | 18 |
| Genres | 14 (pop, lofi, rock, metal, jazz, ambient, synthwave, hip-hop, classical, r&b, country, reggae, latin, electronic) |
| Moods | 12 (happy, chill, intense, relaxed, focused, moody, angry, melancholic, romantic, nostalgic, uplifting, sad) |
| Numeric features | energy (0–1), tempo_bpm (58–178), acousticness (0–1) |

**Key limitation of the data:** Most genres have only one song. Rock has
exactly one entry (Storm Runner), metal has one (Iron Requiem), classical has
one (Raindrop Sonata). When a user asks for "rock," there is no real
competition — Storm Runner wins automatically regardless of whether it is
actually the best sonic match. The catalog is too small to produce genuine
variety within a genre.

The data reflects a narrow slice of musical taste. Western genres dominate.
There is no K-pop, no Afrobeats, no classical subgenres. A user whose actual
taste lives outside this catalog will consistently get poor results, and the
system has no way to tell them so.

---

## 5. Observed Behavior and Biases

**What works well:**

The system cleanly separates stylistically opposite profiles. A "chill lofi"
listener gets Midnight Coding (5.91/6.0); Storm Runner (rock/intense) scores
only 0.95/6.0 for that same listener — a gap of nearly 5 points. The five
features together pull strongly in the right direction whenever the user's
taste is well-represented in the catalog.

Every recommendation includes a plain list of exactly which points were
awarded ("genre match (+2.0)", "energy similarity (+0.96)"). A user can
immediately see whether a song was recommended because of genre, mood, or
purely numeric closeness.

**Biases and failure patterns discovered during testing:**

*Genre gatekeeping.* The +2.0 genre bonus is larger than any single continuous
feature can contribute alone. In an 18-song catalog with one song per genre,
this means the system always promotes that one song to #1 regardless of how
well it actually sounds like what the user wants. There is no competition
within a genre, so the "winner" is predetermined the moment the genre is set.

*Binary matching ignores adjacent genres.* "Indie pop" earns zero genre points
for a pop listener. "Metal" earns zero for a rock listener. There is no partial
credit for genres that are culturally or sonically close. The system treats the
distance between "pop" and "indie pop" as identical to the distance between
"pop" and "metal."

*Silent failure on conflicting preferences (the Sad Headbanger problem).* When
a user asks for "metal" genre but "sad" mood, no song in the catalog satisfies
both. The system silently picks Iron Requiem (#1, genre match, mood=angry)
without ever telling the user that their mood preference went completely unmet.
The user asked for sadness and received anger, with no warning.

*Energy and tempo measure overlapping things.* High-energy songs tend to be
fast. A song that is slightly off in tempo will usually also lose energy
points. The weight experiment (doubling energy, halving genre) confirmed this:
cross-genre high-energy songs like Gym Hero jumped nearly a full point (3.85
to 4.82) just from the energy reweighting — the tempo score moved in the same
direction.

*No variety.* The top 5 results are always the five songs closest to the
profile. A lofi listener sees the same three lofi songs in the same order
every single time. There is no mechanism to surface an outlier or introduce a
pleasant surprise.

---

## 6. Evaluation Process

Five taste profiles were tested and one weight-shift experiment was run.
Results were compared against musical intuition to check whether they "felt"
correct.

**High-Energy Pop** — Sunrise City ranked #1 (5.99/6.0), matching all five
preferences. Gym Hero ranked #2 despite its mood being "intense" not "happy"
because it still earned the genre bonus. Felt right.

**Chill Lofi Study Session** — Midnight Coding #1 (5.91), Library Rain #2
(5.84). Both lofi/chill. Focus Flow ranked #3 despite mood="focused" because
genre and numeric features were close. Spacewalk Thoughts (ambient/chill)
ranked #4 — mood matched but genre did not, exactly as predicted.

**Deep Intense Rock** — Storm Runner #1 (5.98) as expected. Surprising: Iron
Requiem (metal/angry) ranked only #5 (2.24), below Gym Hero (pop/intense, 3.85)
and even Fuego en la Pista (latin/uplifting, 2.35). Metal *feels* closer to
rock than latin pop, but Gym Hero earned the mood bonus and Iron Requiem's
tempo (178 BPM) was too far from the rock target (150 BPM).

**Adversarial — Sad Headbanger (metal genre, sad mood)** — No metal+sad song
exists. Iron Requiem #1 (4.43, genre satisfied, mood ignored). Signal Lost #2
(3.69, sad but electronic). The system failed silently — no warning that mood
was unmet.

**Adversarial — Genre-Less (no genre key)** — Scores capped at ~3.7/6.0.
Rooftop Lights (#1, 3.74) edged out Sunrise City (#2, 3.54) on numeric
similarity alone. Demonstrated that continuous features can meaningfully
differentiate songs without categorical anchors.

**Weight experiment (genre ×0.5, energy ×2.0 for Rock profile)** — Storm
Runner remained #1. Gym Hero jumped from 3.85 to 4.82. The gap between #1
and #2 shrank from 2.13 to 1.15 points. Confirmed that the original genre
weight was suppressing strong cross-genre numeric matches.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**
VibeFinder is designed for classroom learning. It demonstrates how a content-
based recommender system turns explicit user preferences into scored, ranked
results. It is meant to be read, modified, and experimented with — not
deployed. Students and instructors can use it to understand weighting, feature
selection, and the gap between a simple scoring function and real-world
recommendation quality.

**Non-intended use:**

- **Not for real users seeking music discovery.** The 18-song catalog is far
  too small, and the binary genre/mood matching is far too blunt, to produce
  recommendations that would satisfy an actual listener.

- **Not as a neutral or fair arbiter of taste.** The catalog reflects a narrow
  set of Western genres. Users whose taste falls outside the represented genres
  (K-pop, Afrobeats, classical sub-genres, etc.) will receive consistently
  poor results, and the system will not indicate this.

- **Not as a substitute for collaborative filtering.** VibeFinder knows nothing
  about what other users listen to. It cannot bridge genre gaps using shared
  behaviour, which is the primary way real platforms (Spotify, YouTube) surface
  genuinely novel recommendations.

- **Not for high-stakes decisions.** No music recommender should gate access
  to content, influence chart rankings, or determine artist revenue without
  significant additional safeguards and human oversight.

---

## 8. Ideas for Improvement

**Partial credit for adjacent genres.** Instead of all-or-nothing genre
matching, build a small similarity table: "indie pop" scores 1.0 against a
"pop" listener instead of 0; "metal" scores 0.5 against "rock." This would
surface Iron Requiem meaningfully for a rock listener, which currently the
system fails to do.

**Conflict detection and warnings.** Before returning results, check whether
genre and mood preferences can both be satisfied. If no song in the catalog
matches both, tell the user: "No metal+sad song found — showing closest
alternatives, with genre prioritised." Silent failure is the most dangerous
kind of failure.

**Diversity injection.** After scoring, swap one of the top-5 results for the
highest-scoring song from a different genre. This prevents every run from
returning an identical cluster and gives users a chance to discover something
outside their stated preference box — which is where some of the best
recommendations happen in practice.

---

## 9. Personal Reflection

**What was the biggest learning moment?**

The Sad Headbanger test. I designed it expecting the system to produce
obviously wrong results — and it did. But what I did not anticipate was *how
quietly* it failed. Iron Requiem appeared at #1 with a respectable-looking
score (4.43/6.0) and a list of reasons that all sounded valid. Nothing in the
output indicated that the user's mood preference had been completely ignored.
If a real user saw that output, they would not know the system had failed them.

That taught me the difference between two kinds of transparency: explaining
what the system *did* (easy — we list the reasons) and flagging what the
system *could not do* (hard — requires the system to know what it does not
know). Almost every real AI failure I have read about is the second kind, not
the first.

**How did AI tools help, and when did I need to double-check them?**

AI tools were most useful for thinking through weight design — when I described
the dataset and asked for weighting strategies, the response correctly
identified that genre and mood should carry more weight than tempo (because
tempo correlates with energy and would double-count it). That matched my own
reasoning and gave me confidence in the recipe.

Where I needed to double-check: early on, the AI suggested using `list.sort()`
for ranking. That would have mutated the caller's `songs` list and returned
`None` — a silent bug that would have been hard to trace. Reading the output
carefully and comparing it to the Python docs caught it before it became a
problem. AI suggestions are fast, but they are not always safe to copy without
reading.

**What surprised me about how a simple algorithm can "feel" like a
recommendation?**

Sunrise City scoring 5.99/6.0 for the pop/happy profile was genuinely
surprising. I knew mathematically it should score high, but seeing a number
that close to perfect made it feel like the system had *understood* something.
It had not — it just counted matching labels and measured distances. But that
gap between "the system ran a formula" and "the system understood my taste"
is exactly the illusion that makes recommender systems compelling. Users
experience the output, not the mechanism. A 5.99 feels like a great
recommendation even if the algorithm behind it is five lines of arithmetic.

This made me think differently about how I use Spotify. The reason those
recommendations often feel right is not that the algorithm is smart — it is
that the catalog is enormous, so even a blunt formula finds genuinely good
matches. VibeFinder with 18 songs shows the skeleton. Spotify is the same
skeleton with 100 million songs and years of user signal layered on top.

**What would I try next if I extended this project?**

The feature I most want to add is conflict detection — a pre-check that runs
before scoring and warns the user when their genre and mood preferences cannot
both be satisfied in the catalog. This is a small code change (one extra loop)
but it would make the system dramatically more honest.

After that, I would expand the catalog to at least 5 songs per genre. Almost
every limitation I found — genre gatekeeping, no within-genre variety, the
Sad Headbanger failure — traces back to having only one song per genre. More
data does not fix the algorithm, but it makes the algorithm's flaws less
visible, which is also how it works in production.
