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

## 6 Oct 2026 – Invented names renamed after the legal check

Spec: `Set Up/Legal/invented-names-check-2026-10-06.md` section 3; replacements were cleared against the registers and approved by Eva ("happy for things to get renamed without me, they're all fictional names"). Mapping and tooling: `Set Up/Legal/rename_mapping.py`, `apply_renames.py`, `rename_sweep.py`. 
- **Roster swap.** The 319 generated account names were common surnames plus a legal form, which the national registers hold as real companies (Dahl AS, Aalto Oy, Braun GmbH and so on). `COMPANY_PREFIXES_BY_COUNTRY` in `code/config.py` now carries the cleared stems, position by position and at the same list length, so `rng.choice` draws the same index and a regeneration gives the same dataset with only the names changed. Mid-words and suffixes are unchanged. Stems repeat by design (account_id is the key; nothing groups by name). Old names are not recorded here beyond the legal file.
- **Headline account kept.** `HEADLINE_NAME_OVERRIDES = {"ACC0013": "Bergvik Systems AB"}` in `config.py`, applied in `generate_structured.py` after the name draw. The other Bergvik accounts took the SE stem for that position.
- **Applied to the data by mapping, not by re-running anything session-made.** `data/accounts.csv`, `interactive/_data.json`, `_template.html`, `churn_explorer.html`, `interactive/staging/*`, the executed notebook (5 names in its outputs) and both writeups were patched with the identical old-to-new map. Tickets, briefs and agent outputs carry no account names (checked), so nothing else moved.
- **Checks.** `generate_structured.py` run in a scratch copy reproduces `accounts.csv` and `answer_key.csv` byte for byte against the patched files. (`usage_monthly.csv` does not reproduce in the current Python environment, as before this change; the file in the tree is untouched.) `validate_data.py` passes all rules. `fuse_and_evaluate.py`, `tiebreak_before_after.py` and `build_data.py --staging` were re-run in the scratch copy and every output (`data/fusion/*`, `interactive/staging/*`) is byte-identical to the patched files, so every figure in the "after" column of `tiebreak_before_after.md` is unchanged. `verify_interactive.py` passes.
- **For the writer.** `writeup/case_study.md` and `case_study_draft.md` name two accounts beyond Bergvik, which changed with the roster (Nieminen Oy is now Lumikarpalo Oy; Willems Group B.V. is now Zeggeveld Group B.V.). The site's case page does not mention them. The pending site splice of the tie-break data carries the new names through `interactive/staging/_data.json`.
- **Open.** Danish stems were checked on the web only (the CVR register refused automated access); a manual look on virk.dk is still advisable.
## Explicit tie-break for every top-N cut (6 Oct 2026)

**A method clarification recorded after publication, not a retune.** No data, model, score, seed or agent output changed. The only thing that changed is how an existing tie is resolved when a ranked list is cut.

**The defect.** The ticket-text agent's account score has only 33 distinct values. The text layer's top-100 cut falls inside a tie: 23 accounts score 0.55 and occupy ranks 95 to 117, so six of them make the list. The pipeline used a stable sort, which broke ties by the row order of `accounts.csv`. Which six made the list therefore depended on nothing but how the data was laid out. The webpage-editor found it on 6 Oct 2026 while fixing the explorer's quadrant chart. The usage and combined scores are continuous and have no tie at rank 100 (the top-50 text cut also sits in a tie, of 19 accounts, but resolves to the same set under either rule).

**The rule.** Implemented once, in `code/ranking.py`, and used by `code/fuse_and_evaluate.py`, `code/train_models.py` and `interactive/build_data.py` (and mirrored in the explorer's JavaScript for the live mixer).

- Text arm: score descending, then most recent ticket date descending (a more recent concern ranks above an older one at equal score), then account id ascending. Recency stays inside the text layer, so the usage and text arms remain independent.
- Combined arm: the same rule, since that arm already reads ticket data.
- Usage arm: score descending, then account id ascending. Recency is left out so the usage arm never reads a ticket field. This is a small reading of "the same explicit rule" and it changes no figure, because the usage score has no tie at the cut.

`fuse_and_evaluate.py` now also validates that each top-100 flags exactly 100 accounts and that the flagged set is identical under a shuffled row order. `combined_scores.csv` gains `ml_rank`, `text_rank` and `combined_rank` columns so the explorer reads ranks from the pipeline and never re-sorts scores itself.

**Before and after** (`data/fusion/tiebreak_before_after.md`, produced by `code/tiebreak_before_after.py`, which reproduces the old behaviour exactly before comparing). Three accounts swap on the text top-100.

| Figure | Before | After |
|---|---|---|
| Recall@100, text layer | 59.4% (79 of 133) | 58.6% (78 of 133) |
| Recall@100, usage | 59.4% | 59.4% (unchanged) |
| Recall@100, combined | 66.2% | 66.2% (unchanged) |
| Regions: both / usage only / tickets only / neither | 58 / 42 / 42 / 358 | 59 / 41 / 41 / 359 |
| Churned ARR caught by text top-100 | EUR 4,349,027 | EUR 4,137,013 |
| Churned ARR the text layer surfaces that usage does not | EUR 1,340,728 | EUR 1,140,868 |
| Churned ARR usage surfaces that text does not | EUR 703,350 | EUR 715,504 |
| A4 accounts in the text top-100 | 35 | 34 |
| A7 accounts in the text top-100 / rescued from the combined list | 20 / 19 | 19 / 18 |

Unchanged: AUC and average precision for every arm, every top-50 figure, usage and combined recall and ARR at top-100, the combined top-100 and its worth-saving split, and the headline 0.867 to 0.890 AUC and 59% to 66% recall@100 lift.

**What the old figure was.** One arbitrary draw from a spread. Any six of the 23 tied accounts could have filled the slots; across 20,000 seeded random draws, text recall@100 ranged from 57.9% to 62.4% and the text-only ARR figure from EUR 1.14M to EUR 1.54M. The rule lands at the low end of both ranges. It drops ACC0045, ACC0062 and ACC0130 (the last an A4 churner worth EUR 199,860) in favour of ACC0183, ACC0283 and ACC0382, whose last tickets are more recent (Aug to Sep 2025, against Oct 2024 to Apr 2025). The rule was fixed before its outcome was computed. The old "text and usage each catch 59.4%" coincidence was an artefact of the tie and no longer holds.

**Not regenerated.** `data/tickets_raw/`, `data/agent/assessments_raw/`, `text_scores.csv` and `narratives.json` are untouched. `train_models.py` was re-run to confirm the rule is a no-op there (`ml_scores.csv`, `shap_values.csv` and `features.csv` came out byte-identical); the hand-edited `data/model/ml_report.md` was restored afterwards and should not be regenerated, since the script's text for three paragraphs is older than the hand edits.

**Published surfaces still carrying the old figures** (flagged here, not edited): the website explorer and case page, `work.html`, `writeup/case_study.md` and `case_study_draft.md`, and the executed notebook. The regenerated explorer is staged at `interactive/staging/churn_explorer.staging.html`; the standing `interactive/churn_explorer.html` and `_data.json` are the pre-fix build.
