# Qwen Tunnel Runbook

The Qwen endpoint is a Run:ai workload (`qwen38-27b12`, project `romania-dev`) reached
through a local port-forward. Everything binds to `127.0.0.1`.

## Components

| component | location | role |
| --- | --- | --- |
| runai CLI | `.runai-cli/bin/runai` | authenticates to the cluster, port-forwards the workload |
| supervisor | `scripts/qwen_tunnel_supervisor.sh` | keeps the port-forward alive, health-checks every 10 s |
| runai auth | `/home/jovyan/.runai/authentication.json` (pod home, NOT on PVC) | CLI token + refresh token |

Endpoint: `http://127.0.0.1:18000/v1`, model `Qwen/Qwen3.8-27B-FP8`.

**No Caddy.** The cluster gateway `cisco-ai-pod.cc-demos.com` (10.130.240.221) is
directly reachable from the SSH session's network namespace, so the port-forward talks
to it directly. (The original `hotc2026-lab` setup used Caddy because the main
container's netns could not resolve the gateway hostname.)

## Network namespaces (important)

The SSH session (`jovyan@10.130.123.35:32516`) runs in a **sidecar network namespace**
of the pod: the main container's `127.0.0.1:18000` is NOT visible from SSH, and vice
versa. The supervisor must therefore be started **from the SSH session** so the
port-forward binds in the SSH netns where the agents run. The PID namespace is shared,
so `ps` sees main-container processes, but their sockets are not reachable.

## Operations

```bash
cd /home/jovyan/work/causal-mind-v2
scripts/qwen_tunnel_supervisor.sh status    # RUNNING + QWEN HEALTHY expected
scripts/qwen_tunnel_supervisor.sh start
scripts/qwen_tunnel_supervisor.sh stop
bash scripts/test_qwen_proxy.sh             # end-to-end endpoint test
bash scripts/test_qwen_concurrency.sh 1 2 4 # concurrency probe
python scripts/test_qwen_tool_api.py        # tool-call smoke test
```

## Logs

`/home/jovyan/work/causal-mind-v2/.qwen-setup/logs/{supervisor,port-forward}.log`

## Token expiry (recurring, human step required)

The runai CLI access token is short-lived (~24 h) and **the refresh token does not
auto-renew in the CLI**. When it expires the supervisor logs
`waiting for Run:ai authentication` and the endpoint goes unhealthy. Re-authentication:

1. On the pod (SSH as jovyan), stage the flow:
   ```bash
   cd /home/jovyan/work/causal-mind-v2
   setsid python3 scripts/runai_login_pty.py > /tmp/runai-pty.out 2>&1 < /dev/null &
   sleep 15
   cat /tmp/runai-login-url.txt     # the URL to open
   ```
2. Open the URL in a browser, complete SSO, copy the displayed code.
3. Deliver the code to the waiting CLI:
   ```bash
   printf '%s\n' "<CODE>" > /tmp/runai-code.txt
   ```
4. `scripts/qwen_tunnel_supervisor.sh status` should return to `QWEN HEALTHY` within
   ~30 s (the supervisor restarts the port-forward automatically).

`scripts/runai_login_pty.py` runs `runai login remote-browser` under a pty, writes the
auth URL to `/tmp/runai-login-url.txt`, and sends the contents of `/tmp/runai-code.txt`
to the CLI as soon as the file appears. It exits when the login process exits (or after
1 h).

Never print or commit the token. It lives only in `/home/jovyan/.runai` (mode 600).
