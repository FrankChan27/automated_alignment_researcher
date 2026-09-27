# HUMAN_GATE — AAR-xAI-OAuth-002

**Status:** `WAITING_FOR_USER_CONSENT` (not a failure)  
**Auto-consent:** forbidden / not performed  
**`~/.grok/auth.json`:** ABSENT  
**PHASE 2–5:** not started

## What we did
1. **PHASE0:** Re-verified oauth-001 CASE D facts on disk; confirmed current official install method from docs.x.ai; official Grok CLI `1.0.41` present at `~/.grok/bin/grok` (symlink `~/.local/bin/grok`).
2. **PHASE1:** Started `grok login --device-auth`. CLI is **waiting for authorization**. Login was **not** completed by the agent.

## What Human must do (consent)
1. On the box, if a `grok login --device-auth` process is still waiting, read its printed verification URL + user code from that process stdout (e.g. `/tmp/grok_oauth002_live.out`) — codes are **not** stored in git.
2. If expired: run `export PATH="$HOME/.grok/bin:$PATH" && grok login --device-auth` and use the new printed URL/code.
3. Open host `accounts.x.ai` path `/oauth2/device` (param name `user_code` only; do not paste codes into the repo).
4. Confirm the code in the browser (only a code you requested). Finish xAI sign-in/consent screens.
5. Tell the Bot/coordinator when the browser shows success — next shift checks `auth.json` metadata only (PRESENT/expiry names), never token values.
6. Do **not** start PHASE 2–5 until the coordinator opens the next gate.

## Evidence (redacted)
- `PHASE0_BASE_REVERIFY.md`, `PHASE1_AUTH_STARTED.md`
- `evidence/PHASE0_install.txt`, `evidence/CLI_INSTALL_RECORD.txt`, `evidence/OFFICIAL_INSTALL_SOURCE.txt`
- `evidence/PHASE1_device_auth_start.txt`, `evidence/device_auth_started_redacted.txt`, `evidence/device_auth_url_meta.json`

## Non-goals
- No API key creation / Anthropic / Cursor / `aar/` edits / adapter / third-party OAuth bridge
- No secrets committed
