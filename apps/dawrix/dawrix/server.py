"""Dawrix HTTP server — stdlib only (http.server), no framework, no install.

Serves the JSON API under /api/* and the Arabic RTL PWA from web/. Runs free
anywhere Python does. Each request gets its own SQLite connection (SQLite handles
this fine at this scale); the migration plan swaps the service layer for Supabase
without touching this file's routing.

    python -m dawrix.server            # http://127.0.0.1:8080
    DAWRIX_PORT=9000 python -m dawrix.server
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from . import db as _db
from . import service as svc

WEB_DIR = os.path.join(os.path.dirname(__file__), "..", "web")
_CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8", ".webmanifest": "application/manifest+json",
    ".json": "application/json; charset=utf-8", ".svg": "image/svg+xml",
}


class Handler(BaseHTTPRequestHandler):
    server_version = "Dawrix/0.1"

    # --- helpers -----------------------------------------------------------
    def _send_json(self, obj, status: int = 200) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            raise svc.ServiceError("طلب غير صالح")  # invalid request body

    def log_message(self, *args) -> None:  # quieter logs
        if os.environ.get("DAWRIX_VERBOSE"):
            super().log_message(*args)

    # --- routing -----------------------------------------------------------
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path, query = parsed.path, parse_qs(parsed.query)
        if path.startswith("/api/"):
            return self._api_get(path, query)
        return self._serve_static(path)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if not path.startswith("/api/"):
            return self._send_json({"error": "not found"}, 404)
        conn = _db.connect()
        try:
            if path == "/api/subscribe":
                data = self._read_json()
                res = svc.subscribe(
                    conn, name=data.get("name", ""), phone=data.get("phone", ""),
                    area_id=int(data.get("area_id", 0)), plan_id=int(data.get("plan_id", 0)))
                return self._send_json(res, 201)
            m = re.fullmatch(r"/api/collections/(\d+)/done", path)
            if m:
                return self._send_json(svc.mark_done(conn, int(m.group(1))))
            return self._send_json({"error": "not found"}, 404)
        except svc.ServiceError as e:
            return self._send_json({"error": str(e)}, 400)
        except (ValueError, KeyError, TypeError):
            return self._send_json({"error": "طلب غير صالح"}, 400)
        finally:
            conn.close()

    def _api_get(self, path: str, query: dict) -> None:
        conn = _db.connect()
        try:
            if path == "/api/plans":
                return self._send_json(svc.list_plans(conn))
            if path == "/api/areas":
                return self._send_json(svc.list_areas(conn))
            if path == "/api/stats":
                return self._send_json(svc.stats(conn))
            if path == "/api/me":
                phone = (query.get("phone") or [""])[0]
                return self._send_json(svc.customer_view(conn, phone))
            if path == "/api/collections":
                date = (query.get("date") or [_dt.date.today().isoformat()])[0]
                return self._send_json(svc.collections_for_date(conn, date))
            return self._send_json({"error": "not found"}, 404)
        except svc.ServiceError as e:
            return self._send_json({"error": str(e)}, 404)
        finally:
            conn.close()

    def _serve_static(self, path: str) -> None:
        rel = "index.html" if path in ("/", "") else path.lstrip("/")
        # prevent path traversal
        full = os.path.normpath(os.path.join(WEB_DIR, rel))
        if not full.startswith(os.path.normpath(WEB_DIR)) or not os.path.isfile(full):
            self.send_error(404, "Not Found")
            return
        ext = os.path.splitext(full)[1]
        with open(full, "rb") as fh:
            body = fh.read()
        self.send_response(200)
        self.send_header("Content-Type", _CONTENT_TYPES.get(ext, "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    _db.setup()  # ensure schema + seed
    port = int(os.environ.get("DAWRIX_PORT", "8080"))
    host = os.environ.get("DAWRIX_HOST", "127.0.0.1")
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"Dawrix running → http://{host}:{port}  (Ctrl-C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()


if __name__ == "__main__":
    main()
