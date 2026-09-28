"""Grok Bot sand-gateway HTTP provider (RUNTIME-SPECIFIC integration).

STABILITY: NOT a public stable product API.
Depends on a local Grok Bot / sand runtime surface (typically
/home/box/agent-data/gateway.json Bearer token on loopback). Portable
deployments without that runtime cannot use this adapter.

Loaded only via AAR_AGENT_PROVIDER_MODULE — never imported by generic core.
Transport: sand_gateway_HTTP. Auth: grok_bot_sand_gateway_bearer.
Do not confuse with Grok Bot standalone (grok_cli) or any "Grok Build CLI" product name.

Original PoC: downstream/poc/aar_grok_bot_smoke/providers/grok_bot_gateway.py (immutable).
"""
from __future__ import annotations

import asyncio
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, AsyncIterator, Optional

from aar.research_loop.provider import (
    AssistantEvent,
    ProviderError,
    ResultEvent,
    SessionOptions,
    TextPart,
)

DEFAULT_GATEWAY_JSON = "/home/box/agent-data/gateway.json"
DEFAULT_RESEARCHER_AGENT_ID = "fac98a36-f560-43b8-9ac8-1ddacbbd16ed"
DEFAULT_POLL_TIMEOUT_S = 15 * 60
DEFAULT_POLL_INTERVAL_S = 2.0


def _gateway_config(path: Optional[str] = None) -> dict[str, Any]:
    p = Path(path or os.getenv("AAR_GROK_BOT_GATEWAY_JSON", DEFAULT_GATEWAY_JSON))
    if not p.exists():
        raise ProviderError(
            f"gateway.json not found at {p}",
            code="GATEWAY_CONFIG_MISSING",
            retryable=False,
        )
    try:
        data = json.loads(p.read_text())
    except Exception as e:
        raise ProviderError(
            f"gateway.json unreadable: {type(e).__name__}",
            code="GATEWAY_CONFIG_INVALID",
            retryable=False,
        ) from e
    for key in ("host", "port", "scheme", "token"):
        if key not in data or data[key] in (None, ""):
            raise ProviderError(
                f"gateway.json missing required key {key!r}",
                code="GATEWAY_CONFIG_INVALID",
                retryable=False,
            )
    return data


def _base_url(cfg: dict[str, Any]) -> str:
    # Prefer loopback; gateway may bind 0.0.0.0
    host = os.getenv("AAR_GROK_BOT_GATEWAY_HOST", "127.0.0.1")
    return f"{cfg['scheme']}://{host}:{cfg['port']}"


def _redact(text: str) -> str:
    """Strip anything that looks like a bearer token from error strings."""
    if not text:
        return text
    import re
    out = re.sub(r"(?i)(authorization\s*[:=]\s*bearer\s+)\S+", r"\1<redacted>", text)
    out = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9_\-\.]{8,}", r"\1<redacted>", out)
    return out[:800]


def _http_post_json(url: str, body: dict, token: str, timeout: float = 60.0) -> Any:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            if not raw:
                return None
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8", errors="replace")[:400]
        except Exception:
            pass
        raise ProviderError(
            _redact(f"gateway HTTP {e.code} on {url.split('/api/')[-1]}: {err_body}"),
            code="GATEWAY_HTTP_ERROR",
            retryable=e.code in (408, 429, 500, 502, 503, 504),
        ) from None
    except urllib.error.URLError as e:
        raise ProviderError(
            _redact(f"gateway unreachable: {type(e.reason).__name__ if hasattr(e, 'reason') else type(e).__name__}"),
            code="GATEWAY_UNREACHABLE",
            retryable=True,
        ) from None
    except json.JSONDecodeError as e:
        raise ProviderError(
            f"gateway returned non-JSON: {type(e).__name__}",
            code="GATEWAY_BAD_JSON",
            retryable=False,
        ) from None


