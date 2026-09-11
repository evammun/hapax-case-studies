# 07 Tenders — The step up, measured

Status: SIGNED OFF BY EVA, 11 Sep 2026 ("perfect, go for it") — the first fully
Eva-gated design in the portfolio. §10's four open questions resolved to the
recommendations: (1) persona tone = habits, never mockery; (2) sector as drafted;
(3) full 16×4 scope kept; (4) Finnish-flavoured procurement conventions. Arm A's
section title "Seventy private habits" is Eva-endorsed. Pre-registered expectations
in §7 were written before any generation or run; final writeup to be drafted by the
Opus writer agent once all phases complete, per Eva's instruction.

## 1. Purpose

The shapes page claims: "a person asking a chatbot gets a better paragraph; a workflow
with AI inside it gets a better process." Every case so far demonstrates a method. This
one measures the ORGANISATIONAL choice itself: the same tender corpus is answered two
ways — by simulated individuals using a chatbot ad hoc, and by an integrated workflow
with the model inside the steps and checks by design — and both arms are marked against
the same held-out answer key. The deliverable is the difference, including where the
naive arm honestly wins.

## 2. The invented company

Visakoivu Oy — a ~180-person technical and engineering services firm in Jyväskylä,
bidding for public and private contracts (maintenance outsourcing, installation
projects, framework agreements). Named to the portfolio's tree convention; collision
check against real companies and the six existing fictional firms required at build.
A company facts library (`data/facts/company_facts.md` + structured YAML) is part of
the corpus: certifications held, reference projects with dates and values, staff
counts by discipline, insurance cover, financials. It is in-world data available to
BOTH arms — it is not the answer key.

## 3. The corpus — 16 invented tenders

Mix of public-procurement-style RFPs (mandatory eligibility criteria, forms, annexes)
and private RFQs. Size profile: 4 simple (≈15 requirements), 8 medium (≈30), 4 gnarly
(≈50–60, multi-annex). Every requirement is inventoried in the answer key at authoring
time. Planted traps (each recorded in the key):

| Trap                                                        | Count | The correct behaviour            |
|-------------------------------------------------------------|-------|----------------------------------|
| Disqualifying clause buried in an annex                     | 3     | Surface it; bid only if curable  |
| Eligibility threshold Visakoivu genuinely fails             | 2     | Recommend NO-BID                 |
| Contradictory requirements (body vs annex)                  | 3     | Flag; answer both, note conflict |
| Mandatory form/attachment mentioned only once, in passing   | 3     | Include it                       |
| Price/format trap (unit basis, currency, page limit)        | 3     | Comply exactly                   |
| Clean tenders (no trap)                                     | 4     | Just answer everything           |

(Traps overlap tenders; totals need not sum to 16.) The two genuine no-bids are the
sharpest plants: the workflow's requirement matrix should surface the failed threshold
and stop the bid; a naive drafter writes a doomed response fluently.

## 4. Arm A — seventy private habits

A cast of 14 personas with deterministic habit briefs (the careful reader who takes no
notes; the prompt-collector; the paste-everything-and-ask-for-a-response one; the
sceptic who rewrites by hand; the deadline-panicker; …). Each of the 16 tenders is
attempted by 4 different personas → 64 attempts. Per attempt, LLM agents (Sonnet,
ticket-writer pattern: deterministic brief in, prose out, may not add or remove planted
facts) produce (a) a plausible chat transcript — the person's actual back-and-forth
with a general chatbot, habits showing — and (b) the resulting tender response draft.
Persona skill varies BY DESIGN: some attempts will catch traps. Arm A is scored as a
distribution per tender, not a single number; its story is variance without a floor.
No attempt may consult the answer key or the requirement inventory; personas see only
the tender documents and the facts library.

## 5. Arm B — the integrated workflow

One run per tender (operator-independent — that is the point). Deterministic pipeline
with the model inside the steps:

