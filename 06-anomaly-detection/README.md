# 06 Anomaly Detection — "The flags that mattered"

Case 6 of the Hapax portfolio (Theme 3, the data storyteller — 05's bottom-up
sibling). **Complete — all six phases, 3 July 2026.** A synthetic Finnish purchase
ledger (Saarnitukku Oy, fictional; 50,000 rows, seed 42) is screened by seven
sourced audit rule tests and an Isolation Forest; three blinded agent runs triage
every flag; all three layers are marked against a held-out answer key. The honest
headline: the rules caught everything rule-shaped, the detector caught nothing
planted (a frozen, diagnosed, pre-registered deviation), and the drift story the
case is named for was caught by nobody — which is the case's actual argument.

A follow-on drift-report phase ("06b") is being built separately and is not part of
this copy — see the note at the end of this file.

## Pipeline (run from this folder)

```
python code/generate_ledger.py          # 4 public tables + data/answer_key/anomalies.csv (seed 42)
python code/validate_ledger.py          # 13 coherence rules; exits 1 on any failure
python code/run_rule_layer.py           # -> data/analysis/rule_flags.csv (64 flags, pre-registered)
python code/detect_anomalies.py         # -> detector_flags.csv + detector_scores.csv (200 flags; self-checks determinism)
python code/prepare_clusters.py         # -> data/analysis/clusters.json (39 verdict units)
# 3 blinded Claude Code subagent runs, pinned briefing design/storyteller_briefing.md
#   -> data/analysis/agent_runs/run_0N_findings.json + run_0N_memo.md
python code/evaluate.py                 # mechanical marking -> evaluation.json + evaluation_worksheet.md + scores CSV
# data/analysis/report.md = the adjudicated scorecard, written by hand from the worksheet
python code/build_interactive_data.py   # distils results -> interactive/_data.json (asserts vs evaluation)
python code/merge_interactive_data.py   # inlines the JSON into the self-contained page
python code/verify_interactive.py       # page QA gate (19 checks); exits 1 on failure
```

Notebook: `python -m nbconvert --to notebook --execute --inplace notebooks/anomaly_detection_analysis.ipynb`
(re-reads every number live; 23 asserts on the headline figures).

## ⚠️ What regenerates and what does not

**Deterministic (safe to re-run, byte-identical on the pinned environment):** the
generator, validator, rule layer, detector (seeded, `n_jobs=1` — pinned
scikit-learn 1.9.0 / scipy 1.18.0 / numpy 2.5.0 / Python 3.12.6; version drift can
change detector output), cluster prep, evaluation, interactive data prep and page QA.

**NOT regenerable — session artefacts, treat as data:**
`data/analysis/agent_runs/` (the three runs' findings JSONs, memos, and scratch
folders) were produced by blinded Claude Code subagent runs (Opus) on 3 July 2026.
Re-running them means new agent sessions with the pinned briefing, and results
WILL differ — that variance (37/35/38 of 39) is part of the published result.
`data/analysis/report.md` is the hand-adjudicated scorecard of those specific runs.

## Where things live

| Artefact | Location |
|---|---|
| Design doc (gate proxy-passed by Luigi 3 Jul 2026; as-built notes in §4) | `design/design.md` |
| Domain research, sourced [S] vs inferred [I] | `design/audit_research.md` |
| Decision log — every review round and correction stays in | `design/DECISIONS.md` |
| The pinned agent briefing (given verbatim to each run) | `design/storyteller_briefing.md` |
| Generation + detection + evaluation code, build notes | `code/` |
| Public dataset (4 tables) | `data/*.csv` |
| Answer key — held out of every analysis and agent-facing path | `data/answer_key/anomalies.csv` |
| Flags, clusters, agent runs, worksheet, adjudicated scorecard | `data/analysis/` |
| Executed analysis notebook (incl. the labelled post-hoc detector v2) | `notebooks/` |
| Interactive page (single self-contained HTML) + its data | `interactive/anomaly-detection.html` |
| Canonical long-form writeup | `writeup/anomaly_detection_case_study.md` |

## Environment

Python 3.12 with pandas, numpy, scikit-learn 1.9.0 (pinned — recorded in
`design/DECISIONS.md`); the notebook additionally needs matplotlib, nbformat,
nbconvert, ipykernel. No API keys anywhere — portfolio decision.

## The one-line result

Rules 48/64 flags on plants at the designed 75% first-pass precision with 100%
recall on every rule-shaped class; detector 0/200 on anything planted (frozen,
diagnosed deviation); agents 37/35/38 of 39 verdicts with all 78 detector-unit
stand-downs correct, the cross-record vendor-trio story found 3/3 — and the
case's namesake drift story caught by nobody, which is why the answer key exists.

## Note on 06b

A drift-report follow-on phase ("06b") was in progress elsewhere at the time this
public copy was staged. Its design note (`design/design-06b-drift-report.md`) and
any `code/06b_*` / `data/06b/` artefacts are excluded from this copy because the
06b findings report (`data/06b/report.md`) did not yet exist at staging time. This
project's public copy reflects the complete, six-phase 06 case only.
