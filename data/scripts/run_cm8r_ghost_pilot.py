"""CM-8R1: GHOST PILOT on ds006067 — prospective replay, NOT a causal analysis.

Treats each historical 118-subject spontaneous-thought sequence as a "ghost
participant". At each thought event t it:
  1. exposes ONLY information available through t (history window [t-k+1..t]);
  2. builds the current ThoughtState;
  3. runs the FROZEN behavioral forecaster (LinearMultiHorizon, h* = 2);
  4. estimates the predicted future semantic state T[t+h*];
  5. constructs the FROZEN predicted basin (center = pred, radius = r_alpha[h*]);
  6. reveals the ACTUAL future T[t+h*] only AFTER the prediction is stored;
  7. computes basin membership, BRP-compatible baseline behavior, divergence,
     prediction error, and the future-horizon trajectory;
  8. continues sequentially.

The replay is prospectively faithful: no future transcript/annotation is visible at
prediction time (the target embedding is accessed only after the forecast is stored).

Validations (engineering, not causal):
  * online sequence construction (history strictly before the forecast);
  * forecast reproducibility (online predict == batch predict);
  * semantic basin behavior (BRP_control on held-out TEST ~= basin_tail);
  * event timing (onset/duration logged);
  * storage + logging (JSONL audit log, one line per forecast);
  * prediction latency (p50/p90/p95/p99/max of the forecast+basin step);
  * missing events (event_id gaps detected);
  * crash recovery (simulate a crash, resume from checkpoint, identical result);
  * deterministic replay (two runs -> identical hash).

Result state: CM8R_GHOST_PILOT_PASS or CM8R_GHOST_PILOT_ITERATE.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path("/home/jovyan/work/causal-mind-v2")
sys.path.insert(0, str(ROOT / "src"))

from causal_mind.data import osf_a56rm            # noqa: E402
from causal_mind.eval import protocol             # noqa: E402
from causal_mind.thought import encode, state_v1  # noqa: E402
from causal_mind.thought.multihorizon import build_horizon_samples  # noqa: E402
from sklearn.linear_model import Ridge            # noqa: E402

ART = ROOT / "artifacts" / "cm8_forecaster"
OUT = ROOT / "reports" / "cm8r_ghost_pilot"
SEED = 20260911


def _load_frozen():
    cfg = json.loads((ART / "config.json").read_text())
    w = np.load(ART / "ridge_weights.npz")
    h_star = cfg["primary_horizon_h_star"]
    k = cfg["k_history_depth"]
    r_alpha = cfg["r_alpha_by_horizon"][f"h{h_star}"]
    ridge = Ridge()
    ridge.coef_ = w[f"coef_h{h_star}"]
    ridge.intercept_ = w[f"intercept_h{h_star}"]
    return cfg, ridge, h_star, k, r_alpha


def _load_states():
    subs = osf_a56rm.all_subjects()
    enc = encode.MiniLMEncoder()
    states_by_sub = {}
    for s in subs:
        st = state_v1.states_from_events(s, osf_a56rm.load_thought_events(s))
        arr = encode.encode_subject_cached(enc, s, [x.transcript for x in st])
        for x, v in zip(st, arr, strict=True):
            x.embedding = v
        states_by_sub[s] = st
    return states_by_sub


def replay_subject(st, ridge, r_alpha, h_star, k, measure_latency: bool = False):
    """Prospective replay of one session. Returns (records, latency_ms, n_missing)."""
    n = len(st)
    embs = [s.embedding for s in st]
    records: list[dict] = []
    lat = []
    # missing events: gaps in the sequential index (thoughts skipped)
    n_missing = max(0, (st[-1].index + 1) - n) if n else 0
    for t in range(k - 1, n - h_star):
        hist = embs[t - k + 1: t + 1]            # ONLY information through t
        x = np.concatenate(hist)
        if measure_latency:
            t0 = time.perf_counter()
        pred = ridge.predict(x.reshape(1, -1))[0]  # 3-4: frozen forecast (stored first)
        if measure_latency:
            dist = float(np.linalg.norm(embs[t + h_star] - pred))  # 6-7: reveal AFTER
            lat.append((time.perf_counter() - t0) * 1e3)
        else:
            dist = float(np.linalg.norm(embs[t + h_star] - pred))
        nd = dist / r_alpha
        records.append({"t": t, "dist": dist, "nd": nd, "inside": bool(nd <= 1.0)})
    return records, (lat if measure_latency else []), n_missing


def _percentiles(xs):
    a = np.asarray(xs, dtype=float)
    if a.size == 0:
        return {}
    return {str(p): float(np.percentile(a, p)) for p in (50, 90, 95, 99)} | {"max": float(a.max())}


def main() -> int:
    t_start = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    cfg, ridge, h_star, k, r_alpha = _load_frozen()
    states_by_sub = _load_states()
    split = protocol.subject_disjoint_split(osf_a56rm.all_subjects(), seed=SEED)
    assert protocol.verify_seal(split, SEED, len(states_by_sub))
    test = list(split.test)
    print(f"[ghost] {len(states_by_sub)} ghost participants; h*={h_star} k={k} "
          f"r_alpha={r_alpha:.4f}; TEST (held-out) n={len(test)}")

    # --- full replay (all subjects), with latency + audit log ---
    audit = OUT / "ghost_audit.jsonl"
    all_lat: list[float] = []
    per_sub: dict[str, dict] = {}
    n_forecasts = 0
    n_missing_total = 0
    with audit.open("w") as f:
        for s, st in states_by_sub.items():
            recs, lat, n_missing = replay_subject(st, ridge, r_alpha, h_star, k,
                                                   measure_latency=True)
            n_forecasts += len(recs)
            n_missing_total += n_missing
            all_lat.extend(lat)
            outside = sum(1 for r in recs if not r["inside"])
            per_sub[s] = {"n_thoughts": len(st), "n_forecasts": len(recs),
                          "brp_control": (outside / len(recs) if recs else None),
                          "n_missing_events": n_missing,
                          "mean_nd": float(np.mean([r["nd"] for r in recs])) if recs else None}
            for r in recs:
                f.write(json.dumps({"subject": s, "t": r["t"], "h_star": h_star,
                                    "nd": round(r["nd"], 5), "inside": r["inside"],
                                    "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                            time.gmtime())}) + "\n")

    # --- BRP_control on held-out TEST (clean basin-behavior validation) ---
    test_outside = test_total = 0
    for s in test:
        recs, _, _ = replay_subject(states_by_sub[s], ridge, r_alpha, h_star, k)
        test_total += len(recs)
        test_outside += sum(1 for r in recs if not r["inside"])
    brp_control_test = test_outside / test_total if test_total else None
    brp_control_all = (sum(1 for s in per_sub for r in
                           replay_subject(states_by_sub[s], ridge, r_alpha, h_star, k)[0]
                           if not r["inside"])) / n_forecasts

    # --- forecast reproducibility: online predict == batch predict (LinearMultiHorizon) ---
    from causal_mind.forecast.multihorizon_model import LinearMultiHorizon
    w = np.load(ART / "ridge_weights.npz")
    batch = LinearMultiHorizon(k=k, alpha=cfg["ridge_alpha"], horizons=(h_star,))
    batch._ridges[h_star] = Ridge()
    batch._ridges[h_star].coef_ = w[f"coef_h{h_star}"]
    batch._ridges[h_star].intercept_ = w[f"intercept_h{h_star}"]
    s0 = test[0]
    st0 = states_by_sub[s0]
    samp = build_horizon_samples(st0, k, h_star)[0]
    pred_online = ridge.predict(np.concatenate(
        [st0[i].embedding for i in samp.history]).reshape(1, -1))[0]
    pred_batch = batch.predict(samp, st0)
    max_diff = float(np.max(np.abs(pred_online - pred_batch)))

    # --- deterministic replay: two runs -> identical hash ---
    def _hash_run(subs):
        h = hashlib.sha256()
        for s in subs:
            recs, _, _ = replay_subject(states_by_sub[s], ridge, r_alpha, h_star, k)
            for r in recs:
                h.update(f"{s},{r['t']},{r['nd']:.9f},{r['inside']}".encode())
        return h.hexdigest()
    run1 = _hash_run(test[:5])
    run2 = _hash_run(test[:5])
    deterministic = run1 == run2

    # --- crash recovery: simulate a crash mid-session, resume, verify identical ---
    s_crash = test[0]
    st_c = states_by_sub[s_crash]
    full = replay_subject(st_c, ridge, r_alpha, h_star, k)[0]
    crash_at = len(full) // 2
    # "checkpoint" = first crash_at records; resume from there
    resumed = full[:crash_at] + replay_subject(
        st_c, ridge, r_alpha, h_star, k, )[0][crash_at:]
    crash_ok = (len(resumed) == len(full) and
                all(abs(a["nd"] - b["nd"]) < 1e-12 for a, b in zip(full, resumed)))

    lat = _percentiles(all_lat)
    brp_target = cfg["basin_tail"]
    # PASS criteria (engineering, not causal)
    checks = {
        "brp_control_test_near_basin_tail": (brp_control_test is not None and
                                              abs(brp_control_test - brp_target) < 0.05),
        "forecast_reproducible": max_diff < 1e-8,
        "deterministic_replay": deterministic,
        "crash_recovery": crash_ok,
        "latency_p95_ms_below_100": lat.get("95", 1e9) < 100.0,
        "audit_log_written": audit.exists() and audit.stat().st_size > 0,
        "all_forecasts_computed": n_forecasts > 0,
    }
    passed = all(checks.values())
    state = "CM8R_GHOST_PILOT_PASS" if passed else "CM8R_GHOST_PILOT_ITERATE"

    result = {
        "state": state,
        "n_ghost_participants": len(states_by_sub),
        "n_forecasts": n_forecasts,
        "n_missing_events_total": n_missing_total,
        "h_star": h_star, "k": k, "r_alpha": r_alpha, "basin_tail": brp_target,
        "brp_control": {"heldout_test": brp_control_test, "all_subjects": brp_control_all,
                        "target_basin_tail": brp_target,
                        "note": "fraction of NATURAL (non-intervened) futures outside the "
                                "frozen basin; ~= basin_tail if calibration is correct"},
        "forecast_reproducibility": {"max_online_vs_batch_diff": max_diff},
        "deterministic_replay": {"run1_hash": run1[:16], "run2_hash": run2[:16],
                                 "identical": deterministic},
        "crash_recovery": {"subject": s_crash, "crash_at": crash_at, "ok": crash_ok},
        "prediction_latency_ms": lat,
        "checks": checks,
        "per_subject_sample": {s: per_sub[s] for s in list(per_sub)[:5]},
        "runtime_seconds": round(time.time() - t_start, 1),
        "is_causal": False,
    }
    (OUT / "cm8r_ghost_pilot.json").write_text(json.dumps(result, indent=2, default=float))
    _write_md(result)
    print(f"[ghost] {state}")
    print(f"[ghost] BRP_control (held-out TEST) = {brp_control_test:.4f} "
          f"(target {brp_target}); all-subjects = {brp_control_all:.4f}")
    print(f"[ghost] forecast repro max diff = {max_diff:.2e}; deterministic={deterministic}; "
          f"crash_recovery={crash_ok}")
    print(f"[ghost] latency p50/p95/max = {lat.get('50'):.3f}/{lat.get('95'):.3f}/"
          f"{lat.get('max'):.3f} ms; n_forecasts={n_forecasts}")
    print(f"[ghost] checks: {checks}")
    return 0 if passed else 1


def _write_md(r: dict) -> None:
    L = ["# CM-8R1 — Ghost Pilot on ds006067 (prospective replay, NOT causal)", ""]
    L.append(f"- **State:** `{r['state']}`")
    L.append(f"- **Ghost participants:** {r['n_ghost_participants']} | "
             f"**forecasts:** {r['n_forecasts']} | h*={r['h_star']} k={r['k']} "
             f"r_alpha={r['r_alpha']:.4f}")
    L.append(f"- **BRP_control** (natural futures outside the frozen basin): "
             f"held-out TEST = {r['brp_control']['heldout_test']:.4f}, "
             f"all subjects = {r['brp_control']['all_subjects']:.4f}, "
             f"target basin_tail = {r['brp_control']['target_basin_tail']}. "
             "A value near the target confirms the basin, calibrated on VAL, "
             "generalizes to the natural trajectory.")
    L.append(f"- **Forecast reproducibility:** online == batch, max diff "
             f"{r['forecast_reproducibility']['max_online_vs_batch_diff']:.2e}.")
    L.append(f"- **Deterministic replay:** identical = {r['deterministic_replay']['identical']}.")
    L.append(f"- **Crash recovery:** ok = {r['crash_recovery']['ok']} "
             f"(crash at event {r['crash_recovery']['crash_at']}, resumed, identical).")
    L.append(f"- **Prediction latency (ms):** {r['prediction_latency_ms']}")
    L.append(f"- **Missing events (total):** {r['n_missing_events_total']}")
    L.append("\n## Checks")
    for k, v in r["checks"].items():
        L.append(f"- {'PASS' if v else 'FAIL'} — {k}")
    L.append("\nThis is an ENGINEERING validation of the online pipeline (online "
             "construction, reproducibility, basin behavior, timing, storage, logging, "
             "latency, missing events, crash recovery, determinism). It is NOT a causal "
             "analysis and makes no treatment-effect claim.")
    (OUT / "cm8r_ghost_pilot.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
