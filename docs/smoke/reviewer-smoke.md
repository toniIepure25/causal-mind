# Reviewer Smoke: Top 5 Leakage Risks (Next-Thought Prediction, fMRI + Transcript)

Scope: next-thought prediction (CM-3) on fMRI + transcript data. Each risk: one line on the risk, one line on the check that would catch it.

1. **Temporal leakage via future text.** Feature windows built from transcript text that extend past the prediction time (or contain the target event's words) let the model read the answer.
   Check: lag audit — assert every feature text window ends before the target event's start time, and target words have zero string/n-gram overlap with feature text.

2. **Subject leakage via shared participants.** The same participant in train and test lets the model memorize person-specific style instead of thought dynamics, inflating skill.
   Check: automated subject-disjoint check (`causal_mind.utils.splits.validate_split_integrity`): zero shared subjects across splits; every sample maps to exactly one split.

3. **BOLD hemodynamic lag misuse.** BOLD peaks ~4–6 s after the neural response; assigning fMRI samples to the wrong event (e.g., the next event) makes brain features encode the target.
   Check: lag grid + midpoint-assignment audit — verify each sample is assigned to the event covering its midpoint and no feature-assigned sample starts after the prediction time.

4. **Duplicate transcript samples.** Repeated utterances or duplicated loader rows create near-identical train/test pairs, inflating effective sample size and metrics.
   Check: exact + near-duplicate transcript detection (n-gram/embedding similarity) across splits; flag and remove duplicates before any split is made.

5. **Session-identity shortcut.** The model exploits session/run-level statistics or IDs instead of thought dynamics, so "skill" is session memorization.
   Check: session IDs are never model inputs; verify session-id uniqueness per subject and run a session-level permutation control (shuffle session order within subject) — skill must collapse to chance.
