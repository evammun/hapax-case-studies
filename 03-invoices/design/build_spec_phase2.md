# Phase 2 build specification (internal)

Authored by the main loop, 3 July 2026, from the signed-off `design.md`. This file pins every
number the generator must reproduce; python-builder implements it mechanically. Where this file
and `design.md` disagree, stop and flag it — do not pick silently.

## Fixed identities

**Buyer (on every document):** Pyökkipaja Oy, Sorvaajankatu 11, 15520 Lahti, FI.
Y-tunnus and VAT ID computed with `schemas.make_y_tunnus` from base digits `2417551`
(→ Y-tunnus `2417551-C` with its computed check digit; VAT ID `FI2417551C-digits` — i.e. FI +
the 7 digits + check digit, 8 digits total). Buyer `vat_id` is printed (and extracted) only on
reverse-charge/ICS documents; `business_id` printed on all.

**Repeat suppliers** (S1–S8). All identity literals below are FINAL (collision-checked). IBANs:
construct valid ones with a `make_iban(country_code, bban_digits)` helper that computes the
mod-97 check digits, then verify with `schemas.iban_ok`. Choose stable BBAN digit strings from
the seeded RNG at config-build time is NOT allowed — hardcode literal BBANs in config so the
identity block is plainly visible and diffable. Payment terms in days. Reference systems per
`design.md` §3; German documents carry no structured reference (`reference_type: null`) — the
free-text "Verwendungszweck" convention is layout text only.

| id | Name | Country | City | VAT treatment | Currency | Terms | Reference | Language |
|---|---|---|---|---|---|---|---|---|
| s1 | Salpausselän Puutavara Oy | FI | Lahti | 25.5% | EUR | 30 | viitenumero | fi |
| s2 | Päijät-Pakkaus Oy | FI | Hollola | 25.5% | EUR | 21 | viitenumero | fi |
| s3 | Falkenrath Beschläge GmbH | DE | Wuppertal | 0% ICS, "Steuerfreie innergemeinschaftliche Lieferung" | EUR | 30 | null | de |
| s4 | Möbeltyg Viskan AB | SE | Borås | 0% ICS, "Undantag från skatteplikt – unionsintern leverans (Intra-EU supply, Art. 138)" | SEK | 30 | ocr (+ bankgiro, giro band) | sv |
| s5 | Terasleht OÜ | EE | Tallinn | 0% RC, "Reverse charge (Article 196, Council Directive 2006/112/EC)" | EUR | 14 | rf | en |
| s6 | Vesijärven Rahtilinja Oy | FI | Lahti | 25.5% | EUR | 14 | viitenumero | fi |
| s7 | Lounastupa Helmi Oy | FI | Lahti | 14% | EUR | 14 | viitenumero | fi |
| s8 | Työkalu-Tiira Oy | FI | Lahti | 25.5% | EUR | 30 | viitenumero | fi |

Addresses: invent plausible street addresses per city (German/Swedish/Estonian conventions for
s3/s4/s5). Business ids: FI suppliers get valid Y-tunnus via `make_y_tunnus` (hardcode the
resulting literals); s3 an HRB number ("HRB 24xxx, Amtsgericht Wuppertal"); s4 an
organisationsnummer 55xxxxx-xxxx whose digits also form the VAT id SE…01; s5 a registrikood
(8 digits). Every FI VAT id = "FI" + Y-tunnus digits incl. check digit, no hyphen.

## Monthly document matrix (rows sum to §3 volumes; grand total 178)

| Supplier | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| s1 | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 2 | 2 | 3 | 2 | 3 | 32 |
| s2 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 26 |
| s3 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 24 |
| s4 | 2 | 2 | 2 | 2 | 1 | 2 | 1 | 2 | 2 | 2 | 1 | 1 | 20 |
| s5 | 2 | 2 | 2 | 2 | 1 | 2 | 1 | 2 | 1 | 2 | 1 | 2 | 20 |
| s6 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 3 | 24 |
| s7 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 12 |
| s8 | 2 | 2 | 2 | 2 | 1 | 2 | 1 | 2 | 2 | 2 | 1 | 1 | 20 |

Monthly one-off documents: Jan 2, Feb 2, Mar 2, Apr 1, May 2, Jun 1, Jul 2, Aug 1, Sep 2,
Oct 1, Nov 2, Dec 2 (total 20). December grand total = 15 + 2 = 17 (design §4 constraint).
Discovery timing check (enforced by the validator): each supplier's 6th document lands in
Feb (s1), Mar (s2, s3, s4, s5, s6, s8) and Jun (s7) — all within the design's parser-birth
constraints.

## One-off roster (18 suppliers, 20 documents; names FINAL, collision-checked)

