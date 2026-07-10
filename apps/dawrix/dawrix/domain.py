"""Dawrix core domain logic — pure functions, no I/O.

Two things the business runs on, kept transparent and testable:

  1. Billing — the "first month free, then monthly EGP" offer from the flyer.
  2. Scheduling — turning a subscription into concrete collection dates for an area.

All money is integer EGP piastres? No — whole EGP is enough here; amounts are ints.
All dates are datetime.date; nothing here touches the DB or the clock except where a
`today`/`start` is passed in, so every function is deterministic and unit-testable.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass

# Egyptian week: collection days are expressed as weekday ints (Mon=0 .. Sun=6),
# matching date.weekday().
WEEKDAY_AR = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]


@dataclass(frozen=True)
class Plan:
    code: str
    name_ar: str
    price_egp: int           # monthly price after the free month
    pickups_per_week: int     # collection frequency


def invoice_amount(plan_price: int, month_index: int, *, first_month_free: bool = True) -> int:
    """EGP owed for a subscription's Nth month (month_index starts at 1).

    The flyer offer: month 1 free, month 2+ at plan price. `month_index` < 1 is invalid.
    """
    if month_index < 1:
        raise ValueError("month_index starts at 1")
    if first_month_free and month_index == 1:
        return 0
    return plan_price


def billing_schedule(plan_price: int, start: _dt.date, months: int,
                     *, first_month_free: bool = True) -> list[tuple[_dt.date, int]]:
    """Return [(due_date, amount_egp)] for `months` billing cycles from `start`.

    Due dates advance one calendar month at a time (day clamped to end-of-month).
    """
    if months < 1:
        raise ValueError("months must be >= 1")
    out: list[tuple[_dt.date, int]] = []
    for i in range(months):
        due = _add_months(start, i)
        amount = invoice_amount(plan_price, i + 1, first_month_free=first_month_free)
        out.append((due, amount))
    return out


def next_pickup_dates(start: _dt.date, collection_weekdays: list[int], count: int) -> list[_dt.date]:
    """The next `count` pickup dates on or after `start` for the given weekdays.

    `collection_weekdays` is the area's fixed pickup days (e.g. [1, 4] = Tue & Fri).
    Dates come back sorted ascending with no duplicates.
    """
    if count < 1:
        raise ValueError("count must be >= 1")
    if not collection_weekdays:
        raise ValueError("area has no collection days configured")
    days = sorted(set(w % 7 for w in collection_weekdays))
    out: list[_dt.date] = []
    d = start
    # scan forward day by day; bounded by count * 7 iterations worst case
    while len(out) < count:
        if d.weekday() in days:
            out.append(d)
        d = d + _dt.timedelta(days=1)
    return out


def _add_months(d: _dt.date, n: int) -> _dt.date:
    """Add n months to a date, clamping the day to the target month's length."""
    month_index = d.month - 1 + n
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    # clamp day
    day = min(d.day, _days_in_month(year, month))
    return _dt.date(year, month, day)


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        nxt = _dt.date(year + 1, 1, 1)
    else:
        nxt = _dt.date(year, month + 1, 1)
    return (nxt - _dt.date(year, month, 1)).days
