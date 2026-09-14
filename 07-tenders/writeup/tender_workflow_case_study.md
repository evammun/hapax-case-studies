Canonical case study. Drafted in the main loop by the writer agent (Opus), 11 September 2026, per Eva’s standing instruction that this file is written once all six phases are complete. The website case page, the interactive page and any training material derive from this file. Eva’s read-through is pending.

# Sixteen tenders, answered two ways

*Visakoivu Oy, the fourteen people who answer tenders for it, the sixteen buyers and every tender document below are invented; the measurements are real, marked against an answer key written before either arm saw a document.*

## The question

Our shapes page claims that a person asking a chatbot gets a better paragraph, while a workflow with AI inside it gets a better process. That claim is the argument of the page and of most of our advisory work, and until now we had not measured it. Benchmarks score models on tasks. The choice described here is not a model choice but an organisational one – the same model, the same documents, 2 ways of arranging the work around them, and we have not found it marked against a common answer key anywhere.

So we built one. Sixteen invented tenders, 510 requirements inventoried in an answer key at authoring time, before either arm existed. The tenders were then answered twice. On one side, 64 attempts by fourteen simulated individuals working ad hoc with a general chatbot, each with a habit brief. On the other, one integrated workflow run once per tender – requirement matrix, cited drafting, two deterministic gates, a router that produces the sign-off page a named person signs. Both arms were marked by the same script, `code/mark.py`, the only code in the project permitted to open the answer key.

## What happened, in numbers

| Measure | Arm A – fourteen people, 64 attempts | Arm B – one workflow, 16 runs |
|---|---|---|
| Requirement coverage, per tender | medians 64.3% to 93.3%; 13 of 16 medians inside the pre-registered 55–80% band, the other three above it | 100% on 11 of the 14 bid tenders, at or above 95% on 13; lowest 92.9% |
| Single best and worst attempt | 100.0% (T01) and 40.6% (T08) | one run per tender by design; no distribution |
| The two tenders Visakoivu cannot win | 2 of 8 attempts declined to bid | both declined, each with the failing clause named |
| Fabricated claims | seeded in 22 of 64 attempts (34.4%) | zero uncaught across all 16 terminal responses |
| Hidden-form traps caught | 0 of 12 | 0 of 3 |
| Annex-buried disqualifiers / contradictions / format traps | 11 of 12, 4 of 12, 9 of 12 | 3 of 3, 3 of 3, 3 of 3 |
| Extraction recall (workflow step 1) | – | 507 of 510 requirements, 99.4% |
| Gate bounces | – | 10, across 4 runs, all mechanical false positives |

## The corpus

Visakoivu Oy is a 180-person technical and property-services firm in Jyväskylä (heating and ventilation, electrical, building automation, property upkeep) bidding for public and private maintenance and installation work. Its facts library is in-world data available to both arms: certifications with expiry dates, ten reference projects with values and periods, staff by discipline, insurance cover, three years of financials. It is not the answer key, and both arms could read it.

The sixteen tenders run four simple (about 15 requirements), eight medium (about 30) and four gnarly (50 to 60, multi-annex), in a loosely Finnish public-procurement register with no real authority or portal named. Traps were placed by hand rather than drawn at random, so the counts are guaranteed by construction: three disqualifying clauses buried in annexes, two eligibility thresholds Visakoivu genuinely fails, three body-versus-annex contradictions, three mandatory forms mentioned once in passing, three price or format traps, four clean tenders with nothing planted.

## Seventy private habits

The section title comes from the exemplum on the shapes page, where about seventy people in an invented firm had each found their own way to a chatbot. Fourteen of those habits are modelled here: the careful reader who takes no notes, the prompt-collector who transcribes the body faithfully and summarises annexes, the one who pastes the whole document in and asks for a response, the sceptic who rewrites every paragraph by hand, the deadline-panicker, the reader who trusts the buyer’s summary page, and so on. Every persona is a working habit, not a deficiency.

