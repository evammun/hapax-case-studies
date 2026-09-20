# Plan: Project 8 — Inbox Automation case study

Created: 11 September 2026
Status: **Phase 6 complete (20 Sep 2026).** Phases 1-2 done 11 Sep 2026; Phase 3
prose 20 Sep; Phases 4-6 (pipeline, run, marking + writeup) completed 20 Sep 2026.

## Summary

Build the eighth case study of the portfolio ("Straight through, safely", Theme 3-adjacent
automation depth): a full straight-through-processing pipeline for inbound customer email
at Tammilehto Oy, an invented Oulu equipment-rental firm. Where 07 Tenders measured the
step from individuals to an assisted workflow, 08 measures the step beyond that — the
pipeline answers customer email end-to-end with no human in the loop, humans appearing
only where the pipeline deliberately routes an exception to them. The claim under test:
automation earns its keep not by answering everything, but by knowing what NOT to
auto-send. End state: a self-contained interactive HTML page (the inbox browser, the
River flow visualisation, the scoreboard), a marking pass against a held-out answer key,
and a long-form writeup.

## Scope

- **In scope**: new project folder `Case Studies/08 Inbox/` (`design/`, `code/`, `data/`
  with `policy/`, `customers/`, `threads/`, `email_briefs/`, `answer_key/`, `pipeline/`,
  `analysis/` subfolders); Phase 2 deterministic structure (policy handbook, customer
  register, thread skeletons, email briefs, answer key) with a validator; later phases
  add LLM prose for emails and staff replies, the pipeline (classify → retrieve → draft →
  gates → router), the run, marking, and the writeup.
- **Out of scope**: `07 Tenders` (another agent is building it concurrently — its folder
  is untouched by this work); any other case-study folder; the live website; API keys.

## House rules that bind every phase (portfolio precedent)

- **Nothing downstream is generated until Eva signs off the design doc.** Design gate
  passed 11 Sep 2026 (Eva's own words, recorded in `design/DECISIONS.md` — this is a real
  gate, not a proxy one, unlike some earlier cases).
- Deterministic, seeded generation (`RANDOM_SEED = 8`); all tunables in `code/config.py`;
  `pathlib` paths relative to script location; outputs only to the specified output
  folders; source files never modified.
- **Coherence rules in the design doc are hard requirements**, enforced by
  `code/validate_structure.py`, which exits 1 on any failure.
- **The core generation pattern (Hapax `CLAUDE.md`)**: deterministic Python controls
  every email's structure (intent, facts, planted trap); LLM prose agents (Phase 2's
  prose sub-phase and beyond) dramatise only — they may never add or remove a planted
  signal. Briefs carry everything structural.
- **The answer key is read by nothing but the future `code/mark.py`.** It is complete
  before any prose exists, per the design doc's item (e).
- Fictional names collision-checked against the seven existing portfolio firms
  (Jalavakoski Konepaja, Pyökkipaja, Saarnitukku, Paju Consumer Products, Kataja
  Analytics, Sammalkoski, Visakoivu) — checked programmatically in
  `validate_structure.py`, not just by eye.
- Agent cost discipline: scout (Haiku) for lookups, python-builder (Sonnet) for
  mechanical implementation, case-drafter/writer (Sonnet, then Opus edit) for prose;
  main loop / Opus for design decisions and review. At most one heavy-compute agent at
  a time.
- Voice and honesty rules: synthetic data declared prominently; numbers over adjectives;
  negative results stay in; the word "fraud" appears nowhere in the corpus.

## Phases

### Phase 1: Design doc → EVA GATE — PASSED 11 Sep 2026, Eva's own sign-off

**Goal**: a signed-off `design/design.md`.

**Work**:
- [x] `design/design.md` written, covering the story, the invented company (Tammilehto
  Oy), the corpus (150 inbound emails / ~90 threads / 3 simulated weeks), the trap table
  (§3), the pipeline and router rules (§4), marking (§5), what the case does not claim
  (§6), pre-registered expectations (§7), the interactive page concept (§8), phases (§9),
  and four open questions for Eva (§10).
- [x] Eva's gate: "fab, go for it with case 08" — the four open questions resolved to the
  design's own recommendations: (1) equipment rental as the sector; (2) the conservative
  auto-approved set (all commercial judgment queued); (3) 150 emails / ~90 threads; (4)
  the River flow visual leads.

**Verification**:
- [x] **HARD STOP: Eva's sign-off before Phase 2** — passed 11 Sep 2026, her own words,
  recorded in `design/DECISIONS.md`.

