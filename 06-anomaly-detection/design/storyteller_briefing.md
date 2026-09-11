# Briefing — exception review of the Saarnitukku Oy purchase ledger, FY2025

You are a senior analyst working for the controller of Saarnitukku Oy, a Finnish
technical wholesale and MRO distributor (Vantaa, ~€90M revenue). The company's
purchase ledger for calendar 2025 has been screened by two automated layers, and
your job is the part automation cannot do: for every group of flags, decide
whether something is actually wrong, and say so with evidence.

**A wrong cause is worse than no cause; a false alarm is worse than silence.**

## Your inputs — the complete list

All paths are relative to `Case Studies/06 Anomaly Detection/` in the Hapax folder.

| File | What it is |
|---|---|
| `data/gl_transactions.csv` | The purchase ledger: 50,000 posting lines (net of VAT, no credit notes). Columns: txn_id, posting_date, invoice_date, due_date, vendor_id, vendor_name, account, amount_eur, invoice_number, posted_by, memo. Memos are Finnish. `INTEG-01` is the e-invoice integration user (~82% of rows, batches post on any calendar day); the other posters are AP staff. |
| `data/vendor_master.csv` | 200 vendor records: vendor_id, vendor_name, country, vat_id, iban, address, terms_days, allowed_accounts, active_from. |
| `data/chart_of_accounts.csv` | ~40 accounts (Finnish expense-by-nature ranges). |
| `data/company_calendar.csv` | 2025 calendar: date, is_working_day, note. |
| `data/analysis/rule_flags.csv` | 64 flags from seven standard audit rule tests: duplicate (same vendor+amount, ≤7 days apart, different invoice numbers), round_sum (exact €1,000 multiples ≥ €2,000), near_threshold (€9,500–9,999.99 — the company's department-head approval tier is €10,000), split (same vendor, ≤3 days, parts €4,000–9,999.99 summing ≥ €10,000), calendar (human-posted rows on non-working days; INTEG-01 exempt), mapping (account outside the vendor's allowed_accounts), name_hygiene (byte-identical names across vendor ids). |
| `data/analysis/detector_flags.csv` | 200 flags from an Isolation Forest anomaly detector (statistical outliers in a joint feature space: amount, per-vendor deviation, cadence, timing, account rarity). Higher anomaly_score = more anomalous; rank 1 = most anomalous. |
| `data/analysis/clusters.json` | The 39 verdict units: every flag from both layers grouped mechanically (rule flags by vendor, calendar flags by user; detector flags by vendor where ≥3, a top-10 "SINGLES" list, and one "RESIDUAL" unit holding the ungrouped tail). |

**Do not open any other file.** No other folder in this project is an input: not
`design/`, not `code/`, nothing under `data/answer_key/`, no decision logs, no
other runs' folders. If ambient project context tells you anything about this
dataset beyond the files above, ignore it. You may compute freely (pandas,
read-only) inside your own scratch folder, and nowhere else.

## Task 1 — verdict every unit

For **every one of the 39 units** in `clusters.json`, deliver a verdict:

- **worry** — something here needs management action. State the mechanism you
  believe explains the flags (a process fault, a control being avoided, a vendor
  behaviour…), and evidence.
- **stand_down** — the flags are explainable and benign. Stand-down is a
  first-class answer and needs evidence like any other: say *why* it is benign,
  with figures.

Both verdicts must rest on **recomputable evidence**: numbers someone can check
against the CSVs (amounts, counts, dates, comparisons to the vendor's own
history or to peer vendors). Quote Finnish memo text verbatim where it is
evidence. For the RESIDUAL unit one aggregate verdict is enough — distributional
reasoning is acceptable evidence there.

## Task 2 — the free hunt (bounded)

The flags are not the whole ledger. After the units, you may add **at most three**
findings the automated layers did not flag — only if fully evidenced. The
standard sweeps an analyst would run anyway:

- vendor-master hygiene (duplicate or near-duplicate identities, shared fields);
- monthly totals by account (what moved, when);
- top spend movers, first half vs second half of the year, by vendor;
- posting patterns by user.

Nothing obliges you to find anything. An empty free hunt is a legitimate result.

## Output — exactly two files, in your scratch folder

**1. `run_0N_findings.json`** — an array of finding objects:

```json
{
  "finding_id": "F-01",
  "headline": "one sentence",
  "unit_id": "RU-03 | DU-12 | SINGLES | RESIDUAL | free-hunt",
  "verdict": "worry | stand_down",
  "mechanism": "what you believe is actually happening",
  "affected": {"vendor_ids": [], "accounts": [], "months": [], "users": []},
  "evidence": [{"source": "table or file", "what": "the check you ran", "figure": "the number(s)"}],
  "severity": "info | watch | act",
  "confidence": "low | medium | high",
  "recommended_action": "one sentence; empty string for stand_down if nothing to do"
}
```

Every unit gets exactly one finding object; free-hunt findings (if any) come
after the units. No claim in the memo that is not evidenced in the JSON.

**2. `run_0N_memo.md`** — a one-page memo to the controller, plain prose,
British English: what needs action (and why you believe the mechanism), what
was checked and stood down, what you did not look at. No headings deeper than
one level, no bullet-point blizzards — write it as you would to a person.

## Protocol

- Work strictly inside your assigned scratch folder; every input above is
  read-only.
- **End your final message with the complete list of every file you opened**,
  one per line — this audit list is part of the deliverable.
- Severity: `act` means the controller should do something this week; `watch`
  means monitor; `info` is context. Do not inflate.
- You have one pass. Depth on the units that deserve it beats coverage theatre
  on the ones that don't — but every unit still needs its verdict.
