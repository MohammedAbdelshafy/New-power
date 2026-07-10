"""SQLite schema, connection, and seed data for Dawrix.

One file, no ORM. The schema mirrors the domain: areas → plans → customers →
subscriptions → collections. SQLite because it needs zero setup and runs free
anywhere; the migration plan swaps this for Supabase Postgres later without the API
or domain code changing (both talk to the small data-access helpers below).
"""

from __future__ import annotations

import datetime as _dt
import os
import sqlite3

DEFAULT_DB = os.environ.get("DAWRIX_DB", os.path.join(os.path.dirname(__file__), "..", "dawrix.sqlite3"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS areas (
  id INTEGER PRIMARY KEY,
  name_ar TEXT NOT NULL,
  collection_weekdays TEXT NOT NULL   -- comma list of weekday ints (Mon=0..Sun=6)
);
CREATE TABLE IF NOT EXISTS plans (
  id INTEGER PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,
  name_ar TEXT NOT NULL,
  price_egp INTEGER NOT NULL,
  pickups_per_week INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS customers (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  phone TEXT UNIQUE NOT NULL,
  area_id INTEGER NOT NULL REFERENCES areas(id),
  address TEXT DEFAULT '',
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS subscriptions (
  id INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customers(id),
  plan_id INTEGER NOT NULL REFERENCES plans(id),
  status TEXT NOT NULL DEFAULT 'active',   -- active | paused | cancelled
  start_date TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS collections (
  id INTEGER PRIMARY KEY,
  subscription_id INTEGER NOT NULL REFERENCES subscriptions(id),
  scheduled_date TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'scheduled', -- scheduled | done | missed
  done_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_collections_date ON collections(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_subs_customer ON subscriptions(customer_id);
"""

SEED_AREAS = [
    (1, "الوراق", "1,4"),      # Tue & Fri
    (2, "إمبابة", "0,3"),      # Mon & Thu
    (3, "المنيرة الغربية", "2,5"),  # Wed & Sat
]
SEED_PLANS = [
    ("waste_basic", "جمع المخلفات — أساسي", 100, 2),
    ("waste_plus", "جمع المخلفات + تنظيف السلالم", 160, 2),
]


def connect(path: str = DEFAULT_DB) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def seed(conn: sqlite3.Connection) -> None:
    """Insert reference data (areas, plans) if absent. Idempotent."""
    cur = conn.cursor()
    for aid, name, wd in SEED_AREAS:
        cur.execute("INSERT OR IGNORE INTO areas(id, name_ar, collection_weekdays) VALUES (?,?,?)",
                    (aid, name, wd))
    for code, name, price, ppw in SEED_PLANS:
        cur.execute(
            "INSERT OR IGNORE INTO plans(code, name_ar, price_egp, pickups_per_week) VALUES (?,?,?,?)",
            (code, name, price, ppw))
    conn.commit()


def setup(path: str = DEFAULT_DB, *, fresh: bool = False) -> sqlite3.Connection:
    if fresh and os.path.exists(path):
        os.remove(path)
    conn = connect(path)
    init_db(conn)
    seed(conn)
    return conn


def area_weekdays(row_value: str) -> list[int]:
    return [int(x) for x in row_value.split(",") if x.strip() != ""]


def now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
