#!/usr/bin/env python3
"""Phase 4 — native AutonomousAgentLoop.run() via Grok Bot gateway provider."""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import sys
import time
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
POC = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "downstream" / "poc")]

os.environ["AAR_AGENT_PROVIDER"] = os.environ.get("AAR_AGENT_PROVIDER", "external")
os.environ["AAR_AGENT_PROVIDER_MODULE"] = os.environ.get(
    "AAR_AGENT_PROVIDER_MODULE", "aar_grok_bot_smoke.providers.grok_bot_gateway"
)
os.environ["AAR_AGENT_PROVIDER_PATH"] = os.environ.get(
    "AAR_AGENT_PROVIDER_PATH", str(REPO / "downstream" / "poc")
)
os.environ.setdefault("LOCAL_MODE", "true")
os.environ.setdefault("MONITOR_REQUIRED", "0")
os.environ.setdefault("AAR_AGENT_MODEL", "grok-bot")
os.environ.setdefault("MAX_ITERATIONS", "1")
for k in ("ANTHROPIC_API_KEY", "XAI_API_KEY", "ANT_high_prio_API", "ANT_API_KEY"):
    os.environ.pop(k, None)

from aar.research_loop.agent import AutonomousAgentLoop  # noqa: E402
from aar.research_loop.provider import get_agent_provider  # noqa: E402


PROMPT = """You are the AAR researcher (Grok Bot sand gateway).

GOAL: Verify whether Python list.sort() is a stable sort via a minimal reproducible experiment.

WORKSPACE: {workspace}
Write ALL artifacts under WORKSPACE:
  - {workspace}/experiment/stable_sort_test.py   (the experiment code)
  - {workspace}/experiment/output.txt            (stdout from running it)
  - {workspace}/experiment/conclusion.json       ({{"stable": true/false, "summary": "..."}})
  - Update {workspace}/findings.json with a short finding about stability

REQUIRED STEPS:
1. Create experiment/stable_sort_test.py that constructs a list of (key, original_index) pairs
   with duplicate keys, calls .sort() on key, and checks whether equal-key items retain
   original relative order.
2. Run it with Bash: python3 {workspace}/experiment/stable_sort_test.py | tee {workspace}/experiment/output.txt
3. Write conclusion.json with stable true/false based on the run (do not invent).
4. Write/update findings.json at WORKSPACE root, e.g.
   {{"findings":[{{"title":"list.sort stability","stable":true/false,"evidence":"experiment/output.txt"}}]}}
5. In your final reply, include a one-line summary:
   AAR_SMOKE_CONCLUSION stable=<yes|no>

Use tools. Execute for real. Do not fabricate output files.
"""


def file_hash(path: Path) -> str:
    if not path.exists():
        return "EMPTY"
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def dir_state_fingerprint(ws: Path) -> dict:
    """Hash key persisted artifacts AAR / researcher may touch."""
    keys = {
        "findings.json": file_hash(ws / "findings.json"),
        "STATE.json": file_hash(ws / "STATE.json"),
        "experiment/stable_sort_test.py": file_hash(ws / "experiment" / "stable_sort_test.py"),
        "experiment/output.txt": file_hash(ws / "experiment" / "output.txt"),
        "experiment/conclusion.json": file_hash(ws / "experiment" / "conclusion.json"),
    }
    blob = json.dumps(keys, sort_keys=True).encode()
    return {"files": keys, "fingerprint": hashlib.sha256(blob).hexdigest()[:16]}


