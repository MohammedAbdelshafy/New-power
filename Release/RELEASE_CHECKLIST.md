# Release Checklist — every version tag passes ALL gates

Run by the releasing worker; the reviewer verifies. No gate is skippable. `scripts/release.sh <major|minor|patch>` automates gates 1–5 and aborts on any failure.

## Quality gates
1. **Smoke & regression suite** — `bash scripts/smoke-test.sh` exits 0 (26 checks: lifecycle, all guards, dependency gate, routing, CRM, registry, event bus).
2. **CRM integrity** — `bash scripts/mbm.sh validate` exits 0.
3. **Metrics fresh** — `bash scripts/mbm.sh metrics` run after last CRM change; `Dashboard/metrics.json` committed.
4. **No orphan state** — no missions in `Claimed/`/`InProgress/` owned by workers that won't continue them; anything stale is blocked-with-reason or failed-with-reason.
5. **Version + changelog** — `Release/VERSION` bumped; `Release/CHANGELOG.md` has the new section (generated from git log, then human-edited for meaning).
6. **Architecture conformance** — any change to frozen components (`MBM/Architecture_v1.md`) cites its ADR (`DL-###`) in the commit message. No ADR, no release.
7. **Constitution conformance** — nothing in the release automates a human gate (Article 5) or introduces a duplicate system (Article 6).
8. **Docs truthful** — READMEs/SOPs updated for any behavior change in this release.

## Deployment checklist (GitHub Pages — the only deploy target in v1)
1. Merge to `main` (PR from the working branch; founder approves).
2. `pages.yml` publishes **only** `index.html`, `platform.html`, `MBM/Dashboard/` — verify the "Assemble public site artifact" step is intact. CRM/missions/events must never deploy.
3. After the Actions run: open the Pages URL, check the site and `/MBM/Dashboard/` render and show current metrics.
4. Confirm the Telegram/Discord notify fired (if secrets configured).

## Tagging
```bash
bash scripts/release.sh patch        # or minor / major — runs gates, bumps, changelogs, tags
git push --follow-tags
```

## After release
- Emit a bus event: `bash scripts/mbm.sh emit ReleaseTagged v<X.Y.Z> <worker> "<one-line summary>"`.
- File follow-up missions for anything deferred during gate checks.
- If anything went wrong → `Release/ROLLBACK.md`, then a Lessons entry in the release mission.
