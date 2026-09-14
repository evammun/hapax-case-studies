Canonical case study. Drafted by case-drafter, edited in the main loop (Opus tone pass), 3 July 2026. Website, training and LinkedIn material derive from this file. Companion piece to `02 ERP Cleanup/writeup/case_study.md`.

# Supplier by supplier, the automation that retires itself

*The company, the suppliers and every invoice below are invented; the measurements are real, marked against an answer key written before any parsing ran.*

## The problem

Pyökkipaja Oy is a Lahti contract-furniture manufacturer, about 120 employees, making fitted furniture for offices, schools and hotels across Finland and the Nordics. Its large domestic suppliers invoice it through structured e-invoicing, straight into the ledger, roughly how 85% of Finnish B2B invoicing works. What still lands in the accounts-payable inbox as a PDF, keyed by hand, is everything e-invoicing does not reach: a German fittings supplier, a Swedish fabric house, an Estonian steel shop, 5 smaller domestic firms, and a long tail of one-off suppliers who invoice once or twice a year and then not again. This residue is a minority of invoices and most of the manual effort.

We built a synthetic corpus around that shape, 198 PDF invoices across 2025, from 8 repeat suppliers and 18 one-offs, following the EU VAT directive’s content rules and the relevant national formats, marked against an answer key holding the true value of every field. The question is the one our advisory page poses as an exemplum. Can a system learn, supplier by supplier, which invoices to automate?

## What happened, in numbers

| Measure | Result |
|---|---|
| Corpus | 198 invoices, calendar 2025, 26 suppliers (8 repeat, 18 one-off) |
| Deterministic share, whole stream | 117 of 198 documents, 59.1% (pre-registered target 60.6%) |
| LLM-path field accuracy | 100.0000% (5,427 fields, 81 documents, zero errors) |
| Deterministic-path field accuracy | 100.0000% excluding one planted silent error; 99.9757% including it (8,223 fields, 117 documents) |
| Overall field accuracy | 99.9853% (13,650 fields; 2 wrong, both from the same document) |
| Suppliers automated vs volume automated | 8 of 26 suppliers (31%) carry 178 of 198 invoices (90%) |
| Cost, year 1, hybrid vs all-LLM (central estimates) | ~$9.05 vs ~$9.61, about 6% saved |
| Cost, year 2, same stream (central estimates) | ~$1.31 vs ~$9.61, about 86% saved |

## How it works

An agent (a Claude Sonnet subagent, reading each PDF as an image) returns a structured record of header fields, line items and totals, against one shared schema. This is the expensive step, and the only one that can handle an invoice it has not seen before. It held up well. Dense identifiers (IBANs, reference numbers, OCR codes, VAT IDs in 5 languages) came back correct across all 81 agent-read documents, without a single digit wrong.

An overseer watches what the agent produces, supplier by supplier. Once a supplier has sent 6 invoices in a consistent layout, it writes an ordinary deterministic parser for that layout, plain code against the PDF’s text layer with no model at run time. The new parser must first reproduce the agent’s own accepted output on every document seen so far before it goes live. A router sends each invoice to a deterministic parser where one exists, checks the schema, the arithmetic and the master data, and falls back to the agent, loudly, if anything does not fit. This is the mechanism our ERP case study, *The automation that retires itself*, demonstrated on 5 SAP report types; here the unit of learning is the supplier, the literal version of “supplier by supplier”.

## What the year showed

8 of the 26 suppliers earned a parser and carry 178 of the 198 invoices, 90% of the volume. The other 18, each invoicing once or twice a year, stay on the agent by design, because automating a single annual invoice would cost more to build than it would ever save. The ceiling here is set by the supplier base, not by parser quality.

One supplier switched invoicing software on 1 August and changed its layout. Its parser refused the new invoices rather than guess; 6 fell back to the agent, the overseer learned the new layout, and a second parser went live in late October. Same rule as the first learning, no special case required.

The stream also produced an exhibit nobody planned. Two suppliers occasionally send two-page invoices, but the parsers written for them were induced from single-page examples only, so they refuse a second page and fall back. Four invoices fell back unplanned, and at three documents and one per layout they will never reach the 6 needed to re-learn, so they stay with the agent for good. It is the clearest evidence for the design’s own claim: a parser that has not seen a shape does not invent one.

One planted trap failed to trap. A freight invoice carried a fuel-surcharge line with no product code, built to break its supplier’s parser and force a fallback. That parser derives its columns from the document itself, not from a fixed layout assumption, and read the unfamiliar line as ordinary data. 3 of the 4 planted breakers worked as designed; this one did not, and we reported it.

The one error nothing catches is the one built to survive every check. A packaging invoice prints a quantity and unit price transposed at the source: 50 units at €2,00 where the true order was 2 units at €50,00. The line total, €100,00, is identical either way, so the arithmetic passes and the parser accepts it without complaint. Only the answer key, holding the true transaction, sees the error. In production the safeguard is a three-way match (invoice against purchase order against goods receipt) and this document is the argument for running one on every invoice, however cleanly it parses.

## What it cost

The year’s tokens came to 1,885,139: 818,868 for the 81 agent-read invoices (about 10,100 each, since reading a PDF as an image runs roughly 7 times what plain text cost in our ERP case study) and 1,066,271 for the 9 parser-writing runs. At published Sonnet prices ($3/$15 per million tokens, banded from an all-input floor to an all-output ceiling, central estimate at an 85/15 split), the hybrid pipeline cost an estimated $9.05 against $9.61 for reading every invoice with the agent, about 6% saved.

That 6% is not the honest headline. Writing the 9 parsers cost an estimated $5.12, almost exactly what they saved in their first year of use (about $5.67 across the 117 documents they replaced). Year 1 is close to a wash by design. The parsers had to earn out their own construction cost before saving anything outright. In year 2 of the same stream, with the parsers already written, the agent would only be needed for 27 documents (the one-off tail plus the handful of fallbacks that never reach the re-learning threshold) for an estimated $1.31 against $9.61, about a seventh of the cost, repeating every year after. The crossover, not the year-1 total, is the number that matters.

Two caveats apply throughout. Introductory Sonnet pricing ($2/$10) was actually in force on the date these figures were measured, which would cut every number here by roughly a third; we used list prices instead, for comparability with our ERP case study. The token counts also include the harness’s own overhead, so a purpose-built extractor would likely cost less on both sides. It is the ratio between hybrid and counterfactual we would stand behind, not the dollar figures themselves.

## What transfers and what does not

In production there is no answer key to mark against. The check we ran on ours makes that point directly. Running real parses against a key we had written earlier turned up 4 defects in the key, not in the parsing: a payment-terms phrase that did not match its own configuration, null bank fields left out, a German register number filed against the wrong court, and a signed-zero artefact surfaced by the credit-note reads. All four were ours, none the agents’. Anyone running this method against a real inbox should expect the same: whatever source you are marking against is worth testing before you trust it.

What generalises is the steady-state claim, that a supplier with a parser costs nothing to parse from the day it is born, because it follows from how the overseer works, not from anything about Lahti furniture or 2025’s VAT rates. What does not generalise is the shape of the tail, the accuracy figures and the cost curve; those depend on how many suppliers you have and how many send more than a handful of invoices a year. The invoices, the answer key and the code that parsed them are published in full. The numbers above are not a promise about your inbox. They are one run of a method, against data built to have a known right answer.
