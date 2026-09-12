---
name: mbm-revenue-review
description: Run the MBM Chief Revenue Officer weekly review — funnel metrics, THE bottleneck, pricing observations, next week's top-3 missions. Use weekly (Sunday) or when asked for pipeline/revenue status.
---

You are now executing the **Chief Revenue Officer** worker's Weekly Revenue Review SOP.

1. Read `MBM/Workers/01-chief-revenue-officer.md` and follow its SOP exactly.
2. `bash scripts/mbm.sh metrics`, read `MBM/Dashboard/metrics.json`, review leads changed in the last 7 days via git log.
3. Write the review to `MBM/MissionControl/Artifacts/revenue-reviews/YYYY-MM-DD-review.md`: numbers vs last week, wins/losses, **ONE named bottleneck**, pricing/offer observations, decisions (mirror material ones to the Decision Log), next week's top-3.
4. File those top-3 missions in Inbox (`bash scripts/mbm.sh mission new ...`) with binary success criteria. Triage the rest of Inbox.
5. Complete the review mission, file next Sunday's recurring copy, commit. Give the human the bottleneck + top-3 in your reply.
