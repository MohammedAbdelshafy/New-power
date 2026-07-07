# MBM Registry — Workers

Canonical capability registry for the MBM fleet (referenced by
`jarvis-mbm/Agents/ROSTER.md` and `jarvis-mbm/AGENTS.md`). Content lives here to avoid
duplication (Constitution Article 6); the ops repo points at it.

## Contents

| File | What |
|---|---|
| `web-agent-tools.md` | The 15 external agent/web-automation frameworks: role, owner, pipeline stage, adoption gate. |
| `LICENSE-NOTES.md` | Commercial-use license ledger. **Source of truth** for what may touch a revenue path. |

## How registration works

1. A tool is **registered** here (cataloged, licensed, assigned an owner + adoption gate).
2. It stays inert until its **Backlog trigger** fires (see the adoption-gates table).
3. Wiring lands as runnable code in `MBM/Hunter/` (or the relevant lane) and the
   registry `Status` line is updated with the date.

Registered ≠ adopted. The only tools wired today are Tier-1 (Playwright, Scrapling, MCP),
proven by the running `MBM/Hunter/` stack.
