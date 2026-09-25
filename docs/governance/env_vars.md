# Environment Variable Registry

**Status:** canonical · **Template:** `.env.example` (names only, no real values)

All environment variables the project reads, what they do, their default, and
whether they may hold a secret. **Secrets are set in the environment or the
platform secret store — never committed.** `.env.example` lists names with
placeholder values only.

## Repository / path

| Var | Purpose | Default | Secret? |
|-----|---------|---------|---------|
| `CM_REPO_ROOT` | Explicit repository root (overrides auto-discovery). | auto (walk to `pyproject.toml`) | no |
| `CM_DATA_ROOT` | Explicit `data/` root. | `<repo>/data` | no |
| `CM_HF_HOME` | HuggingFace cache location (infrastructure). | `~/.hf-home` | no |
| `CM_AGENT_BIN` | Extra `PATH` dir for the agent's bash tool. | `~/work/.local/bin` | no |

## Run / logging

| Var | Purpose | Default | Secret? |
|-----|---------|---------|---------|
| `CM_RUN_ID` | Reuse an externally assigned run ID (idempotent). | generated (`cm-<exp>-<ts>-<sha>`) | no |
| `CM_LOG_JSON` | `1` = structured JSON logs (CI). | off (one-line) | no |

## Orchestration

| Var | Purpose | Default | Secret? |
|-----|---------|---------|---------|
| `CM_QUEUE_ROOT` | Task queue root. | `<repo>/orchestration/tasks` | no |
| `CM_REPORT_ROOT` | Report output root. | `<repo>/reports` | no |
| `CM_WORKTREE_ROOT` | Agent worktree root. | `<work>/worktrees/causal-mind-v2` | no |

## LLM endpoint (orchestration only — NOT participant inference)

| Var | Purpose | Default | Secret? |
|-----|---------|---------|---------|
| `CM_QWEN_BASE_URL` | OpenAI-compatible Qwen endpoint. | `http://127.0.0.1:18000/v1` | no |
| `CM_QWEN_MODEL` | Model name. | `Qwen/Qwen3.8-27B-FP8` | no |
| `CM_QWEN_API_KEY` | Bearer token, if the proxy requires one. | (none) | **yes** |

## Infrastructure caches (set on the pod, on the PVC)

| Var | Purpose | Note |
|-----|---------|------|
| `HF_HOME`, `TORCH_HOME`, `XDG_CACHE_HOME`, `PIP_CACHE_DIR`, `TMPDIR` | Caches/scratch | Must live under `/home/jovyan/work` (PVC), never system temp. Set by `scripts/bootstrap_environment.sh`. |

## Rules

1. **Never commit a real secret.** `cm security scan` + the CI secret scan
   hard-fail on credential-looking literals.
2. **`.env.example` holds names + placeholders only** (e.g. `CM_QWEN_API_KEY=`).
3. **The Qwen endpoint is for orchestration/agents only.** Participant-facing
   CM-8 inference is offline and never calls a remote LLM.
4. **Caches stay on the PVC.** Pointing them at system temp risks data loss on
   pod restart and violates the storage policy.
