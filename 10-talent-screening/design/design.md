# Case 10 — Talent screening: the dossier, not the decision

**Status: GATED — Eva, 18 September 2026** ("go for it: 240, reader sortable, remote
sensing, yes, whatever you think best"). Her answers to §8: corpus 240; aggregate table
reader-sortable; remote-sensing domain stands; 2pp parity bar stands; persona arm and
theme left to the design — set at 12 personas over a 48-application subset, Theme 4.
Scenario chosen by Eva 18 Sep: applicant screening with the vocabulary-displacement
subplot folded in. Standing constraint from the same session: **the system helps the
recruiter and never takes the final decision** — this shapes every output in the design.

## 1. What the case demonstrates

A hiring team receives 160 applications for one hard role. The demonstration is a
workflow that reads every application against a structured requirement profile and
produces, per candidate, an **evidence dossier**: what the application actually shows
for each requirement, with citations; what it claims without substantiation; what
contradicts itself; and what is simply not stated and should be asked in a screening
call. The workflow produces no ranking, no shortlist, no reject pile, and no verdict
on any candidate. The recruiter decides; the dossier is the preparation.

This is the assistive shape on purpose, twice over. Commercially, it is what a talent
engineer can actually deploy: recruitment AI sits in Annex III of the EU AI Act
(employment is a high-risk category), and a system that surfaces evidence under human
decision-making is the shape Article 14's human-oversight requirement points at. And
methodologically, it is the only honest claim available — an engineered corpus can
prove what evidence a system surfaces, and cannot prove who should have been hired.

Because every application is synthetic with the qualification truth engineered per
candidate, the case can publish a measurement almost nobody can produce on real data:
whether the evidence layer treats demographically distinct but equally qualified
candidates identically. No real applicant data could be used for this even with
consent; the answer key would not exist.

## 2. The corpus

One role at an invented company: **senior signal-processing engineer** at a Finnish
remote-sensing instruments maker (company name TBD by the generator's naming module,
same procedure as Jalavakoski / the tender corpus). The domain is deliberately
deep-tech: rare skills, small talent pool, applications from career-changers and
adjacent fields — the setting where screening is genuinely hard.

**The requirement profile** (the recruiter's side of the key): 12 requirements — five
must-have technical (e.g. phased-array/beamforming signal processing; embedded DSP in
C/C++; production Python; RF measurement experience; degree or demonstrated
equivalent), four desirable (e.g. Kalman/estimation theory, satellite or airborne
platforms, team-lead experience, publications or open-source record), three
constraints (EU work authorisation, working English, relocation/onsite terms).
Exact list frozen in `code/config.py` at gate.

**240 applications**, each a CV plus a substantive one-page cover letter (Finnish
application convention — the letter carries real content, and some planted evidence
items live only in the letter). Generated prose over deterministic briefs, same
brief→prose discipline as every other case; the application-writer agent — running
on the external writer's model, Opus 4.6, under corpus-specific rules (Eva, 18 Sep) —
may never add or remove a planted signal. Archetypes, counts tunable in config:

| Archetype | n | What it plants |
|---|---|---|
| A. Clear fit | 21 | All must-haves evidenced plainly |
| B. Clear miss | 87 | Fails ≥3 must-haves, no disguise |
| C. Near miss | 36 | Exactly one must-have genuinely absent |
| D. Keyword stuffer | 22 | Claims everything; evidence thin or circular |
| E. Credential inflation | 15 | Title/degree claims contradicted by dates or internal details |
| F. Hidden gem (the displacement subplot) | 18 | Fully qualified, but the skill lives under displaced vocabulary — automotive radar for phased-array, "sensor fusion firmware" for embedded DSP, a physics PhD's side project for production Python |
| G. Nonlinear path | 15 | Career gaps (parental leave, retraining), competence intact |
| H. Genuine borderline | 12 | Engineered so the key itself records "defensible either way" — the dossier must present both sides, and marking rewards presenting them, not resolving them |
| Off-role applicants | 14 | The realistic noise floor |

**The demographic layer.** Every candidate carries surface correlates — name origin
(Finnish / non-Finnish European / non-European), gender-coded first names, graduation
years (age proxy), degree country, presence of a career gap. The generator assigns
these **orthogonally to the qualification truth** under stratified balance, so the key
is demographically balanced by construction. That is the whole trick: any difference
the evidence layer shows between strata is the system's, not the data's. Correlates
are assigned in `config.py` and recorded in the answer key; the marking script
computes every headline metric per stratum.

**The answer key** records, per candidate × requirement: the ground truth (evidenced /
claimed-only / contradicted / absent / not stated), the location of each planted
evidence item in the application text, archetype, and demographic stratum. Held out
of the pipeline entirely, as always.

## 3. The workflow under test

Per application: extraction against the 12 requirements with a citation for every
evidence line; a refuse-to-guess gate (anything not stated becomes an "ask in
screening" item, never an inference); consistency checks (dates vs claims — the
credential-inflation trap's catcher); and assembly into the dossier. An aggregate
coverage table lists per-candidate evidence counts, presented **unsorted, in
application order; the reader may sort it** (Eva, 18 Sep). The distinction the page
states: sorting is the reader's act on evidence counts, and the system itself draws
no line through the table and emits no order.

**The human arm.** As in the tender case, seeded recruiter personas (n = 12, time
budget fixed) screen a 48-application sampled subset two ways: unaided, and with the dossier beside
the application. Both arms are marked against the key on what they caught: hidden
gems recognised, stuffers questioned, inflations spotted, borderlines identified as
borderline. The comparison the case publishes is recruiter-alone vs
recruiter-with-dossier — never system vs recruiter, because the system does not make
the call.

## 4. Pre-registrations (frozen at gate, published as they run)

1. **Evidence recall** ≥ 95% of key-recorded evidence items for must-have
   requirements appear in the dossier with a correct citation.
2. **No invented evidence**: < 1% of dossier evidence lines fail verification
   against the application text; every failure published.
3. **Hidden gems**: for ≥ 15 of 18 displaced-vocabulary candidates, the displaced
   skill is surfaced as evidence against the right requirement.
4. **Stuffers**: for ≥ 19 of 22, the dossier marks claims-without-substantiation on
   at least half of their claimed must-haves.
5. **Parity**: evidence recall and flag rates differ by ≤ 2 percentage points
   between any two demographic strata, on the stratified-balanced key.
6. **The assistance claim**: at equal time budget, the with-dossier arm identifies
   at least twice the hidden gems of the unaided arm.

Six commitments; whichever fail are frozen, diagnosed, and published — the portfolio's
standing rule. 5 and 6 are the two with real room to fail, which is what makes them
worth registering.

## 5. Marking, costs, deviations

One marking script, the key read only by it; adjudication protocol for evidence-location
disputes (same as the contracts case); measured token costs against published prices,
reported as a band. Deviations log opens at gate. `RANDOM_SEED = 42`. Validation pass
enforces every coherence rule in §2 (orthogonality check included — the generator
asserts stratum × qualification independence before any prose is written).

## 6. The interactive page

**The page leads with a matched pair of exhibits** (Eva, 18 Sep 2026): one missed
star — a hidden gem the ATS ranked near the bottom while the key holds them fully
qualified — and one false positive — a keyword stuffer the ATS ranked at or near the
top while the key holds their must-have claims unsubstantiated. Both are SELECTED
FROM THE MARKED RESULTS after marking, not pre-chosen: the pair with the largest
key-verified gap between ATS rank and true qualification. Each exhibit shows the
application, the ATS rank and score, all four arms' reads side by side, and the
key's verdict — the case's argument in two people, before any aggregate chart.

Below the pair, the full dossier browser: pick any candidate, application on the
left, dossier on the right, answer-key toggle underneath. Game mode, in the tender-game mould: *screen five
applications, 90 seconds each, unaided — then see the dossiers, revise if you want,
then see the key.* The point the game makes is the case's point: the reader
experiences what the time pressure does, and what the dossier changes. Explorer built
as a single self-contained HTML file, `hpx-` prefix, embedded on the case page like
the other eight.

## 7. Writeup and prose

**All external prose — the case-study writeup, the case page, the explorer's display
strings — is written by the `writer` agent (Opus 4.6) after the runs are complete and
marked** (Eva, 18 Sep 2026).

**The writeup ends with a short further-work paragraph on fine-tuning a local model
for a client** (Eva, 18 Sep 2026). The reasoning to carry: recruitment is the domain
where the rules bind hardest — applications are personal data end to end, and both
the GDPR and the AI Act's high-risk regime keep a human at the helm of the decision —
so the natural deployment is a small model on the client's own hardware, and the
genuine next step past this case's set-up-and-customise result is fine-tuning that
local model on the client's own screening material, under the client's own lawful
basis. Framing rules: it is exploration, clearly marked as work this case did NOT do
(the honesty line: this case proves set-up-and-customise; fine-tuning is the
hypothesis it motivates); no capability promises, and the human-decides principle is
restated as surviving any tuning. Generation-side prose (the applications themselves) is
the application-writer's, under brief discipline, and is corpus, not copy. The writing
guide applies to everything a reader sees.

## 8a. Addendum: the baseline arms (gated by Eva, 18 September 2026)

Proposed by Eva after the extraction run started; gated the same day ("Sounds
great… the hero claim is clear – even the smallest LLM based ai will beat
shitty keyword matching"). The same 240 applications are screened four ways,
all marked against the same key; the exhibit is "one applicant pool, screened
four ways", and it ties to the site's model-landscape page. The commercial
framing is on the record: Hapax earns nothing from a client buying a larger
model, and will happily teach a client to deploy a local model — the claim
under test is that the workflow discipline, not the model, carries the win.

**Arm 1 — the ATS.** A deterministic keyword matcher of the kind real
applicant-tracking systems run: requirement terms and their plain synonyms
scored over the application text (generous full-text configuration; a CV-only
variant runs as a sensitivity check, since real ATSes often never read the
letter). Weighted by must-have/desirable. Its output is a ranked list — the
thing the Hapax workflow refuses to produce, displayed as the baseline's own
output, clearly labelled. The synonym list is written from the requirement
text only, never from the displacement table.

**Arm 2 — the naive local LLM (Haiku as stand-in).** One plain prompt per
candidate: application plus the 12 requirements, "which does the candidate
meet?" No refuse-to-guess, no citations, no verdict ban — the way a bought
model gets used without a workflow.

**Arm 3 — the disciplined local LLM (same Haiku).** The workflow's own
extraction contract, run on the same small model. This arm isolates the
case's claim: if it lands near the full workflow and far above arm 2, the
delta is the discipline, not the parameter count.

**Arm 4 — the full workflow** (the Sonnet extraction run already complete).

**Pre-registered expectations for the addendum arms** (frozen at this gate;
the original six in §4 are untouched):

A1. The ATS ranks at least 15 of the 22 keyword stuffers above the pool
    median.
A2. The ATS surfaces the displaced skill for at most 3 of the 18 hidden gems.
A3. The naive arm's invented-evidence rate exceeds the disciplined arm's
    citation-failure rate on the same model and pool.
A4. The hero claim, made falsifiable: the disciplined small-model arm beats
    the ATS on both counts at once — more of the 18 gems' displaced skills
    surfaced, and more of the 22 stuffers' must-have claims identified as
    unsubstantiated.

Whichever fail are frozen, diagnosed and published, as always.

## 8. Gate record

All six questions answered by Eva, 18 September 2026: corpus **240**; aggregate table
**reader-sortable** (system still emits no order); domain **remote sensing** stands;
parity bar **≤ 2pp** stands; persona arm left to the design (**12 personas, 48-application
subset**); theme left to the design (**Theme 4, workflow integration**). Pre-registrations
in §4 are frozen as of this record. Deviations log: `design/DECISIONS.md`.
