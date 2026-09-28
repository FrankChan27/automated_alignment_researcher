# PROVIDER_CONTRACT_V2 — AAR-provider-002 PHASE 1

Closes adapter-001 REVIEW #8: core must load external researcher providers **without vendor name knowledge**.

## Core question

`CAN_AAR_LOAD_EXTERNAL_RESEARCHER_PROVIDER_WITHOUT_VENDOR_KNOWLEDGE`

PASS only if: core `.py` has **zero** hits for `grok|xai|x\.ai|grok_cli|AAR_GROK|aar_xai_adapter_001`, and loop/run branch on **capability flags**, not name tuples.

## Unchanged transport contract (from MIN_PROVIDER_CONTRACT)

- Types: `TextPart`, `ToolUsePart`, `ThinkingPart`, `AssistantEvent`, `ResultEvent`, `SessionOptions`, `ProviderError`
- Protocols: `AgentSession` (`query` / `receive_response`), `AgentProvider` (`name`, `session(options)`)
- Loop/scheduler/eval/objective: **untouched**

## Capability flags (V2 addition)

Providers expose boolean attributes (defaults conservative for unknown externals):

| Flag | ClaudeSDKProvider | External GrokCLIProvider | Core use |
|------|-------------------|--------------------------|----------|
| `requires_anthropic_key` | `True` | `False` | `run.py` gate before agent launch |
| `supports_inprocess_mcp` | `True` | `False` | `agent.py` MCP server create + mcp__ tool allowlist |

Core **NEVER** string-matches provider names for auth/MCP. Optional `name` is label-only.

## Loading modes

| Mode | When | How |
|------|------|-----|
| **LEGACY_DEFAULT** | `AAR_AGENT_PROVIDER` unset / `claude` / `claude_sdk` / `anthropic` | Import built-in `aar.research_loop.providers.claude_sdk.ClaudeSDKProvider` |
| **EXTERNAL_PLUGIN** | any other name, or explicit module override | **Require** `AAR_AGENT_PROVIDER_MODULE`; importlib; call `get_provider()` **or** instantiate `AAR_AGENT_PROVIDER_CLASS` |

### Env vars (EXTERNAL_PLUGIN)

| Env | Required? | Meaning |
|-----|-----------|---------|
| `AAR_AGENT_PROVIDER` | label | Opaque label (may be anything); not branched on in core |
| `AAR_AGENT_PROVIDER_MODULE` | **yes** for non-claude | Dotted module path exporting factory/class |
| `AAR_AGENT_PROVIDER_CLASS` | optional | Class name if no `get_provider()` |
| `AAR_AGENT_PROVIDER_PATH` | optional | Extra filesystem path prepended to `sys.path` before import |

Unknown non-claude name **without** `AAR_AGENT_PROVIDER_MODULE` → `ProviderError(code="PROVIDER_MODULE_REQUIRED")`.

## Forbidden in core

- Aliases `grok` / `grok_cli` / `xai_grok`
- Default module `aar_xai_adapter_001...`
- Env `AAR_GROK_*`
- Comments/docstrings naming grok/xAI as baked knowledge for control flow

## Allowed out of core (OUT)

- `downstream/poc/aar_provider_002/providers/grok_cli.py` — transport-only; OIDC via official grok CLI; strip Anthropic/xAI keys from subprocess env; `get_provider()`
