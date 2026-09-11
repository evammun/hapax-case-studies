# Financial Anomaly Detection — Design Document

Project 6 of the Hapax case-study portfolio. Theme 3: "The data storyteller."

Status: draft for Eva's review. Nothing downstream gets generated until this is signed off.

**[Reconciliation note, 11 Sep 2026]** Delivered and packaged 3 Jul 2026 — all six
phases complete (see the project `README.md`). The gate was proxy-passed by Luigi;
Eva's formal design-doc review is still owed (README "Open items"). Several
passages below describe *expected* outcomes as if the detector and the cluster
count had not yet run; they have, and several came out differently than
predicted. Nothing below is edited or deleted — every place where the as-run
result diverges from what this section anticipated is annotated in place,
pointing at the frozen deviation and `DECISIONS.md`'s 3 Jul 2026 entries, the
same reconciliation treatment `01 Churn/design/design.md` received.

Companion research: `audit_research.md` (sourced [S] vs inferred [I] throughout); running log: `DECISIONS.md`.

---

## 1. The story we are telling

A mid-size company's purchase ledger runs to fifty thousand rows a year. Nobody reads it. The audit answer is a set of standard rule tests; the data-science answer is an anomaly detector; both produce flags, and flags are not answers — most statistical outliers are a machine invoice, an insurance premium, or December. The expensive part was never the flagging. It is working out, for each flag, whether anything is actually wrong — and that is the part that has always been rationed by human attention.

The case shows three layers doing what each does best. Deterministic rule tests catch what audit practice already knows how to specify (duplicates, round sums, threshold games, weekend postings, mis-posted accounts — every implemented test traces to sourced practice, `audit_research.md` §1). An Isolation Forest catches what rules cannot specify in advance — a vendor whose invoices drift quietly upward. Storyteller agents then do the triage: cluster the flags, explain the ones that matter, and stand down on the ones that don't, with evidence either way. A wrong cause is worse than no cause; a false alarm is worse than silence.

This is the second Theme 3 case, and deliberately the mirror of Case 5: the board-reporting case is top-down (the pack asks *why*), this one is bottom-up (fifty thousand rows ask *which*, then *why*). It is also the literal demonstration of the advisory page's second exemplum — the agent sent through the ledger who finds that a vendor changed its invoicing, and that the useful number sat below the one being reported.

**Honesty framing (decided).** The dataset is synthetic and we say so prominently. Every planted anomaly *and* every planted benign exception lives in a held-out answer key, so all three layers — rules, detector, agents — are marked against ground truth, not trusted. One planted class is designed to be caught by nobody, and is reported as such. This is framed as controls and process quality, never "fraud detection".

**Primary reader (decided):** the buyer — CFO, controller, head of internal audit — with the technical depth present but skimmable.

**Deviation from the spec, flagged (Eva question 8):** `project_specs.md` frames the pipeline as Isolation Forest only. We add the deterministic rule layer in front of it, because most of the spec's own anomaly classes are rule-shaped, and a model-only pipeline would be dishonest about what audit practice already specifies. The rule layer is also where the case earns its Theme 2 kinship — deterministic first, model where rules run out, agents for the why.

---

## 2. The fictional company

**Saarnitukku Oy** (recommended; alternate candidate *Pihlajatukku Oy* — both collision-checked 3 Jul 2026, Eva question 1) — a technical wholesale and MRO distributor: fasteners, seals, tools, maintenance supplies for industrial customers. Vantaa head office plus Tampere and Kuopio branches. Roughly €90M revenue, ~180 staff, an AP team of four. Procurement peaks in November–December (customer year-end stocking) and troughs in July (kesäloma). Volume plausibility for ~50,000 purchase-ledger postings a year from ~200 vendors is reasoned in `audit_research.md` §3.5.

**How the ledger is posted — and why the calendar test is honest.** At this volume most invoices arrive as e-invoices and post through an integration: the system user `INTEG-01` carries ~80–85% of postings, and integration batches can land on any calendar day, which is why weekend rows from a system user mean nothing (`audit_research.md` §1.4's practice caveat, taken seriously rather than assumed away). The four AP staff hand-post the residue — manual invoices, corrections, one-offs — inside office workflows on working days. The calendar test therefore applies to **human posters only**; that is where a non-working-day posting is actually anomalous.

The sector is deliberately distinct from the other cases' fictional worlds (Kataja's SaaS, Paju's consumer products, Pyökkipaja's furniture manufacture), and a distributor's ledger is naturally dense and vendor-diverse, which is the raw material of this case.

**Vendors named in prose** (all individually collision-checked, DECISIONS.md 3 Jul 2026):

