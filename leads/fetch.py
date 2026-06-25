"""
Fetch motivated-seller leads from ATTOM Data API.
Falls back to realistic sample data in --demo mode.
"""

import os
import time
import random
import requests
from datetime import datetime, timedelta


ATTOM_BASE = "https://api.gateway.attomdata.com/propertyapi/v1.0.0"

SAMPLE_FIRST = ["James", "Maria", "Robert", "Patricia", "Michael", "Linda",
                "William", "Barbara", "David", "Susan", "Richard", "Jessica",
                "Joseph", "Karen", "Thomas", "Sarah", "Charles", "Nancy"]
SAMPLE_LAST  = ["Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
                "Davis", "Wilson", "Anderson", "Taylor", "Thomas", "Jackson",
                "White", "Harris", "Martin", "Thompson", "Moore", "Young"]
STREET_NAMES = ["Oak", "Maple", "Cedar", "Pine", "Elm", "Lake", "River",
                "Hill", "Park", "Forest", "Sunset", "Valley", "Ridge", "Spring"]
STREET_TYPES = ["Ave", "St", "Blvd", "Dr", "Ln", "Ct", "Way", "Pl"]
STATUSES     = ["Pre-Foreclosure (NOD)", "Pre-Foreclosure (LIS)",
                "Auction Scheduled", "REO / Bank-Owned", "Distressed Sale"]
AREA_CODES   = ["305", "786", "954", "561", "407", "321", "727", "813",
                "904", "941", "239", "386", "352"]


def _fake_phone(area_code):
    return f"({area_code}) {random.randint(200,999)}-{random.randint(1000,9999)}"


def _fake_email(first, last):
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"]
    sep = random.choice([".", "_", ""])
    tag = random.choice(["", str(random.randint(1, 99))])
    return f"{first.lower()}{sep}{last.lower()}{tag}@{random.choice(domains)}"


def generate_sample_leads(city: str, state: str, count: int = 15) -> list[dict]:
    """Generate realistic-looking demo leads for a given city."""
    area_code = random.choice(AREA_CODES)
    leads = []
    base_zip = random.randint(30000, 99000)

    for i in range(count):
        first = random.choice(SAMPLE_FIRST)
        last  = random.choice(SAMPLE_LAST)
        num   = random.randint(100, 9999)
        street = f"{random.choice(STREET_NAMES)} {random.choice(STREET_TYPES)}"
        zipcode = str(base_zip + random.randint(0, 50)).zfill(5)
        est_value = random.randint(180_000, 850_000)
        owed = int(est_value * random.uniform(0.55, 0.92))
        equity = est_value - owed
        days_delinquent = random.randint(30, 420)
        nod_date = (datetime.today() - timedelta(days=days_delinquent)).strftime("%Y-%m-%d")

        leads.append({
            "owner_name":    f"{first} {last}",
            "address":       f"{num} {street}",
            "city":          city,
            "state":         state,
            "zip":           zipcode,
            "status":        random.choice(STATUSES),
            "nod_date":      nod_date,
            "days_delinquent": days_delinquent,
            "est_value":     est_value,
            "est_owed":      owed,
            "est_equity":    equity,
            "phone":         _fake_phone(area_code),
            "email":         _fake_email(first, last),
            "source":        "Sample (Demo Mode)",
        })

    leads.sort(key=lambda x: x["days_delinquent"], reverse=True)
    return leads


def fetch_attom_leads(city: str, state: str, api_key: str, count: int = 25) -> list[dict]:
    """Fetch real pre-foreclosure/distressed leads from ATTOM Data API."""
    headers = {
        "apikey": api_key,
        "accept": "application/json",
    }

    params = {
        "geoid":      f"CI{city.replace(' ', '').upper()}{state.upper()}",
        "pagesize":   count,
        "page":       1,
    }

    try:
        resp = requests.get(
            f"{ATTOM_BASE}/saleshistory/foreclosure",
            headers=headers,
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.HTTPError as e:
        raise RuntimeError(f"ATTOM API error {e.response.status_code}: {e.response.text[:200]}")
    except requests.RequestException as e:
        raise RuntimeError(f"Network error: {e}")

    properties = data.get("property", [])
    leads = []

    for prop in properties:
        addr  = prop.get("address", {})
        owner = prop.get("assessment", {}).get("owner", {})
        sale  = prop.get("sale", {})
        fc    = prop.get("foreclosure", {})

        first = owner.get("owner1firstname", "")
        last  = owner.get("owner1lastname", "")
        full_name = f"{first} {last}".strip() or "Unknown"

        leads.append({
            "owner_name":      full_name,
            "address":         addr.get("line1", ""),
            "city":            addr.get("locality", city),
            "state":           addr.get("countrySubd", state),
            "zip":             addr.get("postal1", ""),
            "status":          fc.get("fipsstatedescription", "Pre-Foreclosure"),
            "nod_date":        fc.get("recordingdate", ""),
            "days_delinquent": fc.get("defaultamount", 0),
            "est_value":       prop.get("assessment", {}).get("market", {}).get("mktttlvalue", 0),
            "est_owed":        sale.get("amount", {}).get("saleamt", 0),
            "est_equity":      0,
            "phone":           "",  # enriched separately
            "email":           "",  # enriched separately
            "source":          "ATTOM Data",
        })

        # compute equity
        if leads[-1]["est_value"] and leads[-1]["est_owed"]:
            leads[-1]["est_equity"] = leads[-1]["est_value"] - leads[-1]["est_owed"]

    return leads


def get_leads(city: str, state: str, demo: bool = False,
              api_key: str = "", count: int = 20) -> list[dict]:
    if demo or not api_key:
        return generate_sample_leads(city, state, count)
    return fetch_attom_leads(city, state, api_key, count)
