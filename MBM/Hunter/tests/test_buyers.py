"""Buyer/wholesaler finder tests — parse, dedup, rank. Offline."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from hunter.buyers import (  # noqa: E402
    Buyer, Tier, parse_buyers, rank_buyer, merge_buyers, find_buyers,
)

FIXTURE = pathlib.Path(__file__).resolve().parent.parent / "fixtures" / "sample_wholesalers.html"


def test_parse_reads_buyer_cards():
    buyers = parse_buyers(FIXTURE.read_text(), source="t")
    assert len(buyers) == 5
    rick = next(b for b in buyers if b.company.startswith("Bayline Acquisitions LLC"))
    assert rick.email == "rick@baylineacq.example"
    assert "list_request" in rick.signals


def test_rank_hot_for_list_request_buyer():
    b = Buyer(source="t", company="X", email="x@y.z", phone="1", website="y.z",
              signals=["list_request", "acquiring", "cash_buyer"])
    rank_buyer(b)
    assert b.tier == Tier.HOT.value
    assert b.score >= 70


def test_no_contact_is_not_actionable():
    b = Buyer(source="t", company="Anon", signals=["acquiring"])
    rank_buyer(b)
    assert b.tier == Tier.NO_CONTACT.value
    assert b.score == 0


def test_merge_dedups_by_email_and_unions_signals():
    a = Buyer(source="t", company="Bayline Acquisitions LLC", email="rick@b.example",
              signals=["list_request"])
    b = Buyer(source="t", company="Bayline Acquisitions", email="rick@b.example",
              signals=["high_volume"])
    merged = merge_buyers([a, b])
    assert len(merged) == 1
    assert set(merged[0].signals) == {"list_request", "high_volume"}


def test_find_buyers_end_to_end():
    buyers = find_buyers("fixture-wholesalers", backend="urllib")
    # 5 cards, Bayline duplicate collapses -> 4 unique
    assert len(buyers) == 4
    assert buyers[0].tier == Tier.HOT.value          # ranked best-first
    assert buyers[-1].tier == Tier.NO_CONTACT.value  # Anonymous Flips sinks
    bayline = next(b for b in buyers if b.email == "rick@baylineacq.example")
    assert "high_volume" in bayline.signals           # unioned from the duplicate


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
