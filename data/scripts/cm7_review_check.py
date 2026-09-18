import json, numpy as np, collections, math
r = json.load(open("/home/jovyan/work/causal-mind-v2/reports/cm7_results.json"))
d = np.array(r["primary_ate"]["per_list_contrasts"])
ate = r["primary_ate"]["ate"]
print("n lists:", len(d), "mean(d):", d.mean(), "reported ate:", ate)
# EXACT 2-phase randomization null: each list's contrast gets a random sign
# (the actual randomization is only the two alternating phases {1,3,5}/{2,4,6})
rng = np.random.default_rng(1)
B = 400000
s = rng.choice(np.array([-1.0, 1.0]), size=(B, len(d)))
perm = (s * d).mean(axis=1)
p2 = float(np.mean(np.abs(perm) >= abs(ate)))
print("2-phase null mean:", perm.mean(), "sd:", perm.std())
print("EXACT 2-phase p-value (MC B=400k):", p2)
# analytic 2-phase null sd: sqrt(sum(d^2))/n
print("analytic 2-phase null sd:", math.sqrt((d**2).sum())/len(d))
c = collections.Counter(np.round(d, 3))
print("contrast value counts:", dict(sorted(c.items())))
# phase decomposition cross-check
so, soff, no, noff = -0.08256880733944955, 0.006230529595015571, 109, 107
print("ATE from phases:", (no*so + noff*soff)/(no+noff))
print("delta=(so+soff)/2:", (so+soff)/2, " position=(so-soff)/2:", (so-soff)/2)
print("imbalance term (A-B)*(no-noff)/N:", ((so-soff)/2)*(no-noff)/(no+noff))
sl = r["primary_ate"]["subject_level"]
print("subject-level ate:", sl["ate"], "ci:", sl["ci_boot"])
lps = r["integrity"]["lists_per_session"]
tot = sum(lps.values())
print("total lists:", tot, "observed enc:", r["counts"]["enc_stim_lists"],
      "expected if 40%:", 0.4*tot, "binom sd:", math.sqrt(tot*0.4*0.6))
