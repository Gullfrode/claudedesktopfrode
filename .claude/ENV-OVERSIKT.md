# ENV-oversikt

`.env` ligger i `.claude/.env` og er gitignored. Mal: `.env.template`.

| Variabel | Brukes av | Kommentar |
|----------|-----------|-----------|
| GITLAB_PRIVATE_TOKEN | ecoissues | Ecodream GitLab |
| GITLAB_URL | ecoissues | |
| PROJECT_ID | ecoissues | Ecodream prosjekt-ID (1020) |
| GITLAB_HOST | erpsystem | |
| GITLAB_PROJECT_ID | erpsystem | ERP-prosjekt (1035) |
| GITLAB_PROJECT_PATH | erpsystem | ecodream/erpsystem |
| GITLAB_TOKEN | erpsystem | Separat token fra PRIVATE_TOKEN |
| NOTION_TOKEN | notionjobb | Sigma2 HQ |
| NOTION_WEBHOOK | notionjobb | |
| NOTION_ROOT_PAGE_ID | notionjobb | Root-side i HQ |
| NOTION_ROOT_URL | notionjobb | |
| MIRO_CLIENT_ID | miro | OAuth app |
| MIRO_CLIENT_SECRET | miro | OAuth app |
| RT_TOKEN | rt-assistant | Request Tracker (sak.sikt.no) |
| RT_PERSONAL | rt-assistant | Personlig token |
| RT_URL | rt-assistant | https://sak.sikt.no/REST/2.0 |
| MAS_URL | mas | Metacenter Allocation System |
| MAS_TOKEN | mas | |
| LDAP_UID | ldap | Brukernavn (frgri) – passord i macOS Keychain |
| HA_URL | homelab-expert | Home Assistant hai7 (LAN) |
| HA_URL_TS | homelab-expert | Home Assistant hai7 (Tailscale) |
| HA_TOKEN | homelab-expert | hai7 long-lived token |
| HA_I3_URL | homelab-expert | Home Assistant hai3 (Tailscale) |
| HA_I3_URL_LAN | homelab-expert | Home Assistant hai3 (LAN) |
| HA_I3_TOKEN | homelab-expert | hai3 long-lived token |
| MFP_USERNAME | mfp | MyFitnessPal – passord via Chrome-cookies |
| TAILSCALE_TAILNET | homelab-expert | dingo-smoot.ts.net |
| TAILSCALE_API_KEY | homelab-expert | |
| MEALIE_URL | – | mealie.dingo-smoot.ts.net |
| MEALIE_TOKEN | – | |
