Canonical case study. Drafted by case-drafter, edited in the main loop (Opus tone pass), 3 July 2026. Website, training and LinkedIn material derive from this file.

# Board Reporting Automation

## A pack that is right and still incomplete

A competent finance team's monthly board pack is usually correct. Material costs up 12%, gross margin down 2 points, and the number is right. What the pack rarely carries is the cause. The cause usually sits three drill-downs below the line item, in a table nobody has time to open before the meeting starts. So the obvious explanation goes into the commentary – "input cost inflation", "seasonal", "on plan" – the board moves on, and if it is wrong, the real cause keeps costing money for another two quarters, unremarked.

This case study tests whether an AI layer, working from the same numbers the finance team already has, can close that gap. It has to find the cause behind a flagged variance, or say plainly that a scary-looking number needs no story at all.

## Built to be marked, not asserted

Everything in this case study is synthetic. Paju Consumer Products Oy is a fictional Nordic personal-care and home-care manufacturer (3 business units, 4 product lines, roughly €155M net revenue and 480 people in the base year) generated in full by a seeded Python model. It is not a real company, and none of the figures below describe a real client's data.

Four stories were planted into the driver model before a single agent saw the data, each with a designed mechanism, magnitude and answer, held out in a separate answer key file the agents never touch. A Nordics margin move that reads as commodity inflation is actually a discount-and-mix shift into a material-heavy product line. In Central Europe, a warehouse sale-and-leaseback keeps reported EBITDA on plan while one customer's payment terms quietly drift out underneath it. Baltics revenue growth turns out to be substantially bought with escalating discounts. And the fourth story is a trap. January shows a revenue collapse that is pure seasonality, identical to the prior year and to budget – the kind of number a jumpy analyst could easily narrate into a crisis.

We built it this way for the same reason we build every case study this way, so that results can be marked against a known answer, not asserted. The trap exists specifically to catch an agent crying wolf, and we publish the result whichever way it lands.

## Two layers, not one

The case study runs two layers over the same data.

The first is deterministic (pandas, not an agent). It computes budget-vs-actual and year-on-year variance at company and business-unit grain, decomposes revenue and cost moves into price, volume and mix, tracks the standard KPI set, and flags anything that breaches a threshold. This layer is fast, exact and free to run, and it was built properly, not left as a strawman for the agent layer to beat. Run over the full two-year dataset, it raises 327 mechanically correct flags. It attributes zero of them. That is not a flaw in the code. A threshold breach is a fact about a number, not an explanation of one.

The second layer is 3 independent storyteller runs (Claude Code subagents, not a fine-tuned model) each given an identical pinned briefing, the nine public data tables and the deterministic pack, and told to use nothing else. None saw the answer key. The runs were sequential and blinded. Each was barred from the earlier runs' output and ended its transcript with a list of every file it opened, so the audit trail can be checked independently; all three lists contain only permitted files, and none opened the answer key, the design documents, or another run's work. No API costs were metered because the runs executed inside a subscription session, so this case study claims no cost figure for the agent layer. The gap is honest; the alternative would be an invented number.

Each run had three jobs. For every one of the pack's six recurring flag clusters it had to explain the cause with cited evidence, or say "stand down" and show why. Beyond the clusters, it had to surface anything material the pack missed, and write the whole thing up as a findings file plus a one-page board memo. A wrong cause counts against a run. So does a false alarm.

## What the storytellers found

All three runs, independently, landed on the same three board actions and the same three stand-downs.

All three found the Nordics margin story. Every run reported flat unit material costs – the decisive fact the pack itself cannot see, since it never computes cost per unit – and traced the 11.5% material-cost rise to a promotional discount that jumped in a single month, Nordics Home Care from 6.0% to 18.8% of gross, alongside a volume shift into the material-heavy line. All three filed the material-cost flag itself as "stand down, not a procurement problem" and moved the real finding into a margin flag instead, a sharper split than the design brief expected.

The Central Europe receivables story was designed to be the hardest of the four, since it requires connecting four tables while every headline metric looks fine. It was also found intact by all three runs. Each named Rheinkauf Gruppe, the business unit's largest customer, from the per-customer receivables table, and cited the same figures for it – a receivable balance that more than doubled over the year, from about €2.06M to €4.49M. Each linked the April sale-and-leaseback (a €2.2M other-income gain, €5.5M cash) to the flattered headline, and each computed a cash-conversion deterioration once the one-off was stripped out; one run put the underlying operating-cash fall at about €3.4M against a €3.9M build in receivables.

