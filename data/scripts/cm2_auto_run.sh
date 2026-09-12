#!/bin/bash
cd /home/jovyan/work/causal-mind-v2
export HF_HOME=/home/jovyan/work/.hf-home TRANSFORMERS_CACHE=/home/jovyan/work/.hf-home
export PYTHONPATH=src
MIN=100
for i in $(seq 1 150); do
  n=$(ls data/raw/ds006067/sub-*/func/*_events.tsv 2>/dev/null | wc -l)
  if [ "$n" -ge "$MIN" ]; then
    echo "[$(date -u +%H:%M:%S)] enough data ($n subjects); running full evaluation"
    .venv/bin/python data/scripts/run_full_evaluation.py
    echo "[$(date -u +%H:%M:%S)] evaluation exit=$?"
    break
  fi
  sleep 120
done
echo "[$(date -u +%H:%M:%S)] auto-run loop ended (n=$(ls data/raw/ds006067/sub-*/func/*_events.tsv 2>/dev/null | wc -l))"