def _entry_text(entry: dict) -> str:
    """Extract display text from a transcript entry."""
    if not isinstance(entry, dict):
        return ""
    kind = entry.get("kind")
    if kind == "send-message":
        msg = entry.get("message") or {}
        if isinstance(msg, dict):
            c = msg.get("content")
            if isinstance(c, str):
                return c
            if isinstance(c, list):
                parts = []
                for p in c:
                    if isinstance(p, dict) and isinstance(p.get("text"), str):
                        parts.append(p["text"])
                    elif isinstance(p, str):
                        parts.append(p)
                return "\n".join(parts)
        return ""
    if kind == "message":
        c = entry.get("content")
        if isinstance(c, str):
            return c
    return ""


def _assistant_entries_after(entries: list, after_seq: int) -> list[dict]:
    out = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        seq = e.get("seq")
        if not isinstance(seq, int) or seq <= after_seq:
            continue
        if e.get("kind") == "send-message":
            out.append(e)
    return out


def _build_prompt(task: str, options: SessionOptions) -> str:
    cwd = str(options.cwd) if options.cwd else os.getcwd()
    sys_bits = []
    if options.system_prompt:
        sys_bits.append(options.system_prompt.strip())
    guidance = (
        "You are the AAR Grok Researcher agent invoked via the sand gateway.\n"
        f"WORKSPACE CWD: {cwd}\n"
        "Use your tools (Read/Write/Edit/Bash/Glob/Grep/etc.) as needed to complete the task.\n"
        "Write any code, outputs, and conclusions under the WORKSPACE CWD unless the task says otherwise.\n"
        "Do not ask clarifying questions — execute and return a clear final answer.\n"
    )
    if options.allowed_tools:
        guidance += f"Preferred tools: {', '.join(options.allowed_tools)}\n"
    parts = [guidance]
    if sys_bits:
        parts.append("SYSTEM GUIDANCE:\n" + "\n".join(sys_bits))
    parts.append("AAR TASK:\n" + task)
    return "\n\n".join(parts)


