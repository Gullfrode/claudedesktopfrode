#!/usr/bin/env python3
"""
Lønn MCP Server – Sigma2 / UBW Agresso
Leser lønnstransaksjoner og dimensjonsfiler synkronisert fra SharePoint via OneDrive.
"""

import csv
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("lonn-sigma2")


# ---------------------------------------------------------------------------
# Path detection
# ---------------------------------------------------------------------------

def _find_onedrive_sikt() -> Optional[Path]:
    """Auto-detect OneDrive-Deltebiblioteker (Sikt) root."""
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


def _get_trans_file() -> Path:
    if env := os.environ.get("LONN_TRANS_FILE"):
        return Path(env)
    root = _find_onedrive_sikt()
    if root:
        p = root / "Sigma2 - Økonomi - Lønnstransaksjoner" / "AlleLønnstransaksjoner.csv"
        if p.exists():
            return p
    raise FileNotFoundError(
        "Fant ikke AlleLønnstransaksjoner.csv. "
        "Sett env-variabel LONN_TRANS_FILE til full filsti, "
        "eller synkroniser 'Sigma2 - Økonomi - Lønnstransaksjoner' via OneDrive."
    )


def _get_dim_dir() -> Path:
    if env := os.environ.get("LONN_DIM_DIR"):
        return Path(env)
    root = _find_onedrive_sikt()
    if root:
        p = root / "Sigma2 - Økonomi - Dimensjoner"
        if p.exists():
            return p
    raise FileNotFoundError(
        "Fant ikke Dimensjoner-mappen. "
        "Sett env-variabel LONN_DIM_DIR til full mappesti, "
        "eller synkroniser 'Sigma2 - Økonomi - Dimensjoner' via OneDrive."
    )


# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------

