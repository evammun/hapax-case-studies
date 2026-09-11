# 09 Training Outcomes — The ruler, tested

Status: SIGNED OFF BY EVA, 11 Sep 2026 ("let's get to it!" on the case; "whatever you
think best" on the §8 gate questions — resolved to the recommendations: (1) the naive
evaluation arm stays as the comparator; (2) cohort 40 with the tabled archetype mix;
(3) the task-set forms are PUBLISHED in full, real engagements generating fresh forms
by the same published method; (4) Kuusiharju Oy, AI-Augmented Workflows as the in-world
programme). Designed on the strength of the 80-lead outreach analysis: the training
route converts at 3% because no published case is about training; 12 of 55 case-gaps
name a measured-training case explicitly; training is a third of what the firm sells.
Pre-registered expectations in §7 (§5 as numbered) were written before any generation
or run. Writeup by the Opus writer per standing instruction.

## 1. Purpose — what can honestly be claimed, and what cannot

Hapax has trained no commercial cohort yet, and a case that pretended otherwise would
break the honesty rule at its root. What CAN be built and tested is the thing the
training industry conspicuously lacks: the MEASUREMENT INSTRUMENT. Competitors evidence
training with attendance sheets and feedback scores; the field's own worked examples
never mark learning against anything. This case builds the instrument Hapax will attach
to every real training engagement — pre/post assessment on held-out task sets — and
tests the instrument itself on a simulated cohort whose true learning is planted and
recorded in an answer key. The claim the case supports is precise and honest: not "our
training works" but "when we train you, the effect will be measured with an instrument
whose accuracy we have published — including what it cannot see."

It also answers the Article 4 angle without certificate theatre: measured outcomes plus
session records are the strongest literacy evidence a deployer can hold.

## 2. The invented cohort

Kuusiharju Oy (invented, tree convention, collision-check at build): a ~200-person
technical trade company sends 40 employees through a two-day "AI-Augmented Workflows"
programme (the flagship theme — its syllabus on the training page is the in-world
curriculum). The 40 simulated learners span roles (finance, ops, sales, service admin)
and carry deterministic profiles: baseline ability, a PLANTED true ability shift δ from
the training, a self-confidence trajectory (independent of δ — the load-bearing
separation), an assessment-noise level, and a volunteering propensity (for the naive
arm's selection trap).

Archetypes (counts fixed at gate):
| Archetype                          | n  | Planted truth                                           |
|------------------------------------|----|---------------------------------------------------------|
| Genuine improver, strong           | 8  | δ large; confidence tracks ability                      |
| Genuine improver, modest           | 12 | δ small-positive; confidence tracks                     |
| Confident non-learner (the star)   | 7  | δ ≈ 0; confidence rises sharply — feedback-form gold    |
| Non-responder                      | 7  | δ ≈ 0; confidence flat                                  |
| Ceiling case (already skilled)     | 3  | δ ≈ 0 by ceiling; high baseline                         |
| Fast forgetter                     | 3  | δ positive at post-test, decays by +8 weeks (the        |
|                                    |    | designed blind spot — see §6)                           |

## 3. The instruments under test

1. THE HONEST INSTRUMENT (the product): two equivalent held-out task-set forms (A/B,
   counterbalanced pre/post), tasks drawn from the programme's actual skill claims —
   writing an instruction that returns the same answer twice, spotting a model's
   planted error, judging which of two outputs is checkable, deciding what may be
   pasted where (policy task). Scoring rubric deterministic per task. Form equivalence
   is itself tested (pre-scores across forms must not differ beyond tolerance).
2. THE FEEDBACK SHEET (the industry standard, run honestly as a comparator): post-only
   self-report satisfaction and self-assessed improvement.
3. THE NAIVE EVALUATION (how training is usually "measured" when anyone tries):
   volunteers only (selection via volunteering propensity), same form pre and post
   (practice effect planted), self-report weighted in. Assembled deliberately from
   real-world bad practice, each flaw documented.

All three run on the same simulated cohort. Task RESPONSES are LLM prose from
deterministic briefs (ability level + task → plausible answer of that quality; the
scoring rubric marks the response text, so generation and scoring stay separated);
scores, abilities, shifts and noise are deterministic Python.

## 4. Marking

`code/mark.py`, sole reader of the key: per learner, instrument-estimated δ̂ vs planted
δ; cohort-level effect estimates per instrument vs planted cohort truth; detection
table for the confident non-learners (does each instrument separate confidence from
competence?); the naive arm's overstatement decomposed into its planted causes
(selection, practice effect, self-report weighting).

## 5. Pre-registered expectations (before any generation or run)

1. The honest instrument recovers the planted cohort mean effect within ±0.10 σ.
2. It flags ≥ 6 of the 7 confident non-learners (self-report/performance divergence).
3. The feedback sheet correlates with planted δ at r < 0.30 — i.e. the industry's
   standard evidence is close to uninformative about learning (this is the number the
   training page will cite for why we measure differently).
4. The naive evaluation overstates the cohort effect by ≥ 50%, decomposable into its
   three planted flaws; each flaw's share is reported.
5. Form equivalence holds (pre-score difference between forms within tolerance); if it
   fails, that is a frozen finding about how hard equivalent forms are to write.
6. THE DESIGNED BLIND SPOT, stated in advance: the standard pre/post design cannot see
   the fast forgetters — their +8-week decay is invisible without a delayed third
   measurement the instrument (as sold) does not include. The case publishes this as
   the instrument's known limit and the argument for the 30-day follow-up call the
   training page already promises. If the instrument accidentally distinguishes them
   anyway, that is reported as luck, not design.
Any failed expectation is frozen and published, never retuned.

## 6. Honesty framing on the page (non-negotiable)

The cohort is simulated and the page says so in its first lines: this case tests the
RULER, not the training. Simulated learners prove instrument properties (bias,
sensitivity, what it detects and what it cannot); they prove nothing about how much a
real cohort learns. The first real engagement's measured outcomes — whatever they show
— get published with client permission or described without identification, and the
case page says that too.

## 7. Deliverables

Portfolio convention: PLAN, config/generators/validators, the task-set forms
(published — they ARE the instrument; a client can read exactly what would be
measured), answer key, three instrument runs, mark.py, report.md, canonical writeup
(Opus writer), interactive page (browse the cohort: each learner's pre/post responses
side by side with their planted truth and each instrument's verdict on them; the
confident-non-learner gallery as the centrepiece; scoreboard of the three instruments
against truth), case page + work.html + training-page cross-link (the training page's
"we follow up at thirty days" and the FAQ's records answer both gain a quiet link).

## 8. Open questions for Eva (answer at the gate)

1. The two-arm-plus-feedback-sheet comparison — right shape, or drop the naive arm and
   test only our own instrument? (Recommendation: keep it; the naive arm is what every
   buyer has previously been shown, and its planted decomposition is the selling
   argument.)
2. Cohort 40 / archetype mix as tabled — comfortable? The 7 confident non-learners are
   deliberately the largest "problem" group.
3. The task-set forms will be PUBLISHED in full (they are the credibility artefact,
   but a future real client could in principle rehearse them; mitigation: the real
   engagement generates fresh forms by the same published method). Publish, or hold
   the forms and publish only the method? (Recommendation: publish — checkability is
   the brand; rehearsal is handled by fresh forms.)
4. Kuusiharju Oy as the invented company, and the AI-Augmented Workflows syllabus as
   the in-world programme — fine?
