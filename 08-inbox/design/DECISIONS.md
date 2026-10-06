# Inbox Automation case study — decision log

Running log of design, data, and code decisions. Newest entries at the bottom of each
section. Project 8 of the portfolio ("Straight through, safely"). Plan:
`PLAN-inbox-automation-case-study.md` at the project root.

## Gate passed (11 Sep 2026)

Eva's own sign-off — not a proxy gate. Her words: **"fab, go for it with case 08."** The
design doc's four open questions (§10) resolved to the design's own recommendations,
which Eva endorsed as written rather than amending:

1. **Equipment rental as the sector — kept.** Chosen for its rich, checkable policy
   space (deposits, damage, cancellation, insurance, discount authority, safety) — the
   right feel, no change requested.
2. **The auto-approved set stays conservative** — routine classes + policy corrections
   only; all commercial judgment (discount requests) is queued for a human regardless of
   how the gates read. This is the deliberate spine of the "knowing what not to auto-send"
   claim, not a compromise.
3. **150 emails / ~90 threads — right scope.** Smaller than 07 Tenders by design: the
   pipeline is the work in this case, not the corpus.
4. **The River flow visual leads** the interactive page, per design §8.

## Seed choice

`RANDOM_SEED = 8` — the eighth case in the portfolio numbering, no other significance;
chosen once and never re-rolled. All Phase 2 generation is a single seeded
`random.Random(8)` instance threaded through every draw (dates, customer assignment,
trap-scenario selection, staff assignment) — no unseeded randomness anywhere in
`generate_structure.py`. Regeneration verified byte-identical (SHA-256 over the whole
`data/` tree) across two consecutive runs.

## The intent-class taxonomy (Phase 2 interpretation, flagged for Phase 3 confirmation)

The design doc's router rules (§4) name three buckets — auto-approved (routine classes +
policy corrections), human-queue (commercial judgment, needs-info, gate uncertainty), and
escalate (safety, legal, data, on classification alone). It does not spell out a full
intent-class taxonomy, so Phase 2 had to pick one to make the answer key's routes
mechanically derivable. The taxonomy adopted, one intent class per trap type (plus plain
"routine" for the untrapped remainder):

| Intent class          | Trap type(s)                              | Bucket        |
|------------------------|-------------------------------------------|---------------|
| `routine`               | plain routine; refund_denial; angry_entitled | auto-approved |
| `policy_correction`     | policy_misquote                           | auto-approved |
| `commercial_discount`   | above_authority_discount                  | human-queue   |
| `prior_promise`         | prior_promise_contradiction                | human-queue   |
| `needs_info`            | needs_info                                | human-queue   |
| `safety`                | must_escalate_safety                      | escalate      |
| `data_request`          | data_request                              | escalate      |

Two things worth Luigi/Eva's eyes before Phase 3 locks the pipeline's own classifier:

- **`refund_denial` and `angry_entitled` are classed as `routine`, not as a separate
  "refusal" or "commercial" class.** The reasoning: a correctly-grounded refusal citing a
  denial clause is not a judgment call — it is the same skill as answering any other
  routine question, and the whole point of the refund-denial trap is that the automation
  should confidently auto-send the refusal rather than caving to sympathy or bouncing it
  to a human out of caution. Same logic in reverse for angry-entitled: full compliance,
  citing the clause, is the correct auto-send outcome regardless of tone. This makes the
  key's *ideal* auto-approved bucket large (126 of 150, 84%) — deliberately not the same
  number as the design's pre-registered 55–70% straight-through range in §7.3. That range
  is a claim about the **actual Phase 4/5 pipeline run** (which will lose ground to
  classification error and designed gate conservatism — see the over-caution rate,
  §7.4), not a structural property of the Phase 2 key. Recorded here so nobody mistakes
  the 126-figure for a violated pre-registration later.
