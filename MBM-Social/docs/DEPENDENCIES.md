# DEPENDENCIES

```
B-1 (whisper model access: env w/ HF allowed, or founder machine)
B-3 (founder-approved real video) ──┐
                                    ├──▶ T-1 real-video run ──▶ T-2 Arabic e2e ──▶ T-3 M-010 benchmarks ──▶ v0.1-alpha tag
                                    │                     └──▶ T-4 first pilot (revenue)
T-5 smoke-suite pipeline tests ─────┘ (independent — can run now)

Runtime deps: ffmpeg 6.x · python3 · faster-whisper · yt-dlp · libass fonts (DejaVu; add Noto Naskh for AR polish)
Mission deps: M-009 (packaging polish) after T-1 feedback · M-010 after M-009 · v0.1-alpha only after M-010 passes
External: HuggingFace CDN (models) · target platforms' upload UIs (human posts — no API keys needed in v1)
```

Independent-now set (parallelizable immediately): T-5, M-012 lead pack (different worker), M-005 case study, founder M-001 sign-off.
