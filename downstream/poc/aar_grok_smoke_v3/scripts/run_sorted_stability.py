#!/usr/bin/env python3
"""Smoke v3: one real AutonomousAgentLoop iteration on official grok CLI.

Goal (experimental): determine whether Python sorted() is stable.
Does not replace the loop. Does not call Claude/Anthropic.
Keeps XAI_API_KEY so the official grok CLI can authenticate.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import sys
import traceback
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
POC = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "downstream" / "poc")]

# Anthropic must not be available to the researcher subprocess.
for k in list(os.environ):
    if k in ("ANTHROPIC_API_KEY", "ANT_high_prio_API", "ANT_API_KEY") or k.upper().startswith("ANTHROPIC"):
        os.environ.pop(k, None)

if not os.environ.get("XAI_API_KEY"):
    print("SMOKE_PRECONDITION_FAIL: XAI_API_KEY is not set; official grok CLI non-interactive auth unavailable")
    raise SystemExit(2)

os.environ["AAR_AGENT_PROVIDER"] = "external"
os.environ["AAR_AGENT_PROVIDER_MODULE"] = "aar_provider_002.providers.grok_cli"
os.environ["AAR_AGENT_PROVIDER_PATH"] = str(REPO / "downstream" / "poc")
os.environ["LOCAL_MODE"] = "true"
os.environ["MONITOR_REQUIRED"] = "0"
os.environ.setdefault("AAR_AGENT_MODEL", "grok-4.5")
os.environ.setdefault("AAR_PROVIDER_MAX_TURNS", "8")
os.environ.setdefault("AAR_GROK_REASONING_EFFORT", "low")
os.environ["AAR_GROK_DISABLE_WEB_SEARCH"] = "1"
os.environ["AAR_GROK_NO_SUBAGENTS"] = "1"
os.environ.setdefault("GROK_CLI_PATH", str(Path.home() / ".local/bin/grok"))

from aar.research_loop.agent import AutonomousAgentLoop  # noqa: E402
from aar.research_loop.provider import get_agent_provider  # noqa: E402


PROMPT = """You are the AAR researcher executing exactly one iteration of the upstream autonomous loop.

QUESTION: Is Python's built-in sorted() a stable sort? Determine this experimentally with a minimal reproducible example. Do not answer from memory.

WORKSPACE: {workspace}
STATE FILE (read first, then update): {state}

CURRENT STATE is pending with an empty history. You must advance it.

REQUIRED STEPS (use tools; do not skip):
1. Read the state file.
2. Write this exact script to {workspace}/experiment_sorted_stability.py (you may add comments but keep the assertions):

items = [(2, "a"), (1, "b"), (2, "c"), (1, "d")]
result = sorted(items, key=lambda t: t[0])
expected_if_stable = [(1, "b"), (1, "d"), (2, "a"), (2, "c")]
stable = result == expected_if_stable
print("RESULT", result)
print("STABLE", stable)

3. Run it with the Bash tool: python3 {workspace}/experiment_sorted_stability.py
4. Rewrite the state file as JSON with:
   - task: "python_sorted_stability"
   - status: "completed"
   - iterations_completed: 1
   - experiment.script: "experiment_sorted_stability.py"
   - experiment.observed_output: the exact stdout from the script
   - experiment.stable: true or false matching the script
   - experiment.conclusion: one sentence
   - history: a one-element list with iteration=1, stable, and observed_output
5. Finish with a single final line: SORTED_STABILITY=true or SORTED_STABILITY=false

