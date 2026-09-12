---
id: M-013
title: "MBM digital headquarters: docs-first website (context -> brand -> design -> architecture -> code)"
objective: "The single public+private entry point for MBM: products, lead packs, AI services, docs, and Mission Control views - built only after the 11 intelligence docs are founder-approved"
priority: P1
phase: 1
dependencies:
  - M-001
role: marketing-agent
required_skills:
  - writing
  - code
  - marketing
  - architecture
preferred_worker: fabel
fallback_workers:
  - claude
status: inbox
owner: ""
reviewer: human-founder
created: 2026-07-04
due: ""
outputs:
  - Website/CONTEXT.md
  - Website/BRAND.md
  - Website/DESIGN.md
  - Website/ARCHITECTURE.md
  - Website/TECH_STACK.md
  - Website/CONTENT_MAP.md
  - Website/USER_JOURNEYS.md
  - Website/ROADMAP.md
  - Website/MISSIONS.md
  - Website/README.md
acceptance_criteria:
  - CONTEXT.md completed via founder interview (one question at a time), facts only, founder-approved
  - all intelligence docs approved BEFORE any code is generated
  - decision log entries go to the existing Decision_Log (Article 6 - no separate DECISION_LOG.md)
  - site plan covers public (home, products, lead packs, AI services, pricing, contact) and private (mission control, dashboards) surfaces
  - code phase only starts after founder writes "docs approved" in this mission's log
artifacts: []
---

## Context
Founder's master website prompt (2026-07-04): build the digital HQ of an AI company, documentation-first, interview-driven. Existing assets to reuse, not duplicate: ZWM site (`index.html`), ops platform (`platform.html`), revenue dashboard (`MBM/Dashboard/`), this repo's brand-adjacent design language.

## Instructions
Interview protocol per the master prompt: ONE question at a time, never invent facts, show CONTEXT.md before continuing. Seeded draft: `Website/CONTEXT.md`.

## Lessons Learned
(fill before completion — Article 7)

## Log
- 2026-07-04 created by fabel from founder's master website prompt
