# The MBM Constitution

The invariants of the MBM Operating System. Every worker — human, LLM, IDE agent, or script — operates under these articles. Amendments require a Decision Log entry and a reviewed commit; nothing here changes silently.

## Article 1 — Everything is a Mission
No direct prompting into production work, no isolated workflows, no side quests. Work enters through `MissionControl/Missions/Inbox/` and exits through `Completed/` → `Archive/`. If it wasn't a mission, it didn't happen.

## Article 2 — Git is the single source of truth
All state — missions, leads, events, registry, knowledge — lives as files in this repository. No hidden state: nothing lives only in a chat history, a worker's memory, or an external tool. If a worker knows something the repo doesn't, its next commit fixes that.

## Article 3 — Claim before you execute
A worker claims a mission (`Inbox → Claimed`, owner set, `MissionClaimed` event) before doing any work on it. One owner per mission. Pull before claiming; push the claim immediately; if the push is rejected, someone else owns it — pull and pick another mission. Duplicate execution is a constitutional violation, not an accident.

## Article 4 — Workers communicate through events, never hidden state
Every lifecycle change emits an event to `MBM/EventBus/events.jsonl` (append-only). Workers coordinate by reading missions and events — never by assuming what another worker is doing.

## Article 5 — Humans gate the irreversible
Outreach sends, content publishing, pricing changes >20%, legal/contractual commitments, and deletions of CRM history require explicit human approval. Agents draft; humans release. (Decisions DL-003, DL-004.)

## Article 6 — Extend, never duplicate
Before building anything, search for the existing system that almost does it and extend it. A second CRM, a second mission queue, a second dashboard, or a second event log is rejected on sight. Duplicate systems are killed and merged, not maintained.

## Article 7 — Knowledge capture is mandatory
A mission cannot reach `Completed/` with an empty **Lessons Learned** section. Durable lessons flow to `Knowledge_Base/`, material decisions to `Decision_Log/`, outputs to `Artifacts/` or `CRM/`, repeatable procedures to `Missions/SOPs/`. Nothing valuable is ever lost.

## Article 8 — Workers are plug-and-play
A worker joins the system by adding one registry file (`MBM/Registry/workers/<id>.json`) declaring its skills, cost, speed, confidence, context size, tools, availability, and MCP/git/web support — and by honoring Articles 1–7. No integration code, no special cases. Roles (`MBM/Workers/*.md`) define *what* to do; the registry defines *who* can do it.

## Article 9 — Revenue is the success metric
The system exists to generate revenue: meetings booked, opportunities created, deals won, time saved, reusable capability added. Code volume, mission counts, and activity are not achievements. Every architectural change must increase revenue, automation, knowledge, throughput, reliability, or reusability — and should say which.

## Article 10 — Quality gates are binary
Acceptance criteria are written so a stranger can verify them true/false. A mission whose criteria can't be checked gets its criteria rewritten before work starts. Review (`Review/` state) is a real gate, not a formality — the reviewer is named on the mission and is never its owner.
