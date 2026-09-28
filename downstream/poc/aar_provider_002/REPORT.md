# REPORT — AAR-provider-002

## Core question

**CAN_AAR_LOAD_EXTERNAL_RESEARCHER_PROVIDER_WITHOUT_VENDOR_KNOWLEDGE = true**

**PROVIDER_ARCHITECTURE = VENDOR_NEUTRAL**

Suggested **FINAL_CASE = A** (implementer suggestion only — Reviewer decides in PHASE 8).

## What closed adapter-001 nits

| Nit | Attack | Resolution |
|-----|--------|------------|
| #8 | grok aliases / `AAR_GROK_*` / default `aar_xai_adapter_001` in core; name-match auth/MCP | Core purge: `CORE_VENDOR_REFERENCES=0`. Generic `AAR_AGENT_PROVIDER_MODULE` loader. Capability flags `requires_anthropic_key` / `supports_inprocess_mcp`. |
| #10 | Deletion import-only overclaim | LIVE deletion: baseline enters `AutonomousAgentLoop.run()`, then delete, same harness fails. |

## Results

| Field | Value |
|-------|-------|
| CORE_VENDOR_KNOWLEDGE_GONE | true |
| GENERIC_LOADER | true |
| EXTERNAL_PROVIDER_PATH | `downstream/poc/aar_provider_002/providers/grok_cli.py` |
| SESSIONS | 6 (TRACE) |
| HASH_CHAIN_OK | true |
| LIVE_DELETION_A | true (`UPSTREAM_LOOP_DELETION_BREAKS_RUN`) |
| LIVE_DELETION_B | true (`EXTERNAL_PROVIDER_DELETION_BREAKS_RUN`) |
| RENAME_ENV_ONLY | PASS |
| SECRET_SCAN | hits=0 / OAUTH_SECRET_IN_REPO=false |
| RESEARCHER_TRANSPORT | grok_cli_oidc |
| ANTHROPIC_USED | false |
| API_KEY_USED | false |
| CURSOR_USED | false |
| HUMAN | 0 |
| stop_reason (LOOP_RESULT) | max_iterations |

## Key evidence paths

- `evidence/CORE_VENDOR_SCAN.txt` / `CORE_GROK_SCAN.txt`
- `evidence/ITERATION_TRACE.jsonl` / `LOOP_RESULT.json` / `LOOP_5ITER.txt`
- `evidence/deletion_A.txt` / `deletion_B.txt` / `LIVE_DELETION_PROOF.md`
- `evidence/rename_proof.txt` / `PROVIDER_RENAME_PROOF.md`
- `evidence/SECRET_SCAN.txt` / `RESEARCHER_TRANSPORT_CONFIRM.txt`
- `CORE_PATCH.diff` / `COMPATIBILITY_REGRESSION.md`

## Non-goals preserved

- AutonomousAgentLoop scheduler / stop policy / eval / objective not rewritten
- oauth-001/002 untouched; no secrets printed/committed
- adapter-001 evidence not mutated
