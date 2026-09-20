# Adjudication drafts — case 10

**DRAFT verdicts pending Eva's sign-off. Nothing here changes any result file; per the
contracts-case precedent, outputs stand as ran and adjudication decides only how each
item is classified and published.** Scope: the twelve arm-4 `contradiction` calls that
do not match a planted E-contradiction (marking report, adjudication list), plus the
P07-assisted decision-vocabulary mapping. Sources read for each item: the marking
report entry, the assembled dossier, the candidate's application text in
`data/applications_raw/`, and the answer-key row for the disputed pair.

Verdict vocabulary: *extractor error, stands as measurement* (the call was wrong
against the text; it stays in the results as a measured failure) · *extractor
over-read, stands as measurement* (the texts are reconcilable; the call chose the
harsher status) · *defensible extraction* (a careful human could make the same call)
· *corpus defect, published* (the applications themselves are inconsistent; found
after the run, so published rather than repaired).

---

## 1. C022 / R12 — key `evidenced` (archetype H)

**Flagged:** contradiction between "Baltic Sensor Networks, Oulu | 2011 – present"
and being based at the Oulu site "since it opened" (2015–2017).
**The texts:** verified clean in the pre-logged DECISIONS.md entry (18 Sep) — the CV
credits her with helping *establish an additional satellite data processing centre*
in 2015–2017, not with the site's founding, and the extractor's "since it opened"
quote appears nowhere in the documents.
**Draft verdict: extractor error, stands as measurement.** A hallucinated
contradiction resting on a non-verbatim quote; the key's `evidenced` stands and the
false positive is marked like any other call.

## 2. C039 / R07 — key `absent` (archetype C)

**Flagged:** contradiction built on the quote "met its performance specification on
the first flight".
**The texts:** the quote does not exist (citation-verification similarity 0.356,
classified FABRICATION — the pre-registration-2 specimen). Every flight-adjacent line
in C039's documents says ground-based, as the brief required.
**Draft verdict: extractor error (fabricated evidence), stands as measurement.**
Already counted where it belongs, in pre-reg 2's invented-evidence rate; the
contradiction call collapses with its quote.

## 3. C076 / R08 — key `claimed_only` (archetype A)

**Flagged:** profile line "Team-lead experience." vs the work-history description
"Long-tenure individual-contributor role".
**The texts:** one employer for 21 years; the planted signal is an unsubstantiated
skills-list claim (key location `skills_list`). An IC role description and a claim of
team-lead experience are reconcilable — informal or interim lead stints inside a long
IC tenure are common, and the CV never says "never led".
**Draft verdict: extractor over-read at the claimed_only/contradiction boundary,
stands as measurement.** Both statuses agree on the substance (the claim is
unsubstantiated); the key stands. Corpus note, not a defect: the writer's
"individual-contributor" phrasing sharpened a tension the brief didn't plant.

## 4. C079 / R01 — key `evidenced`, letter-only, displaced (archetype F) — pre-logged

**Flagged:** the cover letter attributes a towed-array beamspace design to the 2019
JASA publication; the CV's only 2019 JASA paper is "Efficient Frequency-Domain
Coherence Estimation for Passive Acoustic Monitoring".
**Draft verdict: corpus defect, published (confirming the pre-logged entry) —
extraction defensible.** One publication with two identities is a genuine writer
inconsistency the QA sweeps could not see; the key row stands as registered, the miss
stays counted against pre-registration 3 as ran, and the writeup may honestly note
that flagging a publication inconsistency on a strong candidate is the dossier doing
its job.

## 5. C114 / R01 — key `evidenced`, letter-only (archetype B)

**Flagged:** the CV's only named Kajanti project is a filter-bank receiver evaluation;
the letter describes "a phased-array receiver prototype for a wideband digital
monitoring system" in the same period.
**The texts:** nothing states these are the same project. The letter-only mechanic
plants R01 evidence in the letter deliberately; a CV listing one project and a letter
describing another is that mechanic working as designed. The near-identical framing
("wideband spectral monitoring" / "wideband digital monitoring system") invited the
merge.
**Draft verdict: extractor over-read (two similarly named projects merged into one),
stands as measurement.** The key's `evidenced` stands; corpus note that the naming
similarity is texture worth a mention in the diagnosis, not a defect.

## 6. C196 / R12 — key `evidenced` (archetype B)

**Flagged:** CV dates the Oulu field trial April–June 2025; the letter says "earlier
this year" (corpus now = 2026).
**Draft verdict: corpus defect (minor date-phrase slip), published — extraction
defensible.** The letter should have said "last year"; the trial itself is evidenced
and the key stands. Same family as the timeline defects fixed pre-run, found
post-run, so published rather than repaired.

## 7. C197 / R05 — key `absent` (archetype B)

