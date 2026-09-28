# MIN_PROVIDER_CONTRACT — AAR-xAI-adapter-001 PHASE 1

**Date:** 2026-09-28 (UTC+8)  
**Depends on:** `CLAUDE_COUPLING_MAP.md` (PHASE 0)  
**Goal:** Smallest provider-neutral contract so `AutonomousAgentLoop` can drive researcher inference via official **grok CLI + OIDC**, without POC-001 homemade loop and without baking grok into core.

## Non-negotiables

- Preserve upstream research semantics: iteration = fresh session; stop = timeout | max_iterations; findings / evaluate_model / share_finding / submit_idea_proposal contracts; same 8D task as POC-002 later.
- Forbidden auth for researcher: Cursor, Anthropic API, xAI API Key, hand-stuffed Bearer to api.x.ai.
- Allowed auth: official `grok` CLI local OIDC (`~/.grok/auth.json`).
- Prefer **downstream-only** Grok backend; **core** only to unbind Claude hardwire behind this contract.
- No secrets/PII in artifacts.

## What BaseAgent actually requires today

From `aar/research_loop/agent.py` `BaseAgent._execute_once`:

1. Build session options (tools, system prompt, permission mode, cwd, model, MCP servers, …).
2. Open a session (`async with ClaudeSDKClient`).
3. `await client.query(task)` once per session (task = rendered research prompt).
4. `async for message in client.receive_response()` until terminal result.
5. Interpret message content as text and/or tool-use for logging + `AgentResult`.
6. Map provider failures (esp. capacity/overloaded) to retry/backoff in `execute()`.

MCP tools are **created** via `claude_agent_sdk.tool` / `create_sdk_mcp_server` and passed as `mcp_servers` into options. Tool *bodies* are research HTTP/fs — only the **registration/transport** is Claude-coupled.

## Minimal contract (provider-neutral)

Place (preferred): tiny module under core, e.g. `aar/research_loop/provider.py` (name TBD in PHASE 2), **or** a Protocol defined in core and implemented downstream if import injection works without circularity. Implementations: Claude (legacy wrap) + Grok CLI (downstream).

### Types (neutral; no `claude_agent_sdk` imports)

```text
TextPart(text: str)
ToolUsePart(name: str, input: dict, id: str | None = None)
ThinkingPart(thinking: str)          # optional; log-only

AssistantEvent(content: list[Part])
ResultEvent(result: Any = None, stop_reason: str | None = None)
# ProviderEvent = AssistantEvent | ResultEvent | (opaque log-only events ignored by loop)

@dataclass
class SessionOptions:
  model: str
  cwd: str | Path
  system_prompt: str | None
  allowed_tools: list[str]           # built-in names + mcp__server__tool
  permission_mode: str               # intersect: default|acceptEdits|auto|dontAsk|bypassPermissions|plan
  mcp_servers: dict[str, Any]        # opaque to loop; backend-specific binding
  max_turns: int | None = None
  cli_path: str | None = None        # backend binary override
  extra: dict[str, Any]              # backend-only (Claude betas/thinking/effort; Grok --verbatim etc.)
```

### Protocol

```text
class AgentProvider(Protocol):
  name: str   # "claude_sdk" | "grok_cli" | …

  def session(self, options: SessionOptions) -> AgentSession:
    ...

class AgentSession(Protocol):
  async def __aenter__(self) -> AgentSession: ...
  async def __aexit__(self, *exc) -> None: ...
  async def query(self, task: str) -> None: ...
  def receive_response(self) -> AsyncIterator[ProviderEvent]: ...
```

### Factory (unbind point)

```text
# env AAR_AGENT_PROVIDER=claude_sdk|grok_cli (default today: claude_sdk for upstream compat)
get_agent_provider() -> AgentProvider
```

`BaseAgent` uses **only** `AgentProvider` / `ProviderEvent` / `SessionOptions`. No `ClaudeSDKClient` / message-type imports in `agent.py` after unbind.

### Tool registration seam (separate, still minimal)

Research tools must not import `claude_agent_sdk` at module top if Grok path is active.

Minimal approach (PHASE 2 chooses one):

