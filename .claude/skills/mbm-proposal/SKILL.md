---
name: mbm-proposal
description: Run the MBM Proposal Generator worker — produce a proposal with scope, visible ROI math, three pricing options and timeline for a lead after a meeting. Args: lead id.
---

You are now executing the **Proposal Generator** worker.

1. Read `MBM/Workers/06-proposal-generator.md` (SOP + template) and `MBM/MissionControl/Knowledge_Base/offer.md` (price bands).
2. Load the lead file, its intel report, and meeting notes from `history[]`. Missing meeting notes → ask the human for them; do not guess the prospect's problem.
3. Write `MBM/CRM/proposals/<lead-id>-proposal-v1.md` per the template: problem in their words, scope as numbered nouns, ROI math shown, Pilot/Standard/Full pricing, week-by-week timeline, one next step.
4. Mark `STATUS: READY FOR HUMAN REVIEW`. Update lead stage/next_action after the human sends. Run `bash scripts/mbm.sh metrics`, update the mission, commit.
