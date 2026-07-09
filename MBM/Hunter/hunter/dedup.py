"""Deduplication — collapse the same property seen across sources or repeat hunts.

Selling the same lead twice burns buyer trust, so this is a first-class step. Leads
are keyed by `Lead.dedup_key()` (parcel id, else owner+address+zip). When two records
share a key we keep the richer one and union their signals and contact fields.
"""

from __future__ import annotations

from .models import Lead


def _merge_pair(keep: Lead, other: Lead) -> Lead:
    """Fold `other` into `keep`: union signals, backfill any missing contact fields."""
    for sig in other.signals:
        if sig not in keep.signals:
            keep.signals.append(sig)
    # backfill blank contact/identity fields from the other record
    for fname in ("owner_name", "mailing_address", "phone", "email",
                  "parcel_id", "property_type", "city", "state", "zip_code"):
        if not getattr(keep, fname) and getattr(other, fname):
            setattr(keep, fname, getattr(other, fname))
    return keep


def merge_leads(leads: list[Lead]) -> list[Lead]:
    """Deduplicate by key, preserving first-seen order.

    The surviving record is the one with more signals (a proxy for richness); ties
    keep the earlier one. Contact fields and signals are unioned across duplicates so
    a merge never loses data. Grading is the caller's job — merge does not grade.
    """
    order: list[str] = []
    by_key: dict[str, Lead] = {}
    for lead in leads:
        key = lead.dedup_key()
        if key not in by_key:
            by_key[key] = lead
            order.append(key)
            continue
        existing = by_key[key]
        if len(lead.signals) > len(existing.signals):
            # promote the richer record to primary, folding the old primary in
            merged = _merge_pair(lead, existing)
            merged.source = existing.source  # keep the first source we saw it from
            by_key[key] = merged
        else:
            _merge_pair(existing, lead)
    return [by_key[k] for k in order]
