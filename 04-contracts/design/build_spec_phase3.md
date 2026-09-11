# Build spec — Phase 3: pipeline tooling (Project 4)

For: python-builder. Authored in the main loop, 3 July 2026. Read `design.md` §7–§9, both pinned briefs, and `schemas.py` first. Everything here is pre-registered semantics — implement exactly; deviations are design changes and go through me.

## Semantics pinned here (the contract between all tools)

**Stream**: the manifest's 50 stream contracts in recorded order, batched **6,6,6,6,6,6,7,7** (8 batches).

**Read accounting**: a *read* = one contract processed by an extraction agent (a retry of the same contract = +1 read). Hard cap `config.READ_CAP = 60`; `accept_batch.py` refuses to accept work past the cap and fails loudly.

**Matcher lifecycle**: `none → commissioned → active | failed → demoted?`
- **Commissioning trigger** (evaluated after each accepted batch): category has no matcher and ≥ `N_INDUCTION = 6` accepted positives. Trust grade at commissioning: extraction categories get `two-sided` if additionally ≥ 3 accepted negatives exist, else `one-sided`; yes/no categories are ALWAYS `one-sided` (a pattern cannot prove absence of a clause — design.md §4).
- **Activation gate** (below) must PASS before a matcher routes anything.
- **Active from the next batch** after gate PASS, never retroactively.
- **Demotion triggers**: (a) schema-invalid or non-verbatim-span output at batch-prep time; (b) shadow-regression disagreement (below). Demotion is permanent for the run; frozen and reported.

**Matcher call semantics**: `match(text)` returns `{present, spans, answer}` or raises `NoMatch`. One-sided matchers may only return `present: True`. NoMatch → the category goes on that contract's LLM question list. Matcher outputs are validated at batch-prep: schema shape + every span verbatim (after `schemas.norm_ws`) in the contract text; violation → demotion + category returns to the LLM path for that and subsequent contracts.

