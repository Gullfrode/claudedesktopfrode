#!/usr/bin/env python3
"""
Accounting Assistant MCP Server – UBW Agresso / Sigma2
Reads CSV-files synced from SharePoint via OneDrive for Business.
"""

import os
import csv
import sys
import json
from pathlib import Path
from typing import Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("accounting-assistant")

# ---------------------------------------------------------------------------
# Path detection
# ---------------------------------------------------------------------------

def _find_onedrive_root() -> Optional[Path]:
    """Auto-detect OneDrive-Deltebiblioteker (Sikt) root on Mac or Windows."""
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "CloudStorage"
        if base.exists():
            # Prefer Deltebiblioteker (shared libraries) over personal OneDrive
            candidates = sorted(
                (d for d in base.iterdir() if "OneDrive" in d.name and "Sikt" in d.name),
                key=lambda d: (0 if "Deltebiblioteker" in d.name else 1),
            )
            if candidates:
                return candidates[0]
    elif sys.platform == "win32":
        home = Path.home()
        for c in [home / "Sikt", home / "OneDrive - Sikt"]:
            if c.exists():
                return c
        for d in home.iterdir():
            if d.is_dir() and "Sikt" in d.name:
                return d
    return None


def get_kontoplan_dir() -> Path:
    """Return path to Dimensjoner folder."""
    if env := os.environ.get("ACCOUNTING_KONTOPLAN_DIR"):
        return Path(env)
    root = _find_onedrive_root()
    if root:
        candidates = [
            root / "Sigma2 - Økonomi - Dimensjoner",
            root / "Sigma2 - Økonomi" / "Dimensjoner",
        ]
        for c in candidates:
            if c.exists():
                return c
    raise FileNotFoundError(
        "Fant ikke Dimensjoner-mappen. "
        "Sett ACCOUNTING_KONTOPLAN_DIR til full sti."
    )


def get_hovedbok_dir() -> Path:
    """Return path to Hovedbok folder."""
    if env := os.environ.get("ACCOUNTING_HOVEDBOK_DIR"):
        return Path(env)
    root = _find_onedrive_root()
    if root:
        candidates = [
            root / "Sigma2 - Økonomi - Hovedbok",
            root / "Sigma2 - Økonomi" / "Hovedbok",
        ]
        for c in candidates:
            if c.exists():
                return c
    raise FileNotFoundError(
        "Fant ikke Hovedbok-mappen. "
        "Sett ACCOUNTING_HOVEDBOK_DIR til full sti."
    )


# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------

def read_tsv(path: Path, encoding: str = "utf-8-sig") -> list[dict]:
    with open(path, encoding=encoding) as f:
        return list(csv.DictReader(f, delimiter="\t"))


def format_amount(value: str) -> float:
    """Parse Norwegian decimal format (1.234,56 → 1234.56)."""
    try:
        return float(value.replace(".", "").replace(",", "."))
    except (ValueError, AttributeError):
        return 0.0


