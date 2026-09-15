#!/bin/bash
set -e
cd /home/jovyan/work/causal-mind-v2/data/atlases
echo "=== OSF node 865t3 files ==="
curl -s "https://api.osf.io/v2/nodes/865t3/files/osfstorage/?per_page=100" -o files.json
wc -c files.json
python3 - <<'PY'
import json
try:
    d = json.load(open("files.json"))
except Exception as e:
    print("parse error", e)
    print(open("files.json").read()[:200])
    raise SystemExit
for f in d.get("data", []):
    a = f["attributes"]
    print(f["id"], "|", a["name"], "|", a.get("size"))
PY