Arm A is a simulation, and how it was built decides what it can show. Which requirements an attempt noticed was decided in Phase 2 by a seeded engagement model (one coin-flip per requirement, biased by the persona’s traits, an annex penalty, a penalty for requirements mentioned once, and a decay across the numbered list) and calibrated twice at population level before a single attempt existed. Prose agents then wrote the chat transcript and the draft consistent with that list, and were not permitted to add or remove a noticing. So Arm A’s distribution is a model of how attention spreads across a document, not an observation of real bidders. Its internal structure is what the case leans on.

That structure holds up. Per-tender medians run from 64.3% on T12 to 93.3% on T01, and where they leave the pre-registered band they leave it upwards. The best attempt reaches 90% or better on five of the sixteen tenders, and Outi Leskinen, who builds her own checklist from the numbered requirements before she opens a chat window, answers all 15 of T01’s requirements. The floor is low: 40.6% on T08, 43.1% on T15, 46.7% on T01, the same tender Outi answered completely.

4 individual attempts need reading in full, because the aggregate hides what they show.

**Sanna Peltola on T08** pastes the entire request, body and both annexes, into one message and asks for a complete response. The assistant comes back having noticed that clause 4.10 requires a four-hour emergency response while Annex B’s cross-reference says two hours, and flags it unprompted. Sanna keeps the flag in, and the conflict is one of only four the human arm caught out of twelve. In the same session she is asked for an administrative headcount, says “just put a solid number in, say 26 – sounds about right for a company our size, I’m not going to go dig through the staff sheet”, and 26 goes into the draft. The habit that put both halves of the contradiction in front of the assistant is the same habit that put an unchecked number into the response.

**Timo Rautiainen on T11** takes a first draft and rewrites every paragraph against the tender text, section by section, annexes included. His diligence is real and pointed at the wrong reference: he checks the draft against the document, never against the facts library, so the assistant’s invented figure of 25 building-automation staff survives his entire review, and T11’s actual problem, a required ISO/IEC 27001 certificate Visakoivu does not hold, is never surfaced at all. He bids, at 73.3% coverage.

**Antti Salomaa on T13** is the most attentive body reader of the fourteen and treats annexes as reference material to get back to later. T13’s disqualifying clause is in an annex. His is the single annex-buried disqualifier the human arm missed, out of twelve.

**Marko Salminen on T15** works in interrupted bursts, checks clause 3.7 against the reference list in his first twenty minutes, finds that the largest project on file is €1,650,000 against a €2,000,000 threshold, and flags it before drafting anything. He then drafts sections 4 to 7 anyway while waiting for a decision, never opens the annexes, and scores 43.1%, the worst coverage on that tender. His bid/no-bid call is right.

Every fabrication in this arm has the same shape. A chatbot plausibly overclaims when asked to summarise eligibility, capacity or track record, and the person pastes the answer in without checking it against the facts library; no persona is written as saying something they know to be untrue, and the step that is missing is the verification. Whether that step happens is driven by the persona’s own eligibility-scrutiny and time-pressure traits. Twenty-two of the 64 attempts carry an event, 34.4%, above the 25% pre-registered floor.

The trap classes separate the arm cleanly. Where a requirement is written where a reader looks, people do well: 11 of 12 annex-buried disqualifiers caught, 9 of 12 format traps. Contradictions are harder (4 caught, 5 where both sides were answered without the conflict being flagged, 3 missed entirely) because catching one requires holding two distant clauses in mind at once. Forms mentioned once, in passing, were caught 0 times out of 12.

## The workflow

Arm B runs the same five steps on every tender, with no operator to be good or bad at it. A model extracts a requirement matrix from the tender documents. A model drafts an answer per matrix row, citing a path into the facts library for every factual claim. A deterministic coverage gate requires every row to be answered or the run to stop as a no-bid. A deterministic facts gate resolves every citation, requires each specific claim (a euro amount, a headcount, a certification, a year count) to be supported by the value of one of that row’s own citations, and additionally requires a cited certification’s `held` flag to be true. A router writes the one-page sign-off. No gate ever reads the answer key; every check is draft against matrix against facts library.

Coverage is 100% on 11 of the 14 tenders the workflow bids on and at or above 95% on 13 of them. The extraction step over-produces, not omits: 537 matrix rows against the key’s 510 requirements, splitting compound clauses into separate rows, which costs drafting effort and no coverage.

