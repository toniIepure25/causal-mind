#!/usr/bin/env python3
"""Update current_state.md stage/heading/next sections for the CM-5 null."""
from pathlib import Path
cs = Path("/home/jovyan/work/causal-mind-v2/docs/current_state.md")
t = cs.read_text()

t = t.replace(
    "Phase 2: CM-1 (data), CM-2 (non-neural next-thought prediction), and CM-3\n"
    "(multi-step cognitive futures / Thought Predictive Horizon) complete and pushed.\n"
    "CM-5 (neural) in progress: data-independent pipeline complete, real-data N=2\n"
    "smoke complete, MRI-eligible cohort definition starting (metadata-first audit\n"
    "of all 118 subjects).",
    "Phase 2: CM-1 (data), CM-2 (non-neural next-thought prediction), CM-3\n"
    "(multi-step cognitive futures / Thought Predictive Horizon), and CM-5 (neural)\n"
    "complete and pushed. CM-5 decisive result: a clean NULL — HRF-safe BOLD\n"
    "contains no incremental prospective value for future thought beyond the\n"
    "frozen behavioral-history model + motion/speech confounds (h=1,3,5,10;\n"
    "N1-N3 ladder; red-team GO).",
)
t = t.replace(
    "## CM-5 (neural) — in progress, real-data smoke complete",
    "## CM-5 (neural) — COMPLETE: clean NULL (no incremental neural value)",
)
t = t.replace(
    "- **Next (authorized):** define the MRI-eligible cohort WITHOUT inspecting",
    "- **Decisive result (2026-09-14):** MRI-eligible cohort (106 subjects,\n"
    "  73/17/16 after F2 tSNR + alignment gates) acquired (87.5 GB BOLD,\n"
    "  hash-verified). IncrementalNeuralGain (M4-M2) negative at every horizon\n"
    "  (primary N2: -0.088/-0.085/-0.085/-0.090, CIs exclude 0, 0/16 positive);\n"
    "  N1~0/N3~-0.016/N2~-0.085 ladder; NC4->0; controls confirm no shortcut.\n"
    "  CM5_NULL_NO_INCREMENTAL_NEURAL_VALUE (claim C-005, L5 negative).\n"
    "- **Prior next (done):** define the MRI-eligible cohort WITHOUT inspecting",
)
cs.write_text(t)
print("current_state.md stage/heading/next updated")
