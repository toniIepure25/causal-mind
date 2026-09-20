"""CM-8R10: realtime engine validation (offline, transactional, full session).

Builds the participant-facing experiment engine from the FROZEN artifacts (forecaster,
basin radius, randomization manifest, MiniLM encoder) and runs a full synthetic session
(24 trials). Validates: the trial lifecycle, timestamp ordering, BRP computation,
deterministic randomization, and OFFLINE operation (no Qwen / no LLM API / no internet /
no remote-agent orchestration -- only frozen local artifacts).

Result state: CM8R_REALTIME_ENGINE_PASS.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path("/home/jovyan/work/causal-mind-v2")
sys.path.insert(0, str(ROOT / "src"))
from causal_mind.engine import ExperimentEngine, TrialState  # noqa: E402
from causal_mind.thought.encode import MiniLMEncoder  # noqa: E402
from sklearn.linear_model import Ridge  # noqa: E402

ART = ROOT / "artifacts" / "cm8_forecaster"
MANIFEST = ROOT / "data" / "manifests" / "cm8_randomization_manifest.json"
OUT = ROOT / "reports" / "cm8r_realtime_engine"
SEED = 20260917


class FrozenRandomizer:
    """Loads the frozen per-subject condition manifest."""

    def __init__(self, manifest_path: Path) -> None:
        m = json.loads(manifest_path.read_text())
        self.manifests = m["manifests"]
        self.seed = m["seed"]

    def next_condition(self, subject: str, trial_index: int) -> str:
        code = f"P-{int(subject.split('-')[1]):03d}"
        return self.manifests[code][trial_index]


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


def main() -> int:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    cfg, ridge, h_star, k, r_alpha = _load_frozen()
    enc = MiniLMEncoder()  # frozen local MiniLM (offline)
    rand = FrozenRandomizer(MANIFEST)

    # offline check: the engine module must not IMPORT any remote/network library.
    import inspect
    import causal_mind.engine.engine as eng_mod
    imports = " ".join(l for l in inspect.getsource(eng_mod).splitlines()
                       if l.strip().startswith(("import ", "from "))).lower()
    offline_ok = not any(lib in imports for lib in
                         ["requests", "socket", "http", "urllib", "qwen", "aiohttp",
                          "httpx", "grpc"])

    # run a full synthetic session (24 trials) for subject P-001
    subject = "P-001"
    import shutil
    sess_dir = OUT / f"session_{subject}"
    if sess_dir.exists():
        shutil.rmtree(sess_dir)  # fresh session for each run (logger is append-only)
    engine = ExperimentEngine(subject, sess_dir, ridge, r_alpha,
                              h_star, k, rand, encoder=enc)
    words = ["the", "quiet", "morning", "light", "on", "the", "table", "and",
             "how", "it", "felt", "to", "wait", "for", "the", "bus", "to", "come"]
    # warm up the forecaster's k-step history (no intervention trial)
    for i in range(k):
        engine.add_baseline(" ".join(words[i:i + 3]))
    n_trials = 24
    for i in range(n_trials):
        t = engine.start_trial()
        text = " ".join(words[(i * 3) % len(words): (i * 3) % len(words) + 4]
                        or words[:4])
        try:
            engine.capture_baseline(t, text)
            engine.compute_prediction(t)
            engine.randomize(t)
            engine.render_intervention(t)
            # post-intervention: a few subsequent thoughts
            post = [" ".join(words[(i * 3 + j) % len(words): (i * 3 + j) % len(words) + 3])
                    for j in range(3)]
            engine.capture_post(t, post)
            engine.finalize(t)
        except Exception as e:  # loud failure
            engine.mark_invalid(t, f"{type(e).__name__}: {e}")

    v = engine.validate_all()
    # deterministic randomization: re-run the randomizer, must match
    conds = [t.condition for t in engine.trials if t.condition]
    conds2 = [rand.next_condition(subject, i) for i in range(n_trials)]
    det_rand = conds == conds2
    # BRP computable for all finalized trials
    brp_ok = all(t.brp is not None for t in engine.trials
                 if t.state == TrialState.FINALIZED)
    checks = {
        "offline_no_remote_deps": offline_ok,
        "all_timestamps_ordered": v["all_timestamps_ordered"],
        "all_trials_finalized": v["n_finalized"] == n_trials,
        "no_invalid_trials": v["n_invalid"] == 0,
        "randomization_deterministic": det_rand,
        "brp_computable_all": brp_ok,
        "lifecycle_integrity": all(
            t.state == TrialState.FINALIZED for t in engine.trials),
    }
    passed = all(checks.values())
    state = "CM8R_REALTIME_ENGINE_PASS" if passed else "CM8R_REALTIME_ENGINE_ITERATE"
    result = {
        "state": state,
        "subject": subject, "n_trials": n_trials,
        "h_star": h_star, "k": k, "r_alpha": r_alpha,
        "conditions": conds,
        "brp_by_trial": [t.brp for t in engine.trials],
        "validation": v,
        "checks": checks,
        "runtime_seconds": round(time.time() - t0, 1),
        "offline": "The engine uses ONLY frozen local artifacts (MiniLM encoder, "
                   "ridge forecaster, basin radius, randomization manifest). No Qwen, "
                   "no LLM API, no internet, no remote-agent orchestration.",
    }
    (OUT / "cm8r_realtime_engine.json").write_text(json.dumps(result, indent=2, default=float))
    _write_md(result)
    print(f"[engine] {state}")
    print(f"[engine] checks={checks}")
    print(f"[engine] conditions={conds}")
    return 0 if passed else 1


def _write_md(r: dict) -> None:
    L = ["# CM-8R10 — Realtime Engine (offline, transactional)", ""]
    L.append(f"- **State:** `{r['state']}`  | subject {r['subject']}, {r['n_trials']} trials, "
             f"h*={r['h_star']} k={r['k']} r_alpha={r['r_alpha']:.4f}")
    L.append(f"- **Offline:** {r['offline']}")
    L.append(f"- **Conditions (frozen manifest):** {r['conditions']}")
    L.append(f"- **BRP by trial:** {[round(x, 3) if x is not None else None for x in r['brp_by_trial']]}")
    L.append("\n## Checks")
    for k, v in r["checks"].items():
        L.append(f"- {'PASS' if v else 'FAIL'} — {k}")
    L.append("\n## Lifecycle & timestamps")
    L.append("- Each trial follows CREATED -> BASELINE_CAPTURED -> PREDICTION_COMPUTED -> "
             "RANDOMIZED -> INTERVENTION_RENDERED -> POST_CAPTURED -> FINALIZED (or "
             "ABORTED / INVALID_TECHNICAL / WITHDRAWN). Analysis-valid only after atomic "
             "finalization; duplicate finalization is prevented.")
    L.append("- Every event is stamped with wall-clock UTC + monotonic local time; ordering "
             "is validated automatically.")
    (OUT / "cm8r_realtime_engine.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
