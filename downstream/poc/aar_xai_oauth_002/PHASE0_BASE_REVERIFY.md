# PHASE 0 — Base re-verify (from frozen oauth-001 docs on disk)

**Date:** 2026-09-28 (UTC+8)  
**Base SHA:** `c903de31eb7670bc1c855a031d392103eb32ac49` (`downstream/aar-xai-oauth-001` ancestor / branch point for `downstream/aar-xai-oauth-002`)  
**Source path:** `downstream/poc/aar_xai_oauth_001/` (read-only; no edits)

## Re-verified facts

| Fact | Value on disk | Source file |
|------|---------------|-------------|
| `FINAL_CASE` | **D** | `REPORT.md`, `provenance.json` |
| `CAN_XAI_OAUTH_AUTHENTICATE_RESEARCHER_INFERENCE` | **unknown** | same |
| `XAI_OAUTH_HUMAN_GATE` | **REQUIRED** | same |
| `HUMAN` | 0 (did not complete browser/device consent) | `REPORT.md` |
| Public API OAuth documented | **false** (API key Bearer only) | `OFFICIAL_SOURCE_MAP.md`, `provenance.json` TEST_0 |
| Grok Build / CLI OAuth documented | **true** (`auth.x.ai`, `grok login`, device-code) | `OFFICIAL_SOURCE_MAP.md` rows 4–6, 11–12 |
| Device-code command | `grok login --device-auth` (alias `--device-code`) | `AUTH_SURFACE_MAP.md` (tip lineage); CLI `login --help` this shift |
| Verify UI host | `accounts.x.ai` path `/oauth2/device` | `AUTH_SURFACE_MAP.md` / this shift runtime |
| Issuer | `https://auth.x.ai` | OIDC discovery evidence + docs |
| Token store path | `~/.grok/auth.json` | docs / AUTH_SURFACE_MAP |
| Session at end of oauth-001 | **ABSENT** | REPORT / provenance TEST_1 |
| Adapter / `aar/` edits | **forbidden / not done** | REPORT constraints |
| Third-party OAuth bridges | **non-authoritative; not used** | OFFICIAL_SOURCE_MAP explicit note |

## Note on tip vs base SHA

Mission BASE named `c903de31…`. Local branch `downstream/aar-xai-oauth-002` points at that SHA. Tip of `downstream/aar-xai-oauth-001` is later (`4c035dd…`, FINAL_CASE=D correction). Phase 0 facts above match frozen docs present at this base; CASE D semantics unchanged.

## Constraints carried forward

- Outputs only under `downstream/poc/aar_xai_oauth_002/`
- No Cursor / Anthropic / API key create / cookie auth / `aar/` edits / adapter
- Never print/commit secrets
