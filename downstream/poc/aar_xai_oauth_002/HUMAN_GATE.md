# HUMAN_GATE — AAR-xAI-OAuth-002

**Status:** `COMPLETED` / `PASSED`  
**Prior status:** `WAITING_FOR_USER_CONSENT`  
**Auto-consent:** forbidden / not performed by agent  
**`~/.grok/auth.json`:** PRESENT (mode 0600) — metadata only in evidence  
**PHASE 2–5:** completed  
**FINAL_CASE:** **A** (native inference PASS)

## What happened after the gate

1. Observed `auth.json` PRESENT + login waiter gone → treat user consent completed (no token values committed).
2. PHASE 2: session metadata (path/mode/auth_mode/issuer/expiry; presence flags only).
3. PHASE 3: official CLI `grok models` → logged in; models listed (`API_KEY_USED=false`).
4. PHASE 4: inference smoke via official `grok --single`/`-p` → exact `XAI_OAUTH_RESEARCHER_SMOKE_OK`; host class `cli_native`; model `grok-4.7`.
5. PHASE 5: capability matrix (MULTI_TURN / MACHINE_READABLE / TOOLS / SESSION_RESUME / NONINTERACTIVE / PROGRAMMATIC).
6. PHASE 6: `api.x.ai` OAuth = **NOT_TESTED_NOT_JUSTIFIED**.

## Non-goals (honored)

- No API key creation / Anthropic / Cursor / `aar/` edits / adapter / third-party OAuth bridge
- No secrets committed
