# AAR-xAI-OAuth-002 REPORT

**Date:** 2026-09-28 (UTC+8)  
**Branch:** `downstream/aar-xai-oauth-002`  
**POC:** `downstream/poc/aar_xai_oauth_002`  
**BASE_SHA:** `c903de31eb7670bc1c855a031d392103eb32ac49`  
**Prior:** oauth-001 FINAL_CASE=D (human gate); this mission completed consent + PHASE 2–5.

## Verdict

| Field | Value |
|-------|-------|
| `FINAL_CASE` | **A** |
| Meaning (002 ladder) | Native inference **PASS** |
| `CAN_XAI_OAUTH_AUTHENTICATE_RESEARCHER_INFERENCE` | **true** (official Grok CLI + local OIDC session) |
| `SMOKE_EXACT_MATCH` | **true** |
| `SMOKE_HOST_CLASS` | `cli_native` |
| `SMOKE_MODEL` | `grok-4.7` |
| `API_KEY_USED` | **false** |
| `AUTH_JSON_PRESENT` | **true** (mode 0600; auth_mode=oidc) |
| `HUMAN_GATE` | **COMPLETED** / **PASSED** |
| `CONSENT_COMPLETED` | **true** |
| `API_XAI_OAUTH` | **NOT_TESTED_NOT_JUSTIFIED** |
| AAR provider adapter | **not implemented** (forbidden) |

## Why CASE A

1. Local OAuth session **PRESENT** (`~/.grok/auth.json` mode 0600; `auth_mode=oidc`; not expired at probe; login waiter gone).
2. Official CLI auth probe: `grok models` exit 0; "logged in with grok.com."; default `grok-4.7`.
3. Inference smoke via official CLI returned **exactly** `XAI_OAUTH_RESEARCHER_SMOKE_OK` (`API_KEY_USED=false`).
4. Not D (gate no longer pending). Not B (inference not blocked). Not C (login succeeded). Capability UNKNOWNs for unsmoked multi-turn/tools/resume do not demote past A. Not F: adapter not claimed/implemented; public `api.x.ai` OAuth untested.

## Phase summary

| Phase | Result |
|-------|--------|
| 0–1 | Official grok 1.0.41; device-auth started; human consent completed |
| 2 | Session metadata (no secret / PII values) |
| 3 | `grok models` PASS |
| 4 | Smoke exact match; host `cli_native`; model `grok-4.7` |
| 5 | Capabilities: NONINTERACTIVE/PROGRAMMATIC/MACHINE_READABLE SUPPORTED; MULTI_TURN/TOOLS/SESSION_RESUME documented (runtime not re-smoked) |
| 6 | `api.x.ai` OAuth NOT_TESTED_NOT_JUSTIFIED |

## Explicit non-claims / constraints honored

- No token/refresh/JWT/cookie/API-key **values** in evidence or commits.
- No email/user_id/team_id **values** in committed evidence.
- No hand-stuffed Bearer into `api.x.ai`.
- No `aar/` or `generic_aar` edits; no Cursor; no Anthropic; no xAI API key create; no adapter.

## Outputs

- `OAUTH_RUNTIME_MAP.md`, `SESSION_CAPABILITY.md`, `TEST_MATRIX.md`, `CASE_LADDER.md`, `REPORT.md`
- `STATUS.json`, `HUMAN_GATE.md`, `provenance.json`
- `evidence/*` (incl. `SECRET_SCAN.txt`)