### Phase 2: Corpus structure → COMPLETE 11 Sep 2026

**Goal**: the deterministic structure (policy handbook, customer register, thread
skeletons, email briefs, answer key) passing validation, byte-identical on regeneration.
No prose generated yet.

**Work**:
- [x] `code/config.py` — every tunable: seed, corpus profile (150 emails / 90 threads /
  3-week Sept 2026 window), the trap table exactly per design §3 (8 refund-denial, 5
  above-authority discounts, 6 prior-promise contradictions, 4 must-escalate safety, 3
  data requests, 5 policy-misquotes, 4 angry-but-entitled, 6 needs-info, 109 routine),
  the auto-approved intent-class set (routine + policy corrections only), the router
  rule as a single function (`route_for_intent`) shared by the generator and the
  validator so they cannot drift apart, Tammilehto Oy company constants, discount
  authority ceilings by role, six invented staff members, ~25 customer accounts
  (15 business / 10 consumer, Oulu-region, collision-checked against the seven existing
  portfolio firms).
- [x] `code/generate_structure.py` — deterministic generation of the ~30-clause policy
  handbook (YAML + rendered Markdown), the customer register CSV, 90 thread skeletons
  (JSON, with the 6 prior-promise threads carrying a real planted staff promise
  structurally), 150 email briefs (JSON, one per inbound email), and the answer key CSV
  (route, binding clauses, correct commitments, trap class — built before any prose
  exists).
- [x] `code/validate_structure.py` — eight coherence-rule groups (completeness, trap
  counts, clause-binding consistency, prior-promise integrity, thread date ordering,
  route derivability against the router rule, name-collision freedom, handbook shape).
  Exits 1 on any failure.
- [x] Run personally: `generate_structure.py` then `validate_structure.py` — **all
  checks PASS**. Regeneration verified byte-identical (SHA-256 over the whole `data/`
  tree, two consecutive runs).

**Verification**:
- [x] `validate_structure.py` exit 0
- [x] Byte-identical regeneration (SHA-256 match across two runs)
- [x] Trap counts match config exactly: refund_denial 8, above_authority_discount 5,
  prior_promise_contradiction 6, must_escalate_safety 4, data_request 3,
  policy_misquote 5, angry_entitled 4, needs_info 6, routine 109 (150 total)
- [x] Route distribution derived from perfect classification: auto_send 126,
  human_queue 17, escalate 7 (this is the ideal-key figure, not a prediction about the
  Phase 3/4 pipeline's actual straight-through rate — see `design/DECISIONS.md` for the
  intent-class taxonomy this rests on)
- [x] Customer and company names collision-free against the seven portfolio firms

### Phase 3: Prose (emails + staff replies)

**Goal**: LLM prose agents dramatise every brief and every planted staff promise into
real email language, without adding or removing any planted signal.

**Work**: complete (20 Sep 2026). 16 batches on the email-writer agent (Opus 4.6,
corpus rules), 150 customer emails + 53 staff messages, all 6 promises planted and
redeemed; assemble_emails.py clean; validate_emails.py PASSED after four logged
validator-side adjustments (no prose touched) - see design/DECISIONS.md 20 Sep.

### Phase 4: Pipeline build — COMPLETE 20 Sep 2026

**Goal**: classify → retrieve → draft → gates (policy / consistency / completeness) →
router, per design §4.

**Work**: complete (20 Sep 2026). Pipeline built and fixture-tested (47/47 unit + integration assertions). Seven implementation resolutions endorsed; both LLM stages on Sonnet. See design/DECISIONS.md 20 Sep entries.

### Phase 5: The run — COMPLETE 20 Sep 2026

**Goal**: all 150 emails through the pipeline, artefacts logged per email.

**Work**: complete (20 Sep 2026). Classify 10/10 batches, draft 10/10 batches (Sonnet), gates + router deterministic pass. Route counts as ran: auto_send 122, human_queue 21, escalate 7. Frozen as ran; no reruns.

### Phase 6: Marking + writeup — COMPLETE 20 Sep 2026

**Goal**: `code/mark.py` against the held-out answer key, `data/analysis/report.md`
against §7's pre-registered expectations, interactive page, writeup (Opus writer agent,
per Eva's standing instruction), case page + work.html + shapes cross-link.

**Work**: complete (20 Sep 2026). mark.py scored all 6 pre-registrations (3 met, 3 not met); five marking-judgment verdicts signed off by Eva. Writeup drafted by Opus writer agent. Interactive page and site integration pending.
