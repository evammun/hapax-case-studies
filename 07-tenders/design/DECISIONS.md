# Tender Workflow case study — decision log

Running log of design, data, and code decisions. Newest entries at the bottom
of each section. Project 7 of the portfolio ("The step up, measured",
cross-theme). Plan: `PLAN-tender-workflow-case-study.md` at the project root.

## Gate passed (11 Sep 2026) — Eva's own sign-off

**This is a real gate, not a proxy.** Unlike Cases 2 and 3 (Luigi answered
those open questions in Eva's register, under her advance directive), Eva
read `design/design.md` herself and signed off in her own words: *"perfect,
go for it."* Her four open-question resolutions, as recorded in the design
doc's status line:

1. **Persona cast tone: habits, never mockery.** No persona is stupid, only
   unstructured — the recommendation, endorsed as written. This governs
   every habit paragraph in `code/config.py`: each persona's weakness is a
   specific, recognisable working habit (skips annexes, panics near the
   deadline, trusts the summary page), never incompetence in general.
2. **Sector: kept as drafted.** Maintenance/installation/framework services
   for a technical and engineering firm, not shifted toward Hapax's own
   advisory/training client profile.
3. **Scope: full 16×4 kept, not trimmed to 12×4.** Eva's own words: the
   section title "Seventy private habits" is explicitly endorsed, which only
   scans at the full 64-attempt count.
4. **Procurement flavour: Finnish-flavoured, per the recommendation** —
   hankintailmoitus conventions referenced loosely, no real portal or
   authority named anywhere in the corpus.

## Seed choice

**`RANDOM_SEED = 7`** — fresh for this project, not reused from any other
case (01 Churn and 04/05/06 use 42; 02/03 also use 42). A fresh seed was
chosen deliberately: Project 7 is the first case to combine two independent
seeded subsystems (the requirement/trap generator and the persona engagement
model) in one script, and reusing 42 risked an unexamined coupling between
this project's RNG stream and habits carried over from copy-pasted generator
code. Every draw in `code/generate_structure.py` salts `RANDOM_SEED` with
tender/persona indices via `deterministic_rng()`, so the corpus is
byte-identical on any re-run without needing a single global RNG instance.

## The engagement model — structure decides who noticed what

**Decision (design.md S4, the load-bearing point): coverage outcomes are
seeded structure, not LLM improvisation.** Phase 3's prose agents will
dramatise a chat transcript and a draft response per persona-tender attempt,
but they do not decide which requirements that attempt noticed — Phase 2
already decided that, deterministically, before any prose exists.
`build_attempt_brief()` in `code/generate_structure.py` draws one seeded
coin-flip per requirement, biased by the persona's numeric traits (a type
trait — `eligibility_scrutiny` / `thoroughness` / `form_attentiveness` /
`format_precision` — times an annex penalty, a hidden-requirement penalty,
and a time-pressure decay across the numbered list) and writes the result as
`engagement: "engaged"` or `"skimmed"` per requirement. The Phase 3 brief
tells the prose agent: dramatise a transcript and draft **consistent with
this list**; do not invent additional noticing or missing.

**Calibration, recorded honestly.** The persona trait values, drafted
directly from the habit paragraphs with no reference to any target number,
produced a first-run population median of ~31% Arm-A coverage — well under
design.md S7's pre-registered 55–80% band, because five independent
sub-1.0 probability factors compound multiplicatively per requirement. Two
population-level rescale passes were applied in `code/config.py`
(`TRAIT_RECALIBRATION`, then a concave boost `f(x) = 1-(1-x)^1.9` plus a
halved `time_pressure_decay`), both applied uniformly across all 14 personas
with no persona-specific or attempt-specific tuning, and neither looking at
any individual attempt's resulting number. After the second pass:

