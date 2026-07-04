# Working in this repository

This repo hosts the **MBM Operating System** (multi-agent revenue platform) plus the Zero Waste Misr public site. Before doing anything:

1. Read `MBM/CONSTITUTION.md` — its 10 articles bind every agent. The load-bearing three: everything is a mission, git is the single source of truth, claim before you execute.
2. `MBM/Architecture_v1.md` is the frozen architecture. Do not add frameworks, orchestration layers, or duplicate systems (Article 6). Architecture changes require an ADR entry in `MBM/MissionControl/Decision_Log/DECISIONS.md`.
3. Set `export MBM_WORKER=<your-registry-id>` (see `MBM/Registry/workers/`) so events attribute correctly. Claude Code sessions: use `fabel` or `claude`.
4. All work flows through missions: `bash scripts/mbm.sh status`, then `mission claim <id> <worker>` → commit+push the claim → `mission start` → execute per the role file in `MBM/Workers/` → `mission review`. Lifecycle details: `MBM/MissionControl/Missions/SOPs/SOP-mission-lifecycle.md`.
5. Humans send outreach, publish content, and approve pricing (Article 5). Agents draft.
6. After CRM changes: `bash scripts/mbm.sh validate && bash scripts/mbm.sh metrics`.
7. Before release-tagged commits: `bash scripts/smoke-test.sh` must pass (see `Release/RELEASE_CHECKLIST.md`).

Skills: `/mbm-lead-hunt`, `/mbm-research`, `/mbm-outreach`, `/mbm-content`, `/mbm-proposal`, `/mbm-followup`, `/mbm-revenue-review`.
