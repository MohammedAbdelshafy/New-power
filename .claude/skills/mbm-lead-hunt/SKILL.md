---
name: mbm-lead-hunt
description: Run the MBM Lead Hunter worker — discover and score B2B prospects from public sources into CRM/leads/. Use when asked to find leads, prospects, or fill the pipeline. Args: optional segment/geography focus (e.g. "recycling Egypt").
---

You are now executing the **Lead Hunter** worker.

1. Read `MBM/Workers/02-lead-hunter.md` and `MBM/MissionControl/Knowledge_Base/offer.md` in full — they are the SOP and the scoring rubric.
2. If a matching mission exists in `MBM/MissionControl/Missions/Inbox/`, claim then start it (`bash scripts/mbm.sh mission claim <id> <your-registry-id> && bash scripts/mbm.sh mission start <id>` — commit and push the claim immediately, Article 3); otherwise create one first (`bash scripts/mbm.sh mission new "<title>" lead-hunter P1`).
3. Use WebSearch/WebFetch against the source list in the worker file. Apply the args ($ARGUMENTS) as segment/geography focus if given.
4. Create leads with `bash scripts/mbm.sh lead add "<Company>" --score N --industry <x>`, then fill each JSON per `MBM/CRM/README.md`. Every lead needs a sourced signal — no signal, no lead.
5. Finish: `bash scripts/mbm.sh validate && bash scripts/mbm.sh metrics`, log counts in the mission, move it to Review, commit.
