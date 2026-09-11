# SAP list-output format research

Source-grounded reference for the synthetic document generator. Compiled 2 July 2026 from five scout research passes (one per transaction type). Every claim below is either **[S] sourced** (URL given) or **[I] inferred** from documented ABAP list conventions — the generator may use both, but the distinction stays visible here.

Citation note: two sources are SAP support notes behind a login (2111385, 2143216); their public previews confirm the claims attached to them (checked 2 Jul 2026), but a reader without an SAP account cannot verify them in full.

**The headline finding, stated honestly:** no public verbatim plain-text spool dump could be found for *any* of the five transactions, despite searching SAP Community, help.sap.com, Stack Overflow, Reddit, German SAP forums (dv-treff-community.de, abapforum.com) and Scribd. Real output varies by installation, layout variant, and user settings — "no single canonical format exists" (SAP's own position across multiple notes). Consequence for the case study: our documents are **SAP-style, built from documented conventions**, and are described that way — never as replicas of a specific system. This is the format-fidelity risk mitigation and part of the honesty framing.

---

## 1. Conventions common to all classic list / spool outputs

- **[S] Two-line standard header minimum**: list title + page number on line 1, horizontal dash rule on line 2; user (`sy-uname`), date (`sy-datum`), page (`sy-pagno`) are the standard header variables. German labels: *Seite* (page), *Benutzer* (user), *Datum* (date). ([ABAP REPORT list options](https://help.sap.com/doc/abapdocu_750_index_htm/7.50/en-US/abapreport_list_options.htm), [ABAP system fields](https://help.sap.com/doc/abapdocu_751_index_htm/7.51/en-US/abensystem_fields.htm))
- **[S] Selection-criteria metadata block** printed above the list (account/vendor/plant ranges, key date). ([SAP Community header-rows customization](https://community.sap.com/t5/-/-/m-p/13266969))
- **[S] Separators**: horizontal rules are runs of dashes (`ULINE`); with `FRAMES ON`, dashes and pipes join into frames with `----+----` intersections; "unconverted" list exports separate columns with `|`. ([ABAP FORMAT statement](https://help.sap.com/doc/abapdocu_751_index_htm/7.51/en-us/abapformat.htm), [Exporting spool requests](https://help.sap.com/docs/ABAP_PLATFORM_NEW/b1c834a22d05483b8a75710743b5ff26/4d66ca3e643461bee10000000a42189b.html))
- **[S] Pagination**: default ~65 lines per page (configurable in SPAD); `TOP-OF-PAGE` repeats report and column headers on every page; page number increments; form feed (0x0C) or blank-line runs between pages. ([Spool page size](https://community.sap.com/t5/-/-/m-p/6556059), [repeated headers in SM37 exports](https://community.sap.com/t5/enterprise-resource-planning-q-a/how-to-remove-repeating-column-headers-when-exporting-files-from-sm37/qaq-p/12433275))
- **[S] Line width**: standard spool 132 or 255 characters; special formats up to 1023; content beyond the width wraps or truncates. ([SAP Note 2143216](https://userapps.support.sap.com/sap/support/knowledge/en/2143216))
- **[S] Status icons leak into text spools as `@..@` codes**: green/cleared `@08@`, yellow/partial `@09@`, red/open `@0A@`. A first-class "characteristic horror" — meaningless to a naive parser, meaningful to the business. ([Traffic lights, SAP Help](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/af9ef57f504840d2b81be8667206d485/b298b6535fe6b74ce10000000a174cb4.html))
- **[S] German locale**: numbers `1.234,56`; **credit/negative amounts with trailing minus** `1.234,56-`; dates `DD.MM.YYYY`; debit/credit indicator column `S`/`H` (Soll/Haben); quantity units with a space before the code, `1.000 ST` (ST = Stück). ([German number format](https://answers.sap.com/questions/2531659/amount-value-displayed-in-german-format.html), [SHKZG field](http://leanx.eu/en/sap/table/rfpos.html), [ST unit](https://community.sap.com/t5/technology-q-a/unit-of-measure-st/qaq-p/8436478))
- **[I] Fixed-width columns** via `WRITE AT` positioning; numeric columns right-aligned; widths vary by layout variant (no canonical set).

## 2. FBL3N — G/L Account Line Item Display

- **[S] Underlying structures** RFPOSX/RFPOSXEXT; layout user-customisable. ([Special fields in FBL*N](https://help.sap.com/docs/SUPPORT_CONTENT/fiaccounting/3361880331.html))
- **[S] Header block**: company code, G/L account, date range / key date, shown above the list.
- **[S] Documented columns** (German/English): status indicator; *Belegnr* (document no.); *Belegtyp* (doc type); *Buchungsdatum* (posting date); *Betrag* (amount in local currency); *Ausgleichsbeleg* (clearing doc); *Referenznummer* (reference); *Sachkonto* (G/L account). ([German forum thread on FBL3N](https://abapforum.com/forum/viewtopic.php?t=12351), [FBL3N report guide](https://sapficoblog.com/fbl3n-in-sap-report-to-display-the-gl-balances/))
- **[S] Totals**: subtotal/total rows by selected grouping; opening/closing balance not standard in FBL3N.
- **[I] Totals-row rendering** (leading `*` markers, indentation) not confirmed by any source — generator may use asterisk-prefixed total lines as a plausible convention, flagged as inferred.
- **Gap**: no verbatim sample found.

## 3. ME2M / ME2L — Purchase Orders by Material / Vendor

- **[S] Programs** RM06EM00/RM06EL00; output structure MEREP_OUTTAB_PURCHDOC. ([RM06EM00](https://www.sapdatasheet.org/abap/prog/rm06em00.html), [MEREP_OUTTAB_PURCHDOC](https://leanx.eu/en/sap/table/merep_outtab_purchdoc.html))
- **[S] Documented fields in order**: EBELN (PO number), EBELP (item), BSART (doc type), BEDAT (order date), material + short text (TXZ01), vendor, EKORG (purch. org), MENGE (quantity), MEINS (unit), NETPR (net price), NETWR (net value), WAERS (currency), still-to-deliver quantity/value (MGLIEF/WTLIEF), still-to-invoice (WTINV).
- **[S] German headings**: *Bestellnummer, Material, Lieferant, Menge, Einheit, Nettopreis, Währung*; totals labels *Summe:* / *Gesamtsumme:*.
- **[S] Grouping/subtotals**: per-vendor or per-material subtotal rows (quantity and value) when sorted; grand total at end.
- **[I]** The per-page layout sketch in the scout report is a reconstruction from documented conventions (two-line header + framed columns + repeated headers per page), **not** a verbatim sample.
- **Gap**: no verbatim sample found; column widths vary by "scope of list" customizing.

## 4. VA05 — List of Sales Orders

- **[S] Underlying structure** VBMTV (custom fields via VBMTVZ). ([SAP KB 2964501](https://userapps.support.sap.com/sap/support/knowledge/en/2964501))
- **[S] Documented columns** (German/English): *Verkaufsbelegnr* (sales doc no.); *Auftraggeber* (sold-to party); *Materialbezeichnung* (material description); *Bestellmenge* (order qty); *Einheit* (unit); *Nettowert* (net value); *Beleg-Datum* (document date); *Lieferstatus* (delivery status). ([VA05 customization](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-members/list-of-sales-order-in-va05/ba-p/13220112), [solidforms.de](https://solidforms.de/en/extend-the-va05-and-va05n-with-additional-or-customer-specific-fields/))
- **[S] Export**: "unconverted" local-file save produces pipe-separated plain text.
- **[I] Totals**: net-value totals at list end; exact rendering unconfirmed.
- **Gap**: no verbatim sample; modern systems render VA05 as ALV grid, which exports differently from the classic list — the generator targets the classic-list/spool rendering (the vintage-system premise).

## 5. FBL1N — Vendor Line Item Display

The richest research haul; the generator's reference type.

- **[S] Structures** RFPOS/RFPOSX. ([RFPOS fields](http://leanx.eu/en/sap/table/rfpos.html))
- **[S] Header block**: vendor number/name, company code, open-items key date; customisable extra header rows. ([header-rows blog](https://blogs.sap.com/2020/08/19/how-to-change-and-add-more-information-in-header-row-in-the-output-of-fbl1n-fbl5n-fbl3n-fagll03h-in-sap/))
- **[S] Documented column order**: status traffic-light; BELNR (doc no.); BLART (doc type — KR invoice, KZ payment, KA vendor doc); BLDAT (doc date); BUDAT (posting date); baseline date; net due date; amount in local currency; AUGBL (clearing doc); clearing date; ZUONR (assignment); SGTXT (text); WAERS (currency). ([net due date](https://help.sap.com/docs/SUPPORT_CONTENT/fiaccounting/3361878608.html), [adding fields to FBL1N](https://blogs.sap.com/2019/01/04/5-easy-steps-to-add-new-line-item-fields-to-fbl1n/))
- **[S] German headings**: *Kreditor, Belegnummer, Belegtyp, Belegdatum, Buchungsdatum, Fälligkeitsdatum, Betrag in Landeswährung, Ausgleichsbeleg*.
- **[S] Status codes in text export**: `@08@` cleared / `@09@` partial / `@0A@` open.
- **[S] Print behaviour: one vendor per page**, header (vendor, company code, key date) repeated per page. ([SAP Note 2111385](https://userapps.support.sap.com/sap/support/knowledge/en/2111385))
- **[S] Trailing minus** on credit amounts documented for SAP German locale generally; **[I]** applied to FBL1N specifically (not confirmed per-transaction — plausible and adopted).
- **Gap**: no verbatim sample found (as for all five types); exact totals-line prefix conventions unconfirmed.

## 6. MB52 — Warehouse Stocks of Material

- **[S] Program** RM07MLBS; fields from MARD/MARA/MBEW: MATNR (material), MAKTX (description), WERKS (plant), LGORT (storage location), LABST (unrestricted), INSME (quality inspection), SPEME (blocked), WLABS (value unrestricted), WAERS, MEINS. ([RM07MLBS fields](https://www.sapdatasheet.org/wil/abap/prog/rm07mlbs/dtf.html))
- **[S] German headings**: *Werk, Lagerort, Frei verwendbar, In Qualitätsprüfung, Gesperrt, Lagerbewertung*. ([SAP Help DE](https://help.sap.com/docs/SAP_ERP/89724bcd4ce94b8c886f27bee89f9953/a1a0b9537cceb44ce10000000a174cb4.html?locale=de-DE))
- **[S] Hierarchical display**: grouped plant → storage location with header lines and subordinate item lines; plant-level totals include stock-in-transfer without storage location; value totals toggleable.
- **[I] Totals-row naming** (e.g. a "Werk 1000 gesamt" line) unconfirmed; generator adopts a plausible German rendering, flagged as inferred.
- **Gap**: no verbatim sample.

## 7. The horrors catalogue (variation axes for the generator)

Each axis traces to a documented behaviour above; these are what make the documents *characteristically* awful rather than randomly awful:

| # | Horror | Grounding |
|---|---|---|
| H1 | Repeated page headers + column headers every ~65 lines, page counter, form feed | §1 pagination [S] |
| H2 | `@..@` status-icon codes embedded in data rows | §1, §5 [S] |
| H3 | Trailing-minus negatives (`1.234,56-`) breaking naive float parsing | §1 [S] |
| H4 | German number/date locale throughout | §1 [S] |
| H5 | Dash rules and `----+----` frame intersections mid-document; pipe column separators | §1 [S] |
| H6 | Metadata/selection blocks before any data; blank-line runs | §1 [S] |
| H7 | Fixed-width truncation of long names (vendor/material) at column boundaries | §1 line width [S]/[I] |
| H8 | Subtotal/total rows interleaved with data rows, distinguishable only by format | §3–6 [S]/[I] |
| H9 | Per-vendor page splits (FBL1N) — one logical report, many page fragments | §5 [S] |
| H10 | Layout variants per user/installation (column selection, order) — the reason "no canonical format exists" | §1 [S] |

## 8. What this means for the generator

1. Build each type's template from the documented column sets above; keep German headings.
2. Apply horrors H1–H9 as controlled variation axes with config parameters; H10 is the planted-variant mechanism (a "user's modified layout" appearing late in the stream).
3. Every formatting choice not directly sourced is a declared [I] inference — acceptable because the case study claims "SAP-style, documented conventions", not "replica of system X".
4. Spot-review of generated documents against this file is a Phase 2 verification gate.
