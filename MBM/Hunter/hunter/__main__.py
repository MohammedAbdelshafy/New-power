"""CLI entry point:  python -m hunter <command>

    python -m hunter sources                          list registered sources
    python -m hunter hunt fixture-county               one source: fetch->enrich->grade
    python -m hunter hunt fixture-county fixture-marketplace   multi-source, deduped
    python -m hunter hunt fixture-county --csv out.csv --sellable-only
    python -m hunter hunt fixture-county --backend playwright  force a fetch backend
    python -m hunter hunt fixture-county --ledger master.csv    merge into a ledger
    python -m hunter ledger master.csv                 show ledger stats
"""

from __future__ import annotations

import argparse
import sys

from .pipeline import hunt, hunt_many, write_csv, to_csv
from .sources import list_sources, GATED_SOURCES
from .ledger import Ledger
from .models import Grade
from .buyers import find_buyers, buyers_to_csv, Tier
from .outreach import build_drafts, write_drafts

_GRADE_ORDER = ["Platinum", "Gold", "Silver", "Bronze", "Reject", "total", "sellable"]


def _print_summary(header: str, summary: dict) -> None:
    print(header)
    for key in _GRADE_ORDER:
        print(f"  {key:9} {summary.get(key, 0)}")


def _cmd_sources(_args: argparse.Namespace) -> int:
    for s in list_sources():
        kind = "live" if s.live else "fixture"
        render = " render" if s.render else ""
        print(f"{s.name:24} [{kind}{render}] {s.location}")
        if s.notes:
            print(f"{'':24} {s.notes}")
    print("\ngated (registered, DISABLED — compliance/ToS):")
    for g in GATED_SOURCES:
        print(f"  {g.name:20} {g.url}\n{'':22} {g.reason}")
    return 0


def _cmd_buyers(args: argparse.Namespace) -> int:
    buyers = find_buyers(args.source, backend=args.backend)
    counts: dict[str, int] = {}
    for b in buyers:
        counts[b.tier] = counts.get(b.tier, 0) + 1
    print(f"source={args.source} backend={args.backend}")
    for tier in (Tier.HOT.value, Tier.WARM.value, Tier.COLD.value, Tier.NO_CONTACT.value):
        print(f"  {tier:11} {counts.get(tier, 0)}")
    print(f"  {'total':11} {len(buyers)}")
    if args.csv:
        with open(args.csv, "w", encoding="utf-8", newline="") as fh:
            fh.write(buyers_to_csv(buyers, actionable_only=args.actionable_only))
        print(f"wrote -> {args.csv}")
    elif args.print_csv:
        sys.stdout.write(buyers_to_csv(buyers, actionable_only=args.actionable_only))
    return 0


def _cmd_outreach(args: argparse.Namespace) -> int:
    buyers = find_buyers(args.source, backend=args.backend)
    tiers = tuple(args.tiers.split(",")) if args.tiers else (Tier.HOT.value, Tier.WARM.value)
    drafts, skipped = build_drafts(
        buyers, tiers=tiers, market=args.market, tone=args.tone,
        free_pack_count=args.free_count,
    )
    print(f"source={args.source} tone={args.tone} tiers={','.join(tiers)}")
    print(f"  drafts   {len(drafts)}")
    print(f"  skipped  {len(skipped)}")
    for s in skipped:
        print(f"    - {s}")
    if args.out:
        paths = write_drafts(drafts, args.out)
        print(f"wrote {len(paths)} review-ready drafts -> {args.out}/ (HUMAN SENDS)")
    else:
        for d in drafts:
            print("\n" + "=" * 60)
            print(d.as_markdown())
    return 0


def _cmd_hunt(args: argparse.Namespace) -> int:
    if len(args.sources) == 1:
        result = hunt(args.sources[0], backend=args.backend)
    else:
        result = hunt_many(args.sources, backend=args.backend, dedup=not args.no_dedup)
    _print_summary(f"source={result.source} backend={args.backend}", result.summary())

    if args.ledger:
        ledger = Ledger(args.ledger)
        merged, stats = ledger.merge(result.leads)
        ledger.save(merged)
        print(stats)
        print(f"wrote ledger -> {args.ledger}")
    if args.csv:
        n = write_csv(result.leads, args.csv, sellable_only=args.sellable_only)
        print(f"wrote {n} rows -> {args.csv}")
    elif args.print_csv:
        sys.stdout.write(to_csv(result.leads, sellable_only=args.sellable_only))
    return 0


def _cmd_ledger(args: argparse.Namespace) -> int:
    leads = Ledger(args.path).load()
    if not leads:
        print(f"ledger {args.path}: empty or not found")
        return 0
    summary = {g.value: 0 for g in Grade}
    for l in leads:
        summary[l.grade] = summary.get(l.grade, 0) + 1
    summary["total"] = len(leads)
    summary["sellable"] = sum(1 for l in leads if l.grade != Grade.REJECT.value)
    _print_summary(f"ledger={args.path}", summary)
    dates = sorted(l.last_seen for l in leads if l.last_seen)
    if dates:
        print(f"  last_seen  {dates[0]} .. {dates[-1]}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="hunter", description="MBM lead-hunting pipeline")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("sources", help="list registered sources")
    sp.set_defaults(func=_cmd_sources)

    hp = sub.add_parser("hunt", help="fetch -> enrich -> grade one or more sources")
    hp.add_argument("sources", nargs="+", help="registered source name(s) (see `sources`)")
    hp.add_argument("--backend", default="auto",
                    choices=["auto", "scrapling", "playwright", "urllib"])
    hp.add_argument("--no-dedup", action="store_true",
                    help="keep duplicates when hunting multiple sources")
    hp.add_argument("--csv", metavar="PATH", help="write LeadPack CSV to PATH")
    hp.add_argument("--print-csv", action="store_true", help="print CSV to stdout")
    hp.add_argument("--sellable-only", action="store_true",
                    help="drop Reject rows from CSV output")
    hp.add_argument("--ledger", metavar="PATH",
                    help="merge results into a persistent ledger CSV at PATH")
    hp.set_defaults(func=_cmd_hunt)

    lp = sub.add_parser("ledger", help="show stats for a ledger CSV")
    lp.add_argument("path", help="ledger CSV path")
    lp.set_defaults(func=_cmd_ledger)

    bp = sub.add_parser("buyers", help="find + rank wholesalers/buyers from a source")
    bp.add_argument("source", help="registered buyer source name")
    bp.add_argument("--backend", default="auto",
                    choices=["auto", "scrapling", "playwright", "urllib"])
    bp.add_argument("--csv", metavar="PATH", help="write ranked buyers CSV to PATH")
    bp.add_argument("--print-csv", action="store_true")
    bp.add_argument("--actionable-only", action="store_true",
                    help="drop No-contact buyers from CSV")
    bp.set_defaults(func=_cmd_buyers)

    op = sub.add_parser("outreach",
                        help="generate review-ready email drafts (never sends)")
    op.add_argument("source", help="registered buyer source name")
    op.add_argument("--backend", default="auto",
                    choices=["auto", "scrapling", "playwright", "urllib"])
    op.add_argument("--market", help="override market in the copy")
    op.add_argument("--tone", default="soft", choices=["soft", "direct"])
    op.add_argument("--tiers", help="comma list, default Hot,Warm")
    op.add_argument("--free-count", type=int, default=50, dest="free_count")
    op.add_argument("--out", metavar="DIR", help="write drafts to DIR (else print)")
    op.set_defaults(func=_cmd_outreach)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