Both no-bid tenders were refused, and they were refused in different shapes. On T11 the run drafted all 30 rows, then declined, naming clause 3.5 and the missing ISO/IEC 27001 certificate, “rather than submit a quotation it cannot honour”. On T15 it stopped at row 7 of 53: the sign-off names clause 3.7, gives Visakoivu’s largest reference at €1,650,000 against the €2,000,000 threshold, states that the remaining technical, commercial, form and format rows were deliberately not drafted, and lists all 46 of them by matrix id. Measured against the key, that run covers 13.7% of T15’s requirements, which is what a correct stop looks like when coverage is the metric.

No fabricated claim survived to a terminal response in any of the 16 runs, confirmed two ways: by re-running the facts gate against each run’s final response, and by an independent scan of the free-text cover-letter sections, which are the one place the gate structurally cannot check because they carry no citations field. That gap is documented in the formats spec, not closed. The mechanism behind the zero is the transferable part: an unsupported claim costs a bounce and another drafting round, while a cited claim passes first time, so the cheapest route through the pipeline is to say only what the facts library supports.

## What the process cost

Ten gate bounces, across four of the sixteen runs, each costing that run one extra drafting iteration. All ten are consistency bounces, and all ten are mechanical false positives. The check attributes every number found in a row to every citation that row carries, instead of pairing each number with the citation that supports it. A row citing two insurance figures, or three reference projects, therefore looks like one fact quoted at several values.

T02 shows what that costs. The first draft answered the limitation-of-liability row with both real figures, €2,000,000 of general liability cover and €1,000,000 of professional indemnity, each correctly cited. It bounced. The redraft kept the €2,000,000, dropped the second figure, and said the professional-indemnity limit would be confirmed during negotiation of contract terms. The gate protected a draft that was already right, and the version that passed tells the buyer less than the version that failed. The design pre-registered at least one false block as the bureaucratic cost of process; ten occurred, and none of them was a genuine catch.

## Where the pre-registration was wrong

Six expectations were written into the design before any generation or run. Four were not met. All are frozen as written; nothing in the corpus, either arm, or the marking script was retuned after these numbers appeared.

**Coverage of 95% everywhere failed on exactly one tender**, T03 at 92.9%, and the reason is in the last section of this writeup.

**The human arm beat its own pre-registration.** At most one of the eight attempts on the two doomed tenders was expected to decline; two did, both on T15. The tally traces to Phase 2’s attempt briefs, fixed before any Arm A prose existed, and the error runs in the humans’ favour, so it is published, not corrected.

**Difficulty does not scale with size.** Mean of the per-tender medians: 75.2% simple, 73.4% medium, 78.3% gnarly. T16, the largest clean tender, has the second-highest median in the corpus at 93.3% and its worst attempt still reaches 88.5%, while several trapped medium tenders sit in the sixties. What makes a tender hard here is what has been planted in it, not how long it is.

**Extraction was better than the design wanted it to be.** Recall was pre-registered at 90–99%, on the reasoning that an imperfect model layer is what the gates exist to carry to a high final coverage. Measured recall is 507 of 510 requirements, 99.4% overall, with 13 of the 16 tenders at exactly 100%. The gates’ measured contribution to coverage is therefore zero percentage points on every bid tender, because nothing was missed for them to recover. The design named this outcome in advance as a reported weakness, not a win, and that is how it is reported: on this corpus the coverage argument for the gates is unproven, and what the gates demonstrably did is catch fabrications during drafting and enforce cross-row consistency, at the cost described above.

Two things were not measured at all. The corpus has no time dimension (no timestamps, no modelled drafting duration) so the expectation that individuals are faster on simple tenders is unmeasurable here, neither confirmed nor denied. The hours in the shapes page’s exemplum are labelled hypothetical and nothing here changes that. Prose quality was excluded from the measured variables by design and was not scored; several Arm A drafts read better than the workflow’s matrix-shaped output.

## How the marking was checked

The marking engine was calibrated by hand-reading a sample of attempts against their computed marks before it was trusted on the corpus, and it was wrong three times.

