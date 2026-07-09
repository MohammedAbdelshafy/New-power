"""Lead ledger — the persistent master LeadPack across hunts.

A ledger is a CSV of every lead ever seen, deduplicated, with `first_seen` /
`last_seen` dates so the business can tell fresh inventory from stale and never
re-sells a duplicate. Merging re-enriches and re-grades, because unioning signals
across sources can change a lead's grade (e.g. a second source reveals absentee).
"""

from __future__ import annotations

import csv
import datetime as _dt
import os
from dataclasses import dataclass

from .models import Lead
from .dedup import merge_leads
from .enrich import enrich_all
from .grade import grade_all


def _today() -> str:
    return _dt.date.today().isoformat()


@dataclass
class MergeStats:
    total: int
    new: int
    updated: int

    def __str__(self) -> str:
        return f"ledger: {self.total} total ({self.new} new, {self.updated} updated)"


class Ledger:
    def __init__(self, path: str) -> None:
        self.path = path

    def load(self) -> list[Lead]:
        if not os.path.exists(self.path):
            return []
        with open(self.path, encoding="utf-8", newline="") as fh:
            return [Lead.from_row(row) for row in csv.DictReader(fh)]

    def merge(self, new_leads: list[Lead], *, today: str | None = None) -> tuple[list[Lead], MergeStats]:
        """Merge `new_leads` into the ledger's existing rows; return (leads, stats).

        Dates are reconciled by dedup key: first_seen = earliest ever seen,
        last_seen = today for any key touched this run, else its stored value.
        """
        today = today or _today()
        existing = self.load()
        existing_keys = {l.dedup_key() for l in existing}

        for lead in new_leads:
            lead.first_seen = lead.first_seen or today
            lead.last_seen = today

        # reconcile dates per key across existing + new (ISO strings sort lexically)
        first_by_key: dict[str, str] = {}
        last_by_key: dict[str, str] = {}
        for lead in existing + new_leads:
            key = lead.dedup_key()
            if lead.first_seen:
                cur = first_by_key.get(key)
                first_by_key[key] = min(cur, lead.first_seen) if cur else lead.first_seen
            if lead.last_seen:
                cur = last_by_key.get(key)
                last_by_key[key] = max(cur, lead.last_seen) if cur else lead.last_seen

        merged = merge_leads(existing + new_leads)
        for lead in merged:
            key = lead.dedup_key()
            lead.first_seen = first_by_key.get(key, today)
            lead.last_seen = last_by_key.get(key, today)

        # unioned signals may change the grade -> re-enrich and re-grade
        merged = grade_all(enrich_all(merged))

        new_key_set = {l.dedup_key() for l in new_leads}
        added = len(new_key_set - existing_keys)
        updated = len(new_key_set & existing_keys)
        return merged, MergeStats(total=len(merged), new=added, updated=updated)

    def save(self, leads: list[Lead]) -> None:
        from .pipeline import to_csv  # local import avoids a cycle at module load
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        with open(self.path, "w", encoding="utf-8", newline="") as fh:
            fh.write(to_csv(leads))
