"""Signal enrichment — derive motivation signals the source didn't spell out.

Runs after parse and before grade. Pure functions, no I/O. The flagship rule is
absentee-owner detection (owner's mailing address differs from the property), which
is a top wholesaler signal and is almost never labeled on a raw records page.
"""

from __future__ import annotations

import re

from .models import Lead

_WORD = re.compile(r"[a-z0-9]+")

# common street-suffix noise dropped before comparing addresses
_SUFFIXES = {
    "st", "street", "ave", "avenue", "blvd", "boulevard", "rd", "road", "dr",
    "drive", "ln", "lane", "ct", "court", "cir", "circle", "pl", "place", "way",
    "ter", "terrace", "unit", "apt", "ste", "suite", "n", "s", "e", "w",
}


def _tokens(addr: str) -> set[str]:
    """Significant address tokens: street number + name, minus suffix/unit noise."""
    return {t for t in _WORD.findall(addr.lower()) if t not in _SUFFIXES}


def is_absentee(property_address: str, mailing_address: str) -> bool:
    """True when the owner's mail goes somewhere other than the property.

    Compares significant tokens; if the property's street number/name is not
    contained in the mailing address, the owner is absentee. Empty mailing address
    is inconclusive -> not flagged.
    """
    prop = _tokens(property_address)
    mail = _tokens(mailing_address)
    if not prop or not mail:
        return False
    # owner-occupied iff the property's distinctive tokens all appear in the mailing addr
    return not prop.issubset(mail)


def enrich_lead(lead: Lead) -> Lead:
    """Add derived signals and normalize fields in place, then return the lead."""
    lead.state = lead.state.strip().upper()
    lead.zip_code = lead.zip_code.strip()

    if is_absentee(lead.property_address, lead.mailing_address):
        if "absentee_owner" not in lead.signals:
            lead.signals.append("absentee_owner")

    # de-duplicate signals while preserving order (a source may repeat one)
    seen: set[str] = set()
    lead.signals = [s for s in lead.signals if not (s in seen or seen.add(s))]
    return lead


def enrich_all(leads: list[Lead]) -> list[Lead]:
    for lead in leads:
        enrich_lead(lead)
    return leads
