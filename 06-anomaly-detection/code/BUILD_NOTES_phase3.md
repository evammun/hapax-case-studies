# Phase 3 build notes — detection layer

Built by python-builder from `design/design.md` sections 3, 6, 7 and
`design/DECISIONS.md`. Phase 2 (`config.py`, `generate_ledger.py`,
`rule_tests.py`, `validate_ledger.py`, everything under `data/` root and
`data/answer_key/`) was not touched.

Environment: Python 3.12.6, scikit-learn **1.9.0**, pandas, numpy (as pinned
in `design/DECISIONS.md`, 3 Jul 2026).

**Hard constraint honoured:** none of `run_rule_layer.py`, `detect_anomalies.py`,
`prepare_clusters.py` reads, imports, or otherwise references anything under
`data/answer_key/`. Grepped for `answer_key`/`anomalies.csv` across all three
scripts post-build — the only hits are comments stating the exclusion.

---

## 1. `code/run_rule_layer.py`

Thin runner around the frozen `rule_tests.run_all_rule_tests`. Loads the
three public CSVs it needs (`gl_transactions.csv`, `vendor_master.csv`,
`company_calendar.csv`), runs the seven tests, sorts the output
deterministically (`txn_id`, `test`), asserts the per-test counts against
`config.PREREGISTERED_TEST_COUNTS`, and writes `data/analysis/rule_flags.csv`
(columns: `txn_id`, `test`).

**Result (as-run, matches pre-registered exactly):**

| Test | Flags | Expected |
|---|---:|---:|
| duplicate | 14 | 14 |
| round_sum | 18 | 18 |
| near_threshold | 4 | 4 |
| split | 10 | 10 |
| calendar | 10 | 10 |
| mapping | 8 | 8 |
| name_hygiene | 0 | 0 |
| **Total** | **64** | **64** |

No deviation. `rule_flags.csv` SHA-256 (two independent runs, identical):
`ce3c3d070f134b1c7dc30576c2719b54150cb6d901d8c46803c6b54b6461d7b1`

---

## 2. `code/detect_anomalies.py`

### Interpretation decisions (not pinned verbatim in design.md section 6; recorded here as the build's own choices)

Design section 6 pins all eight feature *formulas* and their edge cases, but
doesn't state which date column (`invoice_date` vs `posting_date`) backs
each calendar-shaped feature. Decisions made, applied consistently:

- `day_of_week`, `non_working_flag`, `month_index` → **`posting_date`**.
  Rationale: `company_calendar.csv` and the calendar rule test (rule_tests.py
  `test_calendar`, validator rule 2) are both keyed on `posting_date` — using
  the same basis keeps the detector's calendar features consistent with the
  rule layer's own calendar test.
- `cadence_ratio` → **`invoice_date`**. Rationale: validator rule 5
  ("cadence consistency") is explicitly an inter-*invoice*-date timing check;
  cadence is a property of when invoices arrive, not when they get keyed in.
- `vendor_amount_z` and `account_rarity` are date-independent (amount and
  account only).
- Cluster preparation's month-grouping step (c) also uses `posting_date`'s
  month, for the same consistency reason.

One additional edge case beyond the pinned list, defensive only: if a
vendor's median inter-invoice gap is exactly 0 (repeated same-day invoices),
`cadence_ratio` is set to the neutral value 1 rather than dividing by zero.
Never triggered in this ledger (checked: no vendor has a zero median gap),
but included so the script cannot crash on a different regeneration.

