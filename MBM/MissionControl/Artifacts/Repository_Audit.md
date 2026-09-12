# Repository Audit — 2026-07-04 (M-011)

Scope: every file in `mohammedabdelshafy/new-power`. Method: full tree walk, placeholder/TODO scan, workflow inspection, lifecycle execution test (smoke suite).

## Findings & dispositions

| # | Finding | Class | Disposition |
|---|---|---|---|
| 1 | `pages.yml` deployed the **entire repo** to GitHub Pages — future CRM lead PII, missions, and the event log would have shipped publicly | security / P0 | **FIXED** — artifact now contains only `index.html`, `platform.html`, `MBM/Dashboard/` |
| 2 | `route` parser broke on inline YAML comments (template-created missions were unroutable) | bug | **FIXED** — caught by new smoke suite |
| 3 | Lessons-Learned completion guard was bypassable via the template's long placeholder text | bug | **FIXED** — caught by new smoke suite |
| 4 | `/mbm-lead-hunt` skill still instructed the v1 claim-less flow (`start` straight from Inbox — rejected by v2 CLI) | stale doc | **FIXED** |
| 5 | No repo-level `CLAUDE.md` — agents entered without constitution/lifecycle context | missing doc | **FIXED** — added |
| 6 | No tests anywhere | missing tests | **FIXED** — `scripts/smoke-test.sh`, 26 checks, green |
| 7 | `.claude/settings.json` hooks point to `/root/.claude/cost-guardrails/*` which don't exist in fresh containers → hook errors every session | debt | **DEFERRED** (issue) — settings.json is agent-self-config; founder should apply the `[ -x … ] && … \|\| true` guard manually |
| 8 | Cost-guardrails toolkit (`install.sh`, 5 scripts, `templates/`) is an unrelated product living in this repo (repo does 3 jobs: OS + ZWM site + guardrails) | debt | **DEFERRED** (issue) — extract to its own repo |
| 9 | `scripts/notify.sh` (Telegram/Discord) not wired to the event bus — blocked/escalated missions don't ping anyone | gap | **DEFERRED** (issue) — highest-value small automation |
| 10 | `jarvis` and `nvidia-local` registry entries are `offline` — registered but no runner exists | unused registry | **DEFERRED** (issues) — roadmap v2.1; honest availability flags prevent routing to them |
| 11 | External Google Fonts on `index.html`/`platform.html`/ZWM pages — render dependency on third party | minor | noted; acceptable for marketing pages |
| 12 | **MBM-Social clipping pipeline: 0 files exist.** No source intake, factories, ranking, publishing, analytics, or learning code anywhere in the tree or git history | missing product | **Missions M-008–M-010 filed**; see `Clipping_Pipeline_Audit.md` |

## Duplicate systems check
None found. v2 explicitly merged the duplicate-risk requests (Sales Agent, Revenue Dashboard, "Factories") into existing namespaces via DL-008. `templates/claude-settings.json` is an installer template, not a duplicate of `.claude/settings.json`.

## Dead code check
No unreachable scripts. `scripts/update-budget.sh` is manual-invocation only (documented behavior). All 7 skills, all 9 role files, all 9 registry entries, and every CLI subcommand are referenced and exercised.

## Broken references check
All internal doc links resolve. All CLI paths resolve. Smoke suite exercises every mission-state transition plus CRM commands: 26/26 pass.
