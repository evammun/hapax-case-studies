# Plan: Project 9 — Training Outcomes case study

Created: 11 September 2026
Status: **Phase 1 → EVA GATE — PASSED 11 Sep 2026** (Eva's own sign-off,
recommendations adopted: (1) keep the naive evaluation arm as comparator;
(2) cohort 40 with the tabled archetype mix; (3) publish the task-set forms
in full; (4) Kuusiharju Oy / AI-Augmented Workflows as the in-world
programme). **Phase 2 (deterministic structure) complete.** Deliverables:
cohort of 40 learners with archetypes/δ/confidence trajectories, Forms A/B
(10 tasks each, published), the complete answer key, 240 response briefs
(40 learners × 2 forms × 3 occasions), three instrument definitions, and a
validator — all passing. **Phase 3 (prose responses) closed.** 240 response
files written by five batch agents; `code/validate_responses.py` passes
manifest/schema/order/self-report/banned-term checks clean; the Task-3/4
cross-batch audit found and fixed a real rubric-mapping ambiguity in
`config.py` (Task 4/Form B) and flagged 8 files for prose regeneration
(`L27_formB_*`, `L29_formB_pre`/`follow_up_8wk`, `L30_formB_pre`,
`L31_formB_follow_up_8wk`, `L34_formB_pre` — task B4 only); `code/
rubric_detectors.py` + `code/score_responses.py` calibrate the eventual
Phase 5 scorer at 94.15% item-level agreement against the briefs (below the
97% target, reported honestly — see `design/DECISIONS.md` and `data/
analysis/scorer_calibration.md`). The 8 flagged files are NOT yet
regenerated (out of scope for this closure pass). **Phase 5 (marking)
complete** (11 Sep 2026): `code/run_instruments.py` + `code/mark.py` +
`code/instrument_scoring.py` built and run; six pre-registered verdicts
computed (4 MET: recovery, confident-non-learner detection, feedback-sheet
uninformativeness, fast-forgetter blind spot; 2 NOT MET: naive overstatement
fell short of 50% at 41.3%, form equivalence failed at 0.0713 vs ±0.05
tolerance — both frozen and published as failures, not retuned); naive-arm
overstatement decomposed into its three flaws plus a large interaction
residual; a robustness table (not anticipated in the design) flips two of
the six verdicts between the scored-text primary pass and a perfect-scoring
sensitivity pass. Full numbers in `data/analysis/report.md` and
`design/DECISIONS.md`. Phase 6 (writeup, interactive page) not started.

## Summary

Build the ninth case study of the portfolio ("The ruler, tested"): a
simulated 40-learner cohort at the invented Kuusiharju Oy sits a two-day
"AI-Augmented Workflows" programme, and three measurement instruments — the
honest pre/post instrument Hapax will actually sell, an industry-standard
feedback sheet, and a deliberately naive evaluation assembled from real-world
bad practice — are run against the same cohort and marked against a held-out
answer key of each learner's planted true ability shift. The claim under test
is not "training works" but "the instrument's accuracy is published,
including what it cannot see" (the fast-forgetter blind spot, named in
advance). Full argument, scope, and pre-registered expectations:
`design/design.md`.

## Scope

- **In scope**: `Case Studies/09 Training Outcomes/` (`design/`, `code/`,
  `data/{cohort, task_sets, answer_key, response_briefs, instruments,
  analysis}`, later `writeup/`, `interactive/`); deterministic corpus
  generation (cohort profiles, task-set forms, response briefs, instrument
  configs) with a validator; prose responses (Phase 3); marking (Phase 5);
  writeup and interactive page (Phase 6).
- **Out of scope**: touching any other case study or the Website; a real
  training engagement or real learner data (design.md §6 — the cohort is
  declared simulated on the page); API keys (portfolio decision, never).

## House rules that bind every phase (portfolio precedent, Cases 2/3/5/6/7/8)

- **Nothing downstream is generated until Eva signs off the design doc.**
  Passed 11 Sep 2026.
- Deterministic Python controls STRUCTURE; LLM agents write only PROSE and
  may never add or remove a planted signal (archetype, δ, confidence
  trajectory value, rubric-band assignment) — the Hapax core generation
  pattern (root `CLAUDE.md`).
- Deterministic, seeded generation (`RANDOM_SEED = 9`, fresh for this
  project); all tunables in `code/config.py`; `pathlib` paths relative to
  script location; outputs only to specified output folders; never modify
  inputs.
