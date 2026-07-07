"""Core domain types for the Hunter pipeline."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field, asdict
from typing import Any


class Grade(str, enum.Enum):
    """Seller-lead grades, best to worst (mirrors LeadPack tiers)."""

    PLATINUM = "Platinum"
    GOLD = "Gold"
    SILVER = "Silver"
    BRONZE = "Bronze"
    REJECT = "Reject"  # failed the minimum-data gate; not a sellable lead

    @property
    def is_sellable(self) -> bool:
        return self is not Grade.REJECT


# Motivation signals mined from public records. Values are point weights used by
# the grader; keeping them here makes the rubric a single source of truth.
SIGNAL_WEIGHTS: dict[str, int] = {
    "pre_foreclosure": 40,
    "tax_delinquent": 30,
    "high_equity": 25,
    "vacant": 20,
    "probate": 20,
    "absentee_owner": 15,
    "code_violation": 15,
    "liens": 10,
}

# Contactability points — a lead you can't reach is worth less regardless of motivation.
CONTACT_WEIGHTS: dict[str, int] = {
    "owner_name": 5,
    "mailing_address": 5,
    "phone": 10,
    "email": 10,
}


@dataclass
class Lead:
    """A single seller-lead record flowing through the pipeline."""

    source: str
    parcel_id: str = ""
    owner_name: str = ""
    property_address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    mailing_address: str = ""
    phone: str = ""
    email: str = ""
    property_type: str = ""
    signals: list[str] = field(default_factory=list)

    # populated by the grader
    score: int = 0
    grade: str = ""
    grade_reasons: list[str] = field(default_factory=list)

    def has_min_data(self) -> bool:
        """Minimum viable lead: a property we can locate and an owner to contact."""
        located = bool(self.property_address and (self.city or self.zip_code))
        contactable = bool(self.owner_name or self.mailing_address or self.phone or self.email)
        return located and contactable

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row["signals"] = ";".join(self.signals)
        row["grade_reasons"] = ";".join(self.grade_reasons)
        return row


# Stable CSV column order for LeadPack deliverables.
CSV_COLUMNS = [
    "grade",
    "score",
    "source",
    "parcel_id",
    "owner_name",
    "property_address",
    "city",
    "state",
    "zip_code",
    "mailing_address",
    "phone",
    "email",
    "property_type",
    "signals",
    "grade_reasons",
]
