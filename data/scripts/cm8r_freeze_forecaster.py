"""CM-8R3: freeze the participant-facing forecasting artifact.

Builds the EXACT participant-facing forecasting stack from the validated CM-3
components (LinearMultiHorizon + frozen MiniLM), fits on the CM-2 TRAIN split,
calibrates the basin radius on the CM-2 VAL split (held-out prediction-error
norms), and writes a cryptographic freeze manifest that lets a clean checkout
reproduce the exact participant-facing forecast.

Participant-facing stack (all frozen, no Qwen / no LLM / no internet):
  thought text
    -> frozen MiniLM embedding (all-MiniLM-L6-v2, 384-d, L2-normalized)
    -> history window [t-k+1 .. t]  (k = 3)
    -> LinearMultiHorizon (one Ridge per horizon h; alpha = 100)
    -> predicted T[t+h]
    -> PredictedFutureBasin (center = predicted, radius = r_alpha[h])

r_alpha[h] = (1 - basin_tail) quantile of the held-out prediction-error norms
||T[t+h] - pred|| on the VAL split (no test, no intervention data).
basin_tail = 0.10 (frozen). Primary horizon h* = 2 (frozen).

Architecture choice: the simple linear transition model (CM-3 primary), NOT a GRU
(CM-3 found linear >= GRU; simplest validated architecture is preferred).
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
from causal_mind.forecast.multihorizon_model import LinearMultiHorizon  # noqa: E402
from causal_mind.thought import encode, state_v1  # noqa: E402
from causal_mind.thought.multihorizon import build_horizon_samples      # noqa: E402

ART = ROOT / "artifacts" / "cm8_forecaster"
MANIFEST = ROOT / "artifacts" / "cm8_forecasting_freeze_manifest.json"

SEED = 20260911          # CM-2 split seed (frozen)
K = 3                    # history depth (CM-3 K_DEFAULT)
ALPHA = 100.0            # Ridge alpha (CM-3)
HORIZONS = (1, 2, 3, 4, 5, 6, 8, 10)
H_STAR = 2               # frozen primary horizon
BASIN_TAIL = 0.10        # frozen basin tail (BRP_control target)
ENCODER = "all-MiniLM-L6-v2"
ENCODER_DIM = 384


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes())


def main() -> int:
    t0 = time.time()
    ART.mkdir(parents=True, exist_ok=True)
    subs = osf_a56rm.all_subjects()
    enc = encode.MiniLMEncoder()
    states_by_sub: dict[str, list] = {}
    for s in subs:
        st = state_v1.states_from_events(s, osf_a56rm.load_thought_events(s))
        # use cached embeddings (deterministic function of transcript + frozen MiniLM)
        texts = [x.transcript for x in st]
        arr = encode.encode_subject_cached(enc, s, texts)
        for x, v in zip(st, arr, strict=True):
            x.embedding = v
        states_by_sub[s] = st
    split = protocol.subject_disjoint_split(subs, seed=SEED)
    assert protocol.verify_seal(split, SEED, len(subs)), "CM-2 SEAL MISMATCH"
    train, val, test = list(split.train), list(split.val), list(split.test)
    print(f"[freeze] {len(subs)} subjects; split {len(train)}/{len(val)}/{len(test)}; seal ok")

    # --- fit the linear multi-horizon forecaster on TRAIN only ---
    samples_by_h: dict[int, list] = {h: [] for h in HORIZONS}
    for s in train:
        for h in HORIZONS:
            samples_by_h[h].extend(build_horizon_samples(states_by_sub[s], K, h))
    model = LinearMultiHorizon(k=K, alpha=ALPHA, horizons=HORIZONS)
    model.fit(samples_by_h, states_by_sub)
    print(f"[freeze] fitted LinearMultiHorizon k={K} alpha={ALPHA} "
          f"horizons={HORIZONS} params={model.param_count()}")

    # --- calibrate the basin radius on VAL (held-out prediction-error norms) ---
    error_norms_by_h: dict[int, list[float]] = {h: [] for h in HORIZONS}
    for s in val:
        st = states_by_sub[s]
        for h in HORIZONS:
            ridge = model._ridges[h]
            for samp in build_horizon_samples(st, K, h):
                x = np.concatenate([st[i].embedding for i in samp.history])
                pred = ridge.predict(x.reshape(1, -1))[0]
                err = float(np.linalg.norm(pred - st[samp.target_index].embedding))
                error_norms_by_h[h].append(err)
    r_alpha_by_h = {h: float(np.quantile(error_norms_by_h[h], 1.0 - BASIN_TAIL))
                    for h in HORIZONS}
    n_err_by_h = {h: len(error_norms_by_h[h]) for h in HORIZONS}
    print(f"[freeze] r_alpha (basin_tail={BASIN_TAIL}): "
          + ", ".join(f"h={h}:{r_alpha_by_h[h]:.3f}" for h in HORIZONS))

    # --- save the forecaster weights (per-horizon Ridge) + config + error norms ---
    # Weights are a large generated artifact (3.5M params); stored as a compact .npz
    # and gitignored. They are DETERMINISTICALLY reproducible by re-running this
    # script with the frozen code + data, and their SHA is recorded in the manifest.
    weight_arrays = {}
    for h in HORIZONS:
        weight_arrays[f"coef_h{h}"] = model._ridges[h].coef_.astype(np.float64)
        weight_arrays[f"intercept_h{h}"] = model._ridges[h].intercept_.astype(np.float64)
    np.savez(ART / "ridge_weights.npz", **weight_arrays)
    err_npz = {f"err_h{h}": np.asarray(error_norms_by_h[h]) for h in HORIZONS}
    np.savez_compressed(ART / "heldout_error_norms.npz", **err_npz)

    config = {
        "architecture": "LinearMultiHorizon (one Ridge per horizon)",
        "k_history_depth": K,
        "ridge_alpha": ALPHA,
        "horizons": list(HORIZONS),
        "primary_horizon_h_star": H_STAR,
        "basin_tail": BASIN_TAIL,
        "r_alpha_by_horizon": {f"h{h}": r_alpha_by_h[h] for h in HORIZONS},
        "n_heldout_error_norms_by_horizon": {f"h{h}": n_err_by_h[h] for h in HORIZONS},
        "semantic_encoder": ENCODER,
        "encoder_dim": ENCODER_DIM,
        "encoder_normalize": True,
        "preprocessing": "none beyond frozen MiniLM L2-normalized embeddings",
        "scaler": "none (Ridge on raw L2-normalized embeddings)",
        "dimensional_transform": "concatenate last k embeddings (k*dim -> dim Ridge)",
        "split_seed": SEED,
        "split": {"train": len(train), "val": len(val), "test": len(test)},
        "fit_subjects": train,
        "calibration_subjects": val,
        "inference": {
            "input": "history window [t-k+1..t] of L2-normalized MiniLM embeddings",
            "output": "predicted T[t+h] embedding (dim)",
            "basin": "PredictedFutureBasin(center=pred, radius=r_alpha[h])",
            "brp": "fraction of post-intervention states outside the basin at h*",
        },
    }
    (ART / "config.json").write_text(json.dumps(config, indent=2))

    # --- reproducibility check: reload weights from disk, verify a prediction matches ---
    w = np.load(ART / "ridge_weights.npz")
    s0 = test[0]
    st0 = states_by_sub[s0]
    samp = build_horizon_samples(st0, K, H_STAR)[0]
    x = np.concatenate([st0[i].embedding for i in samp.history])
    pred_live = model._ridges[H_STAR].predict(x.reshape(1, -1))[0]
    from sklearn.linear_model import Ridge
    ridge_reload = Ridge()
    ridge_reload.coef_ = w[f"coef_h{H_STAR}"]
    ridge_reload.intercept_ = w[f"intercept_h{H_STAR}"]
    pred_reload = ridge_reload.predict(x.reshape(1, -1))[0]
    max_diff = float(np.max(np.abs(pred_live - pred_reload)))
    print(f"[freeze] reload check: max |pred_live - pred_reload| = {max_diff:.2e}")
    assert max_diff < 1e-8, "reloaded weights do not reproduce the live prediction"

    # --- code SHAs (the participant-facing code paths) ---
    code_files = {
        "src/causal_mind/forecast/multihorizon_model.py": "forecaster",
        "src/causal_mind/thought/encode.py": "semantic encoder (frozen MiniLM)",
        "src/causal_mind/thought/state_v1.py": "thought-state construction",
        "src/causal_mind/thought/multihorizon.py": "history-window sample construction",
        "src/causal_mind/data/osf_a56rm.py": "thought-event loader",
        "src/causal_mind/eval/protocol.py": "split + seal + metrics",
        "src/causal_mind/causal/predicted_basin.py": "predicted basin + BRP",
    }
    code = {rel: {"sha256": sha256_file(ROOT / rel), "role": role}
            for rel, role in code_files.items()}

    manifest = {
        "experiment": "CM-8 participant-facing forecasting artifact (FROZEN)",
        "frozen_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "architecture": "LinearMultiHorizon (linear transition model; CM-3 primary; "
                        "linear >= GRU per CM-3, so no GRU)",
        "reproducibility": "A clean checkout with the frozen code SHAs below + the "
                           "frozen MiniLM + the CM-2 split reproduces these exact "
                           "weights (Ridge is deterministic). Embeddings are a "
                           "deterministic function of (transcript, frozen MiniLM).",
        "artifacts": {
            "ridge_weights.npz": sha256_file(ART / "ridge_weights.npz"),
            "heldout_error_norms.npz": sha256_file(ART / "heldout_error_norms.npz"),
            "config.json": sha256_file(ART / "config.json"),
        },
        "artifact_storage": "ridge_weights.npz + heldout_error_norms.npz are large "
                            "generated artifacts (gitignored); deterministically "
                            "reproduced by running cm8r_freeze_forecaster.py with the "
                            "frozen code SHAs + data. SHAs above are the integrity check.",
        "config": config,
        "code": code,
        "semantic_encoder": {
            "name": ENCODER,
            "note": "pretrained, FROZEN (no fitting); embeddings L2-normalized",
            "cache_sha256_note": "embedding cache is a deterministic function of the "
                                 "frozen encoder + transcripts",
        },
        "reload_check_max_diff": max_diff,
        "runtime_seconds": round(time.time() - t0, 1),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    print(f"[freeze] wrote {MANIFEST}")
    print(f"[freeze] done in {time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
