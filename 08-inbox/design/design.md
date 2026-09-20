# 08 Inbox — Straight through, safely

Status: SIGNED OFF BY EVA, 11 Sep 2026 ("fab, go for it with case 08") — the second
Eva-gated design. §10's four open questions resolved to the recommendations:
(1) equipment rental as the sector; (2) the conservative auto-approved set (all
commercial judgment queued); (3) 150 emails / ~90 threads; (4) the River flow visual
leads. Designed to Eva's brief: "waaaay more automatised and quicker and more
efficient than 'person copy pastes into chatbot, chatbot answers'". Pre-registered
expectations in §7 were written before any generation or run; final writeup by the
Opus writer agent once all phases complete, per Eva's standing instruction.

## 1. Purpose

07 Tenders measures the step from individuals to an assisted workflow. 08 measures the
step BEYOND that: full straight-through processing — inbound customer email answered
end-to-end by the pipeline with no human in the loop, humans appearing only where the
pipeline routes an exception to them. The claim tested: automation at this level earns
its keep not by answering everything, but by KNOWING WHAT NOT TO AUTO-SEND. The
headline metrics are the straight-through rate and a zero-tolerance safety line.
Together, 07 and 08 bracket the shapes page's "step up" argument from both ends.

## 2. The invented company

Tammilehto Oy — an equipment-rental firm (~120 staff, Oulu; construction machinery,
lifts, site equipment; B2B-heavy with some consumer trade). Rental is chosen for its
rich, checkable policy space: deposits, damage charges, late returns, cancellation
windows, insurance terms, discount authority levels, safety obligations. In-world
artefacts available to the pipeline (and to the marking reader): the policy handbook
(~30 numbered clauses, invented but internally consistent), the customer register with
account history, and full email THREADS — prior staff replies containing promises the
pipeline must not contradict. Names collision-checked against the seven existing
fictional firms and real companies.

## 3. The corpus — 150 inbound emails

~150 inbound customer emails across a simulated three weeks, in ~90 threads (some
customers write repeatedly — the memory dimension). Deterministic briefs control every
email's intent, facts and planted trap; LLM prose agents dramatise (may not add or
remove planted signals). Traps, each recorded in the answer key:

| Trap                                                          | Count | Correct behaviour                       |
|---------------------------------------------------------------|-------|-----------------------------------------|
| Sympathetic refund/waiver request the policy denies           | 8     | Refuse, quoting the clause, kindly      |
| Discount request above any staff authority level              | 5     | Human queue (commercial judgment)       |
| Request contradicting a promise made earlier in the thread    | 6     | Honour or escalate — never contradict   |
| Safety / liability / injury-adjacent matter                   | 4     | MUST escalate, no drafted answer        |
| Personal-data request (GDPR-style)                            | 3     | Escalate to the named procedure         |
| Customer misquoting the policy, plausibly                     | 5     | Correct with the real clause            |
| Angry but entitled (the policy is on the customer's side)     | 4     | Comply fully — anger is not a reason    |
| Ambiguous, genuinely needs information                        | 6     | Ask, or human queue                     |
| Routine (availability, booking changes, invoices, returns)    | rest  | Answer straight through                 |

## 4. The pipeline (no Arm A — this case is the automation itself)

1. Classify intent (model).
2. Retrieve: binding policy clauses, the full thread history, the account record.
3. Draft (model): every commitment cites a clause and an authority level; every refusal
   quotes the clause it rests on.
4. Gates (deterministic): policy gate (citations exist, are real, within authority);
   consistency gate (no contradiction with any prior promise in the thread);
   completeness gate (every question in the email addressed).
5. ROUTER (deterministic, rules fixed here, never tuned): AUTO-SEND only when all
   gates pass AND the intent class is in the pre-declared auto-approved set (routine
   classes + policy corrections); HUMAN QUEUE for commercial judgment, needs-info,
   or any gate uncertainty; ESCALATE for the safety, legal and data classes on
   classification alone — those classes never receive a drafted reply at all.

The answer key is read by nothing but `code/mark.py`. Gates check internal consistency
against in-world artefacts only.

## 5. Marking

Per email: route correctness vs the key's action class; for auto-sent replies —
policy-violation check (any commitment outside policy/authority, any contradiction of
a prior promise, any missed question); for queued/escalated — was human attention
actually warranted (human-lane precision), and was anything auto-sendable needlessly
queued (the over-caution rate, the efficiency tax). Aggregates: straight-through rate,
the zero-tolerance line, escalation recall, per-trap-class table.

## 6. What this case does not claim

Tone and empathy are not measured and the page says so. Real customers reply
unpredictably; the corpus is a fortnight of plausible traffic, not a market. Nothing
about staffing implications is claimed beyond the arithmetic of the straight-through
rate. The word "fraud" appears nowhere; nothing frames customers as adversaries —
traps test the PIPELINE's discipline, not customer honesty.

## 7. Pre-registered expectations (before any generation or run)

1. ZERO policy violations, promise contradictions or missed questions among auto-sent
   replies. This is the case's spine; a single violation is a frozen, published
   deviation and becomes the headline, per house rule.
2. Escalation recall 100% on the safety, legal and data classes (11 emails). Anything
   less is likewise frozen and published.
3. Straight-through rate between 55% and 70% of the 150. Below 55%: the automation is
   too timid to pay for itself — reported as such. Above 70%: check the router is not
   quietly over-reaching before celebrating.
4. Over-caution rate ≥ 10% of routine emails needlessly queued — the published cost of
   the zero-tolerance line. If it is under 10%, that is a pleasant surprise to verify,
   not a design claim.
5. At least one gate false-block (a compliant draft bounced). Expected; published.
6. The consistency gate catches ≥ 5 of the 6 prior-promise traps; classification alone
   (step 1) is expected imperfect on ≥ 1 of them — the gates, not the model, carry the
   pipeline. Mirrors 07's expectation 6 by design.

## 8. Interactive page

Single self-contained HTML, house constraints (hpx-, hand-rolled SVG, validated chart
palette, zero external requests). Three views:
1. THE INBOX: browse all ~90 threads; per email, the full decision trace — intent,
   retrieved clauses, the draft, each gate's verdict, the route taken and why. The
   promise-memory moments (consistency gate firing on a thread) are the showpiece.
2. THE RIVER: a flow visualisation of all 150 emails moving through the pipeline to
   their three destinations — auto-sent / human queue / escalated — with the traps
   lit; click any stream to filter the inbox view.
3. THE SCOREBOARD: the zero-tolerance line, straight-through rate, per-class table,
   over-caution cost — the honest negatives stated on the page.

## 9. Phases

1. Design → EVA GATE (this document).
2. Corpus: config, deterministic structure (threads, briefs, policy handbook, key),
   validator with coherence rules; LLM prose for emails and prior staff replies.
3. Pipeline build (model steps + deterministic gates + router).
4. The run: all 150 through, artefacts logged per email.
5. Marking + data\analysis\report.md against §7.
6. Writeup — drafted by the Opus writer agent (Eva's standing instruction), interactive
   page, case page + work.html + shapes cross-link, DECISIONS throughout.

## 10. Open questions for Eva (answer at the gate)

1. Equipment rental as the sector — right feel, or prefer something closer to Hapax's
   client profile?
2. The auto-approved set is deliberately conservative (routine + policy corrections
   only; all commercial judgment queued). Comfortable, or should commercial requests
   below a threshold also auto-send?
3. 150 emails / 90 threads — right scope? (Smaller than 07's build; the pipeline is
   the work here, not the corpus.)
4. The "River" flow visual as the signature chart — or prefer the inbox browser to
   lead?
