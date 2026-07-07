"""Parse fetched HTML into Lead records.

Uses the standard-library HTML parser so the core pipeline has zero dependencies.
The extractor targets a stable, documented record shape:

    <article class="listing"
             data-parcel="..." data-owner="..." data-address="..."
             data-city="..." data-state="..." data-zip="..."
             data-mailing="..." data-phone="..." data-email="..."
             data-type="..." data-signals="pre_foreclosure vacant"></article>

Real county / marketplace pages never look exactly like this, so `Scrapling` (see
`fetch.py`) is the intended production extractor for messy live HTML. This parser is
the deterministic, offline-testable baseline and the contract the fixtures honor.
"""

from __future__ import annotations

from html.parser import HTMLParser

from .models import Lead

# maps a data-* attribute to a Lead field
_ATTR_MAP = {
    "data-parcel": "parcel_id",
    "data-owner": "owner_name",
    "data-address": "property_address",
    "data-city": "city",
    "data-state": "state",
    "data-zip": "zip_code",
    "data-mailing": "mailing_address",
    "data-phone": "phone",
    "data-email": "email",
    "data-type": "property_type",
}


class _ListingParser(HTMLParser):
    def __init__(self, source: str) -> None:
        super().__init__(convert_charrefs=True)
        self.source = source
        self.leads: list[Lead] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {k: (v or "") for k, v in attrs}
        classes = attr.get("class", "").split()
        if "listing" not in classes:
            return

        lead = Lead(source=self.source)
        for data_key, field_name in _ATTR_MAP.items():
            if data_key in attr:
                setattr(lead, field_name, attr[data_key].strip())

        raw_signals = attr.get("data-signals", "")
        lead.signals = [s.strip() for s in raw_signals.replace(",", " ").split() if s.strip()]
        self.leads.append(lead)


def parse_listings(html: str, source: str) -> list[Lead]:
    """Extract Lead records from a listings HTML page."""
    parser = _ListingParser(source)
    parser.feed(html)
    return parser.leads
