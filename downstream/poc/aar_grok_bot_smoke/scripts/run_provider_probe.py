#!/usr/bin/env python3
"""Phase 3 — unique provider probe via Grok Bot gateway session (not fabricated)."""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
POC = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "downstream" / "poc")]

os.environ["AAR_AGENT_PROVIDER"] = "external"
os.environ["AAR_AGENT_PROVIDER_MODULE"] = "aar_grok_bot_smoke.providers.grok_bot_gateway"
os.environ["AAR_AGENT_PROVIDER_PATH"] = str(REPO / "downstream" / "poc")
os.environ.setdefault("LOCAL_MODE", "true")
os.environ.setdefault("MONITOR_REQUIRED", "0")
for k in ("ANTHROPIC_API_KEY", "XAI_API_KEY", "ANT_high_prio_API", "ANT_API_KEY"):
    os.environ.pop(k, None)

from aar.research_loop.provider import (  # noqa: E402
    AssistantEvent,
    ResultEvent,
    SessionOptions,
    TextPart,
    get_agent_provider,
)

MARKER = "GROK_BOT_AAR_PROVIDER_OK"
EVIDENCE = Path(
    os.environ.get(
        "AAR_GROK_BOT_PROBE_EVIDENCE",
        "/workspace/aar_grok_bot_smoke_work/evidence/provider_probe",
    )
)


async def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    prov = get_agent_provider()
    meta = {
        "provider_name": prov.name,
        "provider_module": type(prov).__module__,
        "requires_anthropic_key": getattr(prov, "requires_anthropic_key", None),
        "supports_inprocess_mcp": getattr(prov, "supports_inprocess_mcp", None),
        "researcher_agent_id": os.getenv(
            "AAR_GROK_BOT_RESEARCHER_AGENT_ID",
            "fac98a36-f560-43b8-9ac8-1ddacbbd16ed",
        ),
        "marker_expected": MARKER,
        "auth_mechanism": "grok_bot_sand_gateway_bearer",
        "oauth_used": False,
        "xai_api_key_used": False,
        "anthropic_used": False,
    }
    (EVIDENCE / "probe_meta.json").write_text(json.dumps(meta, indent=2) + "\n")

    cwd = EVIDENCE / "cwd"
    cwd.mkdir(parents=True, exist_ok=True)
    task = (
        "UNIQUE PROVIDER PROBE — respond with ONLY the exact string below, "
        "no quotes, no markdown, no extra words:\n"
        f"{MARKER}\n"
        "If you write anything else the probe fails. Do not invent alternate markers."
    )
    opts = SessionOptions(
        model=os.getenv("AAR_AGENT_MODEL", "grok-bot"),
        cwd=str(cwd),
        system_prompt="Reply exactly as instructed. No tools needed for this probe.",
        allowed_tools=[],
        permission_mode="bypassPermissions",
    )
    t0 = time.time()
    texts: list[str] = []
    result_event = None
    err = None
    try:
        async with prov.session(opts) as sess:
            await sess.query(task)
            async for ev in sess.receive_response():
                if isinstance(ev, AssistantEvent):
                    for part in ev.content:
                        if isinstance(part, TextPart):
                            texts.append(part.text)
                elif isinstance(ev, ResultEvent):
                    result_event = {
                        "result_preview": str(ev.result)[:500] if ev.result is not None else None,
                        "stop_reason": ev.stop_reason,
                    }
    except Exception as e:
        err = {"type": type(e).__name__, "code": getattr(e, "code", None), "message": str(e)[:500]}

    reply = "\n".join(texts).strip()
    ok = MARKER in reply and MARKER == reply.strip().splitlines()[-1].strip() or reply.strip() == MARKER
    # Strict: exact match preferred; also accept if marker is the only non-empty line
    exact = reply.strip() == MARKER
    contains = MARKER in reply
    out = {
        "PROBE_OK": bool(exact or (contains and MARKER in reply.replace("`", "").replace('"', "").strip())),
        "EXACT_MATCH": exact,
        "CONTAINS_MARKER": contains,
        "reply_text": reply[:2000],
        "result_event": result_event,
        "duration_s": round(time.time() - t0, 2),
        "error": err,
        "provider_calls": 1 if not err else 0,
        "grok_researcher_calls": 1 if not err else 0,
    }
    # Tighten PROBE_OK: must contain marker and come from provider (no error)
    out["PROBE_OK"] = bool(contains and err is None)
    (EVIDENCE / "probe_result.json").write_text(json.dumps(out, indent=2) + "\n")
    (EVIDENCE / "reply.txt").write_text(reply + "\n")
    # Mirror under repo poc evidence
    poc_ev = POC / "evidence" / "provider_probe"
    poc_ev.mkdir(parents=True, exist_ok=True)
    (poc_ev / "probe_result.json").write_text(json.dumps(out, indent=2) + "\n")
    (poc_ev / "probe_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    (poc_ev / "reply.txt").write_text(reply + "\n")
    print("PROBE_OK", out["PROBE_OK"], "EXACT", exact, "duration_s", out["duration_s"])
    if err:
        print("ERROR", err)
    else:
        print("REPLY_PREVIEW", reply[:200])
    return 0 if out["PROBE_OK"] else 2


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