**Flagged:** CV gives 2022 for the RWTH Aachen MSc; the letter says "two years ago"
(implying 2024).
**Draft verdict: corpus defect (minor date-phrase slip), published — extraction
defensible.** No marking impact: R05 is `absent` on relevance grounds (mechanical
engineering) whichever year is right.

## 8. C198 / R08 — key `claimed_only` (archetype D)

**Flagged:** letter claims "experience managing cross-functional engineering groups";
CV lists "Signal Processing Engineer" doing individual-contributor work.
**The texts:** the letter's claim is a generic career assertion, not tied to the
listed employer; the CV fails to support it but does not affirmatively deny it.
**Draft verdict: extractor over-read at the claimed_only/contradiction boundary,
stands as measurement.** Absence of support is what `claimed_only` means; the key
stands. The stuffer was still declined on the aggregate pattern, so no decision-level
harm.

## 9. C232 / R01 — key `evidenced`, letter-only (archetype E)

**Flagged:** CV describes the Nordtek role (Jan–Aug 2020) as "signal conditioning and
filter implementation"; the letter describes designing phased-array beamforming
algorithms and a 12-element receive array processor in the same role.
**The texts:** the key registers the array work as genuine letter-only R01 evidence,
and separately plants the title inflation on R08 ("Head of Signal Processing…
directed a team of six" — caught, `contradicted`, as designed). But the planted R08
inflation and R01's only evidence share the same sentence, so distrust propagates:
arm 4 and, per their run reports, nearly every persona read the technical content as
fabricated along with the title (the marked per-persona data can give the exact count
if the writeup wants it).
**Draft verdict: defensible extraction — marking stands as ran; published as a
design-level entanglement nuance.** The key stands as registered (the R01 miss stays
counted); the writeup should carry the nuance explicitly: no careful reader can
separate the genuine array work from the inflated title around it, which is the
case's own argument for ask-in-screening over silent rejection.

## 10. C234 / R04 — key `claimed_only` (archetype D)

**Flagged:** letter claims RF measurement as long-standing practice, then concedes
"my primary domain has been optical sensing" with transferability "at the algorithmic
level"; the CV's only employer is optical.
**Draft verdict: extractor over-read at the claimed_only/contradiction boundary,
stands as measurement.** A self-hedged claim is still a claim without substantiation,
not an internal contradiction; both statuses agree the RF experience is not
established, and the key stands.

## 11. C235 / R08 — key `claimed_only` (archetype D)

**Flagged:** letter claims "team leadership responsibilities at various points in my
career"; the CV's single employer (2013–present) is described entirely in
individual-contributor language.
**Draft verdict: extractor over-read at the claimed_only/contradiction boundary,
stands as measurement.** Same reasoning as items 3 and 8; the key stands.

## 12. C236 / R04 — key `claimed_only` (archetype D)

**Flagged:** letter frames optical experience as transferable to RF by analogy, then
separately claims "extensive RF measurement and characterisation experience".
**Draft verdict: extractor over-read at the claimed_only/contradiction boundary,
stands as measurement.** The tension between analogy and direct-experience claim is
real, but it is the anatomy of an unsubstantiated claim, not a contradiction; the key
stands.

## 13. P07-assisted decision vocabulary — mapping for sign-off

The P07-assisted output wrote all 48 `screening_decision` values as Yes / No / Maybe
(one "want to flag before deciding" variant) instead of the contracted
advance / hold / decline. Logged in DECISIONS.md (18 Sep) before any mapped total was
computed: **Yes → advance; No → decline; Maybe and any flag-before-deciding variant →
hold.** The run is kept as ran (judgments legitimate, labels drifted; no
fix-and-rerun), the 48 mapped decisions are listed as adjudicated-mapped in the
marking outputs, and the report shows pre-registration 6 both with the mapping
applied (ratio 1.32) and with P07-assisted excluded (ratio 1.19) — NOT MET either
way, so the verdict does not hinge on the mapping. **For sign-off as logged.**

---

## Pattern across the twelve (observation for the writeup, not a verdict)

Every disputed call errs in the same direction: the workflow over-calls suspicion and
never under-calls it. Two calls are outright extractor errors resting on bad quotes
(items 1–2, both already measured by pre-registration 2's machinery); five are the
claimed_only→contradiction boundary slid harshly on stuffer-style claims (items 3, 8,
10–12 — substantively aligned with the key every time); three are genuine corpus
prose defects found after the run and published (items 4, 6–7); and two are
letter-only evidence plantings misread as cross-document conflict (items 5, 9). The
cost of the over-suspicion lands where the letter-only mechanic lives: all three
letter-only R01 plantings that carried any cross-document tension (C079, C114, C232)
were read as contradictions, which is where pre-registration 3 lost its gems.
