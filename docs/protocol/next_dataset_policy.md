# CM-LAB Next-Dataset Policy (CM-LAB §73)

Policy for adding a NEW dataset to the CAUSAL MIND predictive-dynamics program. A new dataset
is admitted only if it passes the gates below; otherwise it is recorded as
`INCOMPATIBLE_DATASET` (with the reason) and NOT used to modify any existing claim.

## Admission gates (all must pass)

1. **Sequential free-text per subject.** The dataset must contain sequential, well-filled
   free-text thought entries per subject (not single ratings, not clinical notes, not event logs).
2. **Minimum size.** >= 20 subjects, each with >= 20 well-filled sequential entries (the CM-8
   confirmatory minimum; smaller datasets cannot support the subject-disjoint split + inference).
3. **Language + representation compatibility.** The text must be in the language of the frozen
   MiniLM representation (English) OR a new representation must be frozen and a NEW claim
   registered (per §74 multilingual policy). The frozen English MiniLM (384-d) is the reference.
4. **Temporal ordering.** Entries must have a reliable temporal order (timestamps or sequence
   index) so that strictly-prospective targets (CM-3) are well-defined.
5. **Subject identity.** Subjects must be identifiable and disjoint (no subject in >1 split).
6. **Provenance + checksums.** A manifest with source, license, checksums, and acquisition date.
7. **No human-data boundary violation.** If the dataset is a NEW human dataset, it is gated on
   ethics approval and the CM-8P pilot authorization (no pre-ethics collection).

## On admission

- Register the dataset in `data/manifests/` (manifest + checksums) and the data lineage registry.
- Create a NEW subject-disjoint split (seed recorded) and a NEW protocol seal.
- Register a NEW claim (C-1xx) for any result on the new dataset; do NOT modify C-001..C-012 or
  C-101..C-107.
- Run the leakage scanner (`cm_leakage_scan.py`) on any new analysis script.

## On rejection

- Record the dataset as `INCOMPATIBLE_DATASET` with the specific gate(s) failed and the reason
  (as was done for van Halem "Daily event" 0070: 8.2% fill rate, ~4 entries/subject, Dutch text).
- Do NOT use the rejected dataset to modify any existing claim.

## Multilingual extension (§74)

A non-English dataset requires: (a) a frozen multilingual representation (e.g., a multilingual
sentence transformer) with its own protocol seal; (b) a NEW claim for any cross-lingual result;
(c) an explicit statement that the frozen English MiniLM result (C-101..C-107) is NOT extended to
the new language without a dedicated replication. Cross-lingual transfer is a NEW hypothesis, not
an assumption.

## Cross-dataset standardization (§75)

When comparing results across datasets, standardize: (a) the metric (cosine on L2-normalized
embeddings is the reference); (b) the split protocol (subject-disjoint, same seed policy);
(c) the baseline set (the frozen baselines B0-B4); (d) the inference (subject-level, the same
null family). Differences in representation, language, or entry density are reported as
covariates, not averaged away.

## Meta-analysis (§76)

The meta-analysis framework (`data/scripts/cm_meta_analysis.py`) aggregates the per-dataset,
per-representation, per-horizon effect sizes (model gain over the strongest baseline) into a
random-effects estimate. It is a FRAMEWORK: it consumes the per-workstream report JSONs and
produces a pooled estimate + heterogeneity (I^2). It does NOT pool across incompatible datasets
or across representations without an explicit covariate.

**No CM-8 change. No human data. No result shopping.**
