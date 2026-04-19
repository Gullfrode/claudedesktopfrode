#!/usr/bin/env python3
"""
Time Assistant MCP Server – UBW Agresso / Sigma2
Leser timetransaksjoner og dimensjonsfiler synkronisert fra SharePoint via OneDrive.
"""

import csv
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("time-assistant")

DEFAULT_RESSNR = "39036"   # Frode Solem
NORM_TIMER_UKE = 37.5
FLEX_PROSJEKT  = "S9990015"


# ---------------------------------------------------------------------------
# Path detection
# ---------------------------------------------------------------------------

def _find_onedrive_sikt() -> Optional[Path]:
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "CloudStorage"
        if base.exists():
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


def _get_trans_dir() -> Path:
    if env := os.environ.get("TIME_TRANS_DIR"):
        return Path(env)
    root = _find_onedrive_sikt()
    if root:
        p = root / "Sigma2 - Økonomi - Lønnstransaksjoner"
        if p.exists():
            return p
    raise FileNotFoundError(
        "Fant ikke Lønnstransaksjoner-mappen. "
        "Sett TIME_TRANS_DIR til full mappesti, "
        "eller synkroniser 'Sigma2 - Økonomi - Lønnstransaksjoner' via OneDrive."
    )


def _get_dim_dir() -> Path:
    if env := os.environ.get("TIME_DIM_DIR"):
        return Path(env)
    root = _find_onedrive_sikt()
    if root:
        p = root / "Sigma2 - Økonomi - Dimensjoner"
        if p.exists():
            return p
    raise FileNotFoundError(
        "Fant ikke Dimensjoner-mappen. "
        "Sett TIME_DIM_DIR til full mappesti, "
        "eller synkroniser 'Sigma2 - Økonomi - Dimensjoner' via OneDrive."
    )


def _time_fil(år: int) -> Path:
    return _get_trans_dir() / f"{år} AlleTimetransaksjoner.csv"


# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------

