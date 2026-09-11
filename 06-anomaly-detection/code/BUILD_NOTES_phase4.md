# Build notes — Phase 4 analysis notebook (`notebooks/anomaly_detection_analysis.ipynb`)

Built from a main-loop outline (§1–§8, mirroring `design/design.md`'s own section
numbering loosely) against the Phase-3-complete state: `data/*.csv`,
`data/answer_key/anomalies.csv`, `data/analysis/{rule_flags,detector_flags,
detector_scores}.csv`, `clusters.json`, `evaluation.json`, `evaluation_scores.csv`,
`agent_runs/run_0{1,2,3}_findings.json`, and the adjudicated `data/analysis/report.md`.
Nothing under `code/`, `data/` or `design/` was modified — the notebook only reads
those trees. Executed via
`python -m nbconvert --to notebook --execute --inplace notebooks/anomaly_detection_analysis.ipynb`
twice from a clean kernel each time; both runs exit 0 with zero error outputs across
all 20 code cells.

## 1. What every headline number is actually read from

No result literal is typed into the notebook by hand and left unchecked. The nine
figures the brief called out as hard requirements are each a live `assert` against a
value read from disk at execution time, not from memory of this exploration:

| Assertion | Source read live |
|---|---|
| 50,000 ledger rows | `data/gl_transactions.csv`, cross-checked against `config.TOTAL_TRANSACTIONS` |
| 64 rule flags, no double-trip | recomputed by importing `code/rule_tests.py` and running it on the public CSVs inside the notebook, byte-compared to `data/analysis/rule_flags.csv` |
| Rule precision 48/64 | the same recomputation, joined against the answer key |
| 200 detector flags | `data/analysis/detector_flags.csv` |
| Zero detector–key overlap | `detector_flags.csv` ∩ (the full 105-row expanded answer key) |
| Units correct 37/35/38 | `data/analysis/evaluation_scores.csv`, column `units_correct`, in `run_01/02/03` order |
| V found 3/3 | `evaluation_scores.csv`, `story_v_found` |
| G found 0/3 | `evaluation_scores.csv`, `story_g_found` |
| C-trap 0 | `evaluation_scores.csv`, `c_trap_flags` |

A tenth, bonus assertion was added after independently noticing it holds:
`evaluation_scores.csv`'s three `figures_total` values sum to exactly 364, which is
report.md §5's headline figure count — a genuine, unplanned cross-check between the
mechanical CSV and the hand-adjudicated document, not something engineered to match.

The rule engine and the eight detector features are not just read from the frozen
CSVs — they are recomputed from scratch inside the notebook by importing
`code/rule_tests.py` and `code/detect_anomalies.py` (read-only; never edited) and
re-running them on the public CSVs, then asserting byte-identity with the frozen
outputs. This is stronger than "trust the CSV": it demonstrates the pipeline is
still reproducible from the public data alone, inside the notebook, at Phase 4.

## 2. Where the answer key is opened, and why that is disclosed

`data/answer_key/anomalies.csv` is read for the first time in §3 ("The rule layer"),
with an explicit one-line disclosure in the markdown immediately above the load —
mirroring `code/evaluate.py`'s own justification (marking, not modelling, happens
after this point). Every later section reuses the same in-memory `key_long` /
`answer_key` frames rather than reopening the file. This is stated up front in the
notebook's opening cell (§0) as a roadmap line, and restated at first use.

## 3. The v2 post-hoc detector — result, reported honestly

Section 5 is clearly boxed as **post-hoc**: built after §4's frozen-deviation result
was known, not part of the pre-registered pipeline, not counted against
`design/DECISIONS.md`'s 3 July 2026 frozen-deviation entry or against the storyteller
runs. Two changes only, both implemented inside the notebook (not in `code/`):

- `vendor_amount_z` recomputed on an **expanding, prior-transactions-only** basis
  (chronological by `invoice_date`, minimum 5 priors else 0 — the same floor the
  frozen feature uses; std-floor guard reused too), instead of the frozen feature's
  full-year basis.
- A ninth feature, `log10_vendor_txn_count`, appended.
- Everything else — the other seven features, `IsolationForest(n_estimators=200,
  contamination=0.004, random_state=42, n_jobs=1)` — held fixed.

