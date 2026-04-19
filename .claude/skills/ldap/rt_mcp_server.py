#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp", "ldap3", "keyring"]
# ///
"""
LDAP MCP Server – Sikt/Sigma2
Søk etter ansatte, hent brukerinfo og finn direkte rapporter.
Fungerer på macOS og Windows.
"""

import os
import re
import sys
from mcp.server.fastmcp import FastMCP
from ldap3 import Server, Connection, ALL, SUBTREE

mcp = FastMCP("ldap-sikt")

LDAP_HOST = "ldaps://ldap.sikt.no"
LDAP_BASE = "dc=sikt,dc=no"
LDAP_BIND_TEMPLATE = "uid={uid},ou=users,dc=sikt,dc=no"
KEYCHAIN_SERVICE = "ldap-sikt"


def _get_credentials() -> tuple[str, str]:
    """Hent uid og passord fra Keychain/Credential Manager eller miljøvariabler."""
    uid = os.environ.get("LDAP_UID", "frgri")
    password = os.environ.get("LDAP_PASSWORD")

    if not password:
        try:
            import keyring
            password = keyring.get_password(KEYCHAIN_SERVICE, uid)
        except Exception:
            pass

    if not password:
        raise RuntimeError(
            f"Fant ikke LDAP-passord. Kjør setup_credentials.py eller sett "
            f"miljøvariablene LDAP_UID og LDAP_PASSWORD."
        )
    return uid, password


def _connect() -> Connection:
    uid, password = _get_credentials()
    bind_dn = LDAP_BIND_TEMPLATE.format(uid=uid)
    server = Server(LDAP_HOST, get_info=ALL)
    conn = Connection(server, user=bind_dn, password=password, auto_bind=True)
    return conn


def _entry_to_dict(entry) -> dict:
    result = {}
    for attr in ["cn", "uid", "mail", "title", "telephoneNumber", "manager"]:
        try:
            val = entry[attr].value
            if val:
                result[attr] = str(val)
        except Exception:
            pass
    return result


def _format_user(d: dict) -> str:
    lines = []
    for field in ["cn", "uid", "mail", "title", "telephoneNumber", "manager"]:
        if field in d:
            val = d[field]
            if field == "manager":
                m = re.search(r"uid=([^,]+)", val)
                val = m.group(1) if m else val
            lines.append(f"  {field}: {val}")
    return "\n".join(lines)


@mcp.tool()
def ldap_search(query: str) -> str:
    """
    Søk etter ansatte i Sikt/Sigma2 LDAP.
    Matcher mot navn (cn) og brukernavn (uid).
    Eksempel: ldap_search("basir") eller ldap_search("Roger Kvam")
    """
    conn = _connect()
    conn.search(
        LDAP_BASE,
        f"(|(uid=*{query}*)(cn=*{query}*))",
        search_scope=SUBTREE,
        attributes=["cn", "uid", "mail", "title", "telephoneNumber", "manager"]
    )
    entries = [_entry_to_dict(e) for e in conn.entries]
    conn.unbind()
    if not entries:
        return f"Ingen treff for '{query}'."
    results = [_format_user(e) for e in entries]
    return f"{len(entries)} treff for '{query}':\n\n" + "\n\n".join(results)


@mcp.tool()
def ldap_get_user(uid: str) -> str:
    """
    Hent brukerinfo for et bestemt brukernavn (uid).
    Eksempel: ldap_get_user("frgri")
    """
    conn = _connect()
    conn.search(
        LDAP_BASE,
        f"(uid={uid})",
        search_scope=SUBTREE,
        attributes=["cn", "uid", "mail", "title", "telephoneNumber", "manager", "department"]
    )
    entries = conn.entries
    conn.unbind()
    if not entries:
        return f"Ingen bruker med uid='{uid}'."
    return _format_user(_entry_to_dict(entries[0]))


@mcp.tool()
def ldap_get_reports(manager_uid: str) -> str:
    """
    Hent direkte rapporter for en leder (uid).
    Eksempel: ldap_get_reports("rogkva")
    """
    conn = _connect()
    # Finn lederens DN
    conn.search(LDAP_BASE, f"(uid={manager_uid})", search_scope=SUBTREE, attributes=["dn"])
    if not conn.entries:
        conn.unbind()
        return f"Fant ikke leder med uid='{manager_uid}'."
    manager_dn = str(conn.entries[0].entry_dn)

    # Finn direkte rapporter
    conn.search(
        LDAP_BASE,
        f"(manager={manager_dn})",
        search_scope=SUBTREE,
        attributes=["cn", "uid", "mail", "title"]
    )
    entries = [_entry_to_dict(e) for e in conn.entries]
    conn.unbind()
    if not entries:
        return f"Ingen direkte rapporter for '{manager_uid}'."
    lines = [
        f"{e.get('cn', '?')} ({e.get('uid', '?')}) – {e.get('title', '')} – {e.get('mail', '')}"
        for e in entries
    ]
    return f"Direkte rapporter for {manager_uid} ({len(entries)}):\n\n" + "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
