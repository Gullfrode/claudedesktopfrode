---
name: lønn
description: Lønnstransaksjoner og ansattoversikt fra Sigma2/UBW Agresso. Trigger når brukeren spør om lønn, lønnsutbetaling, lønnsoversikt, lønnskostnad, ansattnummer, ressursnummer, lønnart, eller periodesammendrag.
---

# Lønn – Sigma2

Leser CSV-filer synkronisert fra SharePoint via OneDrive.

## Tilgjengelige verktøy (MCP)

| Verktøy | Beskrivelse |
|---|---|
| `check_data()` | Sjekk at filer er tilgjengelig og vis sist oppdatert |
| `lookup_employee(sokeord)` | Finn ansatt på navn eller ressursnummer |
| `list_employees([kun_aktive])` | List alle ansatte/ressurser |
| `get_salary_overview(ressnr_eller_navn, [periode])` | Lønnsoversikt per ansatt |
| `get_period_summary(periode, [gruppering])` | Aggregert sammendrag for Sigma2 |
| `search_lonnart(sokeord)` | Søk i lønnartregisteret |
| `get_employee_projects(ressnr_eller_navn)` | Prosjektkoblinger for ansatt |

## Filbehov

- `AlleLønnstransaksjoner.csv` – fra SharePoint-bibliotek "Sigma2 - Økonomi - Lønnstransaksjoner"
- `DimensjonRessurser.csv`, `DimensjonLonnart.csv`, m.fl. – fra "Sigma2 - Økonomi - Dimensjoner"

## Stibeskrivelse

Serveren finner filene automatisk via OneDrive-synk:
- **Mac:** `~/Library/CloudStorage/OneDrive-...-Sikt/`
- **Windows:** `~\Sikt - Sigma2 - ...` eller `~\OneDrive - Sikt\`

Overstyr med env-variablene `LONN_TRANS_FILE` og `LONN_DIM_DIR` hvis auto-deteksjon feiler.
