# CAUSAL MIND — 10-Minute Pitch (spoken)

A script for a 10-minute conversation with the supervisor. Adjust to your voice. The
goal: (1) convey what the project is, (2) show it is complete and honest up to the human
step, (3) get the three decisions.

---

**[0:00–1:00] The question.**
"The project asks two linked questions about the human thought stream. First: can we
*predict* the future of a person's thoughts from their recent past — the next thought, and
thoughts several steps ahead? Second: can a *prediction-conditioned intervention* actually
*change* that future, in a way we can estimate causally? That second question is the one
no public dataset can answer, so it needs a small, careful experiment."

**[1:00–3:00] What I've built, and that it's real.**
"Everything so far is on *public* data and *synthetic* worlds — I have not collected any
human data. On a public corpus of 1,100-plus thought diaries from 118 people, a simple
linear model over a short window of thought embeddings predicts the *next* thought's
meaning above every baseline, and it predicts *future* thoughts at every horizon up to ten
thoughts ahead, with the advantage decaying smoothly — the signature of a real, finite
signal. I also ran the neural version: fMRI adds *nothing* for predicting thought content.
That's a clean null, and I'm reporting it as a null, not hiding it. And the observational
thought dynamics turn out to be *not* causally identifiable — zero of eighty-four edges —
which is exactly why the confirmatory step has to be a *randomized* experiment, not an
observational one."

**[3:00–5:00] The method is validated.**
"Before I ask you to support a human experiment, I validated the causal machinery on an
*independent* public dataset — a hippocampal-stimulation memory study. The framework
correctly identified and estimated a randomized causal effect there. The specific effect
was a small null, but the *method* is the result: it doesn't hallucinate effects, the
leakage audit passes, and the destructive controls sit at zero. So the instrument is
trusted before I point it at the real question."

**[5:00–7:00] The experiment, and that it's ready.**
"The confirmatory experiment is a within-subject, randomized, four-condition test —
control, sham, a general redirect, and a specific cue — measuring whether the observed
future leaves the predictor's predicted basin. Twenty people, twenty-four trials. And I
have hardened everything that can be hardened *without* humans: the forecaster is frozen
and reproducible — a clean-room re-fit is bit-for-bit identical — the realtime engine runs
the whole trial offline with no LLM in the loop, the randomization is audited, and privacy
is hardened so no raw thought text ever leaves the machine. Ten out of ten pre-human gates
pass. This is a formal freeze, tagged and hash-verified."

**[7:00–9:00] What I need from you.**
"So the only things left are three external approvals. One: your sign-off on the frozen
protocol. Two: the ethics submission to the University of Vienna — the package is ready,
and the deadline is the fifth of October for the fifth of November meeting; for a Master's
thesis you or the study-law body submit, I prepare. Three: authorization for a small,
gated pilot before the confirmatory run. If those clear, I run the experiment; a positive
or a null is a result either way."

**[9:00–10:00] The honest frame.**
"I want to be clear about what I'm *not* claiming: no free-will claim, no causal claim
from the observational data, and the prediction effects are modest with a small test set.
What I *am* offering is a complete, reproducible, honest body of work — positive and
negative results both — and, if you support it, the first test of whether a predicted
thought can be voluntarily redirected. Here are the thesis options and the specific
questions I need answered."

---

*Supporting slides (optional): the one-pager, the master summary, the freeze, and the
thesis options.*
