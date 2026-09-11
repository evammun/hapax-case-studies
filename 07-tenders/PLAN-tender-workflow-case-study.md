# Plan: Project 7 — Tender Workflow case study

Created: 11 September 2026
Status: **Phase 2 (corpus generation) complete.** Design gated and signed off
personally by Eva, 11 Sep 2026 ("perfect, go for it") — the first fully
Eva-gated design in the portfolio (Cases 2/3's Phase 1 gates were proxy-passed
by Luigi). Phase 2 deliverables: 16-tender requirement inventory + answer key,
the Visakoivu Oy facts library, 16 tender briefs, 64 persona attempt briefs
with seeded engagement, and a validator — all passing. Phases 3–6 (Arm A
attempts, Arm B pipeline, marking, writeup/interactive page) not started.

## Summary

Build the seventh case study of the portfolio ("The step up, measured",
cross-theme): the same 16-tender corpus is answered two ways — Arm A, 64
attempts by 14 simulated personas using a general chatbot ad hoc; Arm B, one
run per tender through an integrated workflow with the model inside deterministic
steps and gates — and both arms are marked against a single held-out answer
key. The deliverable is the difference between organisational choices, not a
model-capability claim, including where the naive arm honestly wins (prose
quality, speed on simple tenders). Full argument, scope, and pre-registered
expectations: `design/design.md`.

## Scope

- **In scope**: `Case Studies/07 Tenders/` (`design/`, `code/`, `data/{tenders,
  facts, answer_key, arm_a, arm_b, analysis, tender_briefs, attempt_briefs}/`,
  later `notebooks/`, `interactive/`, `writeup/`); deterministic corpus
  generation (requirement inventory, facts library, tender briefs, persona
  engagement) with a validator; Arm A persona attempts (prose agents, Phase 3);
  Arm B pipeline build and runs (Phase 4); mechanical marking against the
  answer key (Phase 5); writeup and interactive page (Phase 6).
- **Out of scope**: touching any other case study or the Website; real tender
  documents, real public buyers, real portal/authority names; API keys
  (portfolio decision, never); win rate, client persuasion, or real-world
  time claims (design.md S7 — not measurable here).

## House rules that bind every phase (portfolio precedent, Cases 2/3/5/6)

- **Nothing downstream is generated until Eva signs off the design doc.**
  Passed 11 Sep 2026 — a real gate, not a proxy.
- Deterministic Python controls STRUCTURE; LLM agents write only PROSE and
  may never add or remove a planted signal (requirement, trap, or engagement
  outcome) — the Hapax core generation pattern (root `CLAUDE.md`).
- Deterministic, seeded generation (`RANDOM_SEED = 7`, fresh for this
  project); all tunables in `code/config.py`; `pathlib` paths relative to
  script location; outputs only to specified output folders; never modify
  inputs.
- Coherence rules in the design doc are hard requirements, enforced by
  `code/validate_structure.py`, which exits 1 on any failure. A dataset that
  fails validation is a bug, not a judgment call.
- The answer key (`data/answer_key/`) is complete before any prose exists and
  stays out of the modelling path entirely — Arm A personas and Arm B's
  pipeline steps never see it; only `code/mark.py` (Phase 5) reads it.
- Persona cast tone: habits, never mockery — no persona is stupid, only
  unstructured (design.md S10 Q1, Eva-endorsed recommendation).
- Fictional names collision-checked before use — against real companies and
  against the six existing portfolio protagonist companies (Jalavakoski
  Konepaja Oy, Pyökkipaja Oy, Paju Consumer Products Oy, Saarnitukku Oy, 01
  Churn's roster, 04 Contracts' real CUAD parties). Full results in
  `design/DECISIONS.md`.
- Charts anywhere (interactive page) use the validated mark palette — wine
  `#A8352A`, indigo `#41529E`, gold `#B68A2C`, grey `#665E58` context-only,
  beige `#EFE5CE` fills, ink text; dataviz skill consulted before chart code.
