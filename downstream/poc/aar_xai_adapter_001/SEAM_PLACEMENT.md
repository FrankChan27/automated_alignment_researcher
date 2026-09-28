# SEAM_PLACEMENT — AAR-xAI-adapter-001 PHASE 2

**Date:** 2026-09-28 (UTC+8)  
**Depends on:** PHASE 0 map + PHASE 1 contract  
**Status:** design lock before implementation

## Decision

| Choice | Value |
|--------|-------|
| Core seam module | `aar/research_loop/provider.py` — Protocol + neutral types + `get_agent_provider()` only (**no grok imports**) |
| Claude backend | `aar/research_loop/providers/claude_sdk.py` (wrap existing SDK; keeps upstream default) **or** inline adapter in same providers pkg — still Anthropic-only when selected |
| Grok backend | **downstream only:** `downstream/poc/aar_xai_adapter_001/provider/grok_cli.py` (+ `__init__.py`) |
| Registration | `AAR_AGENT_PROVIDER=grok_cli` → importlib load of downstream module path (env `AAR_GROK_PROVIDER_MODULE` defaulting to poc path) so **core never imports grok** |
| `run.py` AUTH | If provider is `grok_cli`, skip `ANTHROPIC_API_KEY` requirement; still require key for `claude_sdk` |
| `BaseAgent` | Depend only on `AgentProvider` / neutral events |
| Tool bind | **Option A**: plain callables + schema registry; `bind_for_provider(provider_name)` — Claude uses `create_sdk_mcp_server`; Grok MVP uses CLI built-ins (`Read,Write,Edit,Bash,Glob,Grep,WebSearch,WebFetch`) + research HTTP via thin wrappers invoked as allow-listed tools **or** Bash-mediated server API if MCP parity incomplete. Prefer real MCP if grok supports SDK MCP servers; else document GAP_MCP and keep evaluate_model reachable. |
| Monitor | `MONITOR_REQUIRED=0` for Grok ≥5-iter POC unless grok-backed monitor added; record gap |
| Forbidden | POC-001 `run_loop`; new scheduler/state machine; editing oauth-001/002; grok code in `aar/` |

## Why core touch is justified

`PROVIDER_INTERFACE_EXISTS=false` and Claude imports live in `agent.py` + tool modules. Downstream monkeypatch alone cannot remove `from claude_agent_sdk import …` at import time without fragile patching. Minimal core unbind = introduce neutral Protocol + factory + BaseAgent reroute. **No research-semantics rewrite.**

## File touch plan (implementation PHASE 3+)

**Core (minimal):**

1. `aar/research_loop/provider.py` (new) — types + Protocol + factory
2. `aar/research_loop/providers/claude_sdk.py` (new) — legacy backend
3. `aar/research_loop/agent.py` — BaseAgent uses factory; drop direct Claude imports
4. `run.py` — conditional AUTH gate
5. Tool modules — defer decorator unbind if Claude backend still needs them; introduce `get_mcp_servers(local_mode)` that Claude path uses existing create_*; Grok path returns {} or alternate bind

**Downstream:**

1. `downstream/poc/aar_xai_adapter_001/provider/grok_cli.py` — subprocess/PTY-free CLI session using `--single` + streaming-messages-json or plain
2. Design docs already in POC root; evidence + smokes
3. Launch helper script for 8D POC-002 task (≥5 iters) with env wiring

**Untouched:** `downstream/poc/aar_xai_oauth_001/`, `…_oauth_002/`, POC-001 homemade loop.

## Evidence plan

| Artifact | Meaning |
|----------|---------|
| `evidence/UNPATCHED_agent_entry.txt` | frozen BLOCKED without key |
| Auth metadata probe | presence/expires/mode only |
| Adapter smoke | token via grok CLI OAuth, `API_KEY_USED=false` |
| Loop drive | instantiate AutonomousAgentLoop with grok provider; aim ≥5 sessions on 8D task |
| SECRET_SCAN.txt | no secrets/PII in POC tree |

## Ready for implementation

PHASE 0–2 design complete → PHASE 3 implement seam + grok_cli backend (still no Reviewer notify).
