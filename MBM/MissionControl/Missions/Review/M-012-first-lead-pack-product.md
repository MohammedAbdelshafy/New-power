---
id: M-012
title: "Build and package lead pack #1 (100 leads, one segment) as a sellable product"
objective: "A founder-sellable 100-lead pack: verified, scored, signal-backed leads with delivery doc and sales one-pager — the fastest path from the existing system to invoiced revenue"
priority: P0
phase: 1
dependencies: []
role: lead-hunter
required_skills:
  - web-search
  - research
  - writing
preferred_worker: claude
fallback_workers:
  - fabel
  - chatgpt
status: review
owner: fabel
reviewer: human-founder
created: 2026-07-04
due: 2026-07-10
outputs:
  - MBM/CRM/leads/ (100 records)
  - MBM/CRM/content/lead-packs/pack-001/ (CSV export + delivery doc + sales one-pager)
acceptance_criteria:
  - 100 leads in ONE segment (founder picks; default construction Egypt), each with company, website, industry, size, named signal + source URL, and >=1 contact where public
  - all records pass mbm.sh validate; fit_score honest per offer.md rubric
  - CSV/Sheet export + a delivery doc explaining scoring and signals (this is what the buyer receives)
  - one-page sales sheet for the pack (what it is, sample rows, price per offer.md Offer 4)
  - zero fabricated contacts - public sources only, every signal traceable
artifacts:
  - MBM/CRM/content/lead-packs/pack-001/
---

## Context
Founder order: "let's start selling 100-pack leads." Offer 4 in Knowledge_Base/offer.md. The Lead Hunter role + CRM already produce exactly this artifact; this mission packages it for sale. Doubles as M-002's hunt (same records feed our own pipeline).

## Instructions
Run `/mbm-lead-hunt` per the role SOP; export via a simple script into pack-001/. Note: web-search quota limits mean this needs a fresh session window.

## Lessons Learned
- 9-lead tranche 1 shipped; construction giants score lower on reachability than mid-size - packs need a mid-size quota next tranche.

## Log
- 2026-07-04 created by fabel per founder order
- 2026-07-04 founder revenue-sprint order: Revenue > all; M-001 dep lifted (pricing stays DRAFT until sign-off)
- 2026-07-04 claimed by fabel
- 2026-07-04 started
- 2026-07-04 moved to review
