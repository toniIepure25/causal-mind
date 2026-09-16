import json, os
os.chdir("/home/jovyan/work/causal-mind-v2")
a = json.load(open("reports/cm6_observational_results.json"))
# top CI edges by |r_partial|
ci = a["analysis_2_ci_structure"]
ci_sorted = sorted(ci, key=lambda e: abs(e["r_partial"]), reverse=True)
print("=== top 8 CI edges by |r_partial| ===")
for e in ci_sorted[:8]:
    print(f"  {e['src']}_t -> {e['dst']}_t1  r_partial={e['r_partial']:.3f} p={e['p']:.2e} dep={e['conditionally_dependent']}")
# top incremental
inc = a["analysis_3_incremental_value"]
inc_sorted = sorted(inc, key=lambda e: abs(e["incremental_r2"]), reverse=True)
print("=== top 6 incremental R2 ===")
for e in inc_sorted[:6]:
    print(f"  {e['src']}_t -> {e['dst']}_t1  incr_r2={e['incremental_r2']:.4f}")
# mediators
med = a["analysis_6_mediator_moderator"]
nt = [m for m in med if m.get("candidate_mediator")]
print(f"=== mediators: total={len(med)} true={len(nt)} ===")
for m in nt:
    print(f"  {m['antecedent']} -> {m['mediator']} -> {m['target']}")
# n CI pairs
print(f"\nn CI pairs tested: {len(ci)}; n incremental pairs: {len(inc)}")
