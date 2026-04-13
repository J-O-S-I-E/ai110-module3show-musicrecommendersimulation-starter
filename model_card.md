# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0** — a content-based music recommender that scores songs
against a user taste profile and returns the top-k matches with explanations.

---

## 2. Intended Use

VibeFinder suggests songs from a small 18-song catalog based on a user's
stated genre, mood, and three numeric preferences (energy, acousticness,
tempo). It is designed for classroom exploration of how real recommender
systems turn raw data into ranked lists. It is not intended for real users or
production use. It assumes the user can accurately describe their own taste
as a set of keyword and numeric targets — an assumption that rarely holds in
practice.

---

## 3. How the Model Works

Every song in the catalog gets a score out of 6.0. The score is built from
five ingredients:

- **Genre bonus (+2.0):** Does the song's genre exactly match what the user asked for? If yes, 2 points. If no, zero. This is the single biggest factor.
- **Mood bonus (+1.5):** Does the song's mood label exactly match? Same idea — all or nothing.
- **Energy closeness (up to +1.0):** Energy is measured 0 to 1. The closer the song's energy is to what the user wants, the more points it earns. A perfect match gives 1.0; a song at the opposite extreme gives 0.
- **Acousticness closeness (up to +1.0):** Same formula applied to how acoustic vs. electronic a song sounds.
- **Tempo closeness (up to +0.5):** How close is the song's BPM to the user's target? Scored using the full range of tempos in the dataset (58–178 BPM). Worth half as much as energy because tempo and energy tend to move together anyway.

After every song is scored, they are sorted from highest to lowest. The top 5
are returned with a plain-language explanation listing exactly which points
were awarded and how much each contributed.

---

## 4. Data

The catalog is `data/songs.csv` — 18 songs spanning 14 genres and 12 mood
labels. Genres include pop, lofi, rock, metal, jazz, ambient, synthwave,
hip-hop, classical, r&b, country, reggae, latin, and electronic. Moods
include happy, chill, intense, relaxed, focused, moody, angry, melancholic,
romantic, nostalgic, uplifting, and sad.

No songs were removed. One important observation: the catalog has only one
song per most genres. Rock has exactly one entry (Storm Runner), metal has one
(Iron Requiem), and classical has one (Raindrop Sonata). This means that
whenever a user's genre preference matches, there is essentially no
competition — the system will always recommend that song first regardless of
whether it is actually the best sonic match. The dataset is too small to
provide meaningful genre-level variety.

---

## 5. Strengths

- **Clean separation of opposing styles.** The system reliably separates
  "intense rock" from "chill lofi" — Storm Runner scored 0.95/6.0 for the
  lofi profile while Midnight Coding scored 5.91/6.0. The five-feature recipe
  pulls hard in the right direction for any two stylistically opposite
  profiles.

- **Transparent explanations.** Every recommendation comes with an itemised
  list of exactly which points were awarded and why. A user can immediately
  see whether a song was recommended because of genre, mood, or purely numeric
  closeness.

- **Works without a genre preference.** The Genre-Less adversarial test showed
  the system degrades gracefully: without the genre key, scores are capped
  around 3.75/6.0, and the ranking shifts to favour songs that best match the
  numeric features — a reasonable behaviour.

---

## 6. Limitations and Bias

**Genre gatekeeping is the primary weakness.** The genre weight (+2.0) is
the single largest value in the recipe — larger than any continuous feature
can contribute by itself. In a catalog where most genres have only one
representative, this means the system will always promote that one song to the
top of the list regardless of how well it actually sounds like what the user
wants. For example, a user who asks for "rock" will always get Storm Runner
ranked first, even if Iron Requiem (metal) or Gym Hero (pop) would be a
closer sonic match on energy and tempo.

**Binary genre matching creates a hard wall.** The system gives zero genre
points to "indie pop" for a user who asked for "pop," and zero genre points
to "metal" for a user who asked for "rock." Culturally and sonically adjacent
genres are penalised identically to completely unrelated ones. There is no
partial credit for near-miss genres.

**The Sad Headbanger problem.** When a user's genre and mood preferences
conflict — for example, asking for metal but with a sad mood — the system has
no way to resolve the contradiction. Because no metal+sad song exists in this
catalog, the system defaults to satisfying the genre preference (Iron Requiem,
mood=angry, scored 4.43/6.0) while completely ignoring the mood request. The
user asked for sadness and got anger. The system did not warn them.

**Energy and tempo double-penalise the same dimension.** High-energy songs
tend to have high tempos. A song that is slightly too fast will lose points on
both the tempo similarity and the energy similarity calculations, even though
they are measuring related things. The weight experiment confirmed this: when
energy was doubled and genre halved, cross-genre high-energy songs like Gym
Hero jumped from 3.85 to 4.82 — a nearly 1-point gain purely from the
reweighted energy score, not from any change in the song itself.