class GrokBotGatewaySession:
    def __init__(self, options: SessionOptions):
        self._options = options
        self._task: Optional[str] = None
        self._ran = False

    async def __aenter__(self) -> "GrokBotGatewaySession":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        return None

    async def query(self, task: str) -> None:
        self._task = task

    async def receive_response(self) -> AsyncIterator:
        if self._task is None:
            raise ProviderError("query() not called", code="NO_QUERY")
        if self._ran:
            return
        self._ran = True

        # Never leak Anthropic/xAI keys into any child env (we use urllib, not subprocess,
        # but strip for safety if callers inspect environ later).
        for k in ("ANTHROPIC_API_KEY", "XAI_API_KEY", "ANT_high_prio_API", "ANT_API_KEY"):
            os.environ.pop(k, None)

        cfg = _gateway_config()
        token = cfg["token"]
        base = _base_url(cfg)
        agent_id = (
            os.getenv("AAR_GROK_BOT_RESEARCHER_AGENT_ID") or DEFAULT_RESEARCHER_AGENT_ID
        ).strip()
        timeout_s = float(os.getenv("AAR_GROK_BOT_POLL_TIMEOUT_S", str(DEFAULT_POLL_TIMEOUT_S)))
        interval_s = float(os.getenv("AAR_GROK_BOT_POLL_INTERVAL_S", str(DEFAULT_POLL_INTERVAL_S)))

        # Baseline transcript
        before = await asyncio.to_thread(
            _http_post_json, f"{base}/api/openAgent", {"id": agent_id}, token
        )
        if not isinstance(before, list):
            raise ProviderError(
                "openAgent did not return a transcript list",
                code="GATEWAY_BAD_TRANSCRIPT",
                retryable=False,
            )
        baseline_ids = {e.get("id") for e in before if isinstance(e, dict)}
        baseline_max_seq = 0
        for e in before:
            if isinstance(e, dict) and isinstance(e.get("seq"), int):
                baseline_max_seq = max(baseline_max_seq, e["seq"])

        prompt = _build_prompt(self._task, self._options)
        send_resp = await asyncio.to_thread(
            _http_post_json,
            f"{base}/api/sendPrompt",
            {"agentId": agent_id, "prompt": prompt},
            token,
        )
        if not (isinstance(send_resp, dict) and send_resp.get("accepted") is True):
            raise ProviderError(
                f"sendPrompt not accepted: {type(send_resp).__name__}",
                code="GATEWAY_SEND_REJECTED",
                retryable=False,
            )

        saw_running = False
        user_seq: Optional[int] = None
        deadline = asyncio.get_event_loop().time() + timeout_s
        reply_text = ""

        while True:
            now = asyncio.get_event_loop().time()
            if now > deadline:
                raise ProviderError(
                    f"timed out after {timeout_s:.0f}s waiting for researcher turn",
                    code="GATEWAY_POLL_TIMEOUT",
                    retryable=True,
                )

            agents = await asyncio.to_thread(
                _http_post_json, f"{base}/api/listAgents", {}, token
            )
            if not isinstance(agents, list):
                raise ProviderError(
                    "listAgents did not return a list",
                    code="GATEWAY_BAD_AGENTS",
                    retryable=False,
                )
            me = next((a for a in agents if isinstance(a, dict) and a.get("id") == agent_id), None)
            if me is None:
                raise ProviderError(
                    "researcher agent not found in listAgents",
                    code="GATEWAY_AGENT_MISSING",
                    retryable=False,
                )
            running_turn = bool(me.get("isRunningTurn"))
            if running_turn:
                saw_running = True

            transcript = await asyncio.to_thread(
                _http_post_json, f"{base}/api/openAgent", {"id": agent_id}, token
            )
            if not isinstance(transcript, list):
                raise ProviderError(
                    "openAgent did not return a transcript list during poll",
                    code="GATEWAY_BAD_TRANSCRIPT",
                    retryable=False,
                )

            # Find new user message from our sendPrompt
            if user_seq is None:
                for e in transcript:
                    if not isinstance(e, dict):
                        continue
                    if e.get("id") in baseline_ids:
                        continue
                    if e.get("kind") == "message" and e.get("role") == "user":
                        seq = e.get("seq")
                        if isinstance(seq, int):
                            user_seq = seq
                            break
                    # Fallback: any new message kind after baseline with higher seq
                    if e.get("kind") == "message" and isinstance(e.get("seq"), int):
                        if e["seq"] > baseline_max_seq:
                            user_seq = e["seq"]
                            break

            after_seq = user_seq if user_seq is not None else baseline_max_seq
            assistants = _assistant_entries_after(transcript, after_seq)
            texts = [_entry_text(e).strip() for e in assistants]
            texts = [t for t in texts if t]
            if texts:
                reply_text = "\n\n".join(texts)

            # Completion: turn not running, and we have a new assistant message after the prompt.
            # Require either we observed running, or enough time + reply present (fast turns).
            if (not running_turn) and reply_text and (saw_running or user_seq is not None):
                # Small settle: ensure no mid-stream flicker
                await asyncio.sleep(interval_s)
                agents2 = await asyncio.to_thread(
                    _http_post_json, f"{base}/api/listAgents", {}, token
                )
                me2 = next(
                    (a for a in agents2 if isinstance(a, dict) and a.get("id") == agent_id),
                    None,
                )
                if me2 and me2.get("isRunningTurn"):
                    continue
                transcript2 = await asyncio.to_thread(
                    _http_post_json, f"{base}/api/openAgent", {"id": agent_id}, token
                )
                if isinstance(transcript2, list):
                    assistants2 = _assistant_entries_after(
                        transcript2, after_seq
                    )
                    texts2 = [t for t in (_entry_text(e).strip() for e in assistants2) if t]
                    if texts2:
                        reply_text = "\n\n".join(texts2)
                break

            await asyncio.sleep(interval_s)

        if not reply_text:
            raise ProviderError(
                "researcher finished without assistant text",
                code="GATEWAY_EMPTY_REPLY",
                retryable=False,
            )

        yield AssistantEvent(content=[TextPart(text=reply_text)])
        yield ResultEvent(result=reply_text, stop_reason="end_turn")


class GrokBotGatewayProvider:
    """Grok Bot sand gateway HTTP backend (external plugin; not imported by core)."""

    name = "grok_bot_gateway"
    requires_anthropic_key = False
    supports_inprocess_mcp = False

    def session(self, options: SessionOptions) -> GrokBotGatewaySession:
        return GrokBotGatewaySession(options)


def get_provider() -> GrokBotGatewayProvider:
    return GrokBotGatewayProvider()
