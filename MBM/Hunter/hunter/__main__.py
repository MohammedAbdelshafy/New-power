"""CLI entry point:  python -m hunter <command>

    python -m hunter sources                 list registered sources
    python -m hunter hunt fixture-county      run pipeline, print grade summary
    python -m hunter hunt fixture-county --csv out.csv --sellable-only
    python -m hunter hunt fixture-county --backend playwright   force a fetch backend
"""

from __future__ import annotations

import argparse
import sys

from .pipeline import hunt, write_csv, to_csv
from .sources import list_sources


def _cmd_sources(_args: argparse.Namespace) -> int:
    for s in list_sources():
        kind = "live" if s.live else "fixture"
        render = " render" if s.render else ""
        print(f"{s.name:24} [{kind}{render}] {s.location}")
        if s.notes:
            print(f"{'':24} {s.notes}")
    return 0


def _cmd_hunt(args: argparse.Namespace) -> int:
    result = hunt(args.source, backend=args.backend)
    summary = result.summary()
    print(f"source={result.source} backend={args.backend}")
    for key in ("Platinum", "Gold", "Silver", "Bronze", "Reject", "total", "sellable"):
        print(f"  {key:9} {summary.get(key, 0)}")

    if args.csv:
        n = write_csv(result.leads, args.csv, sellable_only=args.sellable_only)
        print(f"wrote {n} rows -> {args.csv}")
    elif args.print_csv:
        sys.stdout.write(to_csv(result.leads, sellable_only=args.sellable_only))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="hunter", description="MBM lead-hunting pipeline")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("sources", help="list registered sources")
    sp.set_defaults(func=_cmd_sources)

    hp = sub.add_parser("hunt", help="fetch -> parse -> grade a source")
    hp.add_argument("source", help="registered source name (see `sources`)")
    hp.add_argument("--backend", default="auto",
                    choices=["auto", "scrapling", "playwright", "urllib"])
    hp.add_argument("--csv", metavar="PATH", help="write LeadPack CSV to PATH")
    hp.add_argument("--print-csv", action="store_true", help="print CSV to stdout")
    hp.add_argument("--sellable-only", action="store_true",
                    help="drop Reject rows from CSV output")
    hp.set_defaults(func=_cmd_hunt)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
