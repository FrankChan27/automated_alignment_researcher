# REPORT — aar_xai_oauth_001

**CASE: C**  
**CAN_XAI_OAUTH_AUTHENTICATE_RESEARCHER_INFERENCE:** `null` (unknown; CASE C — Human Gate)  
**HUMAN_GATE:** `true`  
**Tests completed:** 0,1,2,3 (gate),4=SKIPPED_NO_SESSION,5  

## One-line CASE
Official device-code OAuth at `auth.x.ai` is real and startable via `grok login --device-auth`, but this host cannot finish without interactive browser confirmation — stopped at Human Gate before any session inference proof.

## Evidence pointers
- `AUTH_SURFACE_MAP.md` — hosts, flows, stores, headers, CASE defs
- `evidence/TEST_0_inventory.txt`
- `evidence/TEST_1_public_discovery.txt` + `evidence/auth_x_ai_openid_configuration.json`
- `evidence/TEST_2_unauth_inference.txt` (all official probes HTTP 401)
- `evidence/TEST_3_device_code_start.txt` (URL host/path + user_code metadata; values redacted)
- `evidence/TEST_4_session_inference.txt` (SKIPPED_NO_SESSION)
- `evidence/TEST_5_aar_relevance.txt` (Anthropic hard-bind cites)
- `evidence/REF_official_02-authentication.md` (CLI bundled auth guide)

## HUMAN_GATE
- **Status:** true  
- **Why:** Device-code flow requires user to open `accounts.x.ai/oauth2/device` and confirm code.  
- **Next human step:** Run `grok login --device-auth` on an allowed host → approve in browser → confirm `~/.grok/auth.json` present (metadata only) → re-run TEST 4 inference with Bearer from file (no echo) against `api.x.ai` and/or `cli-chat-proxy.grok.com`.

## AAR-as-shipped note
Even after a future CASE A for raw xAI OAuth→inference, shipped AAR researcher loop still hard-binds Anthropic (`run.py` / `ClaudeSDKClient`); substituting xAI without patching `aar/` was **not** found. That alone would keep CAN false for *AAR researcher inference as shipped* unless an official non-patch path appears.

## Constraints honored
- Work only under `downstream/poc/aar_xai_oauth_001/`
- Branch `downstream/aar-xai-oauth-001` (verified)
- No `aar/` / `generic_aar/` edits
- No Cursor CloudAgent; no Anthropic; no xAI API key create/purchase; no auth/billing bypass
- HUMAN=0: did not complete browser login
- Secrets: no token/cookie/key values in evidence (user_code redacted); `REPO_SECRET_WRITTEN=false`