1. Extract: model builds the requirement matrix from the tender documents (itself
   marked against the key's inventory — extraction recall is reported).
2. Draft: model drafts per matrix section, citing the facts library for every factual
   claim (claim → source line).
3. Coverage gate (deterministic): every matrix row must be answered or explicitly
   no-bid-flagged; unanswered rows bounce the draft back. Runs until pass or no-bid.
4. Facts check (deterministic): every cited claim must exist in the facts library;
   uncited factual claims are listed as fabrications and bounced.
5. Sign-off artifact: one-page summary — coverage, flags, the bid/no-bid call — the
   thing a named human signs.

The gates never consult the answer key; they check internal consistency (draft vs
matrix vs facts library). The key is used only by the marking script, on both arms.

## 6. Marking (mechanical, `code/mark.py`, sole reader of the key)

Per tender, per attempt/run: requirement coverage %, traps caught / missed, bid/no-bid
correctness, fabricated-claim count, format compliance. Aggregates: Arm A distribution
(median, best, worst per tender) vs Arm B line. Also reported: Arm B extraction recall
(step 1's own error rate — the workflow's honesty about its weakest link), gate bounce
counts, and false blocks (gate bounces that the key says were fine).

## 7. Pre-registered expectations (before any generation or run)

1. Arm B coverage ≥ 95% of key requirements on every tender, including the gnarly four.
2. Arm B recommends NO-BID on both no-bid tenders; at most 1 of 8 no-bid persona
   attempts does the same.
3. Arm A median coverage lands in the 55–80% band, degrading with tender size; the
   BEST individual attempt on at least 3 tenders reaches ≥ 90% (people are not
   uniformly bad — the point is variance, not incompetence).
4. Fabricated claims: present in ≥ 25% of Arm A attempts; Arm B publishes ZERO
   uncaught fabrications (fabrications the facts-check bounced are reported as caught).
5. Honest negatives, expected and published: Arm A is faster on the 4 simple tenders
   (fewer steps), and its best drafts read at least as well as Arm B's — prose quality
   is explicitly NOT the measured variable and the page says so; Arm B produces at
   least one false block (process has a bureaucratic cost; if zero occur, that is
   reported as a surprise, not claimed as design).
6. Extraction recall (Arm B step 1) between 90% and 99% — i.e. the workflow's model
   layer is imperfect and the gates are what carry it to ≥95% final coverage. If
   extraction alone exceeds 99%, the gates' contribution must be shown some other way
   and that is a reported design weakness.
Any failed expectation is frozen and published, never retuned. Win rate, client
persuasion and real-world time are not measurable here and are never claimed.

## 8. Interactive page (Eva's brief: super interactive)

Single self-contained HTML per house constraints (hpx- prefix, hand-rolled SVG,
validated chart palette, zero external requests now fonts are self-hosted). Three
views:
1. THE WORKFLOW, visualised: a clickable pipeline diagram; pick any tender, walk the
   five steps, see the actual artifact at each step — the matrix filling, the gate
   bouncing a draft (shown live: what bounced, why), the sign-off page. The two
   no-bids show the machine stopping.
2. THE SEVENTY: browse all 64 attempts — persona card, their chat transcript, their
   draft, their marks; filter by tender or persona; the per-tender scatter (attempts
   as dots, Arm B as a line) is the case's signature chart.
3. THE SCOREBOARD: aggregate A-distribution vs B per metric, traps table, the honest
   negatives stated on the page.
4. PLAY A TENDER YOURSELF (committed by Eva, 11 Sep 2026 — "Let's do it!!!"): the
   visitor picks a tender from a curated quick-play set (one simple, one trapped
   medium, one no-bid — full-length gnarly tenders optional for the ambitious), reads
   the real document with annexes collapsed by default (the collapse IS the trap
   mechanism — people don't open annexes), marks the clauses they judge binding,
   calls bid or no-bid, and is scored in the browser against the same held-out answer
   key as everyone else, then placed on the per-tender scatter among the 64 attempts
   and against the workflow's line. Honest rules: identical key, identical marking
   logic (a JS port of mark.py's coverage scoring, spot-checked against it), nothing
   stored and nothing transmitted — the score exists only on the visitor's screen,
   consistent with the trust page. The mode is the thesis experienced: the player who
   misses the annex-buried disqualifier no longer needs the case explained. Detailed
   UI is a Phase 6 design decision; this section commits the mode and its rules.
Size budget: transcripts kept compact (target < 2 MB total page).

## 9. Phases (portfolio convention)

1. Design → EVA GATE (this document — a real one this time).
2. Corpus: config-driven generation of tenders + facts library + answer key
   (deterministic structure; LLM prose for tender text via writer agents with
   may-not-add-or-remove-planted-signals rule); validator with coherence rules.
3. Arm A: 64 persona attempts (Sonnet batches).
4. Arm B: pipeline build + 16 runs.
5. Marking + `data/analysis/report.md` against §7.
6. Writeup (writer/Opus), interactive page, case page + work.html + shapes-page
   exemplum cross-link, DECISIONS entries throughout.

## 10. Open questions for Eva (answer at the gate)

1. Persona cast tone: gently comic habit-diversity is legible and humane — how much
   comedy is allowed before it patronises the fictional staff? (Recommendation:
   habits, never mockery; no persona is stupid, only unstructured.)
2. Sector for the tenders: maintenance/installation services as drafted, or shift
   toward something closer to Hapax's own client profile?
3. The 16/64 scope — content-heaviest build since churn. Comfortable with the volume,
   or trim to 12 tenders × 4?
4. Public-procurement flavour: Finnish-style (hankintailmoitus conventions, referenced
   loosely, no real portal names) or generic-European? (Recommendation: Finnish-
   flavoured, it is the audience's daily reality.)
