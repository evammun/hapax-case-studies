# Phase 3 build specification (internal)

Authored by the main loop, 3 July 2026. Pins the pipeline semantics for the regression gate,
router replay and evaluation. python-builder implements `regression_gate.py`, `router.py` and
`evaluate.py` mechanically from this; the parse and overseer agents run under the pinned briefs
(`parse_brief_v1.md`, `overseer_brief_v1.md`). Main loop reviews everything and runs every step
personally.

## Shared ground

- **Master data for the router** comes from `data/master_data.json` (exported from config by
  `code/export_master_data.py`): supplier identity blocks (name, country, VAT id, business id,
  IBAN/BIC/bankgiro, reference system, terms) for all 26 suppliers + the PO register
  (po_number, supplier_id, po_date). This file is "what a real AP system knows"; the router
  never imports `config.py` (which also knows the planted events) and never touches
  `data/answer_key/`.
- **Accepted LLM parses** live in `data/runs/llm_parses/<doc_id>.json`; acceptance = passes
  `schemas.validate_record`. A schema failure is a pipeline event: logged, and the document is
  re-parsed once in a later batch (the retry is costed like any parse — Case 2 convention).
- **Parser registry**: `code/parsers_generated/parser_<slug>.py` (slugs: s1…s8 for v1 layouts,
  `s8v2` for the re-learned layout). Each has an induction manifest JSON next to it
  (`parser_<slug>.induction.json`: doc_ids + parse paths it was induced from, written at
  dispatch time by the main loop, not by the agent).

## Overseer trigger (pipeline rule, applied in stream order)

A parser for a (supplier, layout) pair is **born** when the pair's 6th accepted LLM parse
exists. Its **birth position** in the stream = immediately after that 6th document. One-off
suppliers never reach 6. s8's post-redesign documents form a new pair (v2): its first 6
fallback parses are v2's induction set, so `parser_s8v2` is born after the 6th post-redesign
document — the re-learning needs no special rule (design §7).

## regression_gate.py (no answer-key access — gate against the pipeline's own history)

For each generated parser:
1. **Activation gate**: run `parse()` on each induction PDF; deep-compare to the accepted LLM
   parse (exact equality of the record dict). All N must match or the parser FAILS the gate.
2. **Full-corpus dry run**: run the parser on every document of its supplier (all layouts),
   record the outcome per document: OK (returns a record that passes `schemas.validate_record`
   and the master-data existence checks), LAYOUT-ERROR (ParserLayoutError), or
   VALIDATION-FAIL. No comparison to the answer key here.
3. Print a per-parser and per-class outcome table; exit non-zero if any activation gate fails.

## router.py (stream replay; no answer-key access)

Replay all 198 documents in stream order (issue date, then doc_id). For each document:
1. Determine live parsers for its supplier at this stream position (born earlier). Try them
   newest-first. A parser "succeeds" when `parse()` returns without ParserLayoutError AND the
   record passes `schemas.validate_record` AND the **existence checks**: supplier identity
   fields match the master data; `po_number`, when present, exists in the PO register for that
   supplier; IBAN/bankgiro belongs to that supplier. (Deliberately NOT checked: line-level
   quantities/prices against PO contents — the three-way match is the production
   recommendation, not part of this router; design §7.)
2. If no parser succeeds → the document takes the LLM path: its accepted parse from
   `data/runs/llm_parses/` is the result (discovery documents take the LLM path by
   construction — no parser is live yet).
3. Every event goes to `data/runs/stream_events.json`: doc_id, date, supplier, path taken
   (`llm-discovery` / `llm-oneoff` / `deterministic` / `llm-fallback`), parser tried/failed
   reasons, parser births as their own events.
4. Consistency requirement: the set of documents that end on the LLM path must equal the set
   of parse files that exist (the LLM waves are run exactly for the documents the replay needs;
   mismatch = exit 1). The answer key plays no part.

## evaluate.py (the marking step — the ONLY pipeline code that reads the answer key)

Produces `data/runs/evaluation.json` (page- and notebook-ready):
1. **Accuracy**: field-level per path (deterministic / LLM), via `schemas.compare_records`
   against the answer key; the S document's two designed mismatches reported as their own
   line-item (`s_doc`), excluded from the error counts and stated separately (design §4);
   both "excluding S" and "including S" figures emitted (Case 2 convention).
2. **Scorecard**: per-class designed outcome (§4 table) vs actual outcome from
   `stream_events.json`; every deviation listed (deviations are frozen and reported, never
   patched — Case 2 precedent).
3. **Shares**: whole-stream deterministic share; per-month share; parser-birth timeline
   (supplier, birth date, documents seen before birth); the long-tail exhibit (suppliers
   automated vs volume automated).
4. **Costs (labelled estimates, method B)**: read `data/runs/parse_agent_log.json`
   (per-batch: doc_ids, subagent_tokens, wall_ms, model). Hybrid cost = measured total agent
   tokens priced at published Sonnet rates as a band — all-input floor, all-output ceiling,
   central estimate at a stated 85/15 input:output split (Case 2 method; the
   pricing_reference block records prices and date). All-LLM counterfactual = (measured mean
   tokens per parsed document) × 198, same band method. Deterministic-path marginal cost = 0;
   parser-generation cost = overseer-batch tokens, amortised in the cumulative curve at each
   parser's birth. Every cost field in the JSON carries `"estimate": true`.
5. **Latency**: per-batch wall-clock from the log, labelled harness-inclusive.

## Cap accounting

Designed LLM-path volume is 78 (§4). Actual = 68 (discovery + one-offs) + only the T/F
documents that actually fall back in the dry run/replay. If a planted trap is defeated
(parses correctly deterministically — Case 2's FBL1N precedent), its LLM parse is simply
never commissioned; the deviation is reported in the scorecard. Actual total must stay ≤ 80;
the main loop checks the count before dispatching each wave.

## Findings report

`data/runs/report.md` is written by the main loop from the evaluation output (not delegated):
scorecard vs pre-registration with deviations, the S-doc result, vision-read error patterns
(dense identifiers especially), retry log, brief-version log, cost-method notes.
