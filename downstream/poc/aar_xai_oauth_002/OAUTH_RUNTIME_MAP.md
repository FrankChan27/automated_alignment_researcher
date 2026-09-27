# OAUTH_RUNTIME_MAP — AAR-xAI-OAuth-002

**Date:** 2026-09-28 (UTC+8)  
**CLI:** grok 1.0.41 (`/home/box/.grok/bin/grok`)  
**API_KEY_USED:** false

## Local session (PHASE 2)

| Field | Value |
|-------|-------|
| `AUTH_JSON_PRESENT` | **true** |
| path | `/home/box/.grok/auth.json` |
| mode | `0600` |
| size_bytes | 1764 |
| mtime (UTC+8) | 2026-09-28T02:14:29+08:00 |
| session_host_class | `https://auth.x.ai` |
| auth_mode | `oidc` |
| oidc_issuer | `https://auth.x.ai` |
| principal_type | `User` |
| create_time (UTC) | 2026-09-27T18:14:29Z |
| expires_at (UTC) | 2026-09-28T00:14:29Z |
| expires_at (UTC+8) | 2026-09-28T08:14:29+08:00 |
| expired_at_probe | **false** |
| token_type field | ABSENT |
| scope field | ABSENT / `SCOPE_UNKNOWN` |
| audience field | ABSENT |
| HAS_KEY | true (value not recorded) |
| HAS_REFRESH_TOKEN | true (value not recorded) |
| login_waiter | **gone** (consent treated completed) |

Evidence: `evidence/PHASE2_session_metadata.txt`, `evidence/phase2_session_metadata.json`

## Official CLI authenticated probe (PHASE 3)

| Probe | Result |
|-------|--------|
| `grok models` | **PASS** exit 0 |
| Login banner | "You are logged in with grok.com." |
| Default model | `grok-4.7` |
| Available | grok-4.7, grok-4.7-build-fast, grok-4.6, grok-4.5 |
| Method | Official CLI reads local OAuth session — **not** hand-stuffed Bearer to `api.x.ai` |

Evidence: `evidence/PHASE3_grok_models.txt`

## Inference smoke (PHASE 4) — ONE call

| Field | Value |
|-------|-------|
| Host class | **cli_native** (Grok Build CLI / grok.com surface) |
| Model | `grok-4.7` |
| `API_KEY_USED` | **false** |
| Command family | `grok --single … --verbatim --model grok-4.7 --max-turns 1 --permission-mode dontAsk …` |
| Expected | `XAI_OAUTH_RESEARCHER_SMOKE_OK` |
| Got exact | **true** |
| exit_code | 0 |

Evidence: `evidence/PHASE4_inference_smoke.txt`

## api.x.ai OAuth (PHASE 6)

| Field | Value |
|-------|-------|
| Result | **NOT_TESTED_NOT_JUSTIFIED** |
| Rationale | Mission forbids hand-stuffing Bearer into `api.x.ai`. Official public REST docs use API-key Bearer only (`PUBLIC_API_OAUTH_DOCUMENTED=false` per oauth-001 OFFICIAL_SOURCE_MAP). No new official evidence this shift justifying CLI OIDC token reuse against public `api.x.ai`. |

## Runtime surfaces exercised

1. **auth.x.ai** — OIDC session stored locally (device-code consent completed by human).
2. **Grok CLI native inference** — authenticated via session file; smoke PASS.
3. **api.x.ai** — not called with OAuth token this POC.