| Vendor | Role in the design |
|---|---|
| Teräskontio Oy | Steel/components supplier — carries the drift story (class G) |
| Kuormaraitti Oy | Freight carrier — the mirrored decline in the drift story |
| Kärrenbach Dichtungstechnik GmbH | German seals supplier — the name-variant trio (class V) |
| Mainostoimisto Kaarniala Oy | Advertising agency — the mis-posted account story (class A) |
| Neuvantila Oy | Consulting firm — the ceiling class (class C) |

**Name policy for the remaining ~193 vendors** (200 minus the seven story-carrying vendor records above): generated from a combinatorial Finnish scheme (common-noun compounds + standard suffixes), shipped with a blanket fictional disclaimer; any name later promoted into prose is collision-checked first. Only story-carrying vendors get individual external checks — checking two hundred generated names externally is neither practical nor useful.

**Approval tiers (declared convention, [I] — Eva question 10):** €10,000 (department head) and €50,000 (CFO). No authoritative Nordic norm exists (`audit_research.md` §3.4); the design says so plainly. Classes R and S are defined against the €10,000 tier.

---

## 3. The anomaly taxonomy and the catch matrix

Eight anomaly classes (the seven from `project_specs.md` plus the designed ceiling) and a declared benign ledger. **Planted anomalous transactions: 87 of 50,000 (0.17%).** All counts below are pre-registered; deviations at build or run time are reported and frozen, not tuned away.

### The classes

