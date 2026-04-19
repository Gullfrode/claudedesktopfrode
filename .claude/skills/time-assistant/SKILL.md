---
name: time-assistant
description: Timetransaksjoner og prosjekttimer fra Sigma2/UBW Agresso. Trigger når brukeren spør om timer, timeregistrering, prosjekttimer, flex-saldo, timeoversikt eller timetransaksjoner.
---

# Time – Sigma2

Leser timetransaksjonsfiler synkronisert fra SharePoint via OneDrive.

## Tilgjengelige verktøy (MCP)

| Verktøy | Beskrivelse |
|---|---|
| `check_data()` | Sjekk tilgjengelige filer og synkstatus |
| `list_available_years()` | List tilgjengelige år |
| `get_time_by_person([ressnr_eller_navn], [periode])` | Timer per prosjekt for en person |
| `get_time_by_project(prosjekt, [periode])` | Ressursbruk på et prosjekt |
| `get_flex_balance([ressnr_eller_navn], [periode])` | Flex-saldo (S9990015) |
| `search_project(sokeord)` | Søk i prosjektregisteret |

## Standard

- Standard person: Frode Solem (Ressnr 39036)
- Standard periode: YTD
- Flex-prosjekt: S9990015
- Normerttid: 37,5 t/uke

## Stibeskrivelse

Serveren finner filene automatisk via OneDrive-synk:
- **Mac:** `~/Library/CloudStorage/OneDrive-Deltebiblioteker-Sikt/`
- **Windows:** `~\Sikt - Sigma2 - ...` eller `~\OneDrive - Sikt\`

Overstyr med `TIME_TRANS_DIR` og `TIME_DIM_DIR` om auto-deteksjon feiler.
