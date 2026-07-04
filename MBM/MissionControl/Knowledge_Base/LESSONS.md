# Lessons Learned — auto-mirrored from completed missions (Article 7)

## M-007 — Mission System v2: claim lifecycle, worker registry, event bus, routing, governance (2026-07-04)
- Git-native primitives covered every requirement: file moves = state machine, push conflicts = claim locks, JSONL in git = event bus. Zero new infrastructure; every worker that can `git pull` can participate.
- Embedding python3 heredocs in bash demands strict quoting discipline: double quotes only inside single-quoted heredocs, no f-strings with nested quotes. Cost three debug cycles in v1; v2 written to that rule from the start.
- Migration scripts that strip quotes naively will mangle YAML values containing quotes — three acceptance criteria needed manual repair. Next schema migration: parse, don't regex-strip.
- The role/executor split (Workers/ vs Registry/) dissolved an apparent requirements conflict: "Sales Agent" and "Revenue Dashboard" became role+executor pairings instead of duplicate systems (DL-008).
- Enforcement beats convention: making `mission complete` refuse on empty lessons turned Article 7 from a hope into a property. Wherever possible, encode constitution articles into the CLI.
