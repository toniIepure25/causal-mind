# CM-XVAL First Milestone — External Validation on Open Play

**Decision: `CMXVAL_PARTIAL`** (new claim **C-101**; does not reuse C-003/C-004)

## Finding under test
C-003/C-004 (validated on ds006067): given the frozen MiniLM embeddings of a subject's
k=3 most recent free-text entries, one predicts the **semantic content** (cosine) of the
subject's next entry, out-of-sample with a subject-disjoint split, **above the strongest
frozen baseline** (B0-B7), at multiple future horizons.

## External dataset (domain shift)
- **Open Play** (digital-wellbeing/open-play), openESM `0075_ballou`, Zenodo DOI
  `10.5281/zenodo.17536656`, CC-licensed.
- 1284 participants x 30 daily waves. We use the free-text `displaced_activity` field
  ("describe what you did instead of gaming") as the thought-analogue text stream.
- **This is a genuine domain shift**: short gaming-diary activity descriptions
  (mean ~2.7 words), not rich internal thoughts. External validation should test exactly
  this: does temporal semantic persistence generalize beyond thought-streams?
- Data: 676 subjects with >=5 non-empty entries, 11328 entries.

## Protocol (faithful CM-3 transfer, `data/scripts/cm_xval_openplay.py`)
- Subject-disjoint 70/15/15 split (473/101/102), fresh seed 20260921 (does NOT touch the
  frozen CM-2 seal).
- Frozen MiniLM (all-MiniLM-L6-v2, 384-d) embeddings; k=3 history.
- Per horizon h in (1,2,3,5,10): fit `LinearMultiHorizon` (alpha=100) on TRAIN, select the
  strongest baseline B0-B7 on VAL, evaluate model + baseline on sealed TEST.
- Metric: per-subject mean cosine of predicted vs actual target embedding.
- PredictiveGain(h) = Model(h) - StrongBaseline(h), subject-level bootstrap CI (B=2000).
- Target-shuffle permutation test on the primary horizon (B=1000).
- Leakage audit passed (history strictly before target, same subject).

## Results
| h | model | strong baseline | gain | gain 95% CI |
| --- | --- | --- | --- | --- |
| 1 | 0.6414 | B3_khistory 0.6250 | +0.0164 | [+0.0094, +0.0229] |
| 2 | 0.6382 | B3_khistory 0.6207 | +0.0175 | [+0.0096, +0.0253] |
| 3 | 0.6355 | B4_drift 0.6016   | +0.0339 | [+0.0144, +0.0508] |
| 5 | 0.6314 | B3_khistory 0.6011 | +0.0303 | [+0.0193, +0.0429] |
| 10 | 0.6161 | B3_khistory 0.5984 | +0.0177 | [+0.0082, +0.0271] |

Permutation (h=1): observed test cosine 0.6509 vs target-shuffle null 0.6531, **p=0.707**.

## Interpretation (honest)
1. **The "beats frozen baselines" effect replicates.** At every horizon the linear model
   beats the strongest frozen baseline with a subject-level CI that excludes zero. The gain
   is positive across horizons with the same qualitative shape as CM-3 (peaking mid-horizon).
   This is a faithful external replication of the PredictiveGain phenomenon.
2. **But the effect is weak and largely a within-person similarity artifact.** The absolute
   test cosine (~0.64) is high because a person's activity descriptions are mutually similar
   (they recur). The target-shuffle permutation is NOT significant (p=0.71): the model's
   prediction is about as similar to the actual next entry as to a random entry of the same
   person. So the model is not strongly predicting the *specific* next entry — it is
   predicting "a typical entry for this person," which the retrieval baselines already do.
3. **Net:** the CM-2/CM-3 predictive-dynamics effect **partially replicates** on an external,
   domain-shifted dataset. The "incremental over baselines" signal transfers; the strong
   temporal-semantic prediction that was clearer on rich thought-streams does not fully
   transfer to short, repetitive activity text. This is a boundary-condition finding, not a
   refutation.

## Decision rationale
- Not `CMXVAL_PASS_REPLICATION`: the permutation (specific next-entry prediction) is not
  significant.
- Not `CMXVAL_NULL_NO_REPLICATION`: the model significantly beats the strongest frozen
  baseline at all horizons (gain CIs exclude 0).
- `CMXVAL_PARTIAL`: the baseline-beating effect transfers, but the underlying temporal
  semantic prediction is weak on this domain.

## Limitations
- Short text (~2.7 words) limits semantic signal; MiniLM on 2-3 word phrases is less
  discriminative than on full thoughts.
- Single external dataset; a second domain (e.g., van Halem "Daily event", openESM 0070)
  would strengthen the conclusion.
- The `displaced_activity` field is a specific prompt, not a free thought stream.

## Reproduction
```
# data: data/clean/survey_daily.csv.gz from https://github.com/digital-wellbeing/open-play
.venv/bin/python data/scripts/cm_xval_openplay.py
```
Machine-readable result: `reports/cm_xval/cm_xval_openplay.json`.