- Coherence rules in the design doc are hard requirements, enforced by
  `code/validate_structure.py`, which exits 1 on any failure. A dataset that
  fails validation is a bug, not a judgment call.
- The answer key (`data/answer_key/`) is complete before any prose exists and
  stays out of the modelling path entirely — response-generating prose
  agents and the instrument scoring never see it; only `code/mark.py`
  (Phase 5, not built yet) reads it.
- Fictional names collision-checked before use — against real companies and
  against the portfolio's existing protagonist firms (Jalavakoski Konepaja
  Oy, Pyökkipaja Oy, Paju Consumer Products Oy, Saarnitukku Oy, Visakoivu Oy,
  Tammilehto Oy, 01 Churn's Koivu Oy / Koivu Ventures Oy) and named people
  (07's 14 personas, 08's customer roster). Full results in
  `design/DECISIONS.md`.
- Charts anywhere (interactive page) use the validated mark palette — wine
  `#A8352A`, indigo `#41529E`, gold `#B68A2C`, grey `#665E58` context-only,
  beige `#EFE5CE` fills, ink text; dataviz skill consulted before chart code.
- Voice and honesty rules: synthetic data declared prominently; numbers over
  adjectives; negative/frozen results stay in and are never retuned after
  the fact; no memory system — durable state lives in this folder's own
  docs.

## Phases

### Phase 1: Design → EVA GATE — PASSED 11 Sep 2026, Eva's own sign-off

**Goal**: a signed-off `design/design.md` settling the cohort, the three
instruments, marking, and the pre-registered §5 expectations before any
generation.

**Work**:
- [x] `design/design.md` written and gated. Status line records the sign-off
  and the four open-question resolutions (§8 in the doc): (1) keep the naive
  arm; (2) cohort 40 as tabled; (3) publish the forms in full; (4) Kuusiharju
  Oy / AI-Augmented Workflows confirmed.
- [x] `design/DECISIONS.md` seeded with the gate entry, seed choice, the
  ability→rubric-band mapping decision, and the practice-effect mechanism.

**Verification**:
- [x] **HARD STOP: Eva's sign-off before Phase 2** — passed 11 Sep 2026,
  personally, in her own words. No proxy.

### Phase 2: Corpus — deterministic structure

**Goal**: the cohort, the task-set forms, the answer key, the response
briefs, and the three instrument definitions, all validated, before any
prose exists.

**Work**:
- [x] `code/config.py` — every tunable: `RANDOM_SEED = 9`; the 40-learner
  archetype table exactly as design.md §2 (8/12/7/7/3/3); per-learner role,
  baseline ability, planted δ, confidence-trajectory parameters (drawn
  independently of δ), assessment noise, volunteering propensity; Kuusiharju
  Oy constants; the Finnish learner-name pool, collision-checked at import
  time against the portfolio exclusion list.
- [x] `code/generate_structure.py` — builds, in order: Forms A and B
  (`data/task_sets/form_a.md`, `form_b.md`, `.yaml`); the cohort
  (`data/cohort/learners.csv` + per-learner JSON); the answer key
  (`data/answer_key/answer_key.csv` + `.json`); 240 response briefs
  (`data/response_briefs/`, 40 learners × 2 forms × 3 occasions); the three
  instrument definitions (`data/instruments/`).
- [x] `code/validate_structure.py` — archetype counts; δ/confidence
  independence (cohort-wide correlation within the documented tolerance
  band); form difficulty balance; brief completeness (40 × 2 × 3 = 240); key
  completeness; name collisions. Exits 1 on any failure.

**Verification**:
- [x] `python code/generate_structure.py` runs clean, prints per-stage
  progress.
- [x] `python code/validate_structure.py` — **ALL CHECKS PASSED** (exit 0).

### Phase 3: Prose responses

**Goal**: for each of the 240 response briefs, plausible task-response prose
at the brief's fixed quality band (ticket-writer pattern: deterministic
brief in, prose out, may not change the band, rubric hits, or self-report
numbers already fixed in Phase 2).

