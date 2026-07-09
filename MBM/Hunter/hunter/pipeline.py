"""The Hunter pipeline: fetch -> parse -> grade -> LeadPack CSV.

This is the single orchestration entry point every caller uses (CLI, MCP server,
hermes.sh executor). It is deliberately linear and observable.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass

from .fetch import fetch_html
from .parse import parse_listings
from .enrich import enrich_all
from .dedup import merge_leads
from .grade import grade_all
from .models import Lead, Grade, CSV_COLUMNS
from .sources import Source, get_source


@dataclass
class HuntResult:
    source: str
    leads: list[Lead]

    @property
    def sellable(self) -> list[Lead]:
        return [l for l in self.leads if l.grade != Grade.REJECT.value]

    def summary(self) -> dict[str, int]:
        counts = {g.value: 0 for g in Grade}
        for l in self.leads:
            counts[l.grade] = counts.get(l.grade, 0) + 1
        counts["total"] = len(self.leads)
        counts["sellable"] = len(self.sellable)
        return counts


def hunt(source: str | Source, *, backend: str = "auto") -> HuntResult:
    """Run the full pipeline for one source: fetch -> parse -> enrich -> grade."""
    src = source if isinstance(source, Source) else get_source(source)
    html = fetch_html(src.location, render=src.render, backend=backend)
    leads = parse_listings(html, source=src.name)
    graded = grade_all(enrich_all(leads))
    return HuntResult(source=src.name, leads=graded)


def hunt_many(sources: list[str], *, backend: str = "auto", dedup: bool = True) -> HuntResult:
    """Hunt several sources and combine them, deduplicated by default.

    Enrichment runs per source; dedup (and the re-grade it implies) runs on the
    union, so a lead enriched by a second source is graded on the merged signals.
    """
    all_leads: list[Lead] = []
    for name in sources:
        all_leads.extend(hunt(name, backend=backend).leads)
    label = "+".join(sources)
    if not dedup:
        return HuntResult(source=label, leads=grade_all(all_leads))
    merged = grade_all(enrich_all(merge_leads(all_leads)))
    return HuntResult(source=label, leads=merged)


def to_csv(leads: list[Lead], *, sellable_only: bool = False) -> str:
    """Serialize leads to a LeadPack CSV string (stable column order)."""
    rows = [l for l in leads if not sellable_only or l.grade != Grade.REJECT.value]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=CSV_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for lead in rows:
        writer.writerow(lead.to_row())
    return buf.getvalue()


def write_csv(leads: list[Lead], path: str, *, sellable_only: bool = False) -> int:
    """Write a LeadPack CSV to `path`; return the number of data rows written."""
    rows = [l for l in leads if not sellable_only or l.grade != Grade.REJECT.value]
    text = to_csv(leads, sellable_only=sellable_only)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    return len(rows)  # exact row count; robust to newlines inside quoted fields
