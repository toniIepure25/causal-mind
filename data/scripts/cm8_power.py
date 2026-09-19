"""CM-8E: power analysis via simulation (participants x trials, ICC, attrition).

Builds on the CM-8D synthetic model but adds a subject-level random effect so
that trials within a subject are correlated (ICC). For a range of sample sizes
N and intervention effect sizes (BRP difference), it estimates the power to
detect the GENERAL-REDIRECT ATE at alpha=0.05 using the same subject-clustered
permutation test as the confirmatory analysis.

The effect is parameterized by the intervention "push" on the error norm; the
resulting BRP difference (the ATE) is reported so the curves can be read in
terms of the actual minimally-interesting effect, not an arbitrary push.
"""
from __future__ import annotations

import numpy as np

B_PERM = 150
ALPHA_BASIN = 0.10  # basin tail (BRP_control ~= this)
TEST_ALPHA = 0.05   # confirmatory test level
SEED = 20260917


def _error_norms(n, sigma_e, delta_s, push, rng):
    base = np.abs(rng.normal(delta_s, sigma_e, size=n))
    return base + push


def simulate_dataset_icc(n_subjects, trials, sigma_e, sigma_s, push_general,
                         alpha, rng):
    """Dataset with a subject-level random effect (within-subject correlation)."""
    heldout = np.abs(rng.normal(0.0, sigma_e, 4000))
    r_alpha = float(np.quantile(heldout, 1.0 - alpha))
    conds = ["control", "sham", "general", "cue"]
    push = {"control": 0.0, "sham": 0.0, "general": push_general, "cue": 0.0}
    subjects, conditions, leave = [], [], []
    for s in range(n_subjects):
        delta_s = float(rng.normal(0.0, sigma_s))
        for _ in range(trials):
            c = conds[rng.integers(0, 4)]
            e = float(_error_norms(1, sigma_e, delta_s, push[c], rng)[0])
            subjects.append(s)
            conditions.append(c)
            leave.append(1 if e > r_alpha else 0)
    return np.array(subjects), np.array(conditions), np.array(leave)


def _ate_and_p(subjects, conditions, leave, ref=("control", "sham"), arm="general",
               rng=None) -> tuple[float, float]:
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


def true_ate_for_push(push, sigma_e, alpha, rng) -> float:
    base = _error_norms(200000, sigma_e, 0.0, 0.0, rng)
    pushed = _error_norms(200000, sigma_e, 0.0, push, rng)
    r_alpha = float(np.quantile(base, 1.0 - alpha))
    return float((pushed > r_alpha).mean() - (base > r_alpha).mean())


def power_for_n(n_subjects, trials, sigma_e, sigma_s, push, n_reps, seed) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    rejects, ates = 0, []
    for _ in range(n_reps):
        subj, cond, leave = simulate_dataset_icc(
            n_subjects, trials, sigma_e, sigma_s, push, ALPHA_BASIN, rng)
        ate, p = _ate_and_p(subj, cond, leave, arm="general", rng=rng)
        ates.append(ate)
        rejects += int(p < TEST_ALPHA)
    return rejects / n_reps, float(np.mean(ates))


def main() -> None:
    sigma_e = 1.0
    sigma_s = 0.5  # ICC = sigma_s^2/(sigma_s^2+sigma_e^2) = 0.2
    trials = 24
    n_reps = 40
    icc = sigma_s ** 2 / (sigma_s ** 2 + sigma_e ** 2)
    print("=== CM-8E power analysis (simulation) ===")
    print(f"config: ICC={icc:.2f} (sigma_s={sigma_s}, sigma_e={sigma_e}), "
          f"trials/subject={trials}, basin alpha={ALPHA_BASIN}, test alpha={TEST_ALPHA}, "
          f"n_reps={n_reps}, B_PERM={B_PERM}")
    truth_rng = np.random.default_rng(SEED + 7)
    print("\npush -> true ATE (BRP difference):")
    pushes = [0.4, 0.6, 0.8]
    true_ates = {p: true_ate_for_push(p, sigma_e, ALPHA_BASIN, truth_rng) for p in pushes}
    for p in pushes:
        print(f"  push={p}: true ATE ~ {true_ates[p]:.3f}")
    print("\npower (fraction of reps with p<0.05) by N and effect:")
    print("N      " + "".join(f"push={p} (d~{true_ates[p]:.2f})   " for p in pushes))
    for N in (10, 20, 30, 40):
        row = f"{N:<6} "
        for p in pushes:
            pw, mean_ate = power_for_n(N, trials, sigma_e, sigma_s, p, n_reps, SEED + N)
            row += f"{pw:.2f} (ATE {mean_ate:+.3f})      "
        print(row)
    print("\nAttrition note: to obtain N completed subjects at attrition a, recruit "
          f"ceil(N/(1-a)). E.g. N=20 at a=0.2 -> recruit 25.")


if __name__ == "__main__":
    main()
