"""Source registry — where the Hunter looks for seller leads.

A Source is a named place to fetch leads from. It can be:
  - a local fixture (offline-safe, used for tests + smoke), or
  - a live URL (fetched via the backends in fetch.py).

Add real county / marketplace sources here as they are onboarded and verified
(see jarvis-mbm/Knowledge/Seller_Source_Playbook.md for the intake standard).
Keeping sources declarative means onboarding a source is a data change, not a code change.
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass

FIXTURES = pathlib.Path(__file__).resolve().parent.parent / "fixtures"


@dataclass(frozen=True)
class Source:
    name: str
    location: str          # URL or local path
    render: bool = False   # needs JS execution?
    live: bool = False     # True hits the network; False reads a local fixture
    notes: str = ""


# The registry. The fixture source lets the whole pipeline run with no network/keys.
REGISTRY: dict[str, Source] = {
    "fixture-county": Source(
        name="fixture-county",
        location=str(FIXTURES / "sample_listings.html"),
        render=False,
        live=False,
        notes="Synthetic county-records page for offline tests + smoke runs.",
    ),
    "fixture-marketplace": Source(
        name="fixture-marketplace",
        location=str(FIXTURES / "sample_marketplace.html"),
        render=False,
        live=False,
        notes="Synthetic off-market feed; overlaps county parcels to exercise dedup.",
    ),
    "fixture-wholesalers": Source(
        name="fixture-wholesalers",
        location=str(FIXTURES / "sample_wholesalers.html"),
        render=False,
        live=False,
        notes="Synthetic public buyer directory (business listings) for the buyer finder.",
    ),
    # --- Add verified live sources below. Examples (disabled until onboarded): ---
    # "hillsborough-fl-taxdeed": Source(
    #     name="hillsborough-fl-taxdeed",
    #     location="https://<county-portal>/taxdeed/search?status=delinquent",
    #     render=True, live=True,
    #     notes="JS portal -> needs scrapling/playwright. Verify ToS + robots before enabling.",
    # ),
}


@dataclass(frozen=True)
class GatedSource:
    """A site we know about but will NOT scrape until compliance clears it."""
    name: str
    url: str
    reason: str


# Commercial / ToS-restricted sites. Registered for visibility, DISABLED for use.
# Enabling any of these requires clearing the FD-001 compliance floor (public-record
# sources only) AND the site's Terms of Service — see Seller_Source_Playbook.md.
GATED_SOURCES: list[GatedSource] = [
    GatedSource("auction.com", "https://www.auction.com",
                "Commercial listing platform; ToS prohibits scraping; not a public-record "
                "source (FD-001). Use only via an official API / data license."),
    GatedSource("zillow", "https://www.zillow.com",
                "ToS prohibits scraping; consumer PII. Prefer public county records."),
    GatedSource("realtor.com", "https://www.realtor.com",
                "ToS prohibits scraping. Not a compliant seller source."),
    GatedSource("biggerpockets", "https://www.biggerpockets.com",
                "Buyer discovery only; respect ToS + rate limits; public profiles where "
                "permitted. Never bulk-scrape."),
]


def get_source(name: str) -> Source:
    try:
        return REGISTRY[name]
    except KeyError:
        known = ", ".join(sorted(REGISTRY)) or "(none)"
        raise KeyError(f"unknown source {name!r}; registered: {known}") from None


def list_sources() -> list[Source]:
    return list(REGISTRY.values())
