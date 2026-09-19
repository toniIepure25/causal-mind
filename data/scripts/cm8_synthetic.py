"""CM-8D: synthetic participant simulator + causal estimator validation.

Generates synthetic thought-stream data with KNOWN intervention effects and
validates that the CM-8 BRP/ATE estimators (a) return a null under H0 (no false
positive at the confirmatory test level) and (b) recover a known effect (unbiased).
This is the data-independent gate G2.

STATISTICAL AUDIT (2026-09-17): the basin tail and the confirmatory test level are
SEPARATE parameters.
  * ``basin_tail`` (design parameter): the basin radius is the (1-basin_tail) quantile
    of the held-out prediction-error norm, so BRP_control ~= basin_tail (target 0.10).
  * ``test_alpha`` (confirmatory significance level): the ATE is tested at alpha=0.05.
The type-I error MUST be measured at the test level (0.05), not the basin tail. The
earlier reported 0.113 was measured at a 0.10 test level (the two were conflated); this
script measures the type-I error at the correct 0.05 level with Monte-Carlo uncertainty.

Model (minimal but faithful to the BRP):
  * Each trial has an "error norm" = distance of the observed future from the frozen
    predictor's forecast. Under the natural (CONTROL/SHAM) trajectory the error norm has
    a baseline distribution; the basin radius r_alpha is the (1-basin_tail) quantile of
    that baseline, so BRP_control ~= basin_tail by construction.
  * An intervention (GENERAL REDIRECT / SPECIFIC CUE) adds a non-negative push to the
    error norm, increasing the probability of leaving the basin (BRP).
  * The ATE is the difference in BRP between an intervention arm and the CONTROL/SHAM
    reference, with a subject-clustered permutation test.
"""
from __future__ import annotations

import numpy as np

B_PERM = 200
SEED = 20260917
BASIN_TAIL = 0.10  # design parameter: BRP_control ~= this


def _error_norms(n: int, sigma_e: float, push: float, rng: np.random.Generator) -> np.ndarray:
    """Baseline error norm (half-normal) plus a non-negative intervention push."""
    base = np.abs(rng.normal(0.0, sigma_e, size=n))
    return base + push


def simulate_dataset(n_subjects: int, trials_per_subject: int, sigma_e: float,
                     push_general: float, push_cue: float, basin_tail: float,
                     rng: np.random.Generator):
    """Simulate a full dataset. ``basin_tail`` sets the radius (BRP_control ~ basin_tail)."""
    heldout = _error_norms(4000, sigma_e, 0.0, rng)
    r_alpha = float(np.quantile(heldout, 1.0 - basin_tail))
    conds = ["control", "sham", "general", "cue"]
    push = {"control": 0.0, "sham": 0.0, "general": push_general, "cue": push_cue}
    subjects, conditions, leave, err = [], [], [], []
    for s in range(n_subjects):
        for _ in range(trials_per_subject):
            c = conds[rng.integers(0, 4)]
            e = float(_error_norms(1, sigma_e, push[c], rng)[0])
            subjects.append(s)
            conditions.append(c)
            err.append(e)
            leave.append(1 if e > r_alpha else 0)
    return np.array(subjects), np.array(conditions), np.array(leave), np.array(err), r_alpha


def _ate_and_p(subjects, conditions, leave, ref=("control", "sham"), arm="general",
               rng: np.random.Generator | None = None) -> tuple[float, float]:
    """ATE = mean(leave | arm) - mean(leave | ref), subject-clustered permutation p."""
    arm_mask = conditions == arm
    ref_mask = np.isin(conditions, ref)
    ate = float(leave[arm_mask].mean() - leave[ref_mask].mean())

    def _diff(a):
        am = a == arm
        rm = np.isin(a, ref)
        return leave[am].mean() - leave[rm].mean()

    groups = [np.where(subjects == s)[0] for s in np.unique(subjects)]
    null = np.empty(B_PERM)
    for b in range(B_PERM):
        perm = conditions.copy()
        for idx in groups:
            perm[idx] = rng.permutation(conditions[idx])
        null[b] = _diff(perm)
    p = float(np.mean(np.abs(null) >= abs(ate)))
    return ate, p