| Class | Mechanism | Txns | Designed catch |
|---|---|---|---|
| **D** — duplicate invoices | 6 re-submission pairs: the vendor re-sends an invoice copy after a week without payment confirmation and both get posted — same vendor, same amount, **4–7 days apart**, *different* invoice numbers; 3 vendors | 12 | **Rules** (duplicate test) |
| **R** — round sums near the tier | 2 vendors: 6 invoices at exact €1,000 multiples (€5k–€9k) + 4 in €9,500–9,999.99 | 10 | **Rules** (round-sum; near-threshold) |
| **W** — non-working-day postings | 8 postings by one user (U-117), Feb–Jun: five Saturdays, Easter Monday 21 Apr, Ascension 29 May, Midsummer Eve 20 Jun | 8 | **Rules** (calendar test) |
| **V** — vendor name variants | One real supplier existing as three master records — Kärrenbach / Kaerrenbach / KARRENBACH DICHTUNGSTECHNIK GMBH — shared VAT ID and address, distinct IBANs, spend split 7/5/3 | 15 | **Agents only** (free hunt) |
| **A** — mis-posted account | Kaarniala (advertising) invoices posted to the IT-services account by a new clerk (U-204), Sep–Oct | 8 | **Rules** (mapping test) |
| **G** — gradual drift *(the exemplum)* | Teräskontio: from July, freight is silently consolidated into goods invoices (+8% step, memo gains "sis. rahtikulut"), **and once freight sits inside the bundled price, the vendor's price rises become invisible** — a further +2%/month compounding, December ≈ +19% over baseline. Baseline invoice variance pinned tight (σ ≈ 3% of the vendor mean) so the elevation is unambiguous. **The euros reconcile by design**: Kuormaraitti's Teräskontio-lane freight billing declines from July by ≈ the step portion in euros (the answer key stores both sides; validated within a stated band) — the creep beyond the step is the separate, hidden mechanism | 12 (the elevated Jul–Dec invoices; the vendor's 12 H1 invoices are normal) | **Detector** (elevated `vendor_amount_z` pushes the late-month invoices into the flagged tail), then agents for the story **[Reconciliation note, 11 Sep 2026: this is the confident, expected mechanism, written before the detector first ran. As-run it did not hold — 0 of G's 12 elevated invoices were flagged (§3 line ~105, `DECISIONS.md` 3 Jul 2026), and all three blinded agent runs' free hunts also left the story unclaimed (0/3). The diagnosed cause: `vendor_amount_z` measures each invoice against the vendor's own full-year mean, so a sustained drift inflates its own baseline and erases its own signal — this is exactly the failure 06b's standing drift review was built to fix (see `design-06b-drift-report.md`).]** |
| **S** — split purchases | 5 events: one purchase split into two same-vendor invoices ≤3 days apart, parts €4,500–8,000 (non-round), sums €11k–15k vs the €10k tier; 3 vendors | 10 | **Rules** (split test) |
| **C** — the ceiling | Neuvantila: twelve unremarkable monthly consulting invoices (€3,800–5,600), correct account, correct cadence, mid-month weekdays. Catchable only with data this corpus does not contain (contracts, deliverables, three-way match) | 12 | **Nobody** — by design |

**Class V, the honest note:** duplicate-VAT-ID and fuzzy-name matching are canon hygiene tests and would catch V in production (`audit_research.md` §1.6). Our implemented rule set is the stated seven tests, and V is designed to slip through it — because the point is that any finite rule set has gaps, and cross-record reasoning is what covers them. The writeup states the production catch. Likewise **class C**: the production catch is PO/goods-receipt three-way matching, which is exactly the data this ledger does not carry — the case's stated epistemic limit.

**Class C is also a false-positive trap:** a run that accuses Neuvantila without evidence has failed the discipline test, and is scored as a false positive.

### The benign ledger (declared stand-down bank, 18 itemised transactions + one pattern)

| Item | What it is | Txns | Which layer flags it |
|---|---|---|---|
| B1 | Landlord rent, €15,000.00 by contract, monthly | 12 | Round-sum test |
| B2 | Inventory-count Saturday (15 Nov), agreed overtime, supervisor U-031, memo says so | 2 | Calendar test |
| B3 | Coincidental equal-amount pair — same vendor, €7,420.00 twice, 4 days apart, genuinely distinct deliveries (different invoice numbers and PO references in the memos) | 2 | Duplicate test |
| B4 | One-off capex: a machine at €78,400 (fixed-asset account, mapped) | 1 | Detector (top singleton) |
| B5 | Annual insurance premium, €24,600, January | 1 | Detector (top singleton) |
| B6 | December procurement peak | pattern | Detector (seasonal cluster — declared, not itemised) |

Every benign item lives in the answer key with its explanation (05's N4 lesson: the key declares everything designed, so a correct stand-down is creditable and a correct observation is never a false positive).

### The catch matrix (pre-registered arithmetic — audited by hand)

**Rule layer** (parameterisation in §6):

| Test | Anomalous flags | Benign flags | Total |
|---|---|---|---|
| Duplicate | 12 (D) | 2 (B3) | 14 |
| Round-sum | 6 (R) | 12 (B1) | 18 |
| Near-threshold | 4 (R) | 0 | 4 |
| Split | 10 (S) | 0 | 10 |
| Calendar | 8 (W) | 2 (B2) | 10 |
| Mapping | 8 (A) | 0 | 8 |
| Exact-name hygiene | 0 | 0 | 0 |
| **Total** | **48** | **16** | **64** |

No transaction trips two tests — a set of generation constraints, each auditable: R's round invoices sit outside the €9,500–9,999.99 band; S parts are non-round, **differ in amount within each pair** (evading the duplicate test), and individually sit outside the near-threshold band; **D pairs are 4–7 days apart** (outside the split test's ≤3-day window — this is why D's gap deviates from the spec's "2–5 days", noted below); W postings are otherwise ordinary; and the flagged vendors and users are **mutually distinct across classes** (3 D + 2 R + 3 S + A + B1 + B3 vendors and the W/B2 users are all different parties), which is also what makes the cluster count below exact. The validator asserts each test's flag count equals this table (§5, rule 9). Rule-layer arithmetic check: 48 anomalous rule flags = D 12 + R 10 + W 8 + A 8 + S 10 ✓; 64 − 48 = 16 benign ✓; anomalous transactions not rule-flagged = V 15 + G 12 + C 12 = 39; 48 + 39 = 87 ✓.

**Spec deviations in this table, stated:** the spec's duplicate example says "2–5 days apart" — ours are 4–7 days so the duplicate and split signatures stay disjoint; the spec's split example (€4,800 + €4,700 = €9,500) sums *below* the threshold — ours sum above the €10,000 tier, because a split that stays under the tier defeats no control and flags nothing. Both are design corrections, carried within Eva question 8's endorsement.

**Rule-layer designed precision vs the anomalous key: 48/64 = 75%** — deliberately not 100%; a quarter of a naive rule dump is legitimate, and triaging that quarter is the agents' scored work. **Stated so the rule layer is not a straw man:** 75% is a *first-pass* rule dump; a practitioner's second pass adds recurring-identical suppression (which silences B1 in week one) and materiality floors, and the writeup names those refinements — the triage burden is real, but it is the burden of a first pass, not the ceiling of rule-based practice.

**Detector layer:** contamination 0.004 → exactly 200 flags of 50,000 (spike-verified). Designed outcomes, **checked when the detector first runs at Phase 3 — a joint-space Isolation Forest cannot be guaranteed from single-feature bounds at generation time, so any miss is a frozen, reported deviation, not a retune**: ≥6 of G's 12 elevated invoices flagged; B4 and B5 flagged; **zero flags on C** (generation-side control: C's amounts are drawn tight around the vendor mean with ordinary cadence, so joint-space isolation is implausible; if the detector nonetheless flags a C transaction, the ceiling claim is weakened to "rule-invisible" and reported as such). Incidental detector flags on D/R/S/W/A members are permitted and recorded (overlap does not break any per-test arithmetic). The remaining ~185 flags are the December cluster (B6) and ordinary tail outliers — the stand-down mass that makes the false-positive-discipline exhibit real.