def rows_to_json(rows: list[dict], limit: int = 200) -> str:
    return json.dumps(rows[:limit], ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Tools – Kontoplan / Dimensjoner
# ---------------------------------------------------------------------------

@mcp.tool()
def search_kontoplan(query: str, limit: int = 30) -> str:
    """
    Søk i Sigma2s kontoplan (DimensjonKontoplan.csv).
    query: søkeord mot Konto-nr eller Beskrivelse
    """
    path = get_kontoplan_dir() / "DimensjonKontoplan.csv"
    rows = read_tsv(path)
    q = query.lower()
    hits = [
        r for r in rows
        if q in r.get("Konto", "").lower() or q in r.get("Beskrivelse", "").lower()
    ]
    return rows_to_json(hits, limit)


@mcp.tool()
def search_prosjektregister(query: str, limit: int = 50) -> str:
    """
    Søk i prosjektregisteret (DimensjonProsjektregister.csv).
    query: søkeord mot prosjektnr eller prosjektnavn
    """
    path = get_kontoplan_dir() / "DimensjonProsjektregister.csv"
    rows = read_tsv(path)
    q = query.lower()
    hits = [
        r for r in rows
        if any(q in str(v).lower() for v in r.values())
    ]
    return rows_to_json(hits, limit)


@mcp.tool()
def search_ressurser(query: str, limit: int = 50) -> str:
    """
    Søk i ressursregisteret / ansattregister (DimensjonRessurser.csv).
    query: navn, ressursnr, e-post e.l.
    """
    path = get_kontoplan_dir() / "DimensjonRessurser.csv"
    rows = read_tsv(path)
    q = query.lower()
    hits = [
        r for r in rows
        if any(q in str(v).lower() for v in r.values())
    ]
    return rows_to_json(hits, limit)


@mcp.tool()
def list_dimension_files() -> str:
    """List alle dimensjonsfiler som er tilgjengelig i Dimensjoner-mappen."""
    d = get_kontoplan_dir()
    files = sorted(p.name for p in d.iterdir() if p.suffix == ".csv")
    return json.dumps(files, ensure_ascii=False)


@mcp.tool()
def read_dimension_file(filename: str, query: str = "", limit: int = 100) -> str:
    """
    Les en vilkårlig dimensjonsfil fra Dimensjoner-mappen.
    filename: f.eks. 'DimensjonBilagsarter.csv'
    query: valgfritt filter – søker i alle felter
    """
    path = get_kontoplan_dir() / filename
    if not path.exists():
        return json.dumps({"error": f"Fant ikke {filename}"})
    rows = read_tsv(path)
    if query:
        q = query.lower()
        rows = [r for r in rows if any(q in str(v).lower() for v in r.values())]
    return rows_to_json(rows, limit)


# ---------------------------------------------------------------------------
# Tools – Kundereskontro
# ---------------------------------------------------------------------------

@mcp.tool()
def lookup_customer(query: str, limit: int = 20) -> str:
    """
    Slå opp kunde på navn eller kundenr (Kunderoversikt.csv).
    query: navn eller kundenummer
    """
    path = get_hovedbok_dir() / "Kunderoversikt.csv"
    rows = read_tsv(path)
    q = query.lower()
    hits = [
        r for r in rows
        if q in r.get("Kundenr", "").lower() or q in r.get("Navn", "").lower()
    ]
    return rows_to_json(hits, limit)


@mcp.tool()
def get_customer_ledger(
    customer_id: str = "",
    status: str = "open",
    limit: int = 100,
) -> str:
    """
    Hent kundereskontroposter (Komplett kundereskontro.csv).
    customer_id: kundenummer (tomt = alle)
    status: 'open' (S=N), 'closed' (S=B), eller 'all'
    """
    path = get_hovedbok_dir() / "Komplett kundereskontro.csv"
    rows = read_tsv(path)
    if customer_id:
        rows = [r for r in rows if r.get("Kundenr", "") == customer_id]
    if status == "open":
        rows = [r for r in rows if r.get("S", "") == "N"]
    elif status == "closed":
        rows = [r for r in rows if r.get("S", "") == "B"]
    return rows_to_json(rows, limit)


@mcp.tool()
def analyze_revenue(
    year: str = "",
    customer_id: str = "",
    exclude_bott: bool = False,
    exclude_nfr: bool = True,
    limit: int = 500,
) -> str:
    """
    Omsetningsanalyse fra kundereskontro med Sigma2-filterregler.
    - Fakturanr: 6 siffer, starter på 4 eller 5
    - Beløp > 0, konto 15-serien
    - exclude_nfr: ekskluderer Norges forskningsråd (default: True)
    - exclude_bott: ekskluderer BOTT-universiteter (UiO, UiB, NTNU, UiT)
    year: filtrer på år i Periode (f.eks. '2026'), tomt = alle
    """
    BOTT_CUSTOMERS = {"1010", "1011", "1046", "1224", "1012"}
    NFR_CUSTOMERS = {"1001", "NFR", "NORGES FORSKNINGSRÅD"}

    path = get_hovedbok_dir() / "Komplett kundereskontro.csv"
    rows = read_tsv(path)

    results = []
    total = 0.0

    for r in rows:
        faktnr = str(r.get("Fakturanr", "")).strip()
        beloep = format_amount(r.get("Beløp", "0"))
        konto = str(r.get("Konto", "")).strip()
        periode = str(r.get("Periode", "")).strip()
        kundenr = str(r.get("Kundenr", "")).strip()

        if not (len(faktnr) == 6 and faktnr[0] in ("4", "5")):
            continue
        if beloep <= 0:
            continue
        if not konto.startswith("15"):
            continue
        if year and not periode.startswith(year):
            continue
        if exclude_nfr and kundenr in NFR_CUSTOMERS:
            continue
        if exclude_bott and kundenr in BOTT_CUSTOMERS:
            continue
        if customer_id and kundenr != customer_id:
            continue

        results.append(r)
        total += beloep

    return json.dumps(
        {
            "antall_poster": len(results),
            "total_omsetning": round(total, 2),
            "poster": results[:limit],
        },
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def get_customer_balance(customer_id: str) -> str:
    """
    Beregn utestående saldo for en kunde (sum åpne poster).
    customer_id: kundenummer
    """
    path = get_hovedbok_dir() / "Komplett kundereskontro.csv"
    rows = read_tsv(path)
    open_rows = [
        r for r in rows
        if r.get("Kundenr", "") == customer_id and r.get("S", "") == "N"
    ]
    total = sum(format_amount(r.get("Restbeløp", r.get("Beløp", "0"))) for r in open_rows)
    return json.dumps(
        {"kundenr": customer_id, "antall_åpne_poster": len(open_rows), "saldo": round(total, 2)},
        ensure_ascii=False,
    )


# ---------------------------------------------------------------------------
# Tools – Leverandørreskontro
# ---------------------------------------------------------------------------

@mcp.tool()
def lookup_vendor(query: str, limit: int = 20) -> str:
    """
    Slå opp leverandør på navn eller leverandørnr (Leverandøreroversikt.csv).
    query: navn eller leverandørnummer
    """
    path = get_hovedbok_dir() / "Leverandøreroversikt.csv"
    rows = read_tsv(path)
    q = query.lower()
    hits = [
        r for r in rows
        if q in r.get("Leverandørnr", "").lower() or q in r.get("Navn", "").lower()
    ]
    return rows_to_json(hits, limit)


@mcp.tool()
def get_vendor_ledger(
    vendor_id: str = "",
    status: str = "open",
    limit: int = 100,
) -> str:
    """
    Hent leverandørreskontroposter (Komplett leverandørreskontro.csv).
    vendor_id: leverandørnummer (tomt = alle)
    status: 'open' (S=N), 'closed' (S=B), eller 'all'
    """
    path = get_hovedbok_dir() / "Komplett leverandørreskontro.csv"
    rows = read_tsv(path)
    if vendor_id:
        rows = [r for r in rows if r.get("Lev.nr", "") == vendor_id]
    if status == "open":
        rows = [r for r in rows if r.get("S", "") == "N"]
    elif status == "closed":
        rows = [r for r in rows if r.get("S", "") == "B"]
    return rows_to_json(rows, limit)


@mcp.tool()
def analyze_costs(
    year: str = "2026",
    vendor_id: str = "",
    account_prefix: str = "",
    limit: int = 500,
) -> str:
    """
    Kostnadsanalyse fra leverandørreskontro.
    - Bilagsnr 3YYxxxxx (inngående faktura for angitt år)
    - Beløp < 0 (kostnad), konto 24-serien
    year: årstall (f.eks. '2026')
    vendor_id: filtrer på leverandørnr
    account_prefix: filtrer på kontoprefiks (f.eks. '24')
    """
    yr_suffix = str(year)[2:] if len(str(year)) == 4 else str(year)
    prefix = f"3{yr_suffix}"

    path = get_hovedbok_dir() / "Komplett leverandørreskontro.csv"
    rows = read_tsv(path)

    results = []
    total = 0.0

    for r in rows:
        bnr = str(r.get("Bilagsnr", "")).strip()
        beloep = format_amount(r.get("Beløp", "0"))
        konto = str(r.get("Konto", "")).strip()
        levnr = str(r.get("Lev.nr", "")).strip()

        if not bnr.startswith(prefix):
            continue
        if beloep >= 0:
            continue
        if account_prefix and not konto.startswith(account_prefix):
            continue
        elif not account_prefix and not konto.startswith("24"):
            continue
        if vendor_id and levnr != vendor_id:
            continue

        results.append(r)
        total += abs(beloep)

    return json.dumps(
        {
            "antall_poster": len(results),
            "total_kostnad": round(total, 2),
            "poster": results[:limit],
        },
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def get_vendor_balance(vendor_id: str) -> str:
    """
    Beregn utestående saldo for en leverandør (sum åpne poster).
    vendor_id: leverandørnummer
    """
    path = get_hovedbok_dir() / "Komplett leverandørreskontro.csv"
    rows = read_tsv(path)
    open_rows = [
        r for r in rows
        if r.get("Lev.nr", "") == vendor_id and r.get("S", "") == "N"
    ]
    total = sum(format_amount(r.get("Beløp", "0")) for r in open_rows)
    return json.dumps(
        {"leverandørnr": vendor_id, "antall_åpne_poster": len(open_rows), "saldo": round(total, 2)},
        ensure_ascii=False,
    )


# ---------------------------------------------------------------------------
# Tools – Hovedbok (GL-transaksjoner)
# ---------------------------------------------------------------------------

@mcp.tool()
def search_transactions(
    year: str = "2026",
    account: str = "",
    text_query: str = "",
    dim1: str = "",
    dim2: str = "",
    limit: int = 200,
) -> str:
    """
    Søk i hovedbokstransaksjoner for et gitt år.
    year: årstall (f.eks. '2026')
    account: kontonummer (eksakt eller prefiks)
    text_query: fritekstsøk i Tekst-feltet
    dim1: filtrer på dimensjon 1 (prosjekt/avdeling)
    dim2: filtrer på dimensjon 2
    """
    filename = f"{year} hovedbokstransaksjoner.csv"
    path = get_hovedbok_dir() / filename
    if not path.exists():
        return json.dumps({"error": f"Fant ikke {filename}"})
    rows = read_tsv(path)

    if account:
        rows = [r for r in rows if str(r.get("Konto", "")).startswith(account)]
    if text_query:
        q = text_query.lower()
        rows = [r for r in rows if q in str(r.get("Tekst", "")).lower()]
    if dim1:
        rows = [r for r in rows if str(r.get("Dim1", "")) == dim1]
    if dim2:
        rows = [r for r in rows if str(r.get("Dim2", "")) == dim2]

    return rows_to_json(rows, limit)


@mcp.tool()
def get_account_balance(
    account: str,
    year: str = "2026",
    dim1: str = "",
) -> str:
    """
    Beregn saldo for en konto i et gitt år.
    account: kontonummer (eksakt eller prefiks for kontoserie)
    year: årstall
    dim1: valgfri dimensjon 1-filtrering
    """
    filename = f"{year} hovedbokstransaksjoner.csv"
    path = get_hovedbok_dir() / filename
    if not path.exists():
        return json.dumps({"error": f"Fant ikke {filename}"})
    rows = read_tsv(path)

    matching = [r for r in rows if str(r.get("Konto", "")).startswith(account)]
    if dim1:
        matching = [r for r in matching if str(r.get("Dim1", "")) == dim1]

    total = sum(format_amount(r.get("Beløp", "0")) for r in matching)
    return json.dumps(
        {
            "konto": account,
            "år": year,
            "antall_poster": len(matching),
            "saldo": round(total, 2),
        },
        ensure_ascii=False,
    )


@mcp.tool()
def list_available_years() -> str:
    """List alle tilgjengelige årstall for hovedbokstransaksjoner."""
    d = get_hovedbok_dir()
    years = sorted(
        p.stem.split(" ")[0]
        for p in d.iterdir()
        if p.name.endswith("hovedbokstransaksjoner.csv")
    )
    return json.dumps(years)


@mcp.tool()
def get_saldobalanse(
    year: str = "2025",
    account_prefix: str = "",
    limit: int = 200,
) -> str:
    """
    Les saldobalanse for et gitt år (Saldobalanseaar.csv / Saldobalansear.csv).
    year: årstall
    account_prefix: filtrer på kontoprefiks
    """
    d = get_hovedbok_dir()
    candidates = [
        d / f"{year} Saldobalanseaar.csv",
        d / f"{year} Saldobalansear.csv",
    ]
    path = next((p for p in candidates if p.exists()), None)
    if path is None:
        return json.dumps({"error": f"Fant ikke saldobalanse for {year}"})

    rows = read_tsv(path)
    if account_prefix:
        rows = [r for r in rows if any(str(v).startswith(account_prefix) for v in r.values())]
    return rows_to_json(rows, limit)


# ---------------------------------------------------------------------------
# Tools – Budsjett
# ---------------------------------------------------------------------------

@mcp.tool()
def search_budget(
    account: str = "",
    dim1: str = "",
    text_query: str = "",
    limit: int = 200,
) -> str:
    """
    Søk i budsjettransaksjoner (Budsjettransaksjoner.csv).
    account: kontonummer eller prefiks
    dim1: dimensjon 1
    text_query: fritekstsøk i Tekst-feltet
    """
    path = get_hovedbok_dir() / "Budsjettransaksjoner.csv"
    if not path.exists():
        return json.dumps({"error": "Budsjettransaksjoner.csv ikke funnet"})
    rows = read_tsv(path)

    if account:
        rows = [r for r in rows if str(r.get("Konto", "")).startswith(account)]
    if dim1:
        rows = [r for r in rows if str(r.get("Dim1", "")) == dim1]
    if text_query:
        q = text_query.lower()
        rows = [r for r in rows if q in str(r.get("Tekst", "")).lower()]

    return rows_to_json(rows, limit)


# ---------------------------------------------------------------------------
# Tools – Helsestatus
# ---------------------------------------------------------------------------

@mcp.tool()
def check_data_dirs() -> str:
    """
    Sjekk hvilke datafiler som er tilgjengelig og sist oppdatert.
    Nyttig for å verifisere at SharePoint-synk er aktuell.
    """
    import datetime

    result = {"kontoplan_dir": None, "hovedbok_dir": None, "files": {}}

    try:
        kd = get_kontoplan_dir()
        result["kontoplan_dir"] = str(kd)
        for p in sorted(kd.iterdir()):
            if p.suffix == ".csv":
                mtime = datetime.datetime.fromtimestamp(p.stat().st_mtime).isoformat()
                result["files"][p.name] = {"dir": "dimensjoner", "modified": mtime, "size_kb": round(p.stat().st_size / 1024, 1)}
    except FileNotFoundError as e:
        result["kontoplan_dir"] = f"FEIL: {e}"

    try:
        hd = get_hovedbok_dir()
        result["hovedbok_dir"] = str(hd)
        for p in sorted(hd.iterdir()):
            if p.suffix == ".csv":
                mtime = datetime.datetime.fromtimestamp(p.stat().st_mtime).isoformat()
                result["files"][p.name] = {"dir": "hovedbok", "modified": mtime, "size_kb": round(p.stat().st_size / 1024, 1)}
    except FileNotFoundError as e:
        result["hovedbok_dir"] = f"FEIL: {e}"

    return json.dumps(result, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()
