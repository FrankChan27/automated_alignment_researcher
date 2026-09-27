# UPSTREAM_NATIVE_UNPATCHED = BLOCKED

**Date:** 2026-09-28 (UTC+8)  
**Policy:** User confirmed — no Anthropic API key; Anthropic stack forbidden. No secret-request for Anthropic.

## Verdict

The official autonomous research entrypoint is **hard-bound to Claude / Anthropic**. Without that stack, the native agent loop cannot run. We do **not** rewrite `AutonomousAgentLoop` or substitute a downstream `run_loop` to fake native.

`UPSTREAM_NATIVE_UNPATCHED=BLOCKED` for ≥5 autonomous iterations via `run.py agent`.

## Hard-bind evidence (code)

1. `run.py:cmd_agent` — exits unless `ANTHROPIC_API_KEY` is set (`run.py` L33–35).
2. `run.py` CLI default model — `claude-opus-4-8` (`--model` / `AAR_AGENT_MODEL`).
3. `aar/research_loop/agent.py` — imports `claude_agent_sdk.ClaudeSDKClient`; `BaseAgent._execute_once` constructs `ClaudeAgentOptions` and runs `async with ClaudeSDKClient(...)`.
4. `AutonomousAgentLoop._create_agent` — `cli_path=shutil.which("claude")` (Claude Code CLI).
5. Default agent model — `claude-opus-4-8`.

Transcripts: `claude_hard_bind.txt`, `claude_hardbind_probe.txt`, `agent_no_key.txt`.

## Runtime evidence

| Probe | Result |
|-------|--------|
| `python3 run.py agent …` without key | `Error: ANTHROPIC_API_KEY is required for agent mode` (exit 1) — `agent_no_key.txt` |
| Fake key + venv | Passes key gate; enters ClaudeSDKClient path; hangs without real Claude CLI/API |
| `claude` on PATH | ABSENT |

## Still allowed (no agent)

- TASK/EVAL/CONFIG adapters under `downstream/poc/aar_poc_002/`
- Eval smoke via `adapter/eval.py` → `aar.eval_pod.run_eval.run`
- Secrets outside git; held-out strip behavior

## Explicitly forbidden

- Rewriting/replacing upstream scheduler/research loop to avoid Claude
- Copying POC-001 `proposer`/`run_loop` and claiming UPSTREAM_NATIVE_AAR=true
