"""Buyer/wholesaler finder — the demand side of the two-sided market (FD-003).

Wholesalers, cash buyers, and acquisition firms are BUSINESSES with public contact
info, so ranking + storing them is inside the FD-001 compliance floor (that floor
restricts private-homeowner PII, not business listings).

Ranking follows CEO REVIEW 001's axes — Urgency · Budget · Response probability ·
Decision speed · Expected LTV — mapped onto observable buying signals. Pure functions;
fetch/parse reuse the same offline-safe stack as the seller pipeline.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field, asdict
from html.parser import HTMLParser
from typing import Any

from .fetch import fetch_html
from .sources import Source, get_source


class Tier(str, enum.Enum):
    HOT = "Hot"
    WARM = "Warm"
    COLD = "Cold"
    NO_CONTACT = "No-contact"  # can't be reached -> not actionable


# Buying signals -> points. Weighted by the CEO-REVIEW-001 axes they evidence.
BUYER_SIGNAL_WEIGHTS: dict[str, int] = {
    "list_request": 40,        # actively asking for lists — urgency + response
    "acquiring": 30,           # active deal flow — budget + LTV
    "high_volume": 30,         # scale — budget + LTV
    "hiring_acquisitions": 25, # staffing up — budget + decision speed
    "expanding_market": 20,    # new market — urgency
    "cash_buyer": 15,          # can close fast — decision speed
}

BUYER_CONTACT_WEIGHTS: dict[str, int] = {"email": 10, "phone": 8, "website": 4}

TIER_RULES = [(70, Tier.HOT), (40, Tier.WARM), (0, Tier.COLD)]

# maps a data-* attribute to a Buyer field
_ATTR_MAP = {
    "data-company": "company",
    "data-name": "name",
    "data-role": "role",
    "data-market": "market",
    "data-email": "email",
    "data-phone": "phone",
    "data-website": "website",
    "data-reason": "contact_reason",
}


@dataclass
class Buyer:
    source: str
    company: str = ""
    name: str = ""
    role: str = ""
    market: str = ""
    email: str = ""
    phone: str = ""
    website: str = ""
    signals: list[str] = field(default_factory=list)
    contact_reason: str = ""  # the [WHY-THEM] personalization slot
    score: int = 0
    tier: str = ""
    reasons: list[str] = field(default_factory=list)

    def has_contact(self) -> bool:
        return bool(self.email or self.phone or self.website)

    def dedup_key(self) -> str:
        def norm(s: str) -> str:
            return " ".join(s.lower().split())
        if self.email:
            return f"email:{norm(self.email)}"
        if self.company:
            return f"company:{norm(self.company)}|{norm(self.market)}"
        return f"name:{norm(self.name)}|{norm(self.phone)}"

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row["signals"] = ";".join(self.signals)
        row["reasons"] = ";".join(self.reasons)
        return row


BUYER_CSV_COLUMNS = [
    "tier", "score", "source", "company", "name", "role", "market",
    "email", "phone", "website", "signals", "contact_reason", "reasons",
]


class _BuyerParser(HTMLParser):
    def __init__(self, source: str) -> None:
        super().__init__(convert_charrefs=True)
        self.source = source
        self.buyers: list[Buyer] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {k: (v or "") for k, v in attrs}
        if "buyer" not in attr.get("class", "").split():
            return
        buyer = Buyer(source=self.source)
        for data_key, field_name in _ATTR_MAP.items():
            if data_key in attr:
                setattr(buyer, field_name, attr[data_key].strip())
        raw = attr.get("data-signals", "")
        buyer.signals = [s.strip() for s in raw.replace(",", " ").split() if s.strip()]
        self.buyers.append(buyer)


def parse_buyers(html: str, source: str) -> list[Buyer]:
    p = _BuyerParser(source)
    p.feed(html)
    return p.buyers


def rank_buyer(buyer: Buyer) -> Buyer:
    """Score and tier a buyer in place. No contact path -> NO_CONTACT regardless."""
    if not buyer.has_contact():
        buyer.score = 0
        buyer.tier = Tier.NO_CONTACT.value
        buyer.reasons = ["no public contact path"]
        return buyer

    score = 0
    reasons: list[str] = []
    for sig in buyer.signals:
        w = BUYER_SIGNAL_WEIGHTS.get(sig)
        if w:
            score += w
            reasons.append(f"+{w} {sig}")
    for fname, w in BUYER_CONTACT_WEIGHTS.items():
        if getattr(buyer, fname):
            score += w
            reasons.append(f"+{w} {fname}")

    buyer.score = score
    for threshold, tier in TIER_RULES:
        if score >= threshold:
            buyer.tier = tier.value
            break
    buyer.reasons = reasons
    return buyer


def rank_all(buyers: list[Buyer]) -> list[Buyer]:
    for b in buyers:
        rank_buyer(b)
    order = {t.value: i for i, t in enumerate(
        [Tier.HOT, Tier.WARM, Tier.COLD, Tier.NO_CONTACT])}
    return sorted(buyers, key=lambda b: (order.get(b.tier, 99), -b.score))


def merge_buyers(buyers: list[Buyer]) -> list[Buyer]:
    """Dedup by key, unioning signals and backfilling blank fields. Preserves order."""
    order: list[str] = []
    by_key: dict[str, Buyer] = {}
    for b in buyers:
        key = b.dedup_key()
        if key not in by_key:
            by_key[key] = b
            order.append(key)
            continue
        keep = by_key[key]
        for sig in b.signals:
            if sig not in keep.signals:
                keep.signals.append(sig)
        for fname in ("company", "name", "role", "market", "email", "phone",
                      "website", "contact_reason"):
            if not getattr(keep, fname) and getattr(b, fname):
                setattr(keep, fname, getattr(b, fname))
    return [by_key[k] for k in order]


def find_buyers(source: str | Source, *, backend: str = "auto") -> list[Buyer]:
    """Fetch -> parse -> dedup -> rank a wholesaler/buyer source."""
    src = source if isinstance(source, Source) else get_source(source)
    html = fetch_html(src.location, render=src.render, backend=backend)
    return rank_all(merge_buyers(parse_buyers(html, source=src.name)))


def buyers_to_csv(buyers: list[Buyer], *, actionable_only: bool = False) -> str:
    """Serialize buyers to CSV (stable columns). actionable_only drops NO_CONTACT."""
    import csv
    import io
    rows = [b for b in buyers
            if not actionable_only or b.tier != Tier.NO_CONTACT.value]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=BUYER_CSV_COLUMNS, extrasaction="ignore")
    w.writeheader()
    for b in rows:
        w.writerow(b.to_row())
    return buf.getvalue()
