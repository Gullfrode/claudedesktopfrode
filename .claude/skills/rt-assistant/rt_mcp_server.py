#!/usr/bin/env python3
# /// script
# dependencies = ["mcp"]
# ///
"""
RT MCP Server – Request Tracker (sak.sikt.no)
Gir Claude Desktop tilgang til RT API via MCP-protokollen.

Token leses fra .env-filen (RT_TOKEN).
"""

import os
import json
import urllib.request
import urllib.parse
from mcp.server.fastmcp import FastMCP

RT_BASE = "https://sak.sikt.no/REST/2.0"

TEAM = {
    "abmoh":    {"name": "Abdulrahman Azab Mohamed", "email": "abmoh@sikt.no"},
    "abach":    {"name": "Andreas Bach",              "email": "abach@sikt.no"},
    "anhag":    {"name": "Andreas Halberg Hagset",    "email": "anhag@sikt.no"},
    "based":    {"name": "Basir Sedighi",             "email": "based@sikt.no"},
    "beedv":    {"name": "Bente Tøndel Edvardsen",   "email": "beedv@sikt.no"},
    "carlt":    {"name": "Calle (Carl Thomas Stene)", "email": "carlt@sikt.no"},
    "dhpus":    {"name": "Dhanya Pushpadas",          "email": "dhpus@sikt.no"},
    "elknu":    {"name": "Elise Knudsen",             "email": "elknu@sikt.no"},
    "frgri":    {"name": "Frode Grimsen Solem",       "email": "frgri@sikt.no"},
    "gunnarb":  {"name": "Gunnar Bøe",                "email": "gunnarb@sikt.no"},
    "haeide":   {"name": "Hans Eide",                 "email": "haeide@sikt.no"},
    "hs":       {"name": "Helge Stranden",            "email": "hs@sikt.no"},
    "hiva":     {"name": "Hildegunn Vada",            "email": "hiva@sikt.no"},
    "ingbli":   {"name": "Inger Lise Blikø",          "email": "ingbli@sikt.no"},
    "injoh":    {"name": "Ingrid Johnsen",            "email": "injoh@sikt.no"},
    "jenamu":   {"name": "Jenny Amundsen Ask",        "email": "jenamu@sikt.no"},
    "kjestr":   {"name": "Kjersti Strømme",           "email": "kjestr@sikt.no"},
    "kngje":    {"name": "Knut Skogstrand Gjerden",   "email": "kngje@sikt.no"},
    "lorand":   {"name": "Lorand Janos Szentannai",   "email": "lorand@sikt.no"},
    "mamik":    {"name": "Martin Mikkelsen",          "email": "mamik@sikt.no"},
    "rogkva":   {"name": "Roger Kvam",                "email": "rogkva@sikt.no"},
    "somor":    {"name": "Sondre Morken",             "email": "somor@sikt.no"},
    "stegun":   {"name": "Steinar Gundersen",         "email": "stegun@sikt.no"},
    "knarbakk": {"name": "Stein Inge Knarbakk",       "email": "knarbakk@sikt.no"},
    "Sucif":    {"name": "Suzan Cifci",               "email": "sucif@sikt.no"},
    "vigdisg":  {"name": "Vigdis Guldseth",           "email": "vigdisg@sikt.no"},
}

mcp = FastMCP("rt-spørring")


def get_token() -> str:
    token = os.environ.get("RT_TOKEN", "")
    if not token:
        env_paths = [
            os.path.expanduser("~/claudedesktop/.claude/.env"),
            os.path.expanduser("~/claude/.claude/.env"),
            os.path.expanduser("~/.claude/.env"),
            os.path.expanduser(
                "~/Library/Mobile Documents/com~apple~CloudDocs/scripts/snippets/RT/.env"
            ),
        ]
        for path in env_paths:
            if os.path.exists(path):
                with open(path) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("RT_TOKEN="):
                            token = line.split("=", 1)[1].strip().strip('"').strip("'")
                            break
            if token:
                break
    return token


def api_get(path: str, params: dict = None):
    token = get_token()
    if not token:
        return {"error": "RT_TOKEN ikke funnet. Sjekk .env-filen."}

    url = f"{RT_BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)

    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/json",
        "User-Agent": "RT-MCP/1.0",
    })
    raw = ""
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        raw = resp.read().decode("utf-8")
        return json.loads(raw)
    except json.JSONDecodeError as e:
        return {"error": f"JSON-parsefeil: {e}. Råsvar: {raw[:200]}"}
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:200]}"}
    except urllib.error.URLError as e:
        return {"error": f"Tilkoblingsfeil: {e.reason}"}


