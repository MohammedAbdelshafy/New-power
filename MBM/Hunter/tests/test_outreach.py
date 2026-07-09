"""Outreach draft tests — content, guards, tone. No mail is ever sent. Offline."""

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from hunter.buyers import Buyer, Tier, rank_all  # noqa: E402
from hunter.outreach import build_draft, build_drafts, write_drafts, OutreachError  # noqa: E402


def _buyer(**kw) -> Buyer:
    d = dict(source="t", company="Acme", name="Rick Alvarez", market="Tampa FL",
             email="rick@acme.example", contact_reason="You asked for Tampa lists.",
             signals=["list_request"], tier=Tier.HOT.value)
    d.update(kw)
    return Buyer(**d)


def test_soft_draft_has_offer_and_meet_and_footer():
    d = build_draft(_buyer(), meet_link="https://meet.example/mbm")
    assert "first 50 records free" in d.subject.lower() or "free" in d.subject.lower()
    assert "https://meet.example/mbm" in d.body
    assert "Google Meet" in d.body
    assert "unsubscribe" in d.body.lower()      # CAN-SPAM opt-out
    assert d.to_email == "rick@acme.example"


def test_direct_tone_pushes_meet():
    d = build_draft(_buyer(), tone="direct", meet_link="https://meet.example/mbm")
    assert "Meet" in d.subject or "meet" in d.body.lower()
    assert "this week" in d.body.lower()


def test_refuses_when_reason_slot_unfillable():
    # no contact_reason AND no signals -> nothing to personalize -> refuse
    b = _buyer(contact_reason="", signals=[])
    try:
        build_draft(b)
        assert False, "expected OutreachError"
    except OutreachError:
        pass


def test_refuses_without_email():
    try:
        build_draft(_buyer(email=""))
        assert False, "expected OutreachError"
    except OutreachError:
        pass


def test_build_drafts_filters_by_tier_and_writes_files():
    buyers = rank_all([
        _buyer(email="a@x.example"),                                   # Hot
        _buyer(company="Cold Co", email="c@x.example", signals=["cash_buyer"]),  # lower
        Buyer(source="t", company="NoReach", signals=["acquiring"]),   # No-contact
    ])
    drafts, skipped = build_drafts(buyers, meet_link="https://m.example")
    assert len(drafts) >= 1
    # the no-contact buyer must never get a draft
    assert all("NoReach" not in d.to_name for d in drafts)
    with tempfile.TemporaryDirectory() as out:
        paths = write_drafts(drafts, out)
        assert len(paths) == len(drafts)
        assert pathlib.Path(paths[0]).read_text().startswith("To: ")


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
