# CUAD dataset research — Project 4 (Contract Clause Extraction)

Compiled 3 July 2026. Source tags: **[S]** sourced (document cited), **[S-fig]** read visually from a published figure (approximate), **[M]** measured by us on the frozen archive, **[I]** inferred. A first scout sweep (Haiku, 3 Jul 2026) located the sources; everything below was verified or measured personally in the main loop.

## 1. What CUAD is [S]

The Contract Understanding Atticus Dataset (CUAD) v1: 510 commercial legal contracts, manually labelled with 13,000+ annotations identifying 41 categories of clauses "that lawyers look for when reviewing contracts in connection with corporate transactions" (M&A, investments, IPOs). Curated and maintained by The Atticus Project, Inc. Contracts sourced from SEC EDGAR — public filings by US-listed companies, 25 contract types, randomly selected within type across filing-company alphabet. [S: `CUAD_v1_README.txt` in-archive; https://arxiv.org/abs/2103.06268]

The paper reports the labelling effort as the work of dozens of law students under attorney supervision, with a value "over $2 million" if priced at prevailing legal rates [S: paper abstract/intro]. The labelling process is a documented seven-step pipeline: student training (~70–100 h), manual labelling in eBrevia, keyword-search sweep for missed labels, category-by-category report review, attorney review to consensus, a machine-assisted "extras" review loop repeated to exhaustion, and final export [S: README, "Labeling Process"].

## 2. Acquisition record [M]

| Item | Value |
|---|---|
| Source | Zenodo record 4595826 (`https://zenodo.org/records/4595826/files/CUAD_v1.zip?download=1`), 3 Jul 2026 |
| Size | 105,883,672 bytes |
| MD5 | `c38f490a984420b8a62600db401fafd5` — **matches the published Zenodo checksum** |
| SHA-256 | `88b694d99007d39777fa44cd72daf8297773d285dc3eab0091ba32078888d18e` |
| Cache | `C:\Users\luigi\Documents\datasets\CUAD_v1\` (machine-local; recoverable anywhere from URL + checksums) |

Alternative routes (not used, recorded): the Atticus Project site (`atticusprojectai.org/cuad`), GitHub `TheAtticusProject/cuad` (code + trained model, not the corpus), HuggingFace `theatticusproject/cuad` and `cuad-qa`. [S: scout sweep 3 Jul 2026]

## 3. Archive structure [S: README; M: verified on extraction]

- `master_clauses.csv` — 83 columns × 511 rows (header + 510 contracts): `Filename`, then per category a clause-text column (annotated spans, a Python-list-like string) and an `-Answer` column (normalised answer). **The recommended starting point per the README.** This is our answer-key source.
- `full_contract_txt/` — 510 plain-text contracts (the LLM path's input and the matchers' input).
- `full_contract_pdf/` (Part_I–III) — 510 PDFs, "raw data … for context and reference"; not used by our pipeline (stay in cache, out of the tree).
- `CUAD_v1.json` — SQuAD 2.0-style QA derivation of the CSV (paragraph-level spans); not used (we work contract-level, like the underlying review task).
- `label_group_xlsx/` — 28 per-category label reports; not used by the pipeline (reference only).
- `CUAD_v1_README.txt` — categories, answer-format rules, redaction conventions, labelling process, licence.

## 4. The 41 categories and the answer model [S: README]

**8 extraction categories** (answers are names/dates/durations/jurisdictions, normalised to unified formats): Document Name, Parties, Agreement Date, Effective Date, Expiration Date, Renewal Term, Notice Period to Terminate Renewal, Governing Law. Dates normalise to `mm/dd/yyyy`; Parties to `Party A Inc. ("Party A"); Party B Corp. ("Party B")` semicolon form.

**33 yes/no categories** (presence of a clause; annotators capture full supporting sentences as context): everything else, from Anti-Assignment to Third Party Beneficiary.

Semantics that bind our schema design:
- **Derived answers.** Expiration Date (and sometimes Effective Date) answers may require *arithmetic over other categories* — e.g. "five years following the Effective Date" → a computed date. A span-finder alone cannot produce the answer. [S: README examples]
- **Group overlap.** Categories in the same group (dates; non-compete/exclusivity/no-solicit; licence family; liability pair) may share or overlapping spans — categories are not mutually exclusive. [S: README]
- **Redaction conventions.** `***`/`___`/blanks are filer redactions and propagate into answers (`1/[]/2020`). [S: README]
- **`<omitted>`.** Annotators splice non-contiguous responsive text with a literal `<omitted>` marker inside clause spans — clause-column text is therefore *not always verbatim-contiguous* in the contract. Answer-key derivation and any span-verbatim validation must treat `<omitted>` as a splice point, not text. [S: README]
- **TXT fidelity caveat.** The provided TXT conversions "may not stay true to the format of the original PDF" — inconsistent spacing, lost table structure. Our pipeline runs on the TXT layer; this is stated honestly as the operating assumption (production systems face the same layer). [S: README]

## 5. Measured corpus statistics [M — computed on the frozen archive, 3 Jul 2026]

**Contract lengths** (words, whitespace-split, over all 510 TXTs): min 109, p10 970, p25 2,452, **median 5,039**, p75 10,211, p90 18,625, max 47,733; mean 7,861. 429 contracts are under 15k words; 27 exceed 25k.

**Contract types** (inferred from filenames [I] — CUAD's own type table is aggregate [S]): the README's 25 types at 3–34 docs each; our filename inference reproduces the shape (License/IP/Distributor/Development/Service/Maintenance/Strategic Alliance the biggest strata) with 19 filenames unmatched to a type keyword (mostly "Joint Filing" and "Servicing" agreements) — treated as their own stratum.

**Per-category prevalence** (contracts where the category is present, of 510) and paper difficulty (Figure 8, per-category Precision @ 80% Recall for DeBERTa-xlarge; values read visually from the published figure — approximate to ±3) [M + S-fig]:

| Category | Present /510 | P@80R (fig. 8) |
|---|---|---|
| Document Name | 510 | ~97 |
| Parties | 509 | ~96 |
| Agreement Date | 465 | ~93 |
| Governing Law | 433 | ~98 |
| Anti-Assignment | 374 | ~76 |
| Effective Date | 359 | ~40 |
| Expiration Date | 329 | ~86 |
| Cap on Liability | 275 | ~62 |
| License Grant | 255 | ~55 |
| Audit Rights | 214 | ~46 |
| Termination for Convenience | 183 | ~37 |
| Post-Termination Services | 182 | ~0–2 |
| Exclusivity | 180 | ~50 |
| Insurance | 167 | ~52 |
| Revenue/Profit Sharing | 166 | ~42 |
| Minimum Commitment | 165 | ~15 |
| Renewal Term | 163 | ~49 |
| Non-Transferable License | 138 | ~30 |
| IP Ownership Assignment | 124 | ~0–2 |
| Change of Control | 121 | ~0–2 |
| Non-Compete | 119 | ~12 |
| Uncapped Liability | 111 | ~22 |
| Covenant Not to Sue | 100 | ~0–2 |
| Rofr/Rofo/Rofn | 85 | ~0–2 |
| Volume Restriction | 82 | ~21 |
| Competitive Restriction Exception | 76 | ~5 |
| Warranty Duration | 75 | ~4 |
| Irrevocable or Perpetual License | 70 | ~50 |
| Liquidated Damages | 61 | ~18 |
| No-Solicit of Employees | 59 | ~62 |
| Affiliate License-Licensee | 59 | ~16 |
| Joint IP Ownership | 46 | ~14 |
| Non-Disparagement | 38 | ~15 |
| No-Solicit of Customers | 34 | ~31 |
| Third Party Beneficiary | 33 | ~21 |
| Most Favored Nation | 28 | ~0–2 |
| Affiliate License-Licensor | 23 | ~10 |
| Unlimited/All-You-Can-Eat License | 17 | ~10 |
| Price Restrictions | 15 | ~15 |
| Source Code Escrow | 13 | ~50 |
| Notice Period to Terminate Renewal | (col-name wart, see §6) | ~35 |

Figure 4 of the paper corroborates the spread at AUPR level ("from close to the ceiling of 100% AUPR … to around 20%") [S: ar5iv HTML]. Note the instructive divergence: Expiration Date scores ~86 on *span-finding* while its *answer* often requires date arithmetic (§4) — model-difficulty numbers proxy span formulaicity, not end-to-end answerability. [I]

## 6. Data warts (recorded for the prep scripts) [M]

1. **Malformed column name**: `Notice Period To Terminate Renewal- Answer` (space after the hyphen, unlike the other 40 `-Answer` columns). Any programmatic column parse must special-case it.
2. **Filename join**: the CSV's `Filename` column holds PDF names whose casing/punctuation doesn't always equal the TXT filename (498/510 match on naive `.pdf→.txt` swap). `prepare_corpus.py` builds an explicit verified mapping and exits 1 on any unmatched selected contract.
3. **CSV clause columns are list-like strings** (`['span one', 'span two']`) — parsed with `ast.literal_eval`-style handling, never `eval`, with the `<omitted>` convention honoured (§4).

## 7. Annotation quality [S + I]

The seven-step process (§1) is serious — attorney-reviewed, with a machine-assisted recall sweep. Nevertheless: the README itself states the categories/contracts "are not comprehensive or representative"; the scout sweep found **no published errata, no datasheet-level error rates, and no follow-up critique quantifying annotation noise** (the datasheet is referenced on the Atticus site but was not retrievable). The honest position: CUAD's error rate is unknown, in both directions. Our evaluation therefore carries a pre-registered disagreement-adjudication lane (design doc §8): as-marked scores are the headline; a hand-adjudicated sample of pipeline-vs-key disagreements is reported alongside; the key is never edited. Framed as prudence toward any external key — and gratitude toward a freely-licensed corpus this expensive to make — not as defect-hunting. [I]

## 8. Licence and attribution [S]

> "CUAD is licensed under the Creative Commons Attribution 4.0 (CC BY 4.0) license and free to the public for commercial and non-commercial use." — `CUAD_v1_README.txt`

The Atticus Project makes "no representations or warranties regarding the license status of the underlying contracts, which are publicly available and downloadable from EDGAR" [S: README]. The contracts themselves are public SEC filings.

**Attribution (required, everywhere the data surfaces — writeup, notebook, interactive page, data README):**

> Hendrycks, D., Burns, C., Chen, A., & Ball, S. (2021). *CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review.* NeurIPS 2021 Datasets and Benchmarks Track. arXiv:2103.06268. Dataset © The Atticus Project, CC BY 4.0.

## 9. LEDGAR — assessed and declared out [S]

LEDGAR (Tuggener et al., LREC 2020): ~850k provisions from SEC filings with ~12.6k labels, available via GitHub/LexGLUE. Declared **out** for two independent reasons: (1) fitness — isolated provisions without their contracts cannot serve a pipeline whose unit of work is the contract and whose story is per-document scope narrowing; (2) licence hygiene — public reporting of its licence conflicts (CC BY-SA 4.0 vs CC BY), and share-alike terms would complicate a CC BY-attributed case. (CORD/WildReceipt precedent from Case 3: named in the spec, assessed, reasons recorded.)

## 10. Implications carried into the design doc [I]

1. **Category selection evidence exists and is strong**: prevalence × figure-8 difficulty spans the full spectrum; the 12-category pick can cite both numbers per category.
2. **Length ceiling**: pre-register a ≤15,000-word cap for stream/holdout eligibility (429/510 remain eligible) — a 47k-word outlier is one read at 9× median cost with no methodological gain; stated honestly as a scoping rule.
3. **Budget arithmetic**: 50 stream reads at mean ~8k words ≈ 500–550k input tokens — comfortably inside the 60-read cap with retries.
4. **Free holdout**: matchers cost nothing to run — mark them on a held-out set larger than the stream (~100 contracts) for the equivalence exhibit.
5. **Schema must distinguish span-finding from answer derivation** (the Expiration Date lesson, §5) and handle `<omitted>`, redactions, and multi-span categories (§4).
6. **The two warts** (§6) are prep-script requirements with loud failures, not silent workarounds.
