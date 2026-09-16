"""Add Benjamini-Hochberg FDR q-values to the CM-6A results (post-hoc on the p-value
families) and record a multiplicity note. Writes reports/cm6_observational_results.json."""
import json, os
import numpy as np
os.chdir("/home/jovyan/work/causal-mind-v2")
P = "reports/cm6_observational_results.json"
a = json.load(open(P))

def bh_qvalues(p):
    p = np.asarray(p, dtype=float)
    m = len(p)
    order = np.argsort(p)
    ranked = p[order]
    ranks = np.arange(1, m + 1)
    thresh = (ranks / m) * 0.05
    # largest rank i where p_(i) <= (i/m)*q
    below = ranked <= thresh
    if not below.any():
        return np.ones(m), 0
    k = int(np.max(np.where(below)[0])) + 1
    # q-values: min over j>=i of (m/j)*p_(j), enforce monotonicity
    q_ranked = (m / ranks) * ranked
    q_ranked = np.minimum.accumulate(q_ranked[::-1])[::-1]
    q_ranked = np.clip(q_ranked, 0, 1)
    q = np.empty(m)
    q[order] = q_ranked
    return q, k

# CI family (272 pairs): use p
ci = a["analysis_2_ci_structure"]
p_ci = np.array([e["p"] for e in ci])
q_ci, k_ci = bh_qvalues(p_ci)
for e, qv in zip(ci, q_ci):
    e["q_fdr"] = float(qv)
    e["fdr_significant"] = bool(qv < 0.05)
n_ci_fdr = int(sum(1 for e in ci if e["fdr_significant"]))

# mediator family (126 triples): use the max of the three path p-values (conservative)
med = a["analysis_6_mediator_moderator"]
p_med = np.array([max(m["p_a_m"], m["p_m_b_given_a"], m["p_a_b"]) for m in med])
q_med, k_med = bh_qvalues(p_med)
for m, qv in zip(med, q_med):
    m["q_fdr"] = float(qv)
    m["fdr_significant"] = bool(qv < 0.05)
n_med_fdr = int(sum(1 for m in med if m["fdr_significant"]))

a["multiplicity"] = {
    "method": "Benjamini-Hochberg (1995), q=0.05, applied post-hoc to the p-value families",
    "ci_family_n": len(ci),
    "ci_fdr_significant": n_ci_fdr,
    "mediator_family_n": len(med),
    "mediator_fdr_significant": n_med_fdr,
    "note": ("The 272-pair CI family and 126-triple mediator family are large; unadjusted "
             "alpha=0.05 yields ~13.6 expected false positives in the CI family. The "
             "composite candidate ranking uses arbitrary weights and is HYPOTHESIS-GENERATING, "
             "not confirmatory."),
}
json.dump(a, open(P, "w"), indent=1)
print(f"CI family: {len(ci)} pairs, {n_ci_fdr} FDR-significant (q<0.05)")
print(f"Mediator family: {len(med)} triples, {n_med_fdr} FDR-significant (q<0.05)")
print("top FDR-surviving CI edges:")
for e in sorted(ci, key=lambda x: x["q_fdr"])[:6]:
    print(f"  {e['src']}_t -> {e['dst']}_t1  r={e['r_partial']:.3f} p={e['p']:.1e} q={e['q_fdr']:.2e}")