async def main() -> int:
    run_id = os.environ.get("SMOKE_RUN_ID") or str(uuid.uuid4())
    os.environ["RUN_ID"] = run_id
    work_root = Path(os.environ.get("AAR_GROK_BOT_WORK", "/workspace/aar_grok_bot_smoke_work"))
    ws = Path(os.environ.get("AAR_GROK_BOT_RUN_WS", str(work_root / "runs" / run_id)))
    logs = ws / "logs"
    ws.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    (ws / "experiment").mkdir(exist_ok=True)

    # Seed findings.json so BEFORE hash is defined; AAR findings_path is logs_dir.parent/findings.json
    findings_path = ws / "findings.json"
    if not findings_path.exists():
        findings_path.write_text(json.dumps({"findings": [], "mission": "aar_grok_bot_smoke"}, indent=2) + "\n")
    state_path = ws / "STATE.json"
    if not state_path.exists():
        state_path.write_text(
            json.dumps({"history": [], "task": "list_sort_stability", "mission": "aar_grok_bot_smoke"}, indent=2)
            + "\n"
        )

    prov = get_agent_provider()
    print(
        "PROVIDER",
        prov.name,
        "requires_anthropic_key=",
        getattr(prov, "requires_anthropic_key", None),
        "module=",
        type(prov).__module__,
    )

    state_before = dir_state_fingerprint(ws)
    (ws / "STATE_BEFORE.json").write_text(json.dumps(state_before, indent=2) + "\n")

    max_iters = int(os.environ.get("MAX_ITERATIONS", "1"))
    loop = AutonomousAgentLoop(
        idea_uid="aar-grok-bot-smoke-sort",
        idea_name="list_sort_stability",
        workspace=ws,
        logs_dir=logs,
        max_runtime_seconds=int(os.environ.get("MAX_RUNTIME", "1200")),
        max_iterations=max_iters,
        model=os.environ.get("AAR_AGENT_MODEL", "grok-bot"),
        local_mode=True,
    )
    loop._prompt = PROMPT.format(workspace=ws)

    # Count provider calls via wrap
    provider_calls = {"n": 0}
    orig_session = loop._run_session

    async def traced_session():
        provider_calls["n"] += 1
        await orig_session()

    loop._run_session = traced_session

    t0 = time.time()
    err = None
    result = None
    try:
        result = await loop.run()
    except Exception as e:
        err = f"{type(e).__name__}: {e}"[:500]
        result = {"error": err, "sessions": loop.session_count}

    if isinstance(result, dict) and result.get("sessions", 0) >= max_iters and result.get("stop_reason") in (
        None,
        "unknown",
        "",
    ):
        result["stop_reason"] = "max_iterations"

    state_after = dir_state_fingerprint(ws)
    (ws / "STATE_AFTER.json").write_text(json.dumps(state_after, indent=2) + "\n")

    # Experiment executed?
    exp_py = ws / "experiment" / "stable_sort_test.py"
    exp_out = ws / "experiment" / "output.txt"
    exp_conc = ws / "experiment" / "conclusion.json"
    conclusion = None
    if exp_conc.exists():
        try:
            conclusion = json.loads(exp_conc.read_text())
        except Exception:
            conclusion = {"raw": exp_conc.read_text()[:500]}

    # Session log presence = provider was invoked through AAR
    session_logs = list(logs.glob("session_*.log"))
    advanced = state_before["fingerprint"] != state_after["fingerprint"]

    smoke = {
        "SMOKE_RUN_ID": run_id,
        "PROVIDER_NAME": getattr(prov, "name", None),
        "PROVIDER_MODULE": os.environ.get("AAR_AGENT_PROVIDER_MODULE"),
        "RESEARCHER_AGENT_ID": os.getenv(
            "AAR_GROK_BOT_RESEARCHER_AGENT_ID", "fac98a36-f560-43b8-9ac8-1ddacbbd16ed"
        ),
        "AUTH_MECHANISM": "grok_bot_sand_gateway_bearer",
        "OAUTH_USED": False,
        "XAI_API_KEY_USED": False,
        "ANTHROPIC_USED": False,
        "AAR_STATE_ADVANCED": advanced,
        "AAR_ITERATIONS": result.get("sessions", 0) if isinstance(result, dict) else 0,
        "PROVIDER_CALLS": provider_calls["n"],
        "GROK_RESEARCHER_CALLS": provider_calls["n"],
        "EXPERIMENT_EXECUTED": exp_py.exists() and exp_out.exists(),
        "STATE_BEFORE": state_before,
        "STATE_AFTER": state_after,
        "LOOP_RESULT": result,
        "CONCLUSION": conclusion,
        "SESSION_LOGS": [p.name for p in session_logs],
        "DURATION_S": round(time.time() - t0, 2),
        "ERROR": err,
        "WORKSPACE": str(ws),
    }
    (ws / "SMOKE_RESULT.json").write_text(json.dumps(smoke, indent=2) + "\n")
    # Also under work evidence + poc
    ev = work_root / "evidence"
    ev.mkdir(parents=True, exist_ok=True)
    (ev / "SMOKE_RESULT.json").write_text(json.dumps(smoke, indent=2) + "\n")
    poc_ev = POC / "evidence"
    poc_ev.mkdir(parents=True, exist_ok=True)
    (poc_ev / "SMOKE_RESULT.json").write_text(json.dumps(smoke, indent=2) + "\n")

    print("SMOKE_SUMMARY", json.dumps({k: smoke[k] for k in (
        "SMOKE_RUN_ID", "AAR_STATE_ADVANCED", "AAR_ITERATIONS", "PROVIDER_CALLS",
        "GROK_RESEARCHER_CALLS", "EXPERIMENT_EXECUTED", "CONCLUSION", "ERROR",
    )}, indent=2))
    ok = (
        smoke["AAR_ITERATIONS"] >= 1
        and smoke["PROVIDER_CALLS"] >= 1
        and smoke["GROK_RESEARCHER_CALLS"] >= 1
        and smoke["EXPERIMENT_EXECUTED"]
        and smoke["AAR_STATE_ADVANCED"]
        and err is None
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
