# Invoice format research — sourced reference

Project 3 ("Invoice Processing"), Phase 1. Compiled 3 July 2026 from six read-only scout passes; synthesis by the main loop. Every claim is marked **[S]** (directly sourced at the URL) or **[I]** (inferred / secondary). This file is the grounding for the per-supplier templates (design.md §3), the extraction schema (§7), and the validator's formatting rules — every formatting feature the generator emits must trace to a section here, or be declared [I] in `design.md`.

Companion: `design.md` (the design doc this research feeds), `DECISIONS.md` (running log).

---

## 1. The legal backbone — EU VAT Directive 2006/112/EC

The extraction schema is grounded in the law's own list of what an invoice must contain, not in anyone's idea of what invoices look like.

**Art. 226 — mandatory content** [S]: the directive enumerates fifteen numbered points, with later insertions 7a, 10a and 11a — (1) date of issue; (2) a sequential number, based on one or more series, uniquely identifying the invoice; (3) the supplier's VAT identification number; (4) the customer's VAT identification number (where the customer is liable or for intra-EU supplies); (5) full names and addresses of both parties; (6) quantity and nature of goods / extent and nature of services; (7) the supply date where it differs from the issue date, (7a) cash-accounting mention; (8) the taxable amount per rate or exemption, the unit price exclusive of VAT, and any discounts or rebates; (9) the VAT rate(s) applied; (10) the VAT amount payable, (10a) "Self-billing"; (11) exemption references, (11a) where the customer is liable for the VAT, **the mention "Reverse charge"** (quoted verbatim from the directive); (12)–(14) new-means-of-transport and margin-scheme mentions; (15) tax-representative details.
Sources: https://www.legislation.gov.uk/eudr/2006/112/article/226 (retained directive text — **list and (11a) wording verified personally, 3 Jul 2026**); https://www.vatupdate.com/2022/05/12/eu-vat-directive-2006-112-ec-explained-art-226-content-of-an-invoice/

**Art. 226b / 220a — simplified invoices** [S]: member states must allow simplified content for invoices ≤ €100 (may allow up to €400); simplified invoices may omit most particulars but not issue date, supplier identity, the supply description, and the VAT amount (or the data to compute it). Not permitted for intra-EU B2B supplies of goods. Source: https://www.vatupdate.com/2022/03/01/eu-vat-directive-2006-112-ec-explained-art-220a-invoicing-simplified-invoice/
*Design consequence*: even the smallest one-off supplier invoices in the corpus carry full content — several are services near or above the threshold, and the schema stays uniform. Simplified invoices are out of scope [I].

**Art. 226(11a) — reverse charge wording** [S]: where the customer is liable for the VAT, the invoice must carry the words "Reverse charge". CJEU C-247/21 (Luxury Trust Automobil) confirmed substitute wording does not satisfy the requirement. Sources: https://www.internationaltaxplaza.info/homepage/news-archive/news-archive-2022/489-news-archive-december-2022/6950-case-c-247-21.html; https://www.fonoa.com/resources/blog/eu-reverse-charge-what-is-it-and-who-is-it-for
Common practice adds a directive citation ("Article 196 of Council Directive 2006/112/EC") though only the phrase is mandatory [I].

**Art. 138 — intra-Community supply of goods** [S]: exempt where goods move between member states, the buyer is VAT-identified in the destination state and provided its number. Customary invoice reference: "Exempt intra-Community supply – Article 138(1) of Directive 2006/112/EC" (or national-language equivalent, §4 below). Source: https://legalclarity.org/article-138-vat-directive-intra-community-supply-exemption/

**Art. 230 — currency** [S]: invoice amounts may be in any currency; the VAT amount payable must be in the national currency of the member state of supply. Source: https://taxation-customs.ec.europa.eu/document/download/12dc566c-9f43-49d9-a306-b706879104ba_en
*Design consequence*: the Swedish supplier invoices in SEK with 0% VAT (intra-EU supply), so no VAT-currency conversion appears on the document — realistic and simple [I].

**ViDA (adopted 14 Apr 2025)** [S]: from 1 July 2030 intra-EU B2B invoicing must be structured (EN 16931); planned Art. 226 additions (corrected-invoice reference, bank identifier, due date) take effect with the 2028–2030 packages. Source: https://taxation-customs.ec.europa.eu/taxation/vat/vat-digital-age-vida_en
*Design consequence*: the case study's in-world window (2025) predates all of this; the writeup can honestly note the 2030 horizon as the reason the PDF problem is a today-problem, not a forever-problem.

## 2. Finnish specifics

