# AUTH_SURFACE_MAP — aar_xai_oauth_001

Research question: `CAN_XAI_OAUTH_AUTHENTICATE_RESEARCHER_INFERENCE`  
Date: 2026-09-28 (UTC+8)  
Branch: `downstream/aar-xai-oauth-001`  
Scope path: `downstream/poc/aar_xai_oauth_001/` only

## CASE definitions (mission-authoritative; coordinator / user brief)

Do **not** invent alternate C/D meanings here. Authoritative for this mission:

| CASE | Meaning |
|------|---------|
| **C** | `XAI_OAUTH_AUTH_ONLY=PASS` — OAuth login 真实存在, but cannot prove programmatic inference we need |
| **D** | `XAI_OAUTH_HUMAN_GATE=REQUIRED` — official OAuth path exists, env not yet authorized, stop at consent (**not a failure**) |

Other letters A/B/E/F remain as mission-wide ladder labels if/when coordinator supplies them; this run only adjudicates C vs D.

**Final CASE for this run: D** (see REPORT.md / STATUS.json).

`CAN_XAI_OAUTH_AUTHENTICATE_RESEARCHER_INFERENCE` = **unknown**.  
`HUMAN_GATE` = **REQUIRED**. `XAI_OAUTH_AUTH_ONLY` = not PASS (no `auth.json` / completed session).

---

## Hosts / endpoints

| Host | Role | Notes |
|------|------|-------|
| `auth.x.ai` | SpaceXAI OAuth / OIDC issuer | `/.well-known/openid-configuration` HTTP 200; device + auth code + refresh |
| `accounts.x.ai` | User-facing sign-in / device verify UI | Device verification URL host from `grok login --device-auth` |
| `api.x.ai` | Public inference API (`/v1/responses`, `/v1/chat/completions`, `/v1/models`) | Docs Quick Start: `Authorization: Bearer $XAI_API_KEY`; unauth → 401 `unauthenticated:no-credentials` |
| `cli-chat-proxy.grok.com` | Grok Build / CLI chat proxy (`/v1/...`) | Unauth → 401; `WWW-Authenticate` mentions Bearer + `x_xai_token_auth` |
| `console.x.ai` | API key console | Key creation **forbidden** by this mission |
| `docs.x.ai` | Public docs | Build overview + API quickstart; dedicated `/docs/authentication` slug 404 |
| `x.ai/cli` | CLI install | `curl …/install.sh` or npm `@xai-official/grok` |

---

## Auth flows

### 1) Browser OIDC / OAuth (default CLI)
- Command: `grok` first launch or `grok login` / `grok login --oauth`
- Issuer: `https://auth.x.ai`
- Authorize: `https://auth.x.ai/oauth2/authorize` (PKCE S256)
- Stores session: `~/.grok/auth.json` (mode 0600); auto-refresh
- **HUMAN_GATE**: requires interactive browser user confirmation

### 2) Device-code (headless / remote) — exercised TEST 3
- Command: `grok login --device-auth` (alias `--device-code`)
- Device endpoint: `https://auth.x.ai/oauth2/device/code`
- Token endpoint: `https://auth.x.ai/oauth2/token`
- Grant: `urn:ietf:params:oauth:grant-type:device_code`
- Verify UI: `https://accounts.x.ai/oauth2/device?user_code=…`
- This host: flow **started**; printed verification URL + user_code; waiting for authorization → **HUMAN_GATE=true**, login **not** completed
- Scopes from OIDC discovery include: `openid`, `profile`, `email`, `offline_access`, `grok-cli:access`, `api:access`, plus team/org/billing/api-keys scopes

### 3) Enterprise OIDC (customer IdP)
- Config: `~/.grok/config.toml` `[grok_com_config.oidc]` or `GROK_OIDC_ISSUER` + `GROK_OIDC_CLIENT_ID`
- Default scopes (docs): `openid profile email offline_access api:access`
- Redirect: loopback `http://127.0.0.1/callback`
- Optional proxy: `GROK_CLI_CHAT_PROXY_BASE_URL`

### 4) External auth provider
- `auth_provider_command` prints token on stdout; used for CI/SSO wrappers
- Not exercised

### 5) API key
- Env: `XAI_API_KEY` from `console.x.ai`
- Precedence: **lowest** vs active session in `auth.json` (session wins)
- **Mission forbids creating/purchasing keys** → unavailable here (`ABSENT`)

---

## Token store paths (paths only; never values)

| Path | Purpose |
|------|---------|
| `~/.grok/auth.json` | Primary OAuth/session tokens (`access_token`, `refresh_token`, expiry metadata) |
| `~/.grok/mcp_credentials.json` | MCP OAuth tokens |
| `~/.grok/config.toml` | Config including OIDC / auth_provider / models |
| `$GROK_HOME/…` | Alternate home when `GROK_HOME` set (TEST 3 used `/tmp/grok_home_test3`; `auth.json` ABSENT) |

Field **names** expected (from official auth guide / binary strings): `access_token`, `refresh_token`, `expires_in` / expiry, optional `issuer`, `id_token`.

---

## Inference endpoints & required headers (names only)

| Endpoint | Auth header names | Notes |
|----------|-------------------|-------|
| `https://api.x.ai/v1/responses` | `Authorization` (Bearer) | Public API; docs show API key; session token portability **unproven** this run (no session) |
| `https://api.x.ai/v1/chat/completions` | `Authorization` (Bearer) | Same |
| `https://cli-chat-proxy.grok.com/v1/chat/completions` | `Authorization` (Bearer); error text references `x_xai_token_auth` | CLI/Build path; binary strings also show header name `X-XAI-Token-Auth` |
| `https://cli-chat-proxy.grok.com/v1/responses` | same | Unauth 401 confirmed |

---

## Precedence (official CLI docs)

**Per request credential resolution (highest → lowest):**
1. Per-model `api_key` / `env_key` in `config.toml`
2. Active session token in `~/.grok/auth.json` (browser / OIDC / external provider)
3. `XAI_API_KEY` fallback

**Login-flow population order when multiple configured:**
1. External auth provider
2. Enterprise OIDC
3. SpaceXAI OAuth2 browser (default)

---

## Billing / entitlement notes

- Public docs market API usage via API keys + console billing.
- OIDC scopes include `billing:read` / `billing:write` and `api:access` / `grok-cli:access` — suggests subscription/CLI entitlement may gate what a session can call.
- Third-party writeups claim SuperGrok / X Premium+ OAuth can call `api.x.ai` without API key; **not verified here** (HUMAN_GATE before tokens).
- Do not bypass billing; do not mint keys.

---

## Local inventory snapshot (TEST 0)

- `XAI_API_KEY` / `GROK_*`: **ABSENT**
- `~/.grok/auth.json`: **ABSENT**
- `grok` CLI initially ABSENT; TEST 3 staged official `@xai-official/grok-linux-x64@1.0.41` binary under `/tmp/grok_cli/bin/grok` (not committed)

---

## AAR researcher loop gap (TEST 5)

Shipped AAR agent loop hard-binds `ANTHROPIC_API_KEY` + `ClaudeSDKClient` (`run.py`, `aar/research_loop/agent.py`). Policy forbids patching `aar/`. No official non-patch path to substitute xAI OAuth session into that loop. Separate from raw xAI OAuth→inference question.
