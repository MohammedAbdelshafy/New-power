"""End-to-end pipeline tests against the offline fixture (no network, no keys)."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from hunter.parse import parse_listings  # noqa: E402
from hunter.pipeline import hunt, hunt_many, to_csv  # noqa: E402
from hunter.models import Grade, CSV_COLUMNS  # noqa: E402

FIXTURE = pathlib.Path(__file__).resolve().parent.parent / "fixtures" / "sample_listings.html"


def test_parse_extracts_all_listings():
    leads = parse_listings(FIXTURE.read_text(), source="t")
    assert len(leads) == 5
    dolores = next(l for l in leads if l.owner_name == "Dolores Vance")
    assert dolores.parcel_id == "APN-11-223-004"
    assert dolores.zip_code == "33607"
    assert "pre_foreclosure" in dolores.signals
    assert "absentee_owner" in dolores.signals


def test_hunt_fixture_grades_and_sorts():
    result = hunt("fixture-county", backend="urllib")
    summary = result.summary()
    assert summary["total"] == 5
    # one record has no owner/contact -> Reject
    assert summary["Reject"] == 1
    assert summary["sellable"] == 4
    # sorted best-first: first sellable lead is the highest grade
    assert result.leads[0].grade == Grade.PLATINUM.value
    # Reject sinks to the bottom
    assert result.leads[-1].grade == Grade.REJECT.value


def test_enrichment_upgrades_absentee_owner():
    # Estate of R. Okafor mails to a law office, not the property -> absentee_owner
    # is derived at enrich time and lifts the lead from Gold to Platinum.
    result = hunt("fixture-county", backend="urllib")
    okafor = next(l for l in result.leads if l.owner_name.startswith("Estate"))
    assert "absentee_owner" in okafor.signals
    assert okafor.grade == Grade.PLATINUM.value


def test_multi_source_hunt_dedups_and_unions():
    result = hunt_many(["fixture-county", "fixture-marketplace"], backend="urllib")
    parcels = [l.parcel_id for l in result.leads]
    # Theo appears twice in the marketplace feed + Dolores overlaps county -> all collapse
    assert parcels.count("APN-66-540-118") == 1
    assert parcels.count("APN-11-223-004") == 1
    assert len(result.leads) == 6
    # Dolores's marketplace-only 'liens' signal is unioned into the county record
    dolores = next(l for l in result.leads if l.parcel_id == "APN-11-223-004")
    assert "liens" in dolores.signals


def test_csv_shape_and_sellable_filter():
    result = hunt("fixture-county", backend="urllib")
    full = to_csv(result.leads).strip().splitlines()
    assert full[0] == ",".join(CSV_COLUMNS)
    assert len(full) - 1 == 5  # header + 5 rows

    sellable = to_csv(result.leads, sellable_only=True).strip().splitlines()
    assert len(sellable) - 1 == 4  # Reject dropped


if __name__ == "__main__":
    import traceback
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception:  # noqa: BLE001
                failures += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    raise SystemExit(1 if failures else 0)
