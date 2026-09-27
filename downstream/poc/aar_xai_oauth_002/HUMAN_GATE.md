# HUMAN_GATE — AAR-xAI-OAuth-002

**Status:** REQUIRED (not a failure)  
**Auto-consent:** forbidden / not performed  
**`~/.grok/auth.json`:** ABSENT  

## What we did
1. **PHASE0:** Installed official Grok CLI via `https://x.ai/cli/install.sh` → `grok 1.0.41` at `~/.local/bin/grok`.
2. **PHASE1:** Started `grok login --device-auth`. CLI is **waiting for authorization**. Login was **not** completed by the agent.

## What Human must do (consent)
1. Open the verification URL shown in chat (host `accounts.x.ai`, path `/oauth2/device`).
2. Confirm the **user code** shown in the same chat message (only a code you requested).
3. Finish any xAI account sign-in / consent screens in the browser.
4. Tell this Bot (or coordinator) when the browser shows success — we will check `auth.json` metadata only (PRESENT/TYPE/EXPIRY), never print token values.

## Evidence (redacted)
- `evidence/PHASE0_install.txt`
- `evidence/PHASE1_device_auth_start.txt` (user_code redacted)

## Non-goals
- No API key creation
- No Anthropic
- No `aar/` / `generic_aar/` edits
- No secrets committed
