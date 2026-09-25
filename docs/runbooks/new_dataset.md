# New Dataset Runbook

**Status:** canonical · **Audience:** data role / anyone adding a dataset.

Adding a dataset means: acquire it lawfully, record its provenance, add a
read-only loader, and — if it feeds a scientific result — wire it into a
frozen split. Follow these steps in order.

## 1. Lawful acquisition + license

- Confirm you have the right to use the data (license, consent, terms). Record
  the license and citation in `docs/datasets/<name>.md`.
- Public datasets: cite by their own license (e.g. OSF `a56rm`, ds005494 CC0).
- If the data contains **human participant data**, it is class **C4** — it must
  not be committed before the human/ethics gate (see
  [data classification](../governance/data_classification.md)). Stop and route
  through the ethics process.

## 2. Provenance manifest

Create `data/manifests/<name>_manifest.yaml` (or `.json`) recording:

- source URL / DOI / version, acquisition date, acquirer
- checksums (SHA-256) of the raw files
- license + citation
- any preprocessing applied to produce derived data

Commit the **manifest**, not the raw data (raw data is gitignored; fetched to
the PVC).

## 3. Read-only loader

Add a loader under `src/causal_mind/data/` (layer L1, domain):

- Read-only over the raw data; no in-place mutation.
- Use `causal_mind.paths` for all paths (no hard-coded pod paths).
- Document the on-disk layout and the temporal-alignment convention in the
  module docstring (see `data/ds006067.py` as the reference).
- Add a loader test in `tests/` (see `tests/test_ds006067_loader.py`).

## 4. Derived data (if any)

If you normalize the raw data into derived features (e.g. thought events):

- Produce them with a script in `data/scripts/build_<name>.py`.
- Write derived data to `data/derived/<name>/` (gitignored if large).
- Record the build command + inputs in the manifest and in
  `registries/lineage.json`.

## 5. If it feeds a scientific result

- Add it to a **subject-disjoint** split (never random rows). If the split is
  part of a frozen protocol, this is a **protocol amendment** — see
  [protocol amendment runbook](protocol_amendment.md).
- Seal the split (see `data/manifests/cm2_split_seal.json` as the reference).
- Run the [new experiment runbook](new_experiment.md) for the result itself.

## 6. Verify + register

```bash
cm doctor                 # data dir present, loader importable
cm validate               # invariants + leakage + security
```

- Add the dataset to `registries/lineage.json` (inputs → outputs).
- Update `docs/datasets/<name>.md` and `docs/current_state.md`.

## Checklist

- [ ] License + citation recorded (`docs/datasets/<name>.md`)
- [ ] Provenance manifest with SHA-256 (`data/manifests/<name>_manifest.*`)
- [ ] Read-only loader under `src/causal_mind/data/` (uses `paths`)
- [ ] Loader test in `tests/`
- [ ] No human data committed (C4 guard clean)
- [ ] Lineage registered (`registries/lineage.json`)
- [ ] `cm doctor` + `cm validate` pass
