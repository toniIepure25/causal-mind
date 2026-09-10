# ADR-001: Thought event definition

Status: accepted (2026-09-09)

## Context

The unit of analysis must be fixed before modeling. Candidates: (a) word, (b) utterance
sentence, (c) dataset-annotated thought segment, (d) fixed time window.

## Decision

A **thought event** is the dataset-annotated thought segment where annotations exist
(ds006067 provides thought boundaries). Where boundaries are absent, we fall back to
pause-delimited segments with a documented heuristic (pause >= dataset median inter-word
gap x 2, or speaker change), and the fallback is flagged per event.

Rationale: annotations are the only ground-truth alignment with the scientific
construct; fixed windows would mix boundaries and destroy the "next thought" semantics.

## Consequences

- Loader must emit: event id, participant, session, start/end time, text, boundary
  source (annotated|heuristic).
- All "next thought" experiments operate on event order, not frame order.
- Neural samples are linked to events by temporal overlap (documented rule: sample
  assigned to the event covering its mid-point).
