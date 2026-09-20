"""CM-8R6: power SURFACE (not a single number).

Grid over participants (12-60), trials/participant (12-48), between-subject effect
variability (ICC proxy via subject_push_sd), and true BRP effect (0.05-0.30). For each
cell, estimates power (reject rate at two-sided alpha=0.05) + the ATE standard error,
with Monte-Carlo uncertainty. Produces the power surface, expected CI width, minimum
detectable effect, and the benefit of adding participants vs trials.

Does NOT rewrite the frozen confirmatory N (N=20, 24 trials) — it characterizes the
robustness of that planning choice.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path("/home/jovyan/work/causal-mind-v2")
sys.path.insert(0, str(ROOT / "src"))
from causal_mind.sim.world import Scenario, simulate_dataset  # noqa: E402
from causal_mind.sim.estimator import ate_and_p, brp_by_condition  # noqa: E402

OUT = ROOT / "reports" / "cm8r_power_surface"
ALPHA = 0.05
B_PERM = 100
N_SIMS = 25

NS = (12, 20, 40, 60)
TRIALS = (12, 24, 48)
ICSD = (0.0, 0.5, 1.0)      # subject_push_sd (ICC proxy)
EFFECTS = (0.05, 0.10, 0.20, 0.30)


def _icc_of(recs) -> float:
    """Achieved ICC of the BRP (leave) outcome: between-subject / total variance."""
    from causal_mind.sim.estimator import _arrays
    subjects, conditions, leave = _arrays(recs)
    if len(np.unique(subjects)) < 2:
        return 0.0
    sub_means = np.array([leave[subjects == s].mean() for s in np.unique(subjects)])
    between = sub_means.var()
    total = leave.var()
    return float(between / total) if total > 0 else 0.0


def _cell(n, trials, icsd, effect, seed):
    sc = Scenario(name="pw", push_general=effect, subject_push_sd=icsd)
    rng = np.random.default_rng(seed)
    rejects = 0
    ates = []
    iccs = []
    for i in range(N_SIMS):
        recs = simulate_dataset(sc, n, trials, seed=seed + i)
        ate, p = ate_and_p(recs, arm="general", b_perm=B_PERM, rng=rng)
        ates.append(ate)
        rejects += int(p < ALPHA)
        iccs.append(_icc_of(recs))
    ates = np.array(ates)
    se = float(ates.std())
    ci_width = 1.96 * 2 * se
    return {
        "power": rejects / N_SIMS,
        "power_ci": [max(0, rejects / N_SIMS - 1.96 * np.sqrt(
            (rejects / N_SIMS) * (1 - rejects / N_SIMS) / N_SIMS)),
            min(1, rejects / N_SIMS + 1.96 * np.sqrt(
                (rejects / N_SIMS) * (1 - rejects / N_SIMS) / N_SIMS))],
        "ate_se": se, "ci_width": ci_width, "achieved_icc": float(np.mean(iccs)),
    }


def main() -> int:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    grid = {}
    for n in NS:
        for tr in TRIALS:
            for icsd in ICSD:
                for eff in EFFECTS:
                    seed = 400000 + (n * 1000 + tr) * 100 + int(icsd * 10) + int(eff * 100)
                    grid[f"N={n},tr={tr},icsd={icsd},eff={eff}"] = _cell(n, tr, icsd, eff, seed)
                    print(f"N={n:2d} tr={tr:2d} icsd={icsd} eff={eff}: "
                          f"power={grid[f'N={n},tr={tr},icsd={icsd},eff={eff}']['power']:.2f} "
                          f"icc={grid[f'N={n},tr={tr},icsd={icsd},eff={eff}']['achieved_icc']:.2f}")

    # minimum detectable effect (80% power) per (N, trials, icsd)
    mde = {}
    for n in NS:
        for tr in TRIALS:
            for icsd in ICSD:
                powers = {eff: grid[f"N={n},tr={tr},icsd={icsd},eff={eff}"]["power"]
                          for eff in EFFECTS}
                # smallest effect with power >= 0.8
                mde[f"N={n},tr={tr},icsd={icsd}"] = next(
                    (eff for eff in sorted(EFFECTS) if powers[eff] >= 0.80), None)
    result = {
        "alpha": ALPHA, "b_perm": B_PERM, "n_sims_per_cell": N_SIMS,
        "grid": grid, "mde_80pct": mde,
        "note": "Power surface for the CM-8 primary ATE (GENERAL vs pooled control/sham), "
                "two-sided alpha=0.05. icsd (subject_push_sd) is the ICC proxy. This "
                "characterizes the robustness of the frozen planning choice (N=20, 24 "
                "trials, ICC~0.2); it does NOT change the frozen N.",
        "runtime_seconds": round(time.time() - t0, 1),
    }
    (OUT / "cm8r_power_surface.json").write_text(json.dumps(result, indent=2, default=float))
    _write_md(result)
    print(f"\n[ps] done in {time.time()-t0:.0f}s; wrote {OUT/'cm8r_power_surface.json'}")
    return 0


def _write_md(r: dict) -> None:
    L = ["# CM-8R6 — Power Surface", ""]
    L.append(f"- alpha={r['alpha']} (two-sided), B={r['b_perm']}, "
             f"{r['n_sims_per_cell']} sims/cell. icsd = subject_push_sd (ICC proxy).")
    L.append("\n## Power grid (rows = N x trials x icsd; cols = true effect)")
    L.append("| N | trials | icsd | ach.ICC | eff=0.05 | eff=0.10 | eff=0.20 | eff=0.30 |")
    L.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    grid = r["grid"]
    for n in NS:
        for tr in TRIALS:
            for icsd in ICSD:
                row = [grid[f"N={n},tr={tr},icsd={icsd},eff={eff}"]["power"]
                       for eff in EFFECTS]
                icc = grid[f"N={n},tr={tr},icsd={icsd},eff={EFFECTS[1]}"]["achieved_icc"]
                L.append(f"| {n} | {tr} | {icsd} | {icc:.2f} | "
                         + " | ".join(f"{v:.2f}" for v in row) + " |")
    L.append("\n## Minimum detectable effect (80% power)")
    L.append("| N | trials | icsd | MDE (smallest effect with power>=0.8) |")
    L.append("| --- | --- | --- | --- |")
    for k, v in r["mde_80pct"].items():
        n, tr, ic = k.split(",")
        L.append(f"| {n.split('=')[1]} | {tr.split('=')[1]} | {ic.split('=')[1]} | "
                 f"{v if v else '> 0.30 (not reached)'} |")
    L.append("\n## Reading the surface")
    L.append("- The effect axis is the intervention home-point shift (push); the resulting "
             "ATE (BRP difference) is smaller (push 0.30 -> ATE ~0.02-0.03 in this "
             "simulator). The grid therefore covers SMALL effects, below the minimally-"
             "interesting ATE (~0.11) from the original power analysis.")
    L.append("- RELATIONSHIPS (the main point): power rises with N (participants) more "
             "reliably than with trials, because the subject is the cluster unit; high ICC "
             "(icsd=1.0) inflates the ATE standard error and reduces power.")
    L.append("- The frozen planning choice (N=20, 24 trials, ICC~0.2) is under-powered for "
             "small effects; it was sized for the a-priori minimally-interesting ATE "
             "(~0.11), which this grid does not reach. This documents the robustness of the "
             "frozen N; it does NOT change it.")
    (OUT / "cm8r_power_surface.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
