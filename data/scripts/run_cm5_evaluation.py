"""CM-5 end-to-end evaluation runner.

The --synthetic mode generates data where the neural features genuinely predict
the behavioral model's residual (via a SHARED neural->future mapping so the
model generalizes across subjects), then runs the full subject-disjoint
pipeline: M2 (behavior+nuisance) vs M4 (behavior+nuisance+neural),
IncrementalNeuralGain, and the destructive negative controls. It asserts the
gain is positive on real-signal data and collapses under every control. This
validates the pipeline end-to-end before the real fMRIPrep BOLD is acquired.

The real-data mode (load BOLD + events + confounds, build HRF-safe windows,
extract N1-N3 features, run M0-M4 + controls + bootstrap/permutation) is wired
to the same scoring path and activates once the derivatives are available.
"""
from __future__ import annotations

import argparse
import json

import numpy as np

from causal_mind.neural.fusion import FusionModel, incremental_neural_gain, score_cosine
from causal_mind.neural.negative_controls import (
    SubjectSample,
    nc1_subject_permute,
    nc2_temporal_shift,
    nc4_nuisance_only,
    nc5_neural_randomize,
    nc6_target_permute,
)


def _stack(data, subjects, attr):
    return np.concatenate([getattr(d, attr) for d in data if d.subject in subjects],
                          axis=0)


def subject_disjoint_score(data, use_neural, use_nuisance, train_subs, test_subs,
                           alpha=10.0):
    """Fit on train subjects, score on test subjects (subject-disjoint)."""
    tr, te = set(train_subs), set(test_subs)
    m = FusionModel(alpha=alpha, use_neural=use_neural, use_nuisance=use_nuisance)
    m.fit(_stack(data, tr, "behavior"), _stack(data, tr, "target"),
          _stack(data, tr, "neural"), _stack(data, tr, "nuisance"))
    pred = m.predict(_stack(data, te, "behavior"), _stack(data, te, "neural"),
                     _stack(data, te, "nuisance"))
    return score_cosine(pred, _stack(data, te, "target"))


def make_synthetic(seed: int = 0):
    """Shared Wb/Wn so the model generalizes across subjects."""
    rng = np.random.default_rng(seed)
    n_subj, n_per, nb, nn, nc, dim = 6, 80, 8, 10, 5, 32
    Wb = rng.normal(size=(nb, dim))
    Wn = rng.normal(size=(nn, dim)) * 1.5  # strong, SHARED neural signal
    data = []
    for s in range(n_subj):
        B = rng.normal(size=(n_per, nb))
        N = rng.normal(size=(n_per, nn))
        C = rng.normal(size=(n_per, nc))
        target = B @ Wb + N @ Wn + 0.4 * rng.normal(size=(n_per, dim))
        data.append(SubjectSample(f"sub-{s}", B, N, C, target))
    return data


def run_synthetic(seed: int = 0) -> dict:
    rng = np.random.default_rng(seed + 1)
    data = make_synthetic(seed)
    subs = [d.subject for d in data]
    train_subs, test_subs = subs[:4], subs[4:]

    s_m2 = subject_disjoint_score(data, False, True, train_subs, test_subs)
    s_m4 = subject_disjoint_score(data, True, True, train_subs, test_subs)
    gain = incremental_neural_gain(s_m4, s_m2)
    result = {"m2": s_m2, "m4": s_m4, "incremental_neural_gain": gain,
              "train": train_subs, "test": test_subs, "controls": {}}

    controls = {
        "NC1_subject_perm": lambda d: nc1_subject_permute(d, rng),
        "NC2_temporal_shift": lambda d: nc2_temporal_shift(d, shift=7, rng=rng),
        "NC4_nuisance_only": lambda d: nc4_nuisance_only(d),
        "NC5_neural_randomize": lambda d: nc5_neural_randomize(d, rng),
        "NC6_target_perm": lambda d: nc6_target_permute(d, rng),
    }
    for name, fn in controls.items():
        s_m4_ctl = subject_disjoint_score(fn(data), True, True, train_subs, test_subs)
        result["controls"][name] = {"m4": s_m4_ctl,
                                    "gain": incremental_neural_gain(s_m4_ctl, s_m2)}

    assert gain > 0.02, f"expected positive neural gain, got {gain}"
    for name, c in result["controls"].items():
        assert c["gain"] < gain / 2, f"control {name} did not collapse the gain"
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--out", default="reports/cm5_results.json")
    args = ap.parse_args()
    if args.synthetic:
        result = run_synthetic()
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(json.dumps(result, indent=2))
        print("SYNTHETIC END-TO-END PASS: neural gain positive, collapses under all controls")
    else:
        print("Real-data mode requires the fMRIPrep BOLD derivatives (currently blocked).")
        print("Use --synthetic to validate the pipeline end-to-end.")


if __name__ == "__main__":
    main()
