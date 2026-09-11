# ERP Output Cleanup — Design Document

Project 2 of the Hapax case study portfolio. Theme 2: "The automation detective."

Status: draft for Eva's review. Nothing downstream gets generated until this is signed off.

Companion files: `format_research.md` (source-grounded SAP format reference), `DECISIONS.md` (running log). Plan: `PLAN-erp-cleanup-case-study.md` in the project folder.

---

## 1. The story we are telling

A manufacturer's ageing ERP produces its reports as spool files — fixed-width text with repeated page headers, German number formats, status codes like `@0A@` embedded in the data, and totals rows distinguishable from line items only by indentation. For twenty years one person has known how to read them. Two obvious fixes exist and both fail. Rebuilding the ERP is a seven-figure project nobody will approve. Leaving an LLM permanently in the parsing path works, but bills per document for as long as it runs.

The case study demonstrates the third option. An agent parses the documents; it is expensive and slow, but it works. An overseer watches the agent's output, recognises that each transaction type has a consistent structure, and generates ordinary deterministic parsers — plain code that runs in milliseconds, costs nothing per document, and can be tested like any other code. Month by month the LLM handles a smaller share of the stream until it is only called for genuine exceptions. **The AI's job was to discover the automation, not to be it.** The centrepiece is the cost curve: what the hybrid path costs per document against the counterfactual of leaving the LLM in the loop.

This is the demonstrated version of the advisory page's "automation that retires itself" exemplum. The exemplum stays labelled hypothetical; this case study shows the mechanism working end-to-end on data we can score.

**Honesty framing (decided).** The documents are synthetic and we say so prominently. Research confirmed that no public verbatim SAP spool output exists and that real layouts vary per installation ("no canonical format") — so our documents are *SAP-style, built from documented conventions* (every convention cited in `format_research.md`), not replicas of any specific system. Because we generate the data, we hold a complete answer key: every field of every document is scored, for both the LLM path and the generated parsers. Both paths get marked, not trusted — including one planted failure that neither catches (§4).

**Primary reader (decided).** The buyer — CFO / COO / Head of Operations — with the technical depth present but skimmable. A data engineer should still find the parser-generation mechanics satisfying.

## 2. The fictional company

**Jalavakoski Konepaja Oy** — a Tampere-based machinery manufacturer, ~350 employees, exporting across the Nordics and Germany. Its SAP R/3 4.6C was implemented in 2003 by a German consultancy; the company codes, column headings, and number formats have been German ever since, and nobody has dared touch the configuration. Finance and operations receive their month-end reports as text spool exports from five transactions. The employee who knows every layout by heart retires this year.

(Name follows the portfolio convention — Finnish tree names: *jalava* = elm, plus *koski* = rapids; *konepaja* is the standard Finnish term for a machine works. First candidate *Saarni Industrial Oy* was dropped after a collision check: Saarni Industries Oy exists — Raisio holding company, founded 2020 — alongside Saarni Group Oy and others. "Jalavakoski" returns no matches, checked 2 Jul 2026. The churn vendor Kataja Analytics is a different fictional world; no cross-references.)

**The shared spine — master data.** One config file defines:
- **Vendor master**: ~40 vendors, German and Nordic names (vendor 10040 *Müller GmbH* among them, per the spec), each with payment terms, typical order sizes, and a home currency.
- **Material master**: ~60 materials (machined components, fasteners, raw steel, consumables), each with base unit, plant/storage assignments, and price ranges.
- **Customer master**: ~30 customers for the sales-side reports.
- **G/L chart**: a small chart of accounts with per-account plausible amount ranges.

Every document draws from this spine, which is what makes cross-transaction coherence checkable (§6).

## 3. Transaction-type taxonomy

The five report types, per `format_research.md` (documented columns, German headings):

