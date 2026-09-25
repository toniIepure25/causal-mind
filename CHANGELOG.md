# Changelog

All notable changes to the Causal Mind repository. Format follows
[Keep a Changelog](https://keepachangelog.com/) and the project uses
[semantic versioning](docs/governance/versioning.md).

The **pre-human freeze** `cm8-prehuman-v1.0` (git `8a9d5dd`, 2026-09-20) is an
immutable historical release; everything below is post-freeze repository
professionalization and the CM-LAB scientific deep dive. Frozen scientific
artifacts are never modified — only added to and verified.

## [Unreleased] — CM-REPO professionalization

### Added
- Research CLI: `cm doctor`, `cm validate`, `cm claims verify`,
  `cm artifacts verify`, `cm security scan`, `cm demo`, `cm reproduce`
  (`src/causal_mind/cli_research.py`).
- Domain error taxonomy (`errors.py`), stable exit-code contract
  (`exit_codes.py`), traceable run IDs (`runid.py`), structured logging
  (`logging_setup.py`).
- Centralized scientific constants read from frozen configs (`constants.py`).
- Centralized path discovery; removed hard-coded pod paths (`paths.py`).
- Human-data guard with pre-commit hook + CI enforcement (`human_data_guard.py`,
  `scripts/hooks/pre-commit`, `scripts/install_hooks.sh`).
- Import-boundary test enforcing the layered architecture
  (`tests/test_import_boundaries.py`); broke the `eval<->forecast` cycle by moving
  `cosines` to `utils/metrics.py`.
- Architecture docs (`docs/architecture/`), governance docs
  (`docs/governance/`), runbooks (`docs/runbooks/`), `SECURITY.md`,
  `docs/glossary.md`, `docs/README.md` index, threat models, data classification,
  env-var registry, versioning + release process.

### Changed
- `README.md` rewritten as a professional entry point (state
  `CMLAB_SCIENTIFIC_DEEP_DIVE_COMPLETE`).
- `scripts/validate_project.sh` now runs the human-data guard.

### Removed
- Dead modules `src/causal_mind/evaluation/` (empty) and
  `src/causal_mind/forecasting/` (superseded B0-B5 stub; active ladder is
  `forecast/baselines.py`).

## [2026-09-24] — CM-LAB scientific deep dive complete

### Added
- 9 workstreams: cross-dataset replication, uncertainty, representation,
  personalization, dynamics, error prediction, oracle selective prediction,
  leakage scan, disaster recovery.
- Decisions: `CMXVAL_PARTIAL_REPLICATION`, `CMUNC_WEAK`, `CMREP_PARTIAL`,
  `CMPERS_NULL`, `CMDYN_LINEAR_PREDICTION_DOMINANT`, `CMERR_WEAKLY_PREDICTABLE`,
  `CMORACLE_SELECTIVE_ONLY`, `CMLEAK_PASS`, `CMLAB_DISASTER_RECOVERY_REPRODUCED`,
  `CM8_CONFIRMATORY_INTACT`.
- Claims C-102…C-107; C-101 revised.
- `data/scripts/cm_deep_dive_runner.py` (full + `--demo`), `cm_meta_analysis.py`,
  `cm_leakage_scan.py`, `cm8_no_drift.py`.
- `scripts/disaster_recovery.sh` (NFS-safe `safe.directory` handling).

## [2026-09-20] — cm8-prehuman-v1.0 (frozen)

- Immutable pre-human freeze: frozen CM-8 forecaster, protocol v1.0, ethics
  package, 10/10 readiness gates. SHA-256 registered in
  `registries/artifact_registry.json`.
