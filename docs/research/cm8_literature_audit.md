# CM-8 Literature Audit — Voluntary Thought Redirection / Suppression / Cognitive Control

- **Author:** ORCHESTRATOR (CM-8), 2026-09-17.
- **Scope:** paradigms, outcome metrics, sham/demand controls, capture-modality
  reactivity, and effect sizes relevant to designing an experimentally-identified causal
  redirection of a predicted semantic trajectory.
- **Citation note:** paradigms and anchor papers below are real and well-established. Where
  I give a specific number (effect size / N) I flag it as a *planning estimate* from the
  general literature, not a single authoritative source; confirm exact values before
  preregistration.

## 1. Thought suppression / redirection

- **Ironic process theory** (Wegner, 1987, *Am. Psychol.*) and the "white bear" paradigm:
  instructing people to suppress a thought typically produces a **rebound** (more
  intrusions after the suppression period than baseline). Suppression is therefore *hard to
  succeed at*; the robust finding is the failure/rebound, not clean suppression.
- **Outcome metrics used:** intrusion occurrence counts / thought-occurrence ratings
  (e.g., "did the thought occur?" per interval), latency to first intrusion, and subjective
  suppression-success ratings. Rebound is usually a reliable effect; "successful reduction
  of the target thought" is usually NOT achieved (effect ≈ 0 or negative).
- **Design implication:** a pure "suppress/don't think of X" instruction is a poor
  redirection instrument (it rebounds). CM-8's GENERAL REDIRECT should be framed as
  *actively steering toward an alternative*, not *suppressing the current content* — this
  avoids the ironic rebound confound. (Flag: verify with a pilot that "move away" framing
  does not itself rebound.)

## 2. Cognitive / executive control

- Paradigms: Stroop, Go/No-Go, stop-signal, n-back, task-switching. These measure control
  over *responses/attention*, not the *content* of a free thought stream. They are useful
  for (a) a covariate of individual control capacity and (b) the general "can top-down
  control alter a process" literature, but they do not directly measure semantic-trajectory
  redirection.
- **Design implication:** optionally collect a brief control-capacity measure (e.g., a short
  Go/No-Go) as a secondary/moderator variable, not a primary outcome.

## 3. Semantic trajectory / thought-stream prediction

- There is limited direct work on *predicting the future content of a free thought stream*
  and then *measuring deviation from that prediction*. Adjacent literatures:
  - **Semantic drift** in dialogue/free association (concepts drift along semantic
    networks; free-association chains).
  - **Inner speech / think-aloud** research (e.g., the protocol-analysis tradition,
    Ericsson & Simon, 1993): thought streams are captured as verbal reports; the stream has
    a semantic structure that can be embedded (as CM-2/3 do with MiniLM).
- **Design implication:** CM-8's "predicted future basin + BRP" (deviation of the observed
  future from the *predicted* future, beyond the predictor's typical error) is, to our
  knowledge, **novel** as a causal-redirection metric. The nearest analog is measuring
  whether an intervention moves a thought stream away from its predicted course.

## 4. Intervention on thought content

- **Cognitive bias modification (CBM) / attentional bias training (ABT):** train attention
  toward/away from threat or reward; measured by bias indices (dot-probe) and, secondarily,
  by symptom change. Meta-analytic effect sizes on *bias* are small (planning estimate:
  d ≈ 0.1–0.3 on the bias index; symptom effects smaller and less consistent).
- **Guided imagery / cue-based redirection:** used clinically (e.g., to shift affect or
  attention); typically measured by self-report or task performance, not by an objective
  semantic-trajectory metric.
- **Design implication:** the literature supports that *cues and instructions can shift
  attentional/semantic focus*, but almost never measured as an objective, time-resolved
  semantic-trajectory deviation. CM-8's SPECIFIC CUE condition is the closest analog; the
  novelty is the objective BRP metric + the predicted-basin reference.

## 5. Sham / demand / attention controls (best practices)

- A valid sham must match the active condition on: **instruction exposure, attention,
  interruption, expectancy, and experimenter demand**, while omitting the active ingredient
  (the redirection content).