def _les_tab(fil: Path) -> list[dict]:
    with open(fil, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def _til_timer(s: str) -> float:
    s = s.strip()
    if not s:
        return 0.0
    return float(s.replace(",", "."))


def _fmt_timer(v: float) -> str:
    return f"{v:,.1f}".replace(",", "\u00a0").replace(".", ",") + " t"


# ---------------------------------------------------------------------------
# Period helpers  (YYYYWW format)
# ---------------------------------------------------------------------------

def _uke_til_dato(år: int, uke: int) -> datetime:
    """Returner mandag i gitt ISO-uke."""
    return datetime.strptime(f"{år}-W{uke:02d}-1", "%G-W%V-%u")


def _dato_til_yyyyww(d: datetime) -> str:
    iso = d.isocalendar()
    return f"{iso[0]}{iso[1]:02d}"


def _månedsnavn_til_nr(navn: str) -> Optional[int]:
    m = {
        "januar": 1, "februar": 2, "mars": 3, "april": 4,
        "mai": 5, "juni": 6, "juli": 7, "august": 8,
        "september": 9, "oktober": 10, "november": 11, "desember": 12,
    }
    return m.get(navn.lower().strip())


def _parse_periode_filter(periode_str: str) -> tuple[list[str], list[int]]:
    """
    Returner (liste med YYYYWW-strenger, liste med relevante år).
    """
    s = periode_str.strip()
    today = datetime.today()

    # YTD
    if s.upper() == "YTD":
        uker = []
        d = datetime(today.year, 1, 4)  # første uke i året
        while d <= today:
            uker.append(_dato_til_yyyyww(d))
            d += timedelta(weeks=1)
        return list(dict.fromkeys(uker)), [today.year]

    # Enkelt år  "2025"
    if s.isdigit() and len(s) == 4:
        år = int(s)
        uker = []
        d = datetime(år, 1, 4)
        while d.year == år or (d.isocalendar()[0] == år):
            yyyyww = _dato_til_yyyyww(d)
            if yyyyww.startswith(str(år)):
                uker.append(yyyyww)
            d += timedelta(weeks=1)
            if d.year > år and d.isocalendar()[0] > år:
                break
        return list(dict.fromkeys(uker)), [år]

    # Enkelt YYYYWW  "202510"
    if s.isdigit() and len(s) == 6:
        return [s], [int(s[:4])]

    # Rekke YYYYWW–YYYYWW  "202501-202512"
    if "-" in s and not s.startswith("-"):
        parts = s.split("-")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            start, slutt = int(parts[0]), int(parts[1])
            uker = [str(w) for w in range(start, slutt + 1)]
            år = list({int(w[:4]) for w in uker})
            return uker, år

    # Q1–Q4  "Q1 2025"
    q_måneder = {"Q1": (1, 3), "Q2": (4, 6), "Q3": (7, 9), "Q4": (10, 12)}
    s_upper = s.upper()
    for q, (mfra, mtil) in q_måneder.items():
        if s_upper.startswith(q):
            deler = s.split()
            år = int(deler[1]) if len(deler) > 1 else today.year
            uker = []
            for mnd in range(mfra, mtil + 1):
                # Første og siste dag i måneden
                første = datetime(år, mnd, 1)
                if mnd == 12:
                    siste = datetime(år, 12, 31)
                else:
                    siste = datetime(år, mnd + 1, 1) - timedelta(days=1)
                d = første
                while d <= siste:
                    uker.append(_dato_til_yyyyww(d))
                    d += timedelta(weeks=1)
            return list(dict.fromkeys(uker)), [år]

    # Månedsnavn  "mars 2025"
    s_lower = s.lower()
    for navn in ["januar","februar","mars","april","mai","juni",
                 "juli","august","september","oktober","november","desember"]:
        if navn in s_lower:
            mnd_nr = _månedsnavn_til_nr(navn)
            rest = s_lower.replace(navn, "").strip()
            år = int(rest) if rest.isdigit() else today.year
            første = datetime(år, mnd_nr, 1)
            siste = (datetime(år, mnd_nr + 1, 1) - timedelta(days=1)) if mnd_nr < 12 else datetime(år, 12, 31)
            uker = []
            d = første
            while d <= siste:
                uker.append(_dato_til_yyyyww(d))
                d += timedelta(weeks=1)
            return list(dict.fromkeys(uker)), [år]

    # "uke 10 2025" eller "uke 10"
    if "uke" in s_lower:
        deler = s_lower.replace("uke", "").split()
        uke_nr = int(deler[0]) if deler else None
        år = int(deler[1]) if len(deler) > 1 else today.year
        if uke_nr:
            return [f"{år}{uke_nr:02d}"], [år]

    raise ValueError(
        f"Ugyldig periode: '{periode_str}'. "
        "Bruk YYYYWW, 'uke N YYYY', månedsnavn, Q1–Q4 YYYY, årstall eller YTD."
    )


def _last_trans(år_liste: list[int]) -> list[dict]:
    rader = []
    trans_dir = _get_trans_dir()
    for år in sorted(set(år_liste)):
        fil = trans_dir / f"{år} AlleTimetransaksjoner.csv"
        if fil.exists():
            rader.extend(_les_tab(fil))
    return rader


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def check_data() -> str:
    """Sjekk at timetransaksjonsfiler er tilgjengelig og vis sist oppdatert."""
    linjer = []
    try:
        td = _get_trans_dir()
        filer = sorted(td.glob("* AlleTimetransaksjoner.csv"))
        for fil in filer:
            stat = fil.stat()
            sist = datetime.fromtimestamp(stat.st_mtime).strftime("%d.%m.%Y %H:%M")
            linjer.append(f"  {fil.name:<45} oppdatert {sist}")
        if not filer:
            linjer.append("  Ingen timetransaksjonsfiler funnet.")
    except FileNotFoundError as e:
        linjer.append(f"  MANGLER: {e}")

    try:
        dd = _get_dim_dir()
        for fil in sorted(dd.glob("DimensjonProsjekt*.csv")):
            stat = fil.stat()
            sist = datetime.fromtimestamp(stat.st_mtime).strftime("%d.%m.%Y %H:%M")
            linjer.append(f"  {fil.name:<45} oppdatert {sist}")
    except FileNotFoundError as e:
        linjer.append(f"  MANGLER dimensjoner: {e}")

    return "Timetransaksjonsfiler:\n\n" + "\n".join(linjer)


@mcp.tool()
def list_available_years() -> str:
    """List tilgjengelige årsbaserte timetransaksjonsfiler."""
    td = _get_trans_dir()
    filer = sorted(td.glob("???? AlleTimetransaksjoner.csv"))
    if not filer:
        return "Ingen årsbaserte timetransaksjonsfiler funnet."
    linjer = []
    for fil in filer:
        stat = fil.stat()
        sist = datetime.fromtimestamp(stat.st_mtime).strftime("%d.%m.%Y")
        size = f"{stat.st_size / 1024:.0f} KB"
        linjer.append(f"  {fil.name[:4]}  {size:>8}  sist oppdatert {sist}")
    return f"Tilgjengelige år ({len(filer)} filer):\n\n" + "\n".join(linjer)


@mcp.tool()
def get_time_by_person(
    ressnr_eller_navn: str = "",
    periode: str = "YTD",
    vis_detaljer: bool = False,
) -> str:
    """
    Hent timer per prosjekt for en person.

    Args:
        ressnr_eller_navn: Ressursnummer eller navn. Tomt = Frode Solem (39036).
        periode: Periode-filter. Eks: "2025", "Q1 2025", "mars 2025", "YTD", "202510",
                 "uke 10 2025", "202501-202512". Standard: YTD.
        vis_detaljer: True = vis enkeltlinjer per uke/prosjekt. False = summert per prosjekt.
    """
    dim = _get_dim_dir()
    ressurser = {r["Ressnr"]: r["Navn"] for r in _les_tab(dim / "DimensjonRessurser.csv")}
    try:
        prosjekter = {r["Prosjekt"]: r.get("Beskrivelse", "") for r in _les_tab(dim / "DimensjonProsjektregister.csv")}
    except Exception:
        prosjekter = {}

    # Finn ressnr
    s = ressnr_eller_navn.strip()
    if not s:
        ressnr = DEFAULT_RESSNR
    elif s in ressurser:
        ressnr = s
    else:
        s_lower = s.lower()
        ressnr = next(
            (rn for rn, navn in ressurser.items() if s_lower in navn.lower()),
            None
        )
        if not ressnr:
            return f"Fant ikke ressurs '{ressnr_eller_navn}'."
    navn_vis = ressurser.get(ressnr, ressnr)

    try:
        periode_filter, år_liste = _parse_periode_filter(periode)
    except ValueError as e:
        return str(e)

    trans = _last_trans(år_liste)
    filtrert = [
        t for t in trans
        if t.get("Ressnr", "").strip() == ressnr
        and t.get("Periode", "").strip() in set(periode_filter)
    ]

    if not filtrert:
        return f"Ingen timetransaksjoner funnet for {navn_vis} i perioden '{periode}'."

    # Grupper per prosjekt
    proj_sum: dict[str, float] = defaultdict(float)
    detaljer: list[tuple] = []
    for t in filtrert:
        proj = t.get("Prosjekt", "").strip()
        timer = _til_timer(t.get("Timer", "0"))
        per = t.get("Periode", "").strip()
        tekst = t.get("Tekst", "").strip()
        dato = t.get("Bilagsdato", "").strip()
        proj_sum[proj] += timer
        if vis_detaljer:
            detaljer.append((per, proj, dato, timer, tekst))

    total = sum(proj_sum.values())
    flex = proj_sum.get(FLEX_PROSJEKT, 0.0)
    arbeid = total - flex

    antall_uker = len(set(
        t.get("Periode", "") for t in filtrert
        if t.get("Prosjekt", "").strip() != FLEX_PROSJEKT
    ))
    norm = NORM_TIMER_UKE * antall_uker

    linjer = [
        f"TIMER – {navn_vis} (Ressnr: {ressnr}) – {periode}",
        "=" * 70,
        f"{'PROSJEKT':<12}  {'BESKRIVELSE':<35}  {'TIMER':>8}",
        f"  {'-'*12}  {'-'*35}  {'-'*8}",
    ]
    for proj, timer in sorted(proj_sum.items(), key=lambda x: -abs(x[1])):
        if proj == FLEX_PROSJEKT:
            continue
        beskrivelse = prosjekter.get(proj, "")[:35]
        linjer.append(f"  {proj:<12}  {beskrivelse:<35}  {_fmt_timer(timer):>8}")

    if flex != 0.0:
        linjer.append(f"  {FLEX_PROSJEKT:<12}  {'Flexitid':<35}  {_fmt_timer(flex):>8}")

    linjer.extend([
        f"{'─'*70}",
        f"  Total arbeidstid:  {_fmt_timer(arbeid):>8}",
        f"  Flex (S9990015):   {_fmt_timer(flex):>8}",
        f"  Netto arbeid:      {_fmt_timer(total):>8}",
        "",
        f"  Arbeidsuke-norm:   {NORM_TIMER_UKE} t/uke × {antall_uker} uker = {_fmt_timer(norm)}",
        f"  Avvik fra norm:    {_fmt_timer(arbeid - norm)}",
    ])

    if vis_detaljer and detaljer:
        linjer.append(f"\n{'─'*70}\nDetaljer:")
        linjer.append(f"  {'UKE':<8}  {'DATO':<12}  {'PROSJEKT':<12}  {'TIMER':>6}  TEKST")
        for per, proj, dato, timer, tekst in sorted(detaljer):
            linjer.append(f"  {per:<8}  {dato:<12}  {proj:<12}  {_fmt_timer(timer):>6}  {tekst[:40]}")

    return "\n".join(linjer)


@mcp.tool()
def get_time_by_project(
    prosjekt: str,
    periode: str = "YTD",
) -> str:
    """
    Hent ressursbruk (hvem jobbet og hvor mye) på et prosjekt.

    Args:
        prosjekt: Prosjektkode (f.eks. "S2010001") eller del av prosjektnavn
        periode: Periode-filter. Eks: "2025", "Q1 2025", "mars 2025", "YTD", "202510".
    """
    dim = _get_dim_dir()
    ressurser = {r["Ressnr"]: r["Navn"] for r in _les_tab(dim / "DimensjonRessurser.csv")}
    try:
        prosjekter = {r["Prosjekt"]: r.get("Beskrivelse", "") for r in _les_tab(dim / "DimensjonProsjektregister.csv")}
    except Exception:
        prosjekter = {}

    # Finn prosjektkode
    proj_søk = prosjekt.strip().upper()
    if proj_søk not in prosjekter:
        treff = [k for k, v in prosjekter.items() if proj_søk in k.upper() or proj_søk.lower() in v.lower()]
        if not treff:
            # Prøv direkte uten register-oppslag
            treff = [proj_søk]
        proj_kode = treff[0]
    else:
        proj_kode = proj_søk
    proj_navn = prosjekter.get(proj_kode, proj_kode)

    try:
        periode_filter, år_liste = _parse_periode_filter(periode)
    except ValueError as e:
        return str(e)

    trans = _last_trans(år_liste)
    filtrert = [
        t for t in trans
        if t.get("Prosjekt", "").strip().upper() == proj_kode.upper()
        and t.get("Periode", "").strip() in set(periode_filter)
    ]

    if not filtrert:
        return f"Ingen timetransaksjoner funnet for prosjekt {proj_kode} i perioden '{periode}'."

    ress_sum: dict[str, float] = defaultdict(float)
    uke_sum: dict[str, float] = defaultdict(float)
    for t in filtrert:
        ress_sum[t.get("Ressnr", "").strip()] += _til_timer(t.get("Timer", "0"))
        uke_sum[t.get("Periode", "").strip()] += _til_timer(t.get("Timer", "0"))

    total = sum(ress_sum.values())

    linjer = [
        f"TIMER PER PROSJEKT – {proj_kode}: {proj_navn} – {periode}",
        "=" * 70,
        f"\nRessursbruk:",
        f"  {'RESSNR':<8}  {'NAVN':<30}  {'TIMER':>8}  {'%':>6}",
        f"  {'-'*8}  {'-'*30}  {'-'*8}  {'-'*6}",
    ]
    for ressnr, timer in sorted(ress_sum.items(), key=lambda x: -x[1]):
        navn = ressurser.get(ressnr, ressnr)
        pst = (timer / total * 100) if total else 0
        linjer.append(f"  {ressnr:<8}  {navn:<30}  {_fmt_timer(timer):>8}  {pst:>5.1f}%")

    linjer.extend([
        f"  {'─'*56}",
        f"  {'Total':<40}  {_fmt_timer(total):>8}",
        f"\nPer uke:",
        f"  {'UKE':<8}  {'TIMER':>8}",
    ])
    for per, timer in sorted(uke_sum.items()):
        linjer.append(f"  {per:<8}  {_fmt_timer(timer):>8}")

    return "\n".join(linjer)


@mcp.tool()
def get_flex_balance(
    ressnr_eller_navn: str = "",
    periode: str = "YTD",
) -> str:
    """
    Beregn flex-saldo (prosjekt S9990015) for en person.

    Args:
        ressnr_eller_navn: Ressursnummer eller navn. Tomt = Frode Solem (39036).
        periode: Periode-filter. Standard: YTD.
    """
    dim = _get_dim_dir()
    ressurser = {r["Ressnr"]: r["Navn"] for r in _les_tab(dim / "DimensjonRessurser.csv")}

    s = ressnr_eller_navn.strip()
    if not s:
        ressnr = DEFAULT_RESSNR
    elif s in ressurser:
        ressnr = s
    else:
        s_lower = s.lower()
        ressnr = next((rn for rn, navn in ressurser.items() if s_lower in navn.lower()), None)
        if not ressnr:
            return f"Fant ikke ressurs '{ressnr_eller_navn}'."
    navn_vis = ressurser.get(ressnr, ressnr)

    try:
        periode_filter, år_liste = _parse_periode_filter(periode)
    except ValueError as e:
        return str(e)

    trans = _last_trans(år_liste)
    flex_rader = [
        t for t in trans
        if t.get("Ressnr", "").strip() == ressnr
        and t.get("Prosjekt", "").strip() == FLEX_PROSJEKT
        and t.get("Periode", "").strip() in set(periode_filter)
    ]

    if not flex_rader:
        return f"Ingen flex-transaksjoner funnet for {navn_vis} i perioden '{periode}'."

    opptjening = sum(_til_timer(t.get("Timer", "0")) for t in flex_rader if _til_timer(t.get("Timer", "0")) > 0)
    uttak = sum(_til_timer(t.get("Timer", "0")) for t in flex_rader if _til_timer(t.get("Timer", "0")) < 0)
    saldo = opptjening + uttak

    linjer_per_uke: dict[str, float] = defaultdict(float)
    for t in flex_rader:
        linjer_per_uke[t.get("Periode", "").strip()] += _til_timer(t.get("Timer", "0"))

    detaljer = "\n".join(
        f"  {per:<8}  {_fmt_timer(timer):>8}  {'(opptjening)' if timer > 0 else '(uttak)'}"
        for per, timer in sorted(linjer_per_uke.items())
    )

    return (
        f"FLEX-SALDO – {navn_vis} (Ressnr: {ressnr}) – {periode}\n"
        f"{'='*50}\n"
        f"  Opptjening:  {_fmt_timer(opptjening):>8}\n"
        f"  Uttak:       {_fmt_timer(uttak):>8}\n"
        f"  {'─'*30}\n"
        f"  Saldo:       {_fmt_timer(saldo):>8}  "
        f"({'pluss' if saldo >= 0 else 'minus'})\n\n"
        f"Per uke:\n{detaljer}"
    )


@mcp.tool()
def search_project(sokeord: str) -> str:
    """
    Søk i prosjektregisteret på kode eller navn.

    Args:
        sokeord: Prosjektkode (f.eks. "S2010") eller del av prosjektnavn
    """
    dim = _get_dim_dir()
    try:
        prosjekter = _les_tab(dim / "DimensjonProsjektregister.csv")
    except FileNotFoundError:
        return "DimensjonProsjektregister.csv ikke funnet."

    s = sokeord.strip().lower()
    funn = [
        r for r in prosjekter
        if s in r.get("Prosjekt", "").lower() or s in r.get("Beskrivelse", "").lower()
    ]

    if not funn:
        return f"Ingen prosjekter funnet for '{sokeord}'."

    linjer = [
        f"  {r.get('Prosjekt',''):<14}  {r.get('Beskrivelse','')[:50]}"
        for r in funn
    ]
    return f"Prosjekter ({len(funn)} treff for '{sokeord}'):\n\n" + "\n".join(linjer)


if __name__ == "__main__":
    mcp.run()