Feature order is fixed (`FEATURE_COLUMNS` in the script, matching design
section 6's numbered list 1–8) and held constant across every fit — row
order is also fixed (sorted by `txn_id` before feature computation and
re-asserted before building the matrix), which is what makes the
determinism check meaningful rather than incidental.

`anomaly_score` is defined as `-model.decision_function(X)`, so **higher =
more anomalous** (sklearn's own convention is the opposite: low
`decision_function` = outlier). `rank` 1 = most anomalous. The flagged set
itself is sklearn's own contamination-based `predict() == -1` label, not
a score threshold picked by this script — so the score's sign convention
has no bearing on which 200 rows get flagged.

### Result (as-run)

- scikit-learn version: **1.9.0** (matches the pinned/spiked environment).
- Feature matrix: 50,000 rows × 8 columns.
- **Flagged: exactly 200 of 50,000** — matches the designed outcome in
  design.md section 3 ("contamination 0.004 → exactly 200 flags of 50,000")
  precisely, on the real feature matrix (not just the synthetic spike
  matrix).
- **Determinism, asserted twice over:**
  - Within one process: the full feature-build-and-fit pipeline ran twice;
    SHA-256 of `detector_scores.csv` and `detector_flags.csv` against a
    second, temp-named run were identical; temps deleted after hashing
    (`delete_with_retry` added — this project's `data/` folder lives under
    Dropbox, whose sync agent transiently locked the just-written temp file
    on the first attempt (`WinError 32`); a short retry loop, not a
    workaround of the determinism guarantee, fixed it).
  - Across two separate process invocations (`python code/detect_anomalies.py`
    run twice from a fresh shell): identical final-output hashes both times.
  - `detector_scores.csv` SHA-256: `7b0f6798fb106e48e853acacb369b0213fd2953111a5803bf8593c251f107512`
  - `detector_flags.csv` SHA-256: `d2face2f7779484ae86ca861b1439acb64f69cc493d14fc6991718332f2dd7f2`

### Observed deviations from the *designed* outcomes (frozen and reported, per design.md section 6's own instruction — not retuned)

Design section 3 states these as outcomes to be *checked* at Phase 3, with
an explicit acknowledgement that a joint-space Isolation Forest cannot be
guaranteed from single-feature bounds at generation time. Checked, using
only Phase-2 build config (`config.TERASKONTIO_VENDOR_ID` etc. — not the
held-out answer key) to identify which vendor is which for diagnostic
purposes; no answer-key file was read by any script or in producing this
note:

- **G (Teräskontio, `V-0001`) — expected "≥ 6 of 12 elevated invoices
  flagged"; realised: 0.** Diagnostic check confirms `vendor_amount_z` does
  carry the designed signal shape (H1 invoices all negative z, roughly
  −1.6…−0.05; H2 invoices all positive z, roughly +0.29…+2.13, rising
  toward December) — the feature computation is behaving correctly. The
  best-ranked Teräskontio transaction placed **818th** of 50,000 (cutoff is
  200). The pinned "full-year mean/std" basis for `vendor_amount_z` computes
  the baseline from *both* H1 and H2 together, which inflates the baseline
  std for a vendor whose own elevated invoices are part of that baseline —
  mechanically damping the very step it's meant to expose. This is an
  artefact of the feature's pinned definition, not a bug in this build.
- **B4 (`V-0019`, €78,400 capex) — expected "flagged as a top singleton";
  realised: not flagged, ranked 6,641st.** B4 is the single largest amount
  in the entire ledger (99.998th percentile of `log10_amount`), but as a
  single-transaction vendor it gets `vendor_amount_z = 0` and
  `cadence_ratio = 1` (both neutral, by the pinned edge-case rules for
  sparse vendors) and `account_rarity = 0`. One extreme axis among seven
  neutral ones did not isolate it inside the contamination-selected 0.4%
  tail of a 50,000-row, 8-feature joint space.
- **B5 (`V-0020`, €24,600 insurance) — expected "flagged as a top
  singleton"; realised: not flagged, ranked 9,069th.** Same mechanism as B4
  (second-largest amount in the ledger, 99.996th percentile, but otherwise
  entirely neutral on every other feature).
- **C (Neuvantila) — designed "zero detector flags"; realised: 0 flags.**
  Matches the design's ceiling claim as intended (checked as a byproduct —
  Neuvantila does not appear among any cluster's vendor keys below).
- **December/B6 month-cluster** — no calendar month reached the ≥ 15
  ungrouped-flags threshold in `prepare_clusters.py` step (c); 24
  vendor-level clusters (step b) already absorbed most of the volume before
  month-grouping ran. No `detector_month` unit was produced. This is a
  mechanical consequence of the pinned ordering (vendor-grouping runs before
  month-grouping) applied to the real flag distribution, not a defect in
  the cluster-prep code.

These are reported here exactly as design.md section 6 anticipated they
might need to be — frozen observations for the main-loop evaluation to
adjudicate against the answer key, not adjustments made by this script.

---

## 3. `code/prepare_clusters.py`

Implements the cluster rule in design.md section 6 exactly: (a) rule flags
group by vendor except calendar flags, which group by `posted_by`; (b)
detector flags group by vendor where ≥ 3 flags; (c) then by month where a
month still holds ≥ 15 ungrouped flags; (d) top 10 remaining detector
singletons by `anomaly_score` form one "notable singles" unit; (e)
everything left is one "residual tail" unit.

Two **independent** partitions are built and each is asserted complete and
disjoint on its own domain (every one of the 64 rule-flag rows into exactly
one `RU-*` unit; every one of the 200 detector-flag rows into exactly one
`DU-*`/`SINGLES`/`RESIDUAL` unit) — a transaction flagged by both layers
legitimately appears once in each partition, which is why design section 7
counts "264 designed flags (64 rule + 200 detector)" rather than a
deduplicated transaction count. Both assertions passed.

Deterministic ordering: rule-side units are `RU-01`…`RU-13` (11
`rule_vendor` units sorted by `vendor_id`, then 2 `rule_user` units sorted
by `posted_by`); detector-side grouped units are `DU-01`…`DU-24` (all 24
were `detector_vendor` — no month cleared the ≥15 threshold, see above);
`SINGLES` and `RESIDUAL` are singleton unit ids. Stats block per unit:
`n_flags`, `months_touched`, `total_eur`, plus `tests_involved` (rule
units) or `score_range` (detector units). `group_key` is `vendor_id`,
`posted_by`, `month` (int), or `null` for `SINGLES`/`RESIDUAL`.

### Result (as-run) — 39 units total

**Rule-side (13 units, 64 flags):**

| unit_id | type | key | n_flags | total_eur |
|---|---|---|---:|---:|
| RU-01 | rule_vendor | V-0006 | 8 | 36,934.24 |
| RU-02 | rule_vendor | V-0008 | 4 | 2,915.40 |
| RU-03 | rule_vendor | V-0009 | 4 | 10,291.20 |
| RU-04 | rule_vendor | V-0010 | 4 | 8,122.20 |
| RU-05 | rule_vendor | V-0011 | 6 | 41,000.00 |
| RU-06 | rule_vendor | V-0012 | 4 | 38,843.29 |
| RU-07 | rule_vendor | V-0013 | 4 | 24,566.55 |
| RU-08 | rule_vendor | V-0014 | 4 | 22,767.00 |
| RU-09 | rule_vendor | V-0015 | 2 | 13,330.75 |
| RU-10 | rule_vendor | V-0016 | 12 | 180,000.00 |
| RU-11 | rule_vendor | V-0018 | 2 | 14,840.00 |
| RU-12 | rule_user | U-031 | 2 | 3,101.15 |
| RU-13 | rule_user | U-117 | 8 | 7,504.66 |

**Detector-side (26 units, 200 flags):** 24 `detector_vendor` units
(`DU-01`…`DU-24`, vendors V-0029, V-0037, V-0041, V-0062, V-0067, V-0072,
V-0076, V-0078, V-0090, V-0098, V-0099, V-0110, V-0114, V-0118, V-0121,
V-0125, V-0131, V-0132, V-0135, V-0155, V-0156, V-0157, V-0176, V-0198;
flag counts 3–17, total_eur 1,267–66,828 each), zero `detector_month`
units, `SINGLES` (10 flags, 46,649.64 EUR), `RESIDUAL` (30 flags,
105,890.93 EUR).

Combined: 64 rule + 200 detector = **264 flags across 39 units**, matching
design section 7's headline exhibit shape exactly (64 rule + 200 detector).

`clusters.json` SHA-256 (two independent runs, identical):
`59e3091fb76be4aece052c0a3d4e9e954008f761b5a16f517945817fb7a237fe`

---

## Output checksums (this build)

| File | SHA-256 | Bytes |
|---|---|---:|
| `data/analysis/rule_flags.csv` | `ce3c3d070f134b1c7dc30576c2719b54150cb6d901d8c46803c6b54b6461d7b1` | 1,311 |
| `data/analysis/detector_flags.csv` | `d2face2f7779484ae86ca861b1439acb64f69cc493d14fc6991718332f2dd7f2` | 7,087 |
| `data/analysis/detector_scores.csv` | `7b0f6798fb106e48e853acacb369b0213fd2953111a5803bf8593c251f107512` | 1,585,711 |
| `data/analysis/clusters.json` | `59e3091fb76be4aece052c0a3d4e9e954008f761b5a16f517945817fb7a237fe` | 19,222 |

scikit-learn version used throughout: **1.9.0**.