Baltics growth turned out to be bought, and all three runs said so. The pack's headline read as good news – company revenue up 8.6%, ahead of plan – but a disproportionate share of it traces to one business unit, Baltics & Poland, where revenue rose 27% funded by discounting that escalated from around 8% to 17% of gross. One run went further and quantified the combined cost directly. Across Nordics and Baltics together, discounting handed back about €5.9M in FY2025 against holding 2024 rates, split roughly €3.6M and €2.3M between the two, a figure that checked out on verification.

The trap held too. All three runs correctly stood down on the January collapse, a 28.7% month-on-month drop that reads as alarming in isolation, citing the same seasonal pattern present in the prior year and in budget. No run cried wolf anywhere else in the dataset either.

Across all 3 runs (30 findings in total) there were zero false positives at watch severity or above, and not one cited figure that turned out, on adjudication, to be wrong. A mechanical check flagged eighteen apparent figure disagreements across the runs; each turned out to be a correct number quoted on a different, clearly labelled basis. One soft spot should be recorded. One run's headline compressed "December EBITDA down 39.5% year-on-year" into "down about 40% year-on-year," which reads as a full-year claim – the actual full-year fall was 8.1% – though the finding's text underneath was accurate. A pack of agent findings needs to be read past the headline.

## What they missed, and why it matters more than the wins

The Baltics story is where the design's two sharpest pieces of evidence went unclaimed by all three runs. The dataset was built so that three of the business unit's ten named accounts – Balticum Retail, Polska Handlowa and Sūduvos Prekyba – carry discount rates above 18% by the end of the period, and so that the volume response per euro of discount fell by roughly 38% between the first half of the year and the second, the signal that the growth strategy is running out of road. Every run found that discounting was buying the growth. No run pulled either exhibit. One run even checked customer-level revenue concentration, found it broad, and stopped one column short of checking discount concentration instead.

Separately, a structural budget-optimism bias – the budget quietly assumes slightly better performance than the business delivers, every month, in every business unit – was noted correctly by exactly one of the three runs, which pointed out that EBITDA had missed budget by 8.2% in FY2024 too, before any discounting, and put the standing planning bias at roughly a third of 2025's budget gap. The other two runs attributed the whole of 2025's budget miss to that year's real drivers, which is defensible, since underlying EBITDA did genuinely fall 13.7% year-on-year, but incomplete.

We kept this finding in. A single, one-pass agent investigation finds the mechanism behind a flagged variance reliably. It does not reliably go looking for evidence nobody pointed it at. That is the argument for checking before believing. A run that reads confidently and cites real numbers can still leave the second-best half of a case on the table, and the only way to know that is to check it against an answer you already have.

## What transfers to a real ledger, and what does not

The mechanics here would run the same way against an actual monthly close: a deterministic variance layer first, doing the arithmetic it is good at and nothing it is not; independent, blinded agent passes next, each required to commit to a verdict, worry or stand down, with evidence for every flag, not just the interesting ones; then a systematic check of what came back against ground truth.

What does not transfer is the ground truth itself. A real client's ledger has no answer key. That is exactly why this exercise runs on synthetic data first, to build the habit of marking an agent's findings against something known, rather than believing a confident memo because it reads well and cites real-looking numbers. The honest conclusion is not "the agents got it right". It is that three independent, checked runs agreed on the three findings that mattered for board action and on both stand-downs, and that even three-for-three still left the sharpest evidence in two of the four stories unclaimed. A deployment on real data needs that checking discipline built in from the start, because there will be no answer key there to catch what a single pass misses.

## Appendix

The pipeline runs in five steps from `Case Studies/05 Board Reporting/`. `generate_financials.py` builds the nine data tables and the held-out answer key from a seeded driver model (`RANDOM_SEED = 42`, byte-identical on every run); `validate_financials.py` checks all twelve coherence rules and exits with failure on any breach, with every total reconciling to the cent; `variance_analysis.py` produces the deterministic board pack; three blinded Claude Code subagent runs, using the pinned briefing at `design/storyteller_briefing.md`, produce the findings files and memos; `evaluate.py` marks all three runs against the answer key into a mechanical worksheet; the adjudicated scorecard this write-up draws from, `data/analysis/report.md`, was then written by hand from that worksheet, and everything that went wrong stays in it.

All code, all generated data, the answer key and the full evaluation worksheet are public in the case study folder. The analysis notebook (`notebooks/board_reporting.ipynb`) walks the pipeline end to end. The interactive page (`interactive/board-reporting.html`) lets you step through a month of the pack, see what it flagged, and compare that against what the storyteller runs found.
