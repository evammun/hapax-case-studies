# Board Reporting Automation — Design Document

Project 5 of the Hapax case study portfolio. Theme 3: "The data storyteller."

Status: **signed off by Eva, 2 July 2026** ("go", relayed by Luigi — recommendations in §7 adopted as proposed, churn "go for it" precedent). Open question 7 (a story from life) remains open; it can be added as a fifth story later without disturbing S1–S4. Phase 2 (generation) may proceed.

---

## 1. The story we are telling

Every month, a competent finance team produces the board pack: variances computed, KPIs tracked, thresholds flagged. The pack says *what* moved — "material costs up 12%, gross margin down 2pp" — and it is right. What it rarely says is *why*, because the why lives three drill-downs deeper than anyone has time to go before the board meeting. So the obvious explanation gets written into the commentary ("input cost inflation"), the meeting moves on, and the real cause — a promotional mix shift in one product line — keeps quietly eating margin for another two quarters.

The case study shows both layers working together: deterministic variance analysis (pandas — fast, exact, free) produces the numbers, and storyteller agents are then turned loose on the underlying data to find the causes behind them, and to say when a scary-looking number needs no story at all. The point is not that agents replace the variance analysis. The deterministic layer is genuinely good — we build it properly and let it set the baseline. The point is the **delta**: the causes the pack cannot see, found and evidenced in language a board can act on.

**Honesty framing (churn precedent):** the dataset is synthetic and we say so prominently. Four stories are engineered into a driver-based financial model with a known answer key, precisely so we can *mark* what the agent layer finds and what it misses, rather than asserting it. One of the four is a trap: a number that looks alarming and isn't. An agent that cries wolf there fails the test, and we publish that result whichever way it lands.

**Primary reader (churn precedent):** the buyer — CFO / COO / Head of FP&A — with the technical depth present but skimmable. This is the case study closest to WS3 (AI for Finance and Controlling) and the one Eva can present entirely from her own world.

---

## 2. The fictional company

**Paju Consumer Products Oy** *(name provisional — see open question 1)* — a Turku-headquartered manufacturer of personal-care and home-care products, selling through grocery and pharmacy retail across Northern Europe, plus a professional (salon and distributor) channel. Founded in-world in the 1980s, family-owned, ~480 FTE. Deliberately not a SaaS company and deliberately not Kataja Analytics — this is a business with factories, materials, promotions, and retailers who squeeze.

**Scale (FY2024, the first in-world year):** net revenue ~€152M, gross margin ~42%, EBITDA ~11%, ~480 FTE (revenue per head ~€317k). All tunable in config; Eva should correct anything that smells wrong (open question 2).

### Structure — the shared spine

Three geographic business units, four product lines present in each. Every table in the dataset lives on this grid; it is the coherence mechanism, as the feature map was for churn.

| Business unit | Markets | ~% of net revenue | Character |
|---|---|---|---|
| **Nordics** | FI, SE, NO, DK | ~55% | Home market, mature, promo-driven grocery trade |
| **Central Europe** | DACH, Benelux | ~25% | Export market, few large wholesale customers, long payment terms |
| **Baltics & Poland** | EE, LV, LT, PL | ~20% | Growth market, price-competitive, discount-hungry retail |

| Product line | ~% of net revenue | Material cost (% of net revenue) | Seasonality |
|---|---|---|---|
| Hair Care | ~30% | ~30% | Q4 gifting peak, Q1 trough |
| Skin & Body | ~28% | ~28% | Q4 gifting peak (strongest), Q1 trough |
| Home Care | ~22% | ~48% — bulk chemicals, heavy packaging | Nearly flat |
| Professional | ~20% | ~26% | Flat (salon demand) |

The material-intensity spread across lines is what makes the mix story (S1) work; the seasonality spread is what makes the trap (S4) work.

