"""Dedup tests — merge by key, union signals, backfill contacts. Offline."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from hunter.models import Lead  # noqa: E402
from hunter.dedup import merge_leads  # noqa: E402


def test_merge_same_parcel_unions_signals_and_backfills():
    a = Lead(source="county", parcel_id="P1", owner_name="Jane",
             property_address="1 A St", zip_code="33607", phone="555-0100",
             signals=["pre_foreclosure"])
    b = Lead(source="market", parcel_id="P1", owner_name="Jane",
             property_address="1 A St", zip_code="33607", email="j@x.com",
             signals=["liens", "vacant"])
    merged = merge_leads([a, b])
    assert len(merged) == 1
    lead = merged[0]
    # richer record (b, 2 signals) becomes primary but keeps first-seen source
    assert lead.source == "county"
    assert set(lead.signals) == {"pre_foreclosure", "liens", "vacant"}
    assert lead.phone == "555-0100"  # backfilled from a
    assert lead.email == "j@x.com"   # from b


def test_addr_key_when_no_parcel():
    a = Lead(source="s", owner_name="Sam", property_address="9 B Rd", zip_code="1",
             signals=["vacant"])
    b = Lead(source="s", owner_name="Sam", property_address="9 B Rd", zip_code="1",
             signals=["vacant"])
    assert len(merge_leads([a, b])) == 1


def test_distinct_leads_not_merged():
    a = Lead(source="s", parcel_id="P1", signals=[])
    b = Lead(source="s", parcel_id="P2", signals=[])
    assert len(merge_leads([a, b])) == 2


def test_merge_preserves_first_seen_order():
    a = Lead(source="s", parcel_id="P1")
    b = Lead(source="s", parcel_id="P2")
    c = Lead(source="s", parcel_id="P1", signals=["vacant"])  # dup of a, richer
    merged = merge_leads([a, b, c])
    assert [l.parcel_id for l in merged] == ["P1", "P2"]


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