@mcp.tool()
def list_open_tickets(user: str = "frgri") -> str:
    """
    Hent åpne RT-saker for en bruker.
    user: RT-brukernavn fra TEAM-listen. Standard: frgri (Frode).

    Brukernavn-mapping (fornavn → brukernavn):
    Abdulrahman=abmoh, Andreas Bach=abach, Andreas Hagset=anhag, Basir=based,
    Bente=beedv, Calle/Carl Thomas=carlt, Dhanya=dhpus, Elise=elknu,
    Frode=frgri, Gunnar=gunnarb, Hans=haeide, Helge=hs, Hildegunn=hiva,
    Inger Lise=ingbli, Ingrid=injoh, Jenny=jenamu, Kjersti=kjestr,
    Knut=kngje, Lorand=lorand, Martin=mamik, Roger=rogkva, Sondre=somor,
    Steinar=stegun, Stein Inge=knarbakk, Suzan=sucif, Vigdis=vigdisg.
    """
    try:
        user_info = TEAM.get(user, {"name": user, "email": user})
        email = user_info["email"]
        name = user_info["name"]
        query = f"(Status='new' OR Status='open' OR Status='stalled' OR Status='pending' OR Status='replied') AND Owner='{email}'"
        data = api_get("/tickets", params={
            "query": query,
            "orderby": "-Created",
            "fields": "id,Subject,Status,Queue,Created",
            "limit": 100,
        })
        if "error" in data:
            return data["error"]

        items = data.get("items", [])
        if not items:
            return f"Ingen åpne saker for {name}."

        lines = [f"Åpne saker for {name} ({len(items)} stk):\n"]
        for t in items:
            tid = t.get("id", "")
            subject = t.get("Subject", "")
            status = t.get("Status", "")
            queue = t.get("Queue", {})
            queue_name = queue.get("id", "") if isinstance(queue, dict) else str(queue)
            url = f"https://sak.sikt.no/Ticket/Display.html?id={tid}"
            lines.append(f"- [{tid}]({url}) {subject} | {status} | {queue_name}")

        return "\n".join(lines)
    except Exception as e:
        return f"Feil i list_open_tickets: {e}"


@mcp.tool()
def list_team_tickets() -> str:
    """Hent åpne RT-saker for hele teamet (Frode, Calle, Suzan)."""
    try:
        results = []
        for user_id, user_info in TEAM.items():
            name = user_info["name"]
            email = user_info["email"]
            query = f"(Status='new' OR Status='open' OR Status='stalled' OR Status='pending' OR Status='replied') AND Owner='{email}'"
            data = api_get("/tickets", params={"query": query, "orderby": "-Created", "fields": "id,Subject,Status", "limit": 100})
            if "error" in data:
                results.append(f"**{name}:** Feil – {data['error']}")
                continue
            items = data.get("items", [])
            if not items:
                results.append(f"**{name}:** Ingen åpne saker.")
            else:
                lines = [f"**{name}** ({len(items)} sak(er)):"]
                for t in items:
                    tid = t.get("id", "")
                    subject = t.get("Subject", "")
                    url = f"https://sak.sikt.no/Ticket/Display.html?id={tid}"
                    lines.append(f"  - [{tid}]({url}) {subject}")
                results.append("\n".join(lines))

        return "\n\n".join(results)
    except Exception as e:
        return f"Feil i list_team_tickets: {e}"


