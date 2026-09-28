# REPORT — AAR-xAI-adapter-001

**FINAL_CASE: A**  
**Date:** 2026-09-28T09:33:31+0800

## Core question

| Field | Value |
|-------|-------|
| **CAN_AAR_NATIVE_RESEARCH_LOOP_RUN_WITH_XAI_OAUTH** | **true** |
| RESEARCHER_TRANSPORT | **grok_cli_oidc** |
| ANTHROPIC_USED | **false** |
| API_KEY_USED | **false** |
| CURSOR_USED | **false** |
| OAUTH_SECRET_IN_REPO | **false** |
| AUTH_MODE | oidc |
| GROK_VERSION | 1.0.41 |
| MODEL | grok-4.7 |
| BASE_SHA | 00ba33b51d6b78cbb0844268fc437d64cd6e0c31 |
| PINNED_UPSTREAM_SHA | 02dbe9d2cadc553720d17cdf6259c0b8727e6cde |

## Path proven

`AutonomousAgentLoop` → min Provider seam → official `grok` CLI → local OIDC (`~/.grok/auth.json`) → Grok.

Not used on researcher path: Anthropic API / ClaudeSDKClient / xAI API key / api.x.ai OAuth.

## PHASE summary

| Phase | Result |
|-------|--------|
| 0 CLAUDE_COUPLING_MAP | DEEP; PROVIDER_INTERFACE_EXISTS was false |
| 1 MIN_PROVIDER_CONTRACT | AgentProvider / SessionOptions |
| 2 SEAM_PLACEMENT + GROK_PROVIDER_MAPPING | downstream grok; core unbind only |
| 3 Implement seam + GrokCLIProvider | CORE_PATCH + smoke PASS |
| 4 DELETION_PROOF | both breaks = true |
| 5 ≥5 iters POC-002 8D | **5/5 sessions**; hash chain OK; native eval |
| 6 FAILURE_RECOVERY | nonzero → ProviderError; state not corrupted; recovery OK |

## Iteration evidence

sessions=5 duration_s=463.5  
HASH_CHAIN_OK=True  
See `evidence/ITERATION_TRACE.jsonl`.

N+1 sees prior state: each `STATE_HASH_BEFORE` equals prior `STATE_HASH_AFTER`.

## Core patch

Required to unbind Claude hardwire. Files: `run.py`, `aar/research_loop/agent.py`, `provider.py`, `providers/claude_sdk.py`.  
Zero grok-specific code in core. Deleting patch restores ANTHROPIC_API_KEY gate + ClaudeSDKClient import.

## Contrast

Not POC-001 homemade `run_loop`. Upstream `AutonomousAgentLoop` preserved.
