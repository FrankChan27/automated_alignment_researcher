"""GrokCLIProvider — official grok CLI + local OIDC for researcher inference.

Transport/session/message only. No strategy, scheduling, objective, leaderboard,
selection, score logic, or stop-policy. Auth: local ~/.grok/auth.json via CLI
(never reads or prints secret values).
"""
from __future__ import annotations

import asyncio
import json
import os
import shutil
from pathlib import Path
from typing import Any, AsyncIterator, Optional

from aar.research_loop.provider import (
    AssistantEvent,
    ProviderError,
    ResultEvent,
    SessionOptions,
    TextPart,
)


def _resolve_grok_bin(cli_path: Optional[str] = None) -> str:
    candidates = [
        cli_path,
        os.getenv("GROK_CLI_PATH"),
        shutil.which("grok"),
        str(Path.home() / ".local/bin/grok"),
        str(Path.home() / ".grok/bin/grok"),
    ]
    for c in candidates:
        if c and Path(c).exists():
            return str(c)
    raise ProviderError(
        "official grok CLI not found on PATH",
        code="GROK_CLI_MISSING",
        retryable=False,
    )


def auth_metadata_only() -> dict:
    """Presence/expiry/mode only — never secret or PII values."""
    p = Path.home() / ".grok" / "auth.json"
    out: dict[str, Any] = {"AUTH_JSON_PRESENT": p.exists(), "path": str(p)}
    if not p.exists():
        return out
    st = p.stat()
    out["mode"] = oct(st.st_mode)[-3:]
    out["size_bytes"] = st.st_size
    try:
        data = json.loads(p.read_text())
        entry = next(iter(data.values())) if isinstance(data, dict) and data else {}
        if isinstance(entry, dict):
            out["auth_mode"] = entry.get("auth_mode")
            out["expires_at"] = entry.get("expires_at")
            out["oidc_issuer"] = entry.get("oidc_issuer")
            out["HAS_KEY"] = bool(entry.get("key"))
            out["HAS_REFRESH_TOKEN"] = bool(entry.get("refresh_token"))
            # never email/user_id/team_id values
            out["PII_FIELDS_PRESENT"] = any(
                bool(entry.get(k)) for k in ("email", "user_id", "team_id")
            )
    except Exception as e:
        out["parse_error"] = type(e).__name__
    return out


class GrokCLISession:
    def __init__(self, options: SessionOptions, grok_bin: str):
        self._options = options
        self._grok_bin = grok_bin
        self._task: Optional[str] = None
        self._ran = False

    async def __aenter__(self) -> "GrokCLISession":
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

        opt = self._options
        model = opt.model or os.getenv("AAR_AGENT_MODEL", "grok-4.7")
        # Default researcher model for grok path
        if model.startswith("claude"):
            model = os.getenv("AAR_GROK_MODEL", "grok-4.7")

        cmd = [
            self._grok_bin,
            "--single",
            self._task,
            "--verbatim",
            "--model",
            model,
            "--cwd",
            str(opt.cwd),
            "--permission-mode",
            opt.permission_mode or "dontAsk",
            "--output-format",
            opt.extra.get("output_format", "plain"),
        ]
        if opt.max_turns:
            cmd.extend(["--max-turns", str(opt.max_turns)])
        else:
            # Allow in-session tool use for one AAR iteration
            cmd.extend(["--max-turns", os.getenv("AAR_PROVIDER_MAX_TURNS", "8")])
        if opt.system_prompt:
            cmd.extend(["--system-prompt-override", opt.system_prompt])
        if opt.allowed_tools:
            # built-in names only (skip mcp__*)
            builtins = [t for t in opt.allowed_tools if not t.startswith("mcp__")]
            if builtins:
                cmd.extend(["--tools", ",".join(builtins)])
        if opt.extra.get("always_approve", True):
            cmd.append("--always-approve")
        # Deny nothing sensitive beyond defaults; never pass API keys in env for auth
        env = os.environ.copy()
        for k in list(env):
            # Do not inject xAI/Anthropic API keys into grok for this path
            if k in ("XAI_API_KEY", "ANTHROPIC_API_KEY", "ANT_high_prio_API", "ANT_API_KEY"):
                env.pop(k, None)

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(opt.cwd),
            env=env,
        )
        stdout_b, stderr_b = await proc.communicate()
        stdout = (stdout_b or b"").decode("utf-8", errors="replace")
        stderr = (stderr_b or b"").decode("utf-8", errors="replace")
        code = proc.returncode or 0

        # Auth failure detection (no secrets)
        combined_low = (stdout + "\n" + stderr).lower()
        if code != 0 and (
            "not authenticated" in combined_low
            or "please run" in combined_low and "login" in combined_low
            or "auth" in combined_low and "expired" in combined_low
        ):
            raise ProviderError(
                "grok CLI OIDC session missing or expired",
                code="AUTH_EXPIRED",
                retryable=False,
            )
        text = stdout.strip() or stderr.strip() or ""
        # Max-turns is a CLI budget stop, not an auth/transport failure. If we got
        # model output, complete the AAR session successfully so the upstream loop
        # can advance (still official grok CLI + OIDC; no Anthropic).
        max_turns_stop = code != 0 and "max turns" in combined_low
        if code != 0 and not (max_turns_stop and text):
            raise ProviderError(
                f"grok CLI exited {code}: {(stderr or stdout)[:500]}",
                code="GROK_CLI_NONZERO",
                retryable=False,
            )
        if not text:
            text = "(empty grok output)"
        yield AssistantEvent(content=[TextPart(text=text)])
        yield ResultEvent(
            result=text,
            stop_reason="max_turns" if max_turns_stop else "end_turn",
        )


class GrokCLIProvider:
    """Official grok CLI + OIDC backend."""

    name = "grok_cli"

    def __init__(self, cli_path: Optional[str] = None):
        self._cli_path = cli_path

    def session(self, options: SessionOptions) -> GrokCLISession:
        bin_path = _resolve_grok_bin(options.cli_path or self._cli_path)
        return GrokCLISession(options, bin_path)


def get_provider() -> GrokCLIProvider:
    return GrokCLIProvider()
