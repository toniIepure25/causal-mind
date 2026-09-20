# License / Data-Use Audit

An audit of the code license and the data-use terms for the public datasets. Part of the
`cm8-prehuman-v1.0` freeze. **No license is assumed; this audit states what applies and what
needs a decision.**

## Code license

- **Current state:** the repository has no explicit top-level `LICENSE` file (to be
  confirmed). The code is research code produced for a Master's thesis.
- **Recommendation:** add an explicit `LICENSE` before any external sharing. For a thesis
  with a supervisor/institution, the **institution's** policy usually governs; a common
  default for research code is **MIT** or **Apache-2.0** (permissive) or **GPL-3.0**
  (copyleft). **Decision required from the supervisor/institution.**
- **CITATION.cff** references the license as "SEE LICENSE IN
  `docs/science/license_data_use_audit.md`" (a placeholder until the `LICENSE` file is
  added).

## Data-use terms (public datasets)

| dataset | source | license / terms | use in this program |
| --- | --- | --- | --- |
| OSF `a56rm` (thought diaries) | OSF | Public; per the OSF project's stated terms (cited) | thought-stream corpus (CM-1/2/3/5/6/8) |
| OpenNeuro `ds006067` (MRI) | OpenNeuro | OpenNeuro data policy (cited) | fMRI for CM-5 (neural null) |
| OpenNeuro `ds005494` (semantic priming) | OpenNeuro | **CC0** (public domain) | CM-7 method validation |

- All three are **public** datasets; they are cited by their own licenses/terms, not
  re-licensed by this program.
- The 119 tracked thought transcripts (3.2 MB) are the public `a56rm` data, tracked for
  reproducibility. They are governed by the `a56rm` terms, not by this program's code
  license.

## Participant data (future, CM-8)

- **No participant data has been collected.** When the CM-8 experiment runs, the participant
  data is governed by the University-of-Vienna ethics approval and the GDPR data-protection
  plan (`docs/ethics/`), **not** by the code license.
- **Privacy-by-design:** pseudonymized, embeddings only, encryption at rest, no remote
  LLM/telemetry, complete deletion on request.
- **Sharing:** the (pseudonymized, post-approval) analysis artifacts may be shared per the
  ethics approval; the raw thought data is handled per the GDPR plan.

## Decisions required

1. **Code license:** choose a `LICENSE` (MIT / Apache-2.0 / GPL-3.0 / institution policy)
   and add the `LICENSE` file. *(Default if silent: leave as-is; do not share externally
   until a license is chosen.)*
2. **CITATION.cff author/affiliation:** complete the placeholder author + affiliation.
3. **Data sharing scope:** confirm which (pseudonymized) artifacts are shareable after
   ethics approval.

## Result

**AUDIT COMPLETE (with 3 decisions required).** No license is assumed; the public datasets
are governed by their own terms; future participant data is governed by the ethics approval
+ GDPR plan. The code license and the CITATION.cff author/affiliation are the open items.
