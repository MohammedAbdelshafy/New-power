# Workers — Roles & Protocol

A worker file here is a **role**: identity, standing responsibilities, SOP, output contract, and handoffs. *Who* executes a role is a separate question answered by `MBM/Registry/` (executors) and `scripts/mbm.sh route` (matching). Any registered executor — Claude, Fabel, ChatGPT, Jarvis, Antigravity, OpenCode, local models, scripts, humans — runs a role the same way:

1. **Load context:** read the worker file, `Knowledge_Base/offer.md`, and the mission being executed.
2. **Follow the SOP.** Deviations that matter get logged in the mission's `## Log`.
3. **Write outputs exactly where the contract says** (paths + schema). Other workers depend on those locations.
4. **Hand off:** if the SOP says the output triggers another worker, file a mission in `Missions/Inbox/` addressed to that worker.
5. **Never invent facts.** Anything customer-facing must trace to a source recorded in `CRM/intel/`.

## Roster

| File | Worker | One-line job |
|---|---|---|
| `01-chief-revenue-officer.md` | CRO | Owns the number. Strategy, pricing, pipeline, weekly review, bottleneck analysis |
| `02-lead-hunter.md` | Lead Hunter | Finds and scores prospects from public sources → structured lead records |
| `03-company-researcher.md` | Company Researcher | Deep intel on a lead before any outreach |
| `04-outreach-agent.md` | Outreach Agent | Personalized cold email / LinkedIn / follow-up drafts that never sound AI-written |
| `05-content-engine.md` | Content Engine | Turns every project and insight into publishable marketing content |
| `06-proposal-generator.md` | Proposal Generator | Proposal + scope + ROI + pricing options within 24h of a meeting |
| `07-followup-manager.md` | Follow-up Manager | No lead ever goes cold by accident; tracks replies/objections/next actions |
| `08-crm-brain.md` | CRM Brain | Data integrity of `CRM/`; the memory every other worker relies on |
| `09-marketing-agent.md` | Marketing Agent | Channels, distribution, campaigns, inbound — makes content travel |

## The 10 revenue workers — where each lives

| Requested worker | Implementation (Article 6: extend, don't duplicate) |
|---|---|
| Chief Revenue Officer | `01-chief-revenue-officer.md` |
| Lead Hunter | `02-lead-hunter.md` |
| Company Researcher | `03-company-researcher.md` |
| Marketing Agent | `09-marketing-agent.md` |
| Sales Agent | `04-outreach-agent.md` (drafting) + `human-founder` (sending/closing, Article 5) — one funnel, two hands |
| Proposal Generator | `06-proposal-generator.md` |
| CRM Brain | `08-crm-brain.md` |
| Content Engine | `05-content-engine.md` |
| Follow-up Manager | `07-followup-manager.md` |
| Revenue Dashboard | `Dashboard/` + the `mbm-scripts` registry worker (role `revenue-dashboard`, deterministic — refreshed via `mbm.sh metrics`) |

## The pipeline they form

```
Lead Hunter → CRM Brain → Company Researcher → Outreach Agent → Follow-up Manager
                                                      │               │
                                                   (meeting)       (reply/objection)
                                                      ▼               │
                                              Proposal Generator ◄────┘
                                                      ▼
                                                 (won/lost) → Content Engine (case study)
                                                      ▲
                                    CRO reviews everything weekly, reprices, reprioritizes
```
