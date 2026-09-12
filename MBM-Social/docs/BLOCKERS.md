# BLOCKERS

| ID | Blocker | Blocks | Owner | Unblock path |
|---|---|---|---|---|
| B-1 | Env network policy denies model CDNs (huggingface.co, openaipublic.azureedge.net, alphacephei.com) — s01 transcribe can't fetch weights in this container | live transcription, T-1..T-3 | founder | Run T-1 on founder's machine (Antigravity bridge), OR loosen the environment's network policy for huggingface.co, OR commit a model into a private storage the policy allows |
| B-2 | No Arabic end-to-end test yet (only EN synthetic ran) | AR go-to-market claim | fabel/claude | T-2 immediately after B-1/B-3 clear |
| B-3 | No founder-approved real source video (test used synthetic espeak narration — fine for plumbing, worthless for judging hook quality) | T-1, M-008 full acceptance | founder | Send any 10–30 min video (podcast, site walkthrough, khutbah, webinar) |
| B-4 | M-001 offer/pricing sign-off still open (3rd day) | ALL selling: lead packs, pilots, clipping offer sheet | founder | 30 minutes on `Knowledge_Base/offer.md` |

B-4 is the company-level bottleneck; B-1/B-3 are the product-level ones. Everything else is execution.
