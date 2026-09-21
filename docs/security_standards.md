# Security Standards (CM-LAB S75-S84)

**Status: `CMLAB_SECURITY_PASS`** — enforced by `data/scripts/cm_lab_security.py`, which runs
in the one-command validation (`scripts/validate_project.sh`) and CI on every push/PR.

## Security properties (all enforced, all currently PASS)
1. **No secrets in the repo.** No private keys, cloud access keys (AWS/GCP/Azure), GitHub/Slack
   tokens, or credential literals. A pattern-based secret scan covers all tracked text files.
   Security test fixtures that deliberately contain FAKE credentials are excluded by name.
2. **No credential files tracked in git.** No SSH keys (`id_*`), `.env` (templates like
   `.env.example` are allowed), `.pem`/`.p12`/`.pfx`, `.netrc`, `known_hosts`, Kubernetes
   `kubeconfig`, Run:ai creds, or service-account JSON.
3. **No public service exposure.** No code binds to `0.0.0.0`; local tooling binds `127.0.0.1`.
4. **No remote telemetry.** No outbound `requests.post/put` of data to external endpoints.
5. **Pinned, auditable dependencies.** The full dependency set (90 packages) is pinned in
   `uv.lock`; the inventory is recorded in `reports/security_audit.json`.

## What the audit does not cover (out of scope / handled elsewhere)
- **Dependency vulnerability DB audit** (e.g., `pip-audit`): requires network access to a
  vulnerability feed; the pinned `uv.lock` is the control. Run `uv pip compile --check` /
  `pip-audit` manually before a release if a feed is reachable.
- **Human/PII data protection**: handled by the CM-8R privacy hardening (pseudonymization,
  encryption at rest, no PII in the repo). No human data is collected in this phase.

## Credential-access rules (from AGENTS.md, enforced by convention + review)
- Agents must not read `~/.runai`, `~/.runai-proxy`, SSH keys, Kubernetes config, or any
  hidden credential file.
- Never print, commit, or log passwords, API keys, bearer tokens, SSH keys, or token-bearing
  files.
- The pod has no GitHub token; pushes go through the authorized workstation flow.

## Reproduction
```
.venv/bin/python data/scripts/cm_lab_security.py            # full audit + report
.venv/bin/python data/scripts/cm_lab_security.py --check    # CI gate (non-zero on any FAIL)
```
Machine-readable result: `reports/security_audit.json`.
