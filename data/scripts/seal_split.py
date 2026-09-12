"""Reseal the CM-2 split over the OSF eligible cohort (Step 6, protocol amendment).

Runs BEFORE any decisive evaluation. Computes the deterministic
subject-disjoint split over the 118 OSF sentence-level subjects, seals it
(SHA-256 persisted to data/manifests/cm2_split_seal.json), and prints the hash
for the protocol amendment record.
"""
from __future__ import annotations

from causal_mind.data import osf_a56rm
from causal_mind.eval import protocol

SEED = 20260911


def main() -> None:
    subs = osf_a56rm.all_subjects()
    split = protocol.subject_disjoint_split(subs, seed=SEED)
    seal = protocol.seal_split(split, seed=SEED, n_subjects=len(subs))
    print(f"eligible cohort: {len(subs)} subjects (OSF sentence-level)")
    print(f"split train/val/test = {len(split.train)}/{len(split.val)}/{len(split.test)}")
    print(f"SEAL: {seal}")
    print(f"seal path: {protocol.SEAL_PATH}")


if __name__ == "__main__":
    main()
