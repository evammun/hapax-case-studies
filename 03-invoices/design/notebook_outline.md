# Notebook outline — invoice_processing_analysis.ipynb

Authored by the main loop, 3 July 2026. python-builder implements; main loop re-executes and
reviews. Portfolio conventions: every number read from run artefacts at execution time (no
result literals in code cells), live asserts on headline figures, restrained styling, modest
figure sizes, the validated chart palette (wine `#A8352A`, indigo `#41529E`, gold `#B68A2C`
on `#FBFAF5`; grey `#665E58` context-only; beige `#EFE5CE` fills; ink `#1A1410` text —
re-validated with the dataviz validator on 3 Jul 2026, all checks pass). British English,
en-dash typography, no banned voice patterns.

**Inputs** (all under `data/`): `runs/evaluation.json`, `runs/stream_events.json`,
`runs/parse_agent_log.json`, `manifest.json`, `master_data.json`. **The notebook never opens
`data/answer_key/`** — marking already happened in `evaluate.py`; state this in §1.

## Sections

1. **What this is.** One markdown cell: the pipeline in five sentences; synthetic-data
   disclosure (known answer key, results marked not asserted); pointer to design.md and
   report.md; how to re-execute; the no-answer-key note. Load all inputs in one code cell.

2. **The corpus at a glance.** From manifest + master_data: 198 documents, 26 suppliers,
   12 months of 2025, five languages/locales, class table R/O/T/F/S with counts and one-line
   meanings (from design §4). Assert class counts equal 165/20/8/4/1.

3. **The stream replay.** Path counts from stream_events (assert 117/48/13/20). **Figure 1 —
   monthly composition**: stacked bars per month, deterministic (indigo) below, LLM path
   (wine) above, 2px white gaps, direct labels on totals only; grey annotation marking August
   ("supplier redesign") and the December share. One y-axis (document count).

4. **Parser births and the re-learning arc.** **Figure 2 — timeline**: months on x, one row
   per parser, birth plotted as a ≥8px marker (indigo; `s8v2` in gold with the annotation
   "re-learned after the August redesign — same N=6 rule"); grey vertical line at the
   redesign date. Markdown: the T-story in four sentences; s7 as the slow learner
   (monthly cadence → June birth).

5. **Accuracy against the answer key** (from evaluation.json, computed by evaluate.py).
   Per-path table (docs, fields, errors, accuracy). The S-document panel: what it is, why
   both paths read it "wrong" (the document lies at the source), what catches it in
   production (**three-way match**), explicitly labelled "designed mismatch — not an
   extraction error". Live asserts: LLM accuracy == 100.0000% (5,427 fields), overall wrong
   values == 2 and both belong to the S document, deterministic-excl-S == 100%.

6. **The designed-outcome scorecard.** Table: class, designed, actual, verdict — the two
   deviations rendered honestly (F1 defeated; four two-page fallbacks with the fail-loud
   explanation). Assert the deviation list from evaluation.json has exactly the four
   class-path rows recorded in report.md and no others.

7. **Costs — labelled estimates.** Markdown states method B up front (measured subagent
   tokens, harness-inclusive; published Sonnet list prices with the intro-pricing
   disclosure from parse_agent_log.pricing_reference — quote its note verbatim).
   **Figure 3 — cumulative cost**: x = document index in stream order, two lines: all-LLM
   counterfactual (wine) vs hybrid (indigo); hybrid includes parser-generation cost added
   at each parser's birth position (step up); beige band optional for the input/output
   pricing band — if used, label it "estimate band"; direct labels at line ends; annotate
   the year-end near-crossover ("automation ≈ paid for itself in year 1") and the "every
   figure an estimate" caption. **Then the amortisation paragraph**: year-2 extrapolation
   (one-off tail + occasional fallbacks only) with the ~87% steady-state figure computed
   from the same per-document means, clearly labelled an extrapolation.

8. **The long tail.** **Figure 4 — two horizontal bars**: share of suppliers automated
   (8/26 = 31%) and share of volume those suppliers carry (178/198 = 90%), indigo, direct
   labels, one sentence on why the other 69% of suppliers (10% of volume) stay with the
   model on purpose. Compute both from master_data + stream_events (not hardcoded).

9. **N-threshold sensitivity (ablation).** Pure-Python simulation over the replayed stream:
   for N in 4..10, recompute discovery counts, birth positions, re-learning, and the
   resulting LLM-parse count and whole-stream deterministic share (no agents re-run — the
   simulation only re-applies the birth rule to the recorded stream order; state this).
   **Two small side-by-side charts (one measure each, no dual axis)**: LLM parses vs N
   (wine), deterministic share vs N (indigo); gold marker at N=6 (the chosen value, driven
   by the ≤80 parse budget). One markdown paragraph: the trade-off and why the budget set N.

10. **What transfers.** Closing markdown: fail-loud beats silent guessing (the two-page
    finding); re-learning is the same rule as learning; the three-way match recommendation;
    check the key before trusting it (the four ground-truth fixes found by first contact).

## Verification (main loop)

- Re-execute top-to-bottom via nbconvert on this machine, exit 0, no error outputs.
- No result literals hardcoded in code cells; grep the notebook JSON for suspect constants.
- All four figures render; inspect visually (label collisions, overflow, palette).
- Asserts pass live against the artefacts.
