# Event Bus (Article 4)

`events.jsonl` is the append-only communication medium between workers. No hidden state: if a worker wants others to know something happened, it emits an event; if a worker wants to know what happened, it reads events. Being a file in git, the bus is readable and writable by every worker — cloud agents, local IDE agents, scripts, humans — and its history is tamper-evident.

## Record format
One JSON object per line:
```json
{"ts": "2026-07-04T12:00:00+00:00", "event": "MissionClaimed", "mission": "M-007", "actor": "fabel", "note": ""}
```

## Event vocabulary

| Event | Emitted by | Meaning |
|---|---|---|
| `MissionCreated` | `mbm.sh mission new` | New mission in Inbox |
| `MissionClaimed` | `mbm.sh mission claim` | Worker took ownership (duplicate-execution guard) |
| `MissionStarted` | `mbm.sh mission start` | Execution began |
| `MissionBlocked` / `MissionUnblocked` | `mbm.sh mission block/unblock` | Stuck / cleared (reason in note) |
| `MissionReviewed` | `mbm.sh mission review` | Handed to the reviewer |
| `MissionCompleted` | `mbm.sh mission complete` | Accepted; lessons captured |
| `MissionFailed` | `mbm.sh mission fail` | Terminal failure (reason in note) |
| `MissionArchived` | `mbm.sh mission archive` | Moved to terminal storage |
| `MissionEscalated` | `mbm.sh mission escalate` | Needs CRO/human attention (e.g. blocked > 7 days) |

New event types may be added; the vocabulary above is the minimum every worker must understand. Emit custom events with `mbm.sh emit <Event> <mission> <actor> [note]`.

## Rules
- **Append-only.** Never edit or delete lines. Corrections are new events.
- Lifecycle events come from the CLI, not hand-written — the CLI keeps mission state and events consistent.
- The routing engine reads this file for per-worker performance (completions vs failures), so accurate actor attribution matters: set `MBM_WORKER=<registry-id>` in your environment.
- Read the bus: `bash scripts/mbm.sh events 20`.
