# Data Classification

**Status:** canonical

Every piece of data in or around this repository has a classification that
determines where it may live, whether it may be committed, and how it must be
handled. This is the single reference for "may I put this file in Git?"

## Classes

| Class | Examples | In Git? | Handling |
|-------|----------|---------|----------|
| **C0 public** | ds006067 (OpenNeuro), OSF `a56rm`, published papers | yes (pointers/manifests) | Cite the source license; raw data usually gitignored, fetched on demand. |
| **C1 derived-synthetic** | `data/derived/thought_events/`, simulated-agent streams, `cm8_synthetic.py` output | yes (small) / gitignored (large) | Deterministic from C0 + frozen code; reproducible. |
| **C2 frozen-artifact** | `artifacts/cm8_forecaster/*`, manifests/seals, registries | **yes** | SHA-256 registered; immutable; verified by `cm artifacts verify`. |
| **C3 report/claim** | `reports/*`, `claims/claims.json`, `docs/*` | **yes** | Human-readable; must not contain raw C4 data. |
| **C4 human-participant** | Real CM-8P pilot thought streams, raw BOLD, consent forms with signatures | **NO (pre-gate)** | Pseudonymized, encrypted at rest, never committed before the human/ethics gate. Guarded by `human_data_guard.py`. |
| **C5 secret** | API keys, tokens, SSH keys, K8s secrets, `.runai` | **NEVER** | Env vars / secret store only; scanned by `cm security scan` + CI. |

## Rules

1. **C4 never enters Git before the human gate.** The pre-commit hook and CI
   (`cm security scan`) hard-fail on staged files in human-data directories
   (`data/cm8p/`, `data/human/`, `data/pilot/`, `data/participants/`) or with
   data-like names under `data/`. See [threat models](threat_models.md).
2. **C2 is immutable.** A frozen artifact's SHA-256 is registered; changing it
   requires a new artifact + a documented amendment, never an in-place edit.
3. **C3 must not embed C4.** Reports cite statistics and file paths, never raw
   participant text. The leakage scanner checks this.
4. **C5 is env-only.** Secrets live in environment variables (see
   [env var registry](env_vars.md)) or the platform secret store — never in a
   tracked file. `.env.example` documents the *names* with placeholder values.
5. **Large C0/C1 data is gitignored.** Only manifests, checksums, and loaders are
   committed; raw data is fetched to the project PVC.

## Where data lives

- **Committed (small, versioned):** `data/manifests/`, `artifacts/`,
  `registries/`, `claims/`, small `data/derived/` samples.
- **Gitignored (large, on PVC):** `data/raw/`, large `data/derived/`,
  `data/embeddings/`, model weights, caches.
- **Never committed:** C4 (pre-gate), C5.

## Decision helper

> "May I commit this file?"
> - Is it a secret (C5)? → **No, ever.**
> - Is it real human data (C4) and the human gate is not passed? → **No.**
> - Is it a frozen artifact (C2)? → **Yes**, and register its SHA-256.
> - Is it a report/claim/doc (C3) with no raw C4? → **Yes.**
> - Is it large raw/derived data (C0/C1)? → **No** (gitignore); commit the
>   manifest + loader instead.