**No diversity guarantee.** Every run returns the tightest cluster around the
user's profile. A lofi listener will always see the same three lofi songs in
the same order. There is no mechanism to surface an interesting outlier or
introduce variety.

---

## 7. Evaluation

Five taste profiles were tested and one weight-shift experiment was run.

**High-Energy Pop:** Sunrise City ranked first with 5.99/6.0 — a near-perfect
match on every dimension. Gym Hero ranked second despite its mood being
"intense" rather than "happy" because it still earned the genre bonus and came
close on energy and acousticness. This felt right; Gym Hero is a pop song and
it belongs in a pop listener's top 5.

**Chill Lofi Study Session:** Midnight Coding and Library Rain took the top two
spots (5.91 and 5.84). Focus Flow ranked third despite its mood being
"focused" rather than "chill" because the genre and numeric features were
close enough. Spacewalk Thoughts (ambient/chill) ranked fourth — it earned the
mood bonus but lost the genre bonus, exactly as the bias analysis predicted.

**Deep Intense Rock:** Storm Runner was the obvious #1 at 5.98/6.0. The
surprise was that Iron Requiem (metal, angry) ranked only #5 with 2.24 points,
below Gym Hero (pop, intense) at 3.85 and even below Fuego en la Pista (latin,
uplifting) at 2.35. This was unexpected: intuitively, a metal song should rank
closer to a rock profile than a latin pop song. The reason is that Iron
Requiem's tempo (178 BPM) is far from the target (150 BPM) and it earned no
categorical bonuses, while Gym Hero earned the mood bonus.

**Adversarial — Sad Headbanger:** Iron Requiem ranked #1 (4.43) because genre
matched, but the sad mood request was completely unmet. Signal Lost (the only
sad song in the catalog) ranked #2 at 3.69 without any genre points. The
system could not resolve the contradiction and silently prioritised genre over
mood.

**Adversarial — Genre-Less:** Without a genre key, scores dropped to a maximum
of roughly 3.7/6.0. Rooftop Lights edged out Sunrise City for #1 despite both
being "happy" songs, because Rooftop's energy (0.76) was closer to the target
(0.75) than Sunrise's (0.82). This demonstrated that the continuous features
alone can meaningfully differentiate songs when the categorical anchor is gone.

**Weight experiment (genre x0.5, energy x2.0 for Rock profile):** Storm Runner
remained #1 (5.97 vs 5.98 before), but the gap between #1 and #2 shrank from
2.13 points to 1.15 points. Gym Hero climbed from 3.85 to 4.82, nearly
matching the genre-correct song. This confirmed that the genre weight was
suppressing otherwise strong numeric matches, and that halving it surfaces more
diverse results without making the top result wrong.

---

## 8. Future Work

- **Weighted genre similarity:** Instead of binary genre matching, compute
  partial credit for adjacent genres (e.g., "indie pop" earns 1.0 instead of
  2.0 for a pop listener, "metal" earns 0.5 for a rock listener).
- **Mood conflict detection:** When genre and mood cannot both be satisfied,
  warn the user instead of silently defaulting to genre.
- **Diversity injection:** After ranking, replace one of the top-5 results with
  the highest-scoring song from a different genre to prevent the list from
  being an identical cluster every run.
- **Expand the catalog:** 18 songs is far too small for genre-level variety.
  Even doubling to 36 with 2-3 entries per genre would significantly improve
  recommendation quality.
- **User feedback loop:** Let the user rate recommendations ("too loud," "not
  quite") and use that to adjust weights for their next query.

---

## 9. Personal Reflection

The most surprising finding was the Sad Headbanger test. I expected the system
to fail somehow, but I did not expect it to fail so silently — it returned Iron
Requiem as #1 without any indication that the mood preference was completely
unsatisfied. A real recommender that behaves this way could leave users
confused and frustrated without ever explaining why. This showed me that
transparency in explanations (what the system CAN say) and transparency about
gaps (what the system CANNOT tell you) are two completely different problems.

Building this also changed how I think about genre labels on streaming
platforms. The binary genre match I implemented is essentially how many real
systems work at their core — they cluster songs by tag and retrieve the nearest
cluster. The sophistication of Spotify or YouTube comes not from a smarter
core algorithm, but from having millions of songs (so every genre niche has
real competition), user behaviour signals (so "similar users" can bridge genre
gaps), and years of weight tuning on real feedback data. My 18-song simulation
exposed the skeleton of that system.
