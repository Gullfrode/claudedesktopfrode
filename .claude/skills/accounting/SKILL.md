---
name: accounting-assistant
description: Regnskapsassistent – kontoplan, kundereskontro, leverandørreskontro, hovedbok og budsjett fra Sigma2/UBW Agresso. Trigger når brukeren spør om regnskap, kontoplan, kunder, leverandører, fakturaer, hovedbok, budsjett, saldo, omsetning eller kostnader.
---

# Regnskap – Sigma2

Leser CSV-filer synkronisert fra SharePoint via OneDrive.

## Tilgjengelige verktøy (MCP)

| Verktøy | Beskrivelse |
|---|---|
| `check_data_dirs()` | Sjekk tilgjengelige filer og synkstatus |
| `search_kontoplan(query)` | Søk i kontoplan |
| `search_prosjektregister(query)` | Søk i prosjektregisteret |
| `search_ressurser(query)` | Søk i ansatt-/ressursregisteret |
| `list_dimension_files()` | List alle dimensjonsfiler |
| `read_dimension_file(filename, [query])` | Les en dimensjonsfil |
| `lookup_customer(query)` | Slå opp kunde |
| `get_customer_ledger(customer_id, [status])` | Kundereskontroposter |
| `get_customer_balance(customer_id)` | Utestående saldo for kunde |
| `analyze_revenue([year, customer_id, ...])` | Omsetningsanalyse |
| `lookup_vendor(query)` | Slå opp leverandør |
| `get_vendor_ledger(vendor_id, [status])` | Leverandørreskontroposter |
| `get_vendor_balance(vendor_id)` | Utestående saldo for leverandør |
| `analyze_costs([year, vendor_id, ...])` | Kostnadsanalyse |
| `search_transactions([year, account, ...])` | Søk i hovedbok |
| `get_account_balance(account, [year])` | Kontosaldo |
| `list_available_years()` | Tilgjengelige år i hovedbok |
| `get_saldobalanse(year)` | Saldobalanse for et år |
| `search_budget([account, dim1, ...])` | Søk i budsjett |

## Filbehov

- Dimensjoner: `Sigma2 - Økonomi - Dimensjoner` (SharePoint-bibliotek)
- Hovedbok: `Sigma2 - Økonomi - Hovedbok` (SharePoint-bibliotek)

## Stibeskrivelse

Serveren finner mappene automatisk via OneDrive-synk:
- **Mac:** `~/Library/CloudStorage/OneDrive-Deltebiblioteker-Sikt/`
- **Windows:** `~\Sikt - Sigma2 - ...` eller `~\OneDrive - Sikt\`

Overstyr med `ACCOUNTING_KONTOPLAN_DIR` og `ACCOUNTING_HOVEDBOK_DIR` om auto-deteksjon feiler.
