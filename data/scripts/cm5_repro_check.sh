#!/bin/bash
cd /home/jovyan/work/causal-mind-v2
export HF_HOME=/home/jovyan/work/.hf-home
.venv/bin/python -m pytest -q 2>&1 | tail -3
echo "=== synthetic end-to-end ==="
.venv/bin/python data/scripts/run_cm5_evaluation.py --synthetic --out /tmp/cm5_synth.json 2>&1 | tail -3