| Type | What it is | Structure | Signature quirks | Parse difficulty |
|---|---|---|---|---|
| **FBL3N** — G/L account line items | Postings on a G/L account for a period | Header block (company code, account, period) → line items → account totals | `S`/`H` debit-credit column; trailing-minus amounts; clearing cross-references | Medium |
| **ME2M** — purchase orders by material | Open/all POs, grouped | Selection block → framed columns (`----+----`) → per-vendor subtotals → *Gesamtsumme* | Grouping rows mid-table; qty + unit (`1.000 ST`); still-to-deliver columns | Medium-high |
| **VA05** — sales order list | Sales orders in a period | Header → pipe-separated columns → net-value total | Free-text customer names (trap for naive splitting); delivery-status words | Medium |
| **FBL1N** — vendor line items | Open/cleared items per vendor | **One vendor per page**, header repeats per vendor → items → per-vendor totals | `@08@`/`@09@`/`@0A@` status codes; doc types KR/KZ/KA; due-date columns | High |
| **MB52** — warehouse stock | Stock by material/plant/location | Hierarchical: plant → storage location → materials, totals per level | Hierarchy encoded in indentation only; three stock-status columns; value columns | High |

Formatting variation *within* a type (the benign kind the overseer must see through): line-item counts, page-break positions, column-width drift from content, optional header rows, selection-block differences. The horrors catalogue (`format_research.md` §7, H1–H10) maps every quirk to its documented source.

## 4. The designed-outcome table — the centrepiece

Every document belongs to a pre-registered class. Evaluation in Phase 3 is scored against this table; the interactive page renders it with actual results overlaid. This is the analogue of the churn project's signal matrix.

| Class | Meaning | Design | Count (of 240) | Designed outcome |
|---|---|---|---|---|
| **R — routine** | Standard layout, benign variation | The majority class, with enough consistent instances for the overseer to learn from | 218 (91%) | LLM path until the type's parser exists; deterministic thereafter |
| **V — variant** | A second layout of an existing type (user-modified column selection, H10), appearing from month 8 | Only 3 instances per affected type (2 types) — deliberately below the learning threshold | 6 | Stays on the LLM path. The honest lesson: not everything is worth automating, and the system should know it |
| **F — fail-and-recover** | Documents that break the generated parser: an extra column after a "system patch" (ME2M); a customer name containing pipe-like characters (VA05); a mid-table currency change (FBL1N) — 5 each | Placed in months 9–12, after parsers are online | 15 | Deterministic parse **fails validation** → router falls back to LLM → correct result. The safety net, demonstrated |
| **S — silent error** | One ME2M document where the net-price and still-to-deliver-value columns swap positions, headers and values together — internally consistent, and the totals column (Nettowert) does not move, so schema, totals and master-data checks all pass on a positional read | Exactly 1, month 11 | 1 | **Neither the router nor validation catches it.** Only the answer key reveals the wrong values. The honest ceiling — and the argument for retaining sampled human spot-checks (a line-level price × quantity cross-check would catch this one; the writeup says so) |
| **First-of-type** | The first documents of each type before any parser exists | Months 1–2 | (subset of R) | LLM path by construction — this is the expensive discovery phase the cost curve starts from |

**Pre-registered headline numbers** (derivable from the table and §5/§7 parameters, stated here so Phase 3 can be marked against them): the LLM path carries the 40 discovery documents (8 per type before each parser exists), the 6 variants, and the 15 fallbacks — 61 documents; the deterministic path carries the other **179 of 240 (≈75%)**, including the one silent error. The steady-state claim is the stronger one: from month 3 onward, 100% of *routine* documents are parsed deterministically at zero marginal cost. The whole-stream share is parameter-dependent (N, corpus length) — a longer stream asymptotes higher, which the case study states rather than implies.

What the buyer takes away: routine work migrates to free deterministic code; genuine exceptions stay with the LLM; failures route back safely; and one class of error survives everything except independent checking — which is why the method includes it.

## 5. Data design