**VAT rates in the in-world window (calendar 2025)** [S]: standard **25.5%** (since 1 Sep 2024); **14%** reduced class (food, restaurant and catering services; enlarged 1 Jan 2025 by items moved up from 10%, incl. books); **10%** remaining for newspapers and periodicals; **0%/exempt** classes incl. intra-EU supplies (0%, input-deductible) and healthcare/financial services (exempt). From **1 Jan 2026** the 14% class falls to 13.5% — the corpus therefore stays inside calendar 2025 so its rates are stable and match the project spec. Source: https://www.vero.fi/en/businesses-and-corporations/taxes-and-charges/vat/rates-of-vat/ (and /the-changes-to-VAT-rates/)

**Invoice content per AVL 209 e §** [S]: the Finnish list mirrors Art. 226 (date, sequential number, both VAT IDs, names/addresses, quantity/nature, supply date, unit price ex-VAT, discounts, taxable amount per rate, rate, VAT payable per rate, exemption/reverse-charge notations). Finnish VAT number = "FI" + Y-tunnus digits without the hyphen. Source: https://www.vero.fi/en/detailed-guidance/guidance/48090/vat-invoice-requirements2/

**Viitenumero (Finnish bank reference)** [S]: 4–20 digits including the check digit; check digit computed with weights 7-3-1 applied right-to-left over the base number, summed, check = (10 − sum mod 10) mod 10. Printed grouped in fives from the right by convention [I]. International alternative: RF creditor reference (ISO 11649, MOD 97-10). Sources: https://johannwalder.com/blog/2014/04/25/how-to-generate-a-reference-number-for-the-finnish-banking-system/; https://www.finanssiala.fi/wp-content/uploads/2024/04/structure-of-the-rf-creditor-reference-iso-11649.pdf

**IBAN/BIC** [S]: Finnish IBAN = FI + 2 check digits + 14 digits (18 chars), MOD-97 validated; common BICs NDEAFIHH (Nordea), OKOYFIHH (OP), DABAFIHH (Danske). Sources: https://www.swift.com/sites/default/files/files/iban-registry_3.pdf; https://www.finanssiala.fi/wp-content/uploads/2025/01/finnish-monetary-institution-codes-and-bics-20012025.pdf

**Payment terms and late interest** [S]: 30 days net is the standard B2B default; late-payment interest per korkolaki = reference rate + 8 pp, plus the €40 fixed compensation. Source: https://e-justice.europa.eu/topics/taking-legal-action/where-and-how/interest-rates/fi_en
Finnish invoices customarily print maksuehto (payment term), viivästyskorko (late interest) and huomautusaika (complaint period, commonly 7–14 days) in the terms line [I]. Käteisalennus (early-payment discount) exists as a term but no official convention source was found — used sparingly if at all [I].

**Rounding** [S]: 5-cent rounding applies to cash payments only, not invoices; invoice totals are ordinary 2-decimal arithmetic. Source: https://www.vero.fi/en/detailed-guidance/guidance/48090/vat-invoice-requirements2/

**Formats** [I, standard Finnish practice]: dates DD.MM.YYYY; decimal comma; space (or none) as thousands separator; € after the amount in running text, column headers often carry the unit.

## 3. The e-invoicing landscape — why this corpus is PDFs

This section is load-bearing for the story's honesty in front of a Finnish audience (design.md §1).

- Finland is one of the most e-invoiced economies: >90% of all invoices electronic (~325M/yr, 2023) [S]; ~85% of B2B invoices structured Finvoice by 2022 [S]; 99% of invoices to public buyers electronic [S]. Sources: https://ec.europa.eu/digital-building-blocks/sites/spaces/DIGITAL/pages/467108884/eInvoicing+in+Finland; https://dddinvoices.com/learn/e-invoicing-finland; https://ec.europa.eu/digital-building-blocks/sites/spaces/einvoicingCFS/pages/718735694/2024+Finland+2024+eInvoicing+Country+Sheet
- Act 241/2019: public buyers must accept EN 16931 e-invoices; a business buyer (turnover > €10k) has the **right to demand** a structured e-invoice from a Finnish supplier — a right, not a universal mandate [S]. Source: the EC country factsheet above.
- **Where PDFs persist**: cross-border trade — "the default solution in cross-border trade has traditionally been the PDF invoice" [S]; only ~13,000 Finnish companies are Peppol-registered against ~370,000 with domestic e-invoicing capability [S]. Small and one-off suppliers default to PDF/email [I, implied by the same OpenPeppol case study]. Source: https://peppol.org/e-invoicing-without-borders-finland-and-germany/
- ViDA makes structured e-invoicing mandatory for intra-EU B2B from 1 Jul 2030 [S] (§1).

