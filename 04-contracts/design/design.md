# Contract Clause Extraction — Design Document

Project 4 of the Hapax case-study portfolio. Theme 2, "the automation detective" — the third and final instance of the overseer method. Written 3 July 2026 (main loop). Gate: passed by Eva's advance direction (3 Jul 2026, via Luigi: "go and implement this fully"), with every decision below reversible at her review — see `DECISIONS.md`.

Companion evidence: `dataset_research.md` (all [S]/[M] sources cited there; this document states decisions and predictions).

## 1. The story we are telling

A company's legal-operations or due-diligence team faces a pile of contracts. Reading them is expensive; most of what a reviewer looks for — where is the governing-law clause, when does this expire, can it be assigned — is the same 41 questions, contract after contract. We put a model on the pile: it reads each contract and answers a fixed set of review questions. An overseer watches the model's accepted answers per question and notices that some questions are answered by the same formulaic language nearly every time. For those, it writes a deterministic matcher — ordinary code, pattern rules on text — and retires the model from that question. The genuinely negotiated language (liability structures, IP transfers, competition covenants) stays with the model, permanently: no volume of examples makes bespoke language formulaic. The unit of learning completes the portfolio's trilogy: Case 2 learned report *formats*, Case 3 learned *suppliers*, this case learns *categories of language*.

**What is genuinely new: the data is real.** The corpus is CUAD — 510 real commercial contracts from SEC filings, annotated by law students and attorneys under The Atticus Project (CC BY 4.0). Nothing is synthetic, nothing is planted, and the answer key was written by someone else, before we existed. Every claim in this case can be re-marked by any reader with the same public download. Where previous cases pre-registered *designed* outcomes, this one pre-registers *predictions* (§4) — and the data marks our judgment, not just our pipeline. Wrong predictions stay in print.

Honesty framing, stated on every deliverable: the annotations are the marking authority and are held out from the pipeline entirely; both the model path and the matcher path are marked against them; disagreements with the key are adjudicated openly (§8) and the key is never edited. This is document processing and review triage, **not legal advice** — no output of this pipeline is a legal opinion, and we say so plainly. Primary reader: the buyer (GC, head of legal ops, COO); technical depth is skimmable.

## 2. The corpus

CUAD v1, frozen under checksum (`dataset_research.md` §2). 510 contracts, 25 types, SEC EDGAR provenance; 8 extraction categories (names/dates/jurisdictions with normalised answers) and 33 yes/no categories; the labelling pipeline was a documented seven-step process with attorney review, valued by the authors at over $2M of legal time. We use the plain-text layer (`full_contract_txt/`) — the same layer a production intake system would work on — and `master_clauses.csv` as the answer-key source. The dataset's own caveats (TXT conversion fidelity, redactions, `<omitted>` splices, "not comprehensive or representative") are recorded in `dataset_research.md` §4 and handled in §6–§8 below.

**Selection rule (pre-registered, seeded, never hand-picked).** Eligibility: contract joins cleanly to its CSV row (explicit verified filename map); text length ≤ 15,000 words (429/510 qualify — a 47k-word outlier is one read at 9× median cost with no methodological gain); not the spike contract (read once during calibration, 3 Jul 2026). From the eligible pool, a seeded draw (`RANDOM_SEED = 42`), stratified by inferred contract type and length band, selects:

- **Stream** — 50 contracts, processed in a fixed seeded order. This is the learning year: the model reads, the overseer learns, matchers are born mid-stream.
- **Holdout** — 100 contracts, disjoint from the stream. The matchers' examination: never seen during induction, marked against the key at zero marginal cost. (The model does not read the holdout — the point is what the learned code does alone on twice the volume it learned from.)

## 3. Clause-type taxonomy — the 12 selected categories

