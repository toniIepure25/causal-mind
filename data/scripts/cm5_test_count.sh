#!/bin/bash
cd /home/jovyan/work/causal-mind-v2
export HF_HOME=/home/jovyan/work/.hf-home
.venv/bin/python -m pytest -q -p no:warnings 2>&1 | tail -2
