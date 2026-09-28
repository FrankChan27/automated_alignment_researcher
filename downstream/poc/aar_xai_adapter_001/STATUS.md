# AAR-xAI-adapter-001

Status: **PHASE 2 done** (SEAM_PLACEMENT) — ready for PHASE 3 implementation

| Field | Value |
|-------|-------|
| PHASE | 2 |
| PHASES_COMPLETE | 0, 1, 2 |
| BASE_SHA | 00ba33b51d6b78cbb0844268fc437d64cd6e0c31 |
| PINNED_UPSTREAM_SHA | 02dbe9d2cadc553720d17cdf6259c0b8727e6cde |
| BRANCH | downstream/aar-xai-adapter-001 |
| CLAUDE_COUPLING_DEPTH | DEEP |
| PROVIDER_INTERFACE_EXISTS | false (pre-implement) |
| MIN_PROVIDER_SEAM | contracted + placement locked |
| UPSTREAM_SEMANTICS_PRESERVED | design-intent yes |
| GROK_PROVIDER_RUNTIME | planned_grok_cli_oidc (downstream module) |
| CORE_SEAM_PATH | aar/research_loop/provider.py (+ BaseAgent/run.py unbind) |
| GROK_BACKEND_PATH | downstream/poc/aar_xai_adapter_001/provider/grok_cli.py |
| READY_FOR_UPSTREAM_LOOP_VIA_GROK_CLI | false |
| CAN_AAR_NATIVE_RESEARCH_LOOP_RUN_WITH_XAI_OAUTH | unknown |
| MAP | CLAUDE_COUPLING_MAP.md |
| CONTRACT | MIN_PROVIDER_CONTRACT.md |
| PLACEMENT | SEAM_PLACEMENT.md |
| HUMAN | 0 |

Next: PHASE 3 implement (core unbind + downstream grok_cli).
