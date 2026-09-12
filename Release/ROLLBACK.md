# Rollback Guide

Git is the entire state (Article 2), so rollback = git operations. Three scenarios, in rising severity:

## 1. Bad site deploy (Pages shows something wrong)
```bash
git revert <bad-commit-sha>          # never force-push main
git push origin main                  # pages.yml redeploys automatically
```
Verify the Pages URL after the Action completes. If the workflow itself is broken, re-run the last green "Deploy to GitHub Pages" run from the Actions tab (it redeploys the artifact of that commit).

## 2. Bad release tag (gates were bypassed or a gate lied)
```bash
git revert <sha-range-of-the-release>       # revert commits, keep history honest
echo "<previous-version>" > Release/VERSION # restore version
# document what happened:
bash scripts/mbm.sh emit ReleaseRolledBack v<X.Y.Z> <worker> "<why>"
```
Add a CHANGELOG entry under the rolled-back version saying it was withdrawn and why. Do **not** delete the tag — tags are history; mark the changelog instead.

## 3. Corrupted system state (bad migration, mangled missions/CRM)
```bash
git log --oneline -15                        # find last-known-good
git revert <bad>..HEAD                       # preferred: revert the range
# ONLY if revert is impossible AND the founder approves:
git checkout <last-good-sha> -- MBM/         # restore the tree, commit forward
```
Never rewrite pushed history — other workers have pulled it (Article 3 depends on shared history). Always roll *forward* with new commits.

## Always, after any rollback
1. `bash scripts/smoke-test.sh` — confirm the system is healthy again.
2. `bash scripts/mbm.sh validate && bash scripts/mbm.sh metrics`.
3. File a P0 mission: root-cause + the missing gate that would have caught it. A rollback without a new gate (or a fixed gate) is an incident waiting to repeat.