def type1_error(n_sims: int, n_subjects: int, trials: int, sigma_e: float,
                test_alpha: float, basin_tail: float, seed: int = SEED) -> dict:
    """Type-I error at the TEST level ``test_alpha`` (no push anywhere).

    Returns the estimate plus its Monte-Carlo (binomial) standard error and 95% CI.
    """
    rng = np.random.default_rng(seed)
    rejects = 0
    ates = []
    for _ in range(n_sims):
        subj, cond, leave, err, _ = simulate_dataset(
            n_subjects, trials, sigma_e, 0.0, 0.0, basin_tail, rng)
        ate, p = _ate_and_p(subj, cond, leave, arm="general", rng=rng)
        ates.append(ate)
        rejects += int(p < test_alpha)
    ti = rejects / n_sims
    se = float(np.sqrt(ti * (1.0 - ti) / n_sims))
    ates = np.array(ates)
    return {
        "type1_error": ti,
        "mc_se": se,
        "mc_ci95": (ti - 1.96 * se, ti + 1.96 * se),
        "nominal_test_alpha": test_alpha,
        "mean_ate": float(ates.mean()),
        "sd_ate": float(ates.std()),
        "n_sims": n_sims,
    }


def brp_calibration(sigma_e: float, basin_tail: float, seed: int = SEED) -> dict:
    """Check that BRP_control ~= basin_tail (the radius calibration is correct)."""
    rng = np.random.default_rng(seed)
    heldout = _error_norms(200000, sigma_e, 0.0, rng)
    r_alpha = float(np.quantile(heldout, 1.0 - basin_tail))
    fresh = _error_norms(200000, sigma_e, 0.0, rng)
    brp_control = float((fresh > r_alpha).mean())
    return {"brp_control": brp_control, "target_basin_tail": basin_tail, "r_alpha": r_alpha}


def recovery(n_sims: int, n_subjects: int, trials: int, sigma_e: float, push: float,
             basin_tail: float, seed: int = SEED) -> dict:
    """Recovery: a known push on the GENERAL arm -> ATE estimate vs the truth."""
    rng = np.random.default_rng(seed)
    truth_rng = np.random.default_rng(seed + 1)
    base = _error_norms(200000, sigma_e, 0.0, truth_rng)
    pushed = _error_norms(200000, sigma_e, push, truth_rng)
    r_alpha = float(np.quantile(base, 1.0 - basin_tail))
    true_ate = float((pushed > r_alpha).mean() - (base > r_alpha).mean())
    ates = []
    for _ in range(n_sims):
        subj, cond, leave, err, _ = simulate_dataset(
            n_subjects, trials, sigma_e, push, 0.0, basin_tail, rng)
        ate, p = _ate_and_p(subj, cond, leave, arm="general", rng=rng)
        ates.append(ate)
    ates = np.array(ates)
    return {
        "true_ate": true_ate,
        "mean_ate_estimate": float(ates.mean()),
        "sd_ate_estimate": float(ates.std()),
        "bias": float(ates.mean() - true_ate),
        "n_sims": n_sims,
        "push": push,
    }


def main() -> None:
    sigma_e = 1.0
    n_subjects = 20
    trials = 24
    print("=== CM-8D synthetic estimator validation (statistical audit) ===")
    print(f"config: basin_tail={BASIN_TAIL} (BRP_control target), sigma_e={sigma_e}, "
          f"n_subjects={n_subjects}, trials/subject={trials}, B_PERM={B_PERM}")
    cal = brp_calibration(sigma_e, BASIN_TAIL)
    print(f"\n[BRP calibration] BRP_control={cal['brp_control']:.4f} "
          f"(target basin_tail={BASIN_TAIL}), r_alpha={cal['r_alpha']:.4f}")
    for test_alpha in (0.05, 0.10):
        t1 = type1_error(n_sims=150, n_subjects=n_subjects, trials=trials,
                         sigma_e=sigma_e, test_alpha=test_alpha, basin_tail=BASIN_TAIL)
        print(f"\n[type-I @ test_alpha={test_alpha}] observed={t1['type1_error']:.3f} "
              f"(MC 95% CI [{t1['mc_ci95'][0]:.3f}, {t1['mc_ci95'][1]:.3f}], "
              f"SE {t1['mc_se']:.3f}); mean ATE={t1['mean_ate']:+.4f} (sd {t1['sd_ate']:.4f})")
    for push in (0.3, 0.6, 1.0):
        rec = recovery(n_sims=50, n_subjects=n_subjects, trials=trials,
                       sigma_e=sigma_e, push=push, basin_tail=BASIN_TAIL)
        print(f"\n[recovery push={push}] true ATE={rec['true_ate']:.4f}, "
              f"mean estimate={rec['mean_ate_estimate']:.4f} (bias {rec['bias']:+.4f})")


if __name__ == "__main__":
    main()
