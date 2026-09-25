# Security

**Status:** canonical · **Companions:**
[threat models](docs/governance/threat_models.md),
[data classification](docs/governance/data_classification.md),
[env var registry](docs/governance/env_vars.md)

## Reporting a vulnerability

If you find a security issue (a committed secret, a public bind, a data-exfil
path, a way to bypass the human-data guard, or a supply-chain risk):

1. **Do not** push it, do not add the secret to a commit, do not open a public
   issue with the details.
2. Report it to the project maintainer / supervisor directly (private channel).
3. If a secret was already committed, treat it as **compromised**: rotate it
   immediately, then purge it from history with a documented, reviewed
   process (never a silent force-push).

## Automated controls (run in CI and locally)

| Control | Command | Enforced by |
|---------|---------|-------------|
| Secret scan (credential-looking literals) | `cm security scan` | CI + pre-commit |
| Security audit (public binds, telemetry, credential files) | `data/scripts/cm_lab_security.py --check` | CI + `cm validate` |
| Human-data guard (no real participant data pre-gate) | `cm security scan` | CI + pre-commit hook |
| Lint/type ratchet | `data/scripts/cm_lab_lint_gate.py` | CI + pre-commit hook |

Run them yourself before pushing:

```bash
cm security scan          # security audit + secret scan + human-data guard
cm validate               # all scientific-integrity gates
bash scripts/validate_project.sh   # full one-command validation
```

## Secrets policy

- **Never commit a secret.** Secrets (API keys, tokens, SSH keys, K8s secrets,
  `.runai` auth) live in the environment or the platform secret store only.
- `.env.example` lists variable **names** with placeholder values — never real
  values. See the [env var registry](docs/governance/env_vars.md).
- The Qwen endpoint (`CM_QWEN_*`) is for orchestration/agents only and is
  **not** used at participant-facing inference (CM-8 is offline).

## Network policy

- Local tooling binds to `127.0.0.1` only. No service is exposed publicly.
- The security audit (`cm_lab_security.py --check`) fails on non-loopback binds
  and on telemetry endpoints.

## Human-data gate (privacy)

No real human participant data may enter Git before the human/ethics gate is
passed. The `human_data_guard.py` check (pre-commit + CI) hard-fails on staged
files in human-data directories or with data-like names under `data/`. See the
[data-protection threat model](docs/governance/threat_models.md#3-data-protection-threat-model).

## Scope

Platform-level security (pod hardening, Kubernetes RBAC, Run:ai credentials,
NVIDIA drivers) is out of scope for this repository and is the platform's
responsibility. This document covers repository-level controls only.
