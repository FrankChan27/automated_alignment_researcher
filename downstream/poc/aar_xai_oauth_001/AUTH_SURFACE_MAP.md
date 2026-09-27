# AUTH_SURFACE_MAP — AAR-xAI-OAuth-001

Access date: **2026-09-28** (UTC+8). Grades: OFFICIAL_DOCUMENTATION | OFFICIAL_SOURCE_CODE | RUNTIME_OBSERVATION | INFERENCE.

## Surfaces (do not conflate)

| Surface | Host / path | Documented auth | OAuth? | Researcher-usable without reverse-engineering? | Grade |
|---------|-------------|-----------------|--------|-----------------------------------------------|-------|
| Public Inference / Responses API | `https://api.x.ai` (`/v1/responses`, chat, models, …) | `Authorization: Bearer <API_KEY>`; keys from console.x.ai | **Not documented** as OAuth for third-party/public clients | Yes via **API key only** (creating keys forbidden in this mission) | OFFICIAL_DOCUMENTATION |
| Management API | `https://management-api.x.ai` | Management / API keys (Bearer) | No (key management, not end-user OAuth login for inference) | N/A for researcher inference | OFFICIAL_DOCUMENTATION |
| Grok Build CLI session | `cli-chat-proxy.grok.com` | Browser OIDC / device-code / enterprise OIDC / external auth provider / `XAI_API_KEY` fallback; session in `~/.grok/auth.json` | **Yes** via `auth.x.ai` (`grok login`) | Only if CLI session present; CLI absent on this box | OFFICIAL_DOCUMENTATION + OFFICIAL_SOURCE_CODE |
| SpaceXAI OAuth/OIDC AS | `https://auth.x.ai` | Authorization Code+PKCE, refresh_token, device_code; scopes include `api:access`, `grok-cli:access` | Yes (AS itself) | Discovery public; **no** public third-party client registration console documented | RUNTIME_OBSERVATION (discovery) + OFFICIAL_DOCUMENTATION (enterprise/CLI) |
| Grok Build MCP client OAuth | `~/.grok/mcp_credentials.json` | OAuth **to third-party MCP servers** (e.g. Linear), not xAI inference auth | Yes (outbound MCP) | Irrelevant to authenticating xAI researcher inference | OFFICIAL_DOCUMENTATION |
| Public API Remote MCP tools | `api.x.ai` tools `type=mcp` | Caller still uses `XAI_API_KEY`; optional `authorization` header **to the MCP server** | MCP-server OAuth ≠ xAI OAuth | API key still required for xAI call | OFFICIAL_DOCUMENTATION |
| Grok.com web / Connectors | grok.com | Account OAuth for connectors | Web account | **Must not conflate** with public API OAuth | OFFICIAL_DOCUMENTATION |
| Grok Bot host (this agent) | MCP: Slack, GitHub only | Platform identity | N/A | **Not** a portable xAI OAuth credential for AAR | RUNTIME_OBSERVATION |

## TEST 0 documentation flags

| Field | Value | Rationale |
|-------|-------|-----------|
| `PUBLIC_API_OAUTH_DOCUMENTED` | **false** | docs.x.ai quickstart + inference reference document API key Bearer only for `api.x.ai`. No official “register OAuth client → call Responses API” guide found. |
| `GROK_BUILD_OAUTH_DOCUMENTED` | **true** | docs.x.ai/build/enterprise + overview: Browser OIDC / device-code via `auth.x.ai`. |
| `CLI_OAUTH_DOCUMENTED` | **true** | `grok login` / `--device-auth` / `--oauth` in docs.x.ai/build/cli/reference + grok-build auth user guide. |
| `MCP_OAUTH_DOCUMENTED` | **true** *(outbound only)* | docs.x.ai/build/features/mcp-servers: OAuth for **MCP servers Grok connects to**; tokens in `mcp_credentials.json`. **Not** “MCP OAuth authenticates xAI inference.” |

## Auth precedence (Grok Build CLI) — official

1. Per-model `api_key` / `env_key`
2. Active session token (`~/.grok/auth.json` from OAuth/OIDC/external)
3. `XAI_API_KEY` fallback

Login flow precedence when multiple configured: external auth provider → enterprise OIDC → SpaceXAI OAuth2 browser.

## Critical distinction

- **Grok account / Grok Build OAuth** (auth.x.ai → CLI proxy session) ≠ **public API authentication** (console API keys → `api.x.ai`).
- OIDC `scopes_supported` includes `api:access` (RUNTIME_OBSERVATION). That alone is **not** OFFICIAL_DOCUMENTATION that third-party AAR researcher adapters may use OAuth tokens against `api.x.ai`. Claiming such support from third-party repos would be INFERENCE / reverse-engineering — forbidden for a “supported” claim.
