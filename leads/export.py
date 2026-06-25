"""Export leads to CSV."""

import csv
import os
from datetime import datetime
from pathlib import Path


COLUMNS = [
    "owner_name", "address", "city", "state", "zip",
    "status", "nod_date", "days_delinquent",
    "est_value", "est_owed", "est_equity",
    "phone", "email", "source",
]

HEADERS = {
    "owner_name":      "Owner Name",
    "address":         "Address",
    "city":            "City",
    "state":           "State",
    "zip":             "ZIP",
    "status":          "Status",
    "nod_date":        "NOD / Filing Date",
    "days_delinquent": "Days Delinquent",
    "est_value":       "Est. Value ($)",
    "est_owed":        "Est. Owed ($)",
    "est_equity":      "Est. Equity ($)",
    "phone":           "Phone",
    "email":           "Email",
    "source":          "Data Source",
}


def to_csv(leads: list[dict], output_dir: str, city: str, state: str) -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_city = city.replace(" ", "_").replace(",", "")
    filename = os.path.join(output_dir, f"leads_{safe_city}_{state}_{stamp}.csv")

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writerow(HEADERS)
        for lead in leads:
            row = dict(lead)
            for field in ("est_value", "est_owed", "est_equity"):
                if row.get(field):
                    row[field] = f"{int(row[field]):,}"
            writer.writerow(row)

    return filename
