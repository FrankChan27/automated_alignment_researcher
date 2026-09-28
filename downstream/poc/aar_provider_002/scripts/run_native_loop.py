#!/usr/bin/env python3
"""Drive upstream AutonomousAgentLoop with external provider (OIDC grok CLI).

AAR-provider-002: loads via AAR_AGENT_PROVIDER_MODULE — core has zero vendor knowledge.
Uses AutonomousAgentLoop.run() (not POC-001 homemade loop). Fresh RUN_ID / TRACE.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
POC = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "downstream" / "poc")]

# EXTERNAL_PLUGIN — no grok name required in core; module path is the seam
os.environ["AAR_AGENT_PROVIDER"] = os.environ.get("AAR_AGENT_PROVIDER", "external")
os.environ["AAR_AGENT_PROVIDER_MODULE"] = os.environ.get(
    "AAR_AGENT_PROVIDER_MODULE", "aar_provider_002.providers.grok_cli"
)
os.environ["AAR_AGENT_PROVIDER_PATH"] = os.environ.get(
    "AAR_AGENT_PROVIDER_PATH", str(REPO / "downstream" / "poc")
)
os.environ.setdefault("LOCAL_MODE", "true")
os.environ.setdefault("MONITOR_REQUIRED", "0")
os.environ.setdefault("AAR_AGENT_MODEL", "grok-4.7")
os.environ.setdefault("AAR_PROVIDER_MAX_TURNS", "12")
for k in ("ANTHROPIC_API_KEY", "XAI_API_KEY", "ANT_high_prio_API", "ANT_API_KEY"):
    os.environ.pop(k, None)

from aar.research_loop.agent import AutonomousAgentLoop  # noqa: E402
from aar.research_loop.provider import get_agent_provider  # noqa: E402


PROMPT = """You are the AAR researcher on the POC-002 8D black-box vector task.

OBJECTIVE (unchanged from AAR-POC-002): propose an 8-dimensional integer vector
(each dim in [0,100]) to maximize the hillclimb safety score under the capability
filter. This is black-box — you do not know the hidden target. Use prior scores.

WORKSPACE: {workspace}
STATE FILE: {workspace}/STATE.json  (read first; write after each attempt)
MODEL OUT: {workspace}/model_out/vector.json
EVAL CMD (native POC-002 eval — run via Bash):
  source /home/box/aar-poc-002-venv/bin/activate
  cd {repo}
  PYTHONPATH={repo}:{repo}/downstream/poc python -m aar_poc_002.adapter.eval \\
    --suite {repo}/downstream/poc/aar_poc_002/adapter/suite.yaml \\
    --model {workspace}/model_out \\
    --secret-dir /home/box/aar-poc-002-secrets \\
    --out {workspace}/scores_latest.json \\
    --heldout-dir /home/box/aar-poc-002-secrets/heldout_scores

IMPORTANT: Make exactly ONE new vector proposal this session (not a full grid search).
Use prior STATE.json history. If already at headline_pct=100, confirm by re-eval or tiny perturbation then restore best.

REQUIRED STEPS THIS SESSION:
1. Read STATE.json if present (history of prior vectors+scores). If missing, start from [50]*8.
2. Propose a NEW 8-int vector (explore based on history). Write model_out/vector.json as {{"vector":[...]}}.
3. Run EVAL CMD via Bash. Read scores_latest.json (headline_pct / per_benchmark means).
4. Append {{"vector":..., "headline_pct":..., "hillclimb_mean":..., "ts":...}} to STATE.json history.
5. Print a one-line summary: ITER_DONE vector=... headline=... hillclimb=...

