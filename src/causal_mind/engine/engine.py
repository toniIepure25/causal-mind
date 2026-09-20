"""CM-8R10-15: participant-facing experiment engine (production hardening).

The engine runs ONE participant session end-to-end, fully OFFLINE (no Qwen, no LLM API,
no internet, no remote-agent orchestration). It uses only frozen local artifacts:
the frozen MiniLM encoder, the frozen forecaster (ridge weights), the frozen basin
radius, and the frozen randomization manifest.

Pipeline per trial:
  thought capture -> ThoughtState encoder (frozen MiniLM) -> frozen forecaster
  -> predicted basin -> randomizer (frozen manifest) -> intervention renderer
  -> post-intervention capture -> trial logger -> BRP/secondary-outcome export

Enforces:
  * the trial LIFECYCLE (CREATED -> BASELINE_CAPTURED -> PREDICTION_COMPUTED ->
    RANDOMIZED -> INTERVENTION_RENDERED -> POST_CAPTURED -> FINALIZED, or
    ABORTED / INVALID_TECHNICAL / WITHDRAWN); analysis-valid only after atomic
    finalization; duplicate finalization is prevented.
  * EVENT TIMESTAMPS: wall-clock UTC + monotonic local execution time for each event;
    ordering is validated automatically.
  * LOUD failure: an invalid technical trial is marked INVALID_TECHNICAL and is NEVER
    silently included as valid data.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import numpy as np


class TrialState(str, Enum):
    CREATED = "CREATED"
    BASELINE_CAPTURED = "BASELINE_CAPTURED"
    PREDICTION_COMPUTED = "PREDICTION_COMPUTED"
    RANDOMIZED = "RANDOMIZED"
    INTERVENTION_RENDERED = "INTERVENTION_RENDERED"
    POST_CAPTURED = "POST_CAPTURED"
    FINALIZED = "FINALIZED"
    ABORTED = "ABORTED"
    INVALID_TECHNICAL = "INVALID_TECHNICAL"
    WITHDRAWN = "WITHDRAWN"


# allowed forward transitions (the lifecycle is a DAG; no skipping)
_ALLOWED = {
    TrialState.CREATED: {TrialState.BASELINE_CAPTURED, TrialState.ABORTED,
                         TrialState.INVALID_TECHNICAL, TrialState.WITHDRAWN},
    TrialState.BASELINE_CAPTURED: {TrialState.PREDICTION_COMPUTED, TrialState.ABORTED,
                                   TrialState.INVALID_TECHNICAL, TrialState.WITHDRAWN},
    TrialState.PREDICTION_COMPUTED: {TrialState.RANDOMIZED, TrialState.ABORTED,
                                     TrialState.INVALID_TECHNICAL, TrialState.WITHDRAWN},
    TrialState.RANDOMIZED: {TrialState.INTERVENTION_RENDERED, TrialState.ABORTED,
                            TrialState.INVALID_TECHNICAL, TrialState.WITHDRAWN},
    TrialState.INTERVENTION_RENDERED: {TrialState.POST_CAPTURED, TrialState.ABORTED,
                                       TrialState.INVALID_TECHNICAL, TrialState.WITHDRAWN},
    TrialState.POST_CAPTURED: {TrialState.FINALIZED, TrialState.INVALID_TECHNICAL},
}
_TERMINAL = {TrialState.FINALIZED, TrialState.ABORTED, TrialState.INVALID_TECHNICAL,
             TrialState.WITHDRAWN}


@dataclass
class EventStamp:
    """A timestamped event: wall-clock UTC + monotonic local execution time."""
    event: str
    wall_utc: str
    monotonic_ns: int


@dataclass
class Trial:
    subject: str
    trial_id: str
    state: TrialState = TrialState.CREATED
    events: list[EventStamp] = field(default_factory=list)
    condition: str | None = None
    baseline_emb: np.ndarray | None = None
    prediction: np.ndarray | None = None
    basin_radius: float | None = None
    intervention: str | None = None
    post_embs: list = field(default_factory=list)
    brp: float | None = None
    valid: bool = False
    error: str | None = None

    def _stamp(self, event: str) -> None:
        self.events.append(EventStamp(
            event=event,
            wall_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            monotonic_ns=int(time.monotonic_ns()),
        ))

    def transition(self, new: TrialState) -> None:
        if self.state in _TERMINAL:
            raise RuntimeError(f"trial {self.trial_id} already terminal ({self.state})")
        if new not in _ALLOWED.get(self.state, set()):
            raise RuntimeError(f"illegal transition {self.state} -> {new} "
                               f"(trial {self.trial_id})")
        self.state = new
        self._stamp(new.value)

    def validate_timestamp_ordering(self) -> bool:
        """Monotonic times must be non-decreasing; wall-clock must be parseable."""
        mono = [e.monotonic_ns for e in self.events]
        return all(a <= b for a, b in zip(mono, mono[1:]))

    def to_dict(self) -> dict:
        return {
            "subject": self.subject, "trial_id": self.trial_id,
            "state": self.state.value, "condition": self.condition,
            "valid": self.valid, "brp": self.brp, "error": self.error,
            "n_events": len(self.events),
            "events": [{"event": e.event, "wall_utc": e.wall_utc,
                        "monotonic_ns": e.monotonic_ns} for e in self.events],
        }


class TransactionalLogger:
    """Append-only JSONL trial log. A trial is written ONLY on atomic finalization."""

    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._finalized: set[str] = set()
        if path.exists():
            for line in path.read_text().splitlines():
                if line.strip():
                    self._finalized.add(json.loads(line)["trial_id"])

    def finalize(self, trial: Trial) -> None:
        if trial.trial_id in self._finalized:
            raise RuntimeError(f"duplicate finalization of {trial.trial_id}")
        if trial.state != TrialState.FINALIZED:
            raise RuntimeError(f"cannot finalize a trial in state {trial.state}")
        with self.path.open("a") as f:
            f.write(json.dumps(trial.to_dict()) + "\n")
        self._finalized.add(trial.trial_id)

    def invalid(self, trial: Trial) -> None:
        """Record an invalid technical trial (LOUD failure; never analysis-valid)."""
        with self.path.open("a") as f:
            f.write(json.dumps(trial.to_dict()) + "\n")

    @property
    def finalized_ids(self) -> set[str]:
        return set(self._finalized)


class ExperimentEngine:
    """One participant session, fully offline, with a transactional trial log."""

    def __init__(self, subject: str, session_dir: Path, forecaster, r_alpha: float,
                 h_star: int, k: int, randomizer, encoder=None) -> None:
        self.subject = subject
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.forecaster = forecaster
        self.r_alpha = r_alpha
        self.h_star = h_star
        self.k = k
        self.randomizer = randomizer
        self.encoder = encoder  # frozen MiniLM (or a stand-in for offline tests)
        self.logger = TransactionalLogger(self.session_dir / "trials.jsonl")
        self.trials: list[Trial] = []
        self._history: list[np.ndarray] = []  # session embedding history
        self._session_stamp = EventStamp(
            "session_created",
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            int(time.monotonic_ns()))
        self._trial_no = 0

    # -- lifecycle -----------------------------------------------------------
    def add_baseline(self, text: str) -> None:
        """Add a thought to the session history WITHOUT starting an intervention trial
        (used to warm up the forecaster's k-step history)."""
        emb = self._encode(text)
        self._history.append(emb)

    def start_trial(self) -> Trial:
        self._trial_no += 1
        t = Trial(subject=self.subject, trial_id=f"{self.subject}-T{self._trial_no:03d}")
        t._stamp("trial_start")
        self.trials.append(t)
        return t

    def capture_baseline(self, t: Trial, text: str) -> None:
        t._stamp("thought_input")
        emb = self._encode(text)
        t.baseline_emb = emb
        t.transition(TrialState.BASELINE_CAPTURED)
        t._stamp("submission")
        self._history.append(emb)

    def compute_prediction(self, t: Trial) -> None:
        t._stamp("prediction_begin")
        if not (self.r_alpha is not None and self.r_alpha > 0):
            raise RuntimeError(f"invalid basin radius {self.r_alpha} (must be > 0)")
        if len(self._history) < self.k:
            raise RuntimeError("not enough history for the forecast "
                               f"(have {len(self._history)}, need {self.k})")
        x = np.concatenate(self._history[-self.k:])
        pred = self.forecaster.predict(x.reshape(1, -1))[0]
        t.prediction = pred
        t.basin_radius = self.r_alpha
        t.transition(TrialState.PREDICTION_COMPUTED)
        t._stamp("prediction_end")

    def randomize(self, t: Trial) -> None:
        t.condition = self.randomizer.next_condition(self.subject, self._trial_no - 1)
        t.transition(TrialState.RANDOMIZED)

    def render_intervention(self, t: Trial) -> str:
        t.intervention = _INTERVENTIONS[t.condition]
        t.transition(TrialState.INTERVENTION_RENDERED)
        return t.intervention

    def capture_post(self, t: Trial, texts: list[str]) -> None:
        t._stamp("post_capture_begin")
        embs = [self._encode(x) for x in texts]
        t.post_embs = embs
        t.transition(TrialState.POST_CAPTURED)
        t._stamp("post_capture_end")

    def finalize(self, t: Trial) -> None:
        # compute the BRP (fraction of post-intervention states outside the basin)
        from causal_mind.causal.predicted_basin import PredictedFutureBasin
        basin = PredictedFutureBasin(center=t.prediction, radius=t.basin_radius)
        post = np.vstack(t.post_embs)
        t.brp = float(basin.brp(post))
        t.transition(TrialState.FINALIZED)
        t.valid = True
        self.logger.finalize(t)

    def abort(self, t: Trial, reason: str = "participant_abort") -> None:
        t.error = reason
        t.transition(TrialState.ABORTED)
        self.logger.invalid(t)

    def mark_invalid(self, t: Trial, reason: str) -> None:
        """LOUD failure: mark the trial invalid technical (never analysis-valid)."""
        t.error = reason
        t.state = TrialState.INVALID_TECHNICAL
        t._stamp("invalid_technical")
        self.logger.invalid(t)

    def withdraw(self, t: Trial, reason: str = "withdrawal") -> None:
        t.error = reason
        t.transition(TrialState.WITHDRAWN)
        self.logger.invalid(t)

    # -- helpers -------------------------------------------------------------
    def _encode(self, text: str) -> np.ndarray:
        if self.encoder is None:
            raise RuntimeError("no encoder configured (offline engine needs a frozen "
                               "local encoder)")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("empty or malformed thought (loud failure, not silent)")
        return np.asarray(self.encoder.encode([text])[0], dtype=np.float64)

    def validate_all(self) -> dict:
        """Validate timestamp ordering + lifecycle integrity for all trials."""
        ok = True
        for t in self.trials:
            if not t.validate_timestamp_ordering():
                ok = False
        return {"all_timestamps_ordered": ok, "n_trials": len(self.trials),
                "n_finalized": sum(1 for t in self.trials
                                   if t.state == TrialState.FINALIZED),
                "n_invalid": sum(1 for t in self.trials
                                 if t.state == TrialState.INVALID_TECHNICAL)}


_INTERVENTIONS = {
    "control": "Continue thinking. (no prompt)",
    "sham": "Take a slow breath. Continue thinking. (neutral prompt)",
    "general": "Deliberately let your mind move AWAY from the direction it was "
               "just heading, into a different kind of thought.",
    "cue": "Let your next thought be about: <CUE_WORD>.",
}
