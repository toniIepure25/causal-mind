# Infrastructure

## Pod

- Kubernetes: namespace `runai-romania-dev`, pod `orchestraiq-jupyter-5d6c688775-fbxj5`
  (Run:ai workload `orchestraiq-jupyter`), node `k8s-worker-gpu-node-xe8545`.
- User: `jovyan` (SSH) / root (kubectl exec).
- SSH from workstation: `ssh -i ~/.ssh/id_ed25519_dgx -p 32516 jovyan@10.130.123.35`
  (node IP; the LoadBalancer IP 10.130.123.131 is firewalled from the workstation).
- kubectl from workstation: `kubectl --kubeconfig <kubeconfig> -n runai-romania-dev exec
  orchestraiq-jupyter-5d6c688775-fbxj5 -- <cmd>`.

## Compute

- GPU: 1x NVIDIA A100-SXM4-40GB (driver 570.172.08, CUDA 12.8).
- CPU: 256 logical cores visible (container limit 16).
- RAM: ~1 TiB visible (container limit 100 Gi).
- PyTorch 2.11.0+cu128 (system conda) and uv-managed 3.11 venv per project.

## Storage

- **Persistent (NFS PVC):** `/home/jovyan/work` (138 TB volume, ~107 TB free),
  `/home/jovyan/legacy-work`.
- **Ephemeral:** everything else (`/`, `/tmp`, `~/.cache`, conda). The pod has been
  evicted before when scratch filled the overlay — therefore:

```bash
export TMPDIR=/home/jovyan/work/.tmp
export PIP_CACHE_DIR=/home/jovyan/work/.pipcache
export XDG_CACHE_HOME=/home/jovyan/work/.cache
export HF_HOME=/home/jovyan/work/.cache/hf
export TORCH_HOME=/home/jovyan/work/.cache/torch
export UV_CACHE_DIR=/home/jovyan/work/.uv-cache
```

- Project data layout (all under the PVC, outside git):
  `data/raw/`, `data/derivatives/`, `data/cache/` (see `data/README.md`).

## Qwen endpoint

- Model: `Qwen/Qwen3.8-27B-FP8` (Run:ai workload `qwen38-27b12`, project
  `romania-dev`), OpenAI-compatible API.
- Local endpoint: `http://127.0.0.1:18000/v1` (port-forward of workload port 8000).
- Chain: `127.0.0.1:18000` -> runai CLI port-forward -> Caddy `127.0.0.1:19080` ->
  cluster ingress `10.130.240.221` (SNI `cisco-ai-pod.cc-demos.com`).
- Auth: runai CLI token under `/home/jovyan/.runai` (pod home, NOT on the PVC); proxy
  copy under `/home/jovyan/.runai-proxy`. Never printed, never committed.
- Supervisor: `scripts/qwen_tunnel_supervisor.sh {start|stop|status}` — health-checks
  `/v1/models` every 5 s and restarts the port-forward on failure.
- Runbook: `docs/runbooks/qwen_tunnel.md`.

## Tooling

- uv 0.12.5 at `/home/jovyan/work/.local/bin/uv` (shared, read-only reuse OK).
- OpenCode 1.18.19 at `.home/.opencode/bin/opencode` (project-local copy).
- runai CLI 2.116.10 at `.runai-cli/bin/runai`; Caddy 2.11.4 at `.caddy/bin/caddy`.
- git 2.43 (NFS: use `git -c safe.directory=*`).

## Network

- Outbound: PyPI, GitHub, OpenNeuro (to verify), Run:ai control plane — all reachable
  from the pod (verified for PyPI/GitHub by prior labs; OpenNeuro to be verified in
  CM-1).