Selection principle: span the boilerplate→bespoke spectrum deliberately, with both selection statistics cited per category (prevalence measured on the full corpus; per-category difficulty from the paper's Figure 8, read-from-figure — `dataset_research.md` §5), and enough expected instances in a 50-contract stream to give the overseer a fair chance everywhere (the rarest selected category expects ~11.7 positives, near twice the induction threshold — no category is rigged into or out of learnability).

| # | Category | Kind | Prev. /510 | P@80R | Commercial meaning | Formulaicity assessment |
|---|---|---|---|---|---|---|
| 1 | Document Name | extract | 510 | ~97 | what the contract is | title line conventions |
| 2 | Parties | extract | 509 | ~96 | who signed | preamble formula, multi-span |
| 3 | Agreement Date | extract | 465 | ~93 | when signed | "dated as of …" anchors |
| 4 | Governing Law | extract | 433 | ~98 | whose courts | near-liturgical phrasing |
| 5 | Expiration Date | extract | 329 | ~86 | when the initial term ends | span formulaic, **answer computed** |
| 6 | Anti-Assignment | yes/no | 374 | ~76 | can it be assigned | strong "shall not assign" family |
| 7 | License Grant | yes/no | 255 | ~55 | is IP licensed | "hereby grants … license" anchor |
| 8 | Cap on Liability | yes/no | 275 | ~62 | is exposure bounded | broad operational definition, many forms |
| 9 | Audit Rights | yes/no | 214 | ~46 | can books be inspected | varied phrasing, false-friend contexts |
| 10 | Insurance | yes/no | 167 | ~52 | must cover be maintained | "maintain … insurance" anchor |
| 11 | IP Ownership Assignment | yes/no | 124 | ~0–2 | does created IP change hands | bespoke by nature |
| 12 | Non-Compete | yes/no | 119 | ~12 | is competition restricted | judgment-laden boundaries |

Category definitions in the pipeline brief are **CUAD-operational**, not naive — the spike proved why: CUAD's attorneys count a consequential-damages waiver as a Cap on Liability, and exclusive-sponsorship terms are Exclusivity, not Non-Compete. The brief carries the README definitions verbatim plus the operational notes evidenced during the spike and induction.

## 4. The predicted-outcome table — the centrepiece

Registered before any pipeline run. Three classes:

- **A — automatable.** The overseer writes a matcher that passes the activation gate with two-sided trust (its positives *and* negatives are reliable); on the holdout it performs statistically indistinguishably from the model path's stream accuracy (margin: ±2 pp). The category leaves the model entirely.
- **P — partially automatable.** The matcher earns one-sided trust: pattern hits are reliable (precision on induction and regression = 100%), but a non-hit proves nothing, so negatives fall back to the model. The category's formulaic instances leave the model; the residue stays.
- **R — model-resident.** No matcher passes the gate (or none is attempted for want of consistent structure). The category stays with the model, and the writeup says why — the floor is semantic, not economic.

| Category | Prediction | Evidence and predicted matcher form |
|---|---|---|
| Governing Law | **A** | P@80R ~98, prevalence 433; "governed by … the laws of [the State of] X" is near-liturgical; jurisdiction lexicon closes the answer. |
| Document Name | **A** | 510/510 present; title-line and "THIS … AGREEMENT" conventions; the spike's answer was the literal heading. |
| Agreement Date | **A** | "dated as of / entered into as of / made … this __ day of" anchors + deterministic date parse; P@80R ~93. |
| Parties | **P** | Preamble formula ("by and between A, a … corporation (\"Short\") and B…") parses most contracts, but multi-party and unconventional preambles break it; multi-span answers make negatives untrustworthy. |
| Anti-Assignment | **P** | "not/neither … assign … without … consent/notice" family is a strong positive anchor (P@80R ~76); absence of the pattern proves nothing. |
| License Grant | **P** | "hereby grants … license" anchor reliable when it fires; licence language without the anchor phrase exists. |
| Insurance | **P** | "shall maintain … insurance" anchor; positives trustworthy, negatives not. |
| Expiration Date | **R** | The trap prediction: span-finding scores ~86 in the paper, but CUAD answers require *date arithmetic over other categories* ("five years following the Effective Date" → a computed date). Patterns find clauses; they do not compute calendars. Fig-8 rank ≠ automatable — this row is why our predictions are judgment, not a lookup. |
| Cap on Liability | **R** | Operational definition spans numeric caps, claim windows, and damage-type waivers, in prose or ALL-CAPS; positive patterns would catch fragments, but precision across forms won't gate, and negatives never will. |
| Audit Rights | **R** | P@80R ~46; "audit/inspect/examine books and records" phrasing varies and collides with audited-financial-statements language. |
| IP Ownership Assignment | **R** | P@80R ≈ 0 — bottom of the paper's figure; assignment hides in work-for-hire clauses, "sole and exclusive property" formulas, and event-triggered transfers. The spec's own example of what stays with the model. |
| Non-Compete | **R** | P@80R ~12; the spike showed the boundary (exclusivity vs non-compete) is an attorney-grade judgment call. |

**Pre-registered arithmetic (hand-audited).** 12 categories = 3 A + 4 P + 5 R. Annotation volume across the 12, full corpus: 3,774 labelled contract-category presences (sum audited: 510+509+465+433+374+329+275+255+214+167+124+119 = 3,774). A-share 1,408 (37.3%); P-share 1,305 (34.6%); A+P = 2,713 (**71.9%** of annotation volume with matcher participation); R-share 1,061 (**28.1%** model-resident). Expected stream positives (prevalence × 50/510): minimum ~11.7 (Non-Compete), all others ≥ 12.2 — every category clears the induction threshold N = 6 with room, so all twelve get a fair shot at the gate.

**Predicted stream dynamics**: A-category matchers born within the first two batches (each has ≥ 6 expected positives by contract ~8–12); P matchers by batch 3–4; from mid-stream the model's per-contract scope shrinks from 12 questions toward the 5 R categories plus P-negatives. As-run deviations are frozen and reported, never re-predicted.

## 5. Data design

```
Case Studies/04 Contracts/
  data/
    contracts/                  50 + 100 selected TXT files (verbatim copies, frozen)
    answer_key/<contract>.json  derived per-contract key (12 categories: presence, spans, answer)
    master_clauses.csv          verbatim copy (the key's source of truth)
    CUAD_LICENCE_ATTRIBUTION.md licence text + required citation
    manifest.json               source URL, zip MD5/SHA-256, per-file SHA-256, selection record,
                                stream order, split membership, library/tool versions
```

The answer-key derivation (`derive_answer_key.py`) is mechanical: parse the 24 relevant CSV columns (12 clause + 12 answer, including the malformed `Notice Period…- Answer` neighbour handled by exact-name mapping), split spans on `<omitted>`, normalise answers per schema (§7), stamp each record with its source row. Byte-identical across runs; the key files are the only place annotations exist inside the project tree, and the pipeline's agents are never given the `data/answer_key/` path or `master_clauses.csv`.

## 6. Integrity rules (non-negotiable, validated by script)

`validate_corpus.py`, `check_rule_N_<slug>` per rule, exit 1 on any failure:

1. **Manifest integrity** — every file in `data/contracts/` matches its manifest SHA-256; the manifest's zip checksums match the recorded download.
2. **Join completeness** — every selected contract maps to exactly one CSV row via the explicit filename map; map failures are enumerated, not skipped.
3. **Key parseability** — all 24 columns parse for all 150 selected rows; list-like clause strings parse without `eval`; yes/no answers are strictly `Yes`/`No`/empty.
4. **Answer well-formedness** — extraction answers parse under the schema's normalisation (dates parse to calendar dates or carry a declared redaction marker; Parties parse to a non-empty party list).
5. **Span presence** — every key span segment (split on `<omitted>`) is found verbatim in its contract text after whitespace normalisation; segments that fail are counted and reported per contract; the rule **fails** if > 10% of segments in any contract are unfound (TXT-fidelity caveat threshold, pre-registered — misses below threshold are recorded as key-vs-text artefacts for the adjudication lane, not silently accepted).
6. **Split discipline** — stream and holdout are disjoint, sized exactly 50/100, all members eligible (length cap, join, non-spike); stream order is recorded and seeded.
7. **Prevalence sanity** — per-category presence counts in the selection are within binomial 99% bounds of full-corpus rates (a mis-stratified draw fails loudly).
8. **Licence presence** — the licence/attribution file exists and carries the required citation.
9. **Derivation determinism** — two consecutive derivation runs produce byte-identical outputs (hashed, compared).
10. **Answer-key isolation** — no file under `code/matchers_generated/` and no pinned brief references `answer_key` or `master_clauses` (static check, same spirit as 03's).

## 7. Pipeline design

**One extraction schema** (`code/schemas.py`, authored in the main loop) binds the model path, the matchers, and the answer key: per category `present` (bool), `spans` (list of verbatim quotes), `answer` (normalised; null for yes/no categories). Normalisation rules, pinned: dates parse to ISO and compare as dates (the key's `m/d/yy` vs `mm/dd/yyyy` variance is a comparator concern, never an agent concern); Parties compare as sets of punctuation-normalised (full name, short name) pairs; Document Name and Governing Law compare case-/whitespace-insensitively with a jurisdiction lexicon for the latter; yes/no categories compare on presence. Spans are evidence, reported descriptively (coverage of key spans), never the scored unit.

**Model path**: Sonnet subagents under the pinned `design/extract_brief_v1.md` (CUAD-operational category definitions, spike lessons, hard file boundaries, audit-list requirement, schema + self-validation). Batches of 6–7 contracts, sequential, ~8 batches for the stream; per-batch tokens and wall time logged to `data/runs/extract_agent_log.json`; schema-invalid output → one logged retry (costed); **hard cap 60 reads total** (50 stream + ≤ 10 retry/fallback reserve — Luigi, 3 Jul 2026).

**Scope narrowing (the mechanism, not a simulation)**: before each batch, the router computes each contract's remaining categories given currently-active matchers; the batch brief asks only for those. Matcher-covered categories are answered by code before the batch is dispatched; P-category non-hits are explicitly listed in the brief as fallback questions. The model's shrinking scope is real work not done, batch by batch — not a replay counterfactual.

**Overseer**: after each batch, per category with ≥ N = 6 accepted positives (and, for two-sided claims, ≥ 6 accepted negatives) and no matcher yet, a Sonnet overseer agent is commissioned under `design/overseer_brief_v1.md`: inputs are the category's accepted extractions plus the relevant contract texts **only** (no key, no CSV); output is one Python matcher, stdlib-only (`re` + text utilities), fail-loud (`NoMatch` result, never a guess), with provenance header and a mandatory self-test over its induction examples. Matchers live in `code/matchers_generated/` — session artefacts, like 02/03's parsers.

**Activation gate** (`code/regression_gate.py`, deterministic): the matcher must reproduce the model's accepted results on its induction set — 100% agreement for an A claim (positives and negatives), 100% precision on positives for a P claim — and is then regression-checked against every subsequent stream contract the model still reads. Any post-activation disagreement on overlap, or gate failure, demotes the matcher; demotions are frozen and reported (the honest inverse of 03's re-learning exhibit). The gate never touches the answer key.

**Router** (`code/router.py`): deterministic replay of the whole stream — which category of which contract was answered by which path, when each matcher was born, what each read's scope was; consistency-checked against the agent log and matcher records.

**Evaluation** (`code/evaluate.py` — the only key-reading step): per category × path, presence accuracy (yes/no) and answer accuracy (extraction) against the derived key, on the stream; matcher-only marking on the 100-contract holdout; the equivalence exhibit per A/P category (matcher-vs-key on holdout alongside model-vs-key on stream, with counts); the predicted table as-run; disagreement extraction for the adjudication lane (§8); cost accounting (§9).

## 8. Evaluation honesty — the adjudication protocol

Tier 1 is mechanical and headline: id-level comparison under the pinned comparators, no prose matching, reported as-marked. **The key is treated as authoritative for scoring and is never edited.**

**Span-only presence (pre-registered 3 Jul 2026, before any pipeline run).** CUAD sometimes records supporting spans for an extraction category but leaves the normalised answer blank — measured: 86/510 Expiration Dates, exactly the category whose answers require computation. Comparing a pipeline answer against a blank is not marking; those rows are therefore scored on presence only (comparator axis `presence-only`), excluded from the answer-accuracy denominator (which covers key-answerable rows), and routed to the adjudication lane by construction. Both counts are always published side by side.

Tier 2 is the adjudication lane, pre-registered: every extraction-category disagreement, every A/P-category disagreement (both paths), and a seeded sample of 20 R-category disagreements are adjudicated by hand in the main loop — the passage quoted, both readings stated, each classified as *pipeline wrong* / *key arguably incomplete or wrong* / *genuinely ambiguous*. Published alongside the as-marked scores, with counts. Framing fixed here: CUAD's annotators did expert work at a scale we benefit from freely; where we disagree with the key, that is a finding about the margins of expert annotation — exactly what a client should expect contract review to look like — not a defect hunt. If both paths agree against the key, that case is *always* adjudicated (it is either our shared error or the most interesting row in the case).

## 9. Cost accounting (method B — portfolio decision, restated)

Claude Code subagents, zero marginal spend; all cost figures are labelled estimates (published per-token prices × measured subagent tokens, upper-bound band + stated-split central estimate; pricing reference verified on the run date). Spike calibration: 64,478 subagent tokens for a median (5k-word) read → stream ≈ 3.2M subagent tokens. Stated honestly: input (reading the contract) dominates a read's cost, so scope narrowing mainly saves output work within the learning year — **the demonstrated saving is the holdout year**, where A/P categories are answered by code that costs nothing, on twice the stream's volume, and the model is priced only for the R residue (counterfactually, since the budget does not run it). No 03-style crossover curve is promised; the exhibits are category retirement, holdout equivalence, and the honest per-category account of what stayed manual and why.

## 10. Deliverables

| Deliverable | Content |
|---|---|
| `data/runs/report.md` | Findings: predicted-vs-actual per category, equivalence table, adjudication findings, deviations frozen |
| `notebooks/contract_review_analysis.ipynb` | Technical narrative; all numbers read from `data/runs/` at run time, live asserts; N-threshold sensitivity ablation; validated palette |
| `interactive/contract-review.html` | Self-contained page (churn embeddability constraints): a boilerplate clause and a bespoke one side by side (real text, quoted, attributed); the stream timeline with matcher births; the predicted-vs-actual centrepiece; drill-down from category → real language → the matcher's actual pattern → both paths' answers; the honest overlay (R categories and why; adjudicated disagreements; attribution block) |
| `writeup/contract_review_case_study.md` | Canonical long-form; trilogy-closer framing; companion to 02/03; not-legal-advice line; CC BY attribution |
| `README.md` | Folder map, pipeline order, ⚠️ regenerate-vs-artefact split |

## 11. Gate decisions and what remains reversible

Decided at the gate by Eva's advance direction (recorded with rationale in `DECISIONS.md`): the 12-category selection (§3); 50/100 stream/holdout (§2); real-data-first public framing; synthetic supplement OUT (spec deviation, recorded); predictions published with misses kept; adjudication lane published with the fixed framing (§8); trilogy-closer positioning; "contract review" naming with the due-diligence scenario. Reversible at her review without invalidating results: all copy/framing/naming decisions, the interactive page's presentation choices, the writeup's positioning. Not reversible after Phase 3 without re-running: category selection, split sizes, N, the cap, comparator rules — which is why they are pre-registered here.
