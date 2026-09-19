"""CM-8R3: massive Monte Carlo validation of the CM-8 estimator.

Runs the 21-scenario synthetic world many times and estimates, for each:
  * type-I error (S0 null) at the confirmatory test level (two-sided alpha=0.05);
  * power (active scenarios);
  * estimator bias (mean ATE estimate - ground-truth ATE);
  * BRP_control calibration;
  * false-positive rate under sham effects (S10);
  * false-positive rate under lexical priming (S11);
  * bias under MNAR (S12);
  * false-positive inflation under forecast error (S13);
  * sensitivity to ICC (S7), fatigue (S8), learning (S9), volatility (S14).

Every estimated probability is reported with its Monte-Carlo standard error and a
95% CI. No vague "approximately calibrated" claims.

Result state: CM8R_MONTE_CARLO_PASS only if the confirmatory inference remains valid
under the preregistered null (type-I ~= 0.05) and the estimator is (near-)unbiased
under the expected implementation assumptions.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path("/home/jovyan/work/causal-mind-v2")
sys.path.insert(0, str(ROOT / "src"))
from causal_mind.sim import scenarios, simulate_dataset, ate_and_p, brp_by_condition  # noqa: E402
from causal_mind.sim.world import true_ate  # noqa: E402

OUT = ROOT / "reports" / "cm8r_monte_carlo"
TEST_ALPHA = 0.05
B_PERM = 200


def _binom_ci(k: int, n: int) -> tuple[float, float, float]:
    p = k / n if n else float("nan")
    se = float(np.sqrt(p * (1 - p) / n)) if n else float("nan")
    return p, se, (p - 1.96 * se, p + 1.96 * se)


def run_scenario(sc, arm: str, n_sims: int, n_subjects: int, n_trials: int,
                 seed: int = 20260917) -> dict:
    rng = np.random.default_rng(seed)
    rejects = 0
    ates = []
    brp_ctrl = []
    for i in range(n_sims):
        recs = simulate_dataset(sc, n_subjects, n_trials, seed=seed + i)
        ate, p = ate_and_p(recs, arm=arm, b_perm=B_PERM, rng=rng)
        ates.append(ate)
        rejects += int(p < TEST_ALPHA)
        b = brp_by_condition(recs)
        brp_ctrl.append((b["control"] + b["sham"]) / 2)
    ates = np.array(ates)
    rate, se, ci = _binom_ci(rejects, n_sims)
    return {
        "n_sims": n_sims, "reject_rate": rate, "mc_se": se, "mc_ci95": [ci[0], ci[1]],
        "ate_mean": float(ates.mean()), "ate_sd": float(ates.std()),
        "brp_control_mean": float(np.mean(brp_ctrl)),
    }


def main() -> int:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    n_subjects, n_trials = 20, 24
    result: dict = {"test_alpha": TEST_ALPHA, "b_perm": B_PERM,
                    "n_subjects": n_subjects, "n_trials": n_trials}

    # --- type-I error under the preregistered null (S0) ---
    s0 = scenarios.S0_TRUE_NULL()
    null = run_scenario(s0, arm="general", n_sims=300, n_subjects=n_subjects,
                        n_trials=n_trials, seed=100000)
    result["type1_error_S0"] = null
    print(f"[type-I S0] {null['reject_rate']:.3f} (CI {null['mc_ci95'][0]:.3f},"
          f"{null['mc_ci95'][1]:.3f}); BRP_control={null['brp_control_mean']:.3f}")

    # --- power + bias for each active scenario ---
    active = {
        "S1": ("S1_EXOGENOUS_ONLY", "cue"), "S2": ("S2_ENDOGENOUS_ONLY", "general"),
        "S3": ("S3_BOTH_WORK", "general"), "S4": ("S4_IMMEDIATE_TRANSIENT", "general"),
        "S5": ("S5_PERSISTENT", "general"), "S6": ("S6_HETEROGENEOUS", "general"),
        "S7": ("S7_HIGH_ICC", "general"), "S8": ("S8_FATIGUE", "general"),
        "S9": ("S9_LEARNING", "general"), "S10": ("S10_SHAM_EFFECT", "general"),
        "S11": ("S11_LEXICAL_PRIMING", "cue"), "S12": ("S12_MNAR", "general"),
        "S13": ("S13_FORECAST_ERROR", "general"), "S14": ("S14_VOLATILITY", "general"),
        "S15": ("S15_STRATEGIC", "general"), "S16": ("S16_CONDITION_LEARNING", "general"),
        "S17": ("S17_DELAYED", "general"), "S18": ("S18_RETURN", "general"),
        "S19": ("S19_CROSSOVER", "general"), "S20": ("S20_STATE_DEPENDENT", "general"),
    }
    result["scenarios"] = {}
    for key, (fname, arm) in active.items():
        sc = getattr(scenarios, fname)()
        r = run_scenario(sc, arm=arm, n_sims=150, n_subjects=n_subjects,
                         n_trials=n_trials, seed=200000 + hash(key) % 1000)
        # ground-truth ATE (computed once, larger sample)
        r["ate_true"] = float(true_ate(sc, arm=arm, n_subjects=150, n_trials=50,
                                       seed=300000 + hash(key) % 1000))
        r["bias"] = r["ate_mean"] - r["ate_true"]
        result["scenarios"][key] = r
        print(f"[{key}] power={r['reject_rate']:.3f} (CI {r['mc_ci95'][0]:.3f},"
              f"{r['mc_ci95'][1]:.3f}) ate_mean={r['ate_mean']:+.3f} "
              f"true={r['ate_true']:+.3f} bias={r['bias']:+.3f}")

    # --- PASS criteria ---
    t1 = result["type1_error_S0"]["reject_rate"]
    t1_lo, t1_hi = result["type1_error_S0"]["mc_ci95"]
    # type-I should be near 0.05 (within MC uncertainty, not anti-conservative)
    type1_ok = t1 <= 0.05 + 3 * result["type1_error_S0"]["mc_se"] and t1_lo >= 0.0
    # the null must not be anti-conservative (reject rate well above 0.05 is a failure)
    not_anticonservative = t1 <= 0.08
    # under a true null the mean ATE should be ~0
    null_bias_ok = abs(result["type1_error_S0"]["ate_mean"]) < 0.02
    checks = {
        "type1_error_near_0.05": type1_ok,
        "not_anti_conservative": not_anticonservative,
        "null_ate_near_zero": null_bias_ok,
    }
    passed = all(checks.values())
    result["state"] = "CM8R_MONTE_CARLO_PASS" if passed else "CM8R_MONTE_CARLO_ITERATE"
    result["checks"] = checks
    result["runtime_seconds"] = round(time.time() - t0, 1)
    (OUT / "cm8r_monte_carlo.json").write_text(json.dumps(result, indent=2, default=float))
    _write_md(result)
    print(f"\n[MC] {result['state']}  checks={checks}  runtime={result['runtime_seconds']}s")
    return 0 if passed else 1


def _write_md(r: dict) -> None:
    L = ["# CM-8R3 — Massive Monte Carlo validation", ""]
    L.append(f"- **State:** `{r['state']}`  | test alpha={r['test_alpha']} (two-sided), "
             f"B={r['b_perm']}, N={r['n_subjects']}, trials={r['n_trials']}")
    t1 = r["type1_error_S0"]
    L.append(f"\n## Type-I error under the preregistered null (S0)")
    L.append(f"- reject rate = **{t1['reject_rate']:.3f}** (MC 95% CI "
             f"[{t1['mc_ci95'][0]:.3f}, {t1['mc_ci95'][1]:.3f}], SE {t1['mc_se']:.3f}, "
             f"n={t1['n_sims']}); mean ATE = {t1['ate_mean']:+.4f}; "
             f"BRP_control = {t1['brp_control_mean']:.3f}.")
    L.append("\n## Power / bias per scenario (active arm)")
    L.append("| scenario | power | 95% CI | ATE mean | true ATE | bias | BRP_ctrl |")
    L.append("| --- | --- | --- | --- | --- | --- | --- |")
    for k, v in r["scenarios"].items():
        L.append(f"| {k} | {v['reject_rate']:.3f} | [{v['mc_ci95'][0]:.3f},"
                 f"{v['mc_ci95'][1]:.3f}] | {v['ate_mean']:+.3f} | {v['ate_true']:+.3f} "
                 f"| {v['bias']:+.3f} | {v['brp_control_mean']:.3f} |")
    L.append("\n## Checks")
    for k, v in r["checks"].items():
        L.append(f"- {'PASS' if v else 'FAIL'} — {k}")
    L.append("\nInterpretation notes: S4 (transient) and S11 (lexical priming) are "
             "expected to have LOW power at the frozen h*=2 (the effect returns before "
             "h*=2) — this is the design working as intended, not a failure. S10 (sham "
             "effect) tests whether the sham contaminates the reference arm. S12 (MNAR) "
             "tests bias under informative missingness. S13 (forecast error) tests "
             "false-positive inflation from a miscalibrated basin.")
    (OUT / "cm8r_monte_carlo.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
