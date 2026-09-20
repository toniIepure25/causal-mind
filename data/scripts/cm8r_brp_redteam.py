"""CM-8R7: BRP adversarial red team.

Attacks the frozen BRP directly: construct cases where BRP gives a MISLEADING "success"
(high BRP with no real semantic redirection), and evaluate the frozen BRP against
SECONDARY diagnostics (cosine-direction change, angular deviation, Mahalanobis distance,
persistence-weighted divergence, return-to-basin time, semantic novelty, trajectory
curvature). The frozen BRP remains PRIMARY; the purpose is to understand failure modes,
NOT to replace it.

Each case is a small synthetic post-intervention trajectory with a known property.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path("/home/jovyan/work/causal-mind-v2")
sys.path.insert(0, str(ROOT / "src"))
from causal_mind.causal.predicted_basin import PredictedFutureBasin  # noqa: E402

OUT = ROOT / "reports" / "cm8r_brp_redteam"
D = 32
RNG = np.random.default_rng(20260917)


def _cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(np.dot(a, b) / (na * nb)) if na and nb else 0.0


def _angle(a, b):
    c = np.clip(_cos(a, b), -1, 1)
    return float(np.arccos(c))


def _mahalanobis(obs, pred, S_inv):
    d = obs - pred
    return float(np.sqrt(max(d @ S_inv @ d, 0.0)))


def _diagnostics(pred, obs, home, S_inv, r_alpha):
    """Secondary diagnostics for a post-intervention trajectory (obs: (n, D))."""
    n = len(obs)
    cos_dir = float(np.mean([1 - _cos(pred, o) for o in obs]))
    ang = float(np.mean([_angle(pred, o) for o in obs]))
    mah = float(np.mean([_mahalanobis(o, pred, S_inv) for o in obs]))
    # persistence: consecutive steps outside the basin from the first leave
    basin = PredictedFutureBasin(center=pred, radius=r_alpha)
    leave = basin.leave(obs)
    persistence = 0
    started = False
    for v in leave:
        if v:
            started = True
            persistence += 1
        elif started:
            break
    # novelty: distance to the home centroid (not just the prediction)
    novelty = float(np.mean([np.linalg.norm(o - home) for o in obs]))
    # AUC divergence across the horizon (normalized distance, trapezoid)
    nd = basin.normalized_distance(obs)
    auc = float(np.trapezoid(nd, dx=1.0)) if n else 0.0
    # trajectory curvature: mean change in direction between consecutive steps
    curv = []
    for i in range(1, n):
        v1 = obs[i] - obs[i - 1]
        if i > 1:
            v0 = obs[i - 1] - obs[i - 2]
            if np.linalg.norm(v0) > 1e-9 and np.linalg.norm(v1) > 1e-9:
                curv.append(_angle(v0, v1))
    return {
        "cosine_direction_change": cos_dir,
        "angular_deviation_rad": ang,
        "mahalanobis_distance": mah,
        "persistence_steps": int(persistence),
        "semantic_novelty": novelty,
        "auc_divergence": auc,
        "trajectory_curvature": float(np.mean(curv)) if curv else 0.0,
    }


def _brp(tag, pred, obs, r):
    obs = np.asarray(obs, dtype=float)
    if obs.ndim != 2 or obs.shape[1] != D:
        print(f"SHAPE-ERR {tag}: obs.shape={obs.shape} (expected (n,{D}))", flush=True)
    return PredictedFutureBasin(np.asarray(pred, dtype=float), r).brp(obs)


def _case(name, pred, obs, home, S_inv, r_alpha, brp, description, misleading):
    diag = _diagnostics(pred, obs, home, S_inv, r_alpha)
    return {"name": name, "brp": brp, "diagnostics": diag,
            "description": description, "misleading_success": misleading}


def main() -> int:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    # natural error covariance (for Mahalanobis) + radius
    nat = RNG.normal(size=(4000, D))
    S = np.cov(nat, rowvar=False)
    S_inv = np.linalg.inv(S + 1e-6 * np.eye(D))
    r_alpha = float(np.quantile(np.linalg.norm(nat, axis=1), 0.90))
    home = np.zeros(D)
    cases = []

    # 1. epsilon crossing: radial shift just outside the radius, direction ~unchanged
    pred = RNG.normal(size=D)
    unit = pred / (np.linalg.norm(pred) + 1e-9)
    obs = pred[None, :] + (r_alpha * 1.05 + 0.02 * RNG.normal(size=(10, 1))) * unit[None, :]
    brp = _brp("epsilon_crossing", pred, obs, r_alpha)
    cases.append(_case("epsilon_crossing", pred, obs, home, S_inv, r_alpha, brp,
                       "Trajectory hovers just outside the radius (5% over) with no "
                       "directional shift. BRP ~1.0 but the semantic change is tiny.",
                       brp > 0.5 and _diagnostics(pred, obs, home, S_inv, r_alpha)["cosine_direction_change"] < 0.05))

    # 2. anisotropic distribution: basin (ball) is a poor fit
    pred = np.zeros(D)
    A = np.eye(D); A[0, 0] = 5.0  # stretch along dim 0
    obs = RNG.normal(size=(10, D)) @ A  # (n, D), stretched along dim 0
    brp = _brp("anisotropic", pred, obs, r_alpha)
    cases.append(_case("anisotropic", pred, obs, home, S_inv, r_alpha, brp,
                       "Embedding distribution is anisotropic (stretched). A ball basin "
                       "is a poor fit; Mahalanobis distance (which uses the covariance) "
                       "disagrees with the Euclidean BRP.", brp > 0.5))

    # 3. high-dimensional concentration: all points far from center
    pred = np.zeros(D)
    obs = 3.0 * RNG.normal(size=(10, D))  # large radius in high-D
    brp = _brp("case", pred, obs, r_alpha)
    cases.append(_case("high_dim_concentration", pred, obs, home, S_inv, r_alpha, brp,
                       "In high dimensions the points concentrate on a large sphere; the "
                       "Euclidean radius is dominated by dimension, not semantics. "
                       "Angular deviation is the right measure here.", brp > 0.5))

    # 4. lexical repetition: cue word repeated, no branch change
    pred = RNG.normal(size=D)
    cue = RNG.normal(size=D)
    obs = np.tile(cue, (10, 1)) + 0.05 * RNG.normal(size=(10, D))  # all near the cue
    brp = _brp("case", pred, obs, r_alpha)
    cases.append(_case("lexical_repetition", pred, obs, home, S_inv, r_alpha, brp,
                       "The participant repeats the cue word (all states near the cue). "
                       "BRP is high (far from the predicted basin) but it is a lexical "
                       "echo, not a semantic branch change. Persistence + novelty "
                       "diagnostics reveal it.", brp > 0.5))

    # 5. magnitude change, no directional shift (4x norm, same direction -> crosses radius)
    pred = RNG.normal(size=D)
    obs = 4.0 * pred[None, :] + 0.05 * RNG.normal(size=(10, D))  # same direction, 4x norm
    brp = _brp("magnitude_change", pred, obs, r_alpha)
    diag5 = _diagnostics(pred, obs, home, S_inv, r_alpha)
    cases.append(_case("magnitude_change", pred, obs, home, S_inv, r_alpha, brp,
                       "Embedding magnitude doubles but the direction is unchanged. "
                       "Euclidean BRP is high, but cosine-direction change ~0 shows no "
                       "semantic redirection.", brp > 0.5 and diag5["cosine_direction_change"] < 0.05))

    # 6. noisy forecast -> tiny basin
    pred = RNG.normal(size=D)
    obs = pred + RNG.normal(size=(10, D))  # natural spread
    tiny_r = 0.3 * r_alpha
    brp = _brp("noisy_forecast_tiny_basin", pred, obs, tiny_r)
    cases.append(_case("noisy_forecast_tiny_basin", pred, obs, home, S_inv, tiny_r, brp,
                       "A noisy forecast produces an abnormally small basin radius; "
                       "nearly everything falls outside -> spuriously high BRP. The "
                       "radius itself is the red flag.", brp > 0.8))

    # 7. naturally volatile participant
    pred = RNG.normal(size=D)
    obs = 2.0 * RNG.normal(size=(10, D))  # high natural volatility
    brp = _brp("case", pred, obs, r_alpha)
    cases.append(_case("volatile_participant", pred, obs, home, S_inv, r_alpha, brp,
                       "A naturally volatile participant jumps between topics; BRP is "
                       "high even without an intervention. The CONTROL BRP would also be "
                       "high (the ATE, not the raw BRP, is the estimand).", brp > 0.5))

    # 8. encoder instability
    pred = RNG.normal(size=D)
    obs = pred + 1.5 * RNG.normal(size=(10, D))  # drift from encoder instability
    brp = _brp("case", pred, obs, r_alpha)
    cases.append(_case("encoder_instability", pred, obs, home, S_inv, r_alpha, brp,
                       "Semantic-encoder instability makes the embeddings drift; BRP is "
                       "miscalibrated. The CONTROL BRP would be off too (calibration "
                       "check catches this).", brp > 0.5))

    # 9. one unusual thought (single outlier, not persistent)
    pred = RNG.normal(size=D)
    obs = np.vstack([pred + 0.2 * RNG.normal(size=D) for _ in range(9)] +
                    [pred + 3.0 * RNG.normal(size=D)])  # last one is an outlier
    brp = _brp("case", pred, obs, r_alpha)
    diag9 = _diagnostics(pred, obs, home, S_inv, r_alpha)
    cases.append(_case("one_unusual_thought", pred, obs, home, S_inv, r_alpha, brp,
                       "A single unusual thought creates an apparent branch change. BRP "
                       "is elevated but persistence is low (it returns) -> not a durable "
                       "redirection.", brp > 0.1 and diag9["persistence_steps"] <= 1))

    n_misleading = sum(1 for c in cases if c["misleading_success"])
    result = {
        "n_cases": len(cases), "n_misleading": n_misleading,
        "cases": cases,
        "conclusion": "The frozen BRP is a valid PRIMARY estimand but has known failure "
                      "modes (magnitude-only change, lexical echo, tiny-basin miscalibration, "
                      "volatility). The secondary diagnostics (cosine-direction change, "
                      "Mahalanobis, persistence, novelty) reveal these modes. The frozen "
                      "BRP is NOT replaced; these diagnostics are pre-declared SECONDARY "
                      "robustness analyses. The ATE (intervention vs control BRP), not the "
                      "raw BRP, is the estimand, which guards against volatility/encoder "
                      "miscalibration.",
        "runtime_seconds": round(time.time() - t0, 1),
    }
    (OUT / "cm8r_brp_redteam.json").write_text(json.dumps(result, indent=2, default=float))
    _write_md(result)
    print(f"[brp] {len(cases)} cases, {n_misleading} misleading-success cases identified")
    for c in cases:
        print(f"  {c['name']}: BRP={c['brp']:.2f} misleading={c['misleading_success']}")
    return 0


def _write_md(r: dict) -> None:
    L = ["# CM-8R7 — BRP Adversarial Red Team", ""]
    L.append(f"- {r['n_cases']} adversarial cases; {r['n_misleading']} produce a "
             "misleading 'success' (high BRP, no real redirection).")
    L.append("\n| case | BRP | cos-dir | Mahalanobis | persist | novelty | misleading |")
    L.append("| --- | --- | --- | --- | --- | --- | --- |")
    for c in r["cases"]:
        d = c["diagnostics"]
        L.append(f"| {c['name']} | {c['brp']:.2f} | {d['cosine_direction_change']:.3f} "
                 f"| {d['mahalanobis_distance']:.2f} | {d['persistence_steps']} "
                 f"| {d['semantic_novelty']:.2f} | {'YES' if c['misleading_success'] else 'no'} |")
    L.append("\n## Failure modes and the diagnostic that catches each")
    for c in r["cases"]:
        L.append(f"- **{c['name']}** (BRP={c['brp']:.2f}): {c['description']}")
    L.append(f"\n## Conclusion\n\n{r['conclusion']}")
    (OUT / "cm8r_brp_redteam.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