*Design consequence*: the fictional buyer runs Finvoice with its large domestic suppliers; the case-study corpus is explicitly the **residue stream** — foreign repeat suppliers, small domestic ones, and the one-off tail — which is exactly where AP manual effort concentrates. A ~200-invoice/year PDF residue against a few-thousand-invoice total AP volume is consistent with the ~85%-structured statistic [I, derivation stated in design.md §5].

## 4. National conventions — Germany, Sweden, Estonia

**Germany (Rechnung)** [S]: mandatory fields per §14 UStG mirror Art. 226 (Rechnungsnummer sequential/unique; Steuernummer or USt-IdNr.; Leistungsdatum stated even when equal to the invoice date; net per rate, Steuerbetrag, Bruttobetrag). Vocabulary: Rechnung, Rechnungsnummer, Rechnungsdatum, Leistungsdatum, USt-IdNr., Netto / Umsatzsteuer / Brutto, Zahlungsbedingungen, Bankverbindung. Number format 1.234,56; dates DD.MM.YYYY. Intra-EU supply to Finland: 0% with "**Steuerfreie innergemeinschaftliche Lieferung**" and both VAT IDs. Sources: https://invoicedataextraction.com/blog/german-vat-invoice-requirements; https://www.facturwise.com/en/blog/mandatory-invoice-fields-germany-guide; https://stripe.com/resources/more/intra-eu-shipment-germany; https://www.freeformatter.com/germany-standards-code-snippets.html

**Sweden (faktura)** [S]: momsregistreringsnummer = SE + 10-digit organisationsnummer + 01; layout standard SS 61 41 14 puts the payment block in fixed positions at the bottom — **Bankgiro** number (123-4567 / 1234-5678), **OCR reference** (3–25 digits, Mod-10 check digit), Att betala, Förfallodatum; number format 1 234,56 (space thousands, comma decimal); dates YYYY-MM-DD; VAT for reporting must be in SEK, but a 0% intra-EU supply carries no VAT line, so SEK invoicing to Finland is clean [S]/[I]. Vocabulary: Faktura, Fakturanummer, Fakturadatum, Förfallodatum, Moms, Att betala. Sources: https://www.bankgirot.se/en/bankmaterial/correctly-designed-invoices/; https://invoicedataextraction.com/blog/sweden-bankgiro-ocr-invoice-payment; https://www.eurofiscalis.com/en/invoicing-in-sweden/; https://taxdo.com/resources/global-tax-id-validation-guide/sweden; https://www.avalara.com/vatlive/en/country-guides/europe/sweden/swedish-vat-invoice-requirements.html

**Estonia (arve)** [S]: KMKR number = EE + 9 digits; registrikood on the invoice; fields per Käibemaksuseadus §37 mirror the directive. Vocabulary: Arve, Arve nr, Kuupäev, Maksetähtaeg, Käibemaks, Summa. English-language export invoices are common; EUR. Sources: https://kiirarve.ee/blogi/arve-nouded-eestis/; https://unicount.eu/en/how-to-invoice-clients-from-your-estonian-ou-requirements-reverse-charge-and-what-every-e-resident-needs-to-know/

## 5. Layout building blocks (for the per-supplier templates)

Catalogued from accounting-software sample invoices, the Bankgirot layout standard, and template galleries — one source per pattern:

