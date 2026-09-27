# REPORT — aar_xai_oauth_001

**FINAL_CASE: D**  
**CAN_XAI_OAUTH_AUTHENTICATE_RESEARCHER_INFERENCE:** `unknown`  
**HUMAN_GATE:** `REQUIRED` (`XAI_OAUTH_HUMAN_GATE=REQUIRED`)  
**XAI_OAUTH_AUTH_ONLY:** not PASS (no completed session / `auth.json`)  
**Tests completed:** 0,1,2,3 (gate),4=SKIPPED_NO_SESSION,5  

## Mission-authoritative CASE (user brief / coordinator)

| CASE | Meaning |
|------|---------|
| **C** | `XAI_OAUTH_AUTH_ONLY=PASS` — OAuth login 真实存在, but cannot prove programmatic inference we need |
| **D** | `XAI_OAUTH_HUMAN_GATE=REQUIRED` — official OAuth path exists, env not yet authorized, stop at consent (**not a failure**) |

This run has no completed session/`auth.json` → AUTH_ONLY is not PASS → **not C**.  
Human Gate without session → **FINAL_CASE=D**.

## One-line CASE
Official device-code OAuth at `auth.x.ai` exists and is startable (`grok login --device-auth`), but this environment is not yet authorized; stopped at consent Human Gate before any session inference proof.

## Evidence pointers
- `AUTH_SURFACE_MAP.md` — hosts, flows, stores, headers
- `evidence/TEST_0_inventory.txt`
- `evidence/TEST_1_public_discovery.txt` + `evidence/auth_x_ai_openid_configuration.json`
- `evidence/TEST_2_unauth_inference.txt` (all official probes HTTP 401)
- `evidence/TEST_3_device_code_start.txt` (URL host/path + user_code metadata; values redacted)
- `evidence/TEST_4_session_inference.txt` (SKIPPED_NO_SESSION)
- `evidence/TEST_5_aar_relevance.txt` (Anthropic hard-bind cites)

## HUMAN_GATE
- **Status:** REQUIRED  
- **Why:** Device-code flow requires user to open `accounts.x.ai/oauth2/device` and confirm code.  
- **Next human step:** Run `grok login --device-auth` → approve in browser → confirm `~/.grok/auth.json` present (metadata only) → re-run TEST 4.

## AAR-as-shipped note
Shipped AAR researcher loop still hard-binds Anthropic (`run.py` / `ClaudeSDKClient`); no non-patch xAI substitute found (TEST 5).

## Constraints honored
- Work only under `downstream/poc/aar_xai_oauth_001/`
- Branch `downstream/aar-xai-oauth-001`
- No `aar/` / `generic_aar/` edits
- No Cursor CloudAgent; no Anthropic; no xAI API key create/purchase; no auth/billing bypass
- HUMAN=0: did not complete browser login
- Secrets: no token/cookie/key values in evidence; `REPO_SECRET_WRITTEN=false`

## Correction log
Coordinator REJECT of FINAL_CASE=C (2026-09-28): restored mission CASE D. Did not invent alternate CASE ladder meanings.
