# CM-8 Data Management & Data-Protection Plan (GDPR)

- **Scope:** thought-stream free text is potentially highly sensitive (special-category-
  adjacent). This plan is privacy-by-design. **Pseudonymized data are NOT anonymous** —
  they remain personal data (the study code is a pseudonym; the name–code key re-identifies).

## 1. Data categories

| category | content | personal? | handling |
| --- | --- | --- | --- |
| Identity key | name ↔ study code | **yes** (directly identifying) | stored separately, encrypted, access-controlled; minimal retention |
| Pseudonym | study code (e.g., P-001) | **yes** (pseudonym = personal data) | used in all analysis files |
| Raw thought text | free text of reported thoughts | **yes** (pseudonymized, sensitive) | encrypted at rest; access-limited; deleted after analysis (or retained per separate consent) |
| Semantic embeddings | MiniLM vectors of thoughts | **yes** (pseudonymized; derived from text) | retained for analysis; not directly re-identifying but linked by code |
| Derived trajectories | BRP, divergence, persistence, etc. | **yes** (pseudonymized) | retained for analysis |
| Self-report | effort / perceived success | **yes** (pseudonymized) | retained for analysis |
| Audit log | timestamps, condition, prediction, latency | **yes** (pseudonymized) | retained for audit |
| Aggregated results | group-level statistics | **no** (anonymized) | may be shared/published |

**Explicit determination:** after pseudonymization, the raw text, embeddings, trajectories,
self-reports, and audit log **remain personal data** (linked to the study code). Only
aggregated, de-identified group statistics are anonymous. We do NOT describe pseudonymized
data as anonymous.

## 2. Pseudonymization and identity key

- Each participant gets a study code (P-001, …). All analysis files use the code only.
- The identity key (code ↔ name/contact) is stored **separately** from the data, encrypted,
  with access limited to the [investigator + supervisor — HUMAN INPUT REQUIRED].
- The key is retained only as long as needed (e.g., for the withdrawal/deletion window and
  any legal hold), then destroyed.

## 3. Access permissions

- **Raw text:** access limited to the analysis team; no access for the model/predictor
  beyond the encoding step (the predictor consumes embeddings, not raw text, in the
  confirmatory analysis).
- **Identity key:** investigator + supervisor only.
- **Aggregated results:** the research team.
- Access is logged; least-privilege; no shared credentials.

## 4. Encryption

- **At rest:** raw text + identity key encrypted (AES-256 or equivalent) on the project
  storage.
- **In transit:** data transferred only over encrypted channels (SSH/HTTPS); no raw text in
  plain text in logs.

## 5. Retention and deletion

- **Raw text:** deleted after the confirmatory analysis + a verification window (e.g.,
  [6 months — HUMAN INPUT REQUIRED]), unless the participant gave the separate §8 consent
  for longer retention.
- **Embeddings / trajectories / self-reports / audit log:** retained for the study + a
  reasonable audit period, then deleted.
- **Identity key:** retained for the withdrawal/deletion window + legal holds, then
  destroyed.
- **Aggregated results:** retained per institutional research-data policy.

## 6. Anonymization strategy

- For any public release or publication: **only aggregated, de-identified group statistics**
  (no individual-level raw text, embeddings, or trajectories).
- If individual-level data must be shared (e.g., for replication), they are pseudonymized,
  the identity key is withheld, and a data-use agreement is required.

## 7. Backups

- Backups of raw text are encrypted and access-controlled like the primary store; backup
  retention matches the primary retention. Backups do not increase the retention period.

## 8. Logs

- Access to raw text and the identity key is logged (who, when, what). Logs are retained for
  the audit period and then deleted.

## 9. Git exclusions

- **No raw text, no identity key, no participant-level data, no credentials, no signatures,
  no supervisor personal information** in Git.
- `.gitignore` excludes `data/raw/`, any participant data directories, and manifest files
  containing personal data. Only code, config hashes, and de-identified aggregated results
  are committed.

## 10. Research-data sharing policy

- Aggregated, de-identified results may be shared/published.
- Individual-level data are shared only pseudonymized, under a data-use agreement, with the
  identity key withheld, and only if the ethics approval permits.

## 11. Accidental disclosure of highly personal information

- **Prevention:** participants may skip/generalize; the task does not probe sensitive topics;
  raw text is access-limited and encrypted.
- **If a participant discloses something highly personal or distressing:** the researcher
  pauses, offers support, and does not press for more; the participant may stop.
- **If a data breach occurs:** the affected participant is informed, the data-protection
  officer and (if required) the supervisory authority are notified per GDPR Art. 33/34, and
  the incident is documented. The study is paused until the breach is contained.

## 12. Legal basis and rights

- **Legal basis:** consent (Art. 6(1)(a) GDPR).
- **Participant rights:** access, rectification, erasure (within the limits of already-
  analyzed/aggregated data), restriction, portability, objection, and withdrawal of consent
  at any time (withdrawal does not affect lawfulness of prior processing).
