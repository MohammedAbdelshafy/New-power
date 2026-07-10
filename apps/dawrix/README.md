# Dawrix — داوريكس لخدمات النظافة

A running, free, zero-dependency reference implementation of the Dawrix cleaning &
waste-collection app: **subscriptions, collection scheduling, and an ops dashboard**,
Arabic-first (RTL), priced in EGP with the flyer's *first-month-free* offer.

## Purpose
Give Dawrix a real, testable app that runs today at **$0** — no cloud accounts, no
npm install — while mapping cleanly onto the Supabase/Cloudflare migration plan. The
domain and service layers are storage-agnostic, so "move to Postgres" is a swap of
`db.py`, not a rewrite.

## Architecture
```
web/ (Arabic RTL PWA)  ──fetch──►  dawrix/server.py (stdlib http.server)
                                      │
                          dawrix/service.py  (business operations)
                             │                    │
                   dawrix/domain.py         dawrix/db.py (SQLite)
              (pure: billing, scheduling)   (schema + seed)
```
- **domain.py** — pure functions: `invoice_amount` (first-month-free), `billing_schedule`, `next_pickup_dates`.
- **service.py** — `subscribe`, `customer_view`, `collections_for_date`, `mark_done`, `stats`.
- **server.py** — JSON API under `/api/*` + serves the PWA. One SQLite connection per request.
- **web/** — vanilla RTL SPA (subscribe · my account · ops dashboard) + service worker for offline shell.

## Setup
```bash
cd apps/dawrix
./run.sh                     # → http://127.0.0.1:8080   (Python 3.9+, nothing to install)
```

## Configuration (env vars)
| Var | Default | Purpose |
|---|---|---|
| `DAWRIX_PORT` | `8080` | HTTP port |
| `DAWRIX_HOST` | `127.0.0.1` | bind host |
| `DAWRIX_DB` | `apps/dawrix/dawrix.sqlite3` | SQLite file path |
| `DAWRIX_VERBOSE` | unset | enable request logging |

## Usage
- **اشترك الآن** — name, phone, area, plan → confirms with first-month-free billing + next pickups.
- **حسابي** — enter phone → your subscription and upcoming collections.
- **لوحة التشغيل** — daily collection list; **تم الجمع** marks a pickup done; live KPI tiles (active subs, today's pickups, MRR).

Seeded areas: الوراق (Tue/Fri), إمبابة (Mon/Thu), المنيرة الغربية (Wed/Sat). Plans: 100 & 160 EGP/mo.

### API
`GET /api/plans` · `GET /api/areas` · `GET /api/stats` · `GET /api/me?phone=` ·
`GET /api/collections?date=YYYY-MM-DD` · `POST /api/subscribe` ·
`POST /api/collections/{id}/done`

## Tests
```bash
python3 tests/test_domain.py     # billing + scheduling (7)
python3 tests/test_service.py    # subscribe→schedule→ops→done on a temp DB (7)
```
All 14 pass offline. The full HTTP flow is verified end-to-end (see commit notes).

## Troubleshooting
- **Port in use** → set `DAWRIX_PORT`. **Fresh data** → delete the `DAWRIX_DB` file (re-seeds on boot).
- **Arabic looks LTR** → ensure the page is served by `server.py` (the shell sets `dir="rtl"`).

## Future improvements
- Swap `db.py` for Supabase Postgres + RLS (per `MBM/README` → Dawrix infra plan).
- Phone-OTP auth; WhatsApp reminders via n8n; Paymob/Fawry EGP payments.
- Crew app with route/ETA; before/after photos to R2; recurring auto-scheduling job.
