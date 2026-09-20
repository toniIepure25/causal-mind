# CM-PUB — Final Report

Publication, supervisor handoff, and pre-pilot freeze. Part of the `cm8-prehuman-v1.0`
freeze. This report summarizes what CM-PUB produced and the resulting project state.

## Objective (restated)

Transform the completed CM-1 → CM-9A program into a professional, reproducible,
publication-ready research package suitable for a University of Vienna supervisor, ethics
support, a Master's project, and future academic publication — while preserving all
positive and negative results and exact provenance. **No human data; no CM-8 protocol
changes; no optimization from simulation; no reopening of closed phases.**

## Success state

**`CMPUB_SUPERVISOR_HANDOFF_READY`** (primary). Secondary states also met:
`CMPUB_PAPER1_DRAFT_READY`, `CMPUB_PAPER2_DRAFT_READY`, `CM9_THEORY_OUTLINE_READY`.

## What was produced (by section)

### Release freeze (§1)
- `docs/releases/cm8_prehuman_v1.md` — the formal pre-human freeze (git `8a9d5dd`, date,
  completed phases, scientific decisions, frozen components + SHAs, ethics status, human
  blockers, reproduction commands).
- Tag `cm8-prehuman-v1.0` created and pushed to GitHub.
- Pre-freeze verification: working tree clean, remote/main exact, no credentials (9 hits all
  false positives), no new participant data (only public OSF `a56rm` transcripts, 3.2 MB),
  no large raw datasets, all manifest hashes valid (clean-room bit-identical).

### Master summary + evidence (§2, §3)
- `docs/CAUSAL_MIND_master_summary.md` — the single authoritative pre-human summary.
- `docs/claims/evidence_matrix.md` — claim-level traceability (C-001..C-012 → level → exact
  value → report → code → reproduction command).

### Supervisor package (§4, §5, §6, §17, §18, §35, §36)
- `docs/supervisor/START_HERE.md` — 5-minute entry point.
- `docs/supervisor/cm_one_page.md` — one-page brief.
- `docs/supervisor/cm_technical_brief.md` — technical overview.
- `docs/supervisor/master_thesis_options.md` — 4 thesis options + recommendation.
- `docs/supervisor/10min_pitch.md` — spoken 10-minute pitch.
- `docs/supervisor/contact_package.md` — ready-to-send email + attachments + asks.
- `docs/supervisor/questions_for_supervisor.md` — specific decisions, each with a default.

### Papers (§7, §8, §9, §10, §11, §29)
- `papers/paper1_predictive_dynamics/` — manuscript + figures + reproducibility (CM-2/CM-3).
- `papers/paper2_prediction_to_intervention/manuscript.md` — causal method + frozen design.
- `papers/paper3_break_the_chain_protocol/protocol.md` — standalone frozen CM-8 protocol.
- `papers/oracle_theory/outline.md` — CM-9A → CM-9 synthetic Oracle theory outline.

### Science docs (§12, §13, §14, §15, §30)
- `docs/novelty_matrix.md`, `docs/science/limitations.md`,
  `docs/science/negative_results.md`, `docs/science/known_unknowns.md`,
  `docs/roadmap_post_cm8.md`.

### Tooling + audits (§16, §20–§28)
- `data/scripts/cm_pub_claim_linter.py` — claim-language linter (verified on the repo:
  **0 BLOCK, 8 WARN, PASS**).
- `reports/publication_consistency_audit.md` — cross-document consistency (ALL CONSISTENT).
- `reports/reproducibility_traceability.md` — result → command → artifact → report.
- `reports/statistical_reporting_audit.md` — every result has effect + CI + p/exact + N +
  method (ALL COMPLETE).
- `docs/paper_methods_detail.md` — paper-quality consolidated methods.
- `reports/story_red_team.md` — red team of the scientific story (7 attacks + defenses).
- `reports/reviewer_simulation.md` — 3 simulated external reviewers + responses.
- `docs/reviewer_response_preparation.md` — consolidated response bank (R1–R12).
- `docs/venue_landscape.md` — venue fit (no acceptance probability claimed).
- `docs/supervisor/thesis_timeline.md` — thesis timeline (Scenario A / B).
- `docs/cm8/cm8_pilot_handoff.md` — CM-8P pilot handoff (GO/ITERATE/STOP).

### Repo hygiene + metadata (§31, §32, §33, §34)
- `README.md` — rewritten for the freeze (keeps the causal-world-model framing; updates the
  state).
- `reports/repo_hygiene_audit.md` — hygiene audit (HYGIENE PASS).
- `CITATION.cff` — citation metadata (author/affiliation placeholders; no DOI claimed).
- `docs/science/license_data_use_audit.md` — code license + data-use terms (3 decisions
  required).

## Verification

- **Claim linter:** 0 BLOCK, 8 WARN (all legitimate negation contexts), PASS.
- **Consistency audit:** all key values/states consistent across documents.
- **Statistical reporting audit:** all results complete (effect + CI + p/exact + N + method).
- **Repo hygiene:** no secrets, no new participant data, no large raw datasets.
- **Provenance:** every result maps to a committed report + frozen artifact + reproduction
  command.

## What was NOT done (by design)

- No human data collected.
- No change to the frozen CM-8 confirmatory protocol (Workstream A).
- No optimization of the CM-8 design from simulation.
- No reopening of a closed negative result.
- No free-will claim; no overclaiming.
- No fabricated visuals, DOIs, affiliations, supervisors, or acceptance probabilities.

## Remaining (external / human) blockers

1. Supervisor sign-off.
2. Ethics approval (University of Vienna; submission deadline 5 Oct 2026).
3. Pilot authorization (CM-8P) → confirmatory run (CM-8H).

## Open decisions (for the supervisor / institution)

- Code license (MIT / Apache-2.0 / GPL-3.0 / institution policy) + add a `LICENSE` file.
- CITATION.cff author + affiliation (placeholders).
- Data-sharing scope (which pseudonymized artifacts are shareable post-approval).
- Thesis direction (Option A/B/C/D) and defense date.

## Result

**`CMPUB_SUPERVISOR_HANDOFF_READY`.** The program is a complete, reproducible, honest,
publication-ready pre-human research package. The only remaining work is the human
experiment, gated on the three external approvals above.
