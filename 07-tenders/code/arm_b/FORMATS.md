# Arm B artifact formats

These are the three JSON artifacts a run-agent (or, for the dry test, a
fixture) produces per tender, per design.md S5. The harness (`gates.py`,
`router.py`) reads and writes these; it never edits `matrix.json` or
`response_v*.json` — those are the run-agent's own work, revised only by the
run-agent itself in response to a `gate_report_N.json`.

Directory convention: one run per tender under `data/arm_b/run_NN/`, where
`NN` is the same two-digit number as the tender (`run_05/` answers `T05`).
Nothing in this folder is generated yet — this file specifies the contract
the future run-agents and `code/arm_b/gates.py` / `router.py` share.

## Run directory contents

```
data/arm_b/run_NN/
  matrix.json          # step 1 output (extraction), written once
  response_v1.json     # step 2 output (draft), first attempt
  gate_report_1.json   # gates.py verdict on response_v1.json
  response_v2.json     # revision, only if gate_report_1 bounced
  gate_report_2.json
  ...                  # up to response_v5 / gate_report_5 (RUNBOOK.md cap)
  signoff.json         # router.py's terminal artifact
```

## `matrix.json` — the extracted requirement matrix

A **top-level JSON array**, one object per requirement the run-agent found in
the tender document:

```json
[
  {
    "matrix_id": "M001",
    "clause_label": "3.1",
    "text": "The tenderer must hold a valid RALA qualification...",
    "kind": "eligibility",
    "location": "body"
  },
  {
    "matrix_id": "M014",
    "clause_label": "A.2",
    "text": "Description of spare parts availability and delivery time...",
    "kind": "technical",
    "location": "annex:Annex A"
  }
]
```

Field notes:

- `matrix_id` — `"M"` + 3-digit zero-padded sequence, `M001`, `M002`, ...,
  assigned in the order the run-agent extracted the requirements. Must be
  unique within the matrix. (This mirrors the answer key's `req_id` shape,
  e.g. `T01-R001`, without being the same namespace — the run-agent never
  sees `req_id` values, so `matrix_id`s are the extraction's own numbering.)
- `clause_label` — **the document's own numbering**, verbatim (`"3.1"`,
  `"A.2"`, `"6.2"`), so a human can find the clause in the source tender. If
  a requirement is genuinely unlabelled in the source (buried in passing
  prose, no clause number of its own — the corpus's `hidden_form` trap is
  exactly this case), `clause_label` is `null`, matching the answer key's own
  convention for `mentioned_once` rows.
- `text` — the requirement, quoted or closely paraphrased from the tender.
  Extraction is the run-agent's own reading; it never sees `answer_key/`,
  `clause_map_NN.json`, or `data/arm_a/`.
- `kind` — one of `eligibility | technical | commercial | form | format`.
- `location` — `"body"` or `"annex:<annex name as printed in the tender>"`
  (e.g. `"annex:Liite A - Tekninen erittely"`, matching the corpus's own
  `location` convention in `answer_key.csv` exactly, so the marking script
  can compare them later without a translation layer).

## `response_v{N}.json` — the drafted response

```json
{
  "rows": [
    {
      "matrix_id": "M001",
      "answer_text": "Visakoivu Oy holds a valid RALA qualification...",
      "citations": ["certifications.RALA"]
    }
  ],
  "no_bid": false,
  "no_bid_reason": null,
  "general_sections": {
    "cover_letter": "...",
    "company_overview": "..."
  }
}
```

Field notes:

- `rows` — one entry per `matrix.json` row the draft addresses. A
  `matrix_id` with no entry in `rows` (or an entry whose `answer_text` is
  empty/whitespace) is an **unanswered row** for the coverage gate.
- `citations` — a list of **fact paths** into `company_facts.yaml`, one per
  fact actually relied on in `answer_text`. Every specific factual claim in
  `answer_text` (a € amount, a headcount, a certification/standard name, a
  year count) must be traceable to one of this row's citations. See
  "Fact-path syntax" below.
