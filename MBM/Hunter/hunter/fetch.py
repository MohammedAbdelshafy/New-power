"""Fetch backends, in order of preference, each optional.

    scrapling  ->  playwright  ->  urllib (stdlib)

The pipeline asks for HTML; this module gets it with the best backend available.
Nothing here is a hard dependency: with none of the optional libs installed, static
pages still load via urllib, and local fixtures load directly. This is the seam where
the Tier-1/Tier-2 web-agent tooling from the registry plugs in.
"""

from __future__ import annotations

import os
import pathlib
import urllib.request

DEFAULT_UA = "MBM-Hunter/0.1 (+https://github.com/mohammedabdelshafy/New-power)"


class FetchError(RuntimeError):
    pass


def _read_local(path: str) -> str:
    return pathlib.Path(path).read_text(encoding="utf-8")


def _fetch_scrapling(url: str, render: bool) -> str:
    # Scrapling: adaptive/resilient scraping. StealthyFetcher renders JS via a
    # headless browser; Fetcher is a fast static GET.
    from scrapling.fetchers import Fetcher, StealthyFetcher  # type: ignore

    if render:
        page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
    else:
        page = Fetcher.get(url, stealthy_headers=True)
    return page.html_content


def _fetch_playwright(url: str, render: bool) -> str:
    from playwright.sync_api import sync_playwright  # type: ignore

    exe = os.environ.get("PLAYWRIGHT_CHROMIUM_PATH")  # optional explicit path
    with sync_playwright() as p:
        launch_kwargs = {"headless": True}
        if exe:
            launch_kwargs["executable_path"] = exe
        browser = p.chromium.launch(**launch_kwargs)
        try:
            page = browser.new_page(user_agent=DEFAULT_UA)
            page.goto(url, wait_until="networkidle" if render else "load", timeout=30000)
            return page.content()
        finally:
            browser.close()


def _fetch_urllib(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": DEFAULT_UA})
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 (trusted, configured sources)
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def fetch_html(url: str, *, render: bool = False, backend: str = "auto") -> str:
    """Return the HTML at `url`.

    - Local paths and `file://` URLs are read directly (offline-safe).
    - `render=True` requests JS execution (needs scrapling or playwright).
    - `backend` is "auto" (try best available) or one of "scrapling"/"playwright"/"urllib".
    """
    if url.startswith("file://"):
        return _read_local(url[len("file://"):])
    if not url.startswith(("http://", "https://")):
        # treat as a local filesystem path
        return _read_local(url)

    order = {
        "auto": ["scrapling", "playwright", "urllib"],
        "scrapling": ["scrapling"],
        "playwright": ["playwright"],
        "urllib": ["urllib"],
    }.get(backend)
    if order is None:
        raise FetchError(f"unknown backend {backend!r}")

    errors: list[str] = []
    for name in order:
        try:
            if name == "scrapling":
                return _fetch_scrapling(url, render)
            if name == "playwright":
                return _fetch_playwright(url, render)
            if name == "urllib":
                if render:
                    raise FetchError("urllib cannot render JS; install scrapling or playwright")
                return _fetch_urllib(url)
        except ImportError:
            errors.append(f"{name}: not installed")
        except Exception as exc:  # noqa: BLE001 - surface a combined diagnostic
            errors.append(f"{name}: {type(exc).__name__}: {exc}")

    raise FetchError(f"all backends failed for {url}\n  " + "\n  ".join(errors))