| Option | Idea | Core churn |
|--------|------|------------|
| **A (prefer)** | Keep tool functions as plain async callables + JSON schemas; thin `bind_mcp(provider, tools) -> mcp_servers` adapter per backend (Claude: `create_sdk_mcp_server`; Grok: CLI `--tools` / MCP bridge or prompt-side HTTP helpers) | Small shared registry in core or downstream preload |
| **B** | Dual-decorated tools (Claude decorator no-op when unused) | Messy |
| **C** | Leave Claude MCP as-is; Grok path uses built-in shell/read/write only + HTTP eval via Bash | Weaker semantics; last resort |

Contract requirement: **tool semantic names** (`evaluate_model`, `share_finding`, …) remain available to the agent under Grok path for UPSTREAM_SEMANTICS_PRESERVED. Exact MCP wire format may differ if Grok CLI accepts equivalent allow-lists.

### Auth contract

| Backend | Auth |
|---------|------|
| `claude_sdk` | existing `ANTHROPIC_API_KEY` (unchanged for upstream) |
| `grok_cli` | **no API key**; official CLI reads `~/.grok/auth.json` OIDC. Entry gate in `run.py` must accept `AAR_AGENT_PROVIDER=grok_cli` **without** Anthropic key. |

Probe-only metadata allowed in evidence: presence, mode, expires_at, auth_mode. Never secret values / PII.

### Error contract

```text
ProviderError(message, code: str | None, retryable: bool)
# map: Claude 529 overloaded → retryable=True
# map: grok auth expired / not authenticated → retryable=False, code=AUTH_EXPIRED
```

`BaseAgent.execute` retries only `retryable` (preserve overloaded behavior for Claude; do not invent Anthropic retries for Grok).

### Out of contract (explicit)

- Integrity **monitor** (`monitor.py` → api.anthropic.com): not part of MIN provider seam. For Grok POC: `MONITOR_REQUIRED=0` or later optional grok-backed monitor. Document as gap if disabled.
- Eval judges (`JUDGE_BACKEND`): unrelated.
- POC-001 `run_loop` / new scheduler / leaderboard / changing 8D objective: **forbidden**.
- Streaming deltas: optional; loop only needs whole Assistant/Result events (Grok `--output-format streaming-messages-json` or `plain` for smoke).

## Grok CLI runtime mapping (oauth-002 + live help)

| Contract need | Grok CLI 1.0.41 |
|---------------|-----------------|
| Noninteractive session | `--single` / `-p` |
| Model | `--model grok-4.7` (default) |
| Permission | `--permission-mode dontAsk` or `bypassPermissions` |
| Max turns | `--max-turns N` |
| CWD | `--cwd` |
| Machine-readable | `--output-format plain\|json\|streaming-json\|streaming-messages-json` |
| Anthropic-wire stream | `streaming-messages-json` (**documented** as Anthropic Messages API NDJSON) — strong fit for MESSAGE_SCHEMA adapter |
| Auth | local OIDC via CLI (no key) |
| Smoke pattern (oauth-002) | `grok --single … --verbatim --model grok-4.7 --max-turns 1 --permission-mode dontAsk` |

Live PHASE 0/1 probe (this box): `grok models` → logged in, default grok-4.7, EXIT=0 (`evidence/PHASE0_grok_models_probe.txt`). Session may still expire later; treat AUTH_EXPIRED as soft-fail with code ready.

## Success metrics for this contract

| Field | Target |
|-------|--------|
| **MIN_PROVIDER_SEAM** | `AgentProvider` + `SessionOptions` + neutral events; factory env switch |
| **UPSTREAM_SEMANTICS_PRESERVED** | `AutonomousAgentLoop` control-flow unchanged in spirit; no homemade loop |
| **GROK_PROVIDER_RUNTIME** | `grok_cli` backend → official binary + OIDC |
| **CLAUDE_COUPLING_DEPTH** after seam | transport unbound; research semantics intact |
| Core touch | only files needed to route through contract (expect `agent.py`, `run.py`, maybe thin `provider.py` + tool bind) |

## PHASE 2 preview (not started)

- SEAM placement decision (core `provider.py` vs injection-only).
- UNPATCHED vs PATCHED evidence plan.
- Grok backend module path under `downstream/poc/aar_xai_adapter_001/`.
- Tool-bind option A/B/C choice.
- Do **not** implement until PHASE 2 design committed.

## CASE hypothesis (updated)

Structurally: **feasible**. Grok CLI surface is close to Claude Code (permission modes, tools flags, Anthropic-wire streaming-messages-json). Remaining risks: MCP server parity for research tools; monitor Anthropic dependency; session expiry.