- **In-world window**: 12 month-end batches, January–December 2025. Each month produces ~4 documents per type (different accounts / vendors / plants / periods), ≈ 48 per type, **240 documents total** (open question 5: spec said 10–20 per type; this is deliberately higher so the curves have enough points).
- **Stream order**: documents are processed in date order. Variants and failures are placed late (months 8–12) so the deterministic path is up and running when they arrive — the demo needs parsers to exist before it can show them failing gracefully.
- **Volume shape**: line items per document drawn from per-type distributions (FBL3N 20–120 lines, ME2M 10–60, VA05 15–80, FBL1N 5–40 per vendor × 3–6 vendors, MB52 40–150) — long enough that page-break horrors actually occur.
- **Files**: one `.txt` per document in `data/documents/` (named `YYYY-MM_<type>_<seq>.txt`), one JSON ground-truth record per document in `data/answer_key/` (every header field, every line item, every total, plus the document's class R/V/F/S). The answer key never enters the parsing path; it exists for scoring only.
- **Generation**: pure Python (pathlib, pandas/numpy), seeded (`RANDOM_SEED = 42`), fully deterministic — same seed, byte-identical corpus. All tunables in `code/config.py`. No LLM anywhere in data generation.

## 6. Coherence rules (non-negotiable, validated by script)

1. **Arithmetic**: every printed subtotal and total equals the sum of its line items, in every document, after German-locale round-tripping. A total that doesn't add destroys the demo instantly.
2. **Cross-transaction consistency**: vendors, materials, customers and G/L accounts exist in the master data everywhere they appear; ME2M purchase orders for a vendor reconcile with FBL1N invoice items for the same vendor within a declared lag (PO date < invoice date ≤ PO date + 60 days; invoiced ≤ ordered value); MB52 materials and plants match the material master.
3. **Amount plausibility**: amounts fall within the per-account / per-material / per-vendor ranges defined in the master data (spec requirement — no €2M fastener orders).
4. **Locale**: German formats throughout — `1.234,56`, trailing minus on credits, `DD.MM.YYYY`, `ST`-style units, German column headings per `format_research.md`.
5. **Dates**: business-day weighted, sequential within documents, month-end clustering for financial reports; no document dated outside its batch month.
6. **Answer-key completeness**: every field the extraction schema (§7) defines is present in the answer key for every document; class labels match the designed-outcome table counts exactly.
7. **Grounded formatting**: every formatting feature the generator emits traces to a section of `format_research.md` (sourced or declared-inferred); horrors are applied per config, not ad hoc.

`code/validate_data.py` checks all seven and exits non-zero on any failure (churn precedent).

## 7. Pipeline design

1. **Extraction schema** (per type): header fields + line-item records + totals, as a JSON Schema. The same schema binds the LLM path, the generated parsers, and the answer key — one definition of "correctly parsed."
2. **LLM path** (`code/llm_parse.py`): one call per document; schema-validated JSON out; a retry after a schema failure is logged and costed like any other call — retries are part of the true cost of the LLM path, not overhead to hide. Per call, log: model, input/output tokens, latency, cost. Execution method per open question 3.
3. **Overseer** (`code/overseer.py`): watches accumulated successful parses per type. After **N = 8** structurally consistent parses of a type, it induces the fixed-width/frame template and generates a deterministic Python parser. **Activation gate**: the candidate parser must reproduce the LLM's accepted output on all previously parsed documents of that type (regression against its own history — no answer-key peeking). Generated parsers live in `code/parsers_generated/` with provenance headers (source documents, date, generating model).
4. **Router** (`code/router.py`): deterministic parser first when one exists; every deterministic result is validated (schema + arithmetic totals + master-data lookups); on validation failure the document falls back to the LLM and the failure is logged; repeated failures on one type flag the template for regeneration.
5. **Evaluation** (`code/evaluate.py`): field-level accuracy per path against the answer key; per-class scorecard against §4 (including the silent error S — reported as *found only by the answer key*); cumulative cost and latency curves for the hybrid stream vs the all-LLM counterfactual; % of stream on the deterministic path per month.

The overseer is structure induction over consistent examples, plus code generation, plus a regression gate — nothing more, and that is the point. The expensive general intelligence gets used to write the cheap specific program.

## 8. Cost accounting (open question 3, method recorded here once decided)

Two candidate methods:
- **A (recommended): real API calls** from Python with per-call logged input/output tokens, priced at published rates, wall-clock latency measured. ~240 documents × (1–3k tokens in, ~0.5–1k out) is a few euros at mid-tier model prices — cheap for the credibility of "measured, not estimated."
- **B: Claude Code subagents** writing parse outputs, costs *estimated* from published pricing and token counts. Zero marginal spend, but every figure must be labelled an estimate.

**Decision (2 Jul 2026, Luigi): method B.** No API keys — this is a showcase, and the parsing runs as Claude Code subagents within the existing Claude Max subscription. Consequences, recorded: accuracy figures remain exact (scored against the answer key); cost figures are *estimates* — computed from published per-token prices applied to measured subagent token usage (an upper bound: a session includes agent overhead a purpose-built extractor would not have) and to modelled per-document token counts — and are labelled as estimates everywhere they appear, including on the interactive page. Latency is subagent wall-clock, labelled as harness-inclusive. The earlier "recommendation A" was the assistant's, not the founders' — logged as a corrected misreading in DECISIONS.md.

## 9. Deliverables

| Artefact | Location | Audience |
|---|---|---|
| Design doc (this file) + format research + decision log | `design/` | Internal |
| Generation code + config + validation | `code/` | Public — part of the rigour story |
| Synthetic corpus + answer key | `data/` | Public |
| Pipeline: LLM path, overseer, generated parsers, router, evaluation | `code/`, `code/parsers_generated/` | Public — the generated parsers are exhibits, not just plumbing |
| Findings report | `data/runs/report.md` | Internal → feeds writeup |
| Analysis notebook | `notebooks/` | Technical readers, WS4 material |
| Interactive HTML page | `interactive/` | Website visitors |
| Long-form case study (canonical) | `writeup/` | Buyer-first; website / training / LinkedIn derive from it |

**Interactive page concept** (embeddability constraints identical to the churn project: one self-contained .html, all CSS/JS/data inlined, hand-rolled SVG, `hpx-` prefix, brand tokens, responsive from 360px, Google-Fonts link as the only external request):
- **The horror, first.** A raw spool document in a monospace viewer — the visitor sees exactly what the finance team receives.
- **Press play.** The 240-document stream processes across 12 months on a timeline; each document ticks LLM (wine) or deterministic (navy); the cumulative cost curve splits from the all-LLM counterfactual; parser-generation moments are annotated as they happen.
- **Drill down.** Click any document: raw text, extracted table, path taken, cost. Click a parser event: the actual generated parser code.
- **The honest overlay.** The designed-outcome table with real results, the F-class fallbacks visible, and the S-class silent error called out — including that only the answer key caught it.

## 10. Open questions for Eva

1. **Company name**: happy with *Jalavakoski Konepaja Oy*? (Tree-name convention kept; collision-checked clean 2 Jul 2026. First candidate Saarni Industrial Oy failed the check — Saarni Industries Oy exists. Alternatives are cheap if the sound doesn't land.)
2. **Scope**: all five transaction types, or three for v1 with the others added later? If three, the recommendation is **FBL3N, FBL1N, ME2M** — the documents a finance audience recognises on sight (G/L, vendors, purchasing); MB52 and VA05 follow in an update. Five is showier; three ships sooner. (Consequence if three: the VA05 planted failures move to a v1 type or wait for the update; the FBL3N silent error is unaffected.)
3. **LLM path execution**: method A (real API calls, measured costs — recommended) or B (subagents, estimated costs)?
4. **Public naming**: "SAP-style" explicitly, or "legacy ERP" in public copy with SAP transaction codes only in the technical layer? (The website exemplum says "ERP"; research docs are unavoidably SAP-specific.)
5. **Volume**: 240 documents (~48/type) vs the spec's 10–20 per type — comfortable with the larger corpus for the sake of the curves?
6. **The planted silent error (S class)**: one document whose wrong parse survives all automated checks, disclosed openly in the case study. Comfortable publishing a deliberate undetected failure as part of the honesty story?
7. **Overseer threshold N = 8** consecutive consistent parses before generating a parser — any instinct for higher/lower? (Affects where the cost curve bends.)
