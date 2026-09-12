# MBM-Wide Scrapling Standard

All scraper-capable workers should use the Scrapling acquisition layer through a stable adapter boundary.

Execution contract:

`approved public source -> Scrapling -> provenance/evidence normalization -> domain QA -> domain ranking -> downstream system`

Scrapling is not a decision engine. The owning system remains authoritative for scoring, CRM, outreach, pricing, approvals, and delivery.

Required controls:

- health check before scheduled production runs;
- dry-run path;
- source URL and extraction provenance on every record;
- explicit blocked/empty/malformed outcomes;
- no fabricated fields or contact data;
- no private/personal contact data in Git;
- adapters isolate Scrapling upgrades from business logic;
- failures remain visible in mission/report state.

This registry entry is the architectural standard. Individual systems adopt it incrementally when they contain scraper-capable collection paths.
