#!/usr/bin/env python3
"""
Daily pipeline runner — configured per client.
Called by cron or GitHub Actions at 7 AM in client's timezone.

Usage:
  python leads/pipeline.py --client clients/johnson_realty.json
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import config
from fetch  import get_leads
from export import to_csv
from mailer import send_leads


def load_client(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def run_for_client(client: dict):
    city  = client["city"]
    state = client["state"]
    email = client["email"]
    count = client.get("leads_per_day", 20)

    print(f"  Running pipeline for {client['name']} — {city}, {state}")

    leads = get_leads(
        city=city,
        state=state,
        demo=False,
        api_key=config.ATTOM_API_KEY,
        count=count,
    )
    print(f"  Fetched {len(leads)} leads")

    csv_path = to_csv(leads, config.OUTPUT_DIR, city, state)
    print(f"  Exported: {csv_path}")

    send_leads(
        csv_path=csv_path,
        client_email=email,
        smtp_host=config.SMTP_HOST,
        smtp_port=config.SMTP_PORT,
        smtp_user=config.SMTP_USER,
        smtp_pass=config.SMTP_PASS,
        city=city,
        state=state,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=True, help="Path to client JSON file")
    args = parser.parse_args()

    client = load_client(args.client)
    run_for_client(client)
    print("  Pipeline complete.\n")


if __name__ == "__main__":
    main()
