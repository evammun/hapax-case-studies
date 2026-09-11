# Hapax case studies

The complete pipelines, datasets and held-out answer keys behind the six case
studies published at [hapax.fi](https://hapax.fi) — an AI advisory and training
boutique in Helsinki. Each folder is one case: the generator that built the
dataset, the code that ran the method, the results, and the analysis, in full.

| Case | What it does | Page |
|---|---|---|
| [`01-churn/`](01-churn/) | A usage-based churn model combined with an agent that reads support tickets | [hapax.fi/case-churn.html](https://hapax.fi/case-churn.html) |
| [`02-erp-cleanup/`](02-erp-cleanup/) | A language model reads legacy ERP spool files; an overseer writes deterministic parsers and keeps the model only for exceptions | [hapax.fi/case-erp-cleanup.html](https://hapax.fi/case-erp-cleanup.html) |
| [`03-invoices/`](03-invoices/) | The same overseer method run on a year of supplier PDF invoices | [hapax.fi/case-invoices.html](https://hapax.fi/case-invoices.html) |
| [`04-contracts/`](04-contracts/) | An overseer learns which CUAD contract-clause categories are boilerplate and writes matchers for them, keeping the model only for the bespoke residue | [hapax.fi/case-contracts.html](https://hapax.fi/case-contracts.html) |
| [`05-board-reporting/`](05-board-reporting/) | A deterministic variance pack says what moved in the numbers; three blinded agent runs say why | [hapax.fi/case-board-reporting.html](https://hapax.fi/case-board-reporting.html) |
| [`06-anomaly-detection/`](06-anomaly-detection/) | Audit rule tests and an Isolation Forest screen a purchase ledger; three blinded agents triage every flag | [hapax.fi/case-anomaly-detection.html](https://hapax.fi/case-anomaly-detection.html) |

Each case folder has its own `README.md` with the exact commands to run its
pipeline, and a `design/` folder with the design doc and running decision log.

## The method, in one paragraph

Each case runs a method end to end on data engineered so that the right answer
is known in advance and held out of the pipeline throughout, which is what lets
every result be marked against ground truth rather than asserted. Company names,
customers and datasets are fictional unless stated otherwise; nothing here
describes or implies a real client. One case, `04-contracts`, runs on real
documents — 150 SEC-filed contracts from CUAD v1, a public dataset released by
The Atticus Project — marked against CUAD's own attorney annotations rather than
an answer key we wrote ourselves. Negative results are kept in: where a method
missed something, the miss is reported next to the catch, not edited out.

## Regenerate vs artefact — read this before re-running anything

Two different kinds of file live in these repos, and they are not interchangeable:

- **Deterministic code and data** — generators, validators, evaluation scripts,
  and the datasets they produce — are seeded (`RANDOM_SEED = 42` throughout) and
  byte-identical on re-run. Safe to regenerate any time.
- **LLM-produced artefacts** — the model's reads, the parsers or matchers an
  overseer agent wrote, the blinded analysts' findings — are the output of a
  specific agent session on a specific date. Re-running the agents produces
  *different* output (same task, different words or judgement calls), which
  would silently invalidate every number published in that case's findings
  report, notebook, and interactive page. These are treated as data, not as
  code to refresh, and are checked into each repo alongside the pipeline that
  produced them.

Every case's own `README.md` says exactly which of its files fall into the
second category — look for the ⚠️ section before running anything end to end.

## Licence

Code (`code/`, `notebooks/`, build scripts) is MIT-licensed — see `LICENSE`.

The synthetic datasets, generated prose, and case-study writeups are
© Hapax Oy, released under CC BY 4.0 — see `LICENSE-DATA.md`.

`04-contracts/data/answer_key/` and `04-contracts/data/manifest.json` are
Hapax adaptations of CUAD v1's `master_clauses.csv` (© The Atticus Project),
also under CC BY 4.0; the governing attribution and citation are in
`04-contracts/data/CUAD_LICENCE_ATTRIBUTION.md`. CUAD's raw contract archive
itself is not redistributed here — `04-contracts/data/contracts/` holds the
150-contract sub-corpus this case uses, and `data/manifest.json` carries the
source URL and checksum for the full archive.
