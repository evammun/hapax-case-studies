# 06 Anomaly Detection — domain research

Compiled 3 July 2026. Web research gathered by scout agents (read-only), composed and
verified in the main loop. Every claim is tagged **[S]** (sourced — stated in the cited
source) or **[I]** (inferred — reasonable practice, not directly stated). Where a finding
forces a design decision, the decision is stated here and carried into `design.md`.

---

## 1. The CAAT canon — standard audit analytics tests for AP/GL

The rule layer implements only tests that trace to sourced audit practice. The canon,
with the parameterisation notes that matter:

**1.1 Duplicate payment/invoice testing [S].** The practitioner standard is a match
hierarchy over (vendor, invoice number, date, amount): exact match on all four, then
"same-same-different" variants where one field differs — same vendor/amount/date with a
different invoice number being the classic double-submission signature. Commercial tools
(TeamMate Analytics) implement this as configurable multi-field matching. Fuzzy variants
(amounts within ±2.5%, transposed invoice numbers) exist but the tolerance is a vendor
illustration, not an industry norm **[I]** — tolerances are a design choice.
Sources: Greenskies Analytics, "Duplicate Invoice Analytics"
(https://greenskiesanalytics.com/duplicate-invoice-analytics/); Wolters Kluwer, TeamMate
Analytics features (https://www.wolterskluwer.com/en/solutions/teammate/teammate-analytics/features);
ACFE, "Anti-Fraud Data Analytics Tests"
(https://www.acfe.com/fraud-resources/fraud-risk-tools---coso/anti-fraud-data-analytics-tests).

**1.2 Round-sum testing [S].** Amounts that are exact multiples of 1,000 (generalised:
multiples of 10^(m−1)) are a recognised fingerprint of estimated, unsupported, or invented
figures; the Journal of Accountancy example applies it directly to a 100,000-invoice AP
population. Source: Journal of Accountancy, "Round numbers: a fingerprint of fraud" (2018)
(https://www.journalofaccountancy.com/issues/2018/may/fraud-round-numbers/); Greenskies
JE test list (https://greenskiesanalytics.com/the-complete-list-of-je-tests/).

**1.3 Split-purchase / threshold-structuring testing [S/I].** "Just below the approval
limit" is a named JE test [S]; "two or more similar procurements from the same supplier
in amounts just under review limits" is a named procurement red flag [S — GSA OIG
Procurement Fraud Handbook, https://www.gsaig.gov/sites/default/files/misc-reports/ProcurementFraudHandbook_0.pdf,
retrieved via search excerpt]. The specific windowing (same vendor, N-day window, parts
summing over the threshold) is engineering practice, not a cited numeric standard **[I]**.

**1.4 Weekend/holiday posting testing [S].** "Transactions made during typical
non-working days (weekends and company holidays)" and "off-hour transactions by the same
employee" are named tests [S — Greenskies JE list]. Honest caveat, kept for the writeup:
practitioner commentary notes the test has weakened as a red flag under remote work
[S — Inside Public Accounting, "Test Journal Entries Like It's 2025, Not 1990",
https://insidepublicaccounting.com/2025/06/19/perspectives-from-the-profession-test-journal-entries-like-its-2025-not-1990/].
**Design consequence:** the fictional company is explicitly weekday-only with posting
tied to office workflows, so the test is meaningful *in this world*; the writeup states
the 2025-practice caveat.

**1.5 Dormant-vendor reactivation [S].** A canon test (dormant account resumes activity;
cross-checks against employee master). Source: Audimation/CaseWare IDEA fraud-testing
page (https://www.audimation.com/fraud/).
**Design decision — NOT implemented.** No dormant-reactivation class is planted; a null
test would add accidental-signature burden (sparse tail vendors trip naive dormancy
definitions) without an exhibit. Listed in the writeup as production canon. Eva can opt
it in at the gate (design doc §10).

**1.6 Vendor-master hygiene [S].** Canon tests: vendor-vs-employee master matching on
address/tax ID; similar-name matching; duplicate bank accounts across vendor records.
Sources: ACFE anti-fraud tests; Audimation; Diligent, "Invoice fraud detection"
(https://www.diligent.com/resources/blog/invoice-fraud-detection).
**Design decision — implemented narrowly, on purpose.** The implemented hygiene test is
byte-exact duplicate names only. Duplicate-IBAN/VAT-ID matching and normalised/fuzzy name
matching are canon and *would* catch the planted name-variant class in production — that
is exactly the point the case makes about finite rule sets (design doc §3, class V), and
the writeup says so. No employee master is generated (out of scope).

**1.7 Unusual account combinations [S].** "Unusual (not typical for a client)
combination of accounts" is a classic JE fraud-risk test; ML literature frames the same
thing as account-pattern deviations. Sources: GAAP Dynamics, "Auditing Fraud Risk:
Journal Entry Testing" (https://www.gaapdynamics.com/auditing-fraud-risk-journal-entry-testing/);
MDPI Systems 10(5):130 (https://www.mdpi.com/2079-8954/10/5/130).
**Design consequence:** implemented as a vendor-to-account mapping test against the
vendor master's allowed-account sets — the client-specific "typical" baseline made
explicit.

## 2. Benford's law — assessed and declared OUT of the rule layer

- Benford analysis of AP populations is established practice as a **screening** tool,
  never a standalone verdict; the seminal practitioner example (Nigrini's NASDAQ software
  company) traced a digit spike to courier-charge processing patterns, not fraud [S —
  Journal of Accountancy, May 1999, https://www.journalofaccountancy.com/issues/1999/may/nigrini/].
- Preconditions: amounts spanning multiple orders of magnitude, no built-in min/max, no
  dominance by set price bands; approval thresholds themselves create digit artefacts
  that are a stated *limitation* of the method [S — ISACA Journal 2011,
  https://www.isaca.org/resources/isaca-journal/past-issues/2011/understanding-and-applying-benfords-law;
  Wikipedia summary, https://en.wikipedia.org/wiki/Benford%27s_law].
- **Decision [I, from the sourced caveats]:** excluded from the implemented rule layer.
  This corpus is dominated by per-vendor price bands and contains designed threshold
  artefacts (classes R and S), so digit-distribution deviations would measure the
  generator's price-band choices, not anomalies — a conformance claim would be
  untestable-by-design and therefore dishonest. Mentioned in the writeup as production
  screening practice with the sourced caveats.

## 3. Finnish context

**3.1 Public holidays, calendar 2025 [S].** 1 Jan (Wed), 6 Jan (Mon), 18 Apr (Fri),
21 Apr (Mon), 1 May (Thu), 29 May (Thu), 20 Jun (Midsummer Eve, Fri — de facto
non-working by near-universal custom, not statutory), 21 Jun (Sat), 1 Nov (Sat),
6 Dec (Sat), 25 Dec (Thu), 26 Dec (Fri). Christmas Eve 24 Dec (Wed) is de facto
non-working. Sources: officeholidays.com/countries/finland/2025 (cross-checked against
timeanddate.com and independently verified by calendar arithmetic).
**Design consequence:** in 2025 All Saints' Day and Independence Day fall on Saturdays —
zero anomaly signal. Holiday plants use the weekday holidays (Epiphany, Easter pair,
Vappu, Ascension, Midsummer Eve, Christmas pair); the company calendar treats 24 Dec and
20 Jun as non-working (declared convention).

**3.2 Chart of accounts [S/I].** The statutory backbone is the expense-by-nature income
statement of Kirjanpitoasetus 1339/1997 ch. 1 §1 (Materiaalit ja palvelut → Aineet,
tarvikkeet ja tavarat / Ulkopuoliset palvelut; Henkilöstökulut; Poistot; Liiketoiminnan
muut kulut) [S — Finlex, https://www.finlex.fi/fi/laki/ajantasa/1997/19971339]. Common
numbering per the widely used Liikekirjuri-style templates: 1xxx assets, 2xxx equity and
liabilities, 3xxx revenue, 4000–4399 purchases, ~4400–4499 external services, 5xxx wages,
6xxx social/pension costs, 7xxx–9xxx other operating costs and below-the-line items
[S, lower confidence — reai.fi summary and Asteri Liikekirjuri 2025 tilikartta,
https://asteri.fi/tiedostot/tilikartat/lk25.pdf; exact sub-ranges vary by software
vendor, so fine slicing is [I]]. **Design consequence:** the fictional CoA (~40 accounts)
anchors to these ranges; the statutory grouping stays recognisable.

**3.3 Payment terms and AP practice [S/I].** B2B terms typically 7–30 days [S — Suomi.fi];
statute caps the default at 30 days, longer only by express agreement (Laki kaupallisten
sopimusten maksuehdoista 30/2013, as amended) [S — Finlex,
https://www.finlex.fi/en/legislation/2013/30]. The viitenumero (bank reference with check
digit) is the backbone of automated payment-to-invoice matching [S — Nordea reference
number service; xmldation wiki]. Payment-run practice (batch runs on 1–2 fixed weekdays,
hard month-end cut-off) is **[I]** — common ERP practice, no authoritative Finnish source
found. **Design consequence:** vendor terms drawn from {14, 21, 30} days net (14/30 [S],
21 [I]); payment runs Tuesdays and Fridays [I, declared convention]; the ledger carries
invoice and posting dates (payment execution itself is out of scope).

**3.4 Approval thresholds [I — no authoritative source exists].** Searches found no
published norm for invoice-approval tiers in mid-size Finnish/Nordic private companies —
only AP-software marketing and public-sector procurement thresholds (not analogous).
**Stated plainly in the design doc:** the company's tiers (€10,000 department head,
€50,000 CFO) are an invented, declared convention. The R and S classes are defined
against the €10,000 tier.

**3.5 Volume plausibility [I, built on S benchmarks].** AP-productivity benchmarks:
~6,000–11,000 invoices/FTE/year manual, ~20,000+ automated [S — HighRadius AP-automation
statistics; DocuClipper AP statistics]. A distribution business generates dense
purchase-ledger volume (restocking, freight, utilities). A ~€90M technical wholesaler
with an AP team of ~4 landing at ~50,000 posting lines/year from ~200 vendors sits inside
the plausible band (250 lines/vendor/year average, concentrated in core suppliers). No
direct benchmark for the exact combination exists; the design doc states this as a
reasoned convention.

## 4. Isolation Forest — determinism and reproducibility

- `random_state` as a fixed int gives reproducible results across runs; scikit-learn's
  own guidance is to pass an int (not to rely on global seeding) [S —
  https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html;
  https://scikit-learn.org/stable/common_pitfalls.html].
- Reproducibility is **not** guaranteed across library versions: bug fixes "may change
  the behavior of estimators, including the predictions of an estimator trained on the
  same data and random_state" [S — scikit-learn Glossary,
  https://scikit-learn.org/stable/glossary.html]. Cross-platform floating-point variance
  is a general numerical-software property, not sklearn-specific [I].
- **Spike result (this machine, 3 Jul 2026, recorded in DECISIONS.md):** 50k×8 synthetic
  matrix, `IsolationForest(n_estimators=200, contamination=0.004, random_state=42,
  n_jobs=1)` → SHA-256 over scores+predictions identical across two fresh processes;
  contamination 0.004 yielded exactly 200 flags of 50,000. **Decision:** detection
  outputs are regenerable given the pinned environment (scikit-learn 1.9.0, scipy 1.18.0,
  numpy 2.5.0, Python 3.12.6); versions recorded in the README at packaging; `n_jobs=1`
  mandatory.