- **§7.2 refers to "the safety, legal and data classes (11 emails)"**, but §3's trap
  table only lists a safety/liability row (4) and a data-request row (3) — 7, not 11. No
  standalone "legal" trap row exists in §3. Phase 2 does not invent one: introducing a
  fourth escalate-on-classification bucket without a design-doc mandate would be adding
  structure the sign-off never specified. The most likely reconciliation is that some of
  the 6 prior-promise-contradiction traps are expected to resolve to `escalate` (not
  merely `human_queue`) once a real draft is attempted and found to require a
  policy exception a human cannot approve on the spot — which would only be decidable at
  Phase 3/4, not from the structural brief alone. Phase 2 keeps all 6 prior-promise traps
  as `human_queue` in the ideal key (simpler, defensible, and consistent with §4's "never
  contradict" framing, which reads as a human decision, not an automatic escalation).
  **Flagged for Luigi/Eva to confirm at Phase 3 gate**: either accept `human_queue` as
  final for all six, or designate a subset as `escalate`-eligible once the consistency
  gate's actual behaviour is built. Nothing downstream depends on resolving this before
  Phase 3 starts.

Ideal-key route distribution as built: **auto_send 126, human_queue 17, escalate 7**
(sums to 150). `config.route_for_intent()` is the single function both the generator and
`validate_structure.py` call, so the two can never silently disagree — Rule 6 of the
validator checks every one of the 150 rows against it directly.

## The clause-binding consistency mechanism

Every trap type that leans on the policy handbook is bound to a specific, named subset of
clause ids in `config.py`, and `validate_structure.py` (Rule 3) checks every single brief
against that subset — not just a sample:

- `DENIAL_CLAUSE_IDS = [H-02, H-06, H-09, H-13, H-16]` — every refund_denial brief's
  `denying_clause_id` must be one of these five, and each is independently a genuine
  denial (deposit forfeiture, damage charges final, late fee not waived, late-cancellation
  forfeiture, DWC exclusions).
- `CUSTOMER_FAVOURING_CLAUSE_IDS = [H-05, H-14, H-24, H-29]` — every angry_entitled
  brief's `favouring_clause_id` must be one of these four, each unambiguously in the
  customer's favour (pre-existing damage, company-caused cancellation, confirmed
  equipment fault, price lock). Cycled 1:1 across the four angry_entitled instances, no
  repeats.
- `MISQUOTE_SCENARIOS` pairs each of the 5 policy_misquote instances with the one real
  clause that contradicts the customer's false claim — checked 1:1, no repeats.
- `above_authority_discount` requests are validated to exceed
  `MAX_DISCOUNT_AUTHORITY` (15%, the Regional Manager ceiling — the highest of any role)
  by construction (`build_facts_above_authority_discount` redraws until this holds, and
  the validator checks it independently rather than trusting the generator).
- The 6 prior-promise threads each carry their planted promise **structurally** in the
  thread JSON (the staff message immediately preceding the trap email, with a `promise`
  block whose `promise_id` matches the brief's `facts.promise_id`) — validated by walking
  every thread's message list and confirming the match, not just checking a promise
  exists somewhere.

This means the coherence rules are checked against the *actual generated data*, not
re-derived from the same generation code — a bug in `generate_structure.py`'s trap logic
would still be caught by `validate_structure.py`'s independent clause-membership checks.

## Name-check results

Config's `PORTFOLIO_FIRMS_TO_AVOID` list carries the seven existing case studies'
fictional firms (Jalavakoski Konepaja, Pyökkipaja, Saarnitukku, Paju Consumer Products,
Kataja Analytics, Sammalkoski, Visakoivu — one per prior case, 01 through 07). All 25
invented customer names plus "Tammilehto Oy" itself were checked programmatically
(case-insensitive substring match, both directions) in `validate_structure.py` Rule 7 —
**clean, no collisions.** The customer roster deliberately avoids the tree/plant-name
convention used for each case's primary invented company (Tammilehto itself follows it —
"tammi" + "lehto", oak grove), so there is no risk of a customer name reading as another
case's protagonist company. Customer names were also checked for internal duplicates
(none) — 15 business accounts (Oulu-region construction/rental-adjacent naming) and 10
consumer accounts (personal Finnish names), matching the design's B2B-heavy-with-consumer-
trade framing.

