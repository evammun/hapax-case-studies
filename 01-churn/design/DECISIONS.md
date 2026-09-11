# Hybrid Churn Intelligence — decision log

Running log of design, data, and code decisions. Newest entries at the bottom.
Project 1 of the portfolio ("ML, but sharper", Theme 1). Plan:
`PLAN-hybrid-churn-intelligence-case-study.md` in this folder.

This log is reconstructed on 11 September 2026 from `design.md` §7's decision
entries, `data/model/ml_report.md`'s preamble narrative, and the delivered
artefacts — the pipeline was built ahead of a formal decision log existing in
the 02/03 format, so this is a retrospective assembly, not a contemporaneous
one. Nothing below is invented; every entry traces to a source named in it.

## Competitor renames (3 Jul 2026)

- **Visby BI -> Storsund BI, Reportify -> Dashlume.** A name check found both
  original invented competitors collided with real products. *Kataja Analytics*
  itself was checked and is clear. `design.md` §2's competitor table and
  `code/config.py`'s `COMPETITORS` dict both ship with the renamed pair.

## Date-clustering defect and the validator's Rule 8

- **A NaN-truthiness bug clustered every non-churning account's tickets into
  the first month of account life**, regardless of total tenure — a disguised
  churn proxy, since a long-tenured survivor's trailing-window ticket count
  would then read as near-zero purely because of *when* its tickets happened
  to be dated, not because the account was quiet. Fixed at source; prose for
  roughly 2,900 non-churn tickets was rewritten to spread realistically across
  each account's life. **Rule 8 was added to `validate_data.py`** to check
  position-in-life spread by archetype and confirm A6's escalation arc still
  lands inside its usage dip window. See `data/model/ml_report.md` item 2 for
  the full before/after diagnostic. The repair tooling for this round
  (`fix_ticket_dates.py`, `make_redate_batches.py`, `merge_redated_prose.py`,
  `apply_patches.py`) is archived per the README, not part of the standing
  pipeline.

## The A4 signal model — four iterations (the published honesty trail)

The entire commercial argument rests on archetype A4 ("quietly unhappy") being
genuinely hard for a usage-metadata model to see. It took four iterations to
get there; each iteration's result is published, including the two that made
things worse. Full detail and the per-run tables live in
`data/model/ml_report.md`; this entry is the narrative summary.

- **v1 (pre-date-fix):** A4 visible to ML at **mean risk score 0.59** (63% in
  the top-100), leaking mainly through visible-dissatisfaction `csat` scores.
  Fix: make csat sparse-and-polite — a disengaged customer skips the survey
  rather than filling it in angry.
- **v2 (post-date-fix, post-csat-fix):** the fix made things *worse* — A4's
  mean risk score **rose to 0.67** (67% top-100). The dominant leak was never
  csat; it was unresolved-ticket metadata (`unresolved_count_6m`,
  `mean_resolution_days_6m`). Fix (`code/fix_a4_ticket_metadata.py`):
  support closes A4's tickets promptly (marked resolved) even though the
  underlying problem does not hold — the realistic "marked resolved, problem
  persists" pattern. Only the `resolved`/`resolution_days` fields changed;
  no ticket prose was touched, since later tickets already say the fix
  didn't hold.
- **v3 (post-close-the-tickets):** visibility rose again, to **0.68** (70%
  top-100). With outcome metadata silenced, the model's weight shifted onto
  ticket VOLUME itself — A4 was generating ~6.65 tickets in the trailing
  6-month window vs A1's ~1.0. **Finding: an account noisy enough to read is
  noisy enough to count.**
- **v4 (Eva's advance directive, 9 Jul 2026):** A4 redesigned as genuinely
  low-volume — 3-6 tickets per account life, ~2.9 in the feature window
  (`code/regenerate_a4_briefs.py`, `A4_LOW_VOLUME_TICKET_PARAMS` in
  `config.py`), each one long, polite, and densely documented; disengagement
  shows as going quiet rather than as traffic. Result: A4's mean risk score
  **fell to 0.477** (50% top-100) — still not fully invisible (residual
  visibility rides on `ticket_count_3m`'s late-crescendo timing and fast
  resolution days), but per the agreed design decision, tuning stopped here
  and the four-run trail is published as the finding rather than chased to
  zero.

## Interactive-page decisions

- **Single self-contained file**, embedded JSON + JS, no server, no build
  step — `interactive/churn_explorer.html`, built by `interactive/build_data.py`
  from the pipeline's own output tables (never source files).
- **Controls**: risk-recipe sliders (usage decline / sentiment / competitor
  weights), a risk-threshold slider, a "usage only" vs "usage + tickets"
  toggle, and click-an-account drill-down to usage curve + ticket history +
  agent narrative — per `design.md` §6.
- **Curated drill-down subset** (documented in `build_data.py`'s docstring):
  all 46 A4 accounts (the money segment, every one included) plus 7
  reproducibly-chosen exemplars each of A1, A3, A5, A6, A7 — 81 accounts get
  full sparkline + ticket text + narrative detail; all 500 get leaderboard,
  2x2, and threshold-counter scores.
- **Embeddability constraints met**: `hpx-` class prefix throughout, one
  external request (Google Fonts), no fixed pixel heights, postMessage height
  reporting — verified mechanically by `code/verify_interactive.py`
  (11 Sep 2026 packaging pass; all checks pass).
- **LinkedIn plan** (per `design.md` §6): posts use screenshots of the page
  and link to the website — the page is the destination, the post is the
  hook.

## Legacy §8 open questions closed (11 Sep 2026)

`design.md` §8 lists four open questions from before the data was built.
Delivery has since answered three of them outright; the fourth is a
recommendation, not yet Eva's decision. Logged here, honestly labelled, per
the 03 Invoices proxy-sign-off convention (a recommendation is recorded as a
recommendation, never as an approval that didn't happen).

- **Q1 (names):** *Kataja Analytics* stands. *Visby BI* and *Reportify* were
  superseded by the 3 Jul 2026 renames above (Storsund BI, Dashlume) before
  any prose was written against them — closed by that decision, not by this
  entry.
- **Q2 (churn rate):** landed at **26.6% (133 of 500 accounts)** — inside the
  design doc's own "~25%" target. Closed by delivery.
- **Q3 (ticket volume):** landed at **3,777 tickets** — inside the 3,500-5,000
  spec (design.md §4) and close to the §8 aim of "~4,000". Closed by delivery.
- **Q4 (extra plants):** **CLOSED as declined — confirmed by Eva, 11 Sep 2026**
  ("okie, nothing else"). The data is frozen at v4; re-planting anything
  further would invalidate every published number in
  `data/model/ml_report.md`, `data/fusion/`, the notebook, and the
  interactive page, all of which cite specific figures against this exact
  dataset. Should a workshop anecdote ever be wanted, the honest options
  remain: an addendum dataset that does not touch the published one, or a
  v5 accepting a full rerun of every downstream figure.
