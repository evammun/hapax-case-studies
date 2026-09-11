# Hybrid Churn Intelligence — Design Document

Project 1 of the Hapax case study portfolio. Theme 1: "ML, but sharper."

Status: delivered; retrospectively packaged 11 Sep 2026. Formal sign-off pending Eva's September review (the pipeline was built ahead of it — see DECISIONS.md).

---

## 1. The story we are telling

A classical churn model trained on usage metrics does what it has always done: it catches the accounts whose behaviour visibly decays. What it cannot see is the account whose usage looks perfectly healthy while the relationship is quietly falling apart in the support queue — frustration building across tickets, a competitor mentioned in passing, a complaint that was closed but never resolved. Those accounts churn "without warning." The warning was there; nobody had time to read it.

The case study shows both layers working together: ML on the numbers, an agent on the text, merged into a single risk score with an explanation a customer success team can act on. The point is not that agents replace the model. The point is the **delta** — the specific accounts the model misses that the text layer catches, and what those accounts are worth.

**Honesty framing (decided):** the dataset is synthetic and we say so prominently. We engineered the data with a known answer key precisely so we could *prove* what each layer catches and misses, rather than asserting it. The data engineering is part of the methodology, not a footnote.

**Primary reader (decided):** the buyer — CFO / COO / Head of CS — with the technical depth present but skimmable. A technical reader should still find the notebook satisfying.

---

## 2. The fictional company

**Vendor:** *Kataja Analytics Oy* — a Helsinki-based B2B SaaS selling a business intelligence and reporting platform to mid-market companies (think: the tool a finance or ops team uses for dashboards and monthly reporting). Chosen because the domain is one Hapax's actual audience lives in, and because "reporting module usage" is a believable churn signal.

**Customers:** ~500 accounts, Nordic and European mid-market, 10–200 seats each, annual contracts with monthly usage telemetry.

**Fictional competitors** (for natural competitor mentions in tickets):
- *Storsund BI* — the cheaper, simpler rival. Mentioned by price-sensitive accounts.
- *Dashlume* — the slicker, better-marketed rival. Mentioned by accounts frustrated with UX.
- *Spreadsheets / "going back to Excel"* — the real competitor, as in life.

### Product feature map (the shared spine)

Every usage metric in the structured data and every ticket in the text layer references the same feature vocabulary. This is the coherence mechanism.

| Module | Usage metric (structured) | What tickets about it look like |
|---|---|---|
| Dashboards | `dashboard_views` | "dashboard slow to load", "can't share dashboard" |
| Report builder | `reports_created` | "report builder crashes", "can't schedule monthly report" |
| Data connectors | `connector_syncs` | "SAP connector keeps failing", "sync delayed again" |
| Alerts | `alerts_configured` | "alert didn't fire", "too many false alerts" |
| API | `api_calls` | "API rate limits", "breaking change in v2" |
| Admin & seats | `active_users` / `licensed_seats` | "can't deactivate user", "SSO setup help", billing |
| Exports | `exports_run` | "Excel export mangles formatting", "PDF export blank" |

---

## 3. Account archetypes

Eight archetypes. Proportions give ~25% churn over the observation window — high but defensible for mid-market SaaS, and we need enough churners to learn from.

| # | Archetype | % | Usage pattern | Ticket pattern | Churns? | Who catches it |
|---|---|---|---|---|---|---|
| A1 | Healthy stable | 35% | Steady | Sparse, neutral how-tos | No | — |
| A2 | Healthy growing | 10% | Rising, seats added | Feature requests, positive | No | — |
| A3 | Slow decay | 12% | Visible multi-month decline | Frustration mounting in parallel | Yes | **Both** (ML leads) |
| A4 | **Quietly unhappy** | 8% | Normal until ~1 month pre-churn | Frustration arc, competitor mentions, unresolved complaints | Yes | **Agent only** |
| A5 | Sudden death | 5% | Normal throughout | Silent or neutral | Yes | **Neither** (honest ceiling: acquisitions, budget cuts, champion leaves) |
| A6 | Saved account | 10% | Dip then recovery | Anger arc → escalation → resolution → calm | No | Tests false positives |
| A7 | Loud but loyal | 12% | Healthy | Regular angry tickets, always resolved fast, no competitor mentions | No | Agent must NOT flag |
| A8 | Quiet decline, stays | 8% | Usage declines (seasonal, role change) | Sparse, neutral | No | ML false-positive that text de-escalates |

**A4 is the money segment.** The entire commercial argument is the lift on A4. A7 is the credibility segment — an agent that just counts angry words flags A7 and loses the room; ours must read resolution and arc, not tone alone.

