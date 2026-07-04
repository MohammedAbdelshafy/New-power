---
name: mbm-outreach
description: Run the MBM Outreach Agent worker — draft a personalized cold email + LinkedIn + follow-up sequence for a researched lead. Drafts only; a human sends. Args: lead id (e.g. L-2026-0003).
---

You are now executing the **Personalized Outreach Agent** worker.

1. Read `MBM/Workers/04-outreach-agent.md` — the style rules there are non-negotiable, especially rule 1 (never sound AI-generated) and the intel-grounding requirement.
2. Load the lead file and its intel report (`MBM/CRM/intel/<lead-id>-intel.md`). **No intel report → stop and run /mbm-research first.**
3. Draft the full sequence to `MBM/CRM/content/outreach/<lead-id>-sequence.md` per the SOP, in the lead's `language`. Self-check every message against the six style rules before marking `STATUS: READY FOR HUMAN REVIEW`.
4. If Gmail tools are available, create drafts (never send — Decision DL-003).
5. Update the lead's next_action, update the mission, commit. Tell the human exactly which file to review and send.
