# SOP — Adding a Worker (plug-and-play, Article 8)

A worker is any executor: an LLM agent (Claude, Fabel, ChatGPT, Jarvis), an IDE agent (Antigravity, OpenCode), a local model (NVIDIA), a deterministic script, or a human. Joining takes one file and zero integration code.

## 1. Create the registry entry
Copy an existing file in `MBM/Registry/workers/` to `<worker-id>.json` and fill honestly:

```json
{
  "id": "my-worker",
  "name": "Human-readable name",
  "kind": "llm-agent | ide-agent | local-model | script | human",
  "skills": ["web-search", "writing", "code"],
  "roles": ["lead-hunter", "company-researcher"],
  "cost": "low | medium | high",
  "speed": "fast | medium | slow",
  "confidence": 0.8,
  "context_size": 128000,
  "tools": ["bash", "git", "browser"],
  "availability": "available | busy | offline",
  "mcp_support": true,
  "git_support": true,
  "web_support": true,
  "notes": "how to invoke this worker; anything routing should know"
}
```

Field meanings: `skills` are the tags missions request in `required_skills`; `roles` are the `MBM/Workers/*.md` role files this worker can execute; `confidence` (0–1) is expected quality on its declared skills — the routing engine trusts this, so overstating it hurts everyone; `cost`/`speed` are tiers, not precision.

## 2. Verify it can operate the system
The worker must be able to: read/write repo files, run (or have a human run) `scripts/mbm.sh`, and follow `SOP-mission-lifecycle.md`. Local workers sync via git per `docs/ANTIGRAVITY_SETUP.md`. A worker with `git_support: false` (e.g. copy-paste ChatGPT) works through a human proxy who commits on its behalf — the registry `notes` must say so.

## 3. Announce
Commit the registry file. Run `bash scripts/mbm.sh workers` to confirm it lists. The worker is now routable — no other change anywhere.

## Updating & leaving
Availability changes (`available`/`busy`/`offline`) are one-line edits to the registry file, committed. Routing skips `offline` workers automatically. A worker that repeatedly fails missions gets its `confidence` corrected by the CRO during weekly review — performance history from the event bus outvotes self-declared confidence.