- `no_bid` / `no_bid_reason` — set `no_bid: true` and give a reason when the
  matrix contains a requirement Visakoivu cannot meet. The coverage gate
  accepts a no-bid run with unanswered rows only if `no_bid_reason` names
  those rows' `matrix_id`s.
- `general_sections` — free-form front/back matter (cover letter, company
  overview, etc.) not tied to one matrix row. **Known limitation, flagged
  rather than fudged**: `general_sections` has no citations field, so the
  facts gate does not (and structurally cannot) fact-check it. A fabricated
  claim placed in `general_sections` instead of a row's `answer_text` would
  not be caught by `gates.py`. This is recorded in `DECISIONS.md` and in the
  build report as a gap in §5's coverage, not silently patched over by
  inventing a citations field the spec never asked for.

### Fact-path syntax

A fact path is a dotted string that walks `company_facts.yaml`:

- A plain key on a dict: `"company.employee_count"`.
- A key on a list-of-dicts, addressed by that item's natural identifier
  (`code` for `certifications`, `id` for `reference_projects`, `kind` for
  `insurances`, `year` for `financials`), case-insensitively:
  `"certifications.RALA"`, `"reference_projects.REF02.value_eur"`,
  `"insurances.liability.cover_eur"`, `"financials.2025.revenue_eur"`.
- A plain dict key for `staff_by_discipline`: `"staff_by_discipline.LVI"`.
- `"references"` is accepted as an alias for the real top-level key
  `"reference_projects"` (the design brief's own example used `references.
  REF02.value_eur`; the corpus's actual YAML root is `reference_projects` —
  the resolver in `gates.py` accepts either so a run-agent following the
  brief's example verbatim still resolves correctly).

`gates.py resolve_fact_path()` implements this and is the single source of
truth for what "resolves to a real path" means for the facts gate.

## `gate_report_{N}.json` — one gate invocation's verdict

```json
{
  "pass": false,
  "iteration": 1,
  "gates": {
    "coverage": true,
    "facts": false,
    "consistency": true
  },
  "coverage_pct": 100.0,
  "bounces": [
    {
      "gate": "facts",
      "type": "FABRICATION",
      "matrix_id": "M004",
      "detail": "claim 'ISO/IEC 27001' in answer_text is not supported by any cited fact (citations: ['certifications.RALA'])"
    }
  ],
  "checked_at": "2026-09-11T00:00:00Z"
}
```

`pass` is `true` only if all three gates pass. `bounces` is empty iff `pass`
is `true`. The harness never edits `response_v{N}.json` in response to a
bounce — the run-agent reads `bounces`, revises **only what is named**, and
writes `response_v{N+1}.json`.

## `signoff.json` — the one-page terminal artifact

Written once, by `router.py`, after gates pass or the run is a clean no-bid,
or after the iteration cap is hit:

```json
{
  "tender_id": "T01",
  "status": "submitted",
  "bid_no_bid": "BID",
  "coverage_pct": 100.0,
  "gates_passed": true,
  "bounce_count": 2,
  "iterations": 2,
  "unresolved_flags": [],
  "no_bid_reason": null
}
```

- `status` — `"submitted"` (bid, gates passed), `"no_bid"` (no-bid, gates
  passed), or `"stuck"` (iteration cap hit without a pass — recorded
  honestly, not forced to a false pass; see RUNBOOK.md).
- `bid_no_bid` — `"BID"`, `"NO_BID"`, or `"UNRESOLVED"` (only for `"stuck"`).
- `bounce_count` — total number of individual bounce entries across every
  `gate_report_N.json` in the run (cumulative, not just the last iteration).
- `unresolved_flags` — e.g. `["max_iterations_exceeded"]` when stuck, plus
  any bounce types still open in the final gate report for a stuck run.
