# Reflection: Cross-Profile Comparisons

This file documents what changed between each pair of test profiles, and why
those changes make sense — written for a non-programmer audience.

---

## High-Energy Pop vs. Chill Lofi

These two profiles are nearly opposites, and the output reflects that perfectly.

The Pop profile asks for upbeat, electronic, fast songs in the "pop" genre
with a happy mood. The system returned Sunrise City as #1 (score 5.99 out of
6.0) because that song matched literally every preference — right genre, right
mood, right energy, right tempo, right acousticness. Gym Hero came in second
even though its mood is "intense" rather than "happy," because it still got
the pop genre bonus and its sound (high energy, electronic, fast) fits the
profile well.

The Lofi profile asks for the opposite: quiet, acoustic, slow songs with a
"chill" mood. The system returned Midnight Coding and Library Rain at the top.
Neither of those songs would even appear in the Pop list's top 5 — their
scores for the Pop profile would be near zero because they are slow and
acoustic when the pop profile wants fast and electronic.

**Why this makes sense:** Think of it like ordering food. If you ask for "spicy
and crunchy," the kitchen gives you chips and hot wings. If you ask for "mild
and soft," the kitchen gives you mashed potatoes. The same kitchen, the same
menu, completely different plates — because the order was different.

---

## Deep Intense Rock vs. High-Energy Pop

Both profiles want high energy, but the genre and mood differ — and the results
diverge sharply.

The Rock profile put Storm Runner (the only rock song in the catalog) at #1 with
a 5.98/6.0 score. Gym Hero — a pop song, not a rock song — came in second at
3.85. Even though Gym Hero is loud and fast (which the rock listener wants),
it still lost 2.0 points because its genre is "pop" not "rock."

The Pop profile put Sunrise City first and Gym Hero second. Notice that Gym
Hero appears in the top 5 for BOTH profiles. That is because Gym Hero is
sonically a high-energy, low-acoustic, fast-tempo song — it fits the numeric
description of both "intense pop" and "intense rock." The genre label is the
only thing separating how highly it ranks.

**Why this is interesting:** It exposes a real-world debate in music. Is "Gym
Hero" a pop song or a rock song? The artist labelled it pop, so the system
treats it as pop. But a rock listener might genuinely enjoy it. Real streaming
platforms solve this with collaborative filtering — they say "other users who
liked Storm Runner also liked Gym Hero" and bridge the genre gap that way. Our
system cannot do that.

---

## Adversarial: Sad Headbanger vs. Deep Intense Rock

The Sad Headbanger profile asks for metal music but with a sad mood. This
combination does not exist in the 18-song catalog — Iron Requiem is metal but
angry; Signal Lost is sad but electronic.

The system chose Iron Requiem as #1 (score 4.43) because the genre bonus
(+2.0) outweighed the mood miss. Signal Lost came in second (3.69) because it
earned the sad mood bonus (+1.5) but nothing else categorical.

Compare this to the regular Rock profile, where Storm Runner scored 5.98 by
matching both genre AND mood. The Sad Headbanger profile's top score was only
4.43 — a full 1.55 points lower — because no song in the catalog could satisfy
both requests at once.

**Plain language version:** Imagine you walk into a small music store and ask
the clerk for "heavy metal music, but make it sad." The clerk looks around and
says, "We only have one metal album and it's angry, not sad. The most similar
sad music we have is electronic. Do you want the angry metal, or the sad
electronic?" The system silently picked the angry metal. It never told you it
could not give you what you actually asked for.

This is the most important limitation discovered in testing.

---

## Adversarial: Genre-Less vs. High-Energy Pop

The Genre-Less profile is like a pop listener who forgot to mention their genre.
They said: "I want happy songs around medium energy, somewhat acoustic, moderate
tempo" — but did not say "pop."

The result: Rooftop Lights (indie pop) came in first, followed by Sunrise City
(pop). Both are happy songs with matching energy and acousticness. Interestingly,
Rooftop Lights — which is technically "indie pop" and would not have gotten the
genre bonus in a full pop profile — beat out Sunrise City purely on better
numeric similarity.

Compare to the regular Pop profile, where Sunrise City scored 5.99 and Rooftop
Lights scored 3.75. Without the genre bonus, those two songs are nearly tied
(3.74 vs 3.54). The genre label alone was worth more than a full point of
separation.

**What this tells us about the system:** The genre label acts like a thumb on
the scale. It does not just influence the ranking — it dominates it. A user who
does not have a strong genre preference (or does not know the genre vocabulary)
gets a fundamentally different experience from the system, and there is no way
for the system to know whether that difference is what the user actually wanted.

---

## Weight Experiment: What Happened When We Changed the Recipe

In the original recipe, genre was worth 2.0 points and energy was worth up to
1.0 points. We ran an experiment where we halved genre (to 1.0) and doubled
energy (to 2.0), keeping the total maximum score at 6.0.

For the Rock profile, Storm Runner still ranked first — it matches on genre,
mood, energy, acousticness, and tempo, so even with a smaller genre bonus it
dominates. But the second-place song jumped from 3.85 to 4.82. The gap between
#1 and #2 shrank from 2.13 points to 1.15 points. The songs below Storm Runner
became more competitive, not because they got better but because the genre
penalty on them became smaller.

**The key insight:** The original weights were set to strongly enforce genre as
the primary filter. That works well when the genre match is right, but it
silently suppresses songs that might be a better sonic match but have a
different genre label. Halving the genre weight made the system more open to
cross-genre suggestions — which could be better or worse depending on what the
user actually wants.

This is exactly the tradeoff real platforms face: do you show users more of what
they already know they like (safe, genre-anchored results), or do you take a
small risk and show them something from a different genre that might surprise
them in a good way?
