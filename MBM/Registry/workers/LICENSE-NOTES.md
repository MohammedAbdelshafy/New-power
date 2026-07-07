# License Notes — Web-Agent Tooling

MBM sells data commercially. A permissive license is a precondition for any tool
touching a revenue path. **This file is the source of truth; the table in
`web-agent-tools.md` is a convenience copy.** Confirm the upstream `LICENSE` file at
the exact pinned commit before adoption — projects relicense.

| Tool | License (verify at adoption) | Commercial use | Notes |
|---|---|---|---|
| microsoft/playwright | Apache-2.0 | ✅ | Patent grant; safe. |
| D4Vinci/Scrapling | BSD-3-Clause | ✅ | Attribution only. |
| modelcontextprotocol | MIT | ✅ | Spec + SDKs. |
| browser-use/browser-use | MIT | ✅ | — |
| browserbase/stagehand | MIT | ✅ | Hosted Browserbase service is separate/paid. |
| openai/openai-cua-sample-app | MIT | ✅ | Sample only; uses OpenAI API (paid). |
| anthropics/anthropic-quickstarts | MIT | ✅ | — |
| langchain-ai/langgraph | MIT | ✅ | — |
| crewAIInc/crewAI | MIT | ✅ | — |
| microsoft/autogen | MIT (some assets CC-BY) | ✅ | Confirm asset licenses if redistributing docs. |
| All-Hands-AI/OpenHands | MIT | ✅ | — |
| mannaandpoem/OpenManus | MIT | ✅ | — |
| **Skyvern-AI/skyvern** | **AGPL-3.0** | ⛔ **QUARANTINED** | Network use = distribution under AGPL. Blocked for SaaS/commercial until relicensed or fully air-gapped with legal sign-off. |
| punkpeye/awesome-mcp-servers | list (CC/MIT) | ✅ (as reference) | Individual servers carry their own licenses — check each. |
| steel-dev/awesome-web-agents | list (CC/MIT) | ✅ (as reference) | Same — per-entry licenses. |

## Rule

> No AGPL/GPL/SSPL code in a revenue path without written founder + legal sign-off.
> API-based tools (OpenAI, Browserbase, Anthropic) are permissive to *use* but bill
> per call — cost, not license, is the gate there.