| Month | Supplier | Country | Service / goods | VAT | Notes |
|---|---|---|---|---|---|
| Jan | Kalibrointi Aho Oy | FI | Measuring-tool calibration | 25.5% | |
| Jan | Painotalo Vesala Oy | FI | Printed catalogues | 25.5% | |
| Feb | Kuriiripalvelu Nopsa Oy (1st) | FI | Courier | 25.5% | invoices twice |
| Feb | Käännöstoimisto Lind & Co | FI | Translation | 25.5% | |
| Mar | Konehuolto Alisalo Oy (1st) | FI | Edgebander service call | 25.5% | invoices twice |
| Mar | Kustannus Höylä Oy | FI | Trade-periodical subscription | **10%** | |
| Apr | Sähköasennus Rautio Oy | FI | Electrical installation | 25.5% | |
| May | Messurakenne Nyman Oy | FI | Trade-fair stand build | 25.5% | |
| May | Ersatzteile Brandt GmbH | DE | Spare parts (goods) | 0% ICS | German; cites a PO |
| Jun | Hotelli Ilvesranta Oy | FI | Accommodation, sales visit | **14%** | |
| Jul | Asianajotoimisto Keto & Mäki Oy | FI | Contract review | 25.5% | |
| Jul | Ashquill Software Ltd | IE | CAD plugin licence | 0% RC (services) | English; "Reverse charge" |
| Aug | Teroituspalvelu Karhinen | FI | Blade sharpening | 25.5% | toiminimi — no "Oy" |
| Sep | Kuriiripalvelu Nopsa Oy (2nd) | FI | Courier | 25.5% | |
| Sep | Frakt Nordkap AB | SE | One-off freight leg | 0% RC (services) | Swedish; **EUR** (rule 7: SEK is s4-only) |
| Oct | Konehuolto Alisalo Oy (2nd) | FI | Spindle repair | 25.5% | |
| Nov | Jätehuolto Routasuo Oy | FI | Waste containers | 25.5% | |
| Nov | Tõlkebüroo Laine OÜ | EE | Manual translation | 0% RC (services) | English |
| Dec | Henkilöstöpalvelu Kiertola Oy | FI | December temp staff | 25.5% | |
| Dec | Pitopalvelu Sinikello Oy | FI | Christmas-party catering | **14%** | |

(If the pending check on "Ashquill Software Ltd" fails, the fallback name is "Loughware Ltd";
one config literal.)

## Planted events (exact placements)

- **T — s8 template redesign**: all s8 documents dated on/after 1 Aug 2025 use template
  `s8_v2` (same legal identity, new layout: metadata box moves from top-right to a full-width
  band, table gains a Nimikekoodi column and reorders columns, totals move left, different
  font family). Class `T` = those 8 documents.
- **F1**: s6, September, 2nd document — a "Polttoainelisä" line (no product code, unit `erä`)
  appended to an otherwise normal freight invoice.
- **F2**: s3, October, 2nd document — a **Gutschrift** (credit note): negative quantities and
  totals, references the s3 September invoice by number, no PO.
- **F3**: s1, November, 2nd document — a **hyvityslasku** (credit note) against the s1 October
  delivery, one returned-goods line, negative totals, no PO.
- **F4**: s4, December, the single document — line table runs long and spills to page 2, which
  also carries a "Leveransvillkor" terms block; totals only on page 2.
- **S**: s2, November, 3rd document — one line's quantity and unit price are TRANSPOSED in the
  rendered document relative to the true transaction. True: quantity 2 × unit price 50.00 =
  100.00. Printed: 50 × 2.00 = 100.00. The answer key stores the TRUE values (2 / 50.00); the
  rendered document shows the transposed ones; every other field identical; document-internal
  arithmetic holds either way. Mark the answer-key wrapper `"s_exception": true` with a note.
  The description on that line: a hinge product where per-unit ~€50 is plausible and per-unit
  €2.00 is also superficially plausible — nothing on the face gives it away.

Class labels in the answer key: `R` all repeat documents except the above; `O` all one-off
documents; `T`/`F`/`S` per this section. Expected counts (validator-enforced):
R 165 / O 20 / T 8 / F 4 / S 1.

## Document content rules

- **Dates**: business days only; spread within each month per supplier (s7 invoices on the
  last business day of its month; s6 within 3 days of month-end; others spread). Due date =
  issue date + terms. `supply_date` printed by s3 (Leistungsdatum, required German field) and
  s5; null for others. Credit notes: no due date.
- **Invoice numbers**: per-supplier formats (s1 `Lasku 2025-NNNN`, s2 bare `NNNNN`, s3
  `RE-2025-NNNN`, s4 `FNNNNN`, s5 `A25-NNN`, s6 `2025NNNNN`, s7 `NNNN`, s8 `T-NNNN` in v1 and
  `2025-NNNN` in v2 — the redesign also changed the numbering series, realistic for new
  software). Strictly increasing per supplier, random gaps 1–19 (they invoice other customers).
- **PO register**: config builds a register of POs (id `PO-2025-NNN`, date, supplier id) for
  goods suppliers s1, s2, s3, s4, s5, s8 and the Brandt one-off; every goods **invoice** cites
  one whose date precedes the invoice by 3–45 days; credit notes and service invoices have
  `po_number: null`.