**Customers:** top-10 named retail accounts per BU plus an aggregated "Other" — fictional names (e.g. *Norrhandel*, *Balticum Retail*, *Rheinkauf Gruppe*), to be collision-checked by scout before Phase 2 generation. Central Europe is deliberately concentrated: its largest customer, *Rheinkauf Gruppe*, carries ~35% of the BU — which is what makes the DSO story (S2) move the needle.

**Observation window:** 24 months, January 2024 – December 2025 in-world (same calendar universe as churn), with an FY2023 driver set as the base year the FY2024 budget is built from. Budgets exist for both years at the same grain as actuals.

---

## 3. The four planted stories

These are the answer key. Each has designed mechanics, timing, affected entities, and a designed magnitude that the validator checks is actually present in the generated data.

### S1 — The mix shift that reads as input inflation
- **Where/when:** BU Nordics, from February 2025 (month 14) onward.
- **Mechanics:** a listing win plus a deep in-store promotional programme (promoted lines sold at ~−10% net price) lifts Home Care volumes ~40%, partly cannibalising Skin & Body (~−8% volume). Home Care carries ~48% material cost against a ~30% line average, so the BU's material cost line rises ~12% YoY while **unit** material costs stay flat (±0.5% — the answer key's decisive fact). BU net revenue grows only ~3%: the promotion moves volume into the material-heavy line at a cut price — share shifts, the pie barely grows, and the materials bill balloons.
- **The pack says:** "Material costs +12% YoY, gross margin −3pp in Nordics." The obvious commentary is commodity inflation.
- **The storyteller must say:** unit costs are flat; the margin went to mix and promotional pricing. Evidence: volume by line, material cost per unit by line (derivable from `pnl_monthly`), the PVM bridge.
- **Failure tested:** right variance, wrong cause.
- *(S1 vs S3: S1 is a mix story that happens to use promotion — its signature is in material intensity and unit costs. S3 is a discount story that buys growth — its signature is in the discount rate, customer concentration, and fading elasticity. Different tables, different evidence.)*

