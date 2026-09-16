from pathlib import Path
p = Path("/home/jovyan/work/causal-mind-v2/docs/cm6_candidate_causal_graph.md")
t = p.read_text()
note = ("\n---\n\n**Anti-HARKing / freeze.** The candidate node/edge set, the 7 analyses, "
        "the edge-label taxonomy, the BH-FDR family, and the hypothesis-generating ranking "
        "are frozen as of commit f3348dc (CM-6 baseline). Any change after seeing downstream "
        "experiment outcomes requires a new ADR + research-log entry and must not be used "
        "to retrofit a causal claim.\n")
if "Anti-HARKing / freeze" not in t:
    t = t.rstrip() + "\n" + note
    p.write_text(t)
    print("freeze note appended to cm6_candidate_causal_graph.md")
else:
    print("freeze note already present")