- Voice and honesty rules: synthetic data declared prominently; numbers over
  adjectives; negative/frozen results stay in and are never retuned after
  the fact (design.md S7's closing line); no memory system — durable state
  lives in this folder's own docs.

## Phases

### Phase 1: Design → EVA GATE — PASSED 11 Sep 2026, Eva's own sign-off

**Goal**: a signed-off `design/design.md` settling the corpus shape, the two
arms, marking, and the pre-registered §7 expectations before any generation.

**Work**:
- [x] `design/design.md` written and gated. Status line records the sign-off
  ("perfect, go for it") and the four open-question resolutions: (1) persona
  tone = habits, never mockery; (2) sector kept as drafted (maintenance/
  installation/framework services); (3) full 16×4 scope kept, not trimmed to
  12×4; (4) Finnish-flavoured procurement conventions, no real portal/
  authority names.
- [x] `design/DECISIONS.md` seeded with the gate entry, seed choice, the
  engagement-model decision, and name collision-check results (this plan's
  Documentation section).

**Verification**:
- [x] **HARD STOP: Eva's sign-off before Phase 2** — passed 11 Sep 2026,
  personally, in her own words. No proxy.

### Phase 2: Corpus — deterministic structure

**Goal**: the requirement inventory, facts library, tender briefs, and
persona attempt briefs, all validated, before any prose exists.

**Work**:
- [x] `code/config.py` — every tunable: `RANDOM_SEED = 7`; the 16-tender size
  profile (4 simple ≈15 reqs / 8 medium ≈30 / 4 gnarly ≈50–60); the traps
  table exactly as design.md S3 (6 rows, exact counts); the 14 persona habit
  briefs (names + numeric traits); the 4-per-tender assignment scheme
  (`PERSONAS_WITH_FIVE`, 8 personas at 5 assignments, 6 at 4, 64 total); the
  Visakoivu Oy company-profile constants (certifications, staff, insurances,
  three years of financials, ten reference projects); the eligibility check
  functions shared by generation and validation; the requirement topic banks.
- [x] `code/generate_structure.py` — builds, in order: the requirement
  inventory per tender (`data/answer_key/requirements_NN.csv` + combined
  `answer_key.csv`); the facts library (`data/facts/company_facts.yaml` +
  rendered `.md`); tender briefs for the Phase 3/4 prose agents
  (`data/tender_briefs/brief_NN.json`); the 16×4 assignment matrix
  (`data/assignment_matrix.json`); and 64 persona attempt briefs with seeded
  engagement lists (`data/attempt_briefs/attempt_NN_PP.json`). Asserts
  facts-library eligibility consistency at generation time (§ below).
- [x] `code/validate_structure.py` — independently re-derives every
  coherence rule from the written files (never trusts generation's in-memory
  state): key completeness and gapless numbering; trap counts vs
  `config.TRAP_TABLE` exactly; eligibility consistency recomputed against
  `company_facts.yaml` on disk; tender briefs agree with the key; assignment
  matrix validity (16×4, 8×5+6×4=64, no persona twice on one tender);
  attempt-brief engagement lists reference only real requirement ids for
  their tender. Exits 1 on any failure.
- [x] Engagement-model calibration (documented in `code/config.py` and
  `design/DECISIONS.md`): the persona trait values drafted from the habit
  paragraphs alone produced ~31% median Arm-A coverage on first run — well
  under design.md S7's 55–80% band, because several multiplicative
  probability factors compound. Two population-level rescale passes (never
  per-attempt, never after seeing individual outcomes) brought the model to
  ~70.5% median coverage, 3 tenders with a best attempt ≥90%, and 2 of 8
  no-bid-tender attempts engaging with the eligibility trap — structurally
  plausible against every §7 Arm-A band without hard-coding any individual
  attempt's result.

**Verification**:
- [x] `python code/generate_structure.py` runs clean, prints per-tender
  progress and a diagnostic summary against §7's bands.
- [x] `python code/validate_structure.py` — **ALL CHECKS PASSED** (exit 0):
  key completeness, trap placement, eligibility consistency, tender-brief
  agreement, assignment-matrix validity, attempt-brief referential integrity.
- [x] Personal spot-check: company facts internally consistent by
  construction (max reference value 1,650,000 EUR < the T15 trap's
  2,000,000 EUR threshold; ISO27001 absent from `CERTIFICATIONS_HELD`,
  matching the T11 trap) and independently re-verified by the validator
  against the written YAML, not the generator's memory.

### Phase 3: Arm A — 64 persona attempts

**Goal**: for each of the 64 attempt briefs, a plausible chat transcript
(the persona's actual back-and-forth with a general chatbot, habits showing)
and the resulting tender response draft — Sonnet batches, ticket-writer
pattern (deterministic brief in, prose out, may not add or remove planted
signals or change engagement outcomes already fixed in Phase 2).

**Work**: not started.

### Phase 4: Arm B — the integrated workflow

**Goal**: one deterministic-pipeline run per tender (extract → draft →
coverage gate → facts check → sign-off artifact), per design.md S5.

**Work**:
- [x] Deterministic harness built (11 Sep 2026): `code/arm_b/FORMATS.md`
  (matrix/response/gate-report/signoff schemas), `code/arm_b/gates.py`
  (coverage, facts, consistency gates — no LLM calls, never reads the
  answer key), `code/arm_b/router.py` (terminal-state routing and
  `signoff.json`), `code/arm_b/RUNBOOK.md` (the run-agent protocol). Dry
  test (`code/arm_b/fixtures/` + `code/arm_b/test_gates.py`) proves all
  three gates against five designed outcomes — ALL CHECKS PASSED. Full
  writeup in `design/DECISIONS.md` ("Arm B harness built").
- [ ] The 16 actual runs (extraction + drafting by run-agents following
  `RUNBOOK.md`) — not started. `data/arm_b/` is still empty.

**Verification**:
- [x] `python code/arm_b/test_gates.py` — ALL CHECKS PASSED.
- [ ] 16/16 runs reach a terminal `signoff.json` (submitted, no-bid, or an
  honestly recorded `stuck`) — pending the runs themselves.

### Phase 5: Marking + `data/analysis/report.md`

**Goal**: mechanical marking of both arms against the answer key
(`code/mark.py`, the sole reader of the key besides the validator's
consistency checks), scored against every design.md S7 expectation, frozen
and published whether it passes or not.

**Work**: not started.

### Phase 6: Writeup, interactive page, packaging

**Goal**: the canonical long-form case study, the "super interactive" page
(design.md S8: workflow view, the seventy attempts, the scoreboard), case
page + work.html + shapes-page cross-link, `README.md`, DECISIONS entries
throughout.

**Work**: not started.

## Documentation

Deliverables, not afterthoughts: `design/design.md` (Phase 1);
`design/DECISIONS.md` (running, Phases 1–2 entries written); this plan file
(created at Phase 1, updated through completion); `data/analysis/report.md`
(Phase 5); `README.md` + root `CLAUDE.md` updates (Phase 1 start and Phase 6
close).

## Open questions

Design.md S10's four open questions were resolved at the gate (see Phase 1
above); none remain from Phase 1. Carried forward for later phases:

- Whether the Phase 3 prose agents get one pinned brief per persona or one
  shared brief parameterised by the persona/tender JSON (precedent: 01
  Churn's ticket-writer used one shared brief; leaning that way here too).
- Exact Arm B gate-bounce reporting granularity for the interactive page
  (design.md S8 wants to "show live" what bounced and why — needs a Phase 4
  decision on how much pipeline internals to expose).

## Risks

- **Engagement-model plausibility is a build-time judgement call**, not a
  provable guarantee — the two calibration passes in `code/config.py` are
  documented and reasoned, but they are still a choice of trait ranges made
  before any real Arm A prose exists. If Phase 3's actual persona drafts
  read as inconsistent with their engagement lists, that is a Phase 3
  prose-fidelity bug, not license to re-tune Phase 2's seeded structure
  after the fact.
- **510 requirements across 16 tenders is a large structural surface** for
  Phase 3/4 prose agents to dramatise faithfully without drift — the
  per-tender brief's `prose_agent_constraints` and per-trap
  `trap_placements` instructions carry the load; batch-by-batch validation
  (as in Cases 2/3/6) will matter more here than anywhere else in the
  portfolio so far.
- **The two no-bid mechanisms are deliberately subtle** (a missing
  certification; a reference-value band) — if Phase 3/4 prose agents
  surface them too visibly (e.g. narrating "this disqualifies us" in body
  text rather than leaving it for the reader/pipeline to find), the
  designed difficulty is defeated. `prose_agent_constraints` says not to
  flag traps in the tender text; the same discipline needs to extend to the
  Arm A/B response-drafting prompts in Phases 3–4.
- **16×4 is the content-heaviest build since Churn** (design.md S10 Q3) —
  Phase 3's 64 attempts and Phase 4's 16 runs are a lot of LLM-agent surface
  area; batches should stay sequential and validated one at a time, per
  ground rules.
