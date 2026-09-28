# CLAUDE_COUPLING_MAP — AAR-xAI-adapter-001 PHASE 0

**Date:** 2026-09-28 (UTC+8)  
**Branch:** `downstream/aar-xai-adapter-001`  
**BASE_SHA (oauth-002 freeze):** `00ba33b51d6b78cbb0844268fc437d64cd6e0c31`  
**PINNED_UPSTREAM_SHA:** `02dbe9d2cadc553720d17cdf6259c0b8727e6cde`  
**Scope:** Researcher inference path only (`run.py agent` → model). Eval judges / dashboard theming out of band except where noted.

## Verdict fields

| Field | Value |
|-------|-------|
| **CLAUDE_COUPLING_POINTS** | 14 (see inventory) |
| **CLAUDE_COUPLING_DEPTH** | **DEEP** |
| **DEPTH** | **DEEP** (transport/auth/message/tool/permission/model); research control-flow + task semantics are **separable** (see §Transport vs research-semantics) |
| **PROVIDER_INTERFACE_EXISTS** | **false** |
| **CORE_FILES_INVOLVED** | `run.py`, `aar/research_loop/agent.py`, `aar/research_loop/tools/server_api_tools.py`, `aar/research_loop/tools/prior_work_tools.py`, `aar/research_loop/monitor.py` (+ secondary: hooks/, `aar/infrastructure/execute_autonomous.py`, `aar/web_ui/backend/worker.py`) |

UNPATCHED entry evidence: `evidence/UNPATCHED_agent_entry.txt` → exact `Error: ANTHROPIC_API_KEY is required for agent mode` EXIT=1.

---

## Call graph (pinned upstream)

```
ENTRYPOINT
  run.py::main → cmd_agent
    AUTH gate: require ANTHROPIC_API_KEY else exit 1
    construct AutonomousAgentLoop(idea_uid, idea_name, model, local_mode, …)
      ↓
LOOP  AutonomousAgentLoop.run
  optional FindingsSync (HTTP, not Claude)
  while True:
    stop if max_iterations | timeout (_StopChecker)
      ↓
SESSION  AutonomousAgentLoop._run_session
  resolve Jinja prompt (_get_prompt / resolve_prompt) — research semantics
  open session_*.log
  agent = _create_agent(session_id) → BaseAgent(...)
      ↓
PROVIDER  BaseAgent.execute → _execute_once
  ClaudeAgentOptions{allowed_tools, system_prompt, permission_mode,
                     cwd, model, mcp_servers, setting_sources, betas,
                     thinking, effort, cli_path?}
  async with ClaudeSDKClient(options) as client:
    await client.query(task)
    async for message in client.receive_response():
      ↓
RESPONSE  isinstance AssistantMessage | ResultMessage | TextBlock | ToolUseBlock
  message_callback → session log
  count ToolUseBlock as iteration_count
  break on ResultMessage
  AgentResult(success, output, duration, iteration_count)
      ↓
STATE UPDATE (research, mostly provider-neutral)
  session_count += 1
  stop_checker.record_success / record_error
  optional _sync_to_s3 (findings.json + session logs)
  (agent-driven) findings.json / MCP evaluate_model|share_finding|submit_idea_proposal
      ↓
NEXT ITERATION  back to while True (fresh Claude session each iteration)
```

**Iteration = one fresh provider session** (docstring: “Each iteration is a fresh Claude session”). Loop control does not resume Claude conversation state across iterations; resume is not part of upstream AAR loop semantics.

---

## Coupling inventory (researcher inference)

| # | Location | What | Coupling class | Claude-specific? |
|---|----------|------|----------------|------------------|
| 1 | `run.py:33–35` | `ANTHROPIC_API_KEY` hard exit | **AUTH** | YES |
| 2 | `run.py:139` | `--model` default `claude-opus-4-8` | **MODEL** | YES (default string) |
| 3 | `agent.py:21–28` | `from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock, ToolUseBlock` | **TRANSPORT** + **MESSAGE_SCHEMA** | YES |
| 4 | `agent.py:225–248` `BaseAgent` | Wraps ClaudeSDKClient; `permission_mode=bypassPermissions`; `cli_path` | **TRANSPORT** + **PERMISSION** + **SESSION** | YES |
| 5 | `agent.py:289–312` | Options: `betas`, `thinking` adaptive, `effort`, `setting_sources=["project"]`, `mcp_servers` | **SESSION** + **PERMISSION** + **TOOL_SCHEMA** | YES (Claude Code / Agent SDK options) |
| 6 | `agent.py:314–329` | `ClaudeSDKClient` query + `receive_response` stream | **TRANSPORT** + streaming | YES |
| 7 | `agent.py:328–374` | `isinstance` on Claude message/block types; extract text/tool_uses | **MESSAGE_SCHEMA** | YES |
| 8 | `agent.py:203–218` | `_is_overloaded` / 529 retry | **errors** (Anthropic capacity) | YES (error taxonomy) |
| 9 | `agent.py:459–482` `_create_agent` | `cli_path=shutil.which("claude")`; allowed_tools mix built-ins + `mcp__…` | **TRANSPORT** + **TOOL_SCHEMA** | YES (claude binary + MCP name shape) |
| 10 | `tools/server_api_tools.py:15,1436` | `@tool` + `create_sdk_mcp_server` from `claude_agent_sdk` | **TOOL_SCHEMA** | YES (registration); tool *bodies* are HTTP/fs research APIs |
| 11 | `tools/prior_work_tools.py:12,189` | same MCP factory | **TOOL_SCHEMA** | YES (registration) |
| 12 | `monitor.py:263–271,430–438` | Direct `POST https://api.anthropic.com/v1/messages` + `x-api-key` | **AUTH** + **TRANSPORT** + **MODEL** | YES |
| 13 | `server_api_tools.submit_idea_proposal` | Calls `check_proposal` / leakage monitors | **RESEARCH_SEMANTICS** wired to Claude monitor | MIXED — research gate, Claude judge |
| 14 | `hooks/*.py`, `telemetry/` | Claude Code PreToolUse/PostToolUse scripts; `setting_sources=["project"]` | **PERMISSION** / observability | YES if project hooks active; not in Python options dict beyond setting_sources |

