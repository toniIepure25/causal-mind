# CM-8 Ethics Application — Answers (mapped to the University of Vienna form)

- **Note:** This maps the study onto standard University of Vienna Ethics Committee
  application fields. Fields requiring institutional/personal details are marked
  **`HUMAN INPUT REQUIRED`** (supervisor / institution). Do NOT fabricate supervisor,
  institutional, funding, compensation, or contact details.
- **Submission authority:** for a Master's thesis, submission is made by the **supervisor or
  responsible study-law body**, not the researcher. This package is for supervisor
  review/sign-off.

## A. Persons and institution

- **Principal investigator / applicant:** `HUMAN INPUT REQUIRED`
- **Supervisor (responsible for submission):** `HUMAN INPUT REQUIRED`
- **Institution / department:** University of Vienna — `HUMAN INPUT REQUIRED` (exact
  department/faculty)
- **Study-law classification:** behavioral, non-medical, non-invasive (to be confirmed by the
  responsible study-law body) — `HUMAN INPUT REQUIRED`
- **Funding source:** `HUMAN INPUT REQUIRED` (e.g., none / thesis / grant)
- **Target submission window:** University of Vienna Ethics Committee deadline **5 October
  2026** for the **5 November 2026** meeting (subject to supervisor/institutional
  eligibility).

## B. Study identification

- **Title:** Causal Redirection of a Predicted Semantic Thought Trajectory: a randomized
  within-subject experiment (Pre-Oracle / "Break the Chain").
- **Type:** behavioral, within-subject, randomized, single-site.
- **Duration of the project:** [pilot + confirmatory] — `HUMAN INPUT REQUIRED` (timeline).
- **Number of participants:** 20 completed (recruit 25 at 20% attrition).
- **Session duration:** ~45–60 minutes (single session).

## C. Scientific rationale and hypotheses

- **Rationale:** CM-2/3 predict future thought semantics from history; CM-6 showed
  observational structure cannot establish causality; CM-7 validated the causal machinery on
  public data. CM-8 tests whether a deliberate or externally-induced intervention causally
  redirects a predicted semantic trajectory. (See `cm8_research_plan.md` §1.)
- **Hypotheses:** H1 (endogenous redirect increases BRP), H2 (external cue increases BRP),
  H3 (sham no-op), H4 (persistence beyond one step). (See `cm8_research_plan.md` §2.)
- **Expected contribution:** first experimentally-identified causal test of redirection of a
  *predicted* semantic trajectory with a frozen basin metric; a null is a valid result.

## D. Procedure

- **Conditions:** CONTROL / SHAM / GENERAL REDIRECT / SPECIFIC CUE (see `cm8_research_plan.md`
  §3).
- **Timeline per trial:** baseline window → state estimation → forecast → randomization →
  intervention → post-window → outcome → optional self-report (§4).
- **Randomization:** within-subject, counterbalanced, frozen seed + manifest (§5).
- **Primary endpoint:** BRP at frozen horizon `h*`; ATE_GENERAL and ATE_CUE vs pooled
  CONTROL/SHAM; subject-clustered permutation test, two-sided α=0.05, B=10,000 (§7).
- **Capture modality:** pilot decision (think-aloud / typed / probes) (§17).

## E. Participants

- **Inclusion:** healthy adults, 18–35, fluent [language — `HUMAN INPUT REQUIRED`].
- **Exclusion:** `HUMAN INPUT REQUIRED` (neurological/psychiatric conditions affecting
  thought/speech, etc.).
- **Recruitment:** via the Vienna Cognitive Science Hub Study Participant Platform (after
  approval) or [other — `HUMAN INPUT REQUIRED`].
- **Vulnerable groups:** none targeted (healthy adults).

## F. Risks and benefits

- **Risks:** minimal (see `cm8_risk_assessment.md`): mild frustration, discomfort, accidental
  disclosure of sensitive content, perceived evaluation, concern about being "predicted,"
  fatigue. Mitigations + stopping criteria defined.
- **Benefits:** no direct benefit to participants; contribution to cognitive science.
- **Compensation:** `HUMAN INPUT REQUIRED` (see `cm8_compensation_plan.md`).

## G. Data protection (GDPR)

- **Legal basis:** consent (Art. 6(1)(a)).
- **Pseudonymization:** study code; identity key stored separately, encrypted, access-limited.
- **Sensitive data:** thought-stream free text (highly sensitive); encrypted, access-limited,
  deleted after analysis (or retained per separate consent). Pseudonymized data are NOT
  anonymous. (See `cm8_data_management_plan.md`.)
- **Retention / deletion:** raw text deleted after analysis + verification window; identity
  key for the withdrawal window + legal holds.
- **Data-protection officer / contact:** `HUMAN INPUT REQUIRED`.
- **Data sharing:** only aggregated, de-identified results.

## H. Consent and debrief

- **Consent:** written (or recorded verbal) informed consent (`cm8_consent.md`); voluntary;
  may stop at any time; may skip/withhold reports.
- **Debrief:** full debrief including the sham (`cm8_debrief.md`).
- **Withdrawal / deletion limits:** data before withdrawal retained unless deletion requested
  within the window; already-analyzed/aggregated data cannot always be deleted (stated in
  consent).

## I. Preregistration and analysis

- **Preregistration:** `cm8_preregistration_final.md` (frozen primary endpoint, exploratory
  secondaries, pre-specified exclusions, decision rules).
- **Statistical calibration:** independently reproduced; type-I error at α=0.05 = 0.047
  (MC CI [0.013, 0.080]); valid exact randomization test; CALIBRATION PASS.

## J. Software / reproducibility

- **Freeze:** experiment UI, forecasting model SHA, semantic encoder, basin calibration,
  randomization code, and primary analysis implementation are frozen in
  `cm8_software_freeze_manifest.json` (machine-readable SHAs/config hashes).
- **Dry run:** synthetic + researcher-operated dry tests performed (no human data); see
  `cm8_dry_run_report.md`.

## K. Ethics contacts

- **Ethics / complaints contact:** `HUMAN INPUT REQUIRED` (University of Vienna ethics
  office).
- **Data-protection officer:** `HUMAN INPUT REQUIRED`.

## L. Declaration

- The researcher declares that no participant recruitment or data collection has begun; the
  study is gated on ethics approval.
- All human-required institutional fields are enumerated above as `HUMAN INPUT REQUIRED`.
