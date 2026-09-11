# 09 Training Outcomes — Decisions log

Running log, portfolio convention (07/08 precedent). Append, never rewrite.

## Phase 1 gate — 11 September 2026

Eva's sign-off, in her own words: "let's get to it!" on the case as a
whole, and "whatever you think best" on the four §8 open questions,
resolved to the written recommendations:

1. Keep the naive evaluation arm as the comparator (not just the honest
   instrument alone) — it is what every buyer has previously been shown,
   and its planted decomposition (selection, practice effect, self-report
   weighting) is the selling argument for measuring differently.
2. Cohort 40 with the archetype mix tabled in design.md §2, unchanged —
   including the 7 confident non-learners as deliberately the largest
   "problem" group.
3. The task-set forms (A and B) are published in full, not held back —
   checkability is the brand; the mitigation for a future client
   rehearsing them is that a real engagement generates fresh forms by the
   same published method.
4. Kuusiharju Oy as the invented company and "AI-Augmented Workflows" (the
   training page's own flagship theme) as the in-world programme, confirmed
   as fine.

Design.md §5's six pre-registered expectations were written before any
generation or run and are frozen — none may be retuned after Phase 5's
actual marking, whatever the result.

## Seed choice

`RANDOM_SEED = 9` — the next unused integer in the portfolio's per-project
seed sequence (01=none fixed pre-42 legacy, 02/03/05/06 used small
project-specific integers, 07=7, 08=8). No significance beyond
"unused and simple."

## Ability-to-rubric-band mapping (Phase 2 build decision)

The design doc asks for "a deterministic scoring rubric (what a response at
ability level x contains)" and instructs documenting the ability-to-band
mapping in code comments. The mapping chosen (see `code/config.py`,
`RUBRIC_BANDS` and `ability_to_band`):

- Ability and rubric-item difficulty share one 0–1 scale.
- Each task's rubric items carry an `item_difficulty` spread across that
  scale (roughly 0.15 to 0.85 within a task).
- A learner earns a rubric item iff `item_difficulty <= effective_ability`
  — a plain threshold rule, not a probabilistic one. This was chosen over a
  logistic/probabilistic hit function for one reason: it keeps the mapping
  from ability to points-earned exactly invertible and auditable by eye
  (useful for the interactive page's planned "each learner's response next
  to their planted truth" view, and for Phase 5's `mark.py`, which will
  need to explain a mark, not just produce one).
- The same `effective_ability` value is banded into one of four qualitative
  labels (minimal/partial/solid/excellent) purely for Phase 3's prose
  agents to target — the band is a writing instruction, not a scoring
  mechanism; `mark.py` will score against rubric items directly, never
  against the band label.
- `effective_ability` itself is drawn PER TASK (not once per whole form
  administration): `occasion_ability + practice_bonus (if applicable) +
  N(0, learner.assessment_noise)`, clipped to [0, 1]. Task-level noise was
  chosen over form-level noise because §2 of the design doc plants
  characteristic-mistake variety task by task, which a single flat
  per-form ability would flatten into identical bands across all ten tasks
  for a given learner-occasion — implausible and less useful for Phase 3
  dramatisation.

## δ/confidence independence — the tolerance band

Design.md's load-bearing claim is that confidence trajectories are drawn
INDEPENDENTLY of the planted true ability shift (δ). Implemented literally:
`confidence_delta_post` is a separate normal draw per learner, from its own
archetype-conditioned distribution, never a function of `delta_post` (see
`code/config.py`, the two are drawn from unrelated `(mean, sd)` pairs and
never combined in the same expression during generation).

Independence within an archetype does not mean zero correlation across the
whole cohort — two archetypes (strong and modest improvers) are
constructed to have both high δ and high confidence gain, and that
co-occurrence is itself an honest pattern, not a leak. What would defeat
the design is near-perfect tracking (r → 1), which would silently erase
the confident-non-learner and non-responder archetypes' reason for
existing. The chosen validation target is:

    0.20 <= r(delta_post, confidence_delta_post) <= 0.65   across all 40

Achieved at seed 9: **r = 0.322** — comfortably inside the band, with the
confident-non-learner archetype alone showing δ ≈ 0.03 against a mean
confidence gain of 1.63 (on the 1–7 scale), the intended decoupling.
Within-archetype correlations were also checked (not a hard pass/fail
threshold, `|r| <= 0.75` as a loose plausibility bound given some
archetypes have as few as n=3 or n=7 points) — all archetypes with n >= 7
came back well inside that bound.

## Practice-effect mechanism (naive arm's flaw #2)

