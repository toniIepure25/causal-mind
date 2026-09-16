import numpy as np, pandas as pd, glob, os
os.chdir("/home/jovyan/work/causal-mind-v2")
EMB = "data/embeddings/all-MiniLM-L6-v2"
DIMS = ["joy","anxiety","emotional_intensity","fear","sadness"]

def lag1_r2(x):
    # pooled OLS R2 of x[t+1] ~ x[t]
    y = x[1:]; X = x[:-1]
    Xb = np.column_stack([np.ones_like(X), X])
    beta, *_ = np.linalg.lstsq(Xb, y, rcond=None)
    pred = Xb @ beta
    ss_res = ((y-pred)**2).sum(); ss_tot = ((y-y.mean())**2).sum()
    return 1 - ss_res/ss_tot

def within_subject_r2(vals_by_sub):
    # demean each subject, then pooled lag1 R2
    ys, Xs = [], []
    for v in vals_by_sub:
        v = v - v.mean()
        ys.append(v[1:]); Xs.append(v[:-1])
    y = np.concatenate(ys); X = np.concatenate(Xs)
    Xb = np.column_stack([np.ones_like(X), X])
    beta, *_ = np.linalg.lstsq(Xb, y, rcond=None)
    pred = Xb @ beta
    return 1 - ((y-pred)**2).sum()/((y-y.mean())**2).sum()

def subject_mean_only_r2(vals_by_sub):
    # predict x[t+1] from the subject's own mean only
    ss_res = 0.0; ss_tot = 0.0
    for v in vals_by_sub:
        m = v.mean()
        y = v[1:]
        ss_res += ((y-m)**2).sum(); ss_tot += ((y-y.mean())**2).sum()
    return 1 - ss_res/ss_tot

def eta_squared(vals_by_sub):
    allv = np.concatenate(vals_by_sub)
    grand = allv.mean()
    ss_between = sum(len(v)*(v.mean()-grand)**2 for v in vals_by_sub)
    ss_total = ((allv-grand)**2).sum()
    return ss_between/ss_total

for dim in DIMS:
    subs = []
    for f in sorted(glob.glob("data/derived/thought_events/sub-*_thoughts.tsv")):
        df = pd.read_csv(f, sep="\t")
        v = df[dim].astype(float).values
        if v.std() > 1e-8:
            subs.append(v)
    pooled = lag1_r2(np.concatenate(subs))
    within = within_subject_r2(subs)
    meanonly = subject_mean_only_r2(subs)
    eta = eta_squared(subs)
    floor = np.mean(np.concatenate(subs) <= np.concatenate(subs).min()+1e-9)
    print(f"{dim:20s} pooled={pooled:.3f} within={within:.3f} meanonly={meanonly:.3f} eta2={eta:.3f} floorfrac={floor:.2f} nsub={len(subs)}")

# verify duration->gap partial r (contemporaneous conditioning on other dims at t)
print("\n=== duration->gap and top CI edges (contemporaneous conditioning) ===")
allrows = []
for f in sorted(glob.glob("data/derived/thought_events/sub-*_thoughts.tsv")):
    df = pd.read_csv(f, sep="\t")
    allrows.append(df)
big = pd.concat(allrows, ignore_index=True)
cont = ["duration","gap","n_words","joy","anxiety","emotional_intensity","fear","sadness","vision"]
# partial corr duration_t -> gap_{t+1} given other cont dims at t
def partial_r(x, y, Z):
    def resid(a, Z):
        Zb = np.column_stack([np.ones(len(Z)), Z])
        b, *_ = np.linalg.lstsq(Zb, a, rcond=None)
        return a - Zb@b
    rx = resid(x, Z); ry = resid(y, Z)
    return np.corrcoef(rx, ry)[0,1]
for src, dst in [("duration","gap"),("gap","duration"),("duration","n_words"),("n_words","duration")]:
    x = big[src].astype(float).values[:-1]
    y = big[dst].astype(float).values[1:]
    Z = big[[c for c in cont if c not in (src,dst)]].astype(float).values[:-1]
    Z = np.nan_to_num(Z)
    print(f"  {src}_t -> {dst}_t1  partial_r={partial_r(x,y,Z):.3f}")

# count candidate_mediator=true in results
import json
a = json.load(open("reports/cm6_observational_results.json"))
med = a["analysis_6_mediator_moderator"]
nt = sum(1 for m in med if m.get("candidate_mediator"))
print(f"\nmediator triples total={len(med)} candidate_mediator_true={nt}")
for m in med:
    if m.get("candidate_mediator"):
        print(f"  {m['antecedent']} -> {m['mediator']} -> {m['target']}")
