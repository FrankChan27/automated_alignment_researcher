# GROK_PROVIDER_MAPPING — AAR-xAI-adapter-001

**CLI:** grok 1.0.41 (`/home/box/.local/bin/grok`)  
**Sources:** `grok --help`, `grok agent --help`, `grok mcp --help`, oauth-002 runtime smoke, live `grok models`  
**Legend:** `RUNTIME_PROVEN` | `DOCUMENTED_ONLY` | `UNSUPPORTED` | `UNKNOWN`

| Contract need (MIN_PROVIDER_CONTRACT) | Grok CLI surface | Status | Notes |
|---------------------------------------|------------------|--------|-------|
| Noninteractive session / `query(task)` | `--single` / `-p PROMPT`, also `--prompt-file`, `--prompt-json` | **RUNTIME_PROVEN** | oauth-002 PHASE4 smoke EXIT=0 exact token |
| Verbatim prompt | `--verbatim` | **RUNTIME_PROVEN** | used in oauth-002 smoke |
| Model select | `-m` / `--model` | **RUNTIME_PROVEN** | default `grok-4.7`; `grok models` lists 4 |
| Permission mode | `--permission-mode` values: default, acceptEdits, auto, dontAsk, bypassPermissions, plan | **RUNTIME_PROVEN** (dontAsk in smoke) | `bypassPermissions` **DOCUMENTED_ONLY** (same enum) |
| Max turns | `--max-turns N` | **DOCUMENTED_ONLY** | smoke used `1`; multi-turn not separately smoked |
| CWD | `--cwd` | **DOCUMENTED_ONLY** | |
| System prompt override | `--system-prompt-override` (alias `--system-prompt`) | **DOCUMENTED_ONLY** | |
| Machine-readable stream | `--output-format plain\|json\|streaming-json\|streaming-messages-json` | **RUNTIME_PROVEN** (plain); streaming-messages-json **DOCUMENTED_ONLY** | help: streaming-messages-json = Anthropic Messages API NDJSON |
| Partial deltas | `--include-partial-messages` | **DOCUMENTED_ONLY** | only with streaming-messages-json |
| Built-in tools allow/deny | `--tools`, `--disallowed-tools`, `--allow`, `--deny`, `--disable-web-search` | **DOCUMENTED_ONLY** | oauth-002 exercised deny-list flags only |
| Always approve tools | `--always-approve` | **DOCUMENTED_ONLY** | |
| OIDC auth (no API key) | local `~/.grok/auth.json`; CLI reads session | **RUNTIME_PROVEN** | `API_KEY_USED=false`; `grok models` login banner |
| Auth probe | `grok models` | **RUNTIME_PROVEN** | EXIT=0 when session live |
| MCP servers | `grok mcp add\|list\|…`; agent `--plugin-dir` can inject MCP | **DOCUMENTED_ONLY** | not runtime-proven for AAR server-api-tools |
| Headless agent stdio | `grok agent stdio` | **DOCUMENTED_ONLY** | not used in oauth-002; optional future transport |
| Structured output schema | `--json-schema` | **DOCUMENTED_ONLY** | |
| Session resume | `--resume` / `--continue` | **DOCUMENTED_ONLY** | AAR loop uses **fresh session per iteration** — resume not required |
| api.x.ai OAuth token reuse | — | **UNSUPPORTED** / NOT_JUSTIFIED | mission forbids hand-stuffed auth header; oauth-002 NOT_TESTED |
| Cursor / Anthropic / xAI API Key | — | **UNSUPPORTED** (forbidden) | |
| In-process Python SDK equivalent to ClaudeSDKClient | — | **UNKNOWN** / not required | we use CLI subprocess |
| Claude-specific `betas` / adaptive `thinking` options | — | **UNSUPPORTED** on grok path | map via `SessionOptions.extra` ignored by grok backend |
| Exact Claude MCP `create_sdk_mcp_server` in-process | — | **UNSUPPORTED** on grok path | alternate: CLI MCP config or Bash-mediated research tools |

## Provider implementation binding (PHASE 3)

`GrokCLIProvider` will use:

```text
grok --single <task> --verbatim \
  --model <model> \
  --cwd <cwd> \
  --permission-mode bypassPermissions|dontAsk \
  --max-turns <N> \
  [--system-prompt-override <sys>] \
  [--tools …] \
  --output-format plain   # MVP parse; upgrade to streaming-messages-json if needed
```

Auth: inherited local OIDC session only. Never pass API keys.

## Gaps affecting PHASE 5

- AAR MCP tools (`evaluate_model`, …) via Claude `create_sdk_mcp_server` are **not** directly portable → status **DOCUMENTED_ONLY/UNSUPPORTED** for in-process MCP. Mitigate with Bash + POC-002 `run_eval` / scripts if MCP add path not proven — may yield CASE partial if full MCP parity missing.