**Shadow regression** (declared in the report; answers marked separately, never merged into the path accuracy tables): in every batch, each *active* category is added to the question list of exactly ONE contract of that batch that the LLM is reading anyway — chosen by seeded rotation (`random.Random(RANDOM_SEED + batch_number)` over the batch's LLM-read contracts, i.e. contracts with a non-empty question list at that point) — max 2 shadow categories per contract; excess shadows dropped by seeded priority and logged. A shadow answer disagreeing with the active matcher's answer for that contract = demotion trigger (adjudicated at evaluation; the demotion itself is mechanical and immediate).

**Answer-key isolation**: none of the files in this spec except `evaluate.py` may reference the key (rule 10's whitelist already encodes this).

## Files to write

### 1. `code/pipeline_common.py`
Shared helpers: manifest loading, stream order, batch membership (sizes above), matcher-state load/save (`data/runs/matcher_state.json`), matcher module loading by path (importlib; call `match`; catch `NoMatch`), accepted-extraction store access (`data/runs/llm_extractions/`), matcher-output store (`data/runs/matcher_outputs/<stem>.json`, accumulated per category), read-count accounting, span-verbatim check via `schemas`.

### 2. `code/prepare_batch.py --batch N`
1. Load matcher state; refuse if batch N-1 not accepted (sequential discipline).
2. For each contract in batch N: run every *active* matcher; record outputs (with `"path": "matcher"`, matcher id, trust) to the matcher-output store; on `NoMatch` add category to the contract's question list; on validation violation → demote (update state, move category to questions, print loudly).
3. Compute shadow assignments per the pinned rule; add to question lists with a separate `"shadow": {...}` map in `questions.json` so accept/evaluate can split them.
4. Write `data/runs/batches/batch_NN/`: contract copies, `questions.json` (contract → asked categories, plus the shadow map), and print the batch summary (per-category path counts, questions per contract, projected reads).

### 3. `code/accept_batch.py --batch N`
1. For each expected `out/<stem>.extraction.json`: parse; `schemas.validate_record(rec, asked ∪ shadow)`; every span verbatim in the contract text (norm_ws); every asked category present, no unasked extras. Any failure → the file is REJECTED (listed with reasons); the caller (me) decides retry (retry = new read; cap enforced).
2. On full-batch acceptance: append non-shadow answers to `llm_extractions/`; append shadow answers to `data/runs/shadow_answers.json`; run shadow-vs-matcher comparison (via `schemas.compare_category`) → any disagreement demotes the matcher NOW (state update + loud print).
3. Update read count (+contracts accepted, +retries recorded via `--retries K` flag when I re-dispatch).
4. Print commissioning candidates: categories crossing the trigger with their positive/negative counts and the trust grade they qualify for.

### 4. `code/prepare_commission.py --category "X"`
Builds `data/runs/commissions/<slug>/`: `induction/` (that category's accepted extractions, one JSON per contract), `contracts/` (the corresponding TXT copies; for two-sided also the accepted-negative contracts), `commission.json` (category, slug, trust, target matcher path, induction list, id `c<NN>-<slug>`). Refuses if a matcher already exists for the category.

### 5. `code/regression_gate.py --category "X"`
Order: (1) static checks on the matcher file — imports stdlib-only from an allowlist (`re`, `datetime`, `string`, `math`, `unicodedata`, `typing`, `dataclasses`), forbidden tokens (`open(`, `import os`, `import sys`, `import pathlib`, `import random`, `import time`, `requests`, `socket`, `subprocess`, `eval(`, `exec(`), `TRUST` equals the commission's, `PROVENANCE["induced_from"]` equals the commission list, `NoMatch` defined and raised somewhere; (2) run the module's `self_test` with a loader that serves induction contract texts; (3) replay `match` over EVERY accepted LLM extraction for the category (not just induction): compare via `schemas.compare_category` treating the accepted extraction as reference — disagreement = FAIL; `NoMatch` = coverage miss, counted and reported (coverage = matched/total); (4) one-sided matchers returning `present: False` anywhere = FAIL. Result → `data/runs/gate_results/<slug>.json` + PASS/FAIL exit code. PASS flips state to active (from next batch).

### 6. `code/run_matchers.py --set holdout`
Run all *active* matchers over the 100 holdout contracts → `data/runs/matcher_outputs_holdout/`. Same validation (schema, spans verbatim, one-sided discipline); violations here don't demote (the stream is over) — they are recorded and reported as holdout failures. Also record per-category coverage (answered vs NoMatch).

### 7. `code/router.py`
Deterministic replay: for each stream contract in order, per category: resolve the path (`matcher` / `llm-discovery` / `llm-fallback` (matcher NoMatch) / `llm-shadow` overlay) from the stores; assemble the pipeline's final record per contract; consistency-check: every category of every stream contract answered exactly once on the primary path; matcher activation batch boundaries respected; read counts match the agent log; shadow overlay consistent. Writes `data/runs/stream_events.json` (events: reads, births, demotions, per-batch scope sizes) — the interactive page's data source.

### 8. `code/evaluate.py` (the ONLY key-reading pipeline file)
Marks, per category × path (matcher / LLM), stream and holdout separately, against `data/answer_key/`:
- yes/no: presence accuracy; extraction: presence accuracy + answer accuracy over key-answerable rows + `presence-only` row counts (axis from `schemas.compare_category`).
- The equivalence table per matcher category: holdout matcher accuracy + coverage alongside stream LLM accuracy, with counts.
- Predicted-vs-actual outcome table (predictions hardcoded from design.md §4 — A/P/R per category; actual = matcher state + coverage + equivalence at thresholds: A-actual = two-sided active + holdout coverage ≥ 95% + accuracy within 2 pp of LLM stream accuracy; P-actual = active otherwise; R-actual = never activated/demoted).
- Disagreement worksheet: every pipeline-vs-key mismatch (both paths), with contract, category, both values, and ±300 chars of contract context around the best-matching span, → `data/runs/evaluation_worksheet.md`; plus the seeded R-category sample (20, `random.Random(RANDOM_SEED)`) and ALL both-paths-agree-against-key cases flagged `adjudicate-first`.
- Costs: from `data/runs/extract_agent_log.json` (written by me at run time): total measured subagent tokens; method-B bands (pricing constants with a `pricing_reference` field I will fill; every cost figure carries `"estimate": true`); the holdout counterfactual (what 100 full reads would have cost at the stream's mean tokens/read) vs the matcher path's zero — labelled estimate.
- Output `data/runs/evaluation.json` (+ the worksheet). Deterministic (sort keys, no timestamps).

### 9. Selftests
`code/test_pipeline.py`: synthetic fixtures (tiny fake manifest, fake contracts, fake matchers incl. a NoMatch-raiser, a span-violator, a one-sided-False violator) covering: batch membership arithmetic (6×6+2×7=50), commissioning trigger incl. trust grading, gate static checks catching each forbidden token, gate replay disagreement→FAIL, shadow assignment determinism + max-2 rule, demotion on shadow disagreement, router consistency check failing on a fabricated double-answer, evaluate's presence-only split and A/P/R classification thresholds. Every test prints PASS/FAIL; exit 1 on any failure. Do NOT touch real `data/` in tests — fixtures under a temp dir.

## Verification you must run before returning
- `python code/test_schemas.py` (38 checks) and `python code/test_pipeline.py` both exit 0.
- `python code/prepare_batch.py --batch 1` against the REAL corpus (no matchers active yet → all questions full scope except none; batch folder written) — then DELETE `data/runs/batches/batch_01/` and any state it wrote, confirm `git`-free tree back to pre-run state by hashing `data/runs/` before/after (it should not exist before; simply remove it). Report what batch 1 looks like (contracts, question counts).
- Report: files written, selftest counts, batch-1 dry-run summary, anything ambiguous you resolved (and how) or left for me.
