# CM-2 Literature Audit — Next-Thought / Spontaneous-Thought Forecasting

Author: orchestrator (the `researcher` agent stalled on `repeated_command` after 18
cycles of exploration without producing a deliverable; this note was written directly
by the orchestrator from domain knowledge). Scope: closest literature + defensible
metrics + baseline-taxonomy cross-check. **No CM-2 held-out results were consulted.**

## 1. The question in context

"Can the next thought state be predicted from preceding thought states above strong
trivial, semantic, and participant-history baselines under strict subject-disjoint
prospective evaluation?" This sits at the intersection of:

* **Spontaneous / mind-wandering thought.** The study of task-unrelated,
  self-generated thought (Smallwood & Schooler 2015; Christoff et al. 2016). Most work
  characterizes the *distribution* of thought content (task-unrelated vs task-related,
  past/future/present orientation); very little treats it as a *sequential prediction*
  problem.
* **Stream-of-consciousness / inner speech.** Verbal inner experience sampled
  continuously (the ds006067 paradigm: continuous verbal report during resting fMRI).
* **Semantic decoding of mental content from neural signals.** Huth et al. 2016 and
  Caucheteux & King 2014 showed semantic content can be decoded from fMRI in a shared
  embedding space. That motivates using a frozen semantic embedding as the thought-state
  representation here — but CM-2 deliberately does NOT use fMRI; it establishes the
  non-neural (text-only) predictive ceiling first.
* **Sequence / language prediction as the methodological template.** Next-token
  prediction (n-gram: Brown et al. 1992; neural LM: Bengio et al. 2003) is the closest
  analog: predict the next unit from history, judged against strong baselines (uniform,
  unigram, bigram, retrieval). Our B0-B7 map directly onto that baseline ladder.

## 2. What is genuinely novel / at risk

The key scientific risk is **triviality**: spontaneous thought has strong *semantic
inertia* (the next thought is often topically continuous with the current one). A naive
"predict next = current" (B1/B4) may already capture most of the signal. The main model
must therefore beat **semantic persistence (B4)** and **semantic nearest-neighbour
transition (B5)** — not just chance (B0). This is the same lesson as language modeling:
unigram/persistence baselines are strong, and n-gram/retrieval baselines capture most of
the "continuity"; a model earns its keep only by learning *transition structure* beyond
persistence.

## 3. Defensible metrics (proposed, pre-results)

For the **semantic** target (next thought's frozen embedding):
* **Cosine similarity** predicted vs actual (primary, continuous).
* **Retrieval / ranking**: rank the true next thought among a candidate pool of valid
  next-thoughts; report mean rank and top-1/top-5 hit rate (robust to embedding scale).
* **Latent-space distance**: distance in the ThoughtState embedding space (equivalent
  view of cosine).

For the **categorical** target (coarse topic, model-inferred via train-fit clustering):
* **Accuracy** and **log-loss / calibration** (reliability of the predicted
  distribution, not just the argmax).

For **uncertainty**: subject-level bootstrap CIs; a **permutation null** that pairs each
history with a random target (preserves marginals, destroys temporal correspondence);
effect sizes (delta over the strongest baseline, not just over chance).

These are standard for sequence prediction and are chosen *before* seeing results, so
they cannot be tuned to flatter a particular model.

## 4. Baseline taxonomy cross-check (B0-B7)

| ID | Baseline | LM analog | Role |
|----|----------|-----------|------|
| B0 | marginal (global prior) | uniform / unigram prior | chance floor |
| B1 | previous state (T_t only) | unigram persistence | semantic inertia |
| B2 | Markov P(T_{t+1}\|T_t) | bigram | 1-step transition |
| B3 | n-gram P(T_{t+1}\|T_{t-1},T_t) | trigram | multi-history transition |
| B4 | semantic persistence | smoothed unigram | strong continuity |
| B5 | semantic NN transition | retrieval / k-NN | **the strong bar** |
| B6 | participant-history | subject-specific prior | within-subject structure |
| B7 | frozen history retrieval | n-gram retrieval over corpus | history-based, no training |

The ladder is monotone in "how much structure it uses," and B5/B7 are the baselines a
real model must beat. This matches the LM literature's insistence that retrieval and
persistence baselines are the honest bar.

## 5. Threats the literature flags (feed to CM-2G red-team)

* **Semantic-embedding leakage**: if the encoder saw test text during (pre)training, the
  "semantic" metric is inflated. Mitigation: frozen pretrained encoder, no fine-tuning on
  any CM-2 text.
* **Topic-label circularity**: if categories are derived from the same embedding being
  predicted, categorical accuracy is a coarser view of semantic accuracy, not independent
  evidence. Mitigation: label categories as model-inferred/derived, fit clustering on
  train only.
* **Temporal adjacency artifacts**: consecutive thoughts share context; a model may
  exploit near-duplicate utterances. Mitigation: duplicate/near-duplicate screen in the
  red-team.
* **Participant leakage**: any transform fit on all subjects (e.g., a global
  normalizer) can leak test-subject information. Mitigation: fit all transforms on train
  only; subject-disjoint split.

## 6. Bottom line

The framing is sound and the baseline ladder is the right honest bar. The decisive
question is whether learned *transition structure* (beyond persistence B4 and retrieval
B5) survives subject-disjoint prospective evaluation. That is exactly what CM-2D/E/F
test.

### References (core, well-established)
- Smallwood & Schooler (2015). The many faces of mind-wandering. *TICS*.
- Christoff et al. (2016). Spontaneous thought: brain networks and implications. *Annu Rev Neurosci*.
- Huth et al. (2016). Natural speech is the key to aligning the brain's semantic networks. *eLife*.
- Caucheteux & King (2014). Graded representation of word categories in the human brain. *Cereb Cortex*.
- Brown et al. (1992). The class-based *n*-gram language model. *SLP*.
- Bengio et al. (2003). A neural probabilistic language model. *JMLR*.
- Su et al. (2025). Neural dynamics of spontaneous memory recall and future thinking in the continuous flow of thoughts. *Nat Commun* (the ds006067 source).
