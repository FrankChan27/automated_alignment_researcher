# TEST_MATRIX — AAR-xAI-OAuth-002

Date: 2026-09-28 (UTC+8)

| Phase / Test | Purpose | Result | Evidence |
|--------------|---------|--------|----------|
| **0** | Reverify oauth-001 CASE D + official CLI install | DONE | `PHASE0_BASE_REVERIFY.md`, `evidence/PHASE0_install.txt`, `evidence/CLI_INSTALL_RECORD.txt` |
| **1** | Start official device-auth; Human Gate | DONE → consent completed | `PHASE1_AUTH_STARTED.md`, `HUMAN_GATE.md` (updated) |
| **2** | Session metadata only (no secret decode) | **PASS** PRESENT mode 0600 oidc | `evidence/PHASE2_session_metadata.txt`, `evidence/phase2_session_metadata.json` |
| **3** | Official CLI auth probe (`grok models`) | **PASS** logged in; models listed | `evidence/PHASE3_grok_models.txt` |
| **4** | ≤1 inference smoke exact token | **PASS** `XAI_OAUTH_RESEARCHER_SMOKE_OK` | `evidence/PHASE4_inference_smoke.txt` |
| **5** | Capability matrix | DONE (some UNKNOWN_NOT_SMOKED) | `SESSION_CAPABILITY.md`, `evidence/PHASE5_*` |
| **6** | api.x.ai OAuth | **NOT_TESTED_NOT_JUSTIFIED** | `OAUTH_RUNTIME_MAP.md` |

## Key field block

```
AUTH_JSON_PRESENT=true
CONSENT_COMPLETED=true
HUMAN_GATE=COMPLETED
API_KEY_USED=false
XAI_API_KEY_CREATED=false
SMOKE_EXACT=true
HOST_CLASS=cli_native
MODEL=grok-4.7
FINAL_CASE=A
CAN_XAI_OAUTH_AUTHENTICATE_RESEARCHER_INFERENCE=true
API_XAI_OAUTH=NOT_TESTED_NOT_JUSTIFIED
AAR_EDITED=false
ADAPTER_IMPLEMENTED=false
CURSOR_USED=false
ANTHROPIC_USED=false
```
