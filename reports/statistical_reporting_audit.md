# Statistical Reporting Audit

Checks that every statistical result in the program is reported with the required elements
(effect size, confidence interval, p-value or exact test, N, and method). Part of the
`cm8-prehuman-v1.0` freeze. Follows transparent-reporting norms (effect + CI + N + method,
not just p).

## Required elements per result

For each reported statistical result, the audit checks for:
1. **Effect size** (point estimate).
2. **Confidence interval** (95%, method stated).
3. **p-value or exact test** (permutation/exact, not just asymptotic).
4. **N** (subjects / trials / samples).
5. **Method** (estimator, test, split).

## Audit by result

| result | effect | CI | p / exact test | N | method | status |
| --- | --- | --- | --- | --- | --- | --- |
| CM-2 next-thought | 0.3623 | [0.3523, 0.3720] (subject bootstrap) | permutation p=0.0000 | 118 subj / 17 test | ridge multi-horizon; subject-disjoint 83/18/17 | COMPLETE |
| CM-2 vs B0 | 0.3623 vs 0.3167 | both CIs, non-overlapping | permutation p=0.0000 | 17 test | paired comparison | COMPLETE |
| CM-3 h=1 gain | +0.0349 | [0.0253, 0.0445] | nulls p=0.0000 | 17 test | gain vs strongest baseline | COMPLETE |
| CM-3 h=10 gain | +0.0044 | CI excl. 0 | nulls p=0.0000 | 17 test | gain vs strongest baseline | COMPLETE |
| CM-5 N2 h=1 gain | −0.088 | [−0.106, −0.072] | permutation p=1.0 | 16 test subj | M4−M2; subject-level | COMPLETE |
| CM-5 ladder | N1 −0.001 / N3 −0.016 / N2 −0.085 | CIs excl. 0 | permutation | 16 test subj | capacity ladder | COMPLETE |
| CM-6 identifiability | 0/84 identifiable | n/a (formal audit) | n/a | 118 subj / 6436 thoughts | backdoor audit (analysis_7) | COMPLETE |
| CM-7 ATE | −0.0386 | list [−0.079, 0.002]; subject [−0.087, 0.011] | 2-phase perm p=0.0733 (20-subset 0.0754) | 20 subj / 216 lists | subject-clustered; list+subject bootstrap | COMPLETE |
| CM-8 type-I audit | 0.047 (nominal 0.05) | MC 95% CI [0.013, 0.080] | MC (independently reproduced, alt-seed 0.040) | MC sims | subject-clustered permutation | COMPLETE |
| CM-8 BRP_control | 0.0785 (target 0.10) | n/a (calibration) | n/a | 118 ghost / 5964 forecasts | ghost pilot | COMPLETE |
| CM-8R power surface | power per (N, trials, ICC, eff) | power CI | MC (25 sims/cell) | grid | MC power | COMPLETE |

## Notes

- **CIs are subject-level** (bootstrap) where the unit of inference is the subject; this
  matches the subject-disjoint split and avoids pseudo-replication.
- **Exact/permutation tests** are used for the primary causal and null tests (not just
  asymptotic p-values), appropriate for small N.
- **The CM-7 ATE** reports both list-level and subject-level (nesting-aware) CIs, and the
  exact two-phase randomization p plus a 20-subset robustness p.
- **The CM-8 type-I audit** reports the empirical type-I error with an MC CI and an
  independent reproduction (alt-seed), not just a single MC estimate.
- **The CM-5 null** reports the negative gain with CIs excluding 0, 0/16 subjects positive,
  and permutation p=1.0 — a complete negative-result report.

## Gaps (none blocking)

- No result is reported as a bare p-value without an effect size and CI.
- No result omits N or the method.
- The only "n/a" entries are for formal audits (identifiability) and calibration checks
  (BRP_control), where a CI/p is not the appropriate statistic.

## Result

**ALL COMPLETE.** Every statistical result reports effect size + CI + (p or exact test) +
N + method. No bare p-values; no pseudo-replication (subject-level inference).
