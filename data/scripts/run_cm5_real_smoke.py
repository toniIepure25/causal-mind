"""CM-5 real-data minimal smoke (N=2: sub-001, sub-005).

NOT a scientific result. Validates end-to-end that the frozen HRF-safe
pipeline runs on real fMRIPrep MNI BOLD: load -> HRF-safe windows ->
neural features -> subject-disjoint M2 vs M4 -> IncrementalNeuralGain.
"""
from __future__ import annotations
import json, sys
import numpy as np
import nibabel as nib
import pandas as pd

from causal_mind.neural.prospective_window import (
    windows_for_subject, DEFAULT_BUFFER_S, DEFAULT_WINDOW_S)
from causal_mind.neural.fusion import FusionModel, score_cosine, incremental_neural_gain

NEURAL = "/home/jovyan/work/causal-mind-v2/data/neural"
GIT = "/home/jovyan/work/ds006067_git"
SUBS = ["sub-001", "sub-005"]
TR = 1.5
MAXVOX = 4000


def load_subject(sub: str):
    bold_path = f"{NEURAL}/derivatives/{sub}/func/{sub}_task-thinkaloud_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"
    mask_path = f"{NEURAL}/derivatives/{sub}/func/{sub}_task-thinkaloud_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz"
    ev_path = f"{GIT}/{sub}/func/{sub}_task-thinkaloud_events.tsv"
    cf_path = f"{NEURAL}/derivatives/{sub}/func/{sub}_task-thinkaloud_desc-confounds_timeseries.tsv"
    img = nib.load(bold_path)
    data = img.get_fdata(dtype=np.float32)
    bold = np.ascontiguousarray(data.transpose(3, 0, 1, 2))
    mask = nib.load(mask_path).get_fdata(dtype=np.float32) > 0.5
    vox = np.argwhere(mask)
    if len(vox) > MAXVOX:
        rng = np.random.default_rng(0)
        keep = rng.choice(len(vox), size=MAXVOX, replace=False)
        vox = vox[keep]
    feats = bold[:, vox[:, 0], vox[:, 1], vox[:, 2]]
    feats = feats - feats.mean(axis=0, keepdims=True)
    ev = pd.read_csv(ev_path, sep="\t")
    cf = pd.read_csv(cf_path, sep="\t")
    return feats, ev, cf, bold.shape[0]


def behavior_vec(transcript: str, dim: int = 8) -> np.ndarray:
    words = transcript.lower().split()
    v = np.zeros(dim)
    v[0] = len(words) / 20.0
    v[1] = len(transcript) / 200.0
    for w in words:
        v[2 + (hash(w) % (dim - 2))] += 1.0
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def main() -> None:
    samples = []
    for sub in SUBS:
        feats, ev, cf, n_vols = load_subject(sub)
        onsets = ev["onset"].to_numpy(dtype=float)
        wins = windows_for_subject(feats, TR, onsets, DEFAULT_BUFFER_S, DEFAULT_WINDOW_S)
        beh = np.stack([behavior_vec(t) for t in ev["transcript"]])
        gcol = cf["global_signal"].to_numpy(dtype=np.float32)
        gcol = gcol - gcol.mean()
        samples.append(dict(sub=sub, feats=feats, wins=wins, beh=beh, g=gcol, n_vols=n_vols))
        print(f"{sub}: n_vols={n_vols} n_vox={feats.shape[1]} n_events={len(ev)} "
              f"valid_windows={len(wins)} avg_vol_in_win={np.mean([w.n_volumes for w in wins]):.1f}",
              file=sys.stderr)

    rows = []
    for s in samples:
        for k, w in enumerate(s["wins"]):
            if k >= len(s["beh"]):
                break
            neural = s["feats"][w.volume_indices].mean(axis=0)
            rows.append(dict(sub=s["sub"], neural=neural, beh=s["beh"][k],
                             g=s["g"][w.volume_indices].mean()))
    print(f"total event-rows: {len(rows)}", file=sys.stderr)

    neural = np.stack([r["neural"] for r in rows])
    beh = np.stack([r["beh"] for r in rows])
    g = np.stack([r["g"] for r in rows]).reshape(-1, 1)
    subs = [r["sub"] for r in rows]
    target = beh.copy()

    tr_subs = ["sub-001"]; te_subs = ["sub-005"]
    def sel(subs_):
        m = np.isin(subs, subs_)
        return neural[m], beh[m], g[m], target[m]

    def fit_score(use_neural):
        Xn, Xb, Xg, Y = sel(tr_subs)
        m = FusionModel(alpha=10.0, use_neural=use_neural, use_nuisance=True)
        m.fit(Xb, Y, Xn, Xg)
        Tn, Tb, Tg, Ty = sel(te_subs)
        pred = m.predict(Tb, Tn, Tg)
        return score_cosine(pred, Ty)

    s_m2 = fit_score(False)
    s_m4 = fit_score(True)
    gain = incremental_neural_gain(s_m4, s_m2)
    result = {
        "mode": "real_data_minimal_smoke",
        "subjects": SUBS,
        "n_event_rows": len(rows),
        "m2_behavior_nuisance": round(s_m2, 4),
        "m4_behavior_nuisance_neural": round(s_m4, 4),
        "incremental_neural_gain": round(gain, 4),
        "note": "N=2 smoke; NOT a scientific result. Validates the frozen HRF-safe pipeline runs end-to-end on real fMRIPrep MNI BOLD.",
    }
    print(json.dumps(result, indent=2))
    with open("/home/jovyan/work/causal-mind-v2/reports/cm5_real_smoke.json", "w") as f:
        json.dump(result, f, indent=2)
    print("REAL-DATA MINIMAL SMOKE COMPLETE", file=sys.stderr)


if __name__ == "__main__":
    main()