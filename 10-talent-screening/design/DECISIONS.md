# Case 10 — decision log

Append-only. Deviations from the gated design are recorded here before any result
depending on them is reported.

## 2026-09-18 — Design gated

Eva gated `design.md` same day it was drafted: corpus 240, aggregate table
reader-sortable (the system still emits no order), remote-sensing domain, parity bar
≤ 2pp, persona arm and theme delegated (set: 12 personas / 48-application subset;
Theme 4). Pre-registrations §4 frozen at this gate: evidence recall ≥ 95%; invented
evidence < 1%; hidden gems ≥ 15/18; stuffers flagged ≥ 19/22; stratum parity ≤ 2pp;
with-dossier arm ≥ 2× hidden-gem detection at equal time.

Standing constraints carried from the same session: the system assists and never
decides (no ranking, no shortlist, no verdict anywhere in any output); all external
prose is written by the `writer` agent (Opus 4.6) after runs are marked.

## 2026-09-18 - Corpus prose to Opus 4.6; cover letters first-class

Eva, same day as the gate: the application prose (CVs and cover letters) is written by the external writer's model, Opus 4.6, via the application-writer agent - content strictly brief-controlled, prose left to the writer; and every application carries a substantive one-page cover letter per Finnish convention, with some planted evidence items letter-only. Config/briefs/validation updated mid-build (builder notified); the Hapax writing guide deliberately does not apply to corpus documents.

## 2026-09-18 — Phase 1 build (structure + briefs): decisions the design left open

Built `code/config.py`, `code/generate_structured.py`, `code/validate_structured.py`,
`code/split_briefs.py` against `design.md` and the task brief. Validation passes
clean (all archetype counts, displacement, contradiction, borderline, stuffer,
career-gap, orthogonality, and brief-integrity checks). The following calls were
not fully specified by the design doc and were made by the builder; flagging them
here per the portfolio's rule that material judgment calls go in this log.

**Company name.** Kaikuvaara Oy ("echo" + "fell/hill"), a fictional remote-sensing
instruments maker in Oulu. Follows the portfolio's existing naming convention (a
Finnish nature/landscape word plus a plain business suffix — Jalavakoski [02],
Pyokkipaja [03], Paju Consumer Products [05], Saarnitukku [06], Visakoivu [07])
and reads as thematically apt (echo → radar/sonar returns). Oulu chosen because
it is a genuine Finnish hub for wireless/photonics/space-systems engineering, so
the setting is grounded without naming a real employer. A quick web check at
build time found no company trading under this exact name. **Not yet
independently re-checked by a `scout` agent** — the task brief asked for that as
a separate step; still open.

**The 12 requirements, frozen.** Five must-have (R01 phased-array/beamforming,
R02 embedded DSP in C/C++, R03 production Python, R04 RF measurement
experience, R05 relevant degree or demonstrated equivalent), four desirable
(R06 Kalman/estimation theory, R07 satellite/airborne platform experience, R08
team-lead experience, R09 publications/open-source record), three constraints
(R10 EU work authorisation, R11 working English, R12 onsite in Oulu /
relocation). The design doc gave these as illustrative examples, not a frozen
list; this is the builder's concretisation.

**Desirable/constraint status profiles per archetype.** The design doc only
specifies must-have planting rules per archetype. For desirables and
constraints, every archetype except D and off-role uses a shared "otherwise
ordinary CV" profile (evidenced 35% / claimed-only 15% / not-stated 40% /
absent 10% for desirables; evidenced 85% / not-stated 15% for constraints,
independently drawn per requirement per candidate). D's desirables skew
claimed-only (70%), consistent with "claims everything." Off-role candidates
get a weak desirable profile and a distinct constraint profile (English still
plausible since the application itself is in English; EU authorisation/
relocation mostly not stated, since an off-role applicant hasn't tailored the
application). These profiles are config-level tunables
(`_STRONG_DESIRABLE_PROFILE` etc. in `config.py`), not hardcoded per candidate.

**E's two contradiction templates and their split.** The design doc says
"title/degree claims contradicted by dates or internal details" without
specifying mechanisms. Built two: (1) a degree-conferral-date contradiction
targeting R05 (a must-have), (2) a claimed-leadership-title contradiction
targeting R08 (a desirable). Split 8/7 across E's 15 candidates by a seeded
draw (came out 8 degree_date / 7 title_inflation). Note: because the second
template targets a desirable, not a must-have, roughly half of E's candidates
end up with all 5 must-haves genuinely evidenced (must_have_pass_count = 5)
and the other half with 4 (one must-have contradicted) — both are legitimate
readings of "credential inflation," but this wasn't obvious from the design
doc and is worth flagging.

**H's two borderline templates and their split.** Built two: (1) RF
measurement experience gained purely in an academic CubeSat/ground-station
project (targets R04), (2) phased-array experience from an unreviewed hobby
project (targets R01). Rotated across H's 12 candidates (came out 5/7). Each
carries a fixed `borderline_note` recording the "defensible either way"
judgment in the key, per the design's explicit requirement.

**F's displacement rotation and letter-only split — made exact, not
probabilistic.** F's 18 candidates rotate evenly across R01/R02/R03 (6 each,
the design doc's own three worked examples). Within each group of 6, the
letter-only split from the mid-build cover-letter spec update is hardcoded
exactly: 3 letter-only (cover_letter), 2 project_description, 1 work_history
— so "9 of 18 F candidates are letter-only" is a frozen number, not a
seed-dependent one that could drift on a config edit elsewhere.