## Build notes (11 Sep 2026)

- `must_escalate_safety` and `above_authority_discount` traps are restricted to business
  customers at thread-assignment time (a consumer injury-on-site or a consumer requesting
  a "three-month standing hire" discount would read as implausible) — implemented as a
  candidate-pool filter in `pick_customer()`, not a post-hoc swap, so it is exact rather
  than probabilistic.
- Thread message counts: the 6 prior-promise threads are fixed at exactly 2 customer
  messages (a routine "setup" ask, then the trap redemption ask, with the planted staff
  promise between them). The other 84 threads share the remaining 138 emails with sizes
  1–4, distributed by seeded random increment from a floor of 1 each — this is what
  produces "some customers write repeatedly" without forcing every thread to the same
  length.
- A small (6%) weekend-email allowance exists for consumer accounts' opening thread
  message only (`WEEKEND_EMAIL_FRACTION` in config) — real inboxes do not stop over the
  weekend, and only a consumer plausibly emails off-hours; every later message in a
  thread stays on a business day regardless.
- PyYAML was not previously a dependency anywhere in the Hapax tree except 07 Tenders
  (built concurrently by another agent, confirmed by grep before adding it here) — reused
  rather than avoided, `pip install pyyaml` (6.0.3) run against the system Python
  (3.11.8, `C:\Users\evama\AppData\Local\Programs\Python\Python311`) used for this build.

## 20 Sep 2026 — Phase 3 (prose) opened; email-writer agent created

Phase 3 begins on Eva's "go for it" (20 Sep). Corpus prose runs on the external writer's model (Opus 4.6) under corpus-specific rules, following the case-10 precedent Eva set on 18 Sep for the application corpus: a dedicated agent, .claude/agents/email-writer.md, brief-is-law, never AI-flavoured, the writing guide explicitly not applied to corpus documents. Tooling (build_prose_tasks.py, assemble_emails.py, validate_emails.py) built by python-builder this session; ambiguities it reports land here before any writer batch runs.

## 20 Sep 2026 — Phase 3 tooling built; five interpretive decisions logged

build_prose_tasks.py / assemble_emails.py / validate_emails.py built and round-trip tested (synthetic writer in an isolated scratchpad copy; planted-promise break and vocabulary leak both caught, exit 1). 16 batches under data/prose_batches/, whole-thread-packed, 150 customer emails + 53 staff messages. Five ambiguity resolutions, endorsed as consistent with house method: (1) the batching unit is the thread, never split, so a promise's setup and redemption are always authored together; (2) the canonical corpus data/emails/ + data/threads_prose/ strips intent_class, trap_type, facts and the structured promise block — ground truth reaches Phase 4 only as prose, per the standing leak discipline (flagged for Eva/Luigi review before Phase 4 is built against these files); (3) internal handbook codes (H-NN) banned from assembled prose; (4) verbatim-locatable enforced as hard verbatim for numeric/code facts and closed-set keyword match for descriptive facts; (5) "routine" excluded from the forbidden-vocabulary scan as ordinary English, all other internal tokens banned. Writer batches (email-writer, Opus 4.6) launch in waves.

## 20 Sep 2026 — Phase 3 complete: 16/16 batches, validation passed after four validator-side adjustments

