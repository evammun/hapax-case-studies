# Phase 5 support scripts -- build notes

Built from the Phase 5 brief: two scripts supplying the interactive results
page's data and QA gate. The page itself (`interactive/anomaly-detection.html`)
is built separately, in the main loop, in a later step.

## 1. `code/build_interactive_data.py` -> `interactive/_data.json`

Distils the public CSVs and `data/analysis/*` outputs into one compact JSON
(18.6 KB, well under the ~80 KB target) for the self-contained page. Every
number is read live or recomputed fresh from source artefacts and asserted
against `data/analysis/evaluation.json` / `evaluation_scores.csv` before the
file is written (05 Board Reporting's own data-prep convention). Nothing is
hand-typed from prose.

Top-level keys: `meta`, `monthly_volume`, `rule_layer`, `detector`,
`catch_matrix`, `flag_timeline`, `runs`, `stories`, `figures`, `units`.

### Decisions not fully pinned by the Phase 5 brief

- **`monthly_volume` vs `flag_timeline` use different date columns, on
  purpose.** `monthly_volume` (12 raw transaction counts) is keyed on
  `invoice_date`, per the brief's own wording ("txn counts by invoice
  month"). `flag_timeline` (rule/detector flag counts) is keyed on
  `posting_date`, matching `detect_anomalies.py`'s own convention for its
  calendar-shaped features (day_of_week, non_working_flag, month_index) and
  `prepare_clusters.py`'s month-grouping step, both of which use
  `posting_date` for consistency with the rule layer's calendar test.
- **The "runs" bullet's "stories summary" and "figure-check summary" are two
  additional top-level keys** (`stories`, `figures`), siblings of `runs`,
  rather than nested inside each run object -- they are properties of the
  three-run set as a whole (found by N of 3 runs), not of any one run.
- **`missed` / `false_positives` per run are unit_id lists, computed fresh**
  by recomputing each of the 39 verdict units' expected verdict (the same
  two-field rule as `evaluate.py`'s `expected_verdict_for_unit`: worry iff
  the unit's txn_ids intersect a key row with `kind=anomalous` AND
  `expected_verdict=worry` -- this is what correctly excludes class C) and
  comparing against each run's actual finding. This is deliberately
  reimplemented locally rather than importing `evaluate.py`, so the two
  scripts check each other rather than sharing a single point of failure.
  The recomputed `units_correct` is asserted against
  `evaluation_scores.csv` for all three runs (37/35/38) and matches exactly;
  the recovered lists also reproduce `data/analysis/report.md` section 3's
  prose exactly (run 01 misses R-ROUND + W; run 02 misses the three S
  units and false-positives on B3; run 03 false-positives on B3 only).
- **`figures.disagreements` (0) and `figures.imprecisions` (2) are the
  hand-adjudicated conclusions from `report.md` section 5**, not a field
  `evaluate.py`'s mechanical worksheet produces (it only has
  exact-match/aggregate-match/not-checkable counts, with no concept of a
  "disagreement" or "imprecision" -- those are judgement calls made once, by
  hand, in the frozen scorecard). Only the total (364) is asserted against
  `evaluation_scores.csv`'s `figures_total` column sum; the other two are
  carried through as the published, adjudicated record.
- **Detector ranks for G/B4/B5 are computed from `detector_scores.csv`**
  (which holds one row per transaction, `anomaly_score` only, no rank
  column) by ranking `anomaly_score` descending (higher = more anomalous,
  per `code/BUILD_NOTES_phase3.md`). This rank formula was cross-checked
  against `detector_flags.csv`'s own `rank` column for all 200 flagged
  transactions -- zero mismatches -- before being trusted for the three
  unflagged classes it actually needs to rank.

### A discrepancy this script's own asserts surfaced (reported, not silently fixed)

Computed ranks: **G = 818, B4 = 9,069, B5 = 6,641** (best-ranked transaction
per class, out of 50,000; cutoff for flagging is 200).