Clause text in T05 to T08 is printed in Finnish verbatim while the surrounding document prose is English, which drove keyword extraction from the documents’ own text to near-zero matches on those 4 tenders, a systematic false negative that looked like persona underperformance. It was fixed by keying a hand-built bilingual gloss off the corpus’s fixed topic banks instead. Some drafts are written entirely in Finnish regardless of the source language; one attempt marked at 35.3% was substantively addressing most of the required topics in Finnish and marked at 78.4% once each topic carried its own Finnish stems. And Finnish morphology defeated naive substring matching outright: the keyword `vat`, from VAT, matched inside ordinary Finnish word forms such as `vaadittavat` and `pysyvät`. A start-of-word boundary fixed it, deliberately left open on the right so suffixed forms still match their stem.

Two limitations are disclosed, not patched. The independent fabrication detector treats a comma as a word boundary, so a planted value of 450,000 matched inside a legitimate, correctly cited 1,450,000. Against the 22 seeded fabrication events that detector found 22 true positives, no false negatives and three false positives, two of which are its capability vocabulary colliding with a buyer’s own name, Datakeskus Silta Oy. Separately, the font-size format trap on T04 is checked by looking for an explicit statement of the point size in the text, which is a weak proxy for the real requirement (a document’s actual typesetting) and is flagged as such, not treated as equivalent.

## The three requirements nobody found

Across all sixteen runs, the workflow’s extraction step missed three of the corpus’s 510 requirements: T03-R014, T09-R031 and T14-R053. Those three are the three hidden-form traps, and nothing else was missed anywhere.

Each is a single sentence, stated once, inside an annex, with no clause number of its own. T03’s reads: “The tender should also confirm the tenderer’s registered business ID and the name of the contact person handling the contract during its term; the tender must also include a certificate confirming payment of the tenderer’s taxes.” T09 buries a pension-insurance certificate the same way. T14’s sits in the enclosure clause of a draft contract annex, listed beside two other forms that are properly required elsewhere in the document, so it reads as a recap, not as a new obligation.

The human arm scored 0 of 12 on that class, which follows from the engagement model’s penalty for requirements mentioned once. The workflow’s 0 of 3 does not follow from anything: a model read those documents and built a matrix, and the requirement written to hide from a reader’s attention hid from extraction in the same way. Because a requirement that was never extracted can never be answered, this is also why T03 finished at 92.9% and missed the pre-registered floor.

The step up is real and large. The workflow covered 100% of requirements on most tenders where the human medians sat in the sixties and seventies, refused both doomed bids where two of eight attempts did, and let no fabricated claim through where 22 of 64 attempts carried one. It is also not omniscience, and this corpus says where the limit sits. A check that reads the same documents in the same way inherits the same blind spot. Catching this class needs a check of a different kind (reconciling the enclosures actually attached against every form named anywhere in the pack, or a pass over annex prose looking specifically for obligations that carry no clause number) and neither of those was in the design.

## What transfers and what does not

The architecture transfers, because it does not depend on anything about tenders: a matrix that enumerates what must be answered, drafting that must cite a source for each factual claim, deterministic gates that check the draft against the matrix and the sources not against a person’s attention, and a sign-off artefact naming the coverage, the flags and the call. So does the gate discipline, including its cost. A mechanical check will bounce correct work, and the design has to decide in advance whether the bounce is cheaper than the miss.

The numbers do not transfer. They belong to this corpus, its trap mix and one invented company’s facts library, and the trap mix was chosen to be hard in particular ways. Arm A’s distribution is a seeded model of working habits calibrated at population level, so its location on the scale is partly a modelling choice; what the individual attempts show is how a given habit interacts with a given document structure, not what any real bidder would score. Arm B’s three misses are not modelled, which is why they are the finding.

A real tender desk also has something this corpus does not. It has outcomes (bids won and lost, clarification questions from the buyer, responses rejected as incomplete) and those are better evidence than a planted key, as well as slower to arrive. Win rates, client persuasion and real-world time were not measurable here and are not claimed. The corpus, both arms’ full output, the marking script and the answer key are published in full, and the numbers above are one run of a method against data built to have a known right answer.
