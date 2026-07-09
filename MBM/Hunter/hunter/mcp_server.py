"""MCP server exposing the Hunter as callable tools.

This is the `modelcontextprotocol` wire-in from the registry: instead of every agent
importing Python, they speak MCP and call the same three tools. Run it over stdio:

    python -m hunter.mcp_server        # requires the `mcp` SDK: pip install "mcp[cli]"

Tools:
    list_sources()                     -> registered sources
    hunt(source, backend="auto")       -> grade summary + sellable leads (JSON)
    grade(lead_fields...)              -> score + grade for an ad-hoc record

The import of the SDK is deferred so the rest of the package (and its tests) never
depend on `mcp` being installed.
"""

from __future__ import annotations

from dataclasses import asdict

from .grade import grade_lead
from .models import Lead
from .pipeline import hunt as run_hunt, hunt_many as run_hunt_many
from .sources import list_sources as _list_sources


def build_server():
    try:
        from mcp.server.fastmcp import FastMCP  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise SystemExit(
            "The MCP SDK is not installed. Install it with:\n"
            '    pip install "mcp[cli]"\n'
            "then rerun `python -m hunter.mcp_server`."
        ) from exc

    server = FastMCP("mbm-hunter")

    @server.tool()
    def list_sources() -> list[dict]:
        """List registered lead sources the hunter can pull from."""
        return [asdict(s) for s in _list_sources()]

    @server.tool()
    def hunt(source: str, backend: str = "auto") -> dict:
        """Fetch, parse, enrich, and grade one source. Returns summary + sellable leads."""
        result = run_hunt(source, backend=backend)
        return {
            "source": result.source,
            "summary": result.summary(),
            "sellable_leads": [l.to_row() for l in result.sellable],
        }

    @server.tool()
    def hunt_many(sources: list[str], backend: str = "auto", dedup: bool = True) -> dict:
        """Hunt several sources and combine them, deduplicated by default."""
        result = run_hunt_many(sources, backend=backend, dedup=dedup)
        return {
            "source": result.source,
            "summary": result.summary(),
            "sellable_leads": [l.to_row() for l in result.sellable],
        }

    @server.tool()
    def grade(
        source: str = "adhoc",
        owner_name: str = "",
        property_address: str = "",
        city: str = "",
        state: str = "",
        zip_code: str = "",
        mailing_address: str = "",
        phone: str = "",
        email: str = "",
        property_type: str = "",
        signals: list[str] | None = None,
    ) -> dict:
        """Score and grade a single ad-hoc lead record (Platinum..Reject)."""
        lead = Lead(
            source=source, owner_name=owner_name, property_address=property_address,
            city=city, state=state, zip_code=zip_code, mailing_address=mailing_address,
            phone=phone, email=email, property_type=property_type,
            signals=signals or [],
        )
        grade_lead(lead)
        return lead.to_row()

    return server


def main() -> None:
    build_server().run()


if __name__ == "__main__":
    main()
