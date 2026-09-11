# Build spec — Phase 2: corpus preparation (Project 4)

For: python-builder. Authored in the main loop, 3 July 2026. Read `design.md` §§2, 5, 6 first; this spec is the implementation contract. `code/schemas.py` is already written and tested (33 checks) — import it, never duplicate its logic.

## House rules that bind this build

- Python 3.12, stdlib + (only if needed) `pandas` — prefer stdlib `csv`; `pathlib` paths relative to `Path(__file__).resolve().parent`; no absolute project paths in code.
- The CUAD cache is machine-local and its location is a config value (see below) — the ONLY permitted absolute path, clearly marked.
- Deterministic everything: `RANDOM_SEED = 42`; sort before sampling; never iterate over unsorted dict/set for anything order-sensitive.
- Outputs go ONLY to `data/` (documents, answer key, manifest, licence file). Never modify the cache, `design/`, or anything else.
- Scripts print a per-step summary and exit non-zero on any hard failure. No silent skips.
- Do not open, read, or copy `CUAD_v1.json` or `label_group_xlsx/` — not needed.
- You may read `data/` outputs to self-verify. **You may not read `answer_key` values into any file other than the answer key itself.**

## Files to write

### 1. `code/config.py`

Constants, no logic beyond light validation:

- `RANDOM_SEED = 42`
- `CACHE_DIR = Path(r"C:\Users\luigi\Documents\datasets\CUAD_v1")` — machine-local, comment: recoverable from data/manifest.json; every script that uses it must fail with a clear message if it does not exist.
- `EXTRACTED = CACHE_DIR / "extracted" / "CUAD_v1"`; `ZIP_PATH = CACHE_DIR / "CUAD_v1.zip"`
- `ZIP_MD5 = "c38f490a984420b8a62600db401fafd5"`; `ZIP_SHA256 = "88b694d99007d39777fa44cd72daf8297773d285dc3eab0091ba32078888d18e"`; `ZIP_URL = "https://zenodo.org/records/4595826/files/CUAD_v1.zip?download=1"`
- `STREAM_SIZE = 50`, `HOLDOUT_SIZE = 100`, `MAX_WORDS = 15_000`
- `SPIKE_CONTRACT = "EmbarkComInc_19991008_S-1A_EX-10.10_6487661_EX-10.10_Co-Branding Agreement.txt"` (excluded from eligibility)
- `LENGTH_BANDS = [(0, 2500), (2500, 7000), (7000, 15000)]` (words; upper bound exclusive)
- `TYPE_PATTERNS` — the ordered (pattern, label) list for filename type inference (copy from the Phase 1 scratch analysis; I will hand you the list below)
- `N_INDUCTION = 6` (Phase 3 uses it; lives here so every tunable is in one file)
- `READ_CAP = 60`

Type patterns (ordered, first match wins; match against uppercased filename):
`AFFILIATE→Affiliate, AGENCY→Agency, COLLABORATION→Collaboration, COOPERATION→Collaboration, CO-BRANDING→Co-Branding, COBRANDING→Co-Branding, CONSULTING→Consulting, DEVELOPMENT→Development, DISTRIBUTOR→Distributor, DISTRIBUTION→Distributor, ENDORSEMENT→Endorsement, FRANCHISE→Franchise, HOSTING→Hosting, INTELLECTUAL PROPERTY→IP, JOINT VENTURE→Joint Venture, JOINTVENTURE→Joint Venture, LICENSE→License, LICENSING→License, MAINTENANCE→Maintenance, MANUFACTURING→Manufacturing, MARKETING→Marketing, NON-COMPETE→Non-Compete, NO-SOLICIT→Non-Compete, NON-DISPARAGEMENT→Non-Compete, OUTSOURCING→Outsourcing, PROMOTION→Promotion, RESELLER→Reseller, SERVICE→Service, SPONSORSHIP→Sponsorship, SUPPLY→Supply, STRATEGIC ALLIANCE→Strategic Alliance, TRANSPORTATION→Transportation, IP→IP` (note: `IP` LAST — it is a substring hazard; `INTELLECTUAL PROPERTY` earlier catches the real ones), unmatched → `Other`.

### 2. `code/prepare_corpus.py`

1. Verify `ZIP_PATH` MD5 + SHA-256 against config (recompute, compare, fail loud). Verify `EXTRACTED` exists.
2. Build the **filename map**: for each of the 510 rows in `master_clauses.csv` (column `Filename`, PDF names), locate the TXT in `full_contract_txt/`: (a) exact stem match after `.pdf`/`.PDF` → `.txt` swap; (b) else case-insensitive stem match; (c) else normalised match (casefold, strip all non-alphanumerics). Every method used is recorded per contract. Fail (exit 1, listing them) if any row matches zero or multiple TXTs. Expect ~12 to need methods (b)/(c) — print the list for personal review.
3. Compute word counts; apply eligibility: joinable + `word_count <= MAX_WORDS` + not `SPIKE_CONTRACT`. Print eligible count.
4. **Stratified seeded draw**: strata = (inferred type, length band). Deterministic procedure, exactly: sort eligible contracts by TXT filename; `rng = random.Random(RANDOM_SEED)`; compute per-stratum quotas for 150 total (stream+holdout combined) proportional to stratum size with largest-remainder rounding (ties broken by sorted stratum key); within each stratum, `rng.sample` the quota (strata processed in sorted-key order). Then a second seeded shuffle assigns the 150: first 50 (after `rng.shuffle` of the sorted selection) → stream, rest → holdout. Stream order = the shuffled order of those 50 (record it).
5. Copy the 150 TXT files **byte-verbatim** to `data/contracts/`. Copy `master_clauses.csv` verbatim to `data/master_clauses.csv`.
6. Write `data/CUAD_LICENCE_ATTRIBUTION.md`: CC BY 4.0 statement quoted from the in-archive README, the required citation (Hendrycks, Burns, Chen & Ball 2021, NeurIPS Datasets and Benchmarks, arXiv:2103.06268), dataset © The Atticus Project, link to the licence deed, and the sentence "This project's derived files (`data/answer_key/`, `data/manifest.json`) are adaptations of CUAD's `master_clauses.csv` under the same licence."
7. Write `data/manifest.json`: source URL + zip hashes; per-file SHA-256 of every copied file; selection record (eligible count, strata table with quotas, stream list *in stream order*, holdout list sorted, per-contract: word count, type, band, join method); versions (python, platform); `generated_utc` field set to `null` (determinism — no timestamps in generated artefacts; the portfolio convention).