The naive instrument's defining flaw is administering the SAME form to a
learner at both pre- and post-training occasions. The practice effect is
planted as a flat `PRACTICE_EFFECT_BONUS = 0.07` added to
`effective_ability` whenever a response brief is for a form the learner has
already seen at an earlier occasion (`is_repeat_form` in
`code/config.py`/`generate_structure.py`). Concretely: each learner is
assigned one "pre-form" (A or B, counterbalanced 20/20 across the cohort).
Every response brief for that same form at the `post` or `follow_up_8wk`
occasion carries the bonus; the OTHER form (first seen at `post`, used by
the honest instrument) never does. This makes the naive arm's post-score
systematically inflated relative to the honest instrument's post-score for
the same underlying learner and occasion — decomposable in Phase 5's
`mark.py` because both the "clean" and "practised" administrations exist
side by side in the 240 response briefs (40 learners × 2 forms × 3
occasions), even though the naive arm only ever reads its own repeated-form
half of that data.

## Response-brief structure decision

The design doc's phrase "per learner × form × occasion" was implemented
literally as a full cross product: 40 learners × 2 forms × 3 occasions =
240 individual brief files, each containing all 10 tasks of that form
scored for that learner at that occasion. This was preferred over
generating only the combinations each instrument actually uses (which
would have been closer to 120 briefs) because: (a) the validator can then
check brief completeness as one clean 240-count invariant rather than three
different instrument-shaped subsets, (b) the fast-forgetter blind spot
(design.md §6) needs the `follow_up_8wk` occasion to exist for every
learner even though no named instrument reads it, and (c) it keeps
generation and instrument-selection logic separated — `data/instruments/`
config files declare which slice of the 240 each instrument reads, and
that selection logic belongs to Phase 5's `mark.py`, not to generation.

## Name collision check — results

Checked against: the portfolio's eight fictional protagonist firms
(Jalavakoski Konepaja Oy / 02, Pyökkipaja Oy / 03, Paju Consumer Products
Oy / 05, Saarnitukku Oy / 06, Visakoivu Oy / 07, Tammilehto Oy / 08, and 01
Churn's Koivu Oy / Koivu Ventures Oy), 07 Tenders' 14 persona names, and 08
Inbox's customer register (person accounts). No overlap found — full and
independent name lists live in `code/config.py`
(`EXISTING_PORTFOLIO_FIRM_NAMES`, `EXISTING_PORTFOLIO_PERSON_NAMES`) and
the check is re-run independently by `code/validate_structure.py` against
the names actually written to `data/cohort/learners.csv`, not against the
generator's in-memory list. "Kuusiharju Oy" (spruce hill) does not collide
with any existing tree-convention name in the portfolio.

## Phase 3 closure — Task 3/4 cross-batch audit and Task-4 rubric tightening

Batch convention assumed for this audit (no batch-boundary file exists in
the corpus, so this is documented here as the working definition used by
every Phase 3 closure check): five batches of eight contiguous learners —
L01–L08, L09–L16, L17–L24, L25–L32, L33–L40.

**Task 3 (error-spotting, single planted error per form)**: scanned all 240
files for cross-form content contamination (form-A-specific figures — unit
price, the 14th/19th dates — appearing in a B3 response, or form-B-specific
figures — the 22nd/23rd, the site-visit crew — appearing in an A3 response).
Zero contamination found. The pre-existing rubric text (`config.py`,
`TASK_PAIRS` index 3) had bundled both forms' facts into one description
string separated by "/", which was a latent risk (confusing to a reader,
even though no batch actually misread it into the prose) rather than a
realised bug. Tightened anyway, on the same pass as Task 4 below, to name
each form's fact explicitly ("Form A: ... Form B: ...") instead of the
old "/"-separated aside.

**Task 4 (error-spotting, two planted errors per form)**: this is where a
real cross-batch divergence was found. The two planted errors trade
positions between forms — Form A's error sits in the on-time-rate figure
(stated 97%, actually ~95%) while its growth figure is clean (54→62, ~15%,
correct as stated); Form B's error sits in the growth figure (stated 20%,
actually ~23%) while its on-time-rate figure is clean (9/118, ~92%, correct
as stated). The old rubric text described item 2 by a fixed figure name
("the on-time-rate error") with a parenthetical aside for Form B, and
described item 1 only as "the first planted error... the real first error
is elsewhere — see below" — genuinely ambiguous about which figure item 1
and item 2 are meant to track once the form is B rather than A.