**[Reconciliation note, 11 Sep 2026 — as-run, `DECISIONS.md` 3 Jul 2026]** These were the pre-registered expectations, checked once and frozen, not adjusted afterward. The actual result: **G 0/12 flagged (pre-registered ≥6 — MISSED)**; **B4 0/1, B5 0/1 (expected top singletons — MISSED)**; **C 0/12 (zero-flag requirement — MET)**. The 200 detector flags overlap zero answer-key transactions — every designed positive catch failed, and the one designed negative held. Diagnosis (recorded at deviation time): `vendor_amount_z` measures against the vendor's own full-year mean, so a sustained drift inflates its own baseline and erases its own signal (Teräskontio's H2 z peaks at +2.13 against a clean-baseline estimate of ~+6.5); the pinned neutral edge-cases make single-invoice vendors invisible (B4/B5's only live signal was `log10_amount`); and a +19% shift on one tight-σ vendor is small against heavy-tailed organic amounts. `data/analysis/report.md` §1 carries the full confirmation. 06b (`design-06b-drift-report.md`) is the fix built directly from this diagnosis.

**Expected findings (the 2×2, Case 1/Case 5 convention):**

| | Real problem | Benign |
|---|---|---|
| **Flagged by a layer** | D, R, W, A, S (rules); G (detector) — agents must explain | B1–B5, B6, tail noise — agents must stand down |
| **Not flagged** | V (agent free hunt); C (nobody — the ceiling) | the other ~49,700 rows |

**[Reconciliation note, 11 Sep 2026]** This matrix was drawn up before the detector first ran. As-run, G moved from "flagged by a layer" to "not flagged" — the detector missed it (0/12, see the §3 reconciliation note above), so its discovery path shifted to the agents' free hunt, where all three runs also missed it (0/3, see below). **B4 and B5 also moved cells**: the detector never flagged either (0/1 each, expected top singletons), so both sit in "not flagged / benign" as-run rather than "flagged by a layer / benign" as designed — no verdict was expected or scored for them under the original pre-registered matching rules (`DECISIONS.md` 3 Jul 2026: "B4/B5 move from 'flagged benign, stand-down expected' to 'unflagged benign, no verdict expected' in the 2×2"). Marking still used the original pre-registered expectations, adjudicated with this context.

**Pre-registered run expectations (three blinded runs):** worry-with-correct-mechanism on D, R, W, A, S and on G's step itself — expected 3/3. G's full second-order story (the Kuormaraitti freight mirror) — expected ≥1/3, honestly uncertain (05 precedent: the sharpest designed evidence can go unclaimed). V found via free hunt — ≥1/3. Stand-downs on B1–B5 and benign detector clusters — 3/3. C findings — 0/3 (any Neuvantila accusation is a false positive). Target false positives: zero.

**[Reconciliation note, 11 Sep 2026 — as-run, `data/analysis/report.md` §§3–4]** G's step itself: **0/3**, not the expected 3/3 — no run's worry-with-correct-mechanism reached it, because the detector never surfaced it as a cluster and none of the three bounded free hunts drilled into a per-vendor H1/H2 movers sweep. G's second-order story (the Kuormaraitti mirror): **0/3**, the pre-registered ≥1/3 also missed. V found via free hunt: **3/3**, comfortably ahead of the ≥1/3 target, each run's top action item with the full mechanism. Stand-downs on B1–B5 and benign detector clusters: **3/3** held (all 26 detector units correctly stood down by every run, 78/78 verdicts). C findings: **0/3** held — the false-positive trap was not tripped. False positives actually recorded: 2 across 120 unit verdicts (both the same B3 hedge, adjudicated as false positives despite the designed distinct-PO evidence being present) — not the targeted zero, but small and diagnosed, not a design failure of the same order as G.

---

## 4. Data design

In-world period: calendar 2025 (aligned with Cases 3 and 5). `RANDOM_SEED = 42`; every tunable in `code/config.py`; byte-identical regeneration verified twice by SHA-256.

### Public tables (`data/`)

**`gl_transactions.csv`** (~50,000 rows — the purchase-ledger extract)
- `txn_id`, `posting_date`, `invoice_date`, `due_date`, `vendor_id`, `vendor_name`, `account`, `amount_eur`, `invoice_number`, `posted_by`, `memo`
- `vendor_name` is denormalised into the ledger on purpose — real GL extracts carry it, and the V-class is only visible if names appear where the work happens.
- `posted_by`: the integration user `INTEG-01` carries ~80–85% of rows; the rest are the named AP staff (§2). **Posting lag is pinned**: integration rows post 0–1 business days after `invoice_date`; human rows 2–5 business days (validator rule 13).
- **Year boundary (stated simplification):** all invoice dates and posting dates fall within 2025 — no December-2024 tail posting in January. A real ledger has one; modelling it adds a coherence surface without an exhibit, so it is declared out, alongside credit notes.
- Amounts are net of VAT; VAT accounting is out of scope, stated in one line in the writeup (the anomaly classes live in net postings; adding a VAT dimension multiplies coherence surface without adding a single exhibit).
- No credit notes in scope (stated; a production ledger has them — one more stated simplification).

**`vendor_master.csv`** (~200 rows)
- `vendor_id`, `vendor_name`, `country`, `vat_id`, `iban`, `address`, `terms_days` (∈ {14, 21, 30} — 14/30 [S], 21 [I]), `allowed_accounts`, `active_from`
- The V-trio: three records, near-identical names, shared `vat_id` and `address`, distinct IBANs.
- **Stated simplification:** apart from the V-trio, this master is clean — unique everything, no dormant records, no legacy duplicates. A real 200-record master is messier; the writeup says so (it is also why the dormant-vendor test has nothing to bite on here — §6 exclusions).

**`chart_of_accounts.csv`** (~40 rows)
- `account`, `name_fi`, `name_en`, `class` — anchored to the statutory expense-by-nature ranges (`audit_research.md` §3.2): 1xxx fixed assets, 4000–4399 purchases, 4400–4499 external services (freight, subcontracting, consulting), 5xxx–6xxx personnel, 7xxx+ other operating costs (premises, marketing, IT, insurance).

**`company_calendar.csv`** (365 rows)
- `date`, `is_working_day`, `note` — Finnish 2025 holidays [S], plus the declared company conventions (24 Dec and Midsummer Eve non-working). Public because the agents need it to judge calendar flags; the validator needs it for coherence.

### The answer key (`data/answer_key/anomalies.csv` — held out of every analysis path)

- `anomaly_id`, `class` (D/R/W/V/A/G/S/C/B1–B6), `kind` (anomalous | benign), `vendor_id`, `txn_ids`, `months`, `mechanism`, `designed_catch` (rules | detector | agent | nobody), `expected_verdict`, `expected_finding`, `notes`
- Completeness is a validator rule: every planted transaction id exists and matches; class counts match `config.py` and §3 exactly.

### As-built notes (Phase 2, 3 Jul 2026 — 05's as-built-calibration convention)

- Realised: 50,000 rows exactly; INTEG-01 posted 82.45% (band 80–85%); organic invoice dates ~90% working-day; INTEG-01's weekend-*posting* fraction ~15.6% (arithmetic of Friday+1-day and weekend-dated e-invoices — validator band [0.08, 0.23]).
- G as built: December mean ≈ +19.5% over the H1 baseline; H1 CV in the pinned band. **The euro reconciliation is per-invoice** (both vendors invoice twice monthly): Kuormaraitti's H1→H2 per-invoice decline €924.37 vs the €880.00 step portion (+5.0%, within ±15%). Kuormaraitti's H2 invoices still average ~€1,530 — the *base* delivery freight moved into Teräskontio's goods invoices; the residual is other freight services on the lane. Partial absorption, stated so the narrative arithmetic reads coherently.
- Memo order-references are an independent per-vendor numbering, decoupled from invoice numbers. **D-class pairs share one order reference across the pair** (different invoice numbers) — the discoverable re-submission evidence; **B3 carries two distinct PO references** — the discoverable distinct-deliveries evidence. The D/B3 contrast is symmetric by design.
- "All dates within 2025" is scoped to `invoice_date` and `posting_date`; `due_date` may run into January 2026 (a future obligation — realistic, untested). Rare late-December human-lag postings that would spill into 2026 fall back to same-day integration posting.
- The vendor master is cleaner than a real one (stated simplification, §4); rule 3's plausibility bands and rule 5's cadence guard are wide regression guards, not distribution assertions.
- Build history, decisions beyond the spec, and output hashes: `code/BUILD_NOTES_phase2.md`; review rounds in `design/DECISIONS.md`.

### Generation realism

- Per-vendor amount distributions (lognormal bands per archetype), cadences (weekly/fortnightly/monthly/sparse), payment runs on Tuesdays and Fridays [I, declared], month-end posting swell, November–December peak, July trough.
- Memos are thin deterministic template strings per vendor archetype (Eva question 3) — including the designed breadcrumbs (Teräskontio "sis. rahtikulut" from July; B2's "sovittu ylityö, inventaario"; B3's distinct PO references).
- `posted_by` from a small AP-staff roster; U-117 (class W) and U-204 (class A) exist in it with otherwise ordinary activity.

---

## 5. Coherence rules (non-negotiable, one validator check each)

`code/validate_ledger.py`, functions `check_rule_N_<slug>`, per-rule PASS/FAIL, `sys.exit(1)` on any failure (portfolio convention).

1. **Referential integrity** — every `vendor_id`, `account`, `posted_by` resolves to its master; every date within 2025.
2. **Working-day postings, human posters** — every *human-posted* `posting_date` is a working day per `company_calendar.csv`, except transactions declared in the key (W, B2). `INTEG-01` rows may fall on any day (batch behaviour, §2); their weekday mix stays within the designed distribution.
3. **Amount plausibility** — amounts positive, two decimals, within per-account-class bands.
4. **Terms consistency** — `due_date` = `invoice_date` + vendor `terms_days`, exactly.
5. **Cadence consistency** — per-vendor inter-invoice gaps within the archetype's tolerance band (except where a designed event says otherwise — G's H2, V's split spend).
6. **Seasonality** — monthly posting volumes within the designed profile bands (Nov–Dec peak, Jul trough).
7. **Invoice-number discipline** — strictly increasing per vendor, no reuse; D-class duplicates carry *different* invoice numbers by design (double-submission, not re-entry).
8. **Planted signatures at designed magnitude** — per class: exact counts; G's step and slope within band, its H1 clean, the Teräskontio baseline σ within its pinned band, **and the euro reconciliation holds** (Kuormaraitti's Teräskontio-lane H2 decline within a stated band of the step portion in euros); V's three spellings and shared VAT ID; C's twelve transactions within their tight amount band (a generation-side control — the detector-side zero-flag outcome is checked at Phase 3, §3); B-items as specified; and the story-carrying vendors and users mutually distinct across classes (§3's disjointness constraint).
9. **No undeclared signatures** — the rule engine (`rule_tests.py`, §6) runs inside the validator: every flag it raises must resolve to an answer-key entry, anomalous or benign, **and each test's flag count must equal §3's pre-registered total** (so a double-trip cannot pass silently). Constructively: the generator avoids accidental duplicate pairs (cent-jitter on repeat amounts within 7 days), exact €1,000 multiples ≥ €2,000 (cent perturbation unless planted), the €9,500–9,999.99 band (excluded unless planted), non-working-day dates for human posters, off-mapping accounts, and split-pattern windows (same-vendor ≤3-day groups summing ≥ €10,000 with parts ≥ €4,000); test 7's zero is guaranteed by rule 11's name-uniqueness, not by this rule. At 50,000 rows accidental signatures are statistically certain unless excluded by construction — this rule is the case's hard generation problem.
10. **Answer-key completeness and exactness** — every key `txn_id` exists; key class counts equal config counts equal §3 counts.
11. **Master hygiene except declared** — vendor names, IBANs, VAT IDs unique across the master except the V-trio as declared.
12. **Memo validity** — every memo derives from the template grammar; every designed breadcrumb memo present verbatim where the key says it is.
13. **Posting lag** — `posting_date` − `invoice_date` within 0–1 business days for `INTEG-01` rows and 2–5 business days for human-posted rows; all dates within 2025 (the stated year-boundary simplification).

---

## 6. Pipeline design

### The rule engine — `code/rule_tests.py` (built in Phase 2; the validator imports it)

Seven tests, every one traceable to sourced practice (`audit_research.md` §1), parameters fixed here:

1. **Duplicate**: same `vendor_id`, same `amount_eur` (exact), `posting_date` gap ≤ 7 days, different `invoice_number`.
2. **Round-sum**: `amount_eur` an exact multiple of €1,000 and ≥ €2,000.
3. **Near-threshold**: €9,500.00 ≤ `amount_eur` < €10,000.00 (within 5% below the €10,000 tier).
4. **Split**: same `vendor_id`, window ≤ 3 days, ≥ 2 invoices each < €10,000 and ≥ €4,000, sum ≥ €10,000.
5. **Calendar**: `posting_date` not a working day — applied to human-posted rows only (`INTEG-01` batch rows are exempt, §2).
6. **Mapping**: `account` ∉ vendor's `allowed_accounts`.
7. **Exact-name hygiene**: byte-identical `vendor_name` across distinct `vendor_id`s.

Declared exclusions (Eva question 8): Benford's law (out, with reasoning — `audit_research.md` §2); dormant-vendor reactivation (canon, no planted class, null test adds burden without an exhibit); fuzzy-name and duplicate-IBAN/VAT-ID hygiene (canon, deliberately left to the agents — §3, class V). All three stated in the writeup as production practice, alongside the second-pass rule refinements (recurring-identical suppression, materiality floors — §3's straw-man note).

