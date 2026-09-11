# 06b — The fix: a standing vendor-drift review

Status: designed 11 Sep 2026 (main loop) on Eva's direction ("go for it — 6a and 6b on the
same page"). Pre-registered expectations in §5 were written BEFORE any 06b code ran.
Eva's read-through folds into her September review sitting alongside 6a's.

## 1. Why this exists

6a's pre-registered, frozen result: the Isolation Forest scored 0 of 200 against the
planted anomalies, and the slow price drift the case is named for (vendor G, Teräskontio:
freight folded into goods prices from July, then ~+2%/month compounding inside the bundle)
was caught by no layer. Diagnosis, published in 6a: `vendor_amount_z` measures each invoice
against the vendor's FULL-YEAR mean, so a sustained drift inflates its own baseline and
erases its own signal (peak z +2.13 observed vs ~+6.5 against a clean baseline).

6a's own closing line names the fix: "a standing review of each vendor against its own
history, which is a report rather than a model." 6b builds exactly that, pre-registers what
it should catch, runs it on data it has never seen, and marks the result. The arc published
on the case page: v1 missed → diagnosed why → the fix, tested honestly on fresh data.

Integrity rules carried over from 6a, unchanged:
- Pre-commitment: any miss is a frozen, reported deviation, never a retune.
- The word "fraud" appears nowhere; framing is controls and process quality.
- Answer key generated first, held out of every analysis path, used only by the marking
  script.
- 6a's session artefacts (agent runs, adjudications, published figures) are NEVER re-run
  or altered. 6b only adds files.

## 2. The data — Saarnitukku Oy, the following year

Same invented company, its FY2026 purchase ledger — the sequel reads naturally: the firm
installed the standing review after the 2025 exercise; here is its next year.

- ~50,000 AP posting lines, calendar 2026, ~200 vendors (regenerated with the 6a generator
  family, new config), RANDOM_SEED = 2026 (6a used 42; fresh seed = fresh data).
- Net of VAT, no credit notes, same GL shape and approval-tier conventions (€10,000 /
  €50,000) as 6a — declared inventions, consistent across the pair.
- The ledger is otherwise CLEAN of 6a's other anomaly classes. 6b tests one claim only:
  does the drift review catch sustained per-vendor drift, and does it stay quiet elsewhere.
  (Re-planting 6a's full zoo would blur what is being measured.)

### Plants (recorded in data/06b/answer_key_06b.csv before any analysis runs)

| id  | What                                                                       | Kind   |
|-----|----------------------------------------------------------------------------|--------|
| D1  | Fast drift: vendor's unit prices rise ~2.5%/month from April onward        | anomaly|
| D2  | Slow drift: ~1.0%/month from February onward — the sensitivity test        | anomaly|
| D3  | Bundling drift, the G re-run: freight folded into goods lines from June,   | anomaly|
|     | then ~+1.8%/month inside the bundle (memo trail in Finnish, as in 6a)      |        |
| B1  | Contractual indexation: +5.2% step on 1 January, memo cites the index      | benign |
|     | clause — SHOULD surface in the report and be stood down on the memo trail  |        |
| B2  | Market repricing: one supplier raises list prices ~9% in one step in       | benign |
|     | August, announced in a memo — surfaces, stands down                        |        |

Three drift anomalies with different rates and start months; two benign lookalikes that
separate detection (the report's job) from judgment (the reader's). Vendor names: new
fictional names, collision-checked against the six portfolio companies and 6a's vendor
master.

## 3. The method — a report, not a model

`drift_report.py` — deterministic, no ML, parameters FIXED HERE before generation:

1. Per vendor, per month: volume-weighted mean unit price per item family (falling back to
   invoice-level totals where item granularity is absent), minimum 3 invoices/month to
   score a month.
2. Baseline: expanding mean and standard deviation of all PRIOR months, minimum 3 months
   of history before scoring begins (months 1–3 are baseline-only).
3. Signal: standardised deviation of the current month vs the trailing baseline; drift
   statistic = one-sided CUSUM of those deviations (k = 0.5).
4. Flag: a vendor is REPORTED when its CUSUM exceeds h = 4.0; the report ranks all vendors
   by peak CUSUM and prints the trajectory (months, magnitudes, first-crossing month).
5. Output: one ranked table + one trajectory panel per flagged vendor. No agent layer —
   the whole point is that this is a report a controller reads in ten minutes.

Also run RETROSPECTIVELY on 6a's frozen 2025 ledger (read-only) as an in-sample diagnostic:
does the review, as parameterised above, catch Teräskontio? Labelled in-sample — the fix
was designed FROM that failure, so this run demonstrates the diagnosis, not the method's
power. The FY2026 run is the real test.

## 4. What 6b does NOT claim (scope, stated up front)

Catches sustained per-vendor price drift only. Out of scope and stated so on the page:
one-off anomalies (6a's rule layer exists for those), cross-vendor effects, drift slower
than ~0.5%/month inside one year, and drift in a vendor's first three months (no baseline).
The benign lookalikes are EXPECTED to surface — a drift report cannot read contracts; the
stand-down is human judgment on the memo trail, and saying so honestly is part of the case.

## 5. Pre-registered expectations (written before any 06b code ran)

1. D1 (fast, April): flagged, CUSUM crossing by June 2026 at the latest; ranks top-3.
2. D3 (bundling, June): flagged, crossing by September 2026; ranks top-5.
3. D2 (slow, February): flagged by year-end; the crossing month is the sensitivity
   finding, expected in the Aug–Nov window. If D2 is NOT flagged, that is a frozen,
   reported miss and the published sensitivity boundary of the method.
4. B1 and B2: both surface (B2 possibly as a single sharp excursion rather than a
   sustained crossing — recorded either way); both distinguishable from D1–D3 only via
   the memo trail. Zero silent passes expected for B1.
5. False positives: at most ~5 unplanted vendors above h = 4.0 (ordinary noise at 200
   vendors); each gets a one-line explanation in the report.
6. Retro-run on 6a's 2025 ledger: Teräskontio ranks top-3 by peak CUSUM, first crossing
   in or before October 2025.
Any expectation that fails is frozen and published, exactly as 6a's were.

## 6. Deliverables and page placement

- `code/06b_generate.py` (config-driven, seed 2026), `code/06b_validate.py` (coherence
  checks incl. plant integrity), `code/drift_report.py`, `code/06b_mark.py` (the only file
  that opens the 06b answer key), all under the existing 06 project.
- `data/06b/` — ledger, answer key, `drift_report.md` (the ranked output), `report.md`
  (marked results vs §5, deviations frozen).
- Writeup: a "6b — the fix" section appended to the canonical writeup (writer agent, after
  numbers exist).
- Case page: a new section on `case-anomaly-detection.html` UNDER the existing content —
  the page becomes 6a (the miss) + 6b (the fix) — prose plus ONE hand-rolled SVG (the
  drift trajectory with baseline and crossing month, validated chart palette, ≤3 hues).
  No second explorer. work.html's entry gains one sentence. All prose via the writer
  agent; DECISIONS entries in both the project log and the website log.

## 7. Also in this pass — 6a design-doc reconciliation

The 6a design doc still reads as if the detector worked (status line "draft for Eva's
review"; §3's expected detector outcomes with no deviation pointers; the ≈20–22 verdict
units vs 39 shipped; the month-grouping rule that never fired; the 2×2 placement of G and
B4/B5). Same reconciliation treatment 01 Churn received: past-tense scoping with pointers
to the frozen deviation, status line updated, nothing about the recorded decisions altered.
