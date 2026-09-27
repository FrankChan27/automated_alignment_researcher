# OFFICIAL_SOURCE_MAP — AAR-xAI-OAuth-001

Access date: **2026-09-28** (UTC+8).

| # | URL | Kind | Key facts | Evidence grade |
|---|-----|------|-----------|----------------|
| 1 | https://docs.x.ai/developers/quickstart | OFFICIAL_DOCUMENTATION | Create account at console.x.ai; generate API key; `XAI_API_KEY`; `Authorization: Bearer` to `https://api.x.ai/v1/responses`. No OAuth login for public API. | OFFICIAL_DOCUMENTATION |
| 2 | https://docs.x.ai/developers/rest-api-reference/inference | OFFICIAL_DOCUMENTATION | Base `https://api.x.ai`; authenticate with Bearer API key. Management at `management-api.x.ai`. | OFFICIAL_DOCUMENTATION |
| 3 | https://docs.x.ai/developers/rest-api-reference/management/auth | OFFICIAL_DOCUMENTATION | API keys bound to teams; ACL strings for endpoints/models; create/list/rotate/delete keys. | OFFICIAL_DOCUMENTATION |
| 4 | https://docs.x.ai/build/overview | OFFICIAL_DOCUMENTATION | First launch opens browser for auth; headless use `XAI_API_KEY`. Same models also on API with API key. | OFFICIAL_DOCUMENTATION |
| 5 | https://docs.x.ai/build/enterprise | OFFICIAL_DOCUMENTATION | Hosts: `cli-chat-proxy.grok.com` (inference proxy), `auth.x.ai` (OAuth2/OIDC). Methods: Browser OIDC, device code, external auth provider, API key. Enterprise OIDC via `[auth.oidc]` / `GROK_OIDC_*`. | OFFICIAL_DOCUMENTATION |
| 6 | https://docs.x.ai/build/cli/reference | OFFICIAL_DOCUMENTATION | `grok login` / `--device-auth`; `grok logout`; `--oauth` flag; `grok mcp` for MCP servers. | OFFICIAL_DOCUMENTATION |
| 7 | https://docs.x.ai/build/features/mcp-servers | OFFICIAL_DOCUMENTATION | Remote MCP OAuth handled automatically; tokens under `~/.grok/mcp_credentials.json`. Outbound MCP auth ≠ xAI inference auth. | OFFICIAL_DOCUMENTATION |
| 8 | https://docs.x.ai/developers/tools/remote-mcp | OFFICIAL_DOCUMENTATION | Remote MCP tools on Responses API still called with `XAI_API_KEY`; optional auth header to MCP server. | OFFICIAL_DOCUMENTATION |
| 9 | https://docs.x.ai/build/settings/reference | OFFICIAL_DOCUMENTATION | `GROK_HOME` default `~/.grok`; `XAI_API_KEY`; `GROK_XAI_API_BASE_URL` default `https://api.x.ai/v1`. | OFFICIAL_DOCUMENTATION |
| 10 | https://docs.x.ai/grok/connectors | OFFICIAL_DOCUMENTATION | Grok.com connectors use OAuth to third-party services — not public API client OAuth. | OFFICIAL_DOCUMENTATION |
| 11 | https://auth.x.ai/.well-known/openid-configuration | Official AS discovery (live) | issuer `https://auth.x.ai`; auth/token/device endpoints; grants: authorization_code, refresh_token, device_code; PKCE S256; scopes include `api:access`, `grok-cli:access`. Snapshot: `evidence/auth_x_ai_openid_configuration.json`. | RUNTIME_OBSERVATION |
| 12 | https://raw.githubusercontent.com/xai-org/grok-build/main/crates/codegen/xai-grok-pager/docs/user-guide/02-authentication.md | OFFICIAL_SOURCE_CODE (xai-org) | Credentials `~/.grok/auth.json`; `grok login --oauth` → auth.x.ai; device-auth; API key fallback; enterprise OIDC; external auth provider; precedence rules. | OFFICIAL_SOURCE_CODE |
| 13 | https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-shell/README.md | OFFICIAL_SOURCE_CODE | Documents CLI chat proxy Bearer session + `X-XAI-Token-Auth: xai-grok-cli` header pattern for proxy calls. | OFFICIAL_SOURCE_CODE |

## Explicitly non-authoritative (cited only as contrast)

Third-party OAuth client reuse (Hermes/public client id blogs, typeclaw, pi-xai-oauth, grok-oauth-mcp, OpenClaw guides): **INFERENCE / unofficial**. Not used to claim official support.
