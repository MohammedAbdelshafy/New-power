"""Domain logic tests — billing + scheduling. Pure, offline, no DB."""

import datetime as dt
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from dawrix.domain import (  # noqa: E402
    invoice_amount, billing_schedule, next_pickup_dates,
)


def test_first_month_free_then_charged():
    assert invoice_amount(100, 1) == 0
    assert invoice_amount(100, 2) == 100
    assert invoice_amount(100, 6) == 100


def test_first_month_free_can_be_disabled():
    assert invoice_amount(100, 1, first_month_free=False) == 100


def test_invoice_month_index_must_be_positive():
    try:
        invoice_amount(100, 0)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_billing_schedule_shape_and_month_rollover():
    sched = billing_schedule(100, dt.date(2026, 1, 31), 3)
    assert [a for _, a in sched] == [0, 100, 100]
    # anchored on the 31st: Feb clamps to 28, Mar returns to 31
    assert [d.isoformat() for d, _ in sched] == ["2026-01-31", "2026-02-28", "2026-03-31"]


def test_next_pickups_land_on_area_weekdays():
    # Tue(1) & Fri(4), starting Mon 2026-07-06
    picks = next_pickup_dates(dt.date(2026, 7, 6), [1, 4], 4)
    assert [d.weekday() for d in picks] == [1, 4, 1, 4]
    assert picks == [dt.date(2026, 7, 7), dt.date(2026, 7, 10),
                     dt.date(2026, 7, 14), dt.date(2026, 7, 17)]
    assert picks == sorted(picks)


def test_next_pickups_includes_start_if_it_matches():
    picks = next_pickup_dates(dt.date(2026, 7, 7), [1], 2)  # start is a Tuesday
    assert picks[0] == dt.date(2026, 7, 7)


def test_next_pickups_requires_days_and_count():
    for bad in (lambda: next_pickup_dates(dt.date(2026, 7, 7), [], 3),
                lambda: next_pickup_dates(dt.date(2026, 7, 7), [1], 0)):
        try:
            bad()
            assert False, "expected ValueError"
        except ValueError:
            pass


if __name__ == "__main__":
    import traceback
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print(f"PASS {name}")
            except Exception:
                failures += 1; print(f"FAIL {name}"); traceback.print_exc()
    raise SystemExit(1 if failures else 0)
