# AAR-POC-002 freeze verdict

**Date:** 2026-09-28 (UTC+8)  
**Branch:** `downstream/aar-poc-002-native`  
**Claim under test:** `CAN_WE_RUN_UPSTREAM_NATIVE_AAR` (unpatched Task-B agent loop)

## UPSTREAM_NATIVE_UNPATCHED = BLOCKED

Primary blocker: **Anthropic hard-bind** (user has no key; Anthropic forbidden).  
See `anthropic_hard_bind.md` + `unpatched_failures/agent_no_key.txt`.

Secondary (server `__main__`): missing `aar.utils.hierarchical_cache` — documented, **not** silently patched (`server_boot.txt`).

Tertiary: `claude` CLI absent on PATH (`agent_blocked_claude_cli.txt`) — moot without API key.

## What still PASSes (eval-only, no Anthropic)

| Check | Result | Evidence |
|-------|--------|----------|
| Vector suite via native `run_eval` | PASS | `freeze_eval_only_smoke.txt`, `vector_eval_smoke.txt` |
| Held-out stripped from research scores | PASS | same |
| `REPO_SECRET_PRESENT` | false | `repo_secret_absent.txt` |
| Downstream adapter only (no `aar/` edit for vector path) | PASS | `adapter/`, monkeypatch loader |

**Narrower true claim:** `CAN_WE_SCORE_VECTOR_VIA_NATIVE_EVAL=PASS`.  
**Agent claim:** `CAN_WE_RUN_UPSTREAM_NATIVE_AAR_AGENT_UNPATCHED=BLOCKED`.

## Out of scope / not done

- No rewrite of research loop
- No OpenAI/other provider swap
- No POC-001 `run_loop` substitute
- No Anthropic calls
