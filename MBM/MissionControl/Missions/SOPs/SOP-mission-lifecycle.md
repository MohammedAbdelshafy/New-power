# SOP — Mission Lifecycle

The one procedure every worker follows. CLI: `scripts/mbm.sh` (all commands emit events automatically).

```
Inbox ──claim──▶ Claimed ──start──▶ InProgress ──review──▶ Review ──complete──▶ Completed ──archive──▶ Archive
                    │                   │                                          
                    └───────block───────┴──▶ Blocked ──unblock──▶ Claimed          failed ──▶ Archive (status: failed)
```

## 1. Claim (Article 3 — prevents duplicate execution)
```bash
git pull                                  # ALWAYS pull first
bash scripts/mbm.sh mission claim M-012 <your-registry-id>
git add -A && git commit -m "claim M-012" && git push   # push IMMEDIATELY
```
If the push is rejected: `git pull` — if the mission is no longer in Inbox, someone else owns it. Pick another. Never force-push a claim.

Before claiming, check: dependencies all Completed? Your registry entry has the `required_skills`? If routing suggested you (`mbm.sh route M-012`), you're eligible.

## 2. Start
`bash scripts/mbm.sh mission start M-012` — moves Claimed → InProgress. Load the role file (`MBM/Workers/<role>.md`), the mission, and `Knowledge_Base/offer.md`. Follow the role SOP. Log notable deviations in the mission's `## Log`.

## 3. Blocked?
`bash scripts/mbm.sh mission block M-012 "waiting on founder pricing sign-off"` — moves to Blocked with the reason logged and `MissionBlocked` emitted. Unblock with `mission unblock M-012` when cleared. A mission blocked > 7 days gets escalated by the CRO (`MissionEscalated`).

## 4. Review
Write outputs to the paths in `outputs:`, list them in `artifacts:`, fill **Lessons Learned**, then `mission review M-012`. The named `reviewer` (never the owner) checks every acceptance criterion — binary pass/fail.

## 5. Complete
Reviewer runs `bash scripts/mbm.sh mission complete M-012`. The CLI **refuses** if Lessons Learned is empty (Article 7) and mirrors the lessons to `Knowledge_Base/LESSONS.md`. Then follow `SOP-knowledge-capture.md`.

## 6. Archive
Completed missions older than 30 days (or immediately, once knowledge capture is verified): `mission archive M-012`. Failed missions: `mission fail M-012 "reason"` → status `failed`, moved to Archive, `MissionFailed` emitted — failures are knowledge too.
