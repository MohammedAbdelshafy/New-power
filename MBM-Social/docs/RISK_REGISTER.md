# RISK_REGISTER — MBM-Social v1

| # | Risk | L×I | Mitigation |
|---|---|---|---|
| R-1 | Hook quality on real content disappoints (heuristic is crude; synthetic test proves plumbing, not taste) | H×H | Agent mode is the production path (`prompts/hook-prompt.md`); T-1 acceptance requires founder rating clips "postable"; iterate prompt before any client sees output |
| R-2 | Predicted scores mistaken for real performance | M×H | Every artifact labels them `predicted`/uncalibrated; M-010 calibrates; never quote predictions to clients |
| R-3 | Arabic rendering defects (RTL, shaping, fonts) ship to the market we claim as our wedge | M×H | T-2 gate before AR go-to-market; add Noto Naskh; visual check on device |
| R-4 | CPU-only rendering too slow at client volume | L×M | Measured 21s/66s source today; scales linearly; NVIDIA runner (issue #8) if a client needs >20 clips/day |
| R-5 | Copyright/permission on client source videos | M×H | Only process client-owned/licensed content; permission line in the pilot agreement; refuse third-party rips |
| R-6 | Platform ToS issues from automated posting | L×M | v1 posts by hand (Article 5) — no automation to ban |
| R-7 | Founder attention split across two revenue lines stalls both | M×H | Sprint plan interleaves; lead packs (already sellable) fund runway while clipping matures |
| R-8 | Scope creep into Post-v1 features before first sale | M×M | Revenue-First rule in TASK_GRAPH; new features need a paying-client justification in the mission |
