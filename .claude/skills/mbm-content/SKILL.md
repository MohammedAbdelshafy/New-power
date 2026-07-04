---
name: mbm-content
description: Run the MBM Content Engine worker — turn completed projects/missions into LinkedIn posts, case studies, before/after stories. Args: optional source (mission id, "zwm platform", topic).
---

You are now executing the **Content Engine** worker.

1. Read `MBM/Workers/05-content-engine.md` (formulas, style rules, quality bar).
2. Pick source material: $ARGUMENTS if given, else the most recent items in `MBM/MissionControl/Missions/Completed/` and won deals without content yet.
3. Draft to `MBM/CRM/content/posts/` or `MBM/CRM/content/case-studies/` per the type formulas. Real numbers only — if you don't have them, list the questions the founder must answer instead of inventing figures.
4. Mark `STATUS: READY FOR HUMAN REVIEW` (publishing is human-gated), update/file the mission, commit.
