# CM-2 — THOUGHT STATE + NEXT (auto-generated results)

subjects=118 thoughts=6436 split={'train': 83, 'val': 18, 'test': 17} seal=675052618750ea7f... encoder=all-MiniLM-L6-v2

## Baselines (test, k=1)
- B0_marginal: semantic 0.3167 [0.3078, 0.3250], category 0.1464 [0.0820, 0.2164]
- B1_previous_state: semantic 0.2717 [0.2550, 0.2883], category 0.2566 [0.2163, 0.2947]
- B2_markov: semantic 0.3265 [0.3149, 0.3381], category 0.2566 [0.2163, 0.2947]
- B3_ngram: semantic 0.3265 [0.3149, 0.3381], category 0.2566 [0.2163, 0.2947]
- B4_semantic_persistence: semantic 0.2796 [0.2630, 0.2961], category 0.2566 [0.2163, 0.2947]
- B5_semantic_nn: semantic 0.2972 [0.2871, 0.3078], category 0.2257 [0.1878, 0.2640]
- B6_participant_history: semantic 0.2717 [0.2550, 0.2883], category 0.2566 [0.2163, 0.2947]
- B7_history_retrieval: semantic 0.2564 [0.2462, 0.2674], category 0.2566 [0.2163, 0.2947]

## Main model: linear_transition k=3 alpha=100.0 (val 0.3493)
- test semantic: 0.3623 [0.3523, 0.3720]

## Analyses
- A1 immediate: B0 0.3167 [0.3078, 0.3250] vs B1 0.2717 [0.2550, 0.2883] (delta -0.0449 [-0.0623, -0.0279])
- A2 added history: {'k=1': (0.3531256519296309, 0.3445108846056486, 0.36137919135981067), 'k=3': (0.3622699766765176, 0.35229362084905663, 0.37204926792238624)}
- A3 semantic vs categorical: {'semantic_cosine': (0.3622699766765176, 0.35229362084905663, 0.37204926792238624), 'category_accuracy': (nan, nan, nan)}
- A4 cross-subject: n=17 mean_ci=0.3623 [0.3523, 0.3720]
- A5 history depth: {1: (0.3531256519296309, 0.3445108846056486, 0.36137919135981067), 2: (0.3617230342898688, 0.35240327456661, 0.37020877658222245), 3: (0.3622699766765176, 0.35229362084905663, 0.37204926792238624), 5: (0.35973605336606973, 0.34986001435542763, 0.3701236078004464), 8: (0.3551283809514564, 0.34489214399248136, 0.365666517890589)}
- A6 permutation null: observed=0.3635 null_mean=0.2958 p=0.0000
