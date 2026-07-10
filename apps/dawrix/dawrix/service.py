"""Service layer — business operations over the DB, using the pure domain logic.

The API and any future front end call these; they never touch SQL directly. This is
the seam the migration plan swaps to Supabase behind (same function signatures).
"""

from __future__ import annotations

import datetime as _dt
import sqlite3

from . import db as _db
from .domain import next_pickup_dates, billing_schedule, WEEKDAY_AR

# How many pickups to pre-schedule when someone subscribes.
INITIAL_PICKUPS = 8


class ServiceError(Exception):
    """Expected, user-facing error (bad input, conflict). Maps to HTTP 400/409."""


def list_plans(conn: sqlite3.Connection) -> list[dict]:
    return [dict(r) for r in conn.execute(
        "SELECT id, code, name_ar, price_egp, pickups_per_week FROM plans ORDER BY price_egp")]


def list_areas(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT id, name_ar, collection_weekdays FROM areas ORDER BY name_ar")
    out = []
    for r in rows:
        wd = _db.area_weekdays(r["collection_weekdays"])
        out.append({"id": r["id"], "name_ar": r["name_ar"], "weekdays": wd,
                    "weekdays_ar": [WEEKDAY_AR[w] for w in wd]})
    return out


def subscribe(conn: sqlite3.Connection, *, name: str, phone: str, area_id: int,
              plan_id: int, start: _dt.date | None = None) -> dict:
    """Create (or reuse) a customer, open a subscription, pre-schedule pickups.

    Returns a summary including the first-month-free billing line and next pickups.
    Raises ServiceError on bad input or a duplicate active subscription.
    """
    name = (name or "").strip()
    phone = (phone or "").strip()
    if not name or not phone:
        raise ServiceError("الاسم ورقم الهاتف مطلوبان")  # name and phone required
    area = conn.execute("SELECT * FROM areas WHERE id=?", (area_id,)).fetchone()
    if not area:
        raise ServiceError("المنطقة غير موجودة")  # area not found
    plan = conn.execute("SELECT * FROM plans WHERE id=?", (plan_id,)).fetchone()
    if not plan:
        raise ServiceError("الباقة غير موجودة")  # plan not found

    start = start or _dt.date.today()
    cur = conn.cursor()

    # reuse a customer by phone, else create
    row = cur.execute("SELECT * FROM customers WHERE phone=?", (phone,)).fetchone()
    if row:
        customer_id = row["id"]
    else:
        cur.execute("INSERT INTO customers(name, phone, area_id, created_at) VALUES (?,?,?,?)",
                    (name, phone, area_id, _db.now_iso()))
        customer_id = cur.lastrowid

    # one active subscription per customer
    active = cur.execute(
        "SELECT id FROM subscriptions WHERE customer_id=? AND status='active'",
        (customer_id,)).fetchone()
    if active:
        raise ServiceError("لديك اشتراك نشط بالفعل")  # you already have an active subscription

    cur.execute(
        "INSERT INTO subscriptions(customer_id, plan_id, status, start_date, created_at) "
        "VALUES (?,?,'active',?,?)",
        (customer_id, plan_id, start.isoformat(), _db.now_iso()))
    sub_id = cur.lastrowid

    weekdays = _db.area_weekdays(area["collection_weekdays"])
    pickups = next_pickup_dates(start, weekdays, INITIAL_PICKUPS)
    cur.executemany(
        "INSERT INTO collections(subscription_id, scheduled_date, status) VALUES (?,?, 'scheduled')",
        [(sub_id, d.isoformat()) for d in pickups])
    conn.commit()

    bills = billing_schedule(plan["price_egp"], start, 3)
    return {
        "subscription_id": sub_id,
        "customer": {"id": customer_id, "name": name, "phone": phone},
        "plan": {"name_ar": plan["name_ar"], "price_egp": plan["price_egp"]},
        "first_month_free": True,
        "billing": [{"due": d.isoformat(), "amount_egp": a} for d, a in bills],
        "next_pickups": [d.isoformat() for d in pickups],
    }


def customer_view(conn: sqlite3.Connection, phone: str) -> dict:
    """A customer's current subscription and upcoming pickups, by phone."""
    cust = conn.execute("SELECT * FROM customers WHERE phone=?", ((phone or "").strip(),)).fetchone()
    if not cust:
        raise ServiceError("لا يوجد عميل بهذا الرقم")  # no customer with this number
    sub = conn.execute(
        "SELECT s.*, p.name_ar AS plan_name, p.price_egp FROM subscriptions s "
        "JOIN plans p ON p.id=s.plan_id WHERE s.customer_id=? ORDER BY s.id DESC LIMIT 1",
        (cust["id"],)).fetchone()
    upcoming = []
    if sub:
        upcoming = [r["scheduled_date"] for r in conn.execute(
            "SELECT scheduled_date FROM collections WHERE subscription_id=? AND status='scheduled' "
            "AND scheduled_date >= ? ORDER BY scheduled_date LIMIT 4",
            (sub["id"], _dt.date.today().isoformat()))]
    return {
        "customer": {"name": cust["name"], "phone": cust["phone"]},
        "subscription": None if not sub else {
            "id": sub["id"], "status": sub["status"], "plan_name": sub["plan_name"],
            "price_egp": sub["price_egp"], "start_date": sub["start_date"],
        },
        "next_pickups": upcoming,
    }


def collections_for_date(conn: sqlite3.Connection, date: str) -> list[dict]:
    """Ops view: every collection scheduled on `date` (ISO), with customer + area."""
    rows = conn.execute(
        "SELECT c.id, c.scheduled_date, c.status, cu.name AS customer, cu.phone, "
        "a.name_ar AS area FROM collections c "
        "JOIN subscriptions s ON s.id=c.subscription_id "
        "JOIN customers cu ON cu.id=s.customer_id "
        "JOIN areas a ON a.id=cu.area_id "
        "WHERE c.scheduled_date=? ORDER BY a.name_ar, cu.name", (date,))
    return [dict(r) for r in rows]


def mark_done(conn: sqlite3.Connection, collection_id: int) -> dict:
    row = conn.execute("SELECT * FROM collections WHERE id=?", (collection_id,)).fetchone()
    if not row:
        raise ServiceError("عملية الجمع غير موجودة")  # collection not found
    conn.execute("UPDATE collections SET status='done', done_at=? WHERE id=?",
                 (_db.now_iso(), collection_id))
    conn.commit()
    return {"id": collection_id, "status": "done"}


def stats(conn: sqlite3.Connection) -> dict:
    today = _dt.date.today().isoformat()
    q = conn.execute
    return {
        "active_subscriptions": q("SELECT COUNT(*) c FROM subscriptions WHERE status='active'").fetchone()["c"],
        "customers": q("SELECT COUNT(*) c FROM customers").fetchone()["c"],
        "collections_today": q("SELECT COUNT(*) c FROM collections WHERE scheduled_date=?", (today,)).fetchone()["c"],
        "done_today": q("SELECT COUNT(*) c FROM collections WHERE scheduled_date=? AND status='done'", (today,)).fetchone()["c"],
        "mrr_egp": q("SELECT COALESCE(SUM(p.price_egp),0) s FROM subscriptions su JOIN plans p ON p.id=su.plan_id WHERE su.status='active'").fetchone()["s"],
    }
