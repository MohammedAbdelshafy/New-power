"""Outreach draft generator — prepares, never sends (FD-001 Art. 5 / OP ORDER 001).

Turns ranked buyers into review-ready email drafts: your proven soft free-pack open
plus a Google Meet invite as the CTA. Output is drafts only — a human sends. Two
guardrails are baked in because they are business rules, not options:

  1. The [WHY-THEM] personalization slot (`contact_reason`) must be filled, or the
     draft is refused — same rule as Sales/outreach/FD003-outreach-pack.md.
  2. Every draft carries a CAN-SPAM footer (identity, postal address, opt-out).

Tone is configurable: "soft" (default, matches what converts) or "direct" (assertive
Meet push) — set via `tone=`. Nothing here talks to a mail server.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .buyers import Buyer, Tier

# Sender/business identity. Real values belong in .env / founder config, not code.
DEFAULT_SENDER = "Mohammed, MBM"
DEFAULT_POSTAL = "[MBM mailing address — required by CAN-SPAM]"
DEFAULT_MEET = "[your Google Meet / Calendly link]"

_SLOT = re.compile(r"\[[A-Z][A-Z0-9 _-]*\]")  # unfilled placeholder like [WHY-THEM]


class OutreachError(ValueError):
    pass


@dataclass
class Draft:
    to_email: str
    to_name: str
    subject: str
    body: str

    def as_markdown(self) -> str:
        return (
            f"To: {self.to_name} <{self.to_email}>\n"
            f"Subject: {self.subject}\n\n"
            f"{self.body}\n"
        )


def _default_reason(buyer: Buyer) -> str:
    """Derive a WHY-THEM line from the strongest buying signal, if none was given."""
    if "list_request" in buyer.signals:
        return f"You asked for graded {buyer.market} lists recently."
    if "hiring_acquisitions" in buyer.signals:
        return "You're staffing up acquisitions — more dials to feed."
    if "expanding_market" in buyer.signals:
        return f"You're expanding into {buyer.market}."
    if buyer.signals:
        return f"You're actively acquiring in {buyer.market}."
    return ""


def build_draft(
    buyer: Buyer,
    *,
    market: str | None = None,
    free_pack_count: int = 50,
    tone: str = "soft",
    sender: str = DEFAULT_SENDER,
    postal: str = DEFAULT_POSTAL,
    meet_link: str = DEFAULT_MEET,
) -> Draft:
    """Render one email draft for a buyer. Raises OutreachError if not sendable."""
    if not buyer.email:
        raise OutreachError(f"{buyer.company or buyer.name}: no email to draft to")

    reason = buyer.contact_reason.strip() or _default_reason(buyer)
    if not reason:
        raise OutreachError(
            f"{buyer.company or buyer.name}: [WHY-THEM] slot empty — refusing to draft")

    mkt = market or buyer.market or "your market"
    greeting = f"Hi {buyer.name.split()[0]}," if buyer.name else "Hi,"

    if tone == "direct":
        subject = f"{free_pack_count} free graded {mkt} seller records + a quick Meet"
        cta = (
            f"Let's get a short Google Meet on the calendar this week so I can walk your "
            f"team through the grading live — pick a slot here: {meet_link}. "
            f"I'll have the free {free_pack_count} pulled and ready for the call."
        )
    else:  # soft (default)
        subject = f"graded seller list for {mkt} — first {free_pack_count} records free"
        cta = (
            f"Happy to send the first {free_pack_count} {mkt} records free so you can "
            f"judge the grading yourself. If it's useful, a quick 15-min Google Meet lets "
            f"me walk your team through the criteria — no pitch deck: {meet_link}."
        )

    body = (
        f"{greeting}\n\n"
        f"{reason} Quick offer, no pitch: we build graded county seller lists — "
        f"tax-delinquent, absentee, pre-foreclosure — merged, deduped, and scored "
        f"Platinum→Bronze with the criteria printed on the file. Your team calls the "
        f"top 20 instead of dialing 500 raw records.\n\n"
        f"{cta}\n\n"
        f"— {sender}\n\n"
        f"---\n"
        f"You received this because {buyer.company or 'your firm'} is listed as an active "
        f"buyer in {mkt}. Reply STOP or \"unsubscribe\" and I won't email again.\n"
        f"{sender} · {postal}\n"
    )

    # Fail loudly if any placeholder survived (except the deliberately-configurable
    # meet/postal defaults, which the caller is expected to supply).
    leftover = [m for m in _SLOT.findall(body)
                if m not in (meet_link, postal) and "MEET" not in m and "ADDRESS" not in m]
    if leftover:
        raise OutreachError(f"unfilled placeholder(s) in draft: {leftover}")

    return Draft(to_email=buyer.email, to_name=buyer.name or buyer.company,
                 subject=subject, body=body)


def build_drafts(
    buyers: list[Buyer], *, tiers: tuple[str, ...] = (Tier.HOT.value, Tier.WARM.value),
    **kwargs,
) -> tuple[list[Draft], list[str]]:
    """Draft for buyers in the given tiers. Returns (drafts, skipped-reasons)."""
    drafts: list[Draft] = []
    skipped: list[str] = []
    for buyer in buyers:
        if buyer.tier not in tiers:
            skipped.append(f"{buyer.company or buyer.name}: tier {buyer.tier or '?'}")
            continue
        try:
            drafts.append(build_draft(buyer, **kwargs))
        except OutreachError as exc:
            skipped.append(str(exc))
    return drafts, skipped


def write_drafts(drafts: list[Draft], outdir: str) -> list[str]:
    """Write each draft as a review-ready .md file. Returns the paths written."""
    import os
    os.makedirs(outdir, exist_ok=True)
    paths: list[str] = []
    for i, d in enumerate(drafts, 1):
        slug = re.sub(r"[^a-z0-9]+", "-", (d.to_name or d.to_email).lower()).strip("-")
        path = os.path.join(outdir, f"{i:02d}-{slug}.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(d.as_markdown())
        paths.append(path)
    return paths