**Work**: [x] 240 response files written (five batch agents, `data/
responses/`). [x] `code/validate_responses.py` — manifest, schema, task-id
order, self-report identity, banned-term scan all pass; the narrow A7/B7/
A8/B8 rubric-fidelity check surfaces candidates cross-referenced against
the calibration run below rather than asserted as bugs on its own. [x]
Task-3/4 cross-batch audit (`design/DECISIONS.md`) — Task 3 consistent
across all batches; Task 4/Form B had a genuine minority-batch divergence,
resolved by tightening `config.py`'s item mapping and flagging 8 files
(task B4 only) for prose regeneration. [x] `code/rubric_detectors.py` +
`code/score_responses.py` — the Phase 5 scorer's calibration harness,
94.15% item-level agreement against the briefs (`data/analysis/
scorer_calibration.md`). [ ] The 8 flagged files' B4 answers are not yet
regenerated — carried forward, not blocking Phase 5's build (mark.py can
be written and tested against the other 232 files' B4 answers plus the 8
flagged ones' other 9 tasks, all unaffected).

### Phase 4: (reserved — this case has no second pipeline arm; the three
instruments all score the same Phase 3 response text, so Phase 4 is folded
into Phase 5's marking step)

### Phase 5: Marking + `data/analysis/report.md`

**Goal**: `code/mark.py` (sole reader of the answer key besides the
validator's consistency checks) applies each instrument's rubric/selection/
weighting rules to the Phase 3 response text and scores the result against
every design.md §5 expectation, frozen and published whether it passes or
not.

**Work**: [x] `code/instrument_scoring.py` — shared administration/scoring
library (the "scored" text-detector layer and the "perfect" brief-intended-
score layer behind one interface). [x] `code/run_instruments.py` — the
three named instrument runs (honest, feedback sheet, naive) over the scored
layer, reading only `data/cohort/learners.csv`'s administrative fields
(never the answer key); outputs to `data/analysis/instrument_runs/`. [x]
`code/mark.py` — sole reader of `data/answer_key/`; the six verdicts, the
naive-arm three-flaw decomposition, the fast-forgetter +8-week
demonstration, and the perfect-scoring robustness pass; writes
`data/analysis/report.md` and `data/analysis/marks.json`. [x] Determinism
verified: a second full pipeline run (`run_instruments.py` then `mark.py`)
reproduced a byte-identical `marks.json`.

**Verification**:
- [x] `python code/run_instruments.py` runs clean, writes
  `data/analysis/instrument_runs/{honest,feedback_sheet,naive,manifest}.json`.
- [x] `python code/mark.py` runs clean, writes `data/analysis/report.md` and
  `data/analysis/marks.json`; re-run confirmed byte-identical.
- [x] All six design.md S5 expectations computed and frozen (4 MET, 2 NOT
  MET, none retuned); robustness table computed (2 of 6 verdicts flip
  between scored and perfect-scoring passes).

### Phase 6: Writeup, interactive page, packaging

**Goal**: the canonical long-form case study (Opus writer per standing
instruction), the interactive page (browse the cohort, the confident-
non-learner gallery, the three-instrument scoreboard), case page + work.html
+ training-page cross-link, `README.md`, DECISIONS entries throughout.

**Work**: not started.

## Documentation

Deliverables, not afterthoughts: `design/design.md` (Phase 1);
`design/DECISIONS.md` (running, Phases 1–2 entries written); this plan file
(created at Phase 1, updated through completion); `data/analysis/report.md`
(Phase 5); `README.md` + root `CLAUDE.md` updates (Phase 1 start and Phase 6
close).

## Open questions

Design.md §8's four open questions were resolved at the gate (see Phase 1
above); none remain from Phase 1. Carried forward for later phases:

- Whether the Phase 3 prose agent gets one pinned brief per learner or one
  shared brief parameterised by the learner/task JSON (precedent: 07's Arm A
  used one shared brief; leaning that way here too).
- Exact reporting granularity for the fast-forgetter blind spot on the
  interactive page (design.md §6 wants the instrument's limit stated
  plainly, not buried).

## Risks

- **The δ/confidence independence figure is a build-time judgement call**,
  not a provable guarantee — the tolerance band is documented and reasoned
  in `design/DECISIONS.md`, but it is still a choice of distribution
  parameters made before any real Phase 3 prose exists.
- **240 response briefs is a lot of structural surface** for Phase 3 prose
  agents to dramatise faithfully without drift — batch-by-batch validation
  (as in Cases 2/3/6/7) will matter here too.
- **The naive arm's three flaws (selection, practice effect, self-report
  weighting) must survive Phase 3 prose intact** — a prose agent that writes
  suspiciously self-aware responses ("I remember this from the pre-test")
  would surface the practice effect too visibly; the response-brief
  constraints need to carry this discipline into Phase 3.
