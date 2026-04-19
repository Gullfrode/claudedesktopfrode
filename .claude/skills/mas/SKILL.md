---
name: mas
description: MAS API – Metacenter Allocation System. Henter prosjekter, kvoter, nøkkeltall og finansdata fra Sigma2s MAS. Trigger når brukeren spør om HPC-prosjekter, kvoter, ressursbruk, aktive brukere, eller sier "MAS", "hent prosjekter fra MAS", "kvoter", "metacenter" o.l.
---

# MAS – Metacenter Allocation System

API-klient for `https://www.metacenter.no/mas/api`.

## Tilgjengelige verktøy (MCP)

| Verktøy | Beskrivelse |
|---|---|
| `open_project_page(account_number)` | Åpne prosjektsiden i nettleseren, f.eks. `NN5005K` |
| `get_team([name])` | Sigma2 AS-ansatte med rolle, e-post og bruker-ID |
| `get_project(account_number)` | Detaljer om ett prosjekt |
| `search_projects([query, project_leader, org, status])` | Søk på tvers av alle prosjekter |
| `get_quotas([account_number])` | Kvoteoversikt, filtrerbar på prosjekt |
| `get_key_numbers()` | Aktive prosjekter, aktive brukere og gjeldende periode |
| `get_financial([org, project_leader_email, period, page])` | Finansdata – kostnad per prosjekt/system |

## Token-håndtering

Token leses automatisk fra `~/claudedesktop/.claude/.env` (`MAS_TOKEN`).

Forny token: gå til `https://www.metacenter.no/mas/api/access-token/` (logg inn med Feide),
og oppdater `MAS_TOKEN` i `.env` og i Desktop-konfigen.

## Nyttige URL-er

| Formål | URL |
|---|---|
| Prosjektside | `https://www.metacenter.no/mas/projects/admin/{account_number}/` |
| Token-generering | `https://www.metacenter.no/mas/api/access-token/` |

## Merk

- `/financial/` bruker Bearer-token (samme som øvrige endepunkter)
- `/json/projects/` og `/json/quotas/` bruker Bearer-token
- Token er 32 tegn hex (MAS-spesifikt format)
