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
from .sources import list_sources
from .ledger import Ledger
from .models import Grade

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
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