def _les_tab(fil: Path) -> list[dict]:
    with open(fil, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def _les_trans(fil: Path) -> list[dict]:
    """
    Les AlleLønnstransaksjoner.csv som har duplikat kolonne 'T' (kolonne 1 og 8).
    csv.DictReader overskriver kolonne 1 med kolonne 8 – vi løser dette ved å
    lese med csv.reader og bygge dict manuelt med unike kolonnenavn.
    Alle filer er utf-8-sig-kodet (BOM), ikke latin-1 som skillen dokumenterte.
    """
    with open(fil, encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader)
        seen: dict[str, int] = {}
        felter = []
        for navn in header:
            if navn in seen:
                seen[navn] += 1
                felter.append(f"{navn}_{seen[navn]}")
            else:
                seen[navn] = 0
                felter.append(navn)
        return [dict(zip(felter, rad)) for rad in reader]


def _les_sc(fil: Path) -> list[dict]:
    with open(fil, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def _til_beløp(s: str) -> float:
    if not s or not s.strip():
        return 0.0
    return float(s.strip().replace("\xa0", "").replace(" ", "").replace(",", "."))


def _fmt_beløp(v: float) -> str:
    """Norsk format: mellomrom som tusenskilletegn, komma som desimal."""
    neg = v < 0
    s = f"{abs(v):_.2f}".replace("_", "\u00a0").replace(".", ",")
    return f"-{s}" if neg else s


# ---------------------------------------------------------------------------
# Period helpers
# ---------------------------------------------------------------------------

def _parse_periode_filter(periode_str: str) -> list[str]:
    """
    Returner liste med YYYYMM-strenger som matcher input.
    Input: "202503", "mars 2025", "Q1 2025", "2025", "YTD"
    """
    s = periode_str.strip()
    today = datetime.today()

    if s.upper() == "YTD":
        return [f"{today.year}{m:02d}" for m in range(1, today.month + 1)]

    if s.isdigit() and len(s) == 4:
        år = int(s)
        return [f"{år}{m:02d}" for m in range(1, 13)]

    if s.isdigit() and len(s) == 6:
        return [s]

    q_map = {"Q1": range(1, 4), "Q2": range(4, 7), "Q3": range(7, 10), "Q4": range(10, 13)}
    for q, måneder in q_map.items():
        if s.upper().startswith(q):
            parts = s.split()
            år = int(parts[1]) if len(parts) > 1 else today.year
            return [f"{år}{m:02d}" for m in måneder]

    måneder_navn = {
        "januar": 1, "februar": 2, "mars": 3, "april": 4,
        "mai": 5, "juni": 6, "juli": 7, "august": 8,
        "september": 9, "oktober": 10, "november": 11, "desember": 12,
    }
    s_lower = s.lower()
    for navn, nr in måneder_navn.items():
        if navn in s_lower:
            parts = s_lower.replace(navn, "").strip()
            år = int(parts) if parts.isdigit() else today.year
            return [f"{år}{nr:02d}"]

    raise ValueError(
        f"Ugyldig periode: '{periode_str}'. "
        "Bruk YYYYMM, månedsnavn, Q1–Q4 YYYY, årstall eller YTD."
    )


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def check_data() -> str:
    """Sjekk at lønnsdatafiler er tilgjengelig og vis sist oppdatert."""
    lines = []
    try:
        tf = _get_trans_file()
        stat = tf.stat()
        sist = datetime.fromtimestamp(stat.st_mtime).strftime("%d.%m.%Y %H:%M")
        størrelse = f"{stat.st_size / 1024 / 1024:.1f} MB"
        lines.append(f"  AlleLønnstransaksjoner.csv  {størrelse}  oppdatert {sist}")
    except FileNotFoundError as e:
        lines.append(f"  MANGLER: {e}")

    try:
        dim = _get_dim_dir()
        for fil in sorted(dim.glob("Dimensjon*.csv")):
            stat = fil.stat()
            sist = datetime.fromtimestamp(stat.st_mtime).strftime("%d.%m.%Y %H:%M")
            lines.append(f"  {fil.name:<45} oppdatert {sist}")
    except FileNotFoundError as e:
        lines.append(f"  MANGLER dimensjoner: {e}")

    return "Lønnsdatafiler:\n\n" + "\n".join(lines)


@mcp.tool()
def lookup_employee(sokeord: str) -> str:
    """
    Finn ansatt på navn eller ressursnummer.

    Args:
        sokeord: Navn (helt eller delvis) eller ressursnummer (f.eks. "39026" eller "Basir")
    """
    dim = _get_dim_dir()
    ressurser = _les_tab(dim / "DimensjonRessurser.csv")

    funn = []
    s = sokeord.strip().lower()
    for r in ressurser:
        if s == r.get("Ressnr", "").strip() or s in r.get("Navn", "").lower():
            funn.append(r)

    if not funn:
        return f"Ingen ansatte funnet for '{sokeord}'."

    linjer = []
    for r in funn:
        linjer.append(
            f"  Ressnr: {r.get('Ressnr',''):<8}  "
            f"Navn: {r.get('Navn',''):<30}  "
            f"Type: {r.get('Ressurstype',''):<10}  "
            f"Status: {r.get('Status','')}"
        )
    return f"Ansatte ({len(funn)} treff for '{sokeord}'):\n\n" + "\n".join(linjer)


@mcp.tool()
def list_employees(kun_aktive: bool = True) -> str:
    """
    List alle ansatte/ressurser.

    Args:
        kun_aktive: Filtrer kun aktive ressurser (standard: True)
    """
    dim = _get_dim_dir()
    ressurser = _les_tab(dim / "DimensjonRessurser.csv")

    if kun_aktive:
        ressurser = [r for r in ressurser if r.get("Status", "").strip().upper() in ("A", "AKTIV", "1", "")]

    if not ressurser:
        return "Ingen ressurser funnet."

    linjer = [f"  {r.get('Ressnr',''):<8}  {r.get('Navn',''):<30}  {r.get('Ressurstype',''):<12}  {r.get('Status','')}" for r in sorted(ressurser, key=lambda x: x.get("Navn", ""))]
    return f"Ansatte/ressurser ({len(linjer)} stk):\n\n" + "\n".join(linjer)


@mcp.tool()
def get_salary_overview(
    ressnr_eller_navn: str,
    periode: str = "",
) -> str:
    """
    Hent lønnsoversikt for en ansatt, gruppert per periode og lønnart.

    Args:
        ressnr_eller_navn: Ressursnummer eller navn på ansatt
        periode: Periode-filter, f.eks. "2025", "Q1 2025", "mars 2025", "YTD", "202503".
                 La stå tomt for alle tilgjengelige perioder.
    """
    dim = _get_dim_dir()
    ressurser = {r["Ressnr"]: r for r in _les_tab(dim / "DimensjonRessurser.csv")}
    lonnarter = {r["Lønnart"]: r for r in _les_tab(dim / "DimensjonLonnart.csv")}

    s = ressnr_eller_navn.strip()
    ressnr = None
    navn_vis = s
    if s in ressurser:
        ressnr = s
        navn_vis = ressurser[s].get("Navn", s)
    else:
        s_lower = s.lower()
        for rn, r in ressurser.items():
            if s_lower in r.get("Navn", "").lower():
                ressnr = rn
                navn_vis = r.get("Navn", rn)
                break
    if not ressnr:
        return f"Fant ikke ansatt '{ressnr_eller_navn}'."

    periode_filter = None
    if periode.strip():
        try:
            periode_filter = set(_parse_periode_filter(periode.strip()))
        except ValueError as e:
            return str(e)

    trans = _les_trans(_get_trans_file())
    filtrert = [
        t for t in trans
        if t.get("Ressnr", "").strip() == ressnr
        and t.get("T", "").strip() == "C"
        and (periode_filter is None or t.get("Periode", "").strip() in periode_filter)
    ]

    if not filtrert:
        periode_tekst = f" for {periode}" if periode.strip() else ""
        return f"Ingen lønnstransaksjoner funnet for {navn_vis} (Ressnr {ressnr}){periode_tekst}."

    grupper: dict[tuple, float] = defaultdict(float)
    for t in filtrert:
        key = (t.get("Periode", "").strip(), t.get("Lønnart", "").strip())
        grupper[key] += _til_beløp(t.get("Beløp", "0"))

    total = sum(grupper.values())
    linjer = []
    forrige_per = None
    per_sum = 0.0
    per_rader = []

    for (per, la), beløp in sorted(grupper.items()):
        if per != forrige_per and forrige_per is not None:
            for rad in per_rader:
                linjer.append(rad)
            linjer.append(f"  {'':6}  {'Sum':20}  {'':25}  {_fmt_beløp(per_sum):>15}")
            linjer.append("")
            per_rader = []
            per_sum = 0.0
        forrige_per = per
        per_sum += beløp
        beskrivelse = lonnarter.get(la, {}).get("Tekst", "")
        per_rader.append(f"  {per}  {la:<20}  {beskrivelse:<25}  {_fmt_beløp(beløp):>15}")

    for rad in per_rader:
        linjer.append(rad)
    if forrige_per:
        linjer.append(f"  {'':6}  {'Sum':20}  {'':25}  {_fmt_beløp(per_sum):>15}")

    header = (
        f"LØNNSOVERSIKT – {navn_vis} (Ressnr {ressnr})"
        + (f" – {periode}" if periode.strip() else "")
        + f"\n{'='*80}\n"
        f"  {'PERIODE':<6}  {'LØNNART':<20}  {'BESKRIVELSE':<25}  {'BELØP':>15}\n"
        f"  {'-'*6}  {'-'*20}  {'-'*25}  {'-'*15}"
    )
    footer = f"\n{'='*80}\nTOTAL: {_fmt_beløp(total)} kr  ({len(filtrert)} transaksjoner)"

    return header + "\n" + "\n".join(linjer) + footer


@mcp.tool()
def get_period_summary(
    periode: str,
    gruppering: str = "lonnart",
) -> str:
    """
    Hent aggregert lønnskostnadssammendrag for en periode, for hele Sigma2.

    Args:
        periode: Periode-filter, f.eks. "2025", "Q1 2025", "mars 2025", "YTD", "202503"
        gruppering: "lonnart" (standard) eller "ansatt"
    """
    try:
        periode_filter = set(_parse_periode_filter(periode.strip()))
    except ValueError as e:
        return str(e)

    dim = _get_dim_dir()
    lonnarter = {r["Lønnart"]: r for r in _les_tab(dim / "DimensjonLonnart.csv")}
    ressurser = {r["Ressnr"]: r for r in _les_tab(dim / "DimensjonRessurser.csv")}

    trans = _les_trans(_get_trans_file())
    filtrert = [
        t for t in trans
        if t.get("T", "").strip() == "C"
        and t.get("Periode", "").strip() in periode_filter
    ]

    if not filtrert:
        return f"Ingen lønnstransaksjoner for perioden '{periode}'."

    summer: dict[str, float] = defaultdict(float)
    for t in filtrert:
        if gruppering == "ansatt":
            key = t.get("Ressnr", "").strip()
        else:
            key = t.get("Lønnart", "").strip()
        summer[key] += _til_beløp(t.get("Beløp", "0"))

    total = sum(summer.values())
    linjer = []

    if gruppering == "ansatt":
        header_linje = f"  {'RESSNR':<8}  {'NAVN':<30}  {'BELØP':>15}"
        linjer.append(header_linje)
        linjer.append(f"  {'-'*8}  {'-'*30}  {'-'*15}")
        for ressnr, beløp in sorted(summer.items(), key=lambda x: -abs(x[1])):
            navn = ressurser.get(ressnr, {}).get("Navn", ressnr)
            linjer.append(f"  {ressnr:<8}  {navn:<30}  {_fmt_beløp(beløp):>15}")
    else:
        header_linje = f"  {'LØNNART':<10}  {'BESKRIVELSE':<30}  {'KONTO':<8}  {'BELØP':>15}"
        linjer.append(header_linje)
        linjer.append(f"  {'-'*10}  {'-'*30}  {'-'*8}  {'-'*15}")
        for la, beløp in sorted(summer.items(), key=lambda x: -abs(x[1])):
            info = lonnarter.get(la, {})
            beskrivelse = info.get("Tekst", "")
            konto = info.get("Konto", "")
            linjer.append(f"  {la:<10}  {beskrivelse:<30}  {konto:<8}  {_fmt_beløp(beløp):>15}")

    return (
        f"LØNNSSAMMENDRAG – {periode} – gruppering: {gruppering}\n"
        f"{'='*70}\n"
        + "\n".join(linjer)
        + f"\n{'='*70}\n"
        f"TOTAL: {_fmt_beløp(total)} kr  ({len(filtrert)} transaksjoner, {len(summer)} grupper)"
    )


@mcp.tool()
def search_lonnart(sokeord: str) -> str:
    """
    Søk i lønnartregisteret på kode eller beskrivelse.

    Args:
        sokeord: Lønnartskode (f.eks. "100") eller del av beskrivelse (f.eks. "overtid")
    """
    dim = _get_dim_dir()
    lonnarter = _les_tab(dim / "DimensjonLonnart.csv")

    s = sokeord.strip().lower()
    funn = [
        la for la in lonnarter
        if s == la.get("Lønnart", "").strip().lower()
        or s in la.get("Tekst", "").lower()
        or s in la.get("Konto", "").lower()
    ]

    if not funn:
        return f"Ingen lønnarter funnet for '{sokeord}'."

    linjer = [
        f"  {la.get('Lønnart',''):<8}  {la.get('Tekst',''):<35}  "
        f"Konto: {la.get('Konto',''):<8}  Motkonto: {la.get('Motkonto','')}"
        for la in funn
    ]
    return f"Lønnarter ({len(funn)} treff for '{sokeord}'):\n\n" + "\n".join(linjer)


@mcp.tool()
def get_employee_projects(ressnr_eller_navn: str) -> str:
    """
    Hent prosjektkoblinger for en ansatt.

    Args:
        ressnr_eller_navn: Ressursnummer eller navn
    """
    dim = _get_dim_dir()
    ressurser = {r["Ressnr"]: r for r in _les_tab(dim / "DimensjonRessurser.csv")}

    s = ressnr_eller_navn.strip()
    ressnr = None
    navn_vis = s
    if s in ressurser:
        ressnr = s
        navn_vis = ressurser[s].get("Navn", s)
    else:
        s_lower = s.lower()
        for rn, r in ressurser.items():
            if s_lower in r.get("Navn", "").lower():
                ressnr = rn
                navn_vis = r.get("Navn", rn)
                break
    if not ressnr:
        return f"Fant ikke ansatt '{ressnr_eller_navn}'."

    linjer = [f"Prosjektkoblinger for {navn_vis} (Ressnr {ressnr})\n{'='*60}"]

    try:
        proj_res = _les_tab(dim / "DimensjonProsjektRessurser.csv")
        pr_funn = [r for r in proj_res if r.get("Ressnr", "").strip() == ressnr]
        if pr_funn:
            linjer.append("\nProsjektperioder (DimensjonProsjektRessurser):")
            for r in pr_funn:
                linjer.append(
                    f"  {r.get('Navn',''):<30}  "
                    f"RT: {r.get('RT',''):<6}  "
                    f"Lev.nr: {r.get('Lev.nr',''):<8}  "
                    f"Fra: {r.get('Dato fra',''):<12}  "
                    f"Til: {r.get('Dato til','')}"
                )
    except Exception:
        pass

    try:
        proj_led = _les_tab(dim / "DimensjonProsjektleder.csv")
        navn_deler = navn_vis.split()
        if len(navn_deler) >= 2:
            søk_etternavn = navn_deler[-1].lower()
            søk_fornavn = navn_deler[0].lower()
            pl_funn = [
                r for r in proj_led
                if søk_etternavn in r.get("Ressnr(T)", "").lower()
                and søk_fornavn in r.get("Ressnr(T)", "").lower()
            ]
            if pl_funn:
                linjer.append("\nProsjektlederroller (DimensjonProsjektleder):")
                for r in pl_funn:
                    linjer.append(
                        f"  Tjeneste: {r.get('Tjeneste',''):<12}  "
                        f"Prosjekt: {r.get('Prosjekt',''):<12}  "
                        f"Navn: {r.get('Ressnr(T)','')}"
                    )
    except Exception:
        pass

    if len(linjer) == 1:
        linjer.append("Ingen prosjektkoblinger funnet.")

    return "\n".join(linjer)


if __name__ == "__main__":
    mcp.run()
