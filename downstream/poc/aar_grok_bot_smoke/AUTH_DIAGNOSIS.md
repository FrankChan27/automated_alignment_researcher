# AUTH_DIAGNOSIS

## Mechanism
`AUTH_MECHANISM=grok_bot_sand_gateway_bearer`

Local sand gateway Bearer token loaded from `/home/box/agent-data/gateway.json`
(key `token`). Sent only as `Authorization: Bearer <token>` on gateway HTTP calls.
Token value is never logged, printed, or written into evidence/errors.

## Flags
| Flag | Value |
|------|-------|
| OAUTH_USED | false |
| XAI_API_KEY_USED | false |
| ANTHROPIC_USED | false |
| GATEWAY_JSON_PRESENT | true |
| TOKEN_PRESENT | true (length withheld) |
| RESEARCHER_AGENT_ID | fac98a36-f560-43b8-9ac8-1ddacbbd16ed |

## Proven calls (redacted)
1. `POST /api/listAgents` → 200, list including researcher (`isRunningTurn` readable)
2. `POST /api/sendPrompt` → 200 `{"accepted": true}`
3. `POST /api/openAgent` → 200 transcript list; user `kind=message` + assistant `kind=send-message`
4. Provider probe reply exact: `GROK_BOT_AAR_PROVIDER_OK`

## Not used
- OAuth / OIDC / `~/.grok/auth.json`
- `XAI_API_KEY`
- `ANTHROPIC_API_KEY` / Claude SDK
- Cursor Cloud Agent
