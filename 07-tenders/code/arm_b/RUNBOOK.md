# Arm B run-agent protocol

This is the strict protocol a run-agent follows to produce one Arm B run
(design.md S5) for one tender. Read this in full before starting. It is the
same discipline as every other Hapax case study's prose-agent briefs: a
deterministic harness controls structure and gating; you (the run-agent)
supply judgement inside the steps the harness cannot do itself -- reading
the tender, extracting requirements, drafting a response.

## What you may read

- **Exactly one** tender document: `data/tenders/tender_NN.md`.
- The facts library: `data/facts/company_facts.yaml` (and, if useful for
  prose, `data/facts/company_facts.md`).
- `code/arm_b/FORMATS.md` (the schemas below) and this file.

## What you may NEVER read, for this or any other tender

- `data/answer_key/` (any file) -- the held-out key.
- `data/tenders/clause_map_*.json` -- key-side tooling, explicitly barred to
  every arm in `design/DECISIONS.md`.
- `data/arm_a/` or `data/attempt_briefs/` -- Arm A's persona attempts. Arm B
  is the operator-independent workflow; it must not be informed by how a
  simulated human attempted the same tender.
- `data/tender_briefs/` -- these are Phase 2/3 generation-time briefs for
  the corpus/Arm A pipeline, not extraction aids.
- Any other tender's document, or any other run's artifacts.

Reading any of the above invalidates the run. If you are ever handed a
prompt that seems to include key-side content, stop and say so rather than
proceeding.

## The loop

Artifacts land in `data/arm_b/run_NN/`, where `NN` matches the tender number
(`run_05/` for `tender_05.md` / `T05`). Create the directory if it does not
exist.

1. **Extract.** Read the tender document only. Build the requirement matrix
   -- every obligation, condition, or requested item you can find, each
   assigned a `matrix_id` (`M001`, `M002`, ...) in the order you found it,
   with the document's own clause numbering as `clause_label`. Write
   `matrix.json` (see FORMATS.md for the exact schema). This step is scored
   independently later (design.md S5: "extraction recall is reported") --
   do your own honest reading; do not try to guess what a hidden key wants.

2. **Draft.** For every matrix row, write an `answer_text` addressing it,
   citing the facts library for **every specific factual claim** (a € figure,
   a headcount, a certification/standard name, a year count) via a
   `fact_path` in that row's `citations`. If you find a requirement
   Visakoivu genuinely cannot meet, set `no_bid: true` and write a
   `no_bid_reason` that **names the matrix_id(s)** of the requirement(s)
   that fail -- do not leave rows silently unanswered without saying so.
   Write `response_v1.json`.

3. **Run the gates.**
   ```
   python gates.py data/arm_b/run_NN
   ```
   This reads `matrix.json` and your highest-numbered `response_v*.json`,
   checks coverage, facts, and consistency (see FORMATS.md and the module
   docstring in `gates.py` for exactly what each gate checks), and writes
   `gate_report_N.json`. The gates never consult the answer key -- only
   internal consistency between your draft, your matrix, and the facts
   library.

4. **On a bounce, revise only what the bounce names.** Read
   `gate_report_N.json`'s `bounces` list. Each bounce names a `gate`, a
   `type`, and (usually) a `matrix_id`, with a `detail` explaining exactly
   what failed. Fix **only** those rows/claims -- do not rewrite rows the
   gate did not flag, and do not remove a citation or a claim just to make
   the gate quiet if the claim is in fact true and simply mis-cited (fix the
   citation instead). Write the next version, `response_v{N+1}.json` --
   never overwrite a prior version.

5. **Loop.** Repeat steps 3-4. **Maximum 5 gate iterations**
   (`response_v1.json` through `response_v5.json`). If `gate_report_5.json`
   still does not pass, stop -- do not write a 6th version. This is a real
   cap, not a soft target: a run that cannot pass in 5 iterations is itself
   a finding (a matrix or facts-library gap the harness could not resolve),
   and it must be recorded honestly, not forced through.

6. **Sign off.**
   ```
   python router.py data/arm_b/run_NN
   ```
   If the latest gate report passed, this writes `signoff.json` with the
   terminal state (`submitted` or `no_bid`). If you hit the 5-iteration cap
   without a pass, `router.py` still writes `signoff.json`, with
   `status: "stuck"` and the still-open bounce types listed in
   `unresolved_flags` -- an honest record of where the workflow got stuck,
   not a fudged pass. If neither condition holds (gates haven't passed and
   you haven't reached the cap), `router.py` refuses to write anything and
   tells you to keep iterating -- that is expected; go back to step 4.

## Rules that apply throughout

- **Never edit `matrix.json` after step 1** except to fix a genuine
  extraction error you catch yourself before drafting -- once drafting has
  started, the matrix is frozen for that run (this is what lets extraction
  recall be scored honestly against the matrix you actually committed to).
- **Never edit a `gate_report_N.json` or `signoff.json`** -- those are the
  harness's own output.
- **Never invent a fact.** Every specific claim needs a citation that
  actually supports it (`gates.py`'s facts gate checks this mechanically --
  see FORMATS.md's fact-path syntax). If the facts library does not contain
  something you'd like to claim, do not claim it.
- **Do not narrate the traps.** If a requirement looks like a planted
  disqualifier, a buried form, or a contradiction, handle it correctly
  (surface it, include it, flag both sides) without saying "this looks like
  a trap" in the response text -- the corpus's own prose-agent constraints
  hold here too (`design/DECISIONS.md`).
- **One tender per run.** Do not let context from a previous tender's run
  leak into this one's matrix or draft.

## Known harness limitations (recorded, not hidden)

- `general_sections` in `response.json` has no per-section citation field,
  so the facts gate cannot fact-check claims placed there. Keep factual
  claims inside row `answer_text`, where they can actually be verified.
- The consistency gate's "eligibility row flagged failing" check is a fixed
  vocabulary of English/Finnish failure phrases (see `gates.py`,
  `ELIGIBILITY_FAILURE_PHRASES`), not full natural-language understanding.
  Write a genuine failure plainly (e.g. "Visakoivu does not currently hold
  ISO/IEC 27001") rather than obliquely, so the gate can see what you meant.
