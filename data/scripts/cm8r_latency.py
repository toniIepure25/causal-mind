"""CM-8R11: latency benchmark for the participant-facing engine.

Measures per-stage latency (thought capture, encoding, prediction, randomization,
intervention render, post-capture, BRP) and the total trial time, reporting
p50/p90/p95/p99/max. Runs warm and cold (first trial after model load).

The engine is fully offline (frozen local artifacts); latency is local CPU/GPU only.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path("/home/jovyan/work/causal-mind-v2")
sys.path.insert(0, str(ROOT / "src"))
from causal_mind.engine import ExperimentEngine  # noqa: E402
from causal_mind.thought.encode import MiniLMEncoder  # noqa: E402
from sklearn.linear_model import Ridge  # noqa: E402

ART = ROOT / "artifacts" / "cm8_forecaster"
MANIFEST = ROOT / "data" / "manifests" / "cm8_randomization_manifest.json"
OUT = ROOT / "reports" / "cm8r_latency"
SEED = 20260917


class FrozenRandomizer:
    def __init__(self, p: Path) -> None:
        m = json.loads(p.read_text())
        self.manifests = m["manifests"]

    def next_condition(self, subject: str, i: int) -> str:
        code = f"P-{int(subject.split('-')[1]):03d}"
        return self.manifests[code][i]


def _load_frozen():
    cfg = json.loads((ART / "config.json").read_text())
    w = np.load(ART / "ridge_weights.npz")
    h_star = cfg["primary_horizon_h_star"]
    k = cfg["k_history_depth"]
    r_alpha = cfg["r_alpha_by_horizon"][f"h{h_star}"]
    ridge = Ridge()
    ridge.coef_ = w[f"coef_h{h_star}"]
    ridge.intercept_ = w[f"intercept_h{h_star}"]
    return h_star, k, r_alpha


def _percentile(arr) -> dict:
    a = np.array(arr)
    return {f"p{p}": float(np.percentile(a, p)) for p in (50, 90, 95, 99)} | {"max": float(a.max())}


def main() -> int:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    h_star, k, r_alpha = _load_frozen()
    enc = MiniLMEncoder()
    rand = FrozenRandomizer(MANIFEST)
    subject = "P-001"
    import shutil
    sess = OUT / "session_lat"
    if sess.exists():
        shutil.rmtree(sess)
    engine = ExperimentEngine(subject, sess, None, r_alpha, h_star, k, rand, encoder=enc)
    # the engine's compute_prediction uses self.forecaster; set it
    cfg = json.loads((ART / "config.json").read_text())
    w = np.load(ART / "ridge_weights.npz")
    ridge = Ridge()
    ridge.coef_ = w[f"coef_h{h_star}"]
    ridge.intercept_ = w[f"intercept_h{h_star}"]
    engine.forecaster = ridge

    words = ["the", "quiet", "morning", "light", "on", "the", "table", "and",
             "how", "it", "felt", "to", "wait", "for", "the", "bus", "to", "come"]
    for i in range(k):
        engine.add_baseline(" ".join(words[i:i + 3]))

    stages = {s: [] for s in ("encode", "predict", "randomize", "render",
                              "post_encode", "brp", "total")}
    n_trials = 24  # matches the frozen per-subject manifest length
    for i in range(n_trials):
        t = engine.start_trial()
        text = " ".join(words[(i * 3) % len(words): (i * 3) % len(words) + 4] or words[:4])
        t_total = time.perf_counter()

        ts = time.perf_counter()
        engine.capture_baseline(t, text)
        stages["encode"].append(time.perf_counter() - ts)

        ts = time.perf_counter()
        engine.compute_prediction(t)
        stages["predict"].append(time.perf_counter() - ts)

        ts = time.perf_counter()
        engine.randomize(t)
        stages["randomize"].append(time.perf_counter() - ts)

        ts = time.perf_counter()
        engine.render_intervention(t)
        stages["render"].append(time.perf_counter() - ts)

        ts = time.perf_counter()
        post = [" ".join(words[(i * 3 + j) % len(words): (i * 3 + j) % len(words) + 3])
                for j in range(3)]
        engine.capture_post(t, post)
        stages["post_encode"].append(time.perf_counter() - ts)

        ts = time.perf_counter()
        engine.finalize(t)
        stages["brp"].append(time.perf_counter() - ts)

        stages["total"].append(time.perf_counter() - t_total)

    result = {
        "n_trials": n_trials,
        "stage_latency_ms": {s: {kk: round(vv * 1000, 3) for kk, vv in _percentile(a).items()}
                             for s, a in stages.items()},
        "cold_first_trial_ms": {s: round(stages[s][0] * 1000, 3) for s in stages},
        "runtime_seconds": round(time.time() - t0, 1),
        "note": "Latency is LOCAL (frozen MiniLM encoder + ridge forecaster). The "
                "participant-facing critical path is encode + predict + render + BRP. "
                "No Qwen / no LLM API / no internet in the loop.",
    }
    (OUT / "cm8r_latency.json").write_text(json.dumps(result, indent=2, default=float))
    _write_md(result)
    print(f"[latency] total p95={result['stage_latency_ms']['total']['p95']:.1f}ms "
          f"max={result['stage_latency_ms']['total']['max']:.1f}ms")
    return 0


def _write_md(r: dict) -> None:
    L = ["# CM-8R11 — Latency Benchmark", ""]
    L.append(f"- {r['n_trials']} trials; local frozen artifacts (no Qwen / no internet).")
    L.append("\n## Per-stage latency (ms)")
    L.append("| stage | p50 | p90 | p95 | p99 | max |")
    L.append("| --- | --- | --- | --- | --- | --- |")
    for s, v in r["stage_latency_ms"].items():
        L.append(f"| {s} | {v['p50']} | {v['p90']} | {v['p95']} | {v['p99']} | {v['max']} |")
    L.append("\n## Cold (first trial after model load), ms")
    L.append("| stage | cold ms |")
    L.append("| --- | --- |")
    for s, v in r["cold_first_trial_ms"].items():
        L.append(f"| {s} | {v} |")
    L.append(f"\n{r['note']}")
    (OUT / "cm8r_latency.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
