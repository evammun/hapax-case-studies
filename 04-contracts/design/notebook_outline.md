# Notebook outline — `notebooks/contract_review_analysis.ipynb`

For: python-builder. Authored in the main loop, 4 July 2026. The notebook is the technical narrative (WS4 material). Hard rules:

- **Every number is read at run time** from `data/runs/evaluation.json`, `data/runs/stream_events.json`, `data/runs/holdout_coverage.json`, `data/runs/extract_agent_log.json`, and `data/manifest.json`. NO result literals hardcoded (the two exceptions below are labelled as hand-adjudicated constants). The notebook NEVER opens `data/answer_key/` or `master_clauses.csv` — it analyses marked results, it does not re-mark.
- **Live asserts** on headline figures (they double as regression checks): stream size 50; holdout 100; total reads 52; comparisons marked 776 (sum over scoring tables); predictions matched == 4; active matchers == 8; holdout violations == 0; Audit Rights holdout coverage == 0.0; Expiration Date holdout n == 4.
- Paths via `pathlib` relative to the notebook (`Path.cwd().parent / "data" / "runs"` guarded, or resolve from `__file__`-less notebook: use `Path().resolve()` climbing to the project root by looking for `data/runs/evaluation.json`).
- Charts: matplotlib only, on `#FBFAF5`; marks wine `#A8352A`, indigo `#41529E`, gold `#B68A2C`; grey `#665E58` for context series only (always direct-labelled); beige `#EFE5CE` fills; ink `#1A1410` text; ≤3 identity hues per chart; one y-axis; no colour-cycling; direct labels over legends where feasible; British English throughout; spaced en-dashes; typographic apostrophes in markdown cells.
- Opening markdown cell: what this is, the real-data framing (CUAD, CC BY 4.0, attribution + citation), the not-legal-advice line, and the "answer key held out; both paths marked; key never edited" honesty statement.

## Cells (≈ 30–36)

1. **Title + framing** (markdown, per above).
2. Imports + palette constants + data loading + root-finding; print library versions.
3. Assert block (the live asserts above).
4. **The corpus** (markdown + cell): from `manifest.json` — 510-contract source, eligibility (≤15k words, joined, non-spike), seeded stratified draw, stream 50 / holdout 100. Table of type × band counts for the selection. **Figure 1**: word-count histogram of the 150 selected (beige fill, ink edge) with stream/holdout medians direct-labelled (wine/indigo rug or markers).
5. **The stream** (markdown): 8 sequential batches, cap 60, key-blind, briefs frozen.
6. **Figure 2 — scope narrowing**: per batch (x = batch 1–8), stacked/step view of per-contract question-list sizes from `stream_events.batches[*].scope_sizes` — mean questions per read per batch (indigo line, direct-labelled) against the full scope of 12 (grey dashed context line). Annotate matcher births (gold markers w/ category initials) and demotions (wine markers) at their batches from `matcher_lifecycle` history.
7. **Matcher lifecycle table** (cell → styled DataFrame): category, commissioned batch, gate result, active-from, demoted-at + reason (truncated), final status, trust.
8. **The gate and the shadows** (markdown): gate order (static → self-test → replay), one gate failure, 33 shadow comparisons → 3 demotions; the four uncaught errors found later at adjudication (hand-adjudicated constant, labelled).
9. **Figure 3 — predicted vs actual**: 12 rows, two columns of coloured chips (predicted vs actual; A gold / P indigo / R wine), match ticks; count 4/12 asserted. (Render as a matplotlib table-like plot with text — keep it legible at notebook width.)
10. **Coverage & equivalence** (markdown incl. the selection-effect caveat, verbatim from report.md's framing).
11. **Figure 4 — holdout coverage vs accuracy**: per active category, horizontal bars for coverage (indigo) with accuracy printed at bar end and holdout n in brackets; Audit Rights' zero bar explicitly labelled "answered nothing"; Expiration Date's 50% flagged wine.
12. Accuracy tables (cell): the three path/split aggregates recomputed from the scoring tables (assert equal to report's numbers via recomputation, not literals).
13. **Presence-only rule** (markdown + cell): count from worksheet_counts; explain the pre-registered rule.
14. **The adjudication** (markdown): family table with hand-adjudicated counts (labelled "hand-adjudicated constants, from data/runs/report.md — not machine-derived"): key errors ~15, ambiguous ~28, comparator-strictness ~19, model errors ~8, matcher errors ~10; the ≈2%-of-everything-marked contextualisation; key never edited.
15. **N-threshold sensitivity ablation**: from `data/runs/llm_extractions/` + batch membership (pipeline outputs, not the key): for N in 3..10, compute per category the batch at which the Nth accepted positive lands (birth-eligibility timing). **Figure 5**: heatmap-ish matrix (categories × N) of eligibility batch, sequential shading built from beige→indigo (fills, not hues), real N=6 column outlined in gold; assert the N=6 column reproduces the actual commissioning batches from the lifecycle history. Markdown: what changes at N=4 (earlier births, more risk — cite the Parties/Document Name demotions) and N=10 (Insurance and the late bloomers never commission inside a 50-contract stream).
16. **Costs** (markdown + cell): method B restated; bands from `evaluation.json['costs']` printed as a small table; every figure suffixed "(estimate)"; the holdout counterfactual + the matcher path's $0; the honest note that this is not a crossover story (design §9).
17. **Limitations** (markdown): shadow sampling density; one-run non-determinism of agent outputs (session artefacts, never re-run); the comparator's Parties strictness; CUAD near-duplicates; batch-7 unmeasured segment.
18. Closing markdown: attribution block (CUAD citation, CC BY 4.0), synthetic-vs-real framing sentence, not-legal-advice line.

## Verification you must run before returning
- `python -m nbconvert --to notebook --execute --inplace notebooks/contract_review_analysis.ipynb` exits 0, zero error outputs.
- Grep the executed notebook JSON for suspicious hardcoded results (e.g. "98.3", "4/12") outside the two labelled hand-adjudicated cells — every headline number must come from a variable.
- Extract the five figures as PNGs to the session scratchpad and report their paths (I will inspect them visually).
- Report cell count, assert results, and anything ambiguous you resolved.
