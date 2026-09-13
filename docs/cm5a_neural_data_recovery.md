# CM-5A — Neural Data Recovery (access audit)

**Date:** 2026-09-13 · **Dataset:** `ds006067` · **Snapshot:** `2.0.0`
**Goal:** acquire the minimum real fMRIPrep MNI BOLD derivatives for `sub-001`/`sub-005` via official/versioned OpenNeuro access paths before treating the outage as unavoidable.

## Decision: `CM5A_OPENNEURO_AUTH_BLOCK`

Every official content path is reachable but **gated on OpenNeuro authentication** (an API key / personal access token). No anonymous/public content access exists. The metadata (git tree, annex keys, sizes, tag `2.0.0`) is fully available via the public GitHub mirror; only the **content** is auth-gated.

## Access paths tested

| Path | Result | Detail |
|------|--------|--------|
| **S3 (public `openneuro`)** | BLOCKED | `s3://openneuro/ds006067/` prefix is empty (no V1.x raw, no V2.0.0). |
| **S3 (private `openneuro-datasets`)** | BLOCKED | `403` for annex keys (needs signed URLs from the down API). |
| **S3 (`openneuro-derivatives`)** | BLOCKED | No `ds006067` objects. |
| **PATH A — OpenNeuro CLI** | BLOCKED (auth) | Installed standalone node v20.11.1 + `@openneuro/cli` 4.30.2 into `/home/jovyan/work/.local`. `openneuro download` fails: *"You must have an API key configured to continue, try `openneuro login` first"* (browser OAuth). URL-only config does not bypass the API-key requirement. |
| **PATH A — git-annex special remote** | BLOCKED | Not a pip package (part of the Node CLI); the CLI path above already shows the API-key gate. |
| **PATH B — direct Git (git server)** | BLOCKED (auth) | `openneuro.org/git/2/ds006067` reachable; `info/refs` + `annex/{key}` return **401** with `www-authenticate: Basic realm="dataset git repo"`. Fake bearer/basic/userinfo creds → 400. Requires a PAT (Basic auth). |
| **PATH C — GitHub mirror** | METADATA ONLY | `OpenNeuroDatasets/ds006067` clone at `/home/jovyan/work/ds006067_git`: commit `53df4728`, tag `2.0.0`, all 118 `events.tsv` + `participants.tsv` real. **0 non-empty annex objects** — BOLD are dangling symlinks (content absent). |
| **PATH D — DataLad** | NOT AVAILABLE | `datalad` not installed; would use the same S3/git-server content (auth-gated). |
| **OpenNeuro API** | PARTIAL | `openneuro.org/api/` → `200 OK` (health). `api.openneuro.org` + `api.neuro.polymtl.ca` + `datasets.openneuro.org` → **no A record** (DNS down). Dataset CRUD routes on the main domain → 404 (minimal API, git-proxy only). No signed-URL endpoint reachable. |

## Annex diagnostics (non-secret)

- Git server: `https://openneuro.org/git/2/ds006067` (Basic auth, `realm="dataset git repo"`).
- Configured annex remote in the clone: `openneuro-annex → https://openneuro.org/annex/ds006067` — but that URL returns the **SPA HTML** (not a git repo) and is marked `annex-ignore=true`; not usable.
- The real annex content is served by the git server (`/git/2/ds006067/annex/{key}`) and returns **401** without a token.
- `git annex get --from=openneuro-annex` hangs (the remote URL is not a valid git repo) — killed; no content fetched.
- A standalone `git-annex` 10.20260717 is installed at `/home/jovyan/work/.local/git-annex/git-annex.linux/git-annex`.

## Minimal file set (sub-001 + sub-005)

Manifest: `data/manifests/cm5_minimal_neural_files.tsv` (12 files).

- **Required (MNI BOLD + mask + confounds + JSONs):** ~1.57 GB
  - sub-001 MNI BOLD `SHA256E-s771374821--52c7…` (771 MB)
  - sub-005 MNI BOLD `SHA256E-s790999446--bf44…` (791 MB)
  - brain masks (8.4 KB / 8.7 KB), confounds TSV (2.1 MB / 2.0 MB), BOLD + confounds JSON (in-git).
- **Optional (smooth4mm denoise, for N1–N3 features):** +742 MB → ~2.31 GB total.
- fMRIPrep **23.2.1**, `space-MNI152NLin2009cAsym`, BIDS 1.4.0 (from `derivatives/dataset_description.json`).

## Raw V1.x fallback

- **Available:** NOT via any working remote. The public S3 `ds006067/` prefix is empty (no raw V1.x), and the raw BOLD is annexed in the same auth-gated git server.
- **Exact preprocessing reproducible:** NOT established (no raw data to run fMRIPrep 23.2.1 on).
- **Estimated cost:** N/A (blocked at access, not at compute).
- Per protocol, **no cohort-wide fMRIPrep** was launched.

## What unblocks this (human action)

Provide an **OpenNeuro API key / personal access token** for an account that can read `ds006067`:
1. Log in at https://openneuro.org.
2. Create a personal access token / API key (read access).
3. Provide the token + account email (do NOT paste it into chat if avoidable — a pod-side secret file or `openneuro login` on a machine with a browser both work).

With a token, the recovery is a single bounded step:
- **CLI:** write `~/.openneuro` = `{"url":"https://openneuro.org","apikey":"<TOKEN>"}` → `openneuro download ds006067 <dir> -s 2.0.0` (then `git annex drop-unwanted` to keep only the 12 files), **or**
- **git server:** `git`/`git-annex` with Basic auth `<email>:<TOKEN>@openneuro.org/git/2/ds006067` → `git annex get` the 12 manifest files.

Then: hash-validate against the manifest keys → `cm5_validate_bold.py` → HRF-safe windows → real-data CM-5 smoke → continue CM-5 automatically.

## State

- Cheap retry poller kept alive: `/home/jovyan/work/cm5_access_retry.sh` (PID 398863), log `/home/jovyan/work/cm5_access_retry.log` (API still no-A-record, S3 403).
- Frozen CM-5 scientific protocol **not modified**.
- No other dataset substituted.
