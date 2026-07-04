---
name: mbm-followup
description: Run the MBM Follow-up Manager worker — sweep for due/overdue follow-ups, classify replies, recommend and queue next actions. Use at session start or when asked "what needs follow-up?".
---

You are now executing the **Follow-up Manager** worker.

1. Read `MBM/Workers/07-followup-manager.md` (sweep SOP + objection playbook).
2. Run `bash scripts/mbm.sh followups` to get the due list.
3. Work every item per the stage-based rules: queue sequence steps, classify replies against the objection playbook, verify post-meeting proposals exist, park not-nows with re-engage dates.
4. For each action: append to the lead's `history[]`, set the new `next_action`, file missions for other workers' work.
5. Finish: `bash scripts/mbm.sh followups` must report zero overdue. Then `bash scripts/mbm.sh validate && bash scripts/mbm.sh metrics`, commit, and give the human a short list of anything that needs a human decision or send.
