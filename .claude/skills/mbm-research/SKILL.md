---
name: mbm-research
description: Run the MBM Company Researcher worker — produce a sourced intel report for a lead before outreach. Use when asked to research a company/lead. Args: lead id (e.g. L-2026-0003) or company name.
---

You are now executing the **Company Researcher** worker.

1. Read `MBM/Workers/03-company-researcher.md` (SOP + report template + quality bar) and `MBM/MissionControl/Knowledge_Base/offer.md`.
2. Locate the lead file in `MBM/CRM/leads/` matching $ARGUMENTS. If none exists, stop and say so — research without a lead record breaks the pipeline.
3. Research with WebSearch/WebFetch per the SOP order (company → decision makers → news → hiring → pains → tech → AI opportunities). Every fact gets a URL.
4. Write `MBM/CRM/intel/<lead-id>-intel.md` per the template. Update the lead file (contacts, pain_points, fit_score, stage "researched", next_action).
5. If qualified, file an outreach mission. Finish with `bash scripts/mbm.sh validate && bash scripts/mbm.sh metrics`, update the mission, commit.
