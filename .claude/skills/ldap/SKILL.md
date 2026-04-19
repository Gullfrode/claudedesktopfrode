---
name: ldap
description: Søk i Sikt/Sigma2 LDAP – finn ansatte, hent brukerinfo og se hvem som rapporterer til en leder. Trigger når brukeren spør etter en ansatt, epost, brukernavn, tittel, leder eller direkte rapporter.
---

# LDAP – Sikt/Sigma2

Søk i Sikt-katalogen via `ldap.sikt.no`.

## Tilgjengelige verktøy (MCP)

| Verktøy | Beskrivelse |
|---|---|
| `ldap_search(query)` | Søk på navn eller brukernavn |
| `ldap_get_user(uid)` | Hent brukerinfo for et bestemt uid |
| `ldap_get_reports(manager_uid)` | Hent direkte rapporter for en leder |

## Autentisering

Passord lagres i macOS Keychain (tjeneste: `ldap-sikt`, bruker: `frgri`).
På Windows: Windows Credential Manager.
Alternativt via env: `LDAP_UID` + `LDAP_PASSWORD`.