- **Lines**: goods 3–12 (integer quantities, catalogue items with per-item plausible unit-price
  ranges, units kpl/m2/jm/ST/st/tk as locale-appropriate); services 1–4. Line totals
  qty × price exactly; VAT summary per rate; totals per `schemas.validate_record` arithmetic.
- **Amount scale** (plausibility): s1 500–6,000 € net per invoice; s2 300–2,500; s3 800–7,000;
  s4 5,000–40,000 SEK; s5 600–5,000; s6 180–900; s7 480–780; s8 150–1,800; one-offs 90–4,500
  (hotel/catering/subscription at the low end, fair stand and temp staff at the high end).
- **Every record must pass `schemas.validate_record` with zero errors** before rendering; the
  generator asserts this per document.

## Templates

Eight repeat templates + `s8_v2` + five one-off template variants (assigned deterministically
to one-off suppliers by locale), all as HTML/CSS producing A4 via the spike-verified pipeline:
`chrome --headless=new --no-pdf-header-footer --print-to-pdf` then pypdf normalisation (copy
pages to fresh writer, fixed /Producer "Hapax invoice generator" and /Creator "Hapax",
/ID zeroed, XMP dropped). Layout building blocks and per-country vocabulary per
`format_research.md` §4–§6: s1 classic FI (L1 boxed metadata top-right, viite in footer),
s2 compact narrow table with unspaced numbers, s3 German Rechnung (Leistungsdatum row,
Netto/Umsatzsteuer/Brutto block, Bankverbindung footer), s4 Swedish faktura with the fixed
bottom giro band (Bankgiro, OCR, Att betala, Förfallodatum) and YYYY-MM-DD dates and
space-thousands SEK amounts, s5 English EE arve with RF reference, s6 service layout with
shipment-description lines, s7 minimal one-pager, s8 v1 vs v2 per the T event. Number/date
rendering helpers per locale live in ONE place (used by both templates and the validator's
re-rendering checks). Fonts: web-safe stacks varied per supplier (Arial/Helvetica, Georgia,
Verdana, Tahoma, Trebuchet, Courier New for s2's dot-matrix look). No external resources in
the HTML (no webfonts, no images beyond inline SVG/data URIs if any).

## Generator and validator

- `code/config.py` — everything above as literals/tables; `RANDOM_SEED = 42`.
- `code/generate_invoices.py` — builds all 198 records deterministically (single RNG stream,
  document order = fixed schedule order); asserts per-record schema validity; renders HTML to
  `data/html/`, PDFs to `data/documents/` (normalised), answer keys to `data/answer_key/`
  (`{"schema_version", "doc_id", "class", "s_exception"?, "record"}`), and a
  `data/manifest.json` (chrome version string, per-file SHA-256, counts per class/supplier).
  Filenames `YYYY-MM_<supplier-slug>_<nn>` (nn = sequence within month per supplier).
  Idempotent: rerunning must produce byte-identical files (the manifest hash set is the check).
- `code/validate_data.py` — exits 1 on any failure; prints per-rule PASS/FAIL:
  1. every answer-key record passes `schemas.validate_record` (S doc included — its record is
     internally consistent too, since 2 × 50.00 = 100.00);
  2. rendered-text checks via pdfplumber: every string field appears verbatim in its document's
     text layer; every monetary/quantity/date field appears when re-rendered in the document's
     locale format — EXCEPT the S document, where exactly the two designed fields (one line's
     quantity and unit_price) must MISMATCH in exactly the transposed way, and everything else
     must match;
  3. class counts R/O/T/F/S = 165/20/8/4/1; per-supplier and per-month counts = the matrices
     above; December total 17;
  4. discovery timing: each repeat supplier's 6th document falls in the month stated above;
  5. PO register integrity (rule 4 of design §6) and credit-note reference resolution;
  6. identifier check digits on every document (via `schemas`);
  7. supplier identity stability across the year (s8 layout change allowed, identity fields
     unchanged);
  8. currency/locale discipline (SEK ⇔ s4; formats per locale);
  9. multi-page: ≥ 10 documents have 2 pages (natural overflow + F4), none exceed 2;
  10. grounded formatting: every template declares the `format_research.md` sections it draws
      from in a registry; the validator asserts every template is registered.

## Boundaries for the builder

- Read `design.md`, `format_research.md`, `code/schemas.py`, and this file first.
- Do not touch anything outside `Case Studies/03 Invoices/`. Never open `data/answer_key/` in
  any downstream-facing code (generator writes it; only the validator reads it back).
- Do not modify `schemas.py`; if it blocks you, stop and report.
- Chrome is at `C:\Program Files\Google\Chrome\Application\chrome.exe`; pdfplumber and pypdf
  are installed. Rendering 198 PDFs takes minutes — print progress with `flush=True`.
- When done: run the generator twice and the validator once; report hash-identity of the two
  runs, validator output, and anything you had to decide that this spec did not pin.
