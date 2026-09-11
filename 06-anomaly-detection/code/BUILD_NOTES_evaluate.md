# Build notes — `code/evaluate.py` (Phase 3 evaluation / marking script)

Built from the Phase-3 evaluation brief (design.md section 7 — the two-tier
split — and section 3, the catch matrix and pre-registered run expectations),
`data/answer_key/anomalies.csv`, `data/analysis/clusters.json`, and whichever
`run_0N_findings.json` files exist under `data/analysis/agent_runs/`.

Reading `data/answer_key/anomalies.csv` here is legitimate and required —
`evaluate.py` is the marking script. It is never imported by, or referenced
from, anything agent-facing; the storyteller runs are given only the files
listed in `design/storyteller_briefing.md`, and nothing under
`data/answer_key/` is on that list.

---

## 1. Discovery is dynamic, not hardcoded

`discover_runs()` globs `data/analysis/agent_runs/run_*_findings.json` at the
top level only (`_scratch_run01`, `_scratch_run02`, … are ignored — they are
working folders, not the frozen deliverable). This was written when only
`run_01` existed; **`run_02` landed mid-build**, and re-running the script
picked it up with no code change, which is the intended behaviour for
`run_03` too. No run count is assumed anywhere in the script.

## 2. The C false-positive trap needs two answer-key fields, not one

The brief's stated mechanical rule is: "a unit expects `worry` iff its
flags' txn_ids intersect a `kind=anomalous` key row". Taken completely
literally this is wrong for class C: `C-01`'s `kind` is `anomalous`, but
design.md section 3 explicitly declares C's own `expected_verdict`
`stand_down` by design — "a run that accuses Neuvantila without evidence has
failed the discipline test, and is scored as a false positive." If any unit
ever came to intersect C's txn_ids (it does not, in this build — the
detector's zero-flag outcome on C is itself part of the ceiling claim), the
literal `kind`-only rule would mechanically demand `worry`, exactly
backwards from the design intent.

