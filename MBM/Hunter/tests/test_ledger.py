"""Ledger tests — persistence, dedup across runs, first/last-seen dates. Offline."""

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from hunter.models import Lead  # noqa: E402
from hunter.ledger import Ledger  # noqa: E402


def _lead(parcel, signals=None):
    return Lead(source="s", parcel_id=parcel, owner_name="O",
                property_address="1 A St", zip_code="1", phone="555",
                signals=signals or [])


def test_first_run_stamps_dates_and_counts_new():
    with tempfile.TemporaryDirectory() as d:
        path = str(pathlib.Path(d) / "master.csv")
        led = Ledger(path)
        merged, stats = led.merge([_lead("P1"), _lead("P2")], today="2026-07-01")
        led.save(merged)
        assert stats.new == 2 and stats.updated == 0 and stats.total == 2
        for l in merged:
            assert l.first_seen == "2026-07-01" and l.last_seen == "2026-07-01"


def test_second_run_preserves_first_seen_and_updates_last_seen():
    with tempfile.TemporaryDirectory() as d:
        path = str(pathlib.Path(d) / "master.csv")
        led = Ledger(path)
        led.save(led.merge([_lead("P1")], today="2026-07-01")[0])

        merged, stats = led.merge(
            [_lead("P1", ["vacant"]), _lead("P9")], today="2026-07-09")
        led.save(merged)
        assert stats.new == 1 and stats.updated == 1 and stats.total == 2

        p1 = next(l for l in merged if l.parcel_id == "P1")
        assert p1.first_seen == "2026-07-01"   # preserved
        assert p1.last_seen == "2026-07-09"    # advanced
        assert "vacant" in p1.signals          # new signal unioned in
        p9 = next(l for l in merged if l.parcel_id == "P9")
        assert p9.first_seen == "2026-07-09"


def test_roundtrip_reload_preserves_fields():
    with tempfile.TemporaryDirectory() as d:
        path = str(pathlib.Path(d) / "master.csv")
        led = Ledger(path)
        merged, _ = led.merge([_lead("P1", ["pre_foreclosure"])], today="2026-07-01")
        led.save(merged)
        reloaded = Ledger(path).load()
        assert len(reloaded) == 1
        assert reloaded[0].parcel_id == "P1"
        assert "pre_foreclosure" in reloaded[0].signals
        assert reloaded[0].first_seen == "2026-07-01"


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