**Result, whatever it turned out to be:**

| | v1 (frozen) | v2 (post-hoc) |
|---|---:|---:|
| G's best rank (of 50,000) | 818 | 98 |
| G invoices in the top 200 (of 12) | 0 | **1** |
| B4 rank | 9,069 | 1,775 |
| B5 rank | 6,641 | 1,272 |
| Overlap with any answer-key transaction (of 200 flags) | 0 | 5 (1×G, 1×D, 3×S) |
| C caught in top 200 | 0 | 0 |

G's best rank improves by roughly 8×, and the detector does catch one of the twelve
elevated invoices for the first time — but that is 1, not the pre-registered "≥6",
so **v2 does not clear the designed bar either**. It is reported as a partial,
genuine improvement with a side effect (S and D transactions — which the rule layer
already catches — now also enter the detector's top 200, a novelty the frozen v1
detector never had). B4 and B5 move a long way up the ranking without crossing into
the flagged tail: a one-invoice vendor still cannot supply five priors for even an
expanding baseline. C stays at zero — the ceiling claim survives this one detector
change. The frozen v1 result stands unchanged; v2 is additive reporting, not a
substitution.

## 4. Design decisions made in the notebook that are not pinned in design.md

These are Phase-4, notebook-local choices (not retroactive edits to the frozen
Phase-3 pipeline):

- **Contamination ablation is rank-based, not refit-based**, exactly as the brief
  specified: `detector_scores.csv`'s existing per-transaction scores are sorted once,
  and a flag budget of *N* is simulated by taking the top *N* ranks. This is
  mathematically identical to what a lower/higher `contamination` value would select
  (IsolationForest's `contamination` parameter only changes the `predict()` cutoff
  rank, not the fitted scores), so no refitting is needed and the ablation is
  computed for budgets 1–2,500 (contamination ≈0.002%–5%, a superset of the
  requested 0.1–5% sweep) in one vectorised pass.
- **Chart palette**: wine `#A8352A` / indigo `#41529E` / gold `#B68A2C` / grey
  `#665E58` (context only, always direct-labelled) / beige `#EFE5CE` (fills) / ink
  `#1A1410` (text) on face `#FBFAF5`, matching `05 Board Reporting`'s already-validated
  notebook convention exactly (same `new_fig`/`style_title`/`end_label` helper
  pattern, same `PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks"
  else Path.cwd()` resolution so the notebook runs correctly whether nbconvert's
  working directory is `notebooks/` or the project root).
- **Typography**: proper Unicode en dashes (–, ranges) and em dashes (—, breaks) in
  all markdown and in every chart title / printed sentence, matching the established
  convention observed in `05 Board Reporting`'s notebook; plain ASCII `--` is used
  only inside Python comments, which are not user-facing prose.
- **The catch-matrix table** (§7) is a `pandas.Styler` with G's row highlighted in
  beige, built entirely from `evaluation.json` + `evaluation_scores.csv` fields (the
  "Designed catch" column is a static design-specification label from
  `design/design.md` §3, not a computed result, and is documented as such in a code
  comment).
- **Narrative detail not present in the mechanical CSVs** (which specific units each
  run missed, the two B3 false positives, the €1,000 Kärrenbach imprecision) is
  quoted/transcribed from `data/analysis/report.md` with attribution, the same
  pattern `05 Board Reporting`'s notebook uses for its own adjudicated scorecard —
  because mechanical figure-matching cannot tell a defensible-sounding wrong verdict
  from a right one, only a human adjudication can, and that adjudication already
  exists and should not be silently re-derived by a different, unaudited method.

## 5. Execution confirmation

```
python -m nbconvert --to notebook --execute --inplace notebooks/anomaly_detection_analysis.ipynb
```

Run twice (once during the build, once as a final clean-state confirmation before
this note was written). Both runs: exit code 0, 40 cells (20 markdown + 20 code),
zero `error` outputs, all asserts pass including the 50,000-row / 64-flag / 75%-
precision / 200-flag / zero-overlap / 37-35-38 / V-3-3 / G-0-3 / C-trap-0 / 364-
figures checks listed in §1 above. Nine chart-producing cells confirmed visually
(exported to PNG and inspected) for palette compliance, readability and absence of
axis/label collisions.
