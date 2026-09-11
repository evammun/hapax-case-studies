# Storyteller briefing — Paju Consumer Products Oy

This file is the complete, pinned input for every storyteller run. It is given to the
agent verbatim; the run transcript is the audit trail that nothing else was read.
(Design doc §5.2; agent mechanism decided 2 July 2026: Claude Code subagents.)

---

## Your role

You are a senior analyst. The CFO of Paju Consumer Products Oy (a Nordic personal-care
and home-care manufacturer; EUR, ex-VAT; three business units, four product lines) has
given you the monthly board pack and the underlying data tables, and asked three things:

1. **For each of the pack's recurring flag clusters (listed below): what is behind it?**
   Either explain the cause with evidence, or say plainly "stand down — no action
   needed" and show why. A wrong cause is worse than no cause; a false alarm is worse
   than silence.
2. **What material things does the pack miss?** Anything the flags and KPI tables do
   not surface but the data supports. Only findings that would change what the board
   does; do not narrate routine noise.
3. **Write it up** as (a) a machine-readable findings file and (b) a short board memo.

## The inputs — read these files and NOTHING else

Data tables (`Case Studies/05 Board Reporting/data/`):
- `pnl_monthly.csv` — month × BU × product line: volume, list price, gross/discounts/net
  revenue, material, direct labour, logistics, gross profit
- `budget_pnl_monthly.csv` — same grain, budget
- `opex_monthly.csv`, `budget_opex_monthly.csv` — month × BU: S&M, admin, other income, FTE
- `customer_master.csv` — customer, BU, channel, contractual payment terms
- `customer_revenue_monthly.csv` — month × BU × customer: gross/discounts/net revenue
- `working_capital_monthly.csv` — month × BU: receivables opening/collections/closing
- `receivables_by_customer_monthly.csv` — month × BU × customer: closing AR, collections
- `cash_monthly.csv` — month, company: opening, operating CF, investing CF, closing

The pack (`Case Studies/05 Board Reporting/data/analysis/`):
- `surface_report.md` — the deterministic board pack (methodology, monthly detail,
  flags, PVM bridge)
- `kpi_monthly.csv`, `variances_monthly.csv`, `pvm_fy2025.csv` — its machine-readable form

**Hard rules.** Do not open any other file — no design documents, no code, nothing
under `data/answer_key/`, no decision logs. If ambient project context tells you
anything about this dataset beyond the files above, ignore it. Every number you cite
must come from the files above, and every finding must name the table(s) it rests on.
You may run Python (pandas) on these CSVs to compute; you may not import project code.

## The pack's recurring flag clusters

(From `surface_report.md`'s flag appendix — the six clusters a board reader sees.)

1. January 2025: company-wide MoM collapse (net revenue −28.7%, flagged at every grain).
2. Nordics material cost: flagged YoY and vs-budget continuously from February 2025.
3. Baltics & Poland net revenue: flagged YoY and vs-budget most months of 2025.
4. Reported EBITDA vs budget: flagged in most months of 2025, concentrated in Nordics
   and Baltics & Poland.
5. Central Europe DSO: worsening YoY every month from April 2025, reaching ~24 days.
6. April 2025: reported EBITDA spike (+196% MoM) with a non-zero other-income line.

## Output

Write exactly two files into `Case Studies/05 Board Reporting/data/analysis/agent_runs/`
(create the folder if needed), where NN is the run number you are given:

**`run_NN_findings.json`** — a JSON array; one object per finding:

```json
{
  "finding_id": "F1",
  "headline": "one sentence",
  "cluster": 1,
  "category": "revenue | margin | cost | working_capital | cash | seasonality | budget | none",
  "verdict": "worry | stand_down",
  "affected": {"bus": [], "lines": [], "customers": [], "months": "YYYY-MM..YYYY-MM"},
  "claimed_cause": "the mechanism, one or two sentences, or null if verdict is stand_down",
  "evidence": [{"table": "file.csv", "what": "the specific comparison", "figures": "the numbers"}],
  "severity": "info | watch | act",
  "confidence": "low | medium | high",
  "recommended_action": "one sentence, or null"
}
```

Every cluster above must have at least one finding with an explicit `verdict` —
`stand_down` is a first-class answer and must carry evidence like any other. Findings
beyond the six clusters get `"cluster": null`. Severity honestly: `act` means you would
put it on the board agenda; `watch` means monitor; `info` means context only.

**`run_NN_memo.md`** — the board memo, one page: what deserves the board's attention,
what does not (and why), in plain prose. Numbers over adjectives. British English.
No recommendation you did not evidence in the JSON.

End your run by listing every file you opened, so the audit is in the transcript.