Rules: do not invent the stdout. Do not call network APIs. Do not use any model other than the one already running you. One experiment only.
"""


def state_hash(path: Path) -> str:
    if not path.exists():
        return "EMPTY"
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


async def main() -> int:
    run_id = os.environ.get("RUN_ID") or f"smoke-v3-{uuid.uuid4().hex[:10]}"
    os.environ["RUN_ID"] = run_id
    runs = Path(os.environ.get("SMOKE_V3_RUNS_DIR", f"/tmp/{run_id}"))
    ws = runs / "workspace"
    logs = runs / "logs"
    ws.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    state_path = ws / "STATE.json"
    state_path.write_text(
        json.dumps(
            {
                "task": "python_sorted_stability",
                "status": "pending",
                "iterations_completed": 0,
                "history": [],
            },
            indent=2,
        )
        + "\n"
    )
    (runs / "STATE_BEFORE.json").write_text(state_path.read_text())
    call_log = runs / "grok_calls.jsonl"
    os.environ["AAR_GROK_CALL_LOG"] = str(call_log)

    prov = get_agent_provider()
    print(
        "PROVIDER",
        type(prov).__module__ + "." + type(prov).__name__,
        "name=",
        getattr(prov, "name", None),
        "requires_anthropic_key=",
        getattr(prov, "requires_anthropic_key", None),
        "supports_inprocess_mcp=",
        getattr(prov, "supports_inprocess_mcp", None),
    )

    loop = AutonomousAgentLoop(
        idea_uid="aar-smoke-v3-sorted-stability",
        idea_name="sorted_stability",
        workspace=ws,
        logs_dir=logs,
        max_runtime_seconds=int(os.environ.get("MAX_RUNTIME", "900")),
        max_iterations=1,
        model=os.environ.get("AAR_AGENT_MODEL", "grok-4.5"),
        local_mode=True,
    )
    assert type(loop).__module__ == "aar.research_loop.agent"
    loop._prompt = PROMPT.format(workspace=str(ws), state=str(state_path))

    trace_path = runs / "ITERATION_TRACE.jsonl"
    before = state_hash(state_path)
    session_error = {"err": None}

    orig = loop._run_session

    async def traced_session():
        try:
            await orig()
        except Exception as e:
            session_error["err"] = f"{type(e).__name__}: {e}"[:500]
            # Stop the upstream loop from retrying a failed session into more Grok calls.
            loop.stop_checker.max_runtime = 0
            raise

    loop._run_session = traced_session

    try:
        result = await loop.run()
    except Exception:
        traceback.print_exc()
        result = {
            "run_id": run_id,
            "sessions": loop.session_count,
            "stop_reason": "exception",
            "error": session_error["err"],
        }

    after = state_hash(state_path)
    state_after = {}
    try:
        state_after = json.loads(state_path.read_text())
    except Exception as e:
        state_after = {"parse_error": type(e).__name__}

    calls = []
    if call_log.exists():
        for line in call_log.read_text().splitlines():
            if line.strip():
                calls.append(json.loads(line))
    grok_http = sum(int(c.get("grok_http_calls") or 0) for c in calls)
    saw_xai = any(c.get("saw_api_x_ai") for c in calls)
    saw_anthropic = any(c.get("saw_api_anthropic") for c in calls)

    summary = {
        "SMOKE_RUN_ID": run_id,
        "AAR_ENGINE": "aar.research_loop.agent.AutonomousAgentLoop",
        "AAR_LOOP_EXECUTED": True,
        "AAR_RESEARCHER_EXECUTED": loop.session_count >= 1 and bool(calls),
        "AAR_STATE_ADVANCED": before != after and state_after.get("status") == "completed",
        "AAR_ITERATIONS": loop.session_count,
        "PROVIDER_CALLS": len(calls),
        "GROK_HTTP_CALLS": grok_http,
        "SAW_API_X_AI": saw_xai,
        "SAW_API_ANTHROPIC": saw_anthropic,
        "STATE_HASH_BEFORE": before,
        "STATE_HASH_AFTER": after,
        "STATE_AFTER": state_after,
        "LOOP_RESULT": result,
        "SESSION_ERROR": session_error["err"],
        "AUTH_MECHANISM": calls[0].get("auth_mechanism") if calls else None,
        "MODELS_OBSERVED": sorted({m for c in calls for m in (c.get("models_observed") or [])}),
        "RUNS_DIR": str(runs),
    }
    (runs / "LOOP_RESULT.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    trace_path.write_text(
        json.dumps(
            {
                "ITERATION": 0,
                "RUN_ID": run_id,
                "STATE_HASH_BEFORE": before,
                "STATE_HASH_AFTER": after,
                "STATUS_AFTER": state_after.get("status"),
                "STABLE": (state_after.get("experiment") or {}).get("stable")
                if isinstance(state_after.get("experiment"), dict)
                else state_after.get("experiment"),
                "PROVIDER_CALLS": len(calls),
                "GROK_HTTP_CALLS": grok_http,
                "ERROR": session_error["err"],
            }
        )
        + "\n"
    )
    (runs / "SUMMARY.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
    print("SUMMARY", json.dumps({k: summary[k] for k in summary if k != "STATE_AFTER"}))
    print("STATE_AFTER_STATUS", state_after.get("status"), "STABLE", (state_after.get("experiment") or {}).get("stable") if isinstance(state_after.get("experiment"), dict) else None)
    ok = (
        summary["AAR_ITERATIONS"] >= 1
        and summary["AAR_STATE_ADVANCED"]
        and summary["AAR_RESEARCHER_EXECUTED"]
        and saw_xai
        and not saw_anthropic
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
