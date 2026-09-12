# Changelog

## v1.0.0 — 2026-07-04

Architecture v1 frozen; production release system established.

- MBM Revenue Engine: Mission Control, 9 revenue roles, file-based CRM, dashboard, CLI
- Mission System v2: Constitution, 7-state claim lifecycle, schema v2, SOP library
- Event bus (append-only JSONL) + worker registry (9 executors) + intelligent routing
- Enforced knowledge capture (completion blocked on empty Lessons Learned)
- Production readiness (M-011): repo audit fixes, Architecture_v1.md freeze,
  smoke/regression suite (26 checks), release/rollback/deployment process
