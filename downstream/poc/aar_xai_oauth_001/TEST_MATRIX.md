# TEST_MATRIX — AAR-xAI-OAuth-001

Date: 2026-09-28 (UTC+8)

| Test | Purpose | Result | Evidence | Notes |
|------|---------|--------|----------|-------|
| **0** | Docs flags | DONE | AUTH_SURFACE_MAP.md, OFFICIAL_SOURCE_MAP.md | PUBLIC_API_OAUTH_DOCUMENTED=false; GROK_BUILD_OAUTH_DOCUMENTED=true; CLI_OAUTH_DOCUMENTED=true; MCP_OAUTH_DOCUMENTED=true (outbound MCP only) |
| **1** | Local credential + MCP discovery (metadata only) | DONE | evidence/test1_local_discovery.txt, evidence/TEST_0_inventory.txt, evidence/test1_mcp_status.txt, evidence/test1_browser_cookie_domains_meta.txt | XAI_OAUTH_CREDENTIAL_PRESENT=false; grok CLI ABSENT; MCP xAI ABSENT; grok.com cookie domains PRESENT (not usable as API/CLI OAuth) |
| **1b** | Public discovery / unauth probes | DONE | evidence/TEST_1_public_discovery.txt, evidence/auth_x_ai_openid_configuration.json | OIDC 200; api.x.ai/v1/models → 401 unauthenticated; cli-chat-proxy/v1/models → 401 |
| **2** | Authenticated account/models metadata | **SKIPPED** | — | Not justified: no OAuth session / API key; would require human OAuth → CASE D |
| **3** | Token scope/audience metadata (safe) | **SKIPPED** | — | No token present; TOKEN_SCOPE_KNOWN=false; TOKEN_AUDIENCE_KNOWN=false |
| **4** | Authenticated lightweight API (non-inference) | **SKIPPED** | — | Same gate |
| **5** | ≤1 inference smoke (`XAI_OAUTH_RESEARCHER_SMOKE_OK`) | **SKIPPED** | — | A/B path not justified |

## TEST 1 field block

```
XAI_OAUTH_CREDENTIAL_PRESENT=false
CREDENTIAL_SOURCE=none
CREDENTIAL_TYPE=ABSENT
TOKEN_SCOPE_KNOWN=false
TOKEN_AUDIENCE_KNOWN=false
GROK_CLI_PRESENT=false
XAI_API_KEY_ENV=ABSENT
MCP_XAI_SERVER_PRESENT=false
GROK_WEB_COOKIE_DOMAINS_PRESENT=true
```
