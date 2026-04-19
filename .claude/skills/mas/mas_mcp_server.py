#!/usr/bin/env python3
# /// script
# dependencies = ["mcp"]
# ///
"""
MAS MCP Server – Metacenter Allocation System
Gir Claude Desktop/Cowork tilgang til MAS API via MCP-protokollen.

Token leses fra MAS_TOKEN env-variabelen, eller fra .env i kjente stier.
"""

import os
import json
import urllib.request
import urllib.parse
import webbrowser
from mcp.server.fastmcp import FastMCP

MAS_BASE = "https://www.metacenter.no/mas/api"

mcp = FastMCP("mas")


def get_token() -> str:
    """Hent MAS Bearer-token fra env eller .env-fil."""
    token = os.environ.get("MAS_TOKEN", "")
    if not token:
        env_paths = [
            os.path.expanduser("~/claudedesktop/.claude/.env"),
            os.path.expanduser("~/claude/.claude/.env"),
            os.path.expanduser("~/.claude/skills/mas/.env"),
        ]
        for path in env_paths:
            if os.path.exists(path):
                with open(path) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("MAS_TOKEN="):
                            token = line.split("=", 1)[1].strip().strip('"').strip("'")
                            break
            if token:
                break
    return token


def api_get(path: str, params: dict = None) -> dict | list:
    """Gjør GET mot MAS API med Bearer-token."""
    token = get_token()
    if not token:
        return {"error": "MAS_TOKEN ikke funnet. Sett token i ~/claudedesktop/.claude/.env"}

    url = f"{MAS_BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "MAS-MCP/1.3",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


SIGMA2_TEAM = """
# Sigma2 AS – Ansatte (oppdatert 2026-04-19, ny org fra 20. april 2026)

| Navn | Rolle | E-post | Bruker-ID |
|---|---|---|---|
| Hildegunn Vada | Adm. direktør | hildegunn.vada@sigma2.no | hiva |
| Jenny Amundsen Ask | Spesialrådgiver | jenny.amundsen.ask@sigma2.no | jenamu |
| Andreas Bach | Senior systemutvikler | andreas.bach@sigma2.no | abach |
| Inger Lise Blikø | Prosjektleder | inger.bliko@sigma2.no | ingbli |
| Gunnar Bøe | Spesialrådgiver | gunnar.boe@sigma2.no | gunnarb |
| Suzan Cifci | Rådgiver | suzan.cifci@sigma2.no | Sucif |
| Bente Tøndel Edvardsen | Administrasjonskoordinator | bente.edvardsen@sigma2.no | beedv |
| Hans Eide | Spesialrådgiver | hans.eide@sigma2.no | haeide |
| Knut Skogstrand Gjerden | Seniorrådgiver | knut.gjerden@sigma2.no | kngje |
| Vigdis Guldseth | Seniorrådgiver | vigdis.guldseth@sigma2.no | vigdisg |
| Steinar Gundersen | Seniorrådgiver | steinar.gundersen@sigma2.no | stegun |
| Andreas Halberg Hagset | Prosjektleder | andreas.hagset@sigma2.no | anhag |
| Ingrid Johnsen | Seniorrådgiver | ingrid.johnsen@sigma2.no | injoh |
| Elise Knudsen | Rådgiver | elise.knudsen@sigma2.no | elknu |
| Stein Inge Knarbakk | Avdelingsleder | stein.knarbakk@sigma2.no | knarbakk |
| Roger Kvam | Avdelingsleder | roger.kvam@sigma2.no | rogkva |
| Martin Mikkelsen | Systemutvikler | martin.mikkelsen@sigma2.no | mamik |
| Abdulrahman Azab Mohamed | Seniorrådgiver | abdulrahman.azab@sigma2.no | abmoh |
| Sondre Morken | Koordinator | sondre.morken@sigma2.no | somor |
| Dhanya Pushpadas | Seniorrådgiver | dhanya.pushpadas@sigma2.no | dhpus |
| Basir Sedighi | Rådgiver | basir.sedighi@sigma2.no | based |
| Frode Grimsen Solem | Seniorrådgiver | frode.solem@sigma2.no | frgri |
| Carl Thomas Stene | Prosjektcontroller | carl.stene@sigma2.no | carlt |
| Helge Stranden | Seniorrådgiver | helge.stranden@sigma2.no | hs |
| Kjersti Strømme | Avdelingsleder | kjersti.stromme@sigma2.no | kjestr |
| Lorand Janos Szentannai | Seniorrådgiver | lorand.szentannai@sigma2.no | lorand |

## Navnealiaser
- Calle / Carl Thomas / Kalle = Carl Thomas Stene (carlt)
- Suzan / Susann / Susan = Suzan Cifci (Sucif)
- Frode = Frode Grimsen Solem (frgri)
"""