- Common techniques: a "no-op" instruction of matched length/complexity (e.g., "keep
  thinking naturally; there is nothing special about this moment"), a fake/placeholder cue
  that is semantically neutral and unrelated to the predicted basin, and identical timing
  and UI to the active conditions.
- **Design implication:** SHAM = a matched-length, matched-attention instruction that says
  *nothing about changing semantic direction* (e.g., a neutral "continue as normal" prompt
  presented identically to the active cues). This isolates the redirection content from the
  mere interruption/attention effect. Red-team must approve the sham as a true no-op.

## 6. Reactivity of the thought-capture modality

- **Think-aloud (continuous verbal):** highest temporal resolution, but verbalization can
  alter the cognition (reactivity / "verbal overshadowing"; Ericsson & Simon, 1993). Paced
  by speech production.
- **Typed stream:** lower reactivity than speech for some content, but changes pace and
  favors lexical/declarative content; still time-resolved.
- **Intermittent probes / silent thought:** lowest reactivity, but weak temporal precision
  (coarse sampling of the trajectory).
- **Design implication:** CM-8 should **pilot the modality explicitly** (CM-8P), comparing
  at least continuous think-aloud vs typed stream on (a) temporal resolution, (b) semantic
  richness (embedding coverage), (c) fatigue, and (d) reactivity (does the act of reporting
  itself change the trajectory?). Do NOT blindly reuse ds006067's methodology. The primary
  modality is a *design decision to be frozen after the pilot*, not assumed.

## 7. Effect sizes + sample sizes (planning estimates for power)

| phenomenon | metric | planning effect size | typical N |
| --- | --- | --- | --- |
| thought-suppression rebound | intrusion count | large/reliable (but it's a *failure* effect) | 20–60 |
| attentional bias training | bias index | small (d ≈ 0.1–0.3) | 30–80 per arm |
| cognitive-control training transfer | task performance | near-zero to small | 30–100+ |
| **CM-8 BRP (novel)** | P(leave predicted basin) | **unknown — assume small-to-medium (d ≈ 0.2–0.5) as a planning range** | to be set by simulation |

- **Design implication:** BRP is a novel binary/continuous outcome; there is no direct
  literature effect size. CM-8E must simulate a *range* of plausible effects (d = 0.2,
  0.3, 0.5) and report power curves, and the minimally-interesting-effect must be justified
  (not reverse-engineered from a pilot). Do NOT use the CM-7 effect size (different
  paradigm).

## 8. Novelty / gap

- **What CM-8 would be the first to do:** an *experimentally-identified* (randomized)
  causal test of whether an intervention redirects a **predicted** semantic trajectory,
  measured by a **frozen, prospective basin metric (BRP)**, with a clean
  **endogenous (GENERAL REDIRECT) vs exogenous (SPECIFIC CUE)** comparison and a proper
  **sham**.
- **What has NOT been done:** (a) redirection measured against a *predicted* future (not
  just a baseline); (b) an objective, time-resolved BRP with persistence horizon; (c) the
  endogenous-vs-exogenous agency comparison in a single randomized design.

## Design implications for CM-8 (summary)

- **(a) BRP/basin:** define the predicted-future basin as a ball around the frozen
  predictor's forecast, radius = a held-out quantile of the predictor's error norm
  (prospective, not tuned to outcomes). BRP = P(observed future outside the basin).
- **(b) sham:** matched-length neutral "continue as normal" prompt, identical UI/timing,
  no redirection content; red-team must approve.
- **(c) modality:** pilot think-aloud vs typed; freeze the primary modality after the
  pilot; measure reactivity explicitly.
- **(d) power:** simulate d ∈ {0.2, 0.3, 0.5} for BRP with within-subject correlation and
  attrition; report power curves; justify the minimally-interesting effect.
- **(e) novelty claim:** first experimentally-identified causal redirection of a predicted
  semantic trajectory with a frozen basin metric and an endogenous/exogenous comparison.
