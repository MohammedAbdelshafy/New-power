#!/usr/bin/env python3
"""
New Power Lead Engine
Usage:
  python leads/run.py --city "Denver" --state CO
  python leads/run.py --city "Atlanta" --state GA --demo
  python leads/run.py --city "Phoenix" --state AZ --count 30 --email client@example.com
"""

import argparse
import sys
import time
import os

# allow running from repo root or from leads/
sys.path.insert(0, os.path.dirname(__file__))

import config
from fetch  import get_leads
from export import to_csv


def fmt_money(n):
    try:
        return f"${int(n):,}"
    except (TypeError, ValueError):
        return "N/A"


def print_table(leads):
    cols = [
        ("Owner",         "owner_name",      26),
        ("Address",       "address",         28),
        ("Status",        "status",          26),
        ("Est. Equity",   "est_equity",      13),
        ("Days Behind",   "days_delinquent",  11),
        ("Phone",         "phone",           16),
    ]
    header = "  ".join(f"{h:<{w}}" for h, _, w in cols)
    sep    = "  ".join("-" * w for _, _, w in cols)
    print(f"\n  {header}")
    print(f"  {sep}")
    for lead in leads:
        row_vals = []
        for _, key, width in cols:
            val = lead.get(key, "")
            if key == "est_equity":
                val = fmt_money(val)
            elif key == "days_delinquent":
                val = str(val)
            row_vals.append(f"{str(val):<{width}}")
        print("  " + "  ".join(row_vals))
    print()


def main():
    parser = argparse.ArgumentParser(description="Pull motivated-seller leads for any US city.")
    parser.add_argument("--city",    required=True,  help='City name, e.g. "Miami"')
    parser.add_argument("--state",   required=True,  help="State abbreviation, e.g. FL")
    parser.add_argument("--count",   type=int, default=20, help="Number of leads (default 20)")
    parser.add_argument("--demo",    action="store_true",
                        help="Demo mode — generate realistic sample data (no API key needed)")
    parser.add_argument("--email",   default="",
                        help="Deliver CSV to this client email address when done")
    parser.add_argument("--no-csv",  action="store_true", help="Skip saving CSV file")
    args = parser.parse_args()

    city  = args.city.strip().title()
    state = args.state.strip().upper()
    demo  = args.demo or not config.ATTOM_API_KEY

    if demo and not args.demo:
        print(f"\n  [!] No ATTOM_API_KEY set — running in demo mode.")
        print(f"      Set ATTOM_API_KEY env var to pull live data.\n")

    mode_label = "DEMO (sample data)" if demo else "LIVE (ATTOM Data)"
    print(f"\n  New Power Lead Engine")
    print(f"  {'─'*40}")
    print(f"  City    : {city}, {state}")
    print(f"  Count   : {args.count} leads")
    print(f"  Mode    : {mode_label}")
    print(f"  {'─'*40}")

    print(f"\n  Pulling leads", end="", flush=True)
    start = time.time()

    for _ in range(3):
        time.sleep(0.4)
        print(".", end="", flush=True)

    leads = get_leads(
        city=city,
        state=state,
        demo=demo,
        api_key=config.ATTOM_API_KEY,
        count=args.count,
    )

    elapsed = time.time() - start
    print(f" done ({elapsed:.1f}s)\n")
    print(f"  Found {len(leads)} motivated-seller leads for {city}, {state}")

    print_table(leads)

    if not args.no_csv:
        csv_path = to_csv(leads, config.OUTPUT_DIR, city, state)
        print(f"  CSV saved: {csv_path}")

        if args.email:
            print(f"  Emailing to {args.email}...", end=" ", flush=True)
            try:
                from mailer import send_leads
                send_leads(
                    csv_path=csv_path,
                    client_email=args.email,
                    smtp_host=config.SMTP_HOST,
                    smtp_port=config.SMTP_PORT,
                    smtp_user=config.SMTP_USER,
                    smtp_pass=config.SMTP_PASS,
                    city=city,
                    state=state,
                )
            except Exception as e:
                print(f"\n  [!] Email failed: {e}")
        print()

    print(f"  Done. {len(leads)} leads ready.\n")
    return leads


if __name__ == "__main__":
    main()