@mcp.tool()
def open_project_page(account_number: str) -> str:
    """
    Åpne prosjektsiden for et HPC-prosjekt i nettleseren.
    account_number: prosjektnummer, f.eks. NN5005K
    """
    acc = account_number.upper()
    url = f"https://www.metacenter.no/mas/projects/admin/{acc}/"
    webbrowser.open(url)
    return f"Åpnet: {url}"


@mcp.tool()
def get_team(name: str = "") -> str:
    """
    Hent Sigma2 AS-ansatte og kontaktinfo.
    name: filtrer på navn (valgfritt) – søker i fornavn, etternavn og bruker-ID.
    Returnerer rolle, e-post og bruker-ID.
    """
    if not name:
        return SIGMA2_TEAM

    needle = name.lower()
    lines = SIGMA2_TEAM.strip().split("\n")
    matches = [l for l in lines if needle in l.lower()]
    if matches:
        return "\n".join(matches)
    return f"Ingen ansatt funnet med navn eller ID '{name}'."


@mcp.tool()
def get_project(account_number: str) -> str:
    """
    Hent informasjon om et spesifikt HPC-prosjekt fra MAS.
    account_number: prosjektnummer, f.eks. NN5005K eller nn5005k
    """
    target = account_number.upper()
    data = api_get(f"/json/projects/{target}/")
    if isinstance(data, dict) and "error" not in data:
        return json.dumps(data, indent=2, ensure_ascii=False)

    all_data = api_get("/json/projects/?limit=5000")
    if isinstance(all_data, dict) and "error" in all_data:
        return all_data["error"]
    for p in all_data:
        if isinstance(p, dict) and p.get("account_number", "").upper() == target:
            return json.dumps(p, indent=2, ensure_ascii=False)

    return f"Prosjekt {account_number} ikke funnet i MAS."


@mcp.tool()
def search_projects(
    query: str = "",
    project_leader: str = "",
    org: str = "",
    status: str = "Active"
) -> str:
    """
    Søk etter HPC-prosjekter i MAS.
    query: fritekstsøk i tittel/beskrivelse
    project_leader: navn på prosjektleder – fornavn, etternavn eller begge fungerer.
                    Eksempel: "Basir", "Sedighi", "Basir Sedighi", "Vollestad"
    org: organisasjon (ntnu, uib, uio, uit, sigma2 e.l.)
    status: Active, Inactive, eller tom for alle
    """
    params = {}
    if status:
        params["status"] = status

    data = api_get("/json/projects/?limit=5000", params if params else None)
    if isinstance(data, dict) and "error" in data:
        return data["error"]

    results = []
    for p in data:
        if not isinstance(p, dict):
            continue
        pl = p.get("project_leader", {})
        pl_name = f"{pl.get('firstname','')} {pl.get('surname','')}".lower()
        title = p.get("title", "").lower()
        desc = p.get("description", "").lower()
        affil = p.get("affiliation", {}).get("name", "").lower()

        if query and query.lower() not in title and query.lower() not in desc:
            continue
        if project_leader and project_leader.lower() not in pl_name:
            continue
        if org and org.lower() not in affil and org.lower() not in pl.get("org_short", "").lower():
            continue

        results.append({
            "account_number": p.get("account_number"),
            "title": p.get("title"),
            "status": p.get("status"),
            "start": p.get("start"),
            "project_leader": f"{pl.get('firstname','')} {pl.get('surname','')}, {pl.get('org_short','')}",
            "affiliation": p.get("affiliation", {}).get("name", ""),
        })

    if not results:
        return "Ingen prosjekter funnet med de gitte søkekriteriene."

    return json.dumps(results, indent=2, ensure_ascii=False)


