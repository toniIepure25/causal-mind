# Datasets

## Primary: OpenNeuro ds006067 (target)

Think-aloud spontaneous thought + fMRI. **Status: authoritative audit pending (CM-1).**
Nothing in this file is trusted until the audit records the openneuro.org metadata,
subject count, run count, TR, transcript format, word timestamps, thought boundaries,
annotations, psychological dimensions, license, and measured footprint in
`data/manifests/ds006067.yaml` with checksums.

Expected use:
- transcripts + timestamps -> thought events (CM-2)
- fMRI -> neural features (CM-5/CM-6), lag-aware for BOLD
- annotations -> cognitive dimensions (temporality, self-relevance, affect, ...)

Acquisition policy:
1. Audit metadata from authoritative sources first.
2. Download the smallest useful subset (1-2 subjects, 1 run each) to validate the
   loader.
3. Expand only after GATE A passes.
4. Every file recorded in the manifest with SHA-256.

## Secondary (CM-10, later): public EEG

Candidates to be verified independently before use: mind-wandering / spontaneous
thought / naturalistic-language EEG datasets (e.g., publicly released mind-wandering
EEG corpora). Goal: a representation suitable for eventual realtime use.

## License and ethics

- All datasets must have a license compatible with research use; recorded per dataset.
- No human-identifying data is stored beyond what the public release provides.
- Any future human experiment (CM-11/12/13) requires ethics/IRB approval first.