@mcp.tool()
def get_ticket(ticket_id: str) -> str:
    """
    Hent metadata for én RT-sak (emne, status, kø, eier, opprettet).
    For å lese innhold/korrespondanse, bruk get_ticket_history.
    ticket_id: Saksnummer (f.eks. '519793').
    """
    try:
        data = api_get(f"/ticket/{ticket_id}")
        if "error" in data:
            return data["error"]

        queue = data.get("Queue", {})
        queue_name = queue.get("id", str(queue)) if isinstance(queue, dict) else str(queue)
        owner = data.get("Owner", {})
        owner_id = owner.get("id", "") if isinstance(owner, dict) else owner
        owner_name = TEAM.get(owner_id, {}).get("name", owner_id) if owner_id in TEAM else owner_id
        url = f"https://sak.sikt.no/Ticket/Display.html?id={data.get('id')}"

        lines = [
            f"**Sak #{data.get('id')}** – {data.get('Subject')}",
            f"Status: {data.get('Status')}",
            f"Kø: {queue_name}",
            f"Eier: {owner_name}",
            f"Opprettet: {data.get('Created', '')}",
            f"URL: {url}",
        ]
        cf = data.get("CustomFields", [])
        if isinstance(cf, list):
            relevant = [f for f in cf if f.get("values")]
            if relevant:
                lines.append("Egendefinerte felt:")
                for f in relevant:
                    lines.append(f"  {f.get('name')}: {', '.join(str(v) for v in f.get('values', []))}")
        elif isinstance(cf, dict) and cf:
            lines.append("Egendefinerte felt:")
            for k, v in cf.items():
                lines.append(f"  {k}: {v}")

        return "\n".join(lines)
    except Exception as e:
        return f"Feil i get_ticket: {e}"


@mcp.tool()
def get_ticket_history(ticket_id: str) -> str:
    """
    Hent korrespondanse og innhold i en RT-sak.
    Bruk dette når brukeren spør hva en sak handler om, vil lese meldinger,
    se historikk eller forstå konteksten i saken.
    ticket_id: Saksnummer (f.eks. '519793').
    """
    import base64
    try:
        # Hent alle attachments for saken
        data = api_get(f"/ticket/{ticket_id}/attachments", params={"per_page": 50})
        if "error" in data:
            return data["error"]

        items = data.get("items", [])
        if not items:
            return f"Ingen vedlegg/innhold funnet for sak #{ticket_id}."

        lines = [f"Innhold i sak #{ticket_id}:\n"]
        found = 0

        for att in items:
            att_id = att.get("id", "")
            if not att_id:
                continue

            detail = api_get(f"/attachment/{att_id}")
            if "error" in detail:
                continue

            content_type = detail.get("ContentType", "") or ""
            content_b64 = detail.get("Content")

            # Bare text/plain – unngå HTML og binærfiler
            if "text/plain" not in content_type or not content_b64:
                continue

            try:
                text = base64.b64decode(content_b64).decode("utf-8", errors="replace").strip()
            except Exception:
                continue

            if not text:
                continue

            # Hent avsender fra transaksjonen (best-effort)
            created = detail.get("Created", "")
            creator = detail.get("Creator", {})
            creator_name = creator.get("id", str(creator)) if isinstance(creator, dict) else str(creator)

            lines.append(f"--- [{created}] {creator_name} ---")
            lines.append(text[:1500] + ("..." if len(text) > 1500 else ""))
            lines.append("")
            found += 1

        return "\n".join(lines) if found > 0 else f"Ingen lesbart tekstinnhold i sak #{ticket_id}."
    except Exception as e:
        return f"Feil i get_ticket_history: {e}"


@mcp.tool()
def search_tickets(query: str) -> str:
    """
    Søk i RT med TicketSQL.
    query: TicketSQL-spørring, f.eks. "Queue='Regnskap' AND Status='open'"
    """
    try:
        data = api_get("/tickets", params={
            "query": query,
            "fields": "id,Subject,Status,Queue,Owner,Created",
            "per_page": 100,
        })
        if "error" in data:
            return data["error"]

        items = data.get("items", [])
        if not items:
            return f"Ingen saker funnet for: {query}"

        lines = [f"Søkeresultat ({len(items)} sak(er)) for: `{query}`\n"]
        for t in items:
            tid = t.get("id", "")
            subject = t.get("Subject", "")
            status = t.get("Status", "")
            queue = t.get("Queue", {})
            queue_name = queue.get("id", "") if isinstance(queue, dict) else str(queue)
            owner = t.get("Owner", {})
            owner_id = owner.get("id", "") if isinstance(owner, dict) else owner
            owner_name = TEAM.get(owner_id, {}).get("name", owner_id) if owner_id in TEAM else owner_id
            url = f"https://sak.sikt.no/Ticket/Display.html?id={tid}"
            lines.append(f"- [{tid}]({url}) {subject} | {status} | {queue_name} | {owner_name}")

        return "\n".join(lines)
    except Exception as e:
        return f"Feil i search_tickets: {e}"


if __name__ == "__main__":
    mcp.run()