`code/BUILD_NOTES_phase3.md` and `design/DECISIONS.md` (3 July 2026, "Phase 3
detection run") both state **"B4 ... ranked 6,641st"** and **"B5 ... ranked
9,069th"** -- the B4/B5 figures transposed relative to what the data actually
shows. Verified two ways before concluding this is a documentation
transcription error rather than a bug in this script:

1. `TXN036635` (B4, the answer key's own €78,400 capex transaction) is
   independently confirmed as the single largest `amount_eur` in
   `gl_transactions.csv` -- consistent with `B4_AMOUNT_EUR` in `config.py`.
   Its `anomaly_score` is -0.1319; `TXN001408` (B5, €24,600) scores -0.1147.
   Higher score = more anomalous, so B5 ranks better (6,641st) than B4
   (9,069th) -- the opposite pairing from the prose.
2. The rank formula used here (`anomaly_score.rank(ascending=False,
   method="min")`) reproduces `detector_flags.csv`'s own `rank` column
   exactly for all 200 flagged rows (0 mismatches), so the same formula's
   output for the two unflagged B4/B5 transactions is trustworthy.

`interactive/_data.json` carries the data-verified values (G=818, B4=9069,
B5=6641). The two historical documents are frozen build/decision records and
were not edited by this task (out of scope, and `DECISIONS.md` is an
append-only running log by convention) -- flagging this for whoever next
touches those files, per the portfolio's own "corrections are part of the
record" convention.

### Assertions run before the file is written

- `n_transactions` / `n_vendors` vs `config.TOTAL_TRANSACTIONS` /
  `config.TOTAL_VENDORS`.
- `rule_layer` per-test flags/anomalous totals vs
  `evaluation.json`'s `precision_by_rule_test` and `precision_vs_anomalous`
  (48/64/16).
- `detector.n_flags` (200), `key_overlap` (0), and all three designed-miss
  ranks > 200, cross-checked against `evaluation.json`'s
  `designed_outcome_checks` (`actual_count == 0` for G/B4/B5/C).
- `catch_matrix` per-class matched/total vs `evaluation.json`'s
  `recall_by_class` (rules layer for D/R/W/S/A; both layers for V/G/C), and
  the planted-txn sum (87) vs `config.TOTAL_ANOMALOUS_TRANSACTIONS`.
- `flag_timeline` sums (64 rule, 200 detector) vs `evaluation.json`'s
  inventory totals.
- Per-run `units_correct`/`units_total` vs `evaluation_scores.csv` exactly;
  internal partition check (correct + missed + false_positives ==
  units_total) for all three runs.
- `stories` summary (V found 3/3, G found 0/3, C clean 3/3) and `figures`
  total (364) vs `evaluation_scores.csv` column sums.
- Every unit's `n_flags` vs `evaluation.json`'s `per_unit_flag_counts`; unit
  count (39) and total flags across units (264 = 64 + 200).

All passed on this run; the script exits non-zero on any failure (never a
silent mismatch).

## 2. `code/verify_interactive.py` -> QA gate for `interactive/anomaly-detection.html`

Modelled on `Case Studies/05 Board Reporting/interactive/_verify_page.py`
(read-only precedent), extended with the checks this project's brief adds:
`id=` prefixing (05 only checked `class=`), an exact external-resource count
("exactly one Google Fonts stylesheet link", not just "no disallowed
hosts"), a `fetch`/XHR/`src=` inlining check, byte-for-byte embedded-JSON
parity against `interactive/_data.json` (05 only checked two anchor values),
and a British-spellings spot-list.

**Runs cleanly before the page exists**: prints a plain "not present yet"
message and exits 0 (there is nothing to gate yet, so a missing page is not
a failure). Once `anomaly-detection.html` exists, every check runs and the
script exits 1 on any failure, with a per-check PASS/FAIL report.

**Verified against three throwaway test pages** (written to
`interactive/anomaly-detection.html`, checked, then deleted -- never left in
the repository):

1. A minimal fully-compliant page -> all 19 checks PASS, exit 0.
2. The same page with one straight apostrophe left in prose -> that one
   check FAILs correctly, exit 1; fixed and re-verified -> PASS.
3. The same page with five deliberate violations injected (an unprefixed
   class, an external non-font URL in prose, a `fetch(` call, an American
   spelling, and a broken embedded-JSON value; plus, in a further pass, a
   removed closing `</div>`) -> every injected violation was caught by its
   corresponding check, none by the wrong one, exit 1 throughout.

### Decisions not fully pinned by the Phase 5 brief

- **British-spellings spot-list is a fixed, documented, non-exhaustive
  list** (`color`, `favorite`, `organization`, `behavior`, `center`, `gray`,
  etc.) chosen to exclude `-ize`/`-ise` verb pairs, both valid in Oxford
  British spelling, so the check cannot fail on correct copy.
- **Windows console encoding.** This machine's default `sys.stdout.encoding`
  is `cp1252`, which cannot encode en-dashes or umlauts -- the exact
  characters this script's own diagnostic messages need to print when
  reporting a typography violation. Both scripts call
  `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` defensively
  at the top, so a diagnostic print can never itself crash the run
  (graceful errors, never a bare crash).

## Commands run

```
python code/build_interactive_data.py   # writes interactive/_data.json, all asserts pass
python code/verify_interactive.py       # page not present yet -> prints notice, exit 0
```
