# FAILURE_RECOVERY — AAR-xAI-adapter-001 PHASE 6

Synthetic provider nonzero-exit (stub `grok` exits 42). OAuth session untouched.

| Field | Value |
|-------|-------|
| FAILURE_PROPAGATION_CORRECT | **true** — `ProviderError(code=GROK_CLI_NONZERO)` |
| LOOP_STATE_CORRUPTED | **false** — STATE.json unchanged during failure |
| RECOVERY_SUPPORTED | **true** — subsequent real `grok` CLI OIDC call returned `RECOVERY_OK` |
| OAUTH_INTACT | true |
| ANTHROPIC_USED | false |
| RESEARCHER_TRANSPORT | grok_cli_oidc |

Evidence: `evidence/FAILURE_RECOVERY.json`