`expected_verdict_for_unit()` therefore uses **both** fields: a matched key
row only counts toward "worry" if `kind == "anomalous" AND expected_verdict
== "worry"`. This is still a mechanical, answer-key-driven rule (not a
judgement call baked into the code) — it just uses the column the design doc
itself uses to declare the trap. The same two-field rule is reused for
`build_key_vendor_anomalous_worry()` (section 6's free-hunt vendor mapping),
so C stays excluded everywhere the "is this a real target" question is
asked. Section 4's C-trap check (`find_c_trap`) is unaffected — it fires
independently on *any* WORRY finding mentioning V-0007/Neuvantila, which is
the actual point of that test.

## 3. Two descriptive keyword-test clauses were operationalised into regexes

The brief states nine mechanism keyword tests verbatim; seven are already
literal regexes. Two are descriptive and needed a concrete translation,
recorded here and in the worksheet itself:

- **D** — "mentions the shared order reference or invoice-number pair" →
  `order|tilaus|reference|invoice number|invoice ref` (ANDed with the
  primary `duplicate|double|resubmi|uudelleen|toistuv` clause).
- **B3** — "(PO|different (order|purchase)|distinct)" is already a regex as
  written; `PO` is wrapped in `\b...\b` (as is A's `IT`) so it does not match
  as a substring of ordinary words (e.g. "unit", "quit", "report") under
  case-insensitive matching. Every other clause is used unmodified.

Keyword-test results are reported per unit per run but are **never** used to
override or annotate the unit-verdict correctness in section 2 — a run can
reach the right verdict by a route the keyword list doesn't anticipate, and
the brief is explicit that these results are "not auto-scored as final".

## 4. Figure-verification tolerance follows the Phase-3 brief, not design.md §7 verbatim

design.md section 7 states "tolerance ±€50 absolute or exact for planted
figures; ±0.1pp for percentages". The brief that commissioned this script
restated the tolerance for tier 2 section 5 as "planted exact amounts
exact-match; aggregates tolerance ±€100 or ±1%". `evaluate.py` implements the
brief's numbers (`AGGREGATE_ABS_TOLERANCE_EUR = 100.0`,
`AGGREGATE_REL_TOLERANCE = 0.01`), flagged here as a deliberate deviation
from the design doc's own wording rather than a silent inconsistency, and
called out again in the worksheet's section 5 preamble so a reader of the
worksheet alone sees it too. Percentages are not verified at all (see next
note) — no percentage tolerance is implemented in this pass.

## 5. Figure parsing: currency-shaped numbers only, and how false positives were closed

`FIGURE_NUMBER_RE` only extracts numbers that are either comma-thousands
grouped (`36,934.24`, `180,000`) or carry an exact two-decimal fraction
(`300.37`). This intentionally excludes ordinary percentages (`+8%`,
`82.45%` — no comma/2-decimal shape, or explicitly rejected by a trailing
`(?!\s*%)`), anomaly scores (`0.0266` — four decimal digits, not two — the
regex cannot land a valid match on it), and plain small counts (`8`, `3/7`).

Two false-positive shapes were caught and fixed while testing against
`run_01`:

- **Truncated multi-decimal numbers.** `\d+\.\d{2}` is not naturally
  anchored at the end, so `99.998` (a percentile, not currency) would
  otherwise match as `99.99`. Fixed with a trailing `(?!\d)` — no digit may
  immediately follow the matched fraction.
- **Finnish DD.MM.YYYY dates.** `15.11.2025` (from B2's memo,
  `"Sovittu ylityö, inventaario 15.11.2025"`) matched `\d+\.\d{2}` as `15.11`
  before the fix — a date, not a euro figure. Fixed with a further
  `(?!\.\d)` — a matched number may not be immediately followed by another
  `.` + digit, which is exactly the shape of a continuing date component.
  Confirmed the false hit disappeared from run_01's not-checkable list after
  the fix (19 → 18 not-checkable figures; the removed row was the `15.11`
  one).

One known, accepted limitation remains: a bare comma-grouped integer that is
actually a **count**, not an amount (e.g. `"...out of U-117's 1,466 (0.5%)"`
in run_01's F-13), still matches the comma-group alternative and is treated
as a currency candidate. This is safe by construction — it will not match
any real euro anchor and will simply land in the `not-checkable` list, which
the brief treats as "for adjudication", never a failure. Tightening this
further (e.g. requiring an `EUR`/`€` token nearby) would risk the opposite
failure — missing genuine whole-euro amounts written without a currency
marker (`"12 x 15,000 on 7000"`) — so it was left as is and documented rather
than "fixed" in a way that trades one blind spot for another.

## 6. Anchor pool for figure verification

Anchors are recomputed fresh from `gl_transactions.csv` per finding, never
read from `clusters.json`'s own pre-computed `total_eur` (which would just
be checking the pipeline against itself):

- **Exact anchors** — every individual transaction amount in the finding's
  scope (the mapped unit's txn_ids; for `unit_id == "free-hunt"`, every
  transaction of the vendors named in `affected.vendor_ids`).
- **Aggregate anchors** — the scope's full total, every pairwise sum within
  the scope (covers "a + b = c" duplicate/split evidence, which is how most
  of this dataset's arithmetic evidence is phrased), and, for free-hunt
  findings, each named vendor's own full-year total.

This is a best-effort pool, not an exhaustive one (no attempt at triple-sums
or arbitrary subset sums beyond pairs). Anything it cannot match lands in
`not-checkable`, which is the safe, by-design outcome for this tier — see
design.md section 7 and the brief: "anything unmatched or disagreeing →
listed as not-checkable/disagree for adjudication, NEVER auto-failed." No
separate "disagree" bucket was implemented: distinguishing "this figure is
wrong" from "this script doesn't know what this figure is meant to
represent" requires semantic understanding of the prose, which tier 2 is
explicitly not supposed to do. Everything unmatched is therefore
`not-checkable`, and it is meant to be read that way — a worklist for a
human, not a verdict.

## 7. Schema validation is diagnostic, not a hard gate

`evaluate.py` does not `sys.exit(1)` on schema violations in a storyteller
run — unlike `validate_ledger.py`'s hard-fail convention for generation-side
coherence rules, a run's schema quality is itself part of what is being
measured (run variance is explicitly named as part of the story — design.md
section 8). The script only exits non-zero for genuinely fatal conditions:
missing required input files, or an exception while building the outputs.
Per-run schema violations are collected and printed in full in worksheet
section 1 instead.

## 8. What was verified against `run_01` and `run_02` (both available at build time)

- `run_01`: 41 findings (39 unit + 2 free-hunt), 0 schema violations,
  37/39 units correctly verdicted mechanically (RU-05 R-ROUND and RU-13 W-01
  are the two the run stood down on that the key expects worry on — a
  genuine, meaningful divergence, not a script defect), story V found (via
  the free-hunt finding on the Kärrenbach trio), G not found (consistent
  with the detector's own zero-overlap-with-G outcome — see
  `code/BUILD_NOTES_phase3.md` — there is no unit for a run to have found it
  through), 1 unmatched worry finding (the free-hunt finding about
  large unflagged manual postings, which touches B4's vendor and is
  correctly left for adjudication rather than auto-scored as a false
  positive).
- `run_02`: landed mid-build; discovered and scored with no code change —
  41 findings, 0 schema violations, 35/39 units correct, same story-V/no-G
  pattern, 1 unmatched worry finding.

## 9. Deliberately out of scope for this pass

- No cross-run agreement/consistency analysis (e.g. "did all three runs
  agree on unit X") — the brief's headline exhibits (design.md section 7)
  belong to the hand-written `data/analysis/report.md`, built from this
  worksheet by a human adjudicator, not by this script.
- No attempt to score the free-hunt findings' *quality* beyond the four
  named story targets (V, G, G-mirror, C-trap) and the generic
  unmatched-worry listing — any other free-hunt content (like run_01's
  F-41 on unreviewed manual postings) is visible in the worksheet's
  unmatched-findings section but is not itself classified as good or bad.
