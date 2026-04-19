---
name: excelerator-gl
description: Generer Excelerator GL-bilag for UBW Agresso. Trigger når brukeren spør om GL-bilag, Excelerator-bilag, bokføring, posteringslinjer eller import til Agresso via Citrix.
---

# Excelerator GL – Sigma2

Genererer `.xlsx`-filer på Skrivebordet klar for import via Citrix/Excelerator.

## Tilgjengelige verktøy (MCP)

| Verktøy | Beskrivelse |
|---|---|
| `preview_gl_bilag(periode, bokføringsdato, linjer_json)` | Forhåndsvis og valider bilag |
| `create_gl_bilag(periode, bokføringsdato, linjer_json, [bilagsnavn])` | Generer .xlsx på Skrivebordet |
| `list_gl_bilag()` | List eksisterende bilag på Skrivebordet |

## Format for linjer_json

```json
[
  {"account": 29300, "amount": -9789.0, "description": "Tekst", "dim_1": "koststed", "dim_2": "prosjekt"},
  {"account": 29300, "amount":  9789.0, "description": "Tekst"}
]
```

Bilaget må balansere (sum = 0). Påkrevde felt per linje: `account`, `amount`, `description`.
