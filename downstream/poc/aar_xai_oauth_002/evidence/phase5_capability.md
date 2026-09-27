# PHASE 5 — Capability probe (AAR-xAI-OAuth-002)

Date (UTC+8): 2026-09-28

## Official grok CLI + local OAuth session

| Question | Answer |
|----------|--------|
| Can official `grok` CLI run authenticated single-turn inference with local OAuth session (`~/.grok/auth.json`)? | **Y** |
| Evidence | PHASE 2 session PRESENT (auth_mode=oidc); PHASE 3 `grok models` exit 0 (4 models); PHASE 4 smoke exit 0 with exact `XAI_OAUTH_RESEARCHER_SMOKE_OK` |

## Shipped AAR agent loop vs Anthropic

Read-only scan of `aar/` (no edits):

- `aar/web_ui/backend/worker.py` requires `ANTHROPIC_API_KEY` before orchestrator/autonomous worker.
- `aar/research_loop/monitor.py` POSTs to `https://api.anthropic.com/v1/messages` with Anthropic keys.
- Eval/judge paths also default to Anthropic backends.

**Brief note:** Shipped AAR agent loop still **hard-binds Anthropic** for the researcher/orchestrator path. No xAI/grok provider adapter exists in-tree (and this mission forbids implementing one under `aar/` / `generic_aar/`).

## Adapter posture

| Field | Value |
|-------|-------|
| Path proven | Official **grok CLI** single-turn inference authenticated via local OIDC session |
| In-process AAR researcher provider using xAI OAuth | **Not present** |
| `ADAPTER_NEEDED` vs `READY_FOR_RESEARCHER_INFERENCE` | **ADAPTER_NEEDED** for embedding into shipped AAR loop; **READY_FOR_RESEARCHER_INFERENCE** via official CLI subprocess / external invocation with existing `~/.grok/auth.json` |

## What this enables for a researcher

- Non-interactive authenticated inference: `grok -p '...' --output-format plain --permission-mode dontAsk --max-turns 1 ...` with OAuth session present.
- Does **not** by itself prove portable Bearer use of the same OAuth token against `api.x.ai` public REST (not probed; prefer CLI per mission).
- Does **not** remove Anthropic hard-bind inside `aar/` without a future adapter (out of scope here).