**Not a coupling for this mission (eval/judge only):** `aar/benchmarks/_judge_http.py`, `aar/eval_pod/judges.py`, `JUDGE_BACKEND=anthropic` — orthogonal to researcher loop provider.

**No alternate agent provider:** search of `aar/research_loop/` + `run.py` finds no OpenAI/litellm/generic `Provider` interface (aligns with POC-002 `evidence/no_alt_agent_provider.txt`). **PROVIDER_INTERFACE_EXISTS=false**.

---

## Coupling class summary

| Class | Present? | Notes |
|-------|----------|-------|
| **TRANSPORT** | YES DEEP | ClaudeSDKClient only path for researcher inference |
| **AUTH** | YES DEEP | Env `ANTHROPIC_API_KEY` at entry + monitor HTTP key |
| **SESSION** | YES | Fresh SDK client per iteration; Claude options (cwd, model, mcp, permission) |
| **MESSAGE_SCHEMA** | YES DEEP | AssistantMessage / ResultMessage / TextBlock / ToolUseBlock hard-typed |
| **TOOL_SCHEMA** | YES DEEP | `@tool` / `create_sdk_mcp_server`; built-in Read/Write/Bash/… Claude Code tools |
| **PERMISSION** | YES | `permission_mode=bypassPermissions`; project setting_sources / hooks |
| **MODEL** | YES | Default `claude-opus-4-8`; monitor `MONITOR_MODEL` same family |
| **STATE** | SHALLOW | `session_count`, findings.json, S3 sync — not Claude-typed |
| **CONTROL_FLOW** | SHALLOW | `while` + timeout + max_iterations + fresh session — provider-agnostic structure |
| **RESEARCH_SEMANTICS** | SHALLOW→MIXED | Prompt/ideas/evaluate_model/share_finding/leaderboard/findings — neutral; **integrity monitor** currently Claude HTTP |

---

## Transport vs research-semantics dependence

**Claude transport (must unbind for Grok CLI OAuth):**

- Auth gate + Claude Agent SDK client/options/message types
- Claude Code CLI binary (`cli_path`)
- MCP tool *registration* via `claude_agent_sdk`
- Permission / betas / thinking / effort options
- Optional: integrity monitor Anthropic Messages API (or `MONITOR_REQUIRED=0` for POC)

**Research semantics (must PRESERVE — not replace with POC-001 homemade loop):**

- `AutonomousAgentLoop` iteration = session; stop = timeout | max_iterations
- Jinja system prompt (`prompt.jinja2` / `prompt_safety.jinja2`)
- Agent tools for eval/submit/share (semantic contracts), findings.json, local_mode server URL
- Same 8D black-box task as AAR-POC-002 (downstream adapter suite) — out of PHASE 0 code scope but in mission goal
- Do **not** invent new scheduler / state machine / leaderboard / evaluator

Implication: smallest seam replaces **PROVIDER** (+ AUTH/MESSAGE/TOOL registration adapters) while keeping LOOP/SESSION orchestration and research tool *behavior*.

---

## CASE hypothesis (post PHASE 0)

| Hypothesis | Rationale |
|------------|-----------|
| **MIN_PROVIDER_SEAM** | Introduce a tiny provider-neutral session interface (query + stream messages + tool bridge) consumed by `BaseAgent` / `_create_agent`; implement Grok CLI backend **downstream**; core change only to unbind Claude imports/options. Prefer injecting provider from downstream. |
| **UPSTREAM_SEMANTICS_PRESERVED** | Keep `AutonomousAgentLoop.run` / `_run_session` / findings / max_iterations; no POC-001 `run_loop`. |
| **GROK_PROVIDER_RUNTIME** | Official `grok` 1.0.41 `--single` / noninteractive + local OIDC `~/.grok/auth.json` (oauth-002 CASE A pattern). Note: live `grok models` may currently report unauthenticated — document in later auth probe; PHASE 0 is read-only. |
| **Core Q preview** | `CAN_AAR_NATIVE_RESEARCH_LOOP_RUN_WITH_XAI_OAUTH` = **unknown until PHASE≥3 smoke**; structurally **feasible iff** AUTH gate + BaseAgent transport + MCP registration unbound and grok OAuth session live. |
| **Likely CASE ladder** | If seam + ≥5 iters: success path; if auth dead: code ready + AUTH_EXPIRED / HUMAN_GATE; if tools/MCP cannot map to grok CLI: partial seam + documented gap. |

---

## Explicit non-goals (PHASE 0)

- No core or downstream implementation yet (PHASE 0 read-only analysis + this map + UNPATCHED evidence).
- No oauth-001/002 tree edits.
- No Reviewer notify.
- No secret/PII capture.

## Next

PHASE 1 → `MIN_PROVIDER_CONTRACT.md` (provider-neutral interface shape only).
