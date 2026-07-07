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
    # --- Add verified live sources below. Examples (disabled until onboarded): ---
    # "hillsborough-fl-taxdeed": Source(
    #     name="hillsborough-fl-taxdeed",
    #     location="https://<county-portal>/taxdeed/search?status=delinquent",
    #     render=True, live=True,
    #     notes="JS portal -> needs scrapling/playwright. Verify ToS + robots before enabling.",
    # ),
}


def get_source(name: str) -> Source:
    try:
        return REGISTRY[name]
    except KeyError:
        known = ", ".join(sorted(REGISTRY)) or "(none)"
        raise KeyError(f"unknown source {name!r}; registered: {known}") from None


def list_sources() -> list[Source]:
    return list(REGISTRY.values())
