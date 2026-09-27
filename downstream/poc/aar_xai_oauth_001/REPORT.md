# AAR-xAI-OAuth-001 REPORT

**Date:** 2026-09-28 (UTC+8)  
**Branch:** `downstream/aar-xai-oauth-001`  
**Parent HEAD:** `71842398db939801bafcfe98a66dbeb922a15297`  
**HEAD_SHA:** `e9945a49e95f9d4909bd1a8b65268f597ebc86ce`  
**Mission:** Determine `CAN_XAI_OAUTH_AUTHENTICATE_RESEARCHER_INFERENCE` and `FINAL_CASE` ∈ {A..F}.

## Verdict

| Field | Value |
|-------|-------|
| `CAN_XAI_OAUTH_AUTHENTICATE_RESEARCHER_INFERENCE` | **unknown** |
| `FINAL_CASE` | **D** |
| `XAI_OAUTH_HUMAN_GATE` | **REQUIRED** |
| `HUMAN` | 0 |
| Phase 2 inference smoke | **not run** (A/B path not justified) |
| AAR provider adapter | **not implemented** (mission forbids) |

## Why CASE D

1. Local Grok/xAI **OAuth session ABSENT** (`~/.grok/auth.json` ABSENT; `XAI_API_KEY` ABSENT; `grok` CLI ABSENT).
2. Official **Grok Build / CLI** OAuth is documented (`auth.x.ai`, `grok login`, device-code) but acquiring a session needs **human browser or device consent**.
3. Mission hard rule: HUMAN=0 → set `XAI_OAUTH_HUMAN_GATE=REQUIRED` and **STOP** (CASE D). Do not automate login.
4. Official **public REST/Responses API** documents **API key** Bearer auth only — `PUBLIC_API_OAUTH_DOCUMENTED=false`. Do not reverse-engineer third-party OAuth-client reuse to claim public API OAuth support.
5. Therefore empirical answer for researcher inference via OAuth remains **unknown** until a human completes official OAuth (or supplies an existing session / key outside this mission).

## What Phase 1 established

- **TEST 0:** Grok Build + CLI OAuth documented; public API OAuth **not** documented; MCP OAuth documented only for **outbound** MCP servers.
- **TEST 1:** No portable OAuth credential on box; no xAI MCP; grok.com cookie domains present in chrome seed (**not** treated as researcher auth).
- Unauth probes: `api.x.ai/v1/models` and `cli-chat-proxy.grok.com/v1/models` → HTTP 401 (RUNTIME_OBSERVATION).
- OIDC discovery live at `auth.x.ai` with `api:access` + `grok-cli:access` scopes (RUNTIME_OBSERVATION ≠ official third-party API OAuth guide).

## Explicit non-claims

- Did **not** claim public API accepts Grok CLI OAuth tokens.
- Did **not** use Grok Bot host identity / web cookies as API credentials.
- Did **not** create/buy xAI API keys; no Anthropic; no Cursor; no AAR-POC-002 agent continuation; no edits under `aar/` or `generic_aar/`.

## Outputs

- `AUTH_SURFACE_MAP.md`, `OFFICIAL_SOURCE_MAP.md`, `CASE_LADDER.md`, `TEST_MATRIX.md`
- `evidence/` (metadata only; no tokens/cookies/keys)
- `provenance.json`
