# Phase 2 build notes — Anomaly Detection case study

Written by the implementing agent after `config.py`, `generate_ledger.py`, `rule_tests.py`
and `validate_ledger.py` were built and the acceptance gate passed. Read alongside
`design/design.md` (the spec) and `design/DECISIONS.md` (the project's running log, which
this file does not modify — decisions specific to the Phase 2 build live here instead).

## Acceptance gate results

1. **Determinism.** `generate_ledger.py` run twice from a clean `data/` directory. SHA-256 of
   all five output files identical across both runs:

   ```
   78e6aca0811c4602192f3ceb05c6e5da0f697d71f5e955e0ce9f5622e6aa38cc  data/gl_transactions.csv
   f36ed0a3b78e90e783ab2a072c3577266d1a748116b6113c8ff7d0d31bad1013  data/vendor_master.csv
   3d7f5bb9109ffbb9efbb7d11b71fc14e24f8513ef825c70f7cf121571276ab7d  data/chart_of_accounts.csv
   8faef97c370e278ac1b7e36a63927a451782e1930bba26b09f9081021386c14c  data/company_calendar.csv
   b5f51221404764f7227b49b45943d0f32b813c20d857e5dfa8f271d16ed0713a  data/answer_key/anomalies.csv
   ```

2. **`python code/validate_ledger.py` → all 13 rules PASS, exit code 0.**

3. **`python code/rule_tests.py` → per-test flag counts exactly match the pre-registered table:**

   | Test | Flags | Pre-registered |
   |---|---|---|
   | duplicate | 14 | 14 |
   | round_sum | 18 | 18 |
   | near_threshold | 4 | 4 |
   | split | 10 | 10 |
   | calendar | 10 | 10 |
   | mapping | 8 | 8 |
   | name_hygiene | 0 | 0 |
   | **total** | **64** | **64** |

   Zero transactions flagged by more than one test (the "no double-trip" property, design
   section 3), and every flagged `txn_id` is confirmed by `validate_ledger.py` rule 9 to
   resolve to an answer-key entry.

4. **Row and class counts.** `gl_transactions.csv` has exactly 50,000 rows. `vendor_master.csv`
   has 200 rows (7 story vendors + 193 generic-scheme vendors, of which 13 carry a reserved
   plant). `answer_key/anomalies.csv` class counts match `config.py` and design section 3
   exactly: D=12, R=10, W=8, V=15, A=8, G=12, S=10, C=12 (anomalous total 87); B1=12, B2=2,
   B3=2, B4=1, B5=1 (benign itemised total 18); B6 is the declared, non-itemised seasonal
   pattern.

   INTEG-01 posted 41,191 of 50,000 rows (**82.4%**), inside the designed 80–85% band. The
   six human staff split the remainder roughly evenly (1,415–1,534 rows each).

## Decisions made beyond the literal spec (smallest reasonable choice in each case)

These are documented here per the build brief's instruction to record anything decided
where the spec was silent. None change the pre-registered arithmetic in design section 3.

1. **Year-boundary safety in the business-day search.** `company_calendar.csv` only covers
   2025. A small number of very-late-December invoice draws with a human posting lag would
   otherwise search forever for a working day in "2026" (which the calendar doesn't contain),
   overflowing `datetime.date` arithmetic. Fixed with a hard iteration cap on the search
   functions (`add_business_days`, `find_invoice_date_for_target_posting`) and a fallback:
   if the computed posting_date would land outside 2025, the transaction is posted same-day
   by INTEG-01 instead of by the originally-chosen human staffer. This is a rare edge case
   (only invoice dates in the last handful of December calendar days can trigger it) and is
   consistent with design section 4's stated year-boundary simplification (all invoice and
   posting dates fall within 2025). Read `choose_posted_by_and_posting_date()`'s docstring.

2. **"Every date within 2025" (rule 1) is checked on `invoice_date` and `posting_date`
   only, not `due_date`.** Design section 4 explicitly scopes the year-boundary
   simplification to invoice and posting dates; `due_date` = `invoice_date` + `terms_days`
   (up to 30 days) can and does spill into early January 2026 for late-December invoices,
   which is realistic (a future payment obligation) and not itself tested.

