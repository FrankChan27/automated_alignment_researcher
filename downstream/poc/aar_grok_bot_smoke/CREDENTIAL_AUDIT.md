# CREDENTIAL_AUDIT

## Summary
| Field | Value |
|-------|-------|
| AUTH_MECHANISM | `grok_bot_sand_gateway_bearer` |
| OAUTH_USED | false |
| XAI_API_KEY_USED | false |
| ANTHROPIC_USED | false |
| ANTHROPIC_API_KEY_IN_ENV_DURING_RUN | false (popped) |
| XAI_API_KEY_IN_ENV_DURING_RUN | false (popped) |
| GATEWAY_TOKEN_LOGGED | false |
| GATEWAY_TOKEN_COMMITTED | false |
| CURSOR_CLOUD_AGENT_USED | false |

## How auth works
Provider reads `/home/box/agent-data/gateway.json` at call time and sends
`Authorization: Bearer <token>` to `http://127.0.0.1:<port>/api/*`.
`ProviderError` messages run through `_redact()` to strip bearer-looking
substrings. Evidence JSON/Markdown never include the token value.

## Researcher agent
- id: `fac98a36-f560-43b8-9ac8-1ddacbbd16ed`
- name: AAR Grok Researcher
- env override: `AAR_GROK_BOT_RESEARCHER_AGENT_ID`

## Secret scan (this turn)
Scanned provider sources, scripts, evidence, and work docs for gateway token /
API key material. No secret values written into repo or work artifacts.
