# Scientific Questions and Definitions

Frozen as part of the CM-0 epistemic seal. Changes require an ADR and a research-log entry.

## S1 — Next-thought predictability

Given a participant's thought history up to time `t` (and context), can we predict
`T_{t+1}` above strong non-neural baselines?

## S2 — Multi-step futures

For which horizons `H` and which cognitive dimensions (semantic, topic, temporal
orientation, valence, self-relevance, cognitive category) does predictability decay, and
how fast? (Thought Predictive Horizon; Future Predictability Curve.)

## S3 — Neural incremental prospective information

Does neural state at `t` (lag-aware for BOLD) improve prediction of `T_{t+1..t+H}`
beyond thought history + context alone? This is the central comparison.

## S4 — Causal genealogy

Which candidate dynamic SCM (thought history, semantic context, neural state, goals,
memory, affect, control) is consistent with the conditional independencies observable in
the data? Which causal claims are **unanswerable** from ds006067?

## S5 — Intervention and redirection (future, requires new data)

Under randomized intervention `do(X)`, does the predicted trajectory diverge
(Branch Divergence Index), and can a revealed prediction be resisted or redirected
(Agency Gain)? Can the attempt to escape prediction itself be predicted (Recursive
Predictability Recovery)?

## Definitions

- **Thought event**: one contiguous, self-reported thought segment in the transcript,
  delimited by the dataset's thought-boundary annotations (or, where absent, by
  pause/speaker-change heuristics documented per dataset). A thought event has a start
  time, end time, text, and participant id.
- **Cognitive trajectory**: the ordered sequence of thought events (and associated
  neural samples) for one participant within one session, plus the latent states
  inferred from them.
- **Next thought**: the thought event immediately following the current one in the
  participant's temporal order (not the next sample frame).
- **Semantic future**: the distribution over semantic content of thoughts in
  `t+1..t+H`, represented in the frozen semantic embedding space.
- **Predictive horizon**: for a dimension `d`, the largest `H` such that the model's
  skill on `d` at horizon `H` remains significantly above the strongest baseline under
  the frozen protocol.
- **Causal genealogy**: for a thought event, the set of upstream variables (past
  thoughts, neural states, context, goals) that are *identified* (under stated
  assumptions) as causes, as opposed to mere correlates.
- **Trajectory divergence**: a quantitative difference between the observed (or
  simulated) post-intervention trajectory and the counterfactual no-intervention
  trajectory, measured in the Thought State metric space.
- **Intervention**: a manipulation applied at a defined time that changes the
  information available to the participant (cue, goal, prediction reveal) or the
  experimental conditions. In observational data, "intervention" is only used for
  natural experiments that satisfy a stated ignorability assumption.
- **Voluntary redirection**: a participant-initiated change of cognitive trajectory
  that (a) follows a revealed prediction or instruction, and (b) is verified by
  trajectory divergence in the intended direction.
- **Agency gain**: the reduction in predictability (or increase in divergence) of the
  post-reveal trajectory relative to the pre-reveal predicted trajectory, under a
  randomized reveal condition.

## Falsifiable hypotheses (summary; full list in `hypotheses.md`)

- H1: Next-thought category/content is predictable above marginal and Markov baselines.
- H2: Predictability decays with horizon; at least one dimension retains skill at H>=2.
- H3: Neural state adds incremental prospective information beyond language history
  (or: it does not — equally valuable).
- H4: Candidate SCM conditional independencies are testable and partially rejected,
  yielding a pruned graph.
- H5 (future): Randomized prediction reveal changes subsequent trajectories; the change
  is measurable as Branch Divergence / Agency Gain.
