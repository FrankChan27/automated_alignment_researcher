# ARCHITECTURE_AUDIT — AAR Grok Bot Gateway Smoke

## Goal
Wire an OUT-of-tree `AgentProvider` that drives the dedicated **AAR Grok Researcher**
agent through the local Grok Bot sand gateway HTTP API, then prove
`AutonomousAgentLoop.run()` advances state with that provider (no Anthropic, no
Cursor Cloud Agent, no XAI_API_KEY).

## Seams used
| Seam | Location |
|------|----------|
| Core factory | `aar.research_loop.provider.get_agent_provider` |
| Core loop | `aar.research_loop.agent.AutonomousAgentLoop` |
| Core session protocol | `AgentSession.query` + `receive_response` → `AssistantEvent`/`ResultEvent` |
| OUT provider | `downstream/poc/aar_grok_bot_smoke/providers/grok_bot_gateway.py` |
| Load path | `AAR_AGENT_PROVIDER=external` + `AAR_AGENT_PROVIDER_MODULE` + `AAR_AGENT_PROVIDER_PATH` |

## Auth path (proven on this box)
- Config: `/home/box/agent-data/gateway.json` (`host`/`port`/`scheme`/`token`)
- Base URL used: `http://127.0.0.1:<port>` (loopback; config host may be `0.0.0.0`)
- `POST /api/sendPrompt` `{"agentId","prompt"}` → `{"accepted":true}`
- `POST /api/openAgent` `{"id"}` → transcript list
- `POST /api/listAgents` → metadata incl. `isRunning` / `isRunningTurn` / `lastMessageId`
- Researcher agent id: `fac98a36-f560-43b8-9ac8-1ddacbbd16ed` (name: AAR Grok Researcher)

## Provider behavior
1. `query(task)` stores task
2. `receive_response` reads gateway.json, baselines transcript seq/ids, POSTs sendPrompt
   with workspace cwd + tool guidance + AAR task
3. Polls listAgents + openAgent until `isRunningTurn` false and a new `send-message`
   assistant entry appears after the user prompt
4. Yields `AssistantEvent([TextPart])` then `ResultEvent(stop_reason="end_turn")`
5. Errors as `ProviderError` with codes; token never included

## Explicit non-goals
- Does not overwrite `aar_provider_002` historical PoC
- No core vendor-name branches; module path is the only external load key
- No OAuth, no Anthropic SDK, no XAI_API_KEY

## Package layout
```
downstream/poc/aar_grok_bot_smoke/
  providers/grok_bot_gateway.py
  scripts/run_provider_probe.py
  scripts/run_native_loop.py
  evidence/
```
Work artifacts: `/workspace/aar_grok_bot_smoke_work/`