Audit method: extracted what each of the 240 files (120 on A4, 120 on B4)
engages with for items 1 and 2, and compared against each file's briefed
`rubric_items_hit`. Because the ability→band threshold rule makes hits a
strict prefix of item indices, files with `rubric_items_hit == [1]` (item 1
credited, item 2 not) are the clean test: does the text confidently state
the item-2-level correction it should NOT yet contain?

Result — **not fully consistent**. Form A resolved identically across all
five batches (34/34 `hits==[1]` files write only the clean delivery-growth
confirmation, correctly withholding the on-time-rate finding). Form B did
not:
- Batch 1 (5/5 `hits==[1]` files) and most of batches 3 and 5 correctly
  wrote item 1 as the clean on-time-rate confirmation, withholding the
  growth-percentage finding — the canonical resolution, symmetric with
  Form A.
- Batch 2 (9/9 files) and batch 3's outliers (L22, L23) substituted
  growth-topic content for item 1, but hedged ("looks a bit high to me,
  not totally sure", "roughly right") rather than stating the precise
  correction — a topic-choice divergence, not a factual contradiction with
  the brief (defensible under the item's own "a learner catching only one
  still earns this item" latitude). Not flagged for regeneration.
- Batch 4 (7/7 files) and one batch-5 outlier (L34) stated the item-2
  correction with full confidence and precision ("96 to 118 comes out at
  about 23%, not the stated 20%") despite the brief recording item 2 as
  NOT earned for these responses — a direct content/points contradiction,
  not a topic-choice judgement call. **Flagged for regeneration** (task B4
  only, within an otherwise sound response file): `L27_formB_follow_up_8wk`,
  `L27_formB_post`, `L27_formB_pre`, `L29_formB_follow_up_8wk`,
  `L29_formB_pre`, `L30_formB_pre`, `L31_formB_follow_up_8wk`,
  `L34_formB_pre`.

No equivalent bug found on item 3 (the "held steady" structural
contradiction, shared substance both forms) or on Task 3 — checked
separately across all 240 files with the same "content present but brief
says not-yet-earned" method: zero hits.

**Config tightened** (`code/config.py`, `TASK_PAIRS` indices 3 and 4): item
descriptions rewritten to name each form's fact explicitly by ROLE (Form
A/Form B stated separately) rather than a fixed figure name with an aside,
adopting the majority/canonical resolution above as the documented
standard. `code/generate_structure.py`'s `render_task_sets()` step was
re-run standalone (it runs before the seeded `rng` is touched and consumes
no randomness — verified by reading the function before running it) to
sync `data/task_sets/form_a.{md,yaml}` and `form_b.{md,yaml}` with the new
text; `data/cohort/`, `data/answer_key/`, `data/response_briefs/` and the
manifest are untouched (hash-verified before/after), since none of those
are derived from the rubric description text.

## Phase 3 closure — corpus validation, scorer calibration, final results

**`code/validate_responses.py`** — corpus-wide validation of all 240
response files against the manifest and their briefs. Five of six checks
**PASS** clean: manifest completeness (240/240, no orphans), schema, task-id
order, `self_report` byte-identity against the brief, and the banned-term
scan (a judgment-call list documented in the script's own comments — the
simulation's internal vocabulary: `rubric`, `archetype`, `effective_ability`,
`answer key`, `band label`, `characteristic mistake`, `practice effect`,
the archetype labels, the instrument names, a literal learner-id token, and
practice-effect self-awareness phrasing — with "planted error"/"planted
errors" deliberately EXCLUDED since both task prompts use that exact phrase
themselves). Zero hits on any of these across all 240 files.

The sixth check — the narrow rubric-fidelity check on the binary/enumerable
policy tasks A7/B7 and A8/B8, run per the spec ("one batch caught two
fidelity bugs this way on its own range; run it everywhere") — surfaces 92
candidate item-level disagreements. Building this check's detectors
(`code/rubric_detectors.py`) caught one genuine, fixable bug immediately: a
numbered-list parser that required the yes/no answer to sit directly after
the digit (`"1. No"`) missed the equally common `"1. Address — no"` /
`"1 - no"` label-and-dash variants entirely, which is exactly the shape of
fidelity bug the spec's precedent describes — fixed once, in the shared
detector, not per file. Beyond that fix, the remaining 92 candidates are
the same phenomenon documented in the calibration run below (a
paraphrase-recall ceiling on the same keyword detector), not newly
discovered response infidelities — the script prints an explicit
cross-reference note to that effect rather than asserting them as bugs.

**`code/score_responses.py`** — the full 10-task calibration run, comparing
`rubric_detectors.py`'s item detections against every response brief's
`rubric_items_hit` (a calibration exercise only; production scoring in
Phase 5's `mark.py` will never read the briefs). First pass: **74.80%**
item-level agreement (7,181/9,600). Iterated the detectors across eight
rounds, reading hand-inspected samples after every round (hundreds of
disagreements read in full, not sampled thinly) and broadening only
confirmed detector misses — never loosening a pattern to absorb a case
where the text genuinely didn't match its brief. Two lessons worth keeping
for Phase 5:

- A keyword net broadened to fix a visible false-negative can be a NET
  REGRESSION if it collapses two genuinely distinct items into the same
  trigger (Task 1's item 2 "unambiguous which line is which" pattern,
  broadened to also fire on item 1's mechanism keyword, was tried, measured
  a ~14-point regression on Tasks A1/B1 specifically, and was reverted with
  the trade-off documented directly in the code comment rather than
  silently discarded).
- Several close item pairs (Task 9 items 1/2, Task 6 items 2/3, Task 4-A
  items 1/2) show genuine BAND-BOUNDARY NOISE: near-identical sentences
  where one is briefed as earning the higher item and an almost-identical
  one is not, because the two effective-ability draws that produced them
  sit either side of a difficulty threshold. No keyword rule can separate
  these reliably; it is intrinsic to a continuous ability score passed
  through natural-language generation, not a scorer defect.

**Final calibration result: 9,038/9,600 = 94.15% overall item-level
agreement — BELOW the 97% target, reported honestly rather than tuned to
clear it.** Every task sits between 90.00% (B3) and 97.92% (B1); every
batch sits between 91.25% (batch 5) and 99.17% (batch 1) — batch 1 alone is
consistently the cleanest, batches 3–5 consistently the noisiest, which is
of a piece with the wider paraphrase divergence documented in the Task-3/4
audit above (later-batch writers drifted further from the earliest
batch's canonical phrasing). Of the 562 remaining disagreements, exactly 8
are the CONFIRMED genuine infidelities from the Task-4/B4 audit above (all
task B4, item 2, all in the eight flagged files); the rest are detector
recall/precision limits, evidenced by a stratified sample (up to 3 per
task, with the actual response text) written directly into
`data/analysis/scorer_calibration.md` so the classification is checkable,
not asserted. No further disagreement was reclassified as infidelity on
inspection beyond the already-known 8.

**Files flagged for regeneration (Phase 3, targeted, prose only — the
complete list, unchanged from the audit above)**: `L27_formB_follow_up_8wk`,
`L27_formB_post`, `L27_formB_pre`, `L29_formB_follow_up_8wk`,
`L29_formB_pre`, `L30_formB_pre`, `L31_formB_follow_up_8wk`,
`L34_formB_pre` — task B4 only within each otherwise-sound file. No other
files are flagged; the validator's 92 tasks-7/8 candidates and the
calibration run's other 554 disagreements were hand-sampled and attributed
to the detector, not the prose.

**Batch convention note**: no batch-boundary file exists anywhere in the
corpus; the 8-learner contiguous grouping (L01–L08 = batch 1, …, L33–L40 =
batch 5) is an assumption documented here and in `score_responses.py`,
inferred from 40 learners ÷ 5 parallel batch agents. If a future phase
discovers the true boundaries differed, the per-batch tables in
`scorer_calibration.md` and this entry should be read as approximate, not
authoritative, though the per-task and overall figures are unaffected.

## Phase 3 closure — targeted B4 regeneration (the 8 flagged files)

Cause: as recorded in the Task-3/4 cross-batch audit above, eight response
files' task-B4 answer confidently stated the item-2-level growth-percentage
correction ("96 to 118 comes out at about 23%, not the stated 20%" or a
close paraphrase) while each file's own brief credits only rubric item 1 —
a content/brief contradiction, batch-4-and-one-outlier's resolution of B4
diverging from the canonical (Form-B-clean-on-time-rate) resolution every
other batch used. Regenerated the B4 answer text ONLY, in each of:
`L27_formB_follow_up_8wk`, `L27_formB_post`, `L27_formB_pre`,
`L29_formB_follow_up_8wk`, `L29_formB_pre`, `L30_formB_pre`,
`L31_formB_follow_up_8wk`, `L34_formB_pre`. Source consulted: the
re-rendered `data/task_sets/form_b.{md,yaml}` (current authority on B4's
per-form error assignment and rubric-item wording), each file's own brief
(confirming `rubric_items_hit: [1]` for B4 throughout), each learner's
`data/cohort/L*.json` profile and their other in-file answers (for
register), and the existing B4 text being replaced. `data/answer_key/` was
not opened.

New text engages with the form's clean figure (the 9-late-of-118 / 92%
on-time rate) as real arithmetic — satisfying item 1 on its own canonical
terms — paired with a vague, unresolved unease about "the other
figure(s)"/"the increase" elsewhere in the note, deliberately never naming
96/118/20%/23% or the specific disagreement, and never invoking a source-
ledger check (item 4) or the "held steady" structural contradiction (item
3). Each learner's phrasing was matched to their own register elsewhere in
the same file (e.g. Toni Männistö/L34's hedged, first-person "I had a quick
look... I didn't get time to properly dig into it" versus Riitta
Ollikainen/L29's more analytic "I'd flag it before anything goes further
rather than take it at face value"). No other answer, `self_report`, or
metadata field was touched in any of the 8 files.

Verification: `python code/rubric_detectors.py`'s `detect("B4", text)` run
directly against all 8 new texts returns exactly `{1}` for each — matching
their briefs precisely, no item 2/3/4 false credit. `python
code/score_responses.py` (the full calibration run) now shows a `scorer_
calibration.md` "Genuine infidelities" table with zero rows (previously the
8 confirmed B4/item-2 contradictions listed above); overall item-level
agreement moved from 94.15% to 94.23% (9,046/9,600), task B4 alone at
96.88% (465/480) — still below the 97% target on remaining detector
recall/precision limits (unrelated paraphrase, documented in the same
report), not on any further content/brief contradiction. `python
code/validate_responses.py` was also re-run: its tasks-7/8 fidelity check
is unaffected (B4 is outside that check's scope) and its pre-existing 92
candidates are unchanged. SHA-256 hashes of all 240 `data/responses/*.json`
files were taken before and after the edit: exactly the 8 files above
differ; the other 232 are byte-identical.

## Phase 5 — instrument runs and marking (`code/run_instruments.py`, `code/mark.py`)

**Build decisions, frozen before this run's numbers were seen:**

- **Administrative data source.** `run_instruments.py` (and the shared
  `code/instrument_scoring.py`) reads `pre_form`/`post_form`/`volunteer`
  from `data/cohort/learners.csv` — never `data/answer_key/`. Those three
  fields are logistics (which form a learner sat, whether they volunteered
  for the naive arm), not planted truth about learning (delta_post,
  ability_*, confidence_*), which stay exclusive to `code/mark.py` per
  design.md S4 ("mark.py, sole reader of the key"). `learners.csv` also
  carries the planted-truth columns, but `instrument_scoring.load_admin()`
  reads and returns only the three administrative fields, so no caller of
  it can accidentally see the rest.
- **Scoring the "scored" layer.** Every task-performance number in the
  primary pass comes from `rubric_detectors.detect()` run against response
  TEXT in `data/responses/`, exactly the calibrated Phase-3 scorer (94.23%
  item-level agreement, `data/analysis/scorer_calibration.md`) — never the
  response briefs' own `points_earned`. The response briefs are read only
  for the robustness/"perfect" pass, a deliberate second use of the
  precedent already set by `score_responses.py`'s calibration run (briefs
  are not "the answer key" in design.md's sense; only `data/answer_key/`
  is).
- **Confidence-gain scaling for blending.** The 1–7 confidence scale is
  rescaled to a 0–1-ish unit by dividing by 6 (its full width) before
  blending with the 0–1 rubric-point-fraction performance delta in the
  naive arm's `blended_effect = (1 - w)*performance_delta +
  w*confidence_delta_scaled`. This is a Phase-5 build choice (not specified
  numerically in config.py beyond `self_report_weight`), documented here
  rather than buried in a code comment only.
- **Confident-non-learner detection rule.** A single statistic,
  `divergence_z = z(confidence_delta_scaled) - z(delta_hat)`, z-scored
  across the honest instrument's own 40 measured values (never against a
  known count of planted archetypes), flagged at `divergence_z > 1.0`
  (one cohort standard deviation). Chosen and frozen before running: it is
  a plain, principled statistical threshold a real deployer could set
  without knowing how many confident non-learners exist in advance — not
  "flag exactly the top 7," which would bake the answer key's own
  archetype count into the detector.
- **Expectation 1's sigma.** The planted cohort delta's own sample standard
  deviation (`statistics.stdev`, n=40, ddof=1) across all 40 learners —
  the natural dispersion unit for "the cohort mean effect," read only by
  `mark.py`.
- **Naive-arm decomposition method.** Three independent one-flaw-off
  counterfactuals (full cohort instead of volunteers; counterbalanced forms
  instead of repeated; self-report weight 0 instead of 0.5), each toggling
  exactly one flaw and holding the other two at the naive arm's actual
  settings, reusing the identical `run_instruments.run_naive` /
  `instrument_scoring.compute_pre_post_effect` code path so there is no
  second, drifted scoring implementation. Each flaw's "share" =
  `naive_effect - counterfactual_effect`; shares are NOT forced to sum to
  the total overstatement — the residual is reported explicitly as the
  flaws' interaction rather than absorbed into any one flaw's number.
- **Fast-forgetter demonstration thresholds.** "Blind at post" =
  |fast-forgetter mean delta-hat − genuine-improver mean delta-hat| ≤ 1.0 ×
  the genuine-improvers' own sample sd. "Visible decay at +8wk" =
  fast-forgetters' 8-week/post delta-hat ratio ≤ 0.60. Both frozen before
  running, both computed via the same `compute_pre_post_effect` function
  used everywhere else, just pointed at `post_occasion="follow_up_8wk"`
  instead of `"post"`.
- **Robustness pass.** Every one of the six verdicts is computed twice:
  once with `mode="scored"` (primary, the realistic noisy layer) and once
  with `mode="perfect"` (the response briefs' own intended points, a
  perfectly-reliable-rater sensitivity check). The feedback sheet is
  identical between the two passes by construction — it never scores
  response text — and is included in the robustness table for
  completeness, not because it could plausibly flip.

**Results (2026-09-11 run, seed 9 corpus, unchanged since Phase 3 closure):**

The six pre-registered verdicts (primary, scored-text pass):

1. Cohort mean effect within ±0.10σ — **MET**. Planted mean delta 0.1338,
   measured delta-hat 0.1437, gap 0.0100, tolerance ±0.0124.
2. Flags ≥6/7 confident non-learners — **MET**. Caught 6/7 (L01, L03, L09,
   L12, L23, L31); missed L30; 2 false positives (L11, L15).
3. Feedback sheet r < 0.30 vs planted delta — **MET**. r(confidence_post,
   delta) = 0.101; r(satisfaction_post, delta) = 0.056.
4. Naive overstates cohort effect by ≥50% — **NOT MET**. Measured
   overstatement 41.3% (naive effect 0.1890 vs planted full-cohort mean
   0.1338). Frozen, not retuned, per design.md's explicit instruction that
   any failed expectation stays published as a failure.
5. Form equivalence within tolerance — **NOT MET**. Mean pre-score Form A
   0.4400 (n=20) vs Form B 0.3688 (n=20), diff 0.0713 against a ±0.05
   tolerance. Per design.md S5.5, this is reported as "a frozen finding
   about how hard equivalent forms are to write," not adjusted after the
   fact — Forms A and B's task-pair item-difficulty spreads were matched at
   design time (Phase 2's `FORM_DIFFICULTY_TOLERANCE` check on structural
   item difficulty passed), but the REALISED scored difficulty diverged
   once run through prose generation and noisy scoring.
6. Designed blind spot demonstrated — **MET**. At post, fast forgetters'
   mean delta-hat (0.2667) sits within 1σ of genuine improvers' (0.2150,
   sd 0.1204) — indistinguishable as designed. At +8 weeks, fast forgetters
   retain 21.9% of their post gain against 87.8% for genuine improvers — a
   decisive, visible gap the standard instrument (as sold) never sees.

Naive-arm decomposition (primary pass; total overstatement 41.3% /
+0.0552 absolute): selection bias +24.1% of the overstatement, practice
effect +42.8%, self-report weighting **−57.9%** (self-report weighting
actually PULLS the naive estimate DOWN, not up — the repeated-form
performance delta is already inflated by the flat practice-effect bonus
propagating through several rubric-band thresholds at once, while the
confidence gain scaled to the same units is comparatively modest; blending
the two dilutes the number). Residual/interaction: 90.9% of the total —
large, meaning the three flaws do not act independently and the individual
shares should be read as marginal effects, not a clean partition. This
inversion was not anticipated at build time and is reported exactly as
computed, per the no-retuning rule.

**Robustness table — two of six verdicts flip between the scored-text
primary pass and the perfect-scoring sensitivity pass:**

- Expectation 1 flips MET → NOT MET (perfect-scoring gap 0.0212 exceeds the
  ±0.0124 tolerance; primary-pass gap 0.0100 was inside it).
- Expectation 4 flips NOT MET → MET (perfect-scoring overstatement 57.5%
  clears the 50% bar; primary-pass 41.3% did not).
- Expectations 2, 3, 5, 6 do not flip.

This is reported as the headline finding the design didn't anticipate but
the scorer calibration made checkable: the primary pass's 94.23%-reliable
scorer is not just "close enough noise" — it is close enough to change
whether two of six pre-registered verdicts pass, in both directions (one
verdict looks better than it should, one looks worse). Neither pass is
privileged as "the real answer" in the writeup; both are published with
the gap between them as the actual finding about what a 94%-reliable rater
costs a marking programme.

No numbers above were adjusted after computation. `code/mark.py` and
`code/run_instruments.py` were run in that order; `marks.json` was
confirmed byte-identical across a second full run of the pipeline before
this entry was written.

## Phase 6 — canonical writeup drafted (11 September 2026)

`writeup/training_outcomes_case_study.md` written in the main loop by the
Opus writer per the standing instruction, with 07 Tenders’ writeup as the
register and provenance-header precedent. Canonical: the website case page,
the interactive page and any training material derive from this file rather
than from `data/analysis/report.md` directly. **Eva’s read-through is
pending.**

Editorial decisions taken in drafting, recorded because they shape every
downstream derivative:

- **Title and disclaimer.** "Forty learners, three instruments", with the
  simulated-cohort disclaimer carrying both loads design.md S6 requires: the
  cohort is invented, AND what is measured is the ruler rather than the
  training. The sentence "nothing here is evidence that training works" sits
  in the disclaimer itself, above the first section.
- **Every figure is taken from `data/analysis/report.md` / `marks.json`**,
  which are treated as the sole authority. The perfect-scoring pass’s two
  numbers not printed in report.md’s tables (expectation 1’s gap 0.0212 and
  expectation 4’s 57.5% overstatement) are quoted from this log’s Phase 5
  entry and were re-verified against `marks.json`
  (`perfect_scoring_robustness_pass.expectations`) before use. No
  discrepancy was found between the drafting brief, report.md and marks.json
  on any figure.
- **Structure.** Why the case exists (the 3% training-route conversion from
  the 80-lead outreach analysis) → the cohort and its planted independence
  (r = 0.322) → the three instruments, with tasks A9 and A4 quoted so the
  reader can see the instrument is real → the six verdicts, failures printed
  in the same table as the passes → the robustness pass as the headline,
  told last and flat → the fast-forgetter blind spot → marking quality →
  what transfers.
- **Two additions beyond report.md’s own tables**, both verifiable in
  `marks.json`: expectation 5’s form gap WIDENS to 0.0900 under perfect
  scoring (so the form-equivalence failure is not a scorer artefact), and
  expectation 2 catches 7/7 rather than 6/7 under perfect scoring with L28
  replacing L15 among the two false positives (composition changes, verdict
  does not).
- **Texture quoted from the corpus**, not paraphrased: L23 (Tiina Räsänen)
  pre/post answers to the verification-habit task plus her "Same as before
  really" opener, against her confidence rise 3.09 → 4.70 and satisfaction
  4.95; L22 (Markus Hirvonen) task A1 at post versus +8 weeks, as the rust.
- **Voice.** One dry remark in the document, in the robustness section (the
  feedback sheet cannot flip because it never reads an answer — immunity to
  rater error bought by measuring nothing); it carries the information that
  self-report instruments are unfalsifiable by a marker, so it earns its
  place. No pricing anywhere, per portfolio convention.

Nothing outside `writeup/` was modified by this pass; no website file was
touched.

## Phase 6 — interactive page built (11 September 2026)

`interactive/build_data.py` + `interactive/_template.html` -> `interactive/
training-outcomes.html`, following 07 Tenders' build pattern exactly (a
deterministic Python assembly step writes one JSON blob to `_data.json` and
inlines it into a hand-written template's `<script type="application/json"
id="hpx-data">`). No number on the page is invented: every figure traces to
`data/analysis/marks.json` (`code/mark.py`'s sole output), `data/cohort/
L*.json`, `data/responses/`, or `code/config.py`; every callout sentence is
sliced verbatim out of `writeup/training_outcomes_case_study.md` by a
`quote_paragraph()` helper that finds an ASCII anchor and returns the whole
blank-line-delimited markdown paragraph containing it — chosen over
hand-typing quoted spans specifically so this script never has to retype a
curly quote, en dash or minus sign (the writeup's typographic apostrophes,
"–" and the literal "−0.025" in the L23 exhibit all ride along in the slice
untouched). 29 quotes extracted this way; all 29 verified present on the
page and re-extracted independently by the QA gate below.

**Three views, matching design.md §7 exactly, no fourth added:**

1. **The cohort.** The seven confident non-learners as a centrepiece gallery
   (planted δ, δ̂, confidence gain, caught/missed chip per learner), L23
   (Tiina Räsänen) pulled out as its own exhibit box quoting the writeup's
   "Same as before really" paragraph verbatim. Below it, all 40 learners
   browsable (filter by archetype/role), archetype revealed on every card
   per design.md's own instruction that this page IS the marked result.
   Selecting a learner shows their planted profile, all three instruments'
   verdicts on them, and three illustrative tasks (indices 1, 4, 9 — chosen
   because the canonical writeup itself quotes exactly these three exhibits,
   not an arbitrary pick) with pre/post responses side by side (pre/post/+8
   weeks for the three fast forgetters), each occasion's own prompt shown
   above its own response since pre and post can be different forms. A
   "full responses in data/responses/" note closes each learner's detail.
2. **The instruments.** The six-verdict table (scored pass) with the two
   NOT MET rows styled identically to the four MET rows, no visual
   demotion. Two direct-labelled scatters (no legend): the honest
   instrument's δ̂ hugging the y=x diagonal in indigo, the feedback sheet's
   confidence-vs-planted-δ cloud in wine with r=0.101 stated directly. The
   naive arm's decomposition as a diverging bar (selection/practice-effect/
   self-report-weighting shares, the negative −57.9% self-report share
   drawn left of centre in wine, the residual 90.9% shown as a distinct
   hatched gold bar rather than folded into the other three, matching
   design.md's "shown, not smoothed" instruction). The fast-forgetter
   retention chart: paired post/+8wk bars per forgetter against genuine-
   improver reference lines, 21.9% vs 87.8% retention stated directly.
3. **The robustness flip.** Six rows, scored-pass and perfect-scoring
   verdict chips side by side, a gold "→" arrow on exactly the two rows
   that flip (expectations 1 and 4), numbers re-checkable under each chip.
   Expectation 3 (the feedback sheet) pulled into its own box below the
   table with the writeup's dry remark ("immunity to rater error bought by
   measuring nothing") quoted beside it, since it is the one row that
   cannot move — never reads an answer, so no scorer can be wrong about it.

**Page size**: 142.3 KB (well under the 2 MB budget) — `_data.json` alone is
99.3 KB, almost entirely the 40 learners' illustrative task responses (three
of ten tasks per learner per occasion, not the full ten, per design.md's own
"pick 2-3 illustrative tasks" instruction).

**QA**: `code/verify_interactive_09.py`, modelled on `code/
verify_interactive_07.py` and trimmed to this project's shape (no in-browser
game here, so no JS-vs-Python agreement check is needed) — single external
request (Google Fonts only), `hpx-` prefix discipline, balanced tags, page
size, embedded-JSON parity with `_data.json`, every headline number and the
full cohort array re-checked against `data/analysis/marks.json` directly
(not against `_data.json`, which is itself downstream and could in
principle drift from marks.json on a build_data.py bug), all 28 writeup
quotes independently re-extracted from the writeup with the QA script's own
copy of `quote_paragraph()` (not imported from `build_data.py`, so a
divergence between the two is visible rather than silently sharing one
failure point) and checked both for verbatim match and for presence on the
page, and a page-wide scan for browser-storage APIs and network calls
(`localStorage`, `sessionStorage`, `indexedDB`, `document.cookie`, `fetch`,
`XMLHttpRequest`, `WebSocket`, `sendBeacon` — none present). **All checks
pass.**

Beyond the static QA gate, the page was also run under `jsdom` (Node,
installed to a scratch prefix outside the repo) with real click/change
event dispatch across all three views, a learner-detail render (including a
fast forgetter's +8-week column and the correct 9 occasion columns for 3
tasks × 3 occasions), and the archetype filter — zero runtime errors. One
real (if minor) bug this caught: `Element.scrollIntoView` was called
unguarded on the gallery-card click handler; jsdom doesn't implement it,
which is a jsdom limitation rather than a real-browser one, but the call
was still wrapped in a `typeof` feature-check before shipping, consistent
with the portfolio's "graceful errors, never crash bare" rule extending to
client-side JS as much as to Python. The live claude-in-chrome browser tool
was unavailable in this environment (extension not connected), so this
jsdom pass is the closest available substitute for an actual browser
smoke-test and was run in addition to, not instead of, the static QA gate.

**Nothing from design.md §7 was left out.** The one thing not built here
(out of scope for this pass, per Eva's brief): the case page, `work.html`
and any training-page cross-link are §7's other listed deliverables and
remain open, per the portfolio's standing pattern of the interactive page
landing before the surrounding site plumbing. Eva's look-and-feel pass on
this page itself is also still owed, per precedent on every prior case's
interactive page. Nothing outside `interactive/` and `code/
verify_interactive_09.py` was touched by this pass; no Website file was
modified.