3. **Chart of accounts.** Built a concrete ~40-account CoA (39 rows) anchored to the ranges
   in `audit_research.md` §3.2, with real Finnish account names. Personnel accounts
   (5xxx–6xxx) exist for chart-of-accounts realism and referential-integrity completeness
   but never receive postings — this is a purchase ledger, not a full GL, and vendor
   invoices don't post to payroll accounts.

4. **Pure-filler vendor archetypes.** Invented five categories (`goods_small`,
   `goods_bulk`, `external_services`, `other_operating`, `sparse_rare`) with lognormal
   amount parameters and a per-vendor Gamma-distributed monthly rate (right-skewed, so a
   few vendors carry much more volume than most — audit_research.md §3.5's "concentrated
   in core suppliers"). Category monthly-rate means were tuned so organic generation lands
   close to the 50,000 target before the deterministic filler top-up (final organic total
   ~46,700; top-up added ~3,300 rows spread across the 8 busiest pure-filler vendors, not
   dumped onto one — see item 8).

5. **D/R/S host-vendor splits.** Not pinned by the brief beyond vendor counts, so: D's 6
   duplicate pairs split 2 pairs/vendor across its 3 vendors; R's 6 round-multiple invoices
   go to one vendor and its 4 near-threshold invoices to the other; S's 5 split-purchase
   events split 2/2/1 across its 3 vendors. Reserved vendor IDs V-0008..V-0020 (13 records:
   D×3, R×2, S×3, B1, B2, B3, B4, B5).

6. **Kaarniala's entire annual invoice history is the 8 planted mis-posted transactions.**
   The brief describes only the mis-posted Sep–Oct invoices; no separate "correctly posted"
   baseline is invented, since design doesn't establish one and inventing one would be
   undeclared scope.

7. **Kuormaraitti is modelled as a single-purpose freight carrier for the Teräskontio lane
   only** (2 invoices/month, all year, baseline mean €2,400) — the design doc gives it no
   other role, so every one of its invoices is "the Teräskontio lane" by construction, which
   is what makes the euro reconciliation in validator rule 8 unambiguous. Realised H1→H2
   decline is €924.37 against a step of €880.00 (+5.0%, well inside the ±15% band).

8. **B1/B2/B3/B4/B5 given specific, thematically-fitting generic-scheme names** (a
   property company, a staffing/inventory-labour firm, a tools wholesaler, a machinery
   supplier, an insurance broker) rather than pulling anonymous names from the combinatorial
   pool, since each plays a distinct, recognisable role in the story.

9. **Posting mechanics for the reserved plant classes.** D and S transactions are posted by
   INTEG-01 with zero lag (`posting_date = invoice_date`), which gives exact, trivial control
   over the posting-date gaps the rule tests actually check (D: 4–7 days; S: ≤3 days) without
   needing business-day arithmetic. B2 (human, U-031) and B4/B5 (human, U-058) have their
   `posting_date` pinned to a specific date and `invoice_date` back-derived via a business-day
   search so the 2–5 business-day human lag rule is satisfied exactly.

10. **Rule 9's "no accidental signature" construction — the hard generation problem, per
    design section 5.** Implemented as: (a) a per-transaction draw-time guard that nudges
    any amount landing on an exact €1,000+ multiple or in the €9,500–9,999.99 band away from
    it, unless the transaction is a designed plant; and (b) a same-vendor pairwise collision
    fix for the duplicate and split signatures. **This second piece is keyed on
    `posting_date`, not `invoice_date`** — the rule tests window on `posting_date` (design
    section 6), and posting lag can move a transaction several calendar days from its
    invoice date, so fixing collisions by invoice-date proximity neither catches nor
    reliably reproduces what the rule tests see. (This was the main thing that fought back —
    see below.) Proportional amount scaling (×0.55) was tried first as the fix for a caught
    split-pattern collision and found insufficient: amounts already close to the €10,000
    ceiling can stay inside the [€4,000, €10,000) band after a 0.55× cut. The fix instead
    redraws the smaller amount of a colliding pair to a safe low range (€400–3,600), which
    guarantees it can never re-trigger the split test regardless of its original magnitude.

11. **The exact-50,000-row filler adjustment is spread across the 8 busiest pure-filler
    vendors**, not dumped onto one (`config.N_FLEX_VENDORS = 8`). An early version added the
    entire ~16,700-row shortfall to a single vendor, which would have made that vendor look
    absurdly dominant (nearly 100x an ordinary vendor's volume); retuning the category rates
    (item 4) brought the organic total close enough to the target that the top-up per flex
    vendor is now a modest ~400–425 rows, roughly a 30–60% increase on top of what each of
    those vendors already had.

12. **Amount plausibility bands (validator rule 3)** are invented, generous per-account-class
    ranges (design doesn't pin figures): €1–100,000 for purchases/external
    services/other operating/personnel, €1–200,000 for fixed assets.

13. **Cadence consistency (validator rule 5)** is implemented as a loose statistical guard
    (no vendor has a single inter-invoice gap over 300 days) rather than a tight per-archetype
    band, since design doesn't pin a numeric tolerance and a stricter check would risk failing
    on legitimately sparse vendors. Observed maximum gap in the final dataset is 181 days
    (a `sparse_rare`-category vendor); no vendor exceeds 300 days.

14. **`rule_tests.py` has no dependency on `config.py`** (per the brief's "pandas+stdlib
    only" constraint) — its seven numeric thresholds are restated as module-level constants
    that mirror `config.py`'s `RULE_*` values and design section 6 exactly. If either file
    is edited, the two must be kept in sync by hand; `validate_ledger.py` rule 9 would catch
    a drift (the pre-registered counts are asserted against `rule_tests.py`'s actual output).

15. **`vendor_master.csv`'s `allowed_accounts` column** stores one or two account codes
    joined with `;` (e.g. `4100` or `4100;4310`). `answer_key/anomalies.csv`'s `vendor_id`,
    `txn_ids` and `months` columns are likewise `;`-joined where multi-valued. The `G` class
    answer-key row's `notes` field carries the Kuormaraitti corroborating-evidence data
    (its vendor_id, H1/H2 `txn_id` lists joined with `|`, the step-euro figure and the
    reconciliation tolerance) in a `key=value;key=value` format, since the schema has no
    second-vendor column and Kuormaraitti's decline is evidence for G's story rather than
    its own answer-key row.

16. **CSV writing.** All five files are written via an explicit `open(path, "w", newline="")`
    handle with `lineterminator="\n"` and `float_format="%.2f"`, per the determinism
    discipline (no CRLF, amounts at a fixed two decimals on disk). The `account` column
    reads back as `int64` via `pd.read_csv` (no account code has a leading zero, so this is
    lossless) — noted here in case a downstream script assumes it reads as a string; several
    Phase 2 scripts (`rule_tests.py`, `validate_ledger.py`) `str()`-cast it before comparison.

## What fought back

- **The year-boundary `OverflowError`** (item 1 above) — the first full-scale run crashed
  partway through pure-filler generation. Traced to a specific vendor (`V-0023`) whose
  business-day-lag search walked forward from a late-invoice_date and never found a working
  day because the calendar set only covers 2025.
- **The organic generation volume was badly under-tuned on the first pass** (33,128 rows
  against a ~49,867 target before the fixed/story/plant rows), which the deterministic filler
  step "corrected" by dumping nearly 17,000 rows onto a single vendor. Retuned the five
  category `monthly_rate_mean` values (roughly ×1.28) to bring the organic total to ~46,700,
  and changed the filler step to spread its top-up across 8 vendors instead of 1.
- **The real fight: `rule_tests.py`'s `split` test initially returned 142–154 flags instead
  of the pre-registered 10.** Root cause was the invoice-date-vs-posting-date mismatch in
  item 10 above, compounded by an under-strength fix (proportional scaling instead of a
  guaranteed-safe redraw) and a gap in the filler-adjustment path (a vendor's organic batch
  and its top-up batch were each individually collision-fixed but never checked against each
  other after being concatenated — fixed by `rescrub_amounts()`, which re-runs the collision
  fix across a vendor's *combined* transaction list). All three pieces needed fixing together
  before the rule engine's per-test counts converged exactly on 14/18/4/10/10/8/0.
- **`pandas.itertuples()` rejects a column named `_posting_dt`** (leading underscore) in
  `rule_tests.py`'s windowing helper — renamed to `posting_dt`.

## Files delivered

- `code/config.py` — every tunable (seed 42, vendor archetypes, ~40-account CoA, 2025
  company calendar, seasonality weights, approval tiers, every planted class and benign
  item's exact placement, the pre-registered per-test and per-class count tables).
- `code/generate_ledger.py` — writes `data/gl_transactions.csv` (50,000 rows),
  `data/vendor_master.csv` (200 rows), `data/chart_of_accounts.csv` (39 rows),
  `data/company_calendar.csv` (365 rows), `data/answer_key/anomalies.csv` (14 rows).
- `code/rule_tests.py` — the seven rule tests, pandas + stdlib only, no answer-key access,
  importable (`run_all_rule_tests(gl_df, vendor_master_df, calendar_df) -> DataFrame`).
- `code/validate_ledger.py` — all 13 coherence rules, `sys.exit(1)` on any failure.

---

## Fix round (main-loop review), 3 July 2026

Personal review of the Phase 2 build found five issues, all fixed in this round. All four
regenerated-from-scratch outputs below supersede the ones recorded earlier in this file.

1. **Restored diacritics everywhere.** The original build had silently ASCII-folded every
   Finnish/German/Swedish string (`config.py`'s vendor-name components, chart-of-accounts
   names, memo templates, holiday notes, addresses) and — the actual spec violation — the
   Kärrenbach trio's *primary* spelling was `Karrenbach` instead of `Kärrenbach`, which is
   the whole point of the V-class mechanism (design section 3: three spellings, one with the
   umlaut). Fixed:
   - `Teräskontio Oy`, `Kärrenbach Dichtungstechnik GmbH` (primary, with ä; the other two
     variants — `Kaerrenbach Dichtungstechnik GmbH` and `KARRENBACH DICHTUNGSTECHNIK GMBH`
     — stay diacritic-free on purpose, since that *is* the variant mechanism), `Kiinteistö Oy
     Vantaan Teollisuustalo`, `Konepaja Ristimäki Oy`, `Industriestraße 14, 22525 Hamburg,
     Germany`.
   - Memo templates: `Terästoimitus`, `Terästoimitus, sis. rahtikulut, ...` (breadcrumb itself
     kept exactly `sis. rahtikulut`, unchanged — no diacritics in those two words anyway),
     `Rahtikuljetus, Teräskontio-erät, ...`, `Sovittu ylityö, inventaario 15.11.2025`.
   - Finnish month names `kesäkuu`, `heinäkuu` (the other ten were already correct without
     diacritics — real Finnish spelling, not a translation gap).
   - Chart of accounts (`Keskeneräiset`, `Kuljetusvälineet`, `hyödykkeet`, `Teräs- ja
     metallituotteet`, `Työkalut`, `Henkilösivukulut`, `Eläkevakuutusmaksut`,
     `henkilöstökulut`, `näyttelyt`, `jätehuoltopalvelut`), the generic name-component pools
     (`väline`, `järjestelmä`; swapped two non-words — `Poru`, `Uunio` — for real Finnish
     words, one of them diacritic-bearing: `Pora`, `Säiliö`), address components
     (`Terästie`, `Jyväskylä`, `Industriestraße`/`Werkstraße`/`Bahnhofstraße`, `Göteborg`/
     `Malmö`/`Norrköping`, `Lagervägen`).
   - `validate_ledger.py` rule 12's memo regex whitelist updated to match (also picked up the
     6-digit invoice-number width from fix 2, see below).
   - Verified `name_hygiene` is still exactly 0 after the fix — `Kärrenbach`, `Kaerrenbach`
     and `KARRENBACH DICHTUNGSTECHNIK GMBH` remain three byte-distinct strings.
   - All five output files confirmed BOM-free, valid UTF-8 (`open(path, 'rb')` header check
     plus a full-file UTF-8 decode). `write_csv()` already used `encoding="utf-8"` — Python's
     plain UTF-8 codec never emits a BOM (that's `"utf-8-sig"`), so this needed no code change,
     only the string-content fixes above.
   - Aside: printing vendor names to a `tail`-piped log in this Bash environment displays as
     mojibake (e.g. `Ter�skontio`) because the pipe's terminal codepage isn't UTF-8. This
     is a *display* artefact only — verified by reading the raw file bytes directly
     (`\xc3\xa4` is exactly correct UTF-8 for `ä`) and by writing decoded strings to a file
     and reading them back with the file-reading tool. The CSVs on disk were never affected.

2. **Per-vendor invoice-number offsets.** Every vendor previously started numbering at 1 (an
   artefact — real vendors serve other customers too). Fixed: a new seeded RNG stream
   (`invoice_offsets`) draws one deterministic starting offset per vendor, uniformly from
   [1,000, 950,000], in the fixed 200-vendor ordering already used for `vendor_master.csv`
   (`all_vendor_ids_ordered`, hoisted earlier in `main()` so both the offset draw and the
   vendor-master assembly share one canonical list instead of two copies of the same
   construction). Invoice numbers now run consecutively from that offset
   (`offset + cumcount`), formatted at 6 digits (`f"{n:06d}"`, up from 5) — offset up to
   950,000 plus the busiest vendor's ~1,800-2,000 annual transactions comfortably fits in 6
   digits with room to spare. `validate_ledger.py` rule 7 rewritten to assert
   strictly-increasing, unique, and **consecutive from an arbitrary start** (not `1..N`), plus
   a sanity check that every vendor's starting offset falls in [1000, 950000].

3. **Invoice-date weekday weighting.** Organic invoice dates were drawn uniformly across all
   seven weekdays (~14.3% per day) — unrealistic; a vendor issuing an invoice is far more
   likely to date it on a working day. Fixed: a new `weighted_invoice_day()` helper computes,
   independently for each month, a working-day weight and a weekend-or-holiday weight such
   that ~90% of that month's draws land on a working day and ~10% on a weekend or holiday
   (`INVOICE_DATE_WORKING_DAY_SHARE = 0.90`), then draws via `rng.choice` with those
   per-day probabilities. Applied to pure-filler vendor generation (`generate_filler_stream`,
   both the organic and filler-adjustment branches) and the Kärrenbach trio
   (`generate_karrenbach`) — the two generators that draw organic, unplanted invoice dates.
   Planted classes with pinned dates (D, R, S, W, B1-B5, G, A) are untouched, as instructed.
   Realised on the reference run: overall invoice-date non-working fraction = 10.0% (exactly
   on target). `validate_ledger.py` rule 2's INTEG-01 weekend-posting-fraction band was
   re-derived from this new reality rather than left at the old uniform-date assumption: the
   realised fraction is 15.6% (INTEG-01's 0-1 calendar-day lag shifts the ~9.2% weekend share
   of invoice dates upward a little, since a Friday + 1 day lands on Saturday); the new band
   is `[0.08, 0.23]`, wide enough for ordinary regeneration variance but tight enough to catch
   a regression toward either the old ~28% (uniform dates) or ~0% (an accidental weekday-only
   constraint).

4. **Answer key re-grained to event level.** Was one row per *class* (8 anomalous + 6 benign
   = 14 rows); is now one row per *event*: `D-01`..`D-06` (each duplicate pair), `R-ROUND` and
   `R-NEAR` (the two distinct sub-mechanisms sharing class `R`), `S-01`..`S-05` (each split
   event), `W-01`, `V-01`, `A-01`, `G-01`, `C-01` (each already a single event, renamed for
   consistency), `B1`-`B5`, `B6` — 24 rows total, exactly matching the pre-registered count.
   Every row keeps a `class` column so class-level aggregation is a one-line groupby.
   Mechanics: `generate_D`/`generate_S` now tag each pair/event with an event-level
   `_plant_tag` (`D-03`, `S-02`, ...) instead of the class-level tag; `generate_R` splits its
   tag into `R-ROUND`/`R-NEAR`; `build_answer_key()` emits one row per event, computing
   `vendor_id`/`txn_ids`/`months` from that event's own transactions (the G row keeps its
   Kuormaraitti corroborating-evidence `notes` field verbatim). `validate_ledger.py`'s
   `answer_key_txn_ids(answer_key, class_name)` helper now filters on the `class` column and
   **aggregates txn_ids across every event row sharing that class** — every existing call
   site in rules 2/8/9/12 already passed a class name (`"D"`, `"S"`, `"W"`, ...), so this one
   change made them all correct again without touching the call sites themselves. Two call
   sites that had iterated over the (now finer-grained) `anomaly_id` column directly — rule
   9's "every flag resolves to a key entry" gather and rule 10's "every key txn_id exists"
   check — were rewritten to use a new `answer_key_all_txn_ids()` helper (every txn_id in the
   key, regardless of grain) and a direct per-row iteration respectively, since passing an
   event id like `"D-03"` into a class-keyed lookup would silently return nothing. Rule 10
   also gained a row-count assertion (`== 24`).

5. **Rule 9 strengthened with per-test flag membership.** Beyond the existing per-test
   *counts* check, rule 9 now asserts **exact set equality** between each rule test's flagged
   `txn_id` set and its expected answer-key set: `duplicate == D ∪ B3`, `round_sum == R-ROUND
   ∪ B1`, `near_threshold == R-NEAR`, `split == S`, `calendar == W ∪ B2`, `mapping == A`,
   `name_hygiene == ∅`. The R-ROUND/R-NEAR distinction needed a new
   `answer_key_txn_ids_by_event()` helper (exact `anomaly_id` lookup) since the class-level
   helper would merge them under `"R"`. All seven sets matched exactly on the first run after
   the fix — no membership mismatches, confirming the count-level PASS from before wasn't
   hiding a same-size-wrong-members coincidence.

### Regenerated acceptance gate (post-fix)

1. **Determinism** — two clean-`data/` runs, SHA-256 identical:

   ```
   66faefcdacf39d4740479c4e7218bf5b987d379248c422118e618665b0eccff6  data/gl_transactions.csv
   6cbba30c58c99050f8aff93f1783135e9d465afbbd775651ef956ff5475d241b  data/vendor_master.csv
   59f644fe8e735db9c3567cf9186867256747578af5d498bcf668523ba702514a  data/chart_of_accounts.csv
   e08c46bb555a785344bf08dd8a22129050cc430c6ce92107f4139ff01b7cfc08  data/company_calendar.csv
   b74290134c24c0ccbeead3358c65a36f1deddaf1b1f7c43bb5ac8c8c1b424200  data/answer_key/anomalies.csv
   ```

2. **`python code/validate_ledger.py`** — all 13 rules PASS, exit 0 (rule 9's new membership
   checks and rule 10's new row-count check included).
3. **`python code/rule_tests.py`** — per-test counts unchanged and still exact:
   duplicate 14 / round_sum 18 / near_threshold 4 / split 10 / calendar 10 / mapping 8 /
   name_hygiene 0 = 64 total, zero double-trips.
4. **Row/class counts** — `gl_transactions.csv` still exactly 50,000 rows;
   `answer_key/anomalies.csv` now 24 event rows, class-level aggregates unchanged (D=12,
   R=10, W=8, V=15, A=8, G=12, S=10, C=12, B1=12, B2=2, B3=2, B4=1, B5=1).
5. **INTEG-01 share** — 82.45% (within the designed 80-85% band; barely moved from the
   pre-fix 82.4-82.5%, since the weekday-weighting change only touches which day within a
   month an invoice is dated, not the INTEG-01/human posting-split probability).
6. **New INTEG-01 weekend-posting fraction** (rule 2) — 15.6%, banded at `[0.08, 0.23]` (see
   fix 3 above for the derivation).

---

## Fix round 2 (main-loop review, memo/invoice decoupling), 3 July 2026

Spot-read found one more issue: the memo `{ref}` token echoed `invoice_number` everywhere.
Two problems: (a) it undermined the D-class re-submission story — a re-sent invoice should
reference the *same* underlying order on both pair members, which is the evidence that
distinguishes D (worry) from B3 (stand-down, genuinely distinct PO references) — and (b)
ledger-wide, order-ref == invoice-number is a synthetic tell an agent could spot immediately.

**Fix, implemented in `generate_ledger.py` only** (no config.py or rule_tests.py changes
needed; validate_ledger.py's memo regexes were checked and did not need to change — same
template shapes, just a different number source):

1. **Decoupled memo order-refs from invoice numbers, globally.** Added a new named RNG
   stream (`order_refs`) and a second per-vendor seeded offset,
   `order_ref_offset_by_vendor`, drawn independently from `invoice_number_offset_by_vendor`
   over the same fixed 200-vendor ordering. New `assign_order_refs(df, offset_by_vendor)`
   walks the already vendor/date-sorted dataframe once and assigns each row its own
   consecutive order-ref counter value from that vendor's offset — a fully independent
   numbering system from `invoice_number`, 6-digit formatted the same way. The memo `{ref}`
   token is now `order_ref`, not `invoice_number`, everywhere a template uses it
   (`finalise_memo`).
2. **D-class pairs share one order ref.** `assign_order_refs` special-cases `_plant_tag`
   values starting with `D-`: the first occurrence of a given D-event tag consumes the
   vendor's counter as normal, but the second occurrence (the pair's other member) reuses
   the same value without advancing the counter. Both invoices in a duplicate pair now carry
   the identical `tilaus NNNNNN` order reference in their memos, with different
   `invoice_number`s — spot-checked directly (e.g. D-01: both members read
   `Ostolasku, tilaus 358022`, invoice numbers 801524/801525). `build_answer_key()`'s D-row
   loop now reads the pair's shared `order_ref` back out of `df` and states it verbatim in
   both `mechanism` and `notes`, naming it as the discoverable evidence and contrasting it
   explicitly with B3's two distinct PO references.
3. **B3 unchanged** — its memo is built directly from `config.B3_PO_REFS`
   (`MEMO_B3_GENERIC.format(po_ref=...)`), never touches `order_ref` or `invoice_number` at
   all, so the fix required no change there. Re-verified: `PO-48213` / `PO-48297`, still
   distinct, still on distinct invoice numbers.
4. **Rule 12 memo regexes** — checked, left as-is. The template shapes are unchanged (still
   `\d{6}` — order_ref is 6-digit formatted exactly like invoice_number was); only the
   *number that fills the slot* changed, which the regex doesn't distinguish.

### Regenerated acceptance gate (post-fix)

1. **Determinism** — clean `rm -rf data/` succeeded both times this round (no Dropbox lock
   hit); SHA-256 identical across two clean runs:

   ```
   759a585e6d4ce00c60fee663f23407f923394110d60289ddd22006c161c0d0f2  data/gl_transactions.csv
   6cbba30c58c99050f8aff93f1783135e9d465afbbd775651ef956ff5475d241b  data/vendor_master.csv
   59f644fe8e735db9c3567cf9186867256747578af5d498bcf668523ba702514a  data/chart_of_accounts.csv
   e08c46bb555a785344bf08dd8a22129050cc430c6ce92107f4139ff01b7cfc08  data/company_calendar.csv
   0ba34ab4d75985eca1a5829339b174ea617c6289dc7cf18977b713a006ed92ba  data/answer_key/anomalies.csv
   ```

   `vendor_master.csv`, `chart_of_accounts.csv` and `company_calendar.csv` hash identically
   to the previous fix round (expected — this fix touches only memo text and the D answer-key
   rows' prose, not vendor identities, accounts, or the calendar); `gl_transactions.csv` and
   `answer_key/anomalies.csv` changed, as expected.
2. **`python code/validate_ledger.py`** — all 13 rules PASS, exit 0.
3. **`python code/rule_tests.py`** — per-test counts unchanged: 14/18/4/10/10/8/0 = 64,
   zero double-trips (order-ref/memo text plays no role in any rule test, so this was
   expected to be a no-op for the rule engine — confirmed).
4. **Row/class counts** — `gl_transactions.csv` still exactly 50,000 rows;
   `answer_key/anomalies.csv` still 24 event rows.
5. **INTEG-01 share** — 82.45%, unchanged (within the designed 80-85% band).
