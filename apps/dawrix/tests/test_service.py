"""Service-layer tests — subscribe -> schedule -> ops -> done, on a temp DB."""

import datetime as dt
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from dawrix import db as _db  # noqa: E402
from dawrix import service as svc  # noqa: E402


def _conn():
    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
    tmp.close()
    return _db.setup(tmp.name, fresh=True)


def test_reference_data_seeded():
    conn = _conn()
    assert len(svc.list_areas(conn)) == 3
    assert len(svc.list_plans(conn)) == 2
    area = svc.list_areas(conn)[0]
    assert "weekdays_ar" in area and area["weekdays_ar"]


def test_subscribe_creates_and_schedules():
    conn = _conn()
    res = svc.subscribe(conn, name="أحمد", phone="0100", area_id=1, plan_id=1,
                        start=dt.date(2026, 7, 6))
    assert res["first_month_free"] is True
    assert res["billing"][0]["amount_egp"] == 0
    assert res["billing"][1]["amount_egp"] > 0
    assert len(res["next_pickups"]) == svc.INITIAL_PICKUPS
    # scheduled on the area's weekdays (الوراق = Tue/Fri)
    wds = {dt.date.fromisoformat(d).weekday() for d in res["next_pickups"]}
    assert wds <= {1, 4}


def test_duplicate_active_subscription_rejected():
    conn = _conn()
    svc.subscribe(conn, name="أحمد", phone="0100", area_id=1, plan_id=1)
    try:
        svc.subscribe(conn, name="أحمد", phone="0100", area_id=1, plan_id=1)
        assert False, "expected ServiceError"
    except svc.ServiceError:
        pass


def test_missing_name_or_phone_rejected():
    conn = _conn()
    try:
        svc.subscribe(conn, name="", phone="0100", area_id=1, plan_id=1)
        assert False
    except svc.ServiceError:
        pass


def test_bad_area_or_plan_rejected():
    conn = _conn()
    for kw in ({"area_id": 999, "plan_id": 1}, {"area_id": 1, "plan_id": 999}):
        try:
            svc.subscribe(conn, name="س", phone="0" + str(kw["area_id"]), **kw)
            assert False
        except svc.ServiceError:
            pass


def test_ops_flow_mark_done_and_stats():
    conn = _conn()
    start = dt.date(2026, 7, 6)  # Monday
    svc.subscribe(conn, name="أحمد", phone="0100", area_id=1, plan_id=1, start=start)
    # first pickup for الوراق (Tue/Fri) after Mon 7/6 is Tue 7/7
    day = "2026-07-07"
    rows = svc.collections_for_date(conn, day)
    assert len(rows) == 1 and rows[0]["status"] == "scheduled"

    svc.mark_done(conn, rows[0]["id"])
    rows2 = svc.collections_for_date(conn, day)
    assert rows2[0]["status"] == "done"

    st = svc.stats(conn)
    assert st["active_subscriptions"] == 1
    assert st["customers"] == 1
    assert st["mrr_egp"] == 100  # plan 1 price


def test_customer_view():
    conn = _conn()
    svc.subscribe(conn, name="منى", phone="0155", area_id=2, plan_id=2)
    view = svc.customer_view(conn, "0155")
    assert view["customer"]["name"] == "منى"
    assert view["subscription"]["status"] == "active"
    try:
        svc.customer_view(conn, "9999")
        assert False
    except svc.ServiceError:
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
