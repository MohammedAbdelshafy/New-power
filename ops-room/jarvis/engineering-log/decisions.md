# JARVIS OPS — Engineering Decision Log

All significant architecture decisions, changes, and rationale are logged here.

---

## 2026-06-27 — Master Operations Room v1.0

**Decision**: Build `ops-room/` as a top-level directory in the New Power repo rather than a separate repo.

**Rationale**: Single repo means every session that clones `mohammedabdelshafy/new-power` automatically has access to the full JARVIS OPS brain, all scripts, and the operations pipeline. No dependency fetching, no separate clone step.

**Trade-off**: ops-room files ship with the repo. Acceptable because they contain no secrets and the repo is the owner's personal workspace.

**Files introduced**:
- `ops-room/CLAUDE.md` — JARVIS OPS identity and protocols
- `ops-room/jarvis/ops-center.py` — live operations dashboard
- `ops-room/jarvis/project-intel.json` — project intelligence state
- `ops-room/intelligence/analyze-content.py` — content reverse-engineering engine
- `ops-room/intelligence/extract-techniques.py` — technique extractor
- `ops-room/sources/find-repos.sh` — GitHub + GitLab search
- `ops-room/sources/clone-and-map.sh` — repo feature mapping
- `ops-room/sources/doppler-sync.sh` — secrets management bridge
- `ops-room/enhancer/read-session.sh` — session reader
- `ops-room/enhancer/patch-session.sh` — session patcher
- `ops-room/dashboard/status.py` — CLI dashboard
- `ops-room/dashboard/index.html` — visual dashboard

**Owner approved**: Yes (session inception).

---

## 2026-06-27 — JARVIS OPS Identity Layer

**Decision**: Adopt JARVIS OPS persona as the authoritative identity for all sessions operating from this repo.

**Rationale**: The owner requires a named, consistent engineering agent persona that operates with:
- A defined permission model (approval gates for destructive actions)
- Continuous project awareness (not just reactive assistance)
- Structured reporting
- AI research capability

**Trade-off**: More structured than a general-purpose assistant. Some responses will follow the report template format even for small tasks.

**Protocols added**:
- Approval gate (7 high-impact action categories require explicit "approved" before execution)
- End-of-task report format (summary, files changed, commands, tests, blockers, priorities)
- Engineering protocol: Inspect → Plan → Implement → Test → Verify → Report
- Research protocol: discoveries logged in `jarvis/research/discoveries.json`

**Owner approved**: Yes.