Do not invent scores. Do not change the 8D objective. Use tools (Read/Write/Bash).
"""


def state_hash(path: Path) -> str:
    if not path.exists():
        return "EMPTY"
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def append_trace(trace_path: Path, row: dict) -> None:
    with trace_path.open("a") as f:
        f.write(json.dumps(row) + "\n")


async def main() -> int:
    runs = Path(os.environ.get("PROVIDER002_RUNS_DIR", "/home/box/aar-provider-002-runs"))
    ws = runs / "workspace"
    logs = runs / "logs"
    ws.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    (ws / "model_out").mkdir(exist_ok=True)
    state_path = ws / "STATE.json"
    if not state_path.exists():
        state_path.write_text(
            json.dumps({"history": [], "task": "poc002_8d_vector", "mission": "aar-provider-002"}, indent=2) + "\n"
        )

    prov = get_agent_provider()
    print(
        "PROVIDER",
        prov.name,
        "requires_anthropic_key=",
        getattr(prov, "requires_anthropic_key", None),
        "supports_inprocess_mcp=",
        getattr(prov, "supports_inprocess_mcp", None),
        "module=",
        type(prov).__module__,
    )

    max_iters = int(os.environ.get("MAX_ITERATIONS", "5"))
    run_id = os.environ.get("RUN_ID") or f"provider002-{uuid.uuid4().hex[:10]}"
    os.environ["RUN_ID"] = run_id

    trace_path = POC / "evidence" / "ITERATION_TRACE.jsonl"
    if os.environ.get("APPEND_TRACE") == "1":
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        if not trace_path.exists():
            trace_path.write_text("")
    else:
        trace_path.write_text("")

    loop = AutonomousAgentLoop(
        idea_uid="aar-provider-002-8d",
        idea_name="poc002_8d_vector",
        workspace=ws,
        logs_dir=logs,
        max_runtime_seconds=int(os.environ.get("MAX_RUNTIME", "7200")),
        max_iterations=max_iters,
        model=os.environ.get("AAR_AGENT_MODEL", "grok-4.7"),
        local_mode=True,
    )
    loop._prompt = PROMPT.format(workspace=ws, repo=REPO)

    orig = loop._run_session

    async def traced_session():
        it = loop.session_count + int(os.environ.get("ITERATION_OFFSET", "0"))
        before = state_hash(state_path)
        err = None
        try:
            await orig()
        except Exception as e:
            err = str(e)[:300]
            raise
        finally:
            after = state_hash(state_path)
            score = None
            proposal = None
            try:
                st = json.loads(state_path.read_text())
                if st.get("history"):
                    last = st["history"][-1]
                    score = last.get("headline_pct", last.get("hillclimb_mean"))
                    proposal = last.get("vector")
            except Exception:
                pass
            scores_p = ws / "scores_latest.json"
            if score is None and scores_p.exists():
                try:
                    sc = json.loads(scores_p.read_text())
                    score = sc.get("headline_pct")
                except Exception:
                    pass
            append_trace(
                trace_path,
                {
                    "ITERATION": it,
                    "RUN_ID": run_id,
                    "MODEL": os.environ.get("AAR_AGENT_MODEL", "grok-4.7"),
                    "PROPOSAL": proposal,
                    "SCORE": score,
                    "STATE_HASH_BEFORE": before,
                    "STATE_HASH_AFTER": after,
                    "RECOVERED_FAILURE": False,
                    "ERROR": err,
                    "PROVIDER_MODULE": os.environ.get("AAR_AGENT_PROVIDER_MODULE"),
                    "PROVIDER_NAME": getattr(prov, "name", None),
                    "API_KEY_USED": False,
                    "ANTHROPIC_USED": False,
                },
            )

    loop._run_session = traced_session
    result = await loop.run()
    # Normalize stop_reason if max_iterations
    if result.get("sessions", 0) >= max_iters and result.get("stop_reason") in (None, "unknown", ""):
        result["stop_reason"] = "max_iterations"
    result["RUN_ID"] = run_id
    result["PROVIDER_MODULE"] = os.environ.get("AAR_AGENT_PROVIDER_MODULE")
    result["CORE_VENDOR_KNOWLEDGE"] = False
    (POC / "evidence" / "LOOP_RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print("LOOP_RESULT", result)
    return 0 if result.get("sessions", 0) >= max_iters else 2


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