All 16 email-writer batches (Opus 4.6) landed complete: 150 customer emails + 53 staff messages, all 6 planted promises dramatised and redeemed, every trap carried per brief. assemble_emails.py: clean, no structural problems. First full validate_emails.py run flagged 12 items; triage found ALL were validator false positives, no prose defect: (1) one-word subject "Discount" — inbox realism, MIN_SUBJECT_WORDS relaxed 2 -> 1, empty still fails; (2) the word "safety" in a genuine electric-shock complaint — ordinary English, excluded from the forbidden-vocabulary scan exactly as "routine" already was (snake_case class tokens stay banned); (3) ten routine request_kind signals "not locatable" — writers dramatised availability/return requests naturally ("wondering if you've got a site cabin I could rent?", subject "Returning the tower light") while the checker scanned only the body with single-keyword sets; Rule 3 now scans subject+body and the two routine keyword sets widened to natural-phrasing stems. No email prose was modified. VALIDATION PASSED on rerun; corpus is frozen as written. Phase 4 (pipeline build) is next.

## 20 Sep 2026 — Phase 4 built; seven implementation resolutions endorsed

Pipeline built per design section 4 and fixture-tested (27 pure unit checks + 20 integration assertions in an isolated scratchpad copy, 47/47 passed; escalate shortcut verified to carry draft null / gates null). Deterministic: retrieval.py, gates.py, run_gates_and_router.py. LLM stages as task files: build_classify_tasks.py (already run: 150 tasks, 10 batches) and build_draft_tasks.py (runs after classify_raw lands). Resolutions endorsed as consistent with the method: (1) classify sees only the trigger email, so its imperfection stays genuine for expectation 6; (2) retrieval includes the full 30-clause handbook, no lossy filtering — retrieval recall is not the claim under test; (3) every non-escalate class gets a draft, including always-queued classes, so the gates generate false-block data across the whole queue population; (4) gates match over the draft's structured self-report (typed commitments with citations, per-prior-message treatment tags, per-question answered flags) — the case-04 model-extracts/matcher-decides idiom; a dishonest self-report is exactly what marking against the key can expose; (5) classify and draft are separate stages so escalate classes never generate a draft; (6) fixed batch size 15 for both stages; (7) policy citations required for refusal / waiver_or_discount / correction commitment types only. Nothing reads data/answer_key/; mark.py stays its only reader.

## 20 Sep 2026 — Phase 5 model choice: both LLM stages on Sonnet

Design section 4 marks classify and draft as "(model)" without pinning one. Both run on Sonnet: the house default for pipeline implementation work, and the right register for the case's claim — the pipeline is deliberately ordinary and the gates, not the model, carry the safety (section 7 expectation 6 anticipates classification staying imperfect even so). Classify runs first, 10 batches.

## 20 Sep 2026 — Phase 5 run complete, frozen as ran

Classify: 10/10 batches (Sonnet), 150/150 emails, 7 shortcut to escalate (safety + data_request). Draft: 10/10 batches (Sonnet), 143/143 drafts, every batch reporting per-prior-message treatment tags; notable self-flagged judgment calls preserved as run data (EML-069 conditional honour of an unbounded price-match; EML-130 deposit waiver honoured under a stretched H-20 citation; EML-081 H-22 whole-thread reading). Gates + router: deterministic pass over all 150, decisions in data/pipeline/decisions/ (one trace per email), routing_summary.csv written. Route counts as ran: auto_send 122, human_queue 21, escalate 7 — against the ideal-key 126/17/7. Nothing read the answer key; mark.py (Phase 6) will be its only reader. No reruns.

## 20 Sep 2026 — marking complete: 3/6 met; five marking-judgment calls, DRAFT verdicts pending Eva

