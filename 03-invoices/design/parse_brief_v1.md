# Parse brief v1 — pinned input for every LLM parse agent

Version 1.0, 3 July 2026. This brief is given verbatim to every parse agent. Any edit creates
v2 and is logged in `DECISIONS.md` (Case 2 lesson: brief drift caused that project's only LLM
errors; briefs are versioned like code).

## Task

You are the LLM parse path of an invoice-processing pipeline. For EACH PDF invoice assigned to
you, read the document (it is a rendered PDF — read it directly) and produce one JSON record of
its contents, exactly in the structure below. The invoices come from many different suppliers in
Finnish, German, Swedish, Estonian and English; layouts differ; extract what the document says,
not what you expect.

## Hard boundaries

- Read ONLY the PDF files listed in your assignment and this brief. Do NOT open anything else
  in the project — no other folders, no HTML files, no answer keys, no code, no design docs.
- Write ONLY the output JSON files specified in your assignment.
- End your final report with a complete list of every file you opened and every file you wrote
  (this is an audit trail and it is checked).
- If a value is genuinely unreadable, extract your best reading — never copy from another
  document, never invent what is not printed.

## Output

One file per document: `<output_dir>/<doc_id>.json` (doc_id = the PDF filename without
extension), UTF-8, containing exactly:

```json
{
  "schema_version": "1.0",
  "doc_id": "<doc_id>",
  "supplier": {"name": "...", "street": "...", "postcode": "...", "city": "...",
                "country": "FI|DE|SE|EE|IE", "vat_id": "... or null", "business_id": "... or null"},
  "buyer":    {"name": "...", "street": "...", "postcode": "...", "city": "...",
                "country": "FI", "vat_id": "... or null", "business_id": "... or null"},
  "invoice":  {"number": "...", "type": "invoice|credit_note", "issue_date": "YYYY-MM-DD",
                "supply_date": "YYYY-MM-DD or null", "due_date": "YYYY-MM-DD or null",
                "payment_terms": "... or null", "currency": "EUR|SEK",
                "po_number": "... or null", "reference_type": "viitenumero|rf|ocr or null",
                "reference_value": "... or null", "original_invoice_number": "... or null",
                "reverse_charge_mention": "... or null"},
  "bank":     {"iban": "... or null", "bic": "... or null", "bankgiro": "... or null"},
  "lines":    [{"description": "...", "quantity": "...", "unit": "...",
                "unit_price": "...", "vat_rate": "25.5|14.0|10.0|0.0", "line_total": "..."}],
  "vat_summary": [{"rate": "25.5|14.0|10.0|0.0", "base": "...", "amount": "..."}],
  "totals":   {"net": "...", "vat": "...", "gross": "..."}
}
```

## Field rules (canonicalisation)

1. **Text fields verbatim**: names, streets, descriptions, invoice numbers, payment terms,
   units, IBAN/BIC/bankgiro, references — exactly as printed, including case, punctuation and
   internal spaces (IBANs: keep the printed spacing).
2. **Dates → ISO**: whatever the printed format (15.03.2025, 2025-03-15, 15. März 2025),
   output `YYYY-MM-DD`.
3. **Money → canonical strings**: strip thousands separators, use `.` as decimal point, always
   two decimals: `1 841,00` → `"1841.00"`; `1.234,56` → `"1234.56"`. Negative amounts (credit
   notes) keep the minus: `"-352.00"`. Same for `unit_price`, `line_total`, `base`, `amount`,
   `net`, `vat`, `gross`.
4. **Quantities**: integer strings (`"24"`); negative on credit-note lines (`"-4"`).
5. **VAT rates**: exactly one of `"25.5"`, `"14.0"`, `"10.0"`, `"0.0"` (a document showing
   "25,5 %" → `"25.5"`; a 0%/reverse-charge document → `"0.0"`).
6. **reference_type**: `"viitenumero"` when labelled Viitenumero/Viite; `"ocr"` when labelled
   OCR (Swedish giro block); `"rf"` when the reference starts with RF. German invoices that
   just say to quote the invoice number in the transfer have NO structured reference → both
   `reference_type` and `reference_value` null.
7. **reverse_charge_mention**: the exact printed exemption/reverse-charge sentence on 0%
   cross-border documents (e.g. "Steuerfreie innergemeinschaftliche Lieferung", "Reverse
   charge (Article 196, Council Directive 2006/112/EC)"), else null.
8. **buyer.vat_id**: only if printed on the document (it appears on cross-border documents);
   else null. `business_id`: the printed registration id (Y-tunnus / HRB / org.nr /
   registrikood), else null.
9. **supply_date**: only when the document prints a separate delivery/service date
   (Leistungsdatum, tarnekuupäev); else null. Credit notes: `due_date` null,
   `original_invoice_number` = the referenced invoice number.
10. **vat_summary**: one row per distinct VAT rate on the document (0% documents have the
    single row rate "0.0", amount "0.00").
11. `po_number`: the printed purchase-order/Bestellnummer/tilausnumero, else null.

## Accuracy over speed

Read carefully; the record is scored field-by-field. Digits in IBANs, references and totals
matter as much as the words. Check your own arithmetic: lines should sum to the net and
net + VAT = gross — if your extraction does not add up, re-read the document before writing
the file (do not "fix" the numbers to force arithmetic; re-read and extract what is printed).
