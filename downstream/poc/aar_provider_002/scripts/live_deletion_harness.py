#!/usr/bin/env python3
"""Enter AutonomousAgentLoop.run() once — used for LIVE deletion proofs (not import-only)."""
from __future__ import annotations
import asyncio, json, os, sys, uuid
from pathlib import Path

REPO = Path(os.environ.get("DELETION_REPO", Path(__file__).resolve().parents[4]))
sys.path[:0] = [str(REPO), str(REPO / "downstream" / "poc")]
for k in ("ANTHROPIC_API_KEY", "XAI_API_KEY"):
    os.environ.pop(k, None)
os.environ.setdefault("LOCAL_MODE", "true")
os.environ.setdefault("MONITOR_REQUIRED", "0")
os.environ.setdefault("MAX_ITERATIONS", "1")

from aar.research_loop.agent import AutonomousAgentLoop
from aar.research_loop.provider import get_agent_provider

async def main() -> int:
    marker = Path(os.environ.get("DELETION_MARKER", "/tmp/aar_live_deletion_entered.json"))
    runs = Path(os.environ.get("DELETION_RUNS", "/tmp/aar_live_deletion_runs"))
    ws = runs / "workspace"; logs = runs / "logs"
    ws.mkdir(parents=True, exist_ok=True); logs.mkdir(parents=True, exist_ok=True)
    prov = get_agent_provider()
    print("HARNESS_PROVIDER", prov.name, type(prov).__module__)
    loop = AutonomousAgentLoop(
        idea_uid="live-deletion",
        idea_name="live_deletion",
        workspace=ws,
        logs_dir=logs,
        max_runtime_seconds=120,
        max_iterations=1,
        model=os.environ.get("AAR_AGENT_MODEL", "stub"),
        local_mode=True,
    )
    loop._prompt = "Reply with exactly: LIVE_DELETION_BASELINE_OK. No tools needed."
    # Mark that we entered run()
    marker.write_text(json.dumps({"entered_run": True, "provider": prov.name, "pid": os.getpid()}) + "\n")
    print("ENTERED_LOOP_RUN")
    result = await loop.run()
    print("LOOP_DONE", json.dumps(result))
    marker.write_text(json.dumps({"entered_run": True, "completed": True, "result": result}) + "\n")
    return 0 if result.get("sessions", 0) >= 1 else 2

if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
