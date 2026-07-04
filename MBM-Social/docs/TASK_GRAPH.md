# TASK_GRAPH — MBM-Social to first revenue

Virtual teams map onto the existing role/executor architecture (Article 6 — no new team system). One executor (fabel/claude session) works batches in parallel within a turn; other registered workers claim missions concurrently via Mission Control.

| Team | Maps to | Owns |
|---|---|---|
| Alpha (Frontend) | marketing-agent role | Post-v1: clips gallery page (reuse Dashboard patterns) |
| Bravo (Backend) | crm-brain role | pipeline runner, CRM ledger (done in M-008) |
| Charlie (AI Pipeline) | content-engine + agent hook prompt | s02 hooks quality, prompt library |
| Delta (Media) | crm-brain role | s04–s06 ffmpeg stages (done) |
| Echo (Database) | CRM (files) | ledger schema (done — no DB server, DL-006) |
| Foxtrot (Auth) | n/a in v1 | Post-v1 (no multi-user surface yet) |
| Golf (Deployment) | mbm-scripts | runner requirements doc (done); founder-machine setup |
| Hotel (QA) | smoke suite | T-5 below |
| India (Performance) | M-010 | benchmarks |
| Juliet (Docs) | this docs/ set | done for v1 |

## Tasks (P=priority, D=dependencies, AC=acceptance, T=time, R=risk)

- **T-1 · Real-video validation run** — P0 · D: founder provides 1 video (B-3) + env with HF access (B-1) · AC: 3 publish packages from a real video, founder rates ≥2 "postable" · T: 1 session · R: hook quality on real content unknown (mitigate: agent mode with hook-prompt.md, not heuristic)
- **T-2 · Arabic end-to-end** — P0 · D: T-1 · AC: AR video → AR captions render correctly (RTL, shaping) on device · T: 0.5 session · R: font/shaping issues (mitigate: libass + Noto/Amiri fallback)
- **T-3 · M-010 benchmarks** — P1 · D: T-1 · AC: Production/Performance/Benchmark reports with measured numbers, ≥3 videos · T: 1 session · R: low
- **T-4 · First clipping pilot (revenue)** — P0 · D: T-1 · AC: one real creator/business gets a free 3-clip pilot + offer sheet; feedback in CRM · T: founder outreach + 1 session · R: pilot converts nobody (mitigate: pick from existing ZWM network)
- **T-5 · Pipeline tests in smoke suite** — P1 · D: none · AC: `smoke-test.sh` gains a pipeline section (synthetic job, stages s02–s07, asserts packages + events) · T: 0.5 session · R: low
- **T-6 · Scheduling/publishing helper** — P2 · D: T-4 demand · AC: packages get suggested post times; human posts · T: 0.5 session · R: over-building before demand
- **Post-v1 backlog** (Revenue-First rule): creator profiles, template system, asset manager, settings UI, notifications, analytics dashboard page, prompt library UI. None block selling; all become missions only when a paying client needs them.
