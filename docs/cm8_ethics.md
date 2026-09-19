# CM-8G — Ethics / IRB Package (DRAFT)

- **Status:** DRAFT. Human recruitment/data collection is **gated** on ethics approval.
  Nothing here authorizes data collection.
- **Study:** a within-subject, randomized, behavioral experiment in which participants
  freely report a stream of thoughts; at randomized points they receive one of four
  instructions (control / sham / general-redirect / specific-cue) and continue; the
  subsequent thought stream is analyzed for semantic-trajectory redirection.

## 1. Risk analysis

- **Risk level:** minimal (no physical intervention; no clinical population required; no
  deception beyond a benign, fully-debriefed sham).
- **Psychological:** the "move your thinking away" and cue instructions are benign and
  non-clinical; no aversive or personal content is requested. Participants may skip or
  stop at any time.
- **Privacy (elevated):** participants generate **free thought streams**, which can be
  unusually sensitive (personal, emotional, or identifying content). This is the primary
  risk and is addressed in §3–4.
- **Reactivity:** reporting thoughts may alter cognition (a scientific consideration, not a
  safety risk); disclosed in consent.

## 2. Consent language (draft)

- You are invited to take part in a research study about how people's streams of thought
  change over time and whether a brief instruction can change the direction of your
  thinking.
- You will spend ~[X] minutes reporting your thoughts (by [think-aloud / typing]) in a
  series of short rounds. At random points you will be given a brief instruction (for
  example, to keep thinking as usual, or to deliberately move your thinking in a
  different direction, or to think about a word we suggest).
- There is no right or wrong way to think; you may pause or stop at any time without
  consequence.
- **Sham disclosure:** some instructions are "placebos" with no intended effect; we will
  explain this fully at the end.
- **Privacy:** your thought reports are stored [pseudonymized / encrypted]; see the data
  statement below. You may request that your raw text be destroyed after analysis.
- Participation is voluntary; withdrawing has no penalty. [Contact for questions.]
- [Optional] Separate consent for retention of raw thought text beyond analysis.

## 3. Privacy (design from the start)

- **Pseudonymization:** participants are identified only by a study code; the key is stored
  separately and access-controlled.
- **Minimization:** collect only the thought stream + the predefined self-report items; no
  extra personal data.
- **Identifying-text stripping:** where scientifically compatible, directly identifying
  text (names, exact locations, contact details) is flagged/stripped before long-term
  storage; the scientific analysis uses semantic embeddings, not raw text.
- **Encrypted storage + access control:** raw thought text is encrypted at rest; access is
  limited to the analysis team; separate consent for raw-text retention.
- **Retention policy:** raw text retained only as long as needed for analysis/audit, then
  destroyed (or per the separate consent); embeddings + aggregated results retained.
- **No public release of identifiable free text** in any publication or dataset.

## 4. Data management plan

- **Capture:** high-resolution timestamps (thought onset/end, model inference time,
  intervention presentation, response timing, condition, prediction, predicted basin,
  actual subsequent states) — auditable log (see `docs/cm8_realtime_platform.md`).
- **Storage:** on the project PVC, encrypted, access-controlled; pseudonymized.
- **Analysis:** semantic embeddings (frozen MiniLM) + the predefined metrics; raw text
  access-restricted.
- **Sharing:** only aggregated/pseudonymized, de-identified results; no raw identifiable
  free text.

## 5. Debriefing

- Full explanation of the study's purpose (causal redirection of thought trajectories),
  the sham conditions, and the randomization.
- Opportunity to ask questions and to request raw-text destruction.

## 6. IRB submission checklist

- [ ] Protocol (this package + `docs/cm8_experiment_design.md` + `docs/cm8_preregistration.md`).
- [ ] Consent form (final).
- [ ] Recruitment materials (if any).
- [ ] Risk/benefit statement (minimal risk; scientific benefit to the field).
- [ ] Privacy / data management plan (§3–4).
- [ ] Debriefing script (§5).
- [ ] Compensation (if any) + exclusion/inclusion criteria (healthy adults, [age range]).
- [ ] Adverse-event / withdrawal procedure.
- [ ] Investigator qualifications + data security attestations.

## 7. Gate

Until IRB (or equivalent ethics) approval is obtained, **no human recruitment or data
collection**. When all data-independent gates (G1–G8) pass and ethics is the only blocker,
the project returns `CM8_READY_FOR_ETHICS_SUBMISSION` with this package.
