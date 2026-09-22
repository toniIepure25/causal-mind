# CM-XVAL-2 — Candidate audit: van Halem (openESM 0070) — `INCOMPATIBLE_DATASET`

**Decision: `INCOMPATIBLE_DATASET`** (second external-validation candidate; no new claim)

## Candidate
- **van Halem** (openESM `0070`), Zenodo DOI `10.5281/zenodo.17348032`, CC BY-NC 4.0.
- 82 participants, 5 days, random + skin-conductance triggers. Free-text field `event_day`
  ("Daily event").

## Why it is incompatible with the CM-3 transfer protocol
Two verifiable, protocol-level blockers (data: `0070_vanhalem_ts.tsv`, 4248 rows):

1. **Too sparse for multi-horizon prediction.** `event_day` fill rate is **8.2%** (348/4248
   non-empty); median **4** entries per participant (max 5). The CM-3 protocol needs a k=3
   history window plus a future horizon h (up to 10). With ~4 entries per person there are
   almost no valid (history -> target) samples at h>=2, so the horizon-prediction protocol
   cannot be run.
2. **Language mismatch with the frozen encoder.** The `event_day` text is **Dutch**
   (e.g., "Huis schoonmaken", "Ik was op school"). The frozen semantic encoder is
   all-MiniLM-L6-v2 (English). Embedding Dutch text with an English encoder does not yield
   meaningful semantic vectors, so the "semantic cosine" metric would be confounded by the
   language mismatch rather than measuring temporal semantic persistence.

## Consequence
- No XVAL-2 result is reported (running it would be confounded, not a clean test).
- The XVAL program's first **compatible** external validation remains **CM-XVAL-1 (Open
  Play) = `CMXVAL_PARTIAL`** (claim C-101).
- Within openESM, these are the only two datasets with genuine free-text variables (a strict
  `variable_type == "freetext"` scan of all 62 openESM datasets found exactly 3 free-text
  variables across these 2 datasets). A compatible second domain would need a non-openESM
  source with (a) >=20 subjects, (b) >=20 well-filled sequential free-text entries per
  subject, and (c) text in the encoder's language (English).

## Reproduction
```
# data: https://zenodo.org/api/records/22809896/files/0070_vanhalem_ts.tsv/content
# inspect fill rate + language:
.venv/bin/python -c "import pandas as pd; df=pd.read_csv('.../vanhalem_ts.tsv',sep='\t'); \
  s=df['event_day'].astype('string').str.strip(); \
  print((s.str.len()>0).mean(), df['id'].nunique())"
```
