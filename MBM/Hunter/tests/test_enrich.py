"""Enrichment tests — absentee detection, normalization, signal dedup. Offline."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from hunter.models import Lead  # noqa: E402
from hunter.enrich import is_absentee, enrich_lead  # noqa: E402


def test_absentee_when_mailing_differs():
    assert is_absentee("418 Marigold Ln", "PO Box 771, Sarasota FL 34230") is True


def test_owner_occupied_when_mailing_matches_property():
    assert is_absentee("9 Kestrel Ct", "9 Kestrel Ct, Tampa FL 33612") is False


def test_absentee_inconclusive_when_mailing_blank():
    assert is_absentee("9 Kestrel Ct", "") is False


def test_enrich_adds_absentee_and_normalizes():
    lead = Lead(source="t", owner_name="X", property_address="1200 Bayshore Blvd Unit 5",
                city="Tampa", state="fl ", zip_code=" 33606 ",
                mailing_address="c/o Law Office, 55 Main St, Tampa FL 33602",
                signals=["probate"])
    enrich_lead(lead)
    assert "absentee_owner" in lead.signals
    assert lead.state == "FL"
    assert lead.zip_code == "33606"


def test_enrich_is_idempotent_and_dedupes_signals():
    lead = Lead(source="t", property_address="1 A St", mailing_address="",
                signals=["vacant", "vacant", "liens"])
    enrich_lead(lead)
    enrich_lead(lead)  # second pass must not duplicate
    assert lead.signals == ["vacant", "liens"]


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
