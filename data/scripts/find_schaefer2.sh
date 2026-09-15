#!/bin/bash
set -e
cd /home/jovyan/work/causal-mind-v2/data/atlases
echo "=== search OSF for Schaefer 2018 ==="
curl -s "https://api.osf.io/v2/nodes/?search=Schaefer%202018%20atlas&per_page=5" -o search.json
python3 - <<'PY'
import json
d = json.load(open("search.json"))
for n in d.get("data", []):
    a = n["attributes"]
    print(a["id"], "|", a["title"], "|", a.get("description","")[:80])
PY
echo "=== try 23y5u follow ==="
curl -sIL https://osf.io/23y5u/download 2>&1 | grep -iE "^location|^HTTP|content-length" | head -12