| §7 expectation | Band | Result |
|---|---|---|
| Arm-A median coverage | 55–80% | **70.5%** |
| Tenders where the best attempt reaches ≥90% | ≥3 | **3** |
| No-bid-tender attempts engaging the eligibility trap | ≤1 recommending NO-BID | **2 of 8 engaged** (engagement is necessary, not sufficient, for the actual recommendation — that call is Phase 3's) |

This is calibrating a generative model before any attempt exists, which is
ordinary model-building; it is categorically different from retuning
individual outcomes after seeing them, which design.md S7's closing line
forbids and which does not happen here or anywhere in this project. Where
the chips fall on any individual attempt is the finding, not a target hit by
construction — the no-bid-catch band in particular is reported as a
diagnostic on the model, not a guarantee, since the actual bid/no-bid
recommendation only exists once Phase 3 drafts the response.

## Name collision-check results (11 Sep 2026, pre-build)

- **"Visakoivu Oy"** (the bidding company, already fixed by the signed-off
  design doc) — web search found no company of that exact name. The word
  itself names a prized curly-birch timber and several real firms trade in
  it (Seinäjoen Puutavara Oy, BellusWood Oy, Eskolan Visa Oy / Royal Koivu),
  but none holds it as a company name. Checked against the six existing
  portfolio protagonist companies — Jalavakoski Konepaja Oy (02), Pyökkipaja
  Oy (03), Paju Consumer Products Oy (05), Saarnitukku Oy (06), 01 Churn's
  un-named vendor, and 04 Contracts' real CUAD parties — no overlap. One
  point of note, not a collision: "Koivu" (birch, plain) is already a
  fictional client name in 01 Churn's roster (Koivu Oy, Koivu Ventures Oy);
  "Visakoivu" is a distinct wood-species term, not "Koivu" with a prefix, so
  this is judged clear, but it is the closest adjacency found and is
  recorded here rather than silently passed.
- **The ten reference-project client names** (`config.REFERENCE_PROJECTS`)
  are fresh tree/nature roots, checked against every root already used
  anywhere in the portfolio's fictional companies: Koivu, Mänty, Paju,
  Haapa, Salo, Laakso, Harjula, Leppä, Raita, Virta, Tammi, Aalto, Jalava,
  Saarni, Pyökki, Kataja, Metsä, Kruunu, and the Estonian/Swedish/German
  rosters used in 01 Churn and 03/05/06. Chosen roots — Kuusi (spruce),
  Petäjä (pine), Vaahtera (maple), Pihlaja (rowan), Honka (tall pine), Näre
  (spruce, dialectal), Tuomi (bird cherry), Kelo (weathered pine), Terva-leppä
  (black alder) — are all unused elsewhere in the portfolio.
- **The 14 persona names** — checked against the portfolio's fictional
  people. No named-individual cast exists anywhere else in the portfolio
  (the other six cases populate companies, job-title placeholders, and real
  CUAD contract parties, never named staff), so this collision surface is
  empty; the names were chosen only for plausibility and variety.
- **Invented tender buyers** (16 organisations, `config.TENDERS`) — chosen
  as clearly generic/invented municipality, wellbeing-region, and private
  company names (e.g. "Keskijärven kaupunki", "Jarviseudun hyvinvointialue"),
  deliberately avoiding the pattern of any real Finnish municipality or
  hyvinvointialue name. Not exhaustively checked against the full Finnish
  municipal register (out of proportion to the risk — these are procuring
  entities in a synthetic exercise, not the protagonist company or a named
  individual), but no real authority or portal name is used anywhere, per
  the design doc's explicit instruction.

## Phase 2 build notes

- **Trap placement is hardcoded, not seeded**, so design.md S3's exact trap
  counts (3/2/3/3/3, 4 clean) are guaranteed by construction rather than by
  a lucky draw — `config.TENDERS` lists each tender's traps explicitly, and
  an import-time assertion in `config.py` checks the resulting counts
  against `config.TRAP_TABLE` before generation even starts.
- **The two no-bid mechanisms are deliberately different failure shapes**:
  T11 fails on a missing certification (ISO/IEC 27001 — Visakoivu, a
  hands-on trade contractor, never pursued an information-security
  certification), T15 fails on a reference-value band (requires a single
  reference ≥ €2,000,000; Visakoivu's largest, REF02 at €1,650,000, falls
  short). Both are checked programmatically against the facts library at
  generation time (`assert_eligibility_consistency`) and again,
  independently, by `validate_structure.py` reading the written
  `company_facts.yaml` from disk — not generation's in-memory dict.
- **Contradiction traps plant two linked rows** (`trap_group_id` shared,
  one in the body, one in an annex) rather than one row, since a body/annex
  contradiction is inherently a pair. The validator counts trap *instances*,
  not rows, for this trap type specifically (3 instances = 6 rows) — a
  first-run validator failure caught this exact miscount and was fixed
  before this log entry was written.
- **Body/annex placement fractions were tuned alongside the engagement
  model** (see above): the first draft routed a majority of technical/
  commercial/form requirements into annexes, which was both unrealistic
  (most tender content lives in the body; annexes hold detail, not the
  bulk) and a major contributor to the too-low first-run coverage. Final
  fractions keep 70–88% of each type in the body depending on type, with
  annexes reserved for genuine detail — consistent with how the annex-based
  traps (buried disqualifier, buried form) are supposed to stand out
  *because* annexes are the less-visited part of the document, not the
  majority of it.

## Corpus-normalisation and integrity pass (11 Sep 2026, pre-arm)

All 16 tender documents existed but nothing downstream (Arm A, Arm B) had
consumed them yet, so structural fixes were still legitimate. Four jobs,
run in order, each gated on the previous one still passing
`validate_structure.py`.

**Job 1 — the T03 duplicate trap.** T03-R013 ("Valtakirja allekirjoittajalle",
an ordinary annex checklist form) and T03-R014 (the hidden_form trap) were
the SAME form — the checklist item defused the trap, since a reader who
noticed R013 had already satisfied R014 without ever finding the buried
sentence. Root cause: the hidden_form trap's topic draw
(`deterministic_rng(tender_num, 2)`) is intentionally independent of the
generic form-pool draw for the same tender (`deterministic_rng(tender_num,
1)`), and for T03 the two independent draws happened to land on the same
FORM_TOPICS entry. Fixed at source with a new `config.HIDDEN_FORM_TOPIC_OVERRIDE
= {"T03": "Todistus verojen maksusta"}`, checked against T03's other form
items (Laatujarjestelman kuvaus, Valtakirja allekirjoittajalle) to guarantee
no overlap, plus a new self-defending assertion in `generate_structure.py`
that raises if any tender's hidden_form topic ever duplicates a form that
tender already requires elsewhere — the same defect class cannot recur
silently for any future tender. `tender_03.md`'s buried closing sentence was
rewritten from the power-of-attorney duplicate to "the tender must also
include a certificate confirming payment of the tenderer's taxes", kept in
the same buried, once-only, end-of-annex location and matching the
document's existing register (mirroring the phrasing already used
elsewhere in the corpus, e.g. T12's "a certificate confirming payment of
the tenderer's taxes").

Regenerated `generate_structure.py` with the same `RANDOM_SEED = 7` and
verified by SHA-256 hash across all 100 generated files (16
`requirements_NN.csv` + the combined `answer_key.csv` + `company_facts.yaml`
+ `company_facts.md` + 16 `brief_NN.json` + 64 `attempt_NN_PP.json` +
`assignment_matrix.json`): only three files changed —
`requirements_03.csv`, the combined `answer_key.csv`, and `brief_03.json`.
Every other file, including T03's own four attempt briefs, is byte-identical
to the pre-fix corpus — the engagement model keys on req_id/type/location/
mentioned_once, not on requirement description text, so the topic swap
never touches it. No surgical patch was needed; the regeneration was
already surgical. `validate_structure.py` passes.

**Job 2 — id-strip normalisation.** Grepping `\bT\d\d-R\d\d\d\b` across
`data/tenders/*.md` found the leak confined to the four gnarly tenders,
T13–T16 (not the twelve originally suspected — T01–T12 already used
realistic clause numbering, confirmed by inspection). Printing internal
req_ids in the tender text is unrealistic and trivialises Arm B's
extraction step, which is the thing this project measures.

Normalisation convention adopted corpus-wide, mirrored from what T09–T12
(and T05/T06/T08) already did organically: body requirements number
`N.M`, where `N` is the body section's own `## N. Title` heading number;
annex requirements number `Letter.M` flat (`A.1`, `B.2`, ...) unless the
annex carries its own numbered `### N. Title` subsections, in which case
items number `N.M` per subsection and the annex letter is dropped
entirely — exactly how T05/T06/T08's annexes already do it. This is a
numbering-LABEL transform only, done by script
(`code/build_clause_maps.py`), never by hand: requirement text and order
are untouched, and the script asserts every requirement in the answer key
is accounted for (either found as a printed tag, for T13–T16, or already
present as a realistic label, for T01–T12) before writing anything, else
it fails loudly rather than guessing. 54/52/51/52 tags were stripped from
T13/T14/T15/T16 respectively. One T13-specific wrinkle: two requirements
in Liite A section 3 already carried pre-existing nested bold titles
("**3.1 Preventive maintenance plan**") announcing their own clause
number one line above the tagged paragraph — the script drops the
now-redundant tag rather than printing the number twice.

Building the id-strip transform's cross-check surfaced four PRE-EXISTING
defects in the "already realistic" documents that would have made an
honest 1:1 clause↔requirement map impossible, none related to Job 1's bug
and all predating this pass:
  - **T01**: the Tarjouslomake (Tender Form) requirement was mentioned only
    in unnumbered intro prose ("Tenderers must complete and return the
    Tender Form...") instead of getting its own clause. Given a number
    (6.1), the two following format clauses renumbered to 6.2/6.3.
  - **T04**: three distinct requirements (pricing basis, PDF-file format,
    the font-size format_trap) were merged into one undifferentiated
    clause 6.2. Split into three clauses (6.2–6.4) in the answer key's own
    order.
  - **T05, T06**: Liite A's "Binding conditions" subsection numbered a
    piece of general chapeau prose ("The conditions in this section are
    binding on...") as clause 3.1 even though it isn't a requirement at
    all — inflating the label count by one in each document. Demoted to
    unnumbered prose; the actual annex_disqualifier trap immediately below
    keeps its already-correct label 3.2 untouched in both documents.
  - **T13** (discovered after the strip, not before): the annex_disqualifier
    trap's text is a fixed template in `config.py` that self-cites "see
    annex clause 3.2" — true by construction for T05/T06 (where the trap
    organically lands at 3.2) but stale for T13, where the mechanical
    renumbering correctly gives the trap clause 7.1. Fixed by editing the
    self-reference to "see Section 7.1 of this annex"; the trap's
    substance and its `correct_action` are unchanged.

Emitted `data/tenders/clause_map_NN.json` for all 16 tenders (document
clause label ↔ req_id ↔ location), built directly from the printed tags
for T13–T16 and recovered, for T01–T12, by parsing the documents' existing
clause numbers in order and zipping them 1:1 against the answer key's
`req_number` order — safe because the prose-agent brief forbids reordering
or relocating requirements, and the script asserts the counts match before
zipping (this is exactly the check that surfaced the four defects above).
Rows flagged `mentioned_once` (the three hidden_form traps, one per T03/
T09/T14) are excluded from the zip and recorded with `clause_label: null` —
by design, deliberately buried and unlabelled in every one of the three
documents that carries one, not just T03.

**These clause maps are key-side tooling, not corpus content: NO ARM MAY
READ THEM.** Each file's own `_meta.notice` field states this, and it is
restated here as a hard project rule: `clause_map_NN.json` exists solely
for the Phase 5 marking script (`code/mark.py`) to translate its own
findings back into document clause numbers when reporting results — never
as an input to Arm A persona prompts or Arm B's extraction pipeline. Any
future pipeline code that reads `data/tenders/clause_map_*.json` outside
`code/mark.py` is a bug.

**Job 3 — corpus integrity check (`code/validate_corpus.py`).** Checks,
independently of `validate_structure.py`: every eligibility requirement's
numeric threshold or certification code is present at its own mapped
clause (63 checked); every non-buried form requirement's named form is
present at its clause via a small bilingual (Finnish/English) alias table
(68 checked); every hidden_form trap's buried topic appears on exactly one
line of its tender's document, corpus-wide (3 checked — a regression guard
for the Job 1 defect class); both values of every contradiction pair are
present in their distinct body/annex locations (3 pairs); neither
eligibility-fail trap (T11, T15) has hedging language ("note", "important",
"please ensure", etc.) near its clause; every tender's submission deadline
is on or after its own publication/issue date and no eligibility
requirement asks for a certification that would have lapsed
(`company_facts.yaml` `valid_until`) before that tender's own deadline —
16/16 tenders had both dates parsed and checked. All checks passed on the
corpus as fixed under Job 1 and Job 2; no further document defects were
found. (Several early failures were bugs in the checker itself, not the
corpus — a case-sensitivity gap in the certification/form alias patterns,
a missing "list of subcontractors" word-order variant, and, most
substantively, `extract_clause_text` initially matching the FIRST
occurrence of a label like "2.1" anywhere in the file rather than scoping
to the correct body-section-or-annex-subsection context, since these
labels are not globally unique. All four were fixed in the checker before
trusting its result.)

**Tooling note.** `code/build_clause_maps.py` is a one-off migration tool
like the churn project's `fix_ticket_dates.py` family — it strips req_id
tags out of T13–T16 and is not idempotent (a second run against an
already-migrated corpus fails loudly rather than silently reprocessing).
It is not part of the regular Phase 2 pipeline order and should not be
re-run.

## Fabrication seeding — the gap between S7.4 and the attempt briefs (11 Sep 2026, pre-Arm-A)

**The gap.** design.md S7.4 pre-registers "fabricated claims present in
≥25% of Arm A attempts", but a grep for "fabricat" across every one of the
64 `data/attempt_briefs/*.json` files, run after Phase 2 finished and
BEFORE any Arm A prose existed, returned nothing. The attempt briefs already
carry a full seeded engagement model (which requirements each persona
noticed) but nothing at all about which claims a persona's draft would
overclaim. Left unfixed, S7.4 would have been satisfied (or not) by the
Phase 3 `ticket-writer`-pattern prose agent improvising fabrication on its
own judgement per attempt — which breaks the house pattern used everywhere
else in this project and portfolio: deterministic Python decides structure
and outcomes, LLM agents dramatise prose consistent with a brief they may
not deviate from. The engagement model's own docstring in
`generate_structure.py` states this explicitly for coverage; fabrication
had simply been left out of that discipline.

**The mechanism chosen: unverified assistant output, not deliberate lying.**
Every fabrication event in the new `code/seed_fabrication.py` is framed the
same way: a chatbot plausibly drafts an overclaim when asked to summarise
Visakoivu's eligibility, track record, capacity, or capability, and the
persona pastes it into the response without checking it against the facts
library. This keeps faith with S10 Q1's "habits, never mockery" register —
no persona is depicted as dishonest, only as skipping a verification step,
exactly like the existing engagement model's skimmed-vs-engaged framing for
requirements. `checks_facts_library` is the field that decides whether that
verification step happened; `fabrication_events` (empty when it did) is
what slipped through when it did not.

**Two new fields, seeded, added to all 64 attempt briefs in place:**

- `checks_facts_library` (bool) — driven by each persona's already-existing
  `eligibility_scrutiny` and `time_pressure_decay` traits (no new persona
  data invented): `eligibility_scrutiny` is literally described in
  `config.py` as the trait for "checking a certification or reference
  threshold against the facts library", which is exactly what this field
  measures. `p_check = clip(-0.35 + 1.6*eligibility_scrutiny -
  0.4*time_pressure_decay, 0.03, 0.97)`, one seeded coin-flip per attempt.
  No persona-specific hardcoding — the same discipline the engagement model
  already uses.
- `fabrication_events` (list, empty when none) — populated only when
  `checks_facts_library` is false, via a second seeded coin-flip
  (`EVENT_PROBABILITY_GIVEN_NOT_CHECKING`) and, if it fires, one concrete
  event drawn from four mechanisms: `invented_certification`,
  `inflated_reference`, `capacity_overclaim`, `uncited_capability`. Kept to
  exactly one event per contaminated attempt, deliberately, for markability
  — Phase 5's `mark.py` needs one clean fabrication count per attempt, not
  a combinatorial mix. Every event carries `claimed_value`/`true_value`
  fields alongside its prose `instruction`, so marking never has to parse
  free text to check it.

**RNG stream.** `RANDOM_SEED = 7` is unchanged (continuity with the rest of
the project). `seed_fabrication.py` folds in a distinct `FABRICATION_SALT`
(424242017) before any tender/persona index, so its draws are statistically
independent of `generate_structure.py`'s engagement-model stream even on
identical (tender, persona) inputs — re-running either script alone stays
byte-for-byte deterministic and the two never share a coin-flip.

**The no-true-fact guard.** Every event is checked programmatically against
`company_facts.yaml`, both at generation time (a freshly built event that
fails its own guard raises immediately, so a bad event can never be written)
and again, independently, by a new Rule 7 in `validate_structure.py`, which
reads `company_facts.yaml` fresh from disk (never trusting any in-memory
dict) and calls the same `seed_fabrication.validate_event()`. Concretely:
`invented_certification` targets are checked against the held-certificate
set; `inflated_reference` and `capacity_overclaim` claims are checked as
strictly exceeding the real value on file; `uncited_capability` claims are
checked via a keyword-absence scan across the flattened facts text.
Sanity-tested against three deliberately-bad events (a cert Visakoivu
genuinely holds, a "claim" that isn't actually higher than the truth, a
target that does not exist) — all three were correctly rejected before this
was trusted.

**Calibration, recorded honestly (the same discipline as the engagement
model's two rescale passes).** The `p_check` formula, drafted directly from
existing traits with no reference to any target number, produced 26/64
(40.6%) `checks_facts_library=true` — directionally consistent with S10
Q1's qualitative buckets in aggregate (the three "mostly true" personas,
P01/P04/P11, checked 8/14 attempts combined = 57%; the four "mostly false"
personas, P03/P05/P10/P14, checked 3/19 = 16%), though individual personas
show real seeded variance at n=4–5 per persona — e.g. P08 ("old-school,
distrusts the chatbot") landed at 4/4 checking, higher than its "mixed"
label implies. This is judged a legitimate emergent finding, not a defect:
P08's habit paragraph has him using a chatbot only as a grammar pass on
paragraphs he already wrote from his own template library, never asking it
to draft content — the fabrication mechanism (an unverified chatbot draft
pasted in) applies to him more weakly than to any other persona for reasons
the habit paragraph already implies, even though no explicit rule encodes
that. The first pass at `EVENT_PROBABILITY_GIVEN_NOT_CHECKING = 0.8` landed
the seeded draw at 32/64 (50%) attempts with an event — real coin-flip
variance on a 38-attempt population, above the intended 30–45% structural
band. Rescaled once, population-wide, to `0.6`, without looking at any
individual attempt's resulting event, landing at 22/64 (34.4%) — comfortably
inside 30–45% and clearly above S7.4's ≥25% floor. Event-type distribution:
`invented_certification` 8, `capacity_overclaim` 7, `uncited_capability` 4,
`inflated_reference` 3 (of 22). This is calibrating a generative model
before any attempt exists, exactly as the engagement model's own DECISIONS
entry describes; it is categorically different from retuning individual
outcomes after seeing them, which does not happen here.

**Pre-registration intact.** This entire pass — gap discovery via grep,
mechanism design, implementation, calibration, and validation — ran before
any Arm A prose existed. No Phase 3 `ticket-writer`-pattern agent has
dramatised a single chat transcript or draft response yet, so nothing about
what those agents will write has been observed or could have influenced
these parameters. `validate_structure.py` passes with this addition
(`Rule 7`); Phase 3 briefs handed to prose agents will need to instruct them
to render exactly the fabrication events listed (or none) in the persona's
draft — no more, no less — the same "may not add or remove a planted
signal" constraint the engagement model and trap placements already use.

## "Play a tender yourself" committed (11 Sep 2026)

- **Eva approved the playable mode for the interactive page** ("Let's do it!!!",
  following her own half-joking suggestion of a browser game). Design doc §8 gains
  view 4: curated quick-play set, annexes collapsed by default as the authentic trap
  mechanism, clause-level marking against the same held-out key via a JS port of the
  marking logic (spot-checked against mark.py), placement on the per-tender scatter
  against the 64 attempts and the workflow line.
- **Privacy rules fixed at commitment**: nothing stored, nothing transmitted; the
  score exists only on the visitor's screen — keeps the trust page's claims exactly
  true with no consent apparatus.
- Detailed UI deferred to Phase 6 design, where it belongs.

## Arm A complete: 64/64 attempts assembled and validated (11 Sep 2026)

**Status.** All 64 persona-attempt files (`data/arm_a/attempt_TT_PP.json`) written by
eight parallel Sonnet prose-writer batches from the frozen Phase 2/2b briefs
(`data/attempt_briefs/`) are in place. `code/validate_arm_a.py` (new, run this session)
checks the corpus against design.md §4/§6; it never generates or edits prose, only
verifies, per the ticket-writer pattern used throughout the portfolio.

**One mechanical defect found and fixed at source, not hand-edited around.** Sixteen
attempts — the complete output of the batches assigned to tenders T03, T04, T07 and
T08 — wrote their internal `attempt_id` field without the `attempt_` prefix (e.g.
`"03_01"` instead of `"attempt_03_01"`), evidently a shared template slip across those
four batches specifically. This is exactly the class of stray-field schema issue the
house rule permits fixing directly (never prose content): a script corrected all 16
`attempt_id` values in place to match their filename, byte-for-byte identical
otherwise. Re-run confirmed clean.

**Validation results (all hard checks pass after the fix):**
- **Completeness**: 64/64 files, one per `assignment_matrix.json` entry, all valid
  JSON against the schema; speakers restricted to `persona`/`assistant`; every
  `persona_name` matches `config.py`.
- **Fabrication fidelity**: all 22 planted fabrication events across the corpus trace
  verbatim or numerically into their own attempt's draft (certification codes matched
  on digit sequence to survive "ISO/IEC 27001" vs "ISO27001" phrasing; free-text
  capability claims matched on keyword overlap). All 26 `checks_facts_library=true`
  attempts were scanned for the corpus-wide fabrication vocabulary (not-held cert
  codes, the specific inflated reference values and capacity-overclaim figures drawn
  elsewhere in the corpus, the uncited-capability phrases) — zero leaks. A staff-figure
  spot-check against `company_facts.yaml` flagged five drafts citing "650" near a
  discipline word; all five are confirmed benign on inspection — an artifact of the
  scanner splitting the correctly-cited reference value "EUR 1,650,000" (REF02, real)
  at the comma, not a fabricated staff count.
- **Decision-table conformance**: every attempt's `bid_decision` matches the
  `eligibility_trap_engaged` × `checks_facts_library` prediction for its tender. Zero
  mismatches.
- **Contamination**: no req-id pattern, "answer key", "clause_map", or self-referential
  "brief" mention anywhere in any transcript or draft. One "trap" hit flagged and
  inspected (`attempt_11_01`: the persona calling the tender's own price-format
  gotcha "a trap I definitely caught" — an in-world, innocent use, not a meta-leak).
- **Hygiene**: the word "fraud" appears nowhere in the corpus. UTF-8 clean throughout.
  Total `data/arm_a` corpus size: **371,319 bytes (0.354 MB)** — comfortably inside the
  interactive page's <2 MB budget (design.md §8). Word counts run shorter than the
  commissioned 300–800 (transcript) / 250–1,200 (draft) range on 24 of 64 attempts,
  concentrated in the four simple tenders (mean 262/231 words there against the 300/250
  floors) and a handful of medium ones; no attempt exceeds the ceiling. Flagged, not
  hand-edited — prose length is a content matter for a targeted re-run, not a schema
  defect, and no per-size batch-instruction record was found in the repo to check
  against instead of the flat range.

**FROZEN pre-registration observation, published as-is.** Design.md §7.2 pre-registered
"Arm B recommends NO-BID on both no-bid tenders; **at most 1 of 8** no-bid persona
attempts does the same." The seeded corpus, unchanged from Phase 2b, produces **2 of 8**:
both on T15 (personas P06 and P12, the only two of the tender's four attempts with
`eligibility_trap_engaged=True` *and* `checks_facts_library=True`), 0 of 4 on T11. This
was already fixed at the brief level before any Arm A prose existed (`eligibility_trap_
engaged` is a Phase 2 generation-time property); this validation pass only confirms the
64 written drafts render it faithfully — every no-bid call traces to exactly the
predicted brief property, no more and no fewer. Per the portfolio's calibration
discipline, this is recorded honestly for Phase 5's `mark.py` to publish, not retuned.

**Next**: Arm B pipeline build (Phase 4).

## Under-length Arm A attempts accepted (11 Sep 2026, main loop)

Validation flagged 24 of 64 attempts under the commissioned word-count floors,
concentrated on the four simple tenders. Ruling: ACCEPTED as-is, no re-run. The
floors were commissioning guidance; the engagement lists are the content driver, and
a persona who engaged 6 of 15 requirements honestly produces a thin draft. Padding
to a floor would inflate the very artefact the case measures. The word-count bands
are hereby subordinate to engagement-list fidelity, which validated clean 64/64.

## Arm B harness built (11 Sep 2026) — the deterministic skeleton, not the runs

**Scope.** This is design.md S5's harness only: the deterministic scaffolding
around the two MODEL steps (extraction, drafting), which future run-agents
perform per `code/arm_b/RUNBOOK.md`. No Arm B run exists yet — `data/arm_b/`
stays empty until Phase 4's actual 16 runs. Built: `code/arm_b/FORMATS.md`
(the `matrix.json` / `response_v{N}.json` / `gate_report_{N}.json` /
`signoff.json` schemas, including fact-path syntax into
`company_facts.yaml`), `code/arm_b/gates.py` (the three deterministic
gates), `code/arm_b/router.py` (terminal-state routing and `signoff.json`),
`code/arm_b/RUNBOOK.md` (the run-agent's strict protocol, including the hard
5-iteration cap and the never-read list: no `answer_key/`, no
`clause_map_*.json`, no `arm_a/`, no `tender_briefs/`), and a dry test
(`code/arm_b/fixtures/` + `code/arm_b/test_gates.py`).

**Gate semantics, five lines.** Coverage: every matrix row needs a
non-empty `answer_text`, or the run is `no_bid` with a reason naming the
unanswered row(s) by `matrix_id`. Facts: every citation must resolve into
`company_facts.yaml`, and every specific claim in an answer (a € amount, a
headcount, a certification name, a year count) must be supported by the
*value* of one of that row's own citations — not merely accompanied by a
citation that happens to exist. Certification claims additionally require
the cited certification's `held` flag to be true, closing a gap a plain
substring match would leave open (Visakoivu's own facts file lists
ISO/IEC 27001 with `held: false` — the T11 trap — so a naive "the text
mentions ISO27001 and a citation exists" check would wave through a false
claim citing that exact entry). Consistency: a bid (`no_bid: false`) may not
go out with an eligibility-kind row whose own `answer_text` concedes failure
(a fixed English/Finnish failure-phrase vocabulary, since the gates cannot
consult the answer key to know the truth independently — only the draft's
own words); and the same cited `fact_path` may not be quoted at two
different numeric values across rows. None of the three gates ever reads
`data/answer_key/` or `clause_map_*.json` — every check is draft-vs-matrix-
vs-facts-library internal consistency, exactly as design.md S5 specifies.


**Fixture test results.** `python code/arm_b/test_gates.py` — **ALL CHECKS
PASSED**, all 5 designed outcomes hit on a tiny synthetic 3-requirement
fixture (`code/arm_b/fixtures/`, not part of the real corpus):
unanswered row → `UNANSWERED_ROW` (coverage); an uncited € claim →
`FABRICATION` (facts); a certification cited from a `held: false` entry →
`FABRICATION` (facts, proving the held-flag check, not just name-matching);
two rows quoting the same `financials.2025.revenue_eur` at two different
values → `CROSS_ROW_INCONSISTENCY` (consistency) — this fixture also
(correctly) trips a `FABRICATION` on the wrong-valued row, since at most one
of two conflicting claims about a single real fact can be true; and a clean
run with all three rows answered and properly cited → zero bounces, all
three gates pass. Also spot-checked `resolve_fact_path()` against the real
`data/facts/company_facts.yaml` directly (RALA, REF02, LVI staff count,
2025 revenue, liability cover, and the `references`→`reference_projects`
alias) — all resolve correctly, not just against the fixture. A separate
CLI-level check (`python gates.py` / `python router.py` run against a copied
fixture, then discarded) confirmed the full loop end to end: gate failure →
router refuses to write `signoff.json` (not a terminal state) → simulated
5 failing iterations → router writes `signoff.json` with `status: "stuck"`,
`bid_no_bid: "UNRESOLVED"`, and the still-open bounce types listed, rather
than forcing a false pass.

**Flagged, not fudged — one gap in S5's coverage.** `response.json`'s
`general_sections` (free-form cover letter / company-overview prose, not
tied to a matrix row) has no per-section citations field, so the facts gate
structurally cannot check claims placed there. This is recorded in
`FORMATS.md` and `RUNBOOK.md` rather than papered over with an invented
citations field the spec never asked for; run-agents are instructed to keep
factual claims inside row `answer_text`, where they are actually checked.
The "eligibility row flagged failing" consistency check is also a documented
heuristic (a fixed failure-phrase vocabulary), not full language
understanding — the only way to check this without an LLM call, and
explicitly named as such in both `gates.py` and `RUNBOOK.md`.

## Phase 5 marking run (11 Sep 2026) — `code/mark.py`, the sole reader of the key

**Scope.** `code/mark.py` is the only script in this project ever permitted to
open `data/answer_key/`. It marks the frozen Arm A (64 attempts) and Arm B
(16 runs) artefacts mechanically against the answer key and writes
`data/analysis/marks.json` (full per-attempt/per-run detail) and
`data/analysis/report.md` (the marked report, verdict table, per-tender
A-vs-B table, trap-class table, gate false-block analysis, marking-quality
notes). Deterministic, one entry point, re-run twice with byte-identical
`marks.json` output. Neither arm's own artefacts were touched.

**Calibration, done before trusting the matcher** (see report.md "Marking-
quality notes" for the full account). Three real matching bugs were found
and fixed by hand-inspecting drafts against their computed marks, not
assumed away: (1) T05–T08's tender documents print their body clauses in
Finnish verbatim (unlike T01–T04/T09–T16's English clause text), which broke
document-text keyword extraction for every technical/commercial/format row
on those four tenders — fixed by keying a hand-translated bilingual keyword
gloss (`TOPIC_KEYWORDS_EN`) off the corpus's own fixed
`config.TECHNICAL_TOPICS`/`COMMERCIAL_TOPICS`/`FORMAT_TOPICS` banks (verified
to cover every non-trap requirement's `description` exactly) instead of
per-tender document extraction; (2) some Arm A drafts (e.g. `attempt_15_10`)
are written entirely in Finnish regardless of the source document's
language, closely echoing the topic-bank sentence as a heading — fixed by
adding each topic's own Finnish stems to its keyword list; (3) naive
substring keyword matching false-positived on Finnish's agglutinative
morphology (`vat` inside `vaadittavat`) — fixed with a left-side
(start-of-word) boundary, deliberately left open on the right so English/
Finnish plural and verb suffixes ('Spare parts', 'Subcontracting') still
match their stem. A remaining, disclosed detector limitation: 1 of 3
independent-fabrication-detector false positives is a comma-substring
collision (corpus value '450,000' found inside a legitimate, correctly-cited
'1,450,000'); the other 2 are the detector's capability-keyword list
colliding with T11's own buyer name ('Datakeskus' = data centre). None of
these are patched into the reused modules; all three are named in report.md.

**Headline numbers.** Arm B final coverage is 100% on 13 of 14 bid tenders,
92.86% on T03 — the ONLY three key requirements Arm B's extraction ever
misses, across all 16 tenders, are the three `hidden_form` traps themselves
(T03-R014, T09-R031, T14-R053), and both arms independently score 0/12 and
0/3 on that trap class: the trap built to be invisible was invisible to
humans and machine alike. Arm A per-tender medians run 60.7–93.3% (13/16
tenders inside the pre-registered 55–80% band; degrading-with-size does NOT
hold strictly — clean gnarly tender T16 (93.27% median) outscores several
trapped medium tenders, since trap presence, not size, drives difficulty).
Extraction recall is 90–100% (mean ~99.2%), exceeding the pre-registered
90–99% band on 13/16 tenders at exactly 100% — the anticipated "reported
design weakness" (design.md S7.6) if this happened. Fabrication: seeded in
22/64 (34.4%) Arm A attempts (>=25% floor MET), Arm B publishes zero
uncaught fabrications on all 16 terminal responses (confirmed by rerunning
`gates.py`'s facts gate on the final response AND an independent scan of
`general_sections`, the one place gates.py structurally cannot check).

**Gate false-block finding.** All 10 gate bounces across the 16 runs (on
T02, T08, T09, T16) are `consistency`/`CROSS_ROW_INCONSISTENCY`, and every
one is a MECHANICAL FALSE POSITIVE on inspection: a response row citing 2–3
fact paths and stating 2–3 correctly-matched numbers gets its numbers
cross-attributed to every citation path on that row (not paired to the
specific citation each supports), which reads as a contradiction to
`gates.py`'s consistency gate even though each individual number is right.
Verified independently against `company_facts.yaml` for every bounce, using
the response version each `gate_report_N.json` actually judged (not the
final, possibly-revised response). Satisfies design.md S7.5's "Arm B
produces at least one false block" — ten, zero genuine.

**FROZEN, published as written, never adjusted.** (1) Arm B coverage >=95%:
MET on 13/14 bid tenders, T03 at 92.86% (traced to the hidden_form
extraction miss above, not folded into a false pass). The two no-bid
tenders' own coverage (T11 100%, T15 13.73%) is reported separately, not
counted against this expectation, since their correct behaviour is
specifically to stop, not draft, once the eligibility failure is confirmed.
(2) The pre-registered "at most 1/8" Arm A no-bid tally is exceeded at 2/8
(both on T15, 0/4 on T11) — already recorded honestly at Phase 3 (see
"FROZEN pre-registration observation" above), re-confirmed here with no
change. (3) Arm A median-coverage-degrades-with-size does not hold strictly.
(4) Extraction recall exceeds the 90–99% band on most tenders (design's own
anticipated failure mode). (5) The corpus has no time dimension, so "Arm A
is faster on simple tenders" is UNMEASURABLE, stated as such rather than
assumed; prose quality is not measured, per design.md S7.5. Full verdict
table, numbers, and every deviation's explanation: `data/analysis/report.md`.

**Next**: Phase 6 (writeup, interactive page, case page + work.html +
shapes-page cross-link). Open items for Eva unchanged from the design gate.

## Writeup drafted (11 Sep 2026) — canonical, Eva read-through pending

**Status.** `writeup/tender_workflow_case_study.md` is written, in the main
loop by the writer agent (Opus), per Eva's standing instruction that this
file waits until all six phases are complete. It is the CANONICAL statement
of the case: the website case page, the interactive page and any training
material derive from it, not from `data/analysis/report.md` directly. **Eva's
read-through is pending** and is an open item alongside the interactive
page's look-and-feel.

**Authority rule applied.** `data/analysis/report.md` was treated as the sole
authority on every printed figure; each number in the writeup was checked
against it before printing. Three figures circulating in earlier prose
(including this log's own Phase 5 entry) did not survive that check and are
corrected in the writeup:

1. **"100% coverage on 13 of 14 bid tenders" is wrong.** Report.md's
   per-tender table gives exactly 100% on **11** of the 14 bid tenders; T03
   is 92.86%, T09 96.77%, T14 98.11%. The correct 13/14 claim is the
   *pre-registered ≥95% floor*, which 13 of 14 meet. The Phase 5 entry above
   conflated the two; the writeup states both separately.
2. **"Arm A per-tender medians run 60.7–93.3%" is wrong.** The lowest
   per-tender median in report.md is T12 at **64.29%**; 60.71% is an
   individual attempt (P10 on T12), not a median. The writeup prints
   64.3–93.3%.
3. **Extraction recall "~99.2%"** is the unweighted mean of the 16 per-tender
   recalls. Requirement-weighted, report.md's own table gives 507 matched of
   510 key requirements = **99.4%**, which is what the writeup prints, since
   the three misses are the point of the section and weighting by tender
   would obscure them.

Derived arithmetic printed in the writeup and not stated verbatim in
report.md: 537 matrix rows against 510 key requirements (sum of the Arm B
table's "Matrix rows" column — extraction over-produces rather than omits);
T15's stop at 7 answered rows of 53, with 46 listed as deliberately
undrafted (from `data/arm_b/run_15/signoff.json`); contradiction traps split
4 caught / 5 answered-but-unflagged / 3 missed (from `marks.json`, consistent
with report.md's 4/12 headline); the single missed annex_disqualifier being
Antti Salomaa on T13 (`marks.json`).

**Honesty decisions taken in the drafting.**

- **Arm A is stated as a simulation, in its own section and again in "what
  transfers".** Its coverage outcomes come from a seeded engagement model
  calibrated twice at population level, so the human arm's 0/12 on
  hidden_form *follows from* the mentioned-once penalty. Arm B's 0/3 on the
  same class does not follow from anything seeded — a model read the
  documents and built the matrix — which is why the writeup rests the crown
  finding on the Arm B side and says so explicitly.
- **The gates' coverage contribution is reported as unproven on this corpus**
  (0 percentage points on every bid tender, because extraction left nothing
  to recover), with the fabrication and consistency work reported as what the
  gates demonstrably did. This is design.md S7.6's anticipated weakness,
  printed as a weakness.
- **The ten false blocks are shown costing something**, using T02's
  limitation-of-liability row: the bounced draft cited both insurance figures
  correctly, the passing redraft dropped the €1,000,000 professional-indemnity
  figure and deferred it to negotiation.
- **Speed is stated as unmeasurable**, and the writeup notes that the hours in
  the shapes page's exemplum are labelled hypothetical and unaffected by this
  case. No pricing anywhere, per house rule.

**House-voice mechanics.** British English, spaced en-dashes, typographic
apostrophes and curly double quotes (matched to `03 Invoices/writeup/` by
inspection, then normalised with a one-off script — no shell heredoc, per the
CLAUDE.md rule). Provenance header line and the italic synthetic-data
disclaimer follow 03's convention. No website file, interactive folder or
other project was touched by this pass.

## Interactive page built (11 Sep 2026) — `interactive/tender-workflow.html`

**Built**: `interactive/build_data.py` + `interactive/_template.html` →
`interactive/_data.json` (839 KB) + `interactive/tender-workflow.html` (894 KB,
well under the 2 MB budget). Follows the 01 Churn pattern exactly: a
deterministic Python build step assembles one JSON blob from `data/` and
`code/config.py`, inlined into a hand-written template via a
`<script type="application/json" id="hpx-data">` placeholder (03 Invoices'
`code/verify_interactive.py` and 06 Anomaly Detection's
`code/verify_interactive.py` were the QA precedents). Single external
request (Google Fonts), `hpx-` prefix throughout (classes and ids), hand-rolled
SVG only, validated chart palette, `{type:"hpx-height", height:N}` postMessage
reporting. Re-running `python interactive/build_data.py` regenerates both
output files from `data/` and the writeup with no hand-editing.

**Structure: four views as an in-page tab switcher, not four scroll
sections.** No precedent page in the portfolio uses tabs (churn, 05, 06 are
single-scroll narratives with embedded widgets) — this is a new pattern for
the portfolio, chosen because this case's four views are each substantial
(a 16-tender pipeline walkthrough, a 64-attempt browser, a six-expectation
scoreboard, and a three-tender playable game) and a single scroll would bury
the game past an enormous amount of browsing content. All four views render
into the DOM at once (nothing lazy-loaded) and are shown/hidden with the
`[hidden]` attribute; only the active view's `init*View()` runs its one-time
setup, on first visit.

**No new external-facing prose.** Every narrative/argumentative sentence on
the page — the title, byline, lede, honesty framing, the four "worth reading
in full" persona vignettes, the T02/T11/T15 workflow exhibits' captions, and
all six scoreboard honest-negative callouts — is sliced verbatim out of
`writeup/tender_workflow_case_study.md` by `build_data.py`'s `quote()`
helper, which slices directly from the loaded file (never retyped) and
raises if a marker string is not found, so a mismatched apostrophe or dash
fails the build loudly rather than silently drifting from the source. Static
template copy is limited to functional/instructional labels (button text,
column headers, "tick the clauses you judge binding" style mechanics) —
several early drafts paraphrased the writer's own sentences (e.g. "no
operator to be good or bad at it") into UI copy; these were cut back to
plain mechanical descriptions and the actual sentence left to the adjacent
verbatim quote block instead, on review against this brief's own
instruction not to write new external-facing prose.

**Quick-play set: T04, T08, T11 — design.md §8's own example composition**
("one simple, one trapped medium, one no-bid"), matching Eva's committed
rules directly: T04 (simple, format_trap in the body, no annex trap), T08
(medium, the contradiction pair — one member in the body at 4.10, the other
in Liite B), T11 (medium, eligibility_fail at body clause 3.5 — Visakoivu's
one certification gap, ISO/IEC 27001). None of the three carries a
hidden_form trap, which matters mechanically: every clause in all three
source documents maps 1:1 to exactly one answer-key requirement (verified by
`build_data.py`'s own assertion and by `verify_interactive_07.py`), so
"tick the clauses you judge binding" is a clean, honest proxy for
requirement coverage with no distractor clauses to weight one way or the
other. The gnarly tenders were left out of the quick-play set (per §8,
"optional for the ambitious") purely on scope grounds for this pass — their
documents are already fully generated and could be added later without
touching the scoring core.

**The JS port's honesty boundary, documented in `quickplay_score.src.js`
itself.** The game's interaction (tick clauses, call bid/no-bid) cannot
reproduce `mark.py`'s free-text drafting checks, so three things are ported
*exactly* because they do not depend on drafted prose in `mark.py`'s own
logic either — coverage % (matched/total, identical arithmetic given
identical "addressed" inputs), the eligibility_fail trap (mark.py's own
`caught` is `bid_decision == "no-bid"` OR explicit text flagging; ticking
plays no part in mark.py's own condition, so the port is exact), and the
contradiction trap (mark.py requires both paired requirements addressed AND
explicit conflict-flagging language; the game asks the visitor directly,
once both members of a pair are ticked, "flag the conflict?" — an exact
port of the same two-part condition, substituting a direct question for
language mark.py would otherwise search for). The format_trap's `caught` is
scored as `ticked` — in `mark.py` this trap's own check is a text-compliance
check, not a bare "addressed" flag, but it is empirically identical to
"addressed" on every one of T04's four real Arm A attempts (the requirement
*is* "state the 11pt minimum", so noticing and stating it are the same
output), which is reported as an empirical equivalence, not assumed.

**JS-vs-Python agreement, run and passing.** `code/quickplay_agreement_check.js`
loads `interactive/quickplay_score.src.js` (the identical file inlined into
the built page — not a re-implementation) under Node and runs it over
fixtures built from `mark.py`'s own recorded per-requirement `addressed`
flags for the twelve real Arm A attempts on T04/T08/T11, comparing the
JS output's `coverage_pct` and per-trap `caught` against `mark.py`'s own
recorded values in `marks.json`. First run found a genuine bug, not a false
positive: two attempts (`attempt_08_02`, `attempt_08_05`) disagreed by
exactly 0.01 (JS 65.63/40.63 vs `mark.py` 65.62/40.62). Root cause: `mark.py`
computes `round(100.0 * n_addressed / len(matchers), 2)`, and Python's
`round()` is round-half-to-even on the true binary value, whereas
`Math.round()` always rounds halves up — both attempts' coverage landed on
an exact eighth (21/32 = 65.625, 13/32 = 40.625), a true tie that the two
languages broke differently. Fixed by porting a `pyRound2()` half-to-even
implementation into `quickplay_score.src.js` (matching Python's arithmetic
order, `100.0 * matched` before dividing, so the pre-rounding double is
bit-identical between the two languages) rather than loosening the QA
check. Final result: **12/12 attempts, exact agreement on `coverage_pct` and
every trap's `caught` value.** `code/verify_interactive_07.py` runs this
check every time and fails the gate if it ever regresses.

**QA**: `code/verify_interactive_07.py` (modelled on 06 Anomaly Detection's
`code/verify_interactive.py`) — single external request, `hpx-` prefix
discipline (classes and ids), balanced tags, page size, embedded-JSON parity
with `_data.json`, all sixteen tenders' and all six expectations' displayed
numbers re-checked against `data/analysis/marks.json` directly, the
JS-vs-Python agreement check above, and a page-wide (not just the game's)
scan for browser-storage APIs and network calls (`localStorage`,
`sessionStorage`, `indexedDB`, `document.cookie`, `fetch`, `XMLHttpRequest`,
`WebSocket`, `sendBeacon` — none present anywhere in the inline scripts).
One false positive surfaced and was fixed in the checker itself, not the
page: the SVG namespace literal `http://www.w3.org/2000/svg`, required by
every `document.createElementNS()` call for hand-rolled SVG, briefly tripped
the "no absolute URLs" scan; excepted by name, since it is never a network
request. **All checks pass.** `python code/validate_corpus.py`,
`validate_structure.py` and `validate_arm_a.py` were re-run after this pass
and are unaffected (all still pass) — nothing outside `interactive/` and
`code/quickplay_agreement_check.js` / `code/verify_interactive_07.py` was
touched.

**Not done in this pass, flagged rather than fudged**: the case page,
`work.html` and the shapes-page exemplum cross-link (§9 Phase 6's other
deliverables) are not part of this brief and remain open; the gnarly tenders
are not in the quick-play set (see above); Eva's look-and-feel pass on the
interactive page itself is still owed, per the portfolio's standing pattern
on every prior case's interactive page.