mark.py built and run (--require-complete, 150/150; gate function verified by deliberate removal test). Scorecard: (1) MET zero gate violations among 122 auto-sends; (2) MET escalation 7/7 — scored against the 7 planted safety/data emails, the section-7.2 "11 emails" figure being the pre-logged Phase 2 discrepancy; (3) NOT MET straight-through 81.3% vs the 55-70 band, exceeded from ABOVE — traced to 6 needs_info emails misclassified routine and auto-sent, all content-checked non-inventive; (4) NOT MET over-caution 8.26% vs the >=10% bar, the design's own "pleasant surprise" direction; (5) MET 7 completeness-gate false blocks, listed; (6) NOT MET both halves — the consistency gate never fired (0/6: no draft ever attempted a contradiction, all six promises honoured upstream) and prior_promise classification went 6/6 against the expected miss. Intent accuracy 140/150. Route confusion: 10 over-cautious, 6 under-cautious, 0 escalation misses either direction. Trap table: discounts 5/5, promises 6/6, safety 4/4, data 3/3, misquotes 5/5, angry-entitled 4/4, needs_info 0/6 on route (safe content), refund_denial 5/8. DRAFT verdicts on the five marking calls, pending Eva's sign-off: (a) EML-002 is a corpus defect published as ours — the brief's trap cites H-02 forfeiture against a 5-days-late fact that never crosses H-02's own 7-day threshold; the draft read the real clause correctly; scored trap-content miss, not violation; (b) EML-024's deferred refusal scored as a content miss as ran; (c) needs_info reported both ways (canonical human_queue route vs design section 3's "Ask, or human queue" allowance), zero invention verified across all six; (d) expectation 6 scored literally — a gate that never fires is unexercised, not validated — with the loose 6/6 safe-outcome number published beside it; (e) over-caution numerator counts needless queueing by any mechanism, components reported separately. Frozen as ran; no reruns.

## 20 Sep 2026 — five marking verdicts signed off (Eva: "Yep, go for it"); Phase 6 writer stage begins

All five draft verdicts accepted as drafted: EML-002 published as a corpus defect (trap cited H-02 against a fact below its own threshold; pipeline policy-correct); EML-024 content miss as ran; needs_info reported both ways with zero invention verified; expectation 6 scored literally (unexercised, not validated), loose number published beside it; over-caution counted across both mechanisms. Writeup, interactive page and site integration proceed on the frozen numbers.

## 20 Sep 2026 — Phase 6 complete: writeup, explorer, site integration

writeup/inbox_automation_case_study.md (1,957 words) written by the writer from the frozen scorecard and verified in main-loop review against every marked number. interactive/ built on the 09/10 pattern (build_data.py -> _data.json 460 KB -> inbox.html 512 KB; river Sankey cross-asserted against marks.json at build time; headless-Chrome verified, zero exceptions). Writer strings pass done in the template and rebuilt. Site: case-inbox.html + explorer-inbox.html (three logged divergences + noindex), work.html gains a Customer operations group with the tenth entry, nine -> ten count sweep across work/notes/shapes/index/answer-key/training, sitemap and _verify.py updated, ALL CHECKS PASSED. README.md and PLAN status complete. Open items for Eva: writeup read-through, interactive look-and-feel pass.

## 6 Oct 2026 – Invented names renamed after the legal check

Spec: `Set Up/Legal/invented-names-check-2026-10-06.md` section 3; replacements were cleared against the registers and approved by Eva ("happy for things to get renamed without me, they're all fictional names"). Mapping and tooling: `Set Up/Legal/rename_mapping.py`, `apply_renames.py`, `rename_sweep.py`. 
- Two customers in the register (Rovaniemi and Vehmaa road and earthworks firms) shared their names with real registered companies: Napapiirin Infra Oy is now Routakallion Infra Oy, and Pohjolan Maanrakennus Oy is now Kurujärven Maanrakennus Oy. Only the nominative forms occur.
- Patched by literal swap in `code/config.py`, `data/customers`, `email_briefs`, `emails`, `emails_raw`, `pipeline`, `prose_batches`, `threads`, `threads_prose` and the interactive files. The email-writer, classification and draft outputs were not re-run.
- `data/emails/prose_manifest.csv` holds body character counts; `assemble_emails.py` was re-run and the manifest regenerated, so the counts follow the longer names (counts changed on affected rows only).
- **Checks.** `generate_structure.py` in a scratch copy reproduces the structure byte for byte against the patched files. `validate_structure.py`, `validate_emails.py`, `run_gates_and_router.py` and `mark.py` re-run with every output byte-identical to the patched files. No published figure moved.
