CSV Interop (Import invoices)

Sample file: `examples/interops/invoices.csv`

Field mapping
- from_org → invoice.from_org (URN)
- to_org → invoice.to_org (URN)
- sku, qty, unit, unit_price → a single line item
- total → invoice.total (must match qty*unit_price in real systems)
- due_net_days → invoice.terms.due_net_days

Importer

Run:

```bash
python3 scripts/import_csv_invoices.py
```

The importer canonicalizes each JSON body, signs it using the `.demo/keys/{org}.json`
private key via `tools/sign.py`, and POSTs to `/invoices` with appropriate headers.


