---
name: rt-assistant
description: RT-assistent for Sigma2/Sikt – henter, viser og søker i RT-saker (Request Tracker på sak.sikt.no). Trigger når brukeren nevner "RT", "RT-sak", "sak i RT", "request tracker", "hent RT", "åpne saker i RT", "hvem har saker" eller spør om status/detaljer på en RT-sak. Trigger også ved saksnummer-referanser som "RT #12345" eller "sak 12345 i RT".
---

# RT-assistent

RT = Request Tracker. Sakssystem hos Sikt – https://sak.sikt.no.

## Tilgjengelige verktøy (MCP)

| Verktøy | Beskrivelse |
|---|---|
| `list_open_tickets([user])` | Åpne saker for én bruker (standard: frgri) |
| `list_team_tickets()` | Åpne saker for hele teamet |
| `get_ticket(ticket_id)` | Metadata for én sak |
| `get_ticket_history(ticket_id)` | Korrespondanse og innhold i en sak |
| `search_tickets(query)` | Søk med TicketSQL |

## Token

Bruker `RT_TOKEN` fra `.env`. Ikke assets-tilgang.

## API-base

`https://sak.sikt.no/REST/2.0`
