# SOP — Knowledge Capture (Article 7)

Runs at every mission completion. The CLI enforces step 1 mechanically; the reviewer enforces the rest. Nothing valuable is ever lost.

On `mission complete <id>`, verify each destination:

| What the mission produced | Where it must land |
|---|---|
| Lessons (what worked / didn't / next worker should know) | Mission's **## Lessons Learned** (CLI blocks completion if empty) → auto-mirrored to `Knowledge_Base/LESSONS.md` |
| Deliverables | `Artifacts/` or `CRM/`, and listed in the mission's `artifacts:` field |
| A decision with consequences (pricing, architecture, channel kill) | `Decision_Log/DECISIONS.md` — one dated paragraph with alternatives rejected |
| A repeated pattern (3+ occurrences: objection, winning angle, dead source) | A playbook file in `Knowledge_Base/` |
| A repeatable procedure | A new/updated SOP in `Missions/SOPs/` |
| A new reusable capability | A skill: `.claude/skills/` wrapper + the canonical SOP in the role file, so every agent inherits it |
| Anything that changes worker fitness (a worker excelled/failed at a skill) | Registry `confidence`/`notes` correction, done by CRO at weekly review |

Checklist the reviewer answers before archiving (all yes/no):
1. Lessons Learned filled with content a stranger could act on?
2. Every path in `outputs:` exists and is listed in `artifacts:`?
3. Any decision made → logged? Any pattern seen 3+ times → playbook?
4. Could any part of this mission be templated? If yes, file a P2 mission to template it.
