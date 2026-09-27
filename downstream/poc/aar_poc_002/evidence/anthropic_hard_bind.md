# Anthropic hard-bind — UPSTREAM_NATIVE_UNPATCHED agent loop

**Verdict:** `UPSTREAM_NATIVE_UNPATCHED=BLOCKED` for the official Task-B **agent** loop on this box.  
**Reason:** User has **no Anthropic API key** and forbids using Anthropic. Upstream AAR agent path is hard-bound to Anthropic / Claude Agent SDK with **no** official alternate provider switch.

**Eval-only path remains useful** (vector suite via `adapter.eval` / `aar.eval_pod.run_eval`) and does **not** require Anthropic — see `freeze_eval_only_smoke.txt`.

Pinned tree: `02dbe9d` / branch `downstream/aar-poc-002-native`. Citations below are from this checkout.

---

## Hard gates (cited)

### 1. CLI refuses agent without key

`run.py` `cmd_agent` (lines 33–35):

```python
if not os.getenv("ANTHROPIC_API_KEY"):
    print("Error: ANTHROPIC_API_KEY is required for agent mode")
    sys.exit(1)
```

**Evidence:** `unpatched_failures/agent_no_key.txt` → exact error + `EXIT=1`.

### 2. Research loop imports Claude Agent SDK only

`aar/research_loop/agent.py` lines 21–28:

```python
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    ...
)
```

`BaseAgent` docstring (line 226): *“Wraps ClaudeSDKClient for research tasks.”*  
Default model (lines 234, 398): `os.getenv("AAR_AGENT_MODEL", "claude-opus-4-8")`.  
Session execution (line ~314): `async with ClaudeSDKClient(options=options) as client`.

### 3. MCP tool servers are Claude SDK MCP

- `aar/research_loop/tools/server_api_tools.py:15` — `from claude_agent_sdk import tool, create_sdk_mcp_server`
- `aar/research_loop/tools/prior_work_tools.py:12` — same

`evaluate_model` / `submit_idea_proposal` / `share_finding` are registered via `create_sdk_mcp_server` for the Claude agent — not a provider-agnostic tool bus.

### 4. Integrity monitor hard-requires Anthropic HTTP API

`aar/research_loop/monitor.py`:

- `MONITOR_MODEL` default `"claude-opus-4-8"` (line 16)
- Lines 263–265: if no `ANTHROPIC_API_KEY` (or `ANT_high_prio_API`) → `error: "no_api_key"` / not approved
- Lines 270–271 / 437–438: `POST https://api.anthropic.com/v1/messages` with `x-api-key` + `anthropic-version`

Even with `MONITOR_REQUIRED=0`, the **agent session itself** still needs ClaudeSDKClient + key (gates 1–2).

### 5. No official OpenAI / other agent-loop provider switch

Search over `aar/research_loop/` + `run.py` for agent providers (`openai`, `OpenAI`, `OPENAI_API`, `litellm`, `langchain`, etc.) found **no** alternate research-loop backend.

Evidence: `no_alt_agent_provider.txt` (empty hit set for provider switch).

Judge backends for **eval** (`JUDGE_BACKEND=openai|anthropic|local` in `aar/eval_pod/run_eval.py`) are unrelated to the **research agent** loop.

---

## What this does / does not block

| Path | Status without Anthropic |
|------|---------------------------|
| `python run.py agent …` | **BLOCKED** (hard exit) |
| `AutonomousAgentLoop` / Claude sessions | **BLOCKED** |
| Integrity monitor (default) | **BLOCKED** / always deny |
| `aar.eval_pod.run_eval` / `generic_aar` / POC-002 `adapter.eval` | **OK** (stub / VectorModel; no Anthropic) |
| Flask `run.py server` import | App object imports OK; `__main__` still hits missing `aar.utils.hierarchical_cache` (separate blocker; not patched) |

---

## Policy for this POC

- **Do not** rewrite `aar/research_loop` to swap providers.
- **Do not** invent a POC-001-style substitute loop to “prove” native AAR.
- Provider swap only if parent opens an explicit **PATCHED** track later.
- Freeze claim: native **unpatched** upstream agent loop cannot run here → `UPSTREAM_NATIVE_UNPATCHED=BLOCKED`.
- Retained value: eval-only submit-model surface + vector suite + held-out strip proof (`CAN_WE_SCORE_VECTOR_VIA_NATIVE_EVAL=PASS`).
