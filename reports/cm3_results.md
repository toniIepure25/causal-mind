# CM-3 — MULTI-STEP COGNITIVE FUTURES (auto-generated)

subjects=118 split={'train': 83, 'val': 18, 'test': 17} seal=675052618750ea7f... k=3

## Future Predictability Curve (semantic; gain = model - strongest baseline)
- h= 1: model 0.3623 [0.3523, 0.3720] vs B4_drift 0.3274 [0.3131, 0.3418] -> gain +0.0349 [+0.0253,+0.0445]
- h= 2: model 0.3406 [0.3316, 0.3499] vs B0_marginal_future 0.3146 [0.3052, 0.3233] -> gain +0.0261 [+0.0205,+0.0321]
- h= 3: model 0.3285 [0.3188, 0.3385] vs B0_marginal_future 0.3133 [0.3041, 0.3221] -> gain +0.0152 [+0.0091,+0.0220]
- h= 4: model 0.3236 [0.3145, 0.3330] vs B0_marginal_future 0.3122 [0.3032, 0.3208] -> gain +0.0114 [+0.0070,+0.0165]
- h= 5: model 0.3210 [0.3118, 0.3299] vs B0_marginal_future 0.3117 [0.3023, 0.3206] -> gain +0.0092 [+0.0053,+0.0133]
- h= 6: model 0.3187 [0.3093, 0.3282] vs B0_marginal_future 0.3114 [0.3027, 0.3199] -> gain +0.0073 [+0.0032,+0.0113]
- h= 8: model 0.3153 [0.3046, 0.3250] vs B0_marginal_future 0.3101 [0.3008, 0.3187] -> gain +0.0052 [+0.0018,+0.0085]
- h=10: model 0.3135 [0.3011, 0.3249] vs B0_marginal_future 0.3091 [0.2971, 0.3197] -> gain +0.0044 [+0.0015,+0.0072]

## Thought Predictive Horizon (semantic): {'tph': 10, 'rule': 'max h with gain>0 and 95% CI lower bound > 0'}

## History-depth x horizon (model semantic, test)
- k=1: h=1:0.3531  h=2:0.3371  h=3:0.326  h=4:0.3231  h=5:0.3195
- k=2: h=1:0.3617  h=2:0.3406  h=3:0.3286  h=4:0.3244  h=5:0.32
- k=3: h=1:0.3623  h=2:0.3406  h=3:0.3285  h=4:0.3236  h=5:0.321
- k=5: h=1:0.3597  h=2:0.3379  h=3:0.3276  h=4:0.3234  h=5:0.3198

## Time horizons (semantic)
- dt=30s: model 0.3264 [0.3123, 0.3406] vs B0 0.3120 [0.2964, 0.3276]
- dt=60s: model 0.3185 [0.3051, 0.3338] vs B0 0.3133 [0.3001, 0.3276]
- dt=120s: model 0.3056 [0.2931, 0.3185] vs B0 0.3043 [0.2918, 0.3183]
- dt=180s: model 0.3093 [0.2974, 0.3229] vs B0 0.3096 [0.2967, 0.3245]

## Topic / category (persistence-nearest)
- h=1: category 0.2370 [0.2017, 0.2708]  topic 0.0437 [0.0250, 0.0646]
- h=2: category 0.1919 [0.1577, 0.2262]  topic 0.0342 [0.0175, 0.0530]
- h=3: category 0.1488 [0.1237, 0.1764]  topic 0.0209 [0.0075, 0.0350]
- h=4: category 0.1533 [0.1300, 0.1821]  topic 0.0147 [0.0068, 0.0234]
- h=5: category 0.1354 [0.1024, 0.1745]  topic 0.0115 [0.0033, 0.0217]

## Nulls: {'h': 3, 'observed': 0.3285, 'time_shuffled': {'null_mean': 0.3231, 'p': 0.0}, 'transition_destroyed': {'null_mean': 0.3246, 'p': 0.0}}

## Entropy / branching (mean future cosine): {'h=1': {'mean_future_cosine': 0.169}, 'h=2': {'mean_future_cosine': 0.17}, 'h=3': {'mean_future_cosine': 0.1705}, 'h=5': {'mean_future_cosine': 0.1665}}