### 3. `code/derive_answer_key.py`

For each of the 150 selected contracts, derive `data/answer_key/<txt-stem>.json`:

- Source: `data/master_clauses.csv` row via the manifest's filename map.
- Per category in `schemas.CATEGORIES` (use `CSV_COLUMN`): clause column parses from its list-like string form to `spans` (use `ast.literal_eval` with a guard: on parse failure, fail loud naming the row/column — never `eval`); answer column per kind:
  - yes/no: `present = (answer strip-casefold == "yes")`; empty/no both → present False. `answer = None`. If clause spans are non-empty but the answer is "No"/empty, keep presence False and record `"key_note": "spans-without-yes"` (report counts; the validator watches this).
  - extraction: `present = bool(answer.strip())` OR non-empty spans; `answer` = the raw answer string verbatim (comparison normalisation happens in `schemas`, at compare time — the key stores what CUAD wrote).
- Record shape: exactly `{"contract": "<txt name>", "source_row": "<csv Filename>", "categories": {name: {present, spans, answer}}}` — must pass `schemas.validate_record` for every contract **except** that key records may carry `answer` even when unparseable (they are the key); still run validate_record and print (not fail) any structural complaints, except missing categories which are a hard fail.
- Deterministic output: `json.dump(..., indent=1, ensure_ascii=False, sort_keys=True)` + trailing newline; UTF-8.
- Print: per-category presence counts across the 150 (stream and holdout separately) for the design-doc sanity check.

### 4. `code/validate_corpus.py`

`check_rule_N_<slug>()` per design.md §6 (ten rules), each printing PASS/FAIL + detail, `main()` runs all and exits 1 if any fail:

1. `manifest_integrity` — recompute SHA-256 of every file in `data/contracts/` + `data/master_clauses.csv`, compare to manifest; zip hashes in manifest equal config.
2. `join_completeness` — every selected contract's map entry resolves; methods recorded; no ambiguities.
3. `key_parseability` — all 24 schema columns parse for all 150 rows; list-strings parse; yes/no answers ∈ {Yes, No, ""} (casefold).
4. `answer_wellformedness` — every extraction answer in the derived key parses under `schemas.parse_date_answer` to a non-"empty" kind (dates), or is non-empty text (others), or the category is absent; count `redacted`.
5. `span_presence` — for every key span segment (`schemas.span_segments`) search `schemas.norm_ws(contract_text)`; per contract compute unfound fraction; FAIL if any contract > 10% unfound; report total segments, unfound count, and the per-contract worst offenders.
6. `split_discipline` — stream/holdout disjoint, sizes 50/100, all eligible, spike absent, stream order recorded and complete.
7. `prevalence_sanity` — for each category, presence count over the 150 within the 99% binomial interval around `p_full` (from the full 510): `|k - 150*p| <= 2.576*sqrt(150*p*(1-p))` (+1 slack). Report per category.
8. `licence_presence` — `data/CUAD_LICENCE_ATTRIBUTION.md` exists, contains "CC BY 4.0", "Atticus", "2103.06268".
9. `derivation_determinism` — re-run the derivation in-memory (import and call, writing to a temp dir under `data/_tmp_validate/`, removed afterwards) and byte-compare against `data/answer_key/`; FAIL on any diff.
10. `answer_key_isolation` — static scan: no file under `code/` other than `derive_answer_key.py`, `validate_corpus.py`, `evaluate.py` (may not exist yet) contains the strings `answer_key` or `master_clauses` (skip this spec's own directory `design/`; skip comments? no — flat string scan, keep it dumb and strict; `config.py` must therefore not name those paths).

## Verification you must run before returning

- `python code/prepare_corpus.py` then `python code/derive_answer_key.py` then `python code/validate_corpus.py` — all exit 0.
- Run `prepare` + `derive` a second time into place and confirm the validator's rule 9 still passes (your own byte-identity check runs inside rule 9; I will additionally verify identity personally with fresh hashes).
- `python code/test_schemas.py` still exits 0 (you have not touched it).
- Report: eligible count, strata table summary, the ~12 non-exact join cases, per-category presence counts (stream/holdout), any `spans-without-yes` counts, and anything that surprised you.

Return a compact factual report. Do not edit `design/`, `schemas.py`, `test_schemas.py`, or this spec.