**Career-gap arithmetic.** G's archetype forces career_gap = True for all 15
of its candidates (the archetype's defining story), which by itself would bias
the gap=True population toward "fully qualified." Compensated by also flagging
career_gap = True for a fixed count of candidates in the four lowest-truth
archetypes plus off-role (B 26, C 11, D 7, E 4, off-role 4 — chosen so the
gap-true population's "fully qualified" count is 15/67 ≈ 22.4%, matching the
overall population's 54/240 = 22.5%). A and F are deliberately gap-free (no
narrative reason for a gap); H is kept gap-free too, to avoid stacking two
designed ambiguities on one candidate. Result: fully-qualified rate differs by
0.16pp between gap=True and gap=False — well inside the 2pp parity bar, and
`validate_structured.py` checks this exact arithmetic by construction (not
just statistically), so a future edit to CAREER_GAP_COUNTS or the archetype
table that breaks the balance fails loudly.

**Orthogonality construction.** Implemented as an exact per-archetype
largest-remainder proportional allocation for name-origin, gender,
graduation-year band, and degree country (every archetype gets the same
global target proportions, so any archetype subset — hence qualification
truth, which is purely archetype-determined for the A/F/G "fully qualified"
set — carries the same demographic mix as the whole population, by
construction). `validate_structured.py` re-derives the same apportionment and
checks it matches exactly (self-defending against a future config edit),
*and* runs a chi-square test as the statistical backstop the design doc also
asked for. All four dimensions: chi2 p > 0.98, max pairwise spread < 2.4pp.

**Evidence-location baseline distribution.** Not specified by the design doc.
Set at work_history 45% / project_description 30% / skills_list 10% /
cover_letter 15% for ordinary evidenced items, drawn independently per item.
This is what lets letter-only evidence occur incidentally across every
archetype (not just F), including for constraints (e.g. "EU work
authorisation" stated only in the letter's opening line) — a realistic
pattern, not an error, though it means the raw per-archetype letter-only
counts are dominated by high-n, high-constraint-pass archetypes (B, C) rather
than by the narratively interesting ones (F, D). The F (displaced) and D
(claimed-only) mechanics have their own dedicated, higher letter-weighted
distributions layered on top, per Eva's spec update.

**Persona-arm parameters.** Design.md names "strictness, keyword-reliance,
time budget fixed" as example traits; built exactly those three
(strictness, keyword_reliance, time_discipline), 12 personas, seeded but not
yet wired into any simulation (that's Phase 2/3, per design.md S3's human
arm — not part of this phase's deliverables). The 48-application subset is
stratified proportionally across all 9 archetypes by largest-remainder
rounding of n_archetype × 0.2 (A4/B18/C7/D4/E3/F4/G3/H2/off-role3).

**Brief structure vs. "no answer-key statuses in machine-readable form."**
Briefs use operational instruction fields (`evidence_to_write`,
`claims_only`, `not_to_mention`, `contradiction`, `borderline`,
`cover_letter.evidence_in_letter` / `claims_in_letter`) rather than a
`status` field mirroring the key's five-value vocabulary. This is a
structural echo of the key by necessity — the writer has to know what to
write and what to omit — but no literal `"status": "evidenced"`-style field
appears anywhere in a brief; `validate_structured.py` checks this explicitly.

## 2026-09-18 - Degree-field resolution rule (Phase 2, corpus-wide)

Batch 02 surfaced a brief ambiguity: R05 in not_to_mention while the career skeleton names a relevant-sounding degree_field. Adopted rule, sent to every in-flight and future batch: degree_field is a category pool and not_to_mention wins - the writer draws an explicitly NON-relevant field (biomedical, mechanical, energy tech, materials, etc.); a relevant degree is never left visible-but-undiscussed, which would plant accidental R05 evidence. Phase-2-close QA will assert corpus-wide: every candidate whose key holds R05 absent/not-stated carries a non-relevant degree field in the written CV.

## 2026-09-18 - Phase-2-close QA checklist (running)

Items accumulated during batch production, to assert corpus-wide before any pipeline run: (1) every R05-absent/not-stated candidate carries a non-relevant degree field; (2) D-archetype R05 claims must read as vague/unsubstantiated, not as contradicted by the visible non-relevant degree - claimed-only and contradicted are different key statuses and D/E separation depends on it; (3) letter-only evidence items appear in letters only; (4) no not_to_mention item appears anywhere in its candidate documents.

## 2026-09-18 - Timeline bug: six briefs carried future dates

Briefs 005, 023, 043, 058, 112, 179 contained dates past the corpus present (2027 up to 2076) - unclamped date arithmetic in generate_structured.py, and the validator had no timeline-sanity rule. Found via batch 06 prose (C043 gap "2027-2028"). Fix in progress: generator clamped, validator gains a no-date-after-2026-09 rule plus monotonic-timeline check, briefs/batches regenerated. Prose already written or in flight against the buggy briefs (candidates 005, 023, 043, 058, 112) gets surgical rewrites against corrected briefs, hash-checked so only those candidates change (the 09-case precedent); brief 179 sits in an unlaunched batch and is fixed at source. QA checklist gains: no date later than September 2026 anywhere in the corpus.

**Root-cause split, on investigation: only 3 of the 6 flagged briefs had a real
date bug.** `build_career_skeleton`'s career-gap arithmetic
(`gap_start = grad_year + 3`, unclamped) overran `CORPUS_NOW_YEAR` only for
candidates who graduated in 2023 or 2024 (the top of the `2019_2024` band):
**C023** (gap 2026-2027 -> fixed to 2025-2026), **C043** (2027-2028 ->
2025-2026), **C058** (2027-2028 -> 2025-2026). The other three flagged
numbers were false positives from a naive "any 4-digit number" scan: 2039
(C005), 2047 (C112), and 2076 (C179) are all `style_seed` values (range
1000-9999), not dates — C005 and C112's actual career-gap years (2019-2020)
were always fine, and C179 has `career_gap = False` and no gap entry at all.
Left `STYLE_SEED_RANGE` as-is rather than widening it to dodge the visual
collision, since that would have changed every candidate's style seed for a
cosmetic reason; instead scoped `validate_structured.py`'s new `check_dates()`
to genuine date fields only (`graduation_year`,
`career_skeleton[].start_year/end_year`), which structurally can't confuse a
style seed for a date again.

Fix: `config.CORPUS_NOW_YEAR = 2026` (plus a config-level assertion no
graduation-year band can extend past it); `build_career_skeleton`'s gap
formula changed to `gap_end = min(grad_year + 4, CORPUS_NOW_YEAR)`,
`gap_start = max(gap_end - 1, grad_year + 1)` (floored at the year the first
job starts); a defensive assertion added on the primary work-history start
year too. `validate_structured.py` gained `check_dates()`: no field exceeds
`CORPUS_NOW_YEAR`, and every candidate's `career_skeleton` is internally
ordered (per-entry start <= end; non-decreasing start year across entries).
Regenerated `generate_structured.py` and `split_briefs.py` outputs;
validation passes clean including the new checks.

**Confirmed scope of the diff.** Direct before/after arithmetic across all
240 candidates confirms exactly 3 brief files changed —
`brief_023.json`, `brief_043.json`, `brief_058.json` (batches 03/06/08) —
and nothing else. The fix only touches `build_career_skeleton`, which feeds
`data/briefs/`, not `build_answer_key`/`build_candidate_summary`, which feed
the CSVs; `answer_key.csv` and `answer_key_candidates.csv` are confirmed
byte-for-byte unaffected (spot-checked all 6 originally-flagged candidates'
archetype/graduation_year/grad_year_band/career_gap/career_gap_reason before
and after — identical; archetype totals unchanged). No candidate's
`graduation_year` or `grad_year_band` moved, so the orthogonality table was
re-run and is numerically identical to the pre-fix run (all four dimensions:
chi2 p > 0.98, max pairwise spread < 2.4pp). `data/applications_raw/` was
not touched by any of this — none of the regeneration scripts write there.

## 2026-09-18 - Name collisions: seven duplicate full names

Name pools were drawn without a uniqueness constraint: 233 unique names across 240 candidates (7 pairs). Fix is surgical, never a re-draw (a reshuffled assignment would rename candidates in batches already written): in six pairs the unwritten member is renamed at brief level (161, 188, 190, 192, 219, 232 - surname swap within the same name-origin pool, first name kept); the Emma Petrov pair had both members written, so brief_104/C104 is renamed with its batch-13 prose patched, other entries byte-checked identical. Generator gains uniqueness enforcement, validator gains an all-names-unique rule. Found via batch 13 report (C104 duplicating C015).

**Executed via `code/fix_duplicate_names.py`** (one-off repair script, kept in
the tree per the churn-case convention for this kind of surgical fix — see
its own docstring). Surname redrawn deterministically per candidate
(`deterministic_rng("manual_rename_fix_v1", candidate_id)`), from the
candidate's own `name_origin` pool, excluding the current surname, rejecting
any candidate surname that would produce a full name already used anywhere
in the 240-candidate corpus (checked incrementally, so the 7 new names also
can't collide with each other):

| Candidate | Old name | New name |
|---|---|---|
| C104 | Emma Petrov | Emma Popescu |
| C161 | Sanne Rossi | Sanne Kovac |
| C188 | Jussi Hamalainen | Jussi Nieminen |
| C190 | Jan Dubois | Jan Popescu |
| C192 | Aleksi Koskinen | Aleksi Makela |
| C219 | Hannu Salo | Hannu Lehtonen |
| C232 | Marko Saarinen | Marko Turunen |

(C104 and C190 both landing on the surname "Popescu" is not a second
collision — the full names "Emma Popescu" and "Jan Popescu" are distinct;
uniqueness is checked on the full name, not the surname alone.)

**Files touched**: the 7 `data/briefs/brief_NNN.json` files; their embedded
copies in `data/brief_batches/batch_13.json`, `batch_21.json`,
`batch_24.json` (three: 188/190/192), `batch_28.json`, `batch_29.json`; the
corresponding 7 rows' `full_name` in `data/answer_key_candidates.csv`
(confirmed no other row or column changed, by an explicit before/after
diff inside the script); and `data/applications_raw/batch_13.json`'s C104
entry only (2 occurrences of "Petrov" replaced in `cv_markdown`, 1 in
`cover_letter_markdown` — the CV header, the invented email address
`emma.petrov@...` -> `emma.popescu@...`, and the letter's closing
signature — 0 remaining afterward; the other 7 entries in that batch file
confirmed byte-identical before/after via a JSON equality check).
`data/applications_raw/batch_02.json`'s C015 ("Emma Petrov") confirmed
untouched. `answer_key.csv` (the per-requirement key) carries no name field
at all, so nothing to patch there.

**Generator/validator hardening**: `generate_structured.py` gained
`enforce_full_name_uniqueness()` (walks candidates in `candidate_id` order;
the first holder of a name keeps it, every later duplicate gets a freshly
redrawn surname from the same deterministic-RNG mechanism, iterated until
collision-free) — unit-tested against a synthetic 4-row frame, not run
against the live corpus (this was a surgical fix, not a regeneration, so
the generator change is a safeguard for the future, not something exercised
now). `validate_structured.py` gained `check_name_uniqueness()`: all 240
full names distinct.

**Validator output after the fix**: `python code/validate_structured.py` —
`=== name uniqueness ===` / `[ok] all 240 candidate full names are unique
(got 0 duplicated names: {})`; full run exits 0, zero `[FAIL]` lines across
every check (archetype counts, displacement, contradictions, borderline,
stuffers, career-gap, orthogonality, brief integrity, dates, name
uniqueness, persona subset).

## 2026-09-18 - QA item: C148 degree field

Batch 19 gave stuffer C148 "MSc Software Engineering, LUT" as the non-relevant degree. Batch 06 set the precedent the other way (C045 changed FROM Software Engineering because it reads relevant-adjacent). Software Engineering plausibly half-supports R05 and definitely colours R03; with C148 R05 claimed-only, the visible degree muddies claimed-only vs evidenced. QA sweep to judge in context and, if needed, surgically swap the degree to a clearly non-relevant field (the C043-style single-candidate repair).
 (also add C198 "Information Processing Science" to the C148 degree-ambiguity QA item - same judgment call, same possible surgical swap)
 (and C218: visible degree "MSc Electronic and Information Engineering" for an R05-claims-only stuffer - the strongest of the three ambiguity cases, since electronic engineering plausibly EVIDENCES R05 outright; QA sweep likely swaps this one)

## 2026-09-18 - Corpus QA triage (first full sweep, 232/240 loaded)

Four findings, four different resolutions:
1. Future dates (C025, C121, C169, C192): all four are PROSPECTIVE statements - planned relocation, permit validity, availability from January 2027. Legitimate in letters written September 2026; the no-future-dates rule governs career HISTORY only. QA check 2 refined to treat forward-looking statements as WARN-with-context; no corpus change.
2. Diacritics (C091, C092): writers "corrected" Hamalainen/Paivi to proper Finnish spellings, diverging from brief and key. Corpus convention is the ASCII name pools (a known, harmless realism constant); the two outliers are patched back to brief spelling so prose always matches the key.
3. Degree rule extended (9 FAIL + 3 WARN): the standing rule covered R05 in not_to_mention; it must equally cover R05 CLAIMED-ONLY for every archetype - a visible relevant degree is de facto evidence and contradicts the key. C028, C060, C148, C175, C198, C218, C227, C228, C233, C234, C235, C236 get surgical degree swaps to clearly non-relevant fields (single-candidate fix-file pattern).
4. R05 letter-only design clarification (13 flags, no fix): a genuinely qualified candidate's CV shows a bare degree line in education regardless of where the brief placed the substantive R05 write-up; the key's location field refers to the write-up. The marking script must accept a citation of either. Frozen as a design interpretation, not a corpus defect; QA check 6 downgrades this pattern to informational for R05 only.

## 2026-09-18 - Phase 2 complete: corpus written and QA green

All 30 batches written (240 applications, CV + cover letter each) by the application-writer on Opus 4.6 under brief discipline. Full qa_corpus.py sweep: 0 FAIL across all seven checks; 504 WARNs reviewed as innocent context (employer-name keyword hits, prospective dates, generic-keyword letter checks); 13 INFO frozen design interpretations (R05 bare-degree-line). Defects found and fixed along the way, all at source or by hash-verified surgical repair: 3 future-dated career gaps (generator clamp + validator rule), 7 duplicate names (renames + uniqueness rule), 2 diacritic deviations, 12 claimed-only degree violations (rule extended to all archetypes). Production survived 3 output-limit failures (split-file protocol now standard) and a session rate-limit window (salvage + relaunch, zero lost candidates).

## 2026-09-18 - Phase 3 harness built (code only, no LLM runs)

Built `code/build_extraction_tasks.py`, `code/assemble_dossiers.py`,
`code/validate_dossiers.py`, `code/persona_arm.py` against design.md S3-S5.
No LLM calls made; no script here reads `data/answer_key.csv` or
`data/answer_key_candidates.csv` except the documented-but-unimplemented
`persona_arm.score_persona_response` stub. `build_extraction_tasks.py` ran
end-to-end on the real 240-candidate corpus (240 task files, 30 batches of
8, self-validation clean); `validate_dossiers.py` and the assisted arm of
`persona_arm.py` were exercised against synthetic fixtures only, since
`data/extraction_raw/` and `data/dossiers/` don't exist until the
separately-gated extraction run happens. Judgment calls made that the design
doc left open, flagged per the portfolio's rule:

**Persona-arm time budget.** Design.md S3 says "time budget fixed" without
a number (distinct from S6's game-mode "90 seconds each", which is a
reader-experience parameter for the published explorer, not a corpus/
simulation one). Set `config.PERSONA_ARM_TIME_BUDGET_SECONDS = 240` (4
minutes per application), identical across all 12 personas and both arms --
`time_discipline` is what already varies how well each persona is modelled
to use that fixed budget, so the budget itself should not also vary.

**Persona-arm response contract.** Design.md doesn't specify what a
simulated recruiter should return. Documented (not enforced -- Phase 4/5
builds the actual scorer) a `PERSONA_RESPONSE_CONTRACT` in `persona_arm.py`:
per-requirement `believed_status` in the answer key's own five-value
vocabulary (a human recruiter isn't bound to the extraction workflow's
four-value refuse-to-guess vocabulary), plus four flag lists
(`vocabulary_notes`, `claims_questioned`, `inconsistencies_noted`,
`borderline_calls`) chosen to map directly onto pre-registrations 3/4/5/6,
plus a real `screening_decision` -- the one place in the pipeline where a
verdict is correct, since design.md S1's no-verdict rule binds the
extraction workflow, not the human recruiter it assists.

**Extraction contract's status vocabulary is narrower than the key's on
purpose.** The key records five statuses (evidenced / claimed_only /
contradicted / absent / not_stated); the extraction contract in
`build_extraction_tasks.py` uses four (evidence_found / claim_only /
contradiction / not_stated), dropping `absent`. An extraction step reading
only the application text has no way to distinguish "not mentioned because
truly absent" from "not mentioned because the writer didn't get to it" --
collapsing both into `not_stated` is the refuse-to-guess gate itself, not an
omission.

**R05 either-citation-location rule, carried forward.** Per the QA triage
entry above (R05 letter-only design clarification), `assemble_dossiers.py`'s
citation check verifies a quote against whichever document (CV or cover
letter) the extraction response actually tags as its source -- it does not
require the citation to land in any particular one of the two for R05 or
any other requirement. The design's "either location is acceptable for
R05" rule is therefore satisfied structurally: nothing in this harness
forces a specific location per requirement, so an extraction agent citing
R05 from the CV's bare education line is verified exactly the same way as
one citing it from a letter write-up.

**Coverage-table columns.** Design.md says "count of must-haves with
evidence_found, desirables, constraints, flags, asks" without naming exact
column headers. `data/coverage_table.csv` (once populated) carries:
`must_have_evidence_found`, `must_have_claim_only`, `must_have_contradiction`,
`must_have_not_stated`, `desirable_evidence_found`, `constraint_evidence_found`,
`flags` (count of `contradiction` statuses across all 12 requirements), and
`asks` (length of `ask_in_screening`) -- one row per candidate, in
application order (C001..C240), never sorted.

**Banned-word list for the no-verdict check.** Design.md states the
constraint ("no ranking, no shortlist, no reject pile, no verdict") but not
a word list. `validate_dossiers.py` defines `BANNED_PHRASES` locally
(recommend, reject, shortlist, rank, top/best/worst candidate, good/poor/bad
fit, hire language, suitable/unsuitable, advance/screen-out/pass-on
language), matched case-insensitively with word boundaries, scanned
recursively across every string field in an assembled dossier. Not
exhaustive by construction -- flagged here so a future addition to the list
is a deliberate edit, not a silent gap.

## 2026-09-18 - Extraction-contract leak caught and fixed pre-run

The Phase-3 harness's refuse-to-guess rule illustrated itself with "automotive radar has NOT thereby evidenced phased-array" - automotive FMCW radar being one of the corpus's actual F-archetype displacement vocabularies. Key-side trap knowledge in the pipeline, suppressive direction: it would have primed the extractor against the exact hidden-gem test pre-registration 3 measures, and either outcome could be called tuned. Replaced with a title-inference example (Senior RF Engineer title does not evidence RF measurement work) plus an explicitly direction-neutral note that adjacent-vocabulary substance is quoted and left to the recruiter. Tasks and batches regenerated; contract scanned clean against the full displacement vocabulary list. The contradiction illustrations (degree-date clash, title-vs-role) were reviewed and kept: canonical CV-fraud patterns any blind contract author would name, no planted domain specifics.
 Addendum: post-fix scan of all 240 regenerated tasks found one remaining displacement-list term outside application text - "sonar" in R01's own frozen description ("e.g. for radar, sonar, or comms arrays"). Ruled legitimate: Phase-1 requirement wording, predates extraction design, identical for the workflow and the persona arms, and consistent with the key counting sonar beamforming as true R01 skill. The displacement table itself is confirmed absent from every task (requirement blocks carry only id/category/name/description).

## 2026-09-18 - Extraction run launched (Eva: "Go for it")

Phase 3b extraction runs on Sonnet: mechanical extraction per the house model-routing rule, and deliberately so for the case's argument - the workflow's discipline (refuse-to-guess, verbatim citations, no verdicts) is what is under test, not maximal model quality; measured subagent token totals per batch are recorded for the published cost band (same method as the ERP case: list prices applied to measured totals, input/output split assumed as a band). Extractors read exactly one batch file each - the isolation rule is in every prompt; briefs and keys are untouchable. 30 batches, waves of 8.

## 2026-09-18 - C022 extraction contradiction: corpus verified clean, output stands

The batch-03 extractor recorded an R12 contradiction for C022 (Oulu tenure 2011 vs "facility opened 2015-2017"). Checked against the prose: the CV places her at Baltic Sensor Networks Oulu from 2011 and separately credits her with participating in ESTABLISHING the company's Oulu satellite data processing centre 2015-2017 - an additional facility, not the site's founding; no contradiction in the text, and the extractor's "since it opened" phrasing appears nowhere in the documents. The output is NOT corrected: extractor errors are measurement, the non-verbatim quote will surface in the citation-verification pass (pre-registration 2's machinery), and the false-positive contradiction is marked against the key like any other call.

## 2026-09-18 - C039 extraction contradiction: an invented quote, kept as data

The batch-05 extractor reported an R07 contradiction for C039 quoting a beamformer "flight-tested on the first flight". The corpus contains no such text - every flight/airborne-adjacent line in C039's documents says ground-based, per the brief (R07 in not_to_mention, honoured). This is fabricated evidence by the extraction step: precisely the failure pre-registration 2 (<1% invented evidence) exists to measure, and the assembly-time verbatim-citation check will catch it mechanically. Output stands untouched. Running pattern worth the writeup's attention: both suspicious extractor calls so far (C022, C039) are hallucinated contradictions, not missed ones.

## 2026-09-18 - C079: real corpus inconsistency, frozen for adjudication

The letter attributes the towed-array beamspace algorithm to a 2019 JASA publication; the CV's only 2019 JASA paper is "Efficient Frequency-Domain Coherence Estimation for Passive Acoustic Monitoring" - one publication, two identities, an accidental writer inconsistency the QA keyword sweeps could not see. Discovered AFTER extraction ran on batch 10, so it is NOT repaired: post-run corpus edits plus selective re-extraction would be re-measurement (the contracts-case precedent governs - defects found after the run are adjudicated and published, not fixed). The extractor's R01 contradiction call is a defensible reading; at marking this key row goes to adjudication, and the writeup can honestly note that flagging a publication inconsistency on an otherwise-strong candidate is the dossier doing its job.

## 2026-09-18 - Baseline arms gated; extraction run complete; validator scan fix

Eva gated the four-arm comparison (design.md S8a): ATS keyword baseline, naive Haiku, disciplined Haiku (the workflow contract on the same small model - the arm that isolates discipline from parameter count), full workflow. Four addendum pre-registrations A1-A4 frozen, including the falsifiable hero claim (disciplined small model beats the ATS on gems surfaced AND stuffers identified).

Same day: all 30 extraction batches complete; 240 dossiers assembled; citation verification 19 failures in 2,116 quoted lines (0.90%, under pre-reg 2's 1% bar pending the marking-phase classification of failures into fabrication vs transcription slippage); coverage table written unsorted. validate_dossiers.py's banned-vocabulary scan produced 13 false positives on radar terminology ("interference rejection", "clutter rejection") inside verbatim corpus quotes - fixed by exempting quote fields (the no-verdict rule binds the dossier's voice, not the candidate's words) and requiring candidate/application context for the reject/rank stems in authored fields. Post-fix: all structural checks pass, zero verdict-language hits.

## 2026-09-18 - Baseline-arms harness built (arm 1 run, arms 2/3 batches built, no LLM calls)

Built `code/ats_baseline.py` (arm 1), `code/build_naive_tasks.py` (arm 2),
`code/build_disciplined_tasks.py` (arm 3), `code/validate_baselines.py`
against design.md S8a. Ran `ats_baseline.py` end-to-end on the real 240-
candidate corpus (both full-text and CV-only variants) and built the arm 2/3
task batches; `validate_baselines.py` is green. No LLM calls made for arms 2
or 3 — those Haiku runs are launched separately, per the task brief.
Judgment calls, flagged per the portfolio's rule:

**ATS scoring scheme.** Design.md S8a specifies must-have/desirable weighting
but not the exact mechanism. Adopted: binary per-requirement hit flag (any
synonym present as a case-insensitive substring anywhere in the scored text,
multiple hits count once), weighted sum (must-have x3, desirable x2,
constraint x1). Plain substring matching rather than word-boundary regex --
a deliberate modelling choice, since real keyword-matching ATSes are
frequently this blunt, and the exhibit's point is a realistically naive
baseline, not a generous one.

**Rank tie-break.** Design.md doesn't specify one. Adopted: score
descending, then candidate_id ascending, ranks 1..240 assigned in that exact
order -- fully deterministic, no random draw. `validate_baselines.py`
independently re-derives this sort and checks it matches, so a future change
to the scoring/sort logic that reintroduced non-deterministic ties would be
caught.

**Synonym lists built from requirement text plus generic ATS vocabulary,
never the displacement table.** `ats_baseline.SYNONYM_TABLE` includes plain
generic terms that happen to appear inside some displacement-table phrases
(e.g. "beamforming" is the generic keyword for R01, and 3 of the R01
displacement table's 4 phrases contain the literal word "beamforming"; "DSP"
similarly). This was a deliberate choice, not an oversight: a real ATS
vendor would obviously ship "beamforming" as an R01 keyword, and avoiding it
specifically because it happens to overlap with the corpus's displacement
phrasing would itself be a form of key-side tuning, in the opposite
direction from the one the self-check assertion guards against. The
consequence is that pre-registration A2 (ATS surfaces the displaced skill
for at most 3 of 18 hidden gems) is a genuinely live, unforced test rather
than one rigged to pass or fail -- whichever way the marking script's count
comes out should be published as measured, per the standing "whichever fail
are frozen, diagnosed and published" rule.

**Arm 3's "output path instructions" difference from arm 4.** Design.md
S8a says arm 3 uses the workflow's own extraction contract, differing from
arm 4 "only in output path instructions". Implemented as two additional
top-level batch fields (`output_path`, pointing at `data/disciplined_raw/`,
and a `note` explaining the arm-isolation purpose) alongside an `arm` label;
`requirements`, `application`, and `output_contract` are imported directly
from `build_extraction_tasks.py` and confirmed byte-identical to the
matching `data/extraction_batches/` file by `validate_baselines.py`'s
sibling-batch comparison in `build_disciplined_tasks.py`'s own
self-validation.

**Arm 1 score distribution (full-text variant, informational, not a
pre-registration check -- this script never reads the answer key).**
n=240, mean 14.81, std 6.05, median 16.0, range 0-26 (max possible score is
5x3 + 4x2 + 3x1 = 26). CV-only sensitivity variant: mean 11.79, std 5.46,
median 12.0, range 0-21 -- every candidate's CV-only score is <= their
full-text score, as expected, since the letter can only add hits.

## 2026-09-18 - Writeup requirement: further-work paragraph on local fine-tuning

Eva: the writeup closes with a short exploration of fine-tuning local models for a client - recruitment's data-protection and human-oversight rules make on-prem local models the natural shape, so this is the genuine case where Hapax might fine-tune a local LLM for a customer. Spec added to design.md S7: clearly marked as not done in this case, no capability promises, human-decides restated. The case's measured claim stays "set up and customised beats off the shelf"; fine-tuning is the motivated hypothesis.

## 2026-09-18 - Page requirement: lead with the matched pair

Eva: the case page opens on two standout exhibits before anything aggregate - the missed star (gem ranked near-bottom by the ATS, fully qualified per key) and the false positive (stuffer at or near the ATS top, claims unsubstantiated per key), with the rest of the 240 browsable below. Selection rule frozen: the pair is chosen from the MARKED results by largest key-verified rank-vs-truth gap, never hand-picked before marking. Spec added to design.md S6.

## 2026-09-18 - Phase 4 marked: results frozen as ran

All four arms marked (code/mark_results.py, the only key-reading script; outputs data/analysis/marking.json + report.md). Pre-registrations: 1 MET (recall 96.71%), 2 MET (fabrications 2/2,116 = 0.09%; 17 of 19 citation failures were transcription slippage), 3 NOT MET (gems 12/18), 4 MET (stuffers 19/22, on the bar), 5 NOT MET (grad-year-band spread 2.88pp, degree-country 2.48pp; other strata within 2pp), 6 pending persona runs. Addendum: A1 MET (ATS ranked 22/22 stuffers above median, rank 1 a stuffer), A2 NOT MET (ATS keyword flags hit 15/18 gems while ranking the star C213 at 144/240 - the registration measured hit-flags where the harm is ranking; published as mis-registered), A3 NOT MET inverted (disciplined-Haiku citation failures 16.53% vs naive 2.59% vs Sonnet 0.90% - Haiku merges lines into non-verbatim quotes; status discipline transfers to the small model, verbatim citation does not, and assembly-time verification caught every failure), A4 NOT MET (stuffer half won 20/22 vs ATS 0/22; gem half 13/18 does not beat the ATS keyword artifact). Contradictions: arm 4 caught 14/15 planted inflations, arm 3 1/15, naive 0/15. Matched pair selected by the frozen rule: C213 (star, ATS rank 144) and C228 (stuffer, ATS rank 1; arm 4 itself over-credited her R05 - kept in the exhibit). 12-item adjudication list open. Nothing retuned; failures publish as they ran.

## 18 Sep 2026 — persona run P05-assisted: procedural restart (no output lost)

The first P05-assisted agent, instead of reading its task file directly, spawned four summariser subagents to compress the applications and dossiers into per-candidate digests, then ended without writing any output. A digest layer between the material and the persona would make the run non-comparable with the other 23 (the persona must screen the material itself, and compression could systematically help or hurt either arm). The summarisers were stopped, no screening output existed, and the run was relaunched cleanly with an explicit rule: the persona agent reads its one task file itself in chunks, never delegates reading or summarisation. The same rule is added to every remaining persona launch (P07–P12). This is a pre-output procedural restart in the batch-26 mould, not a fix-and-rerun of a result.

Follow-up, same day: the stopped first P05-assisted agent later resumed on its one surviving summariser and did write a digest-mediated output to data/persona_raw/assisted/persona_P05.json. That file was moved out of the tree (session scratchpad, marked INVALID) without being read into any result; the clean rerun writes the canonical file. The as-ran P05-assisted result is the rerun's, only.

## 18 Sep 2026 — pre-registration 6: operationalisation frozen before marking

Fixed now, before any persona output is marked, so the definition cannot drift toward the data. A persona "identifies" a hidden gem when its screening_decision for that candidate parses as ADVANCE; holds are reported separately but do not count as identification (a gem parked on hold was not recognised as a star). The pre-reg-6 test: total gems advanced across all 12 personas in the assisted arm >= 2 x the same total in the unaided arm, over the archetype-F candidates present in the 48-application subset per the key; time budget equal by construction (240 s both arms). Decision parsing is mechanical: leading advance/hold/decline token, case-insensitive; any screening_decision that does not parse goes on the adjudication list and is never guessed. Secondary diagnostics reported but NOT pre-registered: stuffers questioned, inflations spotted, borderlines flagged as borderline, per design section 3, each defined against the key's archetypes. Marking runs only when all 24 outputs are on disk (--require-complete).

## 18 Sep 2026 — P07-assisted decision-vocabulary drift: adjudicated mapping drafted BEFORE mapped totals computed

The P07-assisted output uses Yes / No / Maybe (and one "want to flag before deciding" variant) for screening_decision instead of the contracted advance / hold / decline; all 48 entries correctly landed on the decision-parse adjudication list rather than being guessed. The run is kept as-ran (the judgments are legitimate; only the label vocabulary drifted — no fix-and-rerun, per the case-04 precedent). Drafted mapping, logged here before anyone computes what it does to any total, pending Eva's sign-off with the rest of the adjudication list: Yes -> advance; No -> decline; Maybe and any flag-before-deciding variant -> hold. The final report must show pre-registration 6 both with the mapping applied and with P07-assisted left unparsed, so the verdict cannot hinge silently on the mapping.

## 18 Sep 2026 — persona experiment complete: pre-registration 6 NOT MET, frozen as ran

All 24 runs (12 personas x 2 arms) on disk and validated; python code/mark_results.py --require-complete exits 0. The subset carries 4 archetype-F hidden gems (C011, C044, C185, C230), so each arm has a maximum of 48 gem-advances (12 personas x 4). Result: unaided 31/48, assisted 41/48, ratio 1.32 with the logged P07 mapping applied; 31 vs 37, ratio 1.19, with P07-assisted excluded (sensitivity variant). The registered bar was 2.0x -> NOT MET on both variants. Diagnosis, recorded at freeze: a ceiling effect the registration did not anticipate — the moment the unaided arm cleared 24/48, doubling became arithmetically impossible, and these personas found gems unaided at 65%. The dossier's real, measured effects sat elsewhere: gem HOLDS fell 15 -> 7 (holds converted to advances); stuffers questioned rose 75.0% -> 91.7%; inflations spotted rose 55.6% -> 94.4%; and borderlines flagged as borderline INVERTED, 33.3% -> 8.3% — with the dossier, personas resolved the engineered defensible-either-way candidates into firm decisions instead of flagging them, the one measured place assistance reduced appropriate hesitation. Decision totals: unaided 213 advance / 88 hold / 275 decline; assisted 250 / 75 / 251; zero unparsed decisions after the P07 mapping (48 adjudicated-mapped entries listed in the report, sign-off pending). Frozen as ran; no reruns.

## 18 Sep 2026 — adjudication signed off (Eva: "go for it")

All 13 draft verdicts in design/adjudication-drafts.md accepted as drafted: 2 extractor fabrications stand as measurement (C022, C039); 6 over-reads, key stands (C076, C114, C198, C234, C235, C236); 3 corpus defects published as ours (C079, C196, C197); C232 published as the design-level entanglement finding; the P07-assisted Yes/No/Maybe mapping confirmed. The aggregate observation (every disputed call errs toward over-suspicion, cost concentrated on letter-only plantings) is cleared for the writeup. Phase 5 (writer) begins.

## 19 Sep 2026 — Phase 5 complete: writeup, explorer, site integration

writeup/talent_screening_case_study.md written by the writer (Opus 4.6) from the frozen results; one factual correction in review (C232 pronoun — Marko Turunen). interactive/ built on the 07/09 pattern (build_data.py -> _data.json 1.78 MB -> talent-screening.html 1.83 MB, self-contained, browser-verified); the answer-key read in build_data.py is display packaging post-marking, logged in its docstring. Writer strings pass done in the template and rebuilt. Site: case-talent-screening.html + explorer-talent-screening.html (three logged divergences + noindex), work.html ninth entry in the People group, eight -> nine count sweep across work/notes/shapes/index/answer-key/training, sitemap updated, _verify.py ALL CHECKS PASSED. README.md written as the canonical internal record. Open items for Eva: writeup read-through, interactive look-and-feel pass.

## 6 Oct 2026 – Invented names renamed after the legal check

Spec: `Set Up/Legal/invented-names-check-2026-10-06.md` section 3; replacements were cleared against the registers and approved by Eva ("happy for things to get renamed without me, they're all fictional names"). Mapping and tooling: `Set Up/Legal/rename_mapping.py`, `apply_renames.py`, `rename_sweep.py`. 
- **Employer.** Arctic Space Systems is now Hallaharju Space Systems, and the short forms "Arctic's" and "Arctic’s" (239) are now "Hallaharju's" and "Hallaharju’s" in `code/config.py` (`SIGNAL_PROCESSING_EMPLOYERS`), the answer key, briefs, applications, extraction, naive, disciplined and persona batches and outputs, dossiers and the interactive files. Bare "Arctic" (the company's own short form in running CV prose, plus unrelated uses such as the Arctic Sensors Workshop, ArcticWatch and the Arctic-3 positioning system) was not touched; the spec lists only the possessive forms. Flagged for the writer to decide whether bare "Arctic" as a nickname for the employer should follow.
- **Optocap Ltd** is now Lochvane Photonics Ltd (one CV).
- **Hamamatsu.** "Hamamatsu Photonics (Japan)" (13 occurrences in the raw files, one CV) is now "a Japanese photodetector manufacturer". The sentence reads "Served as English-language technical liaison for Norlight's partnership with a Japanese photodetector manufacturer since 2015"; flagged for the writer to check the grammar wherever it is shown.
- All by literal swap into session data (application-writer, extraction, naive, disciplined and persona outputs); nothing re-run.
- **Checks.** `generate_structured.py`, `validate_structured.py`, `assemble_dossiers.py`, `validate_dossiers.py`, `ats_baseline.py`, `validate_baselines.py`, `mark_results.py` and `qa_corpus.py` re-run on scratch copies: all pass, and `data/analysis/marking.json` and `report.md` are byte-identical. No published figure moved. (`qa_corpus_report.txt` quotes one snippet with a lower-cased name, patched by hand to match.)
