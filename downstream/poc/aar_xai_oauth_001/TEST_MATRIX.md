# TEST_MATRIX — aar_xai_oauth_001 (aligned to mission ladder)

Date: 2026-09-28 (UTC+8). Authoritative table: `LADDER.md`.

| Test | Purpose | Result | Evidence |
|------|---------|--------|----------|
| **0** | Local inventory (env/CLI/auth.json metadata) | DONE | `evidence/TEST_0_inventory.txt` (+ early `test1_local_discovery.txt`) |
| **1** | Public discovery / OIDC / docs | DONE | `evidence/TEST_1_public_discovery.txt`, `auth_x_ai_openid_configuration.json` |
| **2** | Unauth inference negative control | DONE | `evidence/TEST_2_unauth_inference.txt` (401s) |
| **3** | Device-code OAuth start (no human complete) | DONE → HUMAN_GATE | `evidence/TEST_3_device_code_start.txt` |
| **4** | Session token inference | SKIPPED_NO_SESSION | `evidence/TEST_4_session_inference.txt` |
| **5** | AAR researcher loop Anthropic hard-bind relevance | DONE | `evidence/TEST_5_aar_relevance.txt` |

Final CASE **D**; CAN unknown; HUMAN_GATE REQUIRED (`XAI_OAUTH_HUMAN_GATE`).
