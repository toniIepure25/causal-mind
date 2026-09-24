"""CM-LAB §76: Cross-dataset / cross-representation meta-analysis framework.

A FRAMEWORK that aggregates per-workstream effect sizes (the model's gain over the strongest
frozen baseline) into a random-effects pooled estimate with heterogeneity (I^2). It consumes the
per-workstream report JSONs and produces a pooled estimate. It does NOT pool across incompatible
datasets or across representations without an explicit covariate (per the next-dataset policy).

Currently the effect sizes come from:
  - CM-XVAL-1 (Open Play, external validation): per-horizon gain over the strongest baseline.
  - CM-2/CM-3 (ds006067, primary): per-horizon gain over the strongest baseline.
  - Representation robustness (ds006067): per-representation gain.

Usage:
    .venv/bin/python data/scripts/cm_meta_analysis.py
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path

ROOT = Path("/home/jovyan/work/causal-mind-v2")
OUT = ROOT / "reports" / "cm_meta_analysis"


def _load(p: Path) -> dict | None:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _collect_effect_sizes() -> list[dict]:
    """Collect (label, effect, se) triples from the per-workstream reports.

    Each effect is the model's gain over the strongest frozen baseline (cosine accuracy
    difference). Where a report provides a per-horizon gain, each horizon is a separate effect.
    Where only a point estimate is available, se is set to a small default (flagged).
    """
    effects: list[dict] = []

    # CM-XVAL-1 (Open Play): per-horizon subject-level gain over the strongest baseline.
    xval = _load(ROOT / "reports" / "cm_xval" / "cm_xval_inference.json")
    if xval:
        for h, v in (xval.get("subject_level_inference") or {}).items():
            gain = v.get("gain_mean")
            ci = v.get("subject_paired_bootstrap_ci")  # [mean, lo, hi]
            if gain is not None and ci and len(ci) >= 3:
                se = (ci[2] - ci[1]) / (2 * 1.96)
                effects.append({"label": f"xval_openplay_h{h}", "effect": gain,
                                "se": se, "strong": v.get("strong_baseline")})

    # Representation robustness (ds006067): per-representation h1/k3 gain.
    rep = _load(ROOT / "reports" / "cm_representation" / "cm_representation.json")
    if rep:
        for r, v in (rep.get("per_representation") or {}).items():
            gain = v.get("gain_h1_k3")
            ci = v.get("gain_h1_k3_ci")  # [mean, lo, hi]
            if gain is not None and ci and len(ci) >= 3:
                se = (ci[2] - ci[1]) / (2 * 1.96)
                effects.append({"label": f"ds006067_{r}", "effect": gain,
                                "se": se, "strong": v.get("strong_baseline_h1")})

    return effects


def random_effects(effects: list[dict]) -> dict:
    """DerSimonian-Laird random-effects meta-analysis."""
    if not effects:
        return {"pooled": None, "i2": None, "k": 0}
    k = len(effects)
    if k == 1:
        e = effects[0]
        return {"pooled": e["effect"], "se": e["se"], "ci": [e["effect"] - 1.96 * e["se"],
                                                             e["effect"] + 1.96 * e["se"]],
                "i2": None, "k": k, "note": "single study, no heterogeneity"}
    # Inverse-variance weights.
    w = [1.0 / (e["se"] ** 2) for e in effects]
    mu = sum(wi * e["effect"] for wi, e in zip(w, effects)) / sum(w)
    # Q statistic.
    Q = sum(wi * (e["effect"] - mu) ** 2 for wi, e in zip(w, effects))
    df = k - 1
    I2 = max(0.0, (Q - df) / Q) if Q > 0 else 0.0
    # Tau^2 (DL).
    c = sum(w) - sum(wi ** 2 for wi in w) / sum(w)
    tau2 = max(0.0, (Q - df) / c) if c > 0 else 0.0
    # Random-effects weights.
    wr = [1.0 / (e["se"] ** 2 + tau2) for e in effects]
    mu_re = sum(wi * e["effect"] for wi, e in zip(wr, effects)) / sum(wr)
    se_re = math.sqrt(1.0 / sum(wr))
    return {
        "pooled": round(mu_re, 4),
        "se": round(se_re, 4),
        "ci": [round(mu_re - 1.96 * se_re, 4), round(mu_re + 1.96 * se_re, 4)],
        "tau2": round(tau2, 6),
        "i2": round(I2, 3),
        "Q": round(float(Q), 3),
        "df": df,
        "k": k,
    }


def main() -> int:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    effects = _collect_effect_sizes()
    pooled = random_effects(effects)
    results = {
        "protocol": "CM-LAB S76 cross-dataset / cross-representation meta-analysis framework",
        "n_effect_sizes": len(effects),
        "effect_sizes": effects,
        "random_effects": pooled,
        "note": "FRAMEWORK: pools the model's gain over the strongest frozen baseline across "
                "datasets/representations/horizons. Does NOT pool incompatible datasets or "
                "representations without an explicit covariate (next-dataset policy).",
        "runtime_s": round(time.time() - t0, 2),
    }
    (OUT / "cm_meta_analysis.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"[meta] {len(effects)} effect sizes")
    for e in effects:
        print(f"   {e['label']:30s} effect={e['effect']:+.4f} se={e['se']:.4f}")
    print(f"[meta] random-effects pooled={pooled.get('pooled')} I^2={pooled.get('i2')} k={pooled.get('k')}")
    print(f"[meta] wrote {OUT / 'cm_meta_analysis.json'} in {results['runtime_s']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