### S2 — The DSO creep behind a one-off
- **Where/when:** BU Central Europe, receivables drift from January to October 2025; the masking one-off lands April 2025.
- **Mechanics:** *Rheinkauf Gruppe* (~35% of the BU) stretches effective payment terms from ~45 to ~95 days over ten months; two smaller wholesale accounts follow partway. BU DSO rises ~18 days; company DSO ~+4–5 days. In April 2025 the company sells and leases back its Tampere warehouse: ~€5.5M cash proceeds, ~€2.2M gain in other income. Reported EBITDA stays on plan and the cash balance stays comfortable all year — the deterioration is real but hidden: cash conversion (operating cash flow ÷ EBITDA, H1-on-H1) falls from ~106% in H1-2024 (above 100%, as it should be — Q1 collects December's receivables balloon) to ~72% reported, and ~63% once the one-off is stripped out, in H1-2025.
- **The pack says:** EBITDA on plan, cash comfortable. DSO appears in the working-capital appendix, drifting, unremarked.
- **The storyteller must say:** the one-off is doing the work; strip it out and cash conversion has deteriorated materially, driven by one named customer's payment behaviour.
- **Where the evidence sits:** the per-customer receivables table (`receivables_by_customer_monthly.csv`) — the AR appendix nobody reads. Rheinkauf's balance-vs-billing drift is right there for anyone who looks; the design gives the storyteller a genuine, citable path to the customer's name, not just an inference from concentration.
- **Failure tested:** missing a story entirely because every headline looks fine. The hardest of the four — it requires connecting four tables.

### S3 — Growth bought with discount
- **Where/when:** BU Baltics & Poland, January 2025 onward.
- **Mechanics:** promotional discounting escalates from ~8% to ~15% of gross revenue; three of the BU's top-10 accounts exceed 18%. Volume responds and BU net revenue grows ~24% YoY — the engine of the company headline (FY2025 by BU: Nordics ~+3%, Central Europe ~+4%, Baltics & Poland ~+24% → company ~+8%). A 7pp-of-gross discount move against constant unit costs mechanically costs ~5pp of margin: BU gross margin erodes from ~38% to ~33%. The unsustainability signal is planted in the elasticity: the volume response per promotional euro in H2 2025 is ~40% weaker than in H1. The discounts are becoming the price.
- **The pack says:** "Revenue +8% — ahead of plan." A good-news number.
- **The storyteller must say:** the growth is bought and fading — with the three account names and the H1/H2 elasticity comparison as evidence.
- **Failure tested:** celebrating a positive headline without reading what funds it.

### S4 — The January cliff that isn't (the trap)
- **Where/when:** every January, by design; the test case is January 2025.
- **Mechanics:** Hair Care and Skin & Body carry a Q4 gifting peak (December ~+35% vs average) and a Q1 trough (January ~−22%). The seasonality is identical in both years **and in the budget**. January 2025: revenue ~−27% month-on-month (the seasonal lines are ~58% of revenue: December index ~1.20, January ~0.87 at company level) — and +6% year-on-year, −1.2% vs budget.
- **The pack says:** the MoM line is genuinely alarming out of context.
- **The storyteller must say:** stand down — seasonal, in line with budget and prior year, no action. Nothing more.
- **Failure tested:** the A7 analogue from churn. An agent that narrates a crisis here loses the room; the credibility of everything else it says depends on this one.

### The expected-findings matrix (designed outcome — the centrepiece figure)

The churn design's 2×2, translated to finance:

|  | There is a real story | There is no story |
|---|---|---|
| **The pack raises an alarm** | S1 — material costs. The pack is right to flag it; the storyteller must supply the *cause* (mix + promo price, not commodities) | S4 — the January cliff. The storyteller must **de-escalate** |
| **The pack stays calm** | S2 — DSO behind the one-off; S3 — erosion under a good-news headline. The storyteller must *surface* these | Everything else — noise the storyteller must leave unnarrated |

| Story | The pack sees | The storyteller must add | Difficulty |
|---|---|---|---|
| S1 | Material +12%, GM −3pp in Nordics | Mix and promo pricing, not commodity prices — unit costs flat | Medium |
| S2 | Nothing alarming (DSO drifts in an appendix) | One-off masks deteriorating cash conversion; one named customer | Hard |
| S3 | Revenue +8% (good news) | Bought growth: discount concentration + fading elasticity | Medium |
| S4 | January −27% MoM (looks bad) | **No story. Stand down.** | Easy — but it's a trap |

### The noise policy

Most variances have no story, as in life. Every driver carries month-to-month noise (±1–3%), and the answer key includes a **noise ledger** of three mundane, self-explaining events that the agent is allowed to explain but must not dramatise:

- N1 — logistics cost spike, BU Nordics, February 2024 (~€150k, winter storms; one month, self-correcting).
- N2 — one-off recruitment and advisory costs in admin, September 2024 (~€90k).
- N3 — contractual price indexation in Central Europe, July 2025 (+2% list prices; a *positive* mundane variance).
- N4 — structural budget optimism *(added post-generation, 2 July 2026)*: the budget's small optimism biases compound through operating leverage to a persistent below-plan EBITDA gap (~−8% in the story-free year, every month, all BUs). Not an event but a planning property — declared in the answer key so a storyteller who spots it ("you always miss budget; that hum predates the stories") is scored as right, not as a false positive. The failure tested: narrating the hum as a crisis, or attributing 2025's story variances to it.

Evaluation counts any finding of severity "watch" or above that matches neither a story nor a noise-ledger entry as a false positive. The storyteller is scored on restraint as well as recall.

### As-built calibration notes (2 July 2026, post-generation)

The illustrative magnitudes above were drafted before the generator existed; calibration against the validator bands moved some of them. The generated data and `data/answer_key/stories.csv` are the ground truth; where the prose above and this list disagree, this list wins. All bands in §4 rule 8 were met; nothing here weakens a designed signature.

- **S1:** Home Care volume lands at **~+42% FY-on-FY** with net price/unit **~−13%** on the promoted line (deeper than the drafted ~−10%); Skin & Body cannibalisation **~−13%** (deeper than the drafted ~−8%). Measured: BU material spend **+11.5%** YoY, BU net revenue **+3.8%**, BU GM **−3.5pp**, unit material costs +0.3%/−0.4% (flat, as designed).
- **S2:** the terms drift runs **January–June 2025** (compressed from the drafted Jan–Oct, so the effect concentrates in the H1 window the cash-conversion check measures) and reaches **~105 days** (from the drafted ~95). Because receivables are seasonal (see the modelling note below), all S2 measurements are like-for-like year-on-year: BU DSO **50 → 74 days (+23.6)** and company DSO **39 → 45 days (+5.6)**, Nov/Dec vs Nov/Dec. Cash conversion (OCF/EBITDA, H1-on-H1): **~106% in H1-2024** — above 100% because Q1 collects the December balloon, as in life — falling to **~72% reported / ~63% underlying** in H1-2025 (fall ~42pp against the ≥15pp band). The cash balance never dips below €12.7M on an €8M opening: the mask holds.
- **S3:** the discount endpoint is **~17% of gross** (from the drafted ~15%) — needed to hit the ≥4pp margin-erosion band once erosion is measured honestly (FY2024 average vs Q4-2025 average, the "before/after" the narrative describes, rather than full-year averages diluted by the ramp's early months). Measured: BU GM 41.4% → 36.6% (−4.8pp), Baltics net revenue **+27%**, company **+8.6%**, H2 volume-per-promo-euro **38% weaker** than H1.
- **S4:** measured January 2025: **−28.7% MoM, +2.6% YoY, −1.6% vs budget**; company seasonal index December ~1.24 / January ~0.81 (the drafted ~−27% used static revenue shares; the empirical index weights December's gifting mix properly).
- **N1** reduced to **€80k** (from the drafted ~€150k) to clear rule 9's noise ceiling with headroom; and rule 9's "smallest monthly impact" is implemented as each story's **median** absolute monthly gross-profit impact — S3's first month is near-zero by design, and a literal minimum would measure the ramp's transition instant, not the story.
- **Modelling choices:** (1) *Receivables seasonality — resolved 2 July 2026.* The first build smoothed AR on a trailing-12-month basis, which left December balances flat; Eva's FP&A eye objected, and receivables were rebuilt **terms-based** (closing AR = the most recent `terms` days of billing, with a noiseless FY2023 backfill for opening balances). December now balloons and Q1 unwinds (€14.7M Sep-24 → €17.7M Dec-24 → €14.4M Feb-25); January's collection of the December peak is a real cash event; DSO comparisons run like-for-like YoY so the seasonal numerator cancels. The rebuild touched only the working-capital, receivables and cash tables — the P&L is byte-identical to the validated build. (2) **N3's contractual price indexation is in the budget too** (contractual escalators are known at budget time), so it shows as a YoY effect, not a budget variance — still held out for the spot-read.
- **Four customer names replaced after the scout collision check** (real companies found): Fjellmat AS → Berghav AS; Vilnia Prekyba → Sūduvos Prekyba; Warszawska Grupa Handlowa → Poznańska Grupa Detaliczna; Tallinna Kaubandus → Läänemere Kaubad. (Also Kaunas Diskonts → Kauno Diskontas, for correct Lithuanian.)

---

## 4. Data design

### Generation method

Pure Python (pandas + numpy), driver-based, seeded (`RANDOM_SEED = 42`), fully deterministic — **no LLM anywhere in the generation path** (unlike churn, which needed prose; financial data is numbers, and numbers are Python's job). One generator script, one config holding every tunable: the company grid, all driver levels and trends, the seasonal indices, the noise sigmas, the four story injections and the noise-ledger events as explicit parameter blocks, and the budget assumptions.

**Drivers, not line items.** The model generates volume by BU × line, list prices, promotional discount rates, unit material/labour/logistics costs, opex blocks, headcount, customer revenue shares, and per-customer payment terms. Every reported financial line is *computed* from those drivers; no total is ever generated independently of its parts. Budgets are computed the same way from prior-year drivers plus growth assumptions (with a small, mundane optimism bias so budget variances exist even where no story does).

**Rounding policy (hard rule):** all monetary values are computed and stored in exact cents at the leaf grain; every aggregate is a sum of leaf cents; ratios and KPIs are computed from cent sums at presentation time and never re-derived from rounded intermediates. Sum-of-rounded ≠ rounded-sum is how financial fakes betray themselves; here the identities hold to the cent by construction, and the validator proves it rather than trusts it.

### Tables

All CSV, EUR ex-VAT, ISO-8601 months, UTF-8.

**`pnl_monthly.csv`** — month × BU × product line (24 × 3 × 4 = 288 rows): `volume_units`, `list_price_eur`, `gross_revenue`, `promo_discounts`, `net_revenue`, `material_cost`, `direct_labour`, `logistics_cost`, `gross_profit`. Storing the list price makes rule 1 verifiable by any public reader from the CSVs alone, and unit economics (material cost per unit — S1's decisive evidence) are derivable by simple division.

**`opex_monthly.csv`** — month × BU (72 rows): `sales_marketing`, `admin_general`, `other_income` (zero except one-offs), `headcount_fte`. EBITDA is derived (GP − S&M − admin + other income), never stored.

**`customer_revenue_monthly.csv`** — month × BU × customer, top-10 named + "Other" per BU (~800 rows): `gross_revenue`, `promo_discounts`, `net_revenue`.

**`customer_master.csv`** — customer, BU, channel, `contractual_terms_days`.

**`working_capital_monthly.csv`** — month × BU: `receivables_opening`, `collections`, `receivables_closing`. DSO is derived in analysis, never stored.

**`receivables_by_customer_monthly.csv`** — month × BU × customer, same roster as the revenue table (~800 rows): `receivables_closing`, `collections`. The AR-by-customer appendix — a completely standard artefact, and the table where S2's answer actually sits. Without it the storyteller could only infer Rheinkauf from concentration; with it, the attribution is citable evidence, which is what the evaluation demands.

**`cash_monthly.csv`** — month, company level: `cash_opening`, `operating_cash_flow`, `investing_cash_flow`, `cash_closing`. A declared simplification: OCF = EBITDA − Δreceivables − simplified tax; no inventory or payables (kept out to hold the dataset minimal — stated openly in the writeup). The warehouse proceeds sit in investing; the gain sits in other income.

**`budget_pnl_monthly.csv`**, **`budget_opex_monthly.csv`** — same schema and grain as their actuals counterparts, both years. (No budget for customer/working-capital/cash tables — packs track DSO against prior year, not budget.)

**`answer_key/stories.csv`** — held out of the analysis path entirely (churn precedent): `story_id`, `type` (story | noise), `name`, `mechanism`, `affected_bus`, `affected_lines`, `affected_customers`, `months`, `designed_magnitude`, `expected_finding`, `failure_mode_tested`.

### Coherence rules (non-negotiable, one validator check each)

`validate_financials.py`, churn's `check_rule_N` convention: rule N below is implemented as `check_rule_N_<slug>`, per-rule PASS/FAIL report, `sys.exit(1)` on any failure.

1. **Row identities to the cent:** volume × list price = gross revenue (all three stored, so the identity is publicly checkable); gross − discounts = net; net − (material + labour + logistics) = gross profit. Every row, both actuals and budget.
2. **Aggregation identities:** product lines sum to BU, BUs to company, months to quarters and YTD — recomputed from leaf rows, to the cent.
3. **Budget completeness:** a budget cell exists for every actual cell at the same grain, and budget rows satisfy rule 1.
4. **EBITDA reconciliation:** GP − S&M − admin + other income = reported EBITDA; reported − one-offs = underlying EBITDA; both derivable at every grain.
5. **Customer sums:** named customers + "Other" sum exactly to their BU's gross/discount/net revenue.
6. **Receivables roll-forward:** closing = opening + net revenue − collections, per BU per month *and* per customer per month; customer receivables sum exactly to their BU's balance; implied payment behaviour matches the customer-terms model, including S2's designed drift.
7. **Cash roll-forward:** closing = opening + OCF + ICF each month; OCF reconciles to EBITDA − ΔAR − tax; the one-off appears exactly once in each of ICF (proceeds) and other income (gain).
8. **Story signatures present at designed magnitude:** S1 — BU material spend +12% ± 1 YoY with unit material costs flat (±0.5%), BU net revenue +2–4%, BU GM −3pp ± 0.5; S2 — DSO drift (BU ≥ +15 days, company ≥ +4) with the cash-stability mask condition and H1-2025 cash conversion falling ≥ 15pp; S3 — discount-rate path 8→15% of gross, ≥3 accounts above 18%, BU margin erosion ≥ 4pp, company revenue +8% ± 1, H2-2025 volume response per promotional euro ≥ 30% weaker than H1 (the fading-elasticity signal must be *provably* in the data, not hoped for); S4 — seasonal ratios in band in both years and in budget, January-2025 budget variance within ±2%.
9. **Noise ceiling:** measured as absolute euro impact on monthly BU gross profit, no non-story event exceeds 60% of the smallest story's smallest monthly impact; noise-ledger events present at their designed sizes on the same measure.
10. **Seasonality consistency:** the budget's seasonal index equals the generator's, so S4's alarm exists only in the MoM view — never against budget.
11. **Headcount and labour coherence:** direct labour tracks volume; headcount paths are smooth; revenue per head stays in a plausible band.
12. **Format:** exactly 24 months (2024-01 … 2025-12), ISO months, UTF-8, no nulls outside designed sparsity.

---

## 5. Analysis pipeline

1. **Deterministic layer** (`variance_analysis.py`) — budget-vs-actual and YoY variance tables at company/BU/line grain; price–volume–mix decomposition of revenue and material cost; KPI series (growth, GM%, EBITDA%, DSO, revenue per head); threshold flags. Output: `data/analysis/surface_report.md` — *the board pack in prose*: what moved, exactly, and nothing about why. This layer is built properly and presented respectfully; the case study must not strawman the thing most finance teams already do well.
2. **Storyteller layer** — the agent receives the data tables (never the answer key), the surface report, and a findings schema. Task: for each flagged variance, explain the cause with evidence (table, rows, numbers) or say explicitly that no explanation is needed; then surface anything material the pack missed. Output per finding: `headline`, `category`, `affected` (BU/line/customers/months), `claimed_cause`, `evidence[]`, `severity` (info/watch/act), `confidence`. The "should the board worry?" verdict on each pack flag is mandatory — that is where S4 bites. Mechanism (API calls vs subagents): open question 5.
3. **Evaluation** (`evaluate.py`) — findings matched to the answer key by affected-area and category: each story scored **found / found-wrong-cause / missed**; false positives counted against the noise policy; S4 reported explicitly as de-escalated or cried-wolf; evidence spot-checked against the actual tables (an agent citing numbers not in the data fails that finding). Output: `data/analysis/report.md`, ml_report.md precedent — everything that went wrong stays in.
4. **The business translation** — variances carry euros by construction; the writeup attaches them: "the pack's commentary would have attributed €X of margin erosion to input costs; the correct attribution changes what you do about it." S2's translation is the sharpest: cash conversion deterioration a covenant or an acquirer would find in due diligence, surfaced twelve months early.

---

## 6. Deliverables

| Artefact | Location | Audience |
|---|---|---|
| Design doc (this file) | `design/` | Internal |
| Decision log | `design/DECISIONS.md` | Internal |
| Generation code + config | `code/` | Public — part of the rigour story |
| Generated dataset + answer key | `data/` | Public |
| Surface report, agent findings, evaluation | `data/analysis/` | Public — technical readers |
| Analysis notebook(s) | `notebooks/` | Technical readers, WS3 material |
| Interactive HTML page | `interactive/` | Website visitors |
| Long-form case study (canonical) | `writeup/` | Buyer-first; website / training / LinkedIn derive from it |

**Interactive page concept — "the board pack that answers back."** A month slider; the pack view (KPI tiles, variance table) on one side; click any flagged line to drill into the PVM waterfall, the trend, and the storyteller's evidenced narrative; a toggle between *what the pack says* and *what the agents found*; January 2025 as the built-in teaching moment. Embeddability constraints are the churn design doc's, verbatim: single self-contained HTML, all CSS/JS/data inlined, hand-rolled SVG, `hpx-` prefix, brand tokens exact, responsive from 360px.

Optionally (open question 6): one month's board pack generated as a branded .docx from the office templates — the "before" artefact, and a workshop prop for WS3.

---

## 7. Open questions for Eva

1. **The company name.** *Paju Consumer Products Oy* is the working proposal (paju = willow; Finnish nature-word precedent set by Kataja). Scout collision check, 2 July 2026: **Paju** clear (Finnish namesakes are in accounting, consulting and forestry — non-competing); **Vaahtera** minor collisions, acceptable fallback; **Kuura** rejected (Metsä Group's registered Kuura® textile fibre, plus an active Kuura Beauty hair-care brand); **Saarni** rejected (Saarni GB Oy sells men's grooming — directly adjacent sector). Case 2 had not yet minted its fictional company name when checked the same day, so no internal collision. Happy with the sector — personal care & home care? It is deliberately close to your world; if it is *too* close for comfort, light manufacturing (e.g. packaging or food) works with the same story structure.
2. **Shape realism.** €152M net revenue, GM 42%, EBITDA 11%, 480 FTE, BU split 55/25/20, the four product lines and their material intensities, ~+8% FY2025 growth. What would you correct? Everything is a config parameter.
3. **Grain.** Receivables per BU per month *plus* a per-customer receivables table, one company-level cash summary, top-10 named customers per BU. The per-customer AR table is deliberate: it is where S2's evidence sits — without it the storyteller can only infer the customer from concentration, and the evaluation could not demand citable evidence. Trimming the cash table weakens S2's mask; trimming the per-customer AR table lowers S2's evidence bar. Comfortable with both staying in?
4. **Numbers-only dataset — confirm.** The spec's "competitor entered the Nordic market" backstory is not derivable from financials; recommendation is to keep the dataset numbers-only, let the discount-concentration finding be the in-data second-order insight, and give the competitor context in the writeup, clearly labelled as interpretation.
5. **Agent mechanism** (shared decision with Case 2): real API calls with logged token costs, or Claude Code subagents. Recommendation: decide once, portfolio-wide; API calls are the cleaner honesty story. → **Decided (Luigi, 2 July 2026): Claude Code subagents for now.** The run transcript is kept as the audit trail, agent inputs are pinned in the briefing prompt, and any cost figure quoted is a labelled subscription-based estimate, never a measurement. Real API calls remain the upgrade path if Case 2's cost-curve story sets up the key anyway.
6. **The exemplar board pack** as a branded .docx (one month, after Phase 3): yes/no?
7. **A story from life.** A variance you actually chased at P&G or Coty — sanitised — is worth three invented ones. It can replace a noise-ledger event or become a fifth story. (Churn precedent: this question produced the best material.)
8. **Which EBITDA leads the pack?** As designed, S2 *requires* that reported EBITDA (including one-offs) leads, with underlying in the appendix — that is the mask. Many real packs do exactly this, which is rather the point. This question is a confirmation, not a fork: if you would rather the pack lead with underlying EBITDA, S2's mask has to be re-engineered (it would then rest on the cash table alone).
