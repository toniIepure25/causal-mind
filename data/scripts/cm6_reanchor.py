from pathlib import Path
ROOT = Path("/home/jovyan/work/causal-mind-v2/docs")
HASH = "f3348dc"
files = [
    "cm6_candidate_causal_graph.md",
    "cm6_identification_assumptions.md",
    "cm6_break_the_chain_protocol.md",
    "cm6_oracle_readiness.md",
    "datasets/cm6_intervention_dataset_audit.md",
]
for rel in files:
    p = ROOT / rel
    if not p.exists():
        print("skip (missing):", rel); continue
    t = p.read_text()
    n = t.count("frozen as of this commit")
    if n:
        t = t.replace("frozen as of this commit", f"frozen as of commit {HASH} (CM-6 baseline)")
        p.write_text(t)
        print(f"{rel}: re-anchored {n} freeze note(s) to {HASH}")
    else:
        print(f"{rel}: no 'frozen as of this commit' phrase")