- **L1 — header**: logo left / seller block left, boxed invoice-metadata table top-right (number, dates, reference) [S: https://www.bankgirot.se/en/bankmaterial/correctly-designed-invoices/]; Finnish ERP templates reserve a fixed logo area and put seller details in the header band [S: https://support.procountor.fi/hc/en-us/articles/360000252817-Invoice-layout].
- **L2 — buyer block**: recipient name/address left, below or beside the seller block; separate delivery address where used [S: https://www.snappyinvoice.com/resources/what-does-an-invoice-look-like].
- **L3 — line-item table**: description, quantity, unit, unit price ex-VAT, (discount %), VAT %, line total; VAT rate carried per line where rates mix [S: https://www.lido.app/blog/invoice-line-item].
- **L4 — VAT summary**: per-rate summary (net, rate, VAT) between the line table and the grand total, one line per distinct rate — the EN 16931 semantic model [S: https://www.vatupdate.com/2025/10/22/ultimate-guide-on-invoicing-in-the-european-union/].
- **L5 — totals block**: net subtotal → VAT per rate → gross total; rounding row optional; amount-in-words rare in the Nordics [S: https://www.billdu.com/blog/advice/essential-invoice-elements/].
- **L6 — footer**: registration identifiers (Y-tunnus / HRB / org.nr / registrikood), bank details (IBAN + BIC), web/email, often multi-column [S: https://nikonyrh.github.io/finnishinvoicetemplate.html].
- **L7 — Swedish giro band**: fixed-position payment block at the bottom (Bankgiro, OCR, amount, due date), a distinctly Swedish structure that survives on PDF invoices [S: Bankgirot, as L1]. Finnish PDFs generally carry payment data in the footer/terms rather than a tear-off band [I: OpusCapita blog, page now 404; corroborated by the Procountor/finnishinvoicetemplate layouts above].
- **L8 — hybrid formats exist** (ZUGFeRD PDF/A-3 with embedded XML; XRechnung XML-only) but impose no visual layout; out of scope for the corpus, worth one line in the writeup [S: https://invoicedataextraction.com/blog/zugferd-invoice-format-guide].

## 6. Variation axes and horrors (the catalogue templates draw from)

Mapped to sources above; anything not traceable is marked [I] and used sparingly.

- **H1 — language mixing**: Finnish, German, Swedish, Estonian/English documents in one stream (§4) [S].
- **H2 — number formats**: 1.234,56 (DE) vs 1 234,56 (FI/SE) vs unspaced 1234,56 (small suppliers) [S §2/§4; unspaced variant I].
- **H3 — date formats**: DD.MM.YYYY (FI/DE) vs YYYY-MM-DD (SE) [S §4].
- **H4 — currency**: EUR everywhere except the Swedish supplier's SEK (§1 Art. 230, §4) [S].
- **H5 — tax treatments on one stream**: 25.5% / 14% / 10% domestic, 0% reverse-charge intra-EU with mandatory mentions in three national phrasings (§1, §2, §4) [S].
- **H6 — layout diversity**: metadata box positions, line-table column sets (with/without discount column), VAT-summary placement (§5) [S].
- **H7 — reference systems**: viitenumero vs RF reference vs Swedish OCR vs German "Verwendungszweck: Rechnungsnummer" free text (§2, §4) [S; the German free-text convention I].
- **H8 — page overflow**: long line tables spill to a second page with repeated table headers; totals only on the last page [I — standard behaviour of invoice generators; kept because Case 2 showed page-break handling is a real parser hazard].
- **H9 — credit notes**: negative quantities/amounts, "Hyvityslasku" / "Gutschrift" titles, reference to the original invoice (Art. 226 corrective mention, §1) [S for the mention; layout I].
- **H10 — non-product lines**: freight surcharges, small-order fees, fuel surcharges appearing as unnumbered lines without product codes [I — common carrier practice; used for one planted F-doc].

## 7. Datasets assessed and not used

- **CORD**: ~11k Indonesian retail till receipts (shops/restaurants), CC BY 4.0-family licence, 30 semantic classes. B2C point-of-sale receipts, no European B2B invoices [S: https://github.com/clovaai/cord].
- **WildReceipt**: 1,768 English in-the-wild retail receipt images, 25 classes, Apache 2.0 [S: https://github.com/Ikomia-hub/dataset_wildreceipt].
- **Decision**: neither contains anything resembling a European B2B invoice; both are receipts. The corpus is generated, as the spec itself anticipated for the repeated-supplier set; the datasets are recorded here so the spec's pointer is answered rather than ignored.

## 8. PDF tooling feasibility (spike result, 3 July 2026)

Run in the session scratchpad (`spike/spike.py`), no project data:

- `chrome --headless=new --no-pdf-header-footer --print-to-pdf` on a Finnish-language test invoice: two consecutive renders produce PDFs of identical size but **different bytes** (creation timestamps, document ID).
- After **pypdf normalisation** (pages copied to a fresh writer; fixed /Producer and /Creator; /ID zeroed; XMP metadata dropped): the two renders are **byte-identical** (SHA-256 equal, verified) at ~54 KB/page.
- **pdfplumber** extracts the full text layer with word coordinates (106 words on the test page), Finnish characters intact; invoice number, totals, IBAN, viitenumero and VAT rate all recovered exactly.
- Versions pinned for the record: Chrome 149.0.7827.201, pypdf 5.8.0, pdfplumber 0.11.10 (Python 3.12.6). Byte-identity is guaranteed for a fixed Chrome version; a Chrome upgrade may change PDF bytes (not content). The generation manifest therefore records the Chrome version, and regeneration byte-identity claims are stated relative to it. The HTML sources and the answer key are deterministic independent of Chrome.
- **Decision: HTML/CSS templates → headless Chrome → pypdf normalisation.** reportlab (`invariant` mode) remains the tested-available fallback; weasyprint (the spec's suggestion) rejected — not installed, GTK dependency on Windows.