### The signal matrix (designed outcome)

|  | Text says trouble | Text says fine/silent |
|---|---|---|
| **Usage says trouble** | A3 — both catch | A8 — ML false alarm, text de-escalates |
| **Usage says fine** | A4 — agent's catch | A1/A2 fine; A5 churns unseen |

This 2×2 is the centrepiece figure of the case study.

---

## 4. Data design

Observation window: **24 months** (Jan 2024 – Dec 2025 in-world). Accounts sign up on a rolling basis through the first 12 months; churn events occur from month 6 onward. Snapshot date for modelling: each account's data is featurised as of N months before its churn/censoring date so we are honestly predicting forward, not reading the answer off the last row.

### Tables

**`accounts.csv`** (~500 rows)
- `account_id`, `company_name` (generated, Nordic-flavoured), `industry`, `country`, `signup_date`, `licensed_seats`, `plan_tier` (Standard / Professional / Enterprise), `arr_eur`, `churn_date` (null if retained), `churned` (label)

**`usage_monthly.csv`** (~500 accounts × up to 24 months)
- `account_id`, `month`, `active_users`, `dashboard_views`, `reports_created`, `connector_syncs`, `alerts_configured`, `api_calls`, `exports_run`, `logins`

Generated from per-archetype parameter distributions (base level, trend, noise, seasonality) with a per-account random seed. Decay archetypes get module-specific decline (e.g. A3 account #117's `reports_created` collapses while logins linger — people log in, look, leave).

**`tickets.csv`** (~3,500–5,000 rows)
- `ticket_id`, `account_id`, `created_at`, `channel` (email/portal), `subject`, `body`, `module` (from feature map), `resolved` (bool), `resolution_days`, `csat` (1–5, sparse — most customers don't fill it in)
- Sentiment is **not** a column. It lives in the language, where the agent has to find it. That's the point.

**`answer_key.csv`** (held out of the modelling path entirely)
- `account_id`, `archetype`, `planted_signals` (e.g. "competitor_mention:Reportify@2025-03", "unresolved_complaint:connectors"), `churn_driver`

### Coherence rules (non-negotiable, validated by script)

1. If a module's usage drops in `usage_monthly`, that account's tickets in that period reference that module — and vice versa for ticket-heavy accounts.
2. A4 accounts must have **no statistically detectable usage decline** until ≤1 month before churn. We verify this by running the ML features on A4 and confirming low scores.
3. A5 churners have no text signal — at most routine how-tos.
4. A7 anger always pairs with fast resolution (`resolution_days` ≤ 2) and never with competitor mentions.
5. Competitor mentions appear in context ("we're evaluating Reportify for next year's budget"), never as keyword stuffing, and also appear occasionally in healthy accounts as noise (a salesperson asking for a comparison sheet) so the agent can't just grep.
6. Every ticket's `module` exists in the feature map; every `account_id` exists in accounts.
7. Dates: tickets only after signup, none after churn, business-day weighting.

### Generation method

- **Structured layer:** pure Python (pandas + numpy), driver-based, seeded, deterministic. One script, one config of archetype parameters.
- **Ticket layer:** Sonnet subagents. Each agent receives an account's archetype, its usage trajectory summary, the feature map, and a "ticket brief" (how many tickets, which modules, what arc) — and writes the actual ticket language. Briefs are generated deterministically by Python so the *structure* of the signal is controlled and only the *prose* is delegated. Batched ~10–20 accounts per agent call.
- **Validation script:** checks all coherence rules above and produces a one-page data quality report. Run before any analysis.

---

## 5. Analysis pipeline

1. **EDA** — usage curves by cohort, churn timing, the "everything looks normal" plot for a soon-to-churn A4 account. Plant the dramatic irony early.
2. **Classical ML** — features: usage levels, 3-month trends, module mix shifts, seat utilisation, ticket *counts* (the metadata a traditional model would use — count and resolution time, not content). Logistic regression as the honest baseline, gradient boosting as the production candidate, SHAP for explanations. Proper temporal split.
3. **Agent layer** — per account: read the full ticket history in order, output a structured assessment: frustration trajectory (improving/stable/deteriorating), unresolved-issue count, competitor mentions with context, escalation pattern, one-paragraph narrative, text risk score. The agent never sees usage data or the label.
4. **Fusion** — combined risk score (simple, explainable combination — likely a logistic layer over both scores, not a black box), plus the narrative attached to every high-risk account.
5. **Evaluation against the answer key** — recall at top-k for ML-only vs text-only vs combined; **the A4 table** (how many quietly-unhappy accounts each approach surfaces); A7 false-positive check; honest A5 miss rate.
6. **The business translation** — attach `arr_eur` to the catches: "the combined model surfaces €X of at-risk revenue the usage model alone misses, with an explanation per account." Segmentation: worth-saving (high ARR, fixable driver) vs let-go.

---

## 6. Deliverables

| Artefact | Location | Audience |
|---|---|---|
| Design doc (this file) | `design/` | Internal |
| Data generation code + config | `code/` | Public — part of the rigour story |
| Generated dataset + answer key | `data/` | Public |
| Analysis notebook(s) | `notebooks/` | Technical readers, WS4 material |
| Interactive HTML page | `interactive/` | Website visitors — self-contained (embedded JSON + JS, no server). Controls: risk-recipe sliders (usage decline / sentiment / competitor mentions weights), risk threshold slider, "usage only" vs "usage + tickets" toggle, click-an-account drill-down to usage curve + ticket history + agent narrative |
| Long-form case study (canonical) | `writeup/` | Buyer-first; website / training / LinkedIn derive from it |

**Embeddability requirements (hard constraints — the page lives on the Hapax website):**
- One self-contained .html file: all CSS, JS and data inlined; no build step, no server, no CDN dependencies (fonts via Google Fonts link with serif fallback is the only allowed external request — Cormorant Garamond is on Google Fonts)
- Charts hand-rolled in SVG/vanilla JS, not a heavyweight chart library — keeps the file small enough to load fast on the site
- Fully responsive from 360px width up; no fixed heights that break iframe embedding; optional postMessage height reporting for iframe autosize
- All CSS class names prefixed (e.g. `hpx-`) so the page can also be inlined into a site section without style collisions
- Brand: match the tokens in `Brand Assets\Gallery\Hapax Brand Portfolio.html` exactly (Cormorant Garamond; Wine #7A2018, Navy #1F2A52, Ink #1A1410, Beige #EFE5CE, Grey #665E58)

LinkedIn posts use screenshots of the interactive page and link to the website to play with it — the page is the destination, the post is the hook.

Notebook styling per the established aesthetic: restrained highlighting, modest chart sizes, solid bars. Writing voice: direct, factual, no corporate phrasing.

---

## 7. Decision log

- **3 Jul 2026 — competitor renames:** Visby BI → Storsund BI, Reportify → Dashlume (real-product collisions found by name check). Kataja Analytics clear.
- **Date-distribution fix:** a NaN-truthiness bug clustered all non-churn tickets into the first month of account life; fixed at source, non-churn prose rewritten (~2,900 tickets), Rule 8 added to the validator (position-in-life spread + A6 arcs aligned to usage dips).
- **A4 signal model, four iterations (the published honesty trail — see `data/model/ml_report.md`):**
  - v1: A4 visible to ML (0.59 mean risk) via low csat → csat made sparse-and-polite (disengaged customers skip surveys).
  - v2: visibility rose (0.67) — dominant leak was unresolved-ticket metadata → "close-the-tickets" fix: support closes A4 tickets (resolved=true), the fix doesn't hold, the truth lives only in later tickets' prose. Realistic and prose-compatible.
  - v3: visibility rose again (0.68) — the residual leak was ticket VOLUME itself (~6.7 in window vs ~1.0 healthy). Finding: an account noisy enough to read is noisy enough to count.
  - v4 (Eva's advance directive, 9 Jul 2026): **A4 redesigned as low-volume** — 3–6 per account life, ~2.9 in window (as delivered), each long/polite/densely documented; disengagement shows as going quiet. If a residual trace remains, we stop and publish the iteration story as the finding.
- **Interactive page:** embeddable single-file HTML (see §6); risk-recipe sliders; LinkedIn uses screenshots linking to the website.

## 8. Open questions for Eva

These questions are closed in `design/DECISIONS.md` (superseded by delivery, save for Q4 which is a recommendation awaiting Eva's confirmation); the original questions stay below as provenance.

1. **Names:** happy with *Kataja Analytics*, *Visby BI*, *Reportify*? (Checked for obvious real-company collisions, but worth a second look before anything public.)
2. **Churn rate ~25%** over 24 months — comfortable, or pull it down to ~18% for realism at the cost of fewer positive examples?
3. **Ticket volume:** spec says 3–5k. I'd aim ~4,000 (median ~6 per account, heavy tail for A6/A7). Sonnet cost is modest at this scale.
4. Anything you want planted in the data that I haven't listed — e.g. a specific anecdote you'd like to be able to tell in a workshop?
