# Personalization & Predictability Reliability (CM-LAB §36-40)

**Decision:** `CMPERS_NULL` (personalization provides no benefit; it actively hurts)
**Claim:** C-103 (new)
**Script:** `data/scripts/cm_personalization.py`
**Machine-readable:** `reports/cm_personalization/cm_personalization.json`
**Dataset:** ds006067 thought-stream, subject-disjoint 83/18/17, frozen CM-2 seal, seed 20260911, k=3, h=1.

---

## 1. Question (§36)

> Does a small amount of a person's OWN earlier thought history improve prediction of their
> LATER thoughts?

**Design (strict chronology, no leakage).** For each of the 17 test subjects (with usable
early/late segments), the timeline is split at the midpoint: EARLY (first half) and LATE
(second half, held out). The GLOBAL model (P0) is fit on TRAIN (without the subject).
Personalized variants adapt using ONLY the subject's EARLIER observations and are evaluated
on the LATER observations.

**Ladder (§37).** P0 global; P1 global + subject intercept (mean residual on adaptation data);
P3 global + subject ridge residual correction (ridge: global_pred → residual).

## 2. Results

Mean global (P0) error on LATE: **0.6413**.

| Level | f=10% | f=25% | f=50% |
|---|---|---|---|
| P1 gain (P0 − P1) | **−0.1587** [−0.1836,−0.1342] | −0.1078 [−0.1252,−0.0898] | −0.0730 [−0.0871,−0.0584] |
| P3 gain (P0 − P3) | **−0.1587** [−0.1836,−0.1342] | −0.1078 [−0.1253,−0.0898] | −0.0730 [−0.0871,−0.0584] |

All gains are **negative** with CIs excluding 0, in **all 17 subjects** (proportion positive
= 0.0). The personalized model has *higher* error than the global model at every adaptation
fraction. P3 (ridge) reduces to P1 (intercept) on the small adaptation data, so the two
ladders coincide.

**Data curve (§38).** The (negative) gain is worst at the smallest adaptation fraction
(f=10%, −0.159) and improves (toward zero) as more EARLY data is used (f=50%, −0.073) — but
it never crosses into positive. More personal data reduces the harm but does not produce a
benefit.

**Failure modes (§39).**
- The harm is consistent across subjects (not confined to low-data subjects; the single
  low-data subject also shows a negative gain, −0.117).
- The likely mechanism is **session drift**: the subject's EARLY behavior does not predict
  their LATE behavior, so a correction fit on EARLY shifts the LATE prediction *away* from
  the actual LATE target (P1 error rises from 0.641 to 0.800 at f=10%).
- The small adaptation data (10% of EARLY ≈ 1–2 samples) makes the intercept noisy.

## 3. Predictability reliability (§40)

Session-level predictability stability (first-half vs second-half error of the LATE segment,
across the 17 test subjects):
- Pearson = **0.143**, Spearman (rank) = **0.240**.

This is **weak**: a subject's predictability in one half of their session is only weakly
related to their predictability in the other half. We therefore do **not** call this a
cognitive trait; the cautious term is **session-level predictability**, and it is not stable
enough to support a "predictability phenotype" claim.

## 4. Decision (§39)

> **`CMPERS_NULL`** — lightweight personalization (subject intercept or ridge residual
> correction) provides **no benefit**; it actively *hurts* out-of-sample (negative gain, CIs
> exclude 0, all subjects). The most parsimonious explanation is session drift (early ≠ late
> behavior) compounded by the small adaptation data. No CM-8 protocol change.

**Interpretation.** A small amount of a person's own earlier history does **not** improve
prediction of their later thoughts under these simple, prospective adaptations. This is a
valuable negative result: it bounds the personalization claim and indicates that any future
personalization must (a) use more personal data, (b) model the early→late drift explicitly,
or (c) use a fundamentally different adaptation mechanism.

## 5. Guardrails

- Strict chronology: adaptation uses only EARLY (past); evaluation uses only LATE (future).
- Global model fit on TRAIN (without the target subject); no test-set tuning.
- No CM-8 change; no human data.
