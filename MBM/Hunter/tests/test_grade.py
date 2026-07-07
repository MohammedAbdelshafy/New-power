"""Grading rubric tests — pure, offline, no dependencies."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from hunter.models import Lead, Grade  # noqa: E402
from hunter.grade import grade_lead, score_lead  # noqa: E402


def _base(**kw) -> Lead:
    defaults = dict(
        source="t", owner_name="Jane Doe", property_address="1 Main St",
        city="Tampa", state="FL", zip_code="33607",
    )
    defaults.update(kw)
    return Lead(**defaults)


def test_platinum_high_motivation_and_contactable():
    lead = _base(
        phone="813-555-0100", email="j@example.com",
        mailing_address="PO Box 1",
        signals=["pre_foreclosure", "tax_delinquent", "high_equity"],
    )
    grade_lead(lead)
    assert lead.grade == Grade.PLATINUM.value
    assert lead.score >= 80


def test_bronze_low_motivation():
    lead = _base(signals=["liens"])  # 10 + owner(5) = 15
    grade_lead(lead)
    assert lead.grade == Grade.BRONZE.value
    assert lead.score < 30


def test_reject_without_contact_path():
    lead = Lead(source="t", property_address="1 Main St", city="Tampa",
                zip_code="33607", signals=["pre_foreclosure"])
    grade_lead(lead)
    assert lead.grade == Grade.REJECT.value
    assert lead.score == 0
    assert not Grade.REJECT.is_sellable


def test_reject_without_location():
    lead = Lead(source="t", owner_name="Jane", phone="813-555-0100",
                signals=["pre_foreclosure"])
    grade_lead(lead)
    assert lead.grade == Grade.REJECT.value


def test_score_is_pure_and_explained():
    lead = _base(signals=["vacant"])  # 20 + owner(5)
    score, reasons = score_lead(lead)
    assert score == 25
    assert any("vacant" in r for r in reasons)
    # score_lead must not mutate
    assert lead.score == 0 and lead.grade == ""


def test_unknown_signal_ignored():
    lead = _base(signals=["not_a_real_signal"])
    grade_lead(lead)
    # only owner-name contact point (5) counts -> Bronze
    assert lead.score == 5
    assert lead.grade == Grade.BRONZE.value


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