@mcp.tool()
def get_quotas(account_number: str = "") -> str:
    """
    Hent kvoteinformasjon fra MAS.
    account_number: filtrer på spesifikt prosjekt (valgfritt)
    Returnerer CPU-timer, ressurs og periode.
    """
    data = api_get("/json/quotas/?limit=10000")
    if isinstance(data, dict) and "error" in data:
        return data["error"]

    if account_number:
        target = account_number.upper()
        data = [q for q in data if isinstance(q, dict) and q.get("project", "").upper() == target]
        if not data:
            return f"Ingen kvoter funnet for {account_number}."

    return json.dumps(data, indent=2, ensure_ascii=False)


@mcp.tool()
def get_key_numbers() -> str:
    """Hent nøkkeltall fra MAS: antall aktive prosjekter, aktive brukere og gjeldende periode."""
    try:
        active = api_get("/key-numbers/active-projects/")
        users  = api_get("/key-numbers/active-users/")
        period = api_get("/key-numbers/period/")
        return json.dumps({
            "active_projects": active,
            "active_users": users,
            "period": period
        }, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Feil: {e}"


def _parse_financial_results(results: list) -> list:
    summary = []
    for r in results:
        pl = r.get("project_leader", {})
        pl_navn = f"{pl.get('firstname', '')} {pl.get('lastname', '')}".strip()
        pl_email = pl.get("email", "")
        for proj, perioder in r.items():
            if proj == "project_leader":
                continue
            for per, systemer in perioder.items():
                total = 0.0
                breakdown = {}
                for sys_navn, typer in systemer.items():
                    sys_total = 0.0
                    for type_navn, detaljer in typer.items():
                        if isinstance(detaljer, dict):
                            cost = detaljer.get("cost") or 0
                            units = detaljer.get("billing_units") or 0
                            sys_total += cost
                            if units:
                                breakdown[f"{sys_navn}/{type_navn}"] = {
                                    "units": units,
                                    "cost": round(cost, 2),
                                }
                    total += sys_total
                summary.append({
                    "project": proj,
                    "project_leader": pl_navn,
                    "project_leader_email": pl_email,
                    "org": pl.get("org", ""),
                    "period": per,
                    "total_cost_nok": round(total, 2),
                    "breakdown": breakdown,
                })
    return summary


@mcp.tool()
def get_financial(
    org: str = "",
    project_leader_email: str = "",
    period: str = "",
    page: int = 1,
    account_number: str = "",
) -> str:
    """
    Hent finansdata (kostnad per prosjekt) fra MAS.
    org: ntnu, uib, uio eller uit (valgfritt)
    project_leader_email: filtrer på prosjektleder-epost (valgfritt)
    period: f.eks. '2025.2' (valgfritt, default = gjeldende periode)
    page: sidenummer (20 prosjekter per side, default 1) – ignoreres hvis account_number er satt
    account_number: prosjektnummer, f.eks. NN5020K – søker gjennom alle sider automatisk

    Returnerer kostnad per prosjekt, system og ressurstype (CPU/GPU-timer, pris, beløp).
    Inkluderer prosjektleders e-postadresse.
    """
    params: dict = {}
    if org:
        params["org"] = org.lower()
    if project_leader_email:
        params["pl"] = project_leader_email
    if period:
        params["periods"] = [period]

    if account_number:
        target = account_number.upper()
        current_page = 1
        while True:
            p = dict(params)
            if current_page > 1:
                p["page"] = current_page
            data = api_get("/financial/", p if p else None)
            if isinstance(data, dict) and "error" in data:
                return data["error"]
            meta = data.get("meta", {})
            for entry in _parse_financial_results(data.get("results", [])):
                if entry["project"].upper() == target:
                    return json.dumps({"meta": meta, "results": [entry]}, indent=2, ensure_ascii=False)
            if not meta.get("has_next"):
                break
            current_page += 1
        return f"Prosjekt {account_number} ikke funnet i finansdata."

    if page > 1:
        params["page"] = page
    data = api_get("/financial/", params if params else None)
    if isinstance(data, dict) and "error" in data:
        return data["error"]

    return json.dumps({
        "meta": data.get("meta", {}),
        "results": _parse_financial_results(data.get("results", [])),
    }, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()
