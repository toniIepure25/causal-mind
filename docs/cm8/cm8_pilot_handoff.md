# CM-8 Pilot (CM-8P) Handoff

A handoff document for running the small, gated pilot (CM-8P) before the confirmatory run.
Part of the `cm8-prehuman-v1.0` freeze. **The pilot's only purpose is operational
GO/ITERATE/STOP — it is NOT an analysis of the ATE.** No protocol change is made based on
the pilot's outcome values.

## 1. Purpose and scope

- **Purpose:** verify the operational pipeline end-to-end with real participants before the
  confirmatory run: capture modality, latency in the wild, participant burden, manipulation
  check, report-reactivity, and engine stability.
- **Scope:** 3–5 participants (a small, gated run). **Not** a power analysis; **not** an
  ATE analysis.
- **Gate:** GO → confirmatory run; ITERATE → fix operational issues (no protocol change);
  STOP → stop (a valid outcome).

## 2. Preconditions (all must be true before the pilot)

- [ ] Supervisor sign-off on the frozen protocol + pre-human freeze.
- [ ] Ethics approval (University of Vienna Ethics Committee).
- [ ] Pilot authorization.
- [ ] The frozen forecaster + engine are deployed (SHA-verified against
  `artifacts/cm8_forecasting_freeze_manifest.json`).
- [ ] The randomization manifest is loaded (SHA-verified).
- [ ] The privacy pipeline is active (PII detection, pseudonymization, encryption at rest).
- [ ] The capture modality is decided (default: keyboard thought-entry).

## 3. Per-participant procedure

1. Consent + participant information (lay language, no sensational terms).
2. Pseudonymization (salted hash; the salt is encrypted and stored separately).
3. A short practice block (familiarization with the capture + intervention flow).
4. The trial sequence (a subset of the 24-trial design, balanced across conditions).
5. Debrief (the participant is told the study's purpose; no deception beyond the SHAM).
6. Data finalized atomically (append-only JSONL; no duplicate finalization).

## 4. Operational checks (the pilot's actual outputs)

| check | what to verify | pass criterion |
| --- | --- | --- |
| Capture modality | participants can enter thoughts fluently | no systematic capture failures |
| Latency in the wild | total critical path under real conditions | p95 within ~2× the offline p95 (478 ms) |
| Participant burden | time + number of thoughts | ~28 min / 96 thoughts (feasible) |
| Manipulation check | participants experience the intended condition | check rate within pre-set range |
| Report-reactivity | participants do not change behavior because they are measured | no systematic reactivity flag |
| Engine stability | no crashes, no duplicate finalization, logs parseable | 0 unhandled faults (chaos 7/7 offline) |
| Privacy | no raw text leaves the machine; PII redacted | 0 PII leaks in the audit log |

## 5. GO / ITERATE / STOP criteria

- **GO:** all operational checks pass; proceed to the confirmatory run (CM-8H).
- **ITERATE:** one or more operational checks fail in a fixable way (e.g., capture modality
  friction, a UI issue). Fix the **operational** issue (NOT the protocol), re-run the
  failing check. The frozen protocol (estimands, α, randomization, N, basin) is **not**
  changed.
- **STOP:** an operational check fails in an unfixable way, or a participant-safety /
  privacy issue arises. Stop. This is a valid outcome.

## 6. What the pilot will NOT do

- Will **not** estimate the ATE (no power; not the purpose).
- Will **not** change the frozen confirmatory protocol (Workstream A).
- Will **not** be used to tune the analysis to a desired outcome.

## 7. Data handling

- Pseudonymized; embeddings only (no raw text stored beyond the privacy pipeline).
- Encryption at rest; access audit; complete deletion on request.
- No remote LLM / no telemetry.

## 8. Handoff checklist (sign-off)

- [ ] Preconditions met (section 2).
- [ ] Operational checks defined (section 4).
- [ ] GO/ITERATE/STOP criteria agreed (section 5).
- [ ] Privacy pipeline verified active.
- [ ] Debrief script ready.
- [ ] Data-handling plan agreed (section 7).

*The pilot is a gate, not a result. Its output is a decision (GO/ITERATE/STOP), not an
effect size.*
