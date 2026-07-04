# Lessons Learned — auto-mirrored from completed missions (Article 7)

## M-007 — Mission System v2: claim lifecycle, worker registry, event bus, routing, governance (2026-07-04)
- Git-native primitives covered every requirement: file moves = state machine, push conflicts = claim locks, JSONL in git = event bus. Zero new infrastructure; every worker that can `git pull` can participate.
- Embedding python3 heredocs in bash demands strict quoting discipline: double quotes only inside single-quoted heredocs, no f-strings with nested quotes. Cost three debug cycles in v1; v2 written to that rule from the start.
- Migration scripts that strip quotes naively will mangle YAML values containing quotes — three acceptance criteria needed manual repair. Next schema migration: parse, don't regex-strip.
- The role/executor split (Workers/ vs Registry/) dissolved an apparent requirements conflict: "Sales Agent" and "Revenue Dashboard" became role+executor pairings instead of duplicate systems (DL-008).
- Enforcement beats convention: making `mission complete` refuse on empty lessons turned Article 7 from a hope into a property. Wherever possible, encode constitution articles into the CLI.

## M-011 — Production readiness & revenue launch: audit, freeze v1, release system, MBM-Social readiness (2026-07-04)
- A smoke suite pays for itself immediately: 26 checks caught 2 real bugs (route parser vs inline YAML comments; lessons-guard bypass via template placeholder) on their first run.
- The honest answer to "audit the pipeline" was "it does not exist" — refusing to fabricate benchmarks kept every other report trustworthy. Reports that can only come from measurement (Production/Performance/Benchmark) were assigned to the mission that measures (M-010), not written speculatively.
- The permission system rightly blocked agent modification of its own hook config; such changes belong to the founder (issue filed). Design lesson: assume agent-self-config is out of bounds.
- Fastest-revenue analysis beat feature-building: the lead-pack product (M-012) required zero new code - only packaging what the Lead Hunter already produces.
