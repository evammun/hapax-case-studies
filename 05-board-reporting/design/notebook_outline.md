# Notebook outline — `notebooks/board_reporting.ipynb`

Agreed outline (main loop, 3 July 2026). python-builder implements exactly this; no
new design decisions in the notebook. Voice: direct, factual, British English; the
main loop does the final prose pass after execution.

## Global style (first code cell)

- matplotlib only; figures modest (≈ 7×3.5 in, dpi 130), solid fills, no chartjunk;
  light y-grid only (`#EFE5CE`-tinted, thin), spines minimal (left/bottom only, Grey).
- **Chart palette (validated 3 Jul 2026 via the dataviz procedure — do not substitute):**
  marks `WINE = "#A8352A"`, `INDIGO = "#41529E"`, `GOLD = "#B68A2C"`;
  context/reference series `GREY = "#665E58"` (always direct-labelled, often dashed);
  text `INK = "#1A1410"`; fills/bands `BEIGE = "#EFE5CE"`; figure face `#FBFAF5`.
  The raw brand tokens are NOT mark colours (they fail the lightness/chroma checks);
  these are the brand-derived, validated tints.
- Titles in Cormorant Garamond if available (serif fallback, silent); tick/annotation
  text default sans, Ink/Grey. Text never wears a series colour.
- Rules that bind every chart: one y-axis per chart (different units → index to a
  common base, never twin axes); colour carries ≤ 3 identities, assigned fixed
  (never cycled); legend whenever ≥ 2 series plus selective direct labels; numbers
  formatted €k/€M with thin ticks.

## Section plan

**0. Head matter** (markdown): title; the honesty statement up front — synthetic
dataset, engineered with a held-out answer key, seed 42, pointer to `design/design.md`
and the pipeline; what this notebook shows (pack → storytellers → marking).

**1. The company at a glance.** Load the nine public CSVs only. Headline table
FY2024/FY2025: net revenue, growth, GM%, EBITDA reported and underlying, DSO
(Dec, trailing-12), revenue/head. `assert` each against these anchors (from
`evaluation_worksheet.md` §E): FY24 revenue 154,680,645.51; FY25 168,028,808.07;
growth 8.63%; GM 42.54/40.23; EBITDA reported 17,956,325.27 / 17,697,896.35;
underlying FY25 15,497,896.35.
**Chart 1** — company monthly net revenue, 24 months, single Wine line (no legend);
Decembers ticked subtly; Jan-2025 annotated. Caption: everything that follows starts
from this shape.

**2. The pack (deterministic layer).** What `variance_analysis.py` does; print the
surface report's methodology block verbatim; flag counts by measure × basis from
`variances_monthly.csv` (small table).
**Chart 2** — "January 2025, three comparisons": three bars around a zero baseline
(MoM −28.7%, YoY +2.6%, vs budget −1.6%), single Indigo, direct labels, no legend.

**3. S4 — the trap.**
**Chart 3** — monthly net revenue, actual (Wine) vs budget (Grey dashed, end-labelled),
Jan-2025 band in Beige. Prose: the pack must flag January (it breaches any honest MoM
threshold); the correct answer is stand down; all three storyteller runs did.

**4. S1 — the mix shift that reads as input inflation.**
**Chart 4** — Nordics, indexed to FY2024 monthly average = 100, one axis: material
spend (Wine), volume (Indigo), unit material cost (Grey, flat — the decisive line).
Legend + end labels.
**Chart 5** — Nordics volume share by product line, 2024 vs 2025: grouped bars,
x = line, colour = year (2024 Grey, 2025 Wine), % direct labels. Prose: Home Care
36→46% of volume at ~19% promo discount from February; unit costs flat ±0.5%;
what the commentary would have said ("input inflation") vs what the data says.

**5. S2 — the DSO creep behind a one-off.**
**Chart 6** — €: Rheinkauf closing AR monthly (Wine), Rheinkauf monthly net revenue
(Grey, flat), rest-of-CE AR (Indigo). Legend + end labels. Caption: balance triples,
billing doesn't move.
**Chart 7** — cash conversion, H1-2024 vs H1-2025, reported (Indigo) vs underlying
(Wine): four bars, % single axis, direct labels. Prose: the €2.2M gain sits in other
income, €5.5M proceeds in investing; every number disclosed, nothing connected —
the mask is attention, not concealment.

**6. S3 — growth bought with discount, and the exhibits nobody claimed.**
**Chart 8** — Baltics discount rate by month, 2024–2025 (Wine), budget assumption
(Grey dashed). Caption: 8% → 17%, a ladder not a step.
**Chart 9** — two-panel figure, clearly captioned "**in the data; claimed by 0 of 3
runs**": (a) horizontal bars, Dec-2025 discount rate per named Baltics customer,
Grey bars with the three >18% in Wine, 18% reference line, labels; (b) volume
response per promotional euro, H1 vs H2 2025, two Indigo bars, direct labels
(H2 ≈ 38% weaker). Panel (b) values recomputed the honest way: state in a markdown
note that the counterfactual baseline comes from the generator's driver model
(generation-side), so this exhibit uses `code/` — it is the *designer's* proof the
signal exists, not something a reader of the public CSVs alone could compute for (b);
panel (a) is fully public-data.

**7. The storyteller layer and the marking.** Protocol (pinned briefing, three
blinded Opus subagent runs, transcript audits, no answer-key access; subscription
execution, no cost figures claimed). Load `run_0*_findings.json`: cluster × run
verdict table; findings-count table. Then the marking: load
`data/answer_key/stories.csv` **here and only here** (markdown note: the answer key
enters the notebook at evaluation time, mirroring the pipeline); scorecard table
exactly as `data/analysis/report.md` states it (S1/S2/S4 3/3; S3 found 3/3 with
both designed exhibits 0/3; N4 1/3; false positives 0; incorrect figures 0).
**Figure 10** — the designed-outcome 2×2 as a styled matplotlib figure (Beige cell
fills, Ink text, thin Grey rules): rows = pack raises an alarm / stays calm,
columns = real story / no story; cells name S1–S4 + outcome ("explained 3/3",
"surfaced 3/3", "stood down 3/3", "left unnarrated ✓") with the S3 evidence caveat
footnoted.

**8. What a board does with this** (short, numbers-only prose): three actions
(discount policy — €5.9M counterfactual give-away; Baltics cost-to-grow; the
Rheinkauf receivable, ~€2.4M above terms) and three stand-downs (January,
procurement, April). One paragraph on the honest misses and why they argue for
evaluation harnesses rather than trust.

**9. Reproducibility** (markdown): the pipeline commands in order
(generate → validate → variance analysis → storyteller runs → evaluate), seed 42,
byte-identical regeneration, where every file lives.

## Verification (builder must do all)

- Executes top-to-bottom clean via `jupyter nbconvert --to notebook --execute`
  (or papermill) on this machine; committed with outputs.
- All §E anchor asserts pass in-notebook.
- Chart rules hold (one axis, ≤3 identity hues, fixed assignment, legends, no text
  in series colours). Check every chart against the dataviz anti-patterns list.
- No answer-key read before section 7's marked cell; sections 1–6 use public CSVs
  (+ the declared §6(b) generator-side counterfactual, clearly labelled).
- Every quoted number traces to the CSVs, worksheet anchors, or report.md — nothing
  invented; run a final pass comparing notebook prose numbers against report.md.
