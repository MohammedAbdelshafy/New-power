# ARCHITECTURE_UPDATE — MBM-Social within Architecture v1 (ADR DL-010)

**This is an addition inside the frozen architecture, not a change to it.** Filed as ADR DL-010 in `MBM/MissionControl/Decision_Log/DECISIONS.md`.

| Requested concept | Resolution (Article 6 — reuse, don't duplicate) |
|---|---|
| Queue manager | **Not built.** Mission Control Inbox is the queue; jobs are missions; claim = dequeue |
| Retry system | **Not built.** Stages are restartable (skip-if-done + `--force`); a failed mission is re-claimed. `StageFailed` events carry the error |
| Error logging | Event bus (`StageFailed`, `ClipRejected`) + per-job `state.json` — no separate log system |
| Metrics | Per-stage wall/RSS in `state.json`; funnel metrics stay in `mbm.sh metrics` |
| Workflow automation | `run.py` sequences ONE job; cross-job orchestration stays with Mission Control |
| Asset manager | Job directories + CRM content ledger (`MBM/CRM/content/clips/`) |
| Prompt library | `MBM-Social/prompts/` (first entry: hook-prompt.md) |
| Dashboard / analytics | Post-v1 page reusing `MBM/Dashboard` patterns; data already lands in CRM ledger |
| Publishing | Human-gated (Article 5) — packages prepared, person posts. No platform API keys in v1 |

## Data flow
`jobs/<id>/job.json` → stage artifacts in the same dir (source.mp4, transcript.json, hooks.json, selected.json, clips/, clips_captioned/, covers/, publish/) → ledger mirrored to `MBM/CRM/content/clips/<id>-ledger.json` → events on `MBM/EventBus/events.jsonl` throughout.

## Boundaries kept
No new framework, no daemon, no broker, no DB. The pipeline is 8 small modules + a 50-line runner; every piece is replaceable without touching the OS. GPU is an optimization (issue #8), not a dependency.