### The detector — `code/detect_anomalies.py`

- Features per transaction (fixed here, 8, with edge cases pinned so Phase 2/3 has nothing to invent):
  1. `log10_amount`.
  2. `vendor_amount_z` — (amount − vendor's full-year mean) ÷ vendor's full-year std; vendors with < 5 transactions or std < €1 → 0.
  3. `cadence_ratio` — days since the vendor's previous invoice ÷ the vendor's median inter-invoice gap; a vendor's first transaction, or vendors with < 3 transactions → 1 (neutral).
  4. `day_of_week` — 0–6.
  5. `non_working_flag` — 0/1 per `company_calendar.csv`.
  6. `account_rarity` — 1 − (count of this account among the vendor's transactions ÷ the vendor's transaction count); single-transaction vendors → 0.
  7. `month_index` — 1–12.
  8. `vendor_month_volume_z` — (the vendor's transaction *count* in this transaction's month − the vendor's mean monthly count) ÷ the std of the vendor's 12 monthly counts; std = 0 → 0.
- `IsolationForest(n_estimators=200, contamination=0.004, random_state=42, n_jobs=1)` — spike-verified deterministic on the pinned environment (scikit-learn 1.9.0; DECISIONS.md). Contamination targets the spec's ~200-flag scale exactly.
- Run twice at Phase 3; output checksums must match.

### Cluster preparation (mechanical, pre-registered)

- Rule flags: grouped by vendor (all rule flags for one vendor form one cluster), except calendar-test flags, which group by `posted_by` (the story is the user, not the vendor).
- Detector flags: grouped by vendor where ≥ 3 flags; then by calendar month where a month still holds ≥ 15 ungrouped flags (this is what surfaces the December/B6 cluster); the top 10 remaining singletons by anomaly score form one "notable singles" list; and **everything left is one "residual tail" unit** that must receive its own aggregate verdict with evidence (distributional reasoning is acceptable evidence for a residual stand-down).

**[Reconciliation note, 11 Sep 2026 — as-run, `DECISIONS.md` 3 Jul 2026]** The month-grouping rule never fired: the mechanical vendor-grouping pass (≥ 3 flags) absorbed the detector's 200 flags into 24 vendor clusters before any single calendar month accumulated ≥ 15 ungrouped flags on its own — so no separate December/B6 month-cluster ever formed. B6 (the December procurement peak) is still a declared benign pattern in the answer key; it simply never became its own verdict unit under the rule as specified.

- Every flag therefore belongs to exactly one **verdict unit**; expected ≈ 20–22 units (13 rule-side; detector-side: G, the December month-cluster, a few vendor/noise clusters, the singles list, the residual). The exact list is produced mechanically at Phase 3 and recorded. Every unit receives a verdict from every run.

**[Reconciliation note, 11 Sep 2026 — as-run, `DECISIONS.md` 3 Jul 2026]** The mechanically produced list came to **39 verdict units** (13 rule-side; 24 detector-vendor clusters + the singles list + the residual — no month-cluster, per the note above), not the ≈20–22 estimated here. The ≈20–22 figure was a pre-Phase-3 estimate, not a pre-registered count with its own pass/fail gate; the rule that actually ran (vendor-grouping first, then month-grouping, then singles, then residual) is what was pre-registered, and 39 is its exact, mechanical output (`data/analysis/report.md` §3 confirms 39 units marked per run).

### The storyteller protocol (Case 5 method)

- Pinned briefing at `design/storyteller_briefing.md`, given verbatim to **three sequential, mutually blinded Opus subagent runs** (mechanism and tier per portfolio decision, 05 DECISIONS 2 Jul 2026; stated honestly in the writeup).
- Allowed inputs, whitelisted in the briefing: the four public CSVs + `rule_flags.csv` + `detector_flags.csv` + `clusters.json` — nothing else; no design documents, nothing under `answer_key/`, no decision logs, no other runs' folders. Each run ends its transcript with the list of every file it opened; the audit list is verified before the next run starts.
- Agents may run read-only pandas in their own scratch folder — the realistic workflow is computing over the ledger, not reading it.
- Output per run: `run_0N_findings.json` (per finding: `finding_id`, `headline`, `cluster_id` or `free-hunt`, `verdict` ∈ {worry, stand_down}, `mechanism`, `affected` {vendor_ids, accounts, months}, `evidence[]` with recomputable figures, `severity` ∈ {info, watch, act}, `confidence`, `recommended_action`) + `run_0N_memo.md` (one page, plain prose, British English; no claim not evidenced in the JSON).
- **Worry/stand-down is mandatory per cluster, with evidence either way; stand-down is a first-class answer.**
- **Free hunt, bounded:** at most 3 findings beyond the cluster list, each fully evidenced. The briefing lists the standard hygiene sweeps an analyst would run anyway (vendor-master duplicate review, monthly totals by account, top spend movers) without pointing at any answer.

---

## 7. Evaluation design

Two tiers, split explicitly (05's load-bearing distinction between mechanical scoring and adjudication):

**Tier 1 — fully mechanical, transaction-id matching only.** `code/evaluate.py` scores both detection layers against the key: recall per class per layer; precision per layer; precision per rule test (a single detector's false positives have no class, so per-class precision exists only rule-side). No prose parsing anywhere in tier 1.

**Tier 2 — the narrative worksheet + adjudication.** For the three runs: per-cluster verdict checks against the key's `expected_verdict` (matching rules stated verbatim in the worksheet); story-detection checks for G's step, G's freight mirror, and V (keyword + affected-entity rules, stated verbatim); figure verification of every `evidence[]` number against anchors recomputed fresh from the public CSVs (tolerance ±€50 absolute or exact for planted figures; ±0.1pp for percentages); unmatched findings listed for adjudication, never auto-scored. The final scorecard is `data/analysis/report.md`, hand-written from the worksheet — matcher artefacts adjudicated, not trusted (05's eighteen-disagreements lesson); everything that went wrong stays in (ml_report precedent).

**Headline exhibits:** the catch matrix as-run vs §3 as-designed; per-layer precision/recall; the triage table — all 264 designed flags (64 rule + 200 detector) partitioned into their ≈20 verdict units (§6), and per run: units correctly explained, units correctly stood down on, units wrongly verdicted; V and the free hunt; C reported as the ceiling; false positives (target: zero).

---

## 8. Mechanism honesty

The storyteller runs are Claude Code subagents (Opus), the current portfolio mechanism (05 DECISIONS, 2 Jul 2026); the writeup names the model. No cost figures are claimed — Theme 3's argument is the insight delta, not a cost curve; any figure quoted is a labelled subscription-based estimate. Real API calls (pinned inputs, reproducible scripts, logged token costs) remain the stated upgrade path. The rule engine and detector are free to re-run and deterministic on the pinned environment; the three agent runs are session artefacts whose variance is part of the story.

---

## 9. Deliverables

| Artefact | Where | Phase |
|---|---|---|
| This design doc + `audit_research.md` + `DECISIONS.md` | `design/` | 1 |
| `config.py`, `generate_ledger.py`, `rule_tests.py`, `validate_ledger.py` | `code/` | 2 |
| Public tables ×4 + `answer_key/anomalies.csv` | `data/` | 2 |
| `detect_anomalies.py`, cluster prep, `storyteller_briefing.md`, 3 run outputs, `evaluate.py`, worksheet, adjudicated `report.md` | `code/`, `design/`, `data/analysis/` | 3 |
| Analysis notebook (numbers read live, asserts on headlines, sensitivity ablation on contamination) | `notebooks/` | 4 |
| Interactive page — single self-contained HTML, embeddability constraints, `hpx-` prefix | `interactive/` | 5 |
| Long-form writeup + README + packaging | `writeup/`, root | 6 |

**Interactive page concept (Phase 5, built in the main loop):** the 12-month ledger as a flag timeline, rule flags and detector flags visually distinct; drill-down from any cluster to its transactions and to what each layer and each of the three runs said about it; the catch matrix as the centrepiece visual, designed vs as-run; the honest overlay — the benign bank the runs stood down on, the class nobody caught, and the one that only turned up when an agent went looking where no flag pointed.

---

## 10. Open questions for Eva

1. **Company name and sector** — Saarnitukku Oy, technical wholesale/MRO distribution (recommended); alternate name Pihlajatukku Oy. Both cleared.
2. **Corpus scale** — ~50,000 transactions, 12 months, ~200 vendors (the spec's numbers; volume plausibility reasoned in `audit_research.md` §3.5). Confirm.
3. **Memo text** — thin deterministic template strings incl. the designed breadcrumbs (recommended; keeps generation LLM-free and byte-identical). Or no memo column at all, which weakens G's discoverability and B2/B3's stand-down evidence.
4. **The ceiling class (C)** — comfortable publishing a planted anomaly that nothing catches, again (03's S-class precedent)? It is the honesty centrepiece.
5. **Public framing and title** — "controls and ledger anomalies" language throughout, never "fraud detection" (recommended; the memos and writeup describe process issues — double submissions, coding errors, threshold habits — not accusations).
6. **Positioning vs 05** — companion pair ("the data storyteller, top-down and bottom-up") or standalone?
7. **Run count** — three blinded runs (05 precedent). Confirm.
8. **The layered architecture and its exclusions** — rules first (a recorded deviation from the spec's model-only pipeline); Benford out; dormant-vendor test out; fuzzy/IBAN hygiene deliberately left to the agents. Endorse (or opt any back in — dormant is a cheap add if wanted with a planted class to match).
9. **GL shape** — recommended: the AP purchase-ledger extract at posting-line grain (net of VAT, no credit notes, both stated), which is the artefact an auditor actually pulls for payables testing. The alternative — a full double-entry journal — doubles row count with balancing lines that carry no story and would make several coherence rules heavier without adding an exhibit. Her controller eye decides.
10. **Approval tiers** — €10,000 / €50,000 as a declared invented convention (no authoritative Nordic source exists — stated honestly). Comfortable?

---

*Everything above regenerates from `code/config.py` at seed 42 once Phase 2 exists; the three storyteller runs are session artefacts, and their variance is part of the story. The answer key stays out of every analysis path — it exists so the results can be marked honestly.*
