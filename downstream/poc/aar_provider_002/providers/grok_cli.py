"""GrokCLIProvider — official grok CLI (OUT package aar_provider_002).

Transport/session/message only. No strategy, scheduling, objective, leaderboard,
selection, score logic, or stop-policy.

Auth (no secret values are read or printed):
  1. If XAI_API_KEY is in the environment, it is passed through to the official
     grok CLI. That is the CLI's documented non-interactive auth
     ("set the XAI_API_KEY environment variable"). A local ~/.grok/auth.json
     can still exist and not be a CLI login ("Not signed in" /
     "No auth credentials for cli-chat-proxy"); stripping the key reproduces
     that failure, so this provider does not strip it.
  2. If XAI_API_KEY is absent, the CLI uses its own local OIDC session.

Anthropic / Claude API keys are always removed from the subprocess environment.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator, Optional

from aar.research_loop.provider import (
    AssistantEvent,
    ProviderError,
    ResultEvent,
    SessionOptions,
    TextPart,
)


_ANTHROPIC_ENV = ("ANTHROPIC_API_KEY", "ANT_high_prio_API", "ANT_API_KEY")


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
    out: dict[str, Any] = {
        "AUTH_JSON_PRESENT": p.exists(),
        "path": str(p),
        "XAI_API_KEY_PRESENT": bool(os.getenv("XAI_API_KEY")),
        "ANTHROPIC_API_KEY_PRESENT": bool(os.getenv("ANTHROPIC_API_KEY")),
    }
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
            out["PII_FIELDS_PRESENT"] = any(
                bool(entry.get(k)) for k in ("email", "user_id", "team_id")
            )
    except Exception as e:
        out["parse_error"] = type(e).__name__
    return out


def _auth_mechanism(env: dict) -> str:
    if env.get("XAI_API_KEY"):
        return "xai_api_key_official_cli"
    return "oidc_local_session"


def _redact(text: str) -> str:
    text = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._\-]+", r"\1[REDACTED]", text)
    text = re.sub(
        r"(?i)(xai_api_key|api[_-]?key|authorization|refresh_token)(['\"\s:=]+)[^\s'\"]+",
        r"\1\2[REDACTED]",
        text,
    )
    text = re.sub(r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+", "[JWT]", text)
    return text


def _write_call_receipt(record: dict) -> None:
    path = os.getenv("AAR_GROK_CALL_LOG")
    if not path:
        return
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


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
        model = opt.model or os.getenv("AAR_AGENT_MODEL", "grok-4.5")
        if model.startswith("claude"):
            model = os.getenv("AAR_GROK_MODEL", "grok-4.5")

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
            cmd.extend(["--max-turns", os.getenv("AAR_PROVIDER_MAX_TURNS", "8")])
        effort = os.getenv("AAR_GROK_REASONING_EFFORT", "").strip()
        if effort:
            cmd.extend(["--reasoning-effort", effort])
        if os.getenv("AAR_GROK_DISABLE_WEB_SEARCH", "").lower() in ("1", "true", "yes"):
            cmd.append("--disable-web-search")
        if os.getenv("AAR_GROK_NO_SUBAGENTS", "").lower() in ("1", "true", "yes"):
            cmd.append("--no-subagents")
        if opt.system_prompt:
            cmd.extend(["--system-prompt-override", opt.system_prompt])
        if opt.allowed_tools:
            builtins = [t for t in opt.allowed_tools if not t.startswith("mcp__")]
            if builtins:
                cmd.extend(["--tools", ",".join(builtins)])
        if opt.extra.get("always_approve", True):
            cmd.append("--always-approve")

        env = os.environ.copy()
        for k in list(env):
            if k in _ANTHROPIC_ENV or k.upper().startswith("ANTHROPIC"):
                env.pop(k, None)
        # XAI_API_KEY is intentionally retained. Official grok CLI treats it as
        # non-interactive auth. Stripping it forces "Not signed in" when the
        # local auth.json is not a CLI OIDC login.

        auth_mechanism = _auth_mechanism(env)
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

        grok_http_calls = len(re.findall(r"http\.create_response_stream", stderr))
        if grok_http_calls == 0:
            grok_http_calls = len(re.findall(r'event="client_post"', stderr))
        models = sorted(set(re.findall(r'model(?:_id)?="(grok[^"]*)"', stderr)))
        saw_xai = "api.x.ai" in stderr or "api.x.ai" in stdout
        saw_anthropic = ("api.anthropic.com" in stderr) or ("api.anthropic.com" in stdout)
        not_signed_in = "not signed in" in (stdout + "\n" + stderr).lower()

        _write_call_receipt(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "auth_mechanism": auth_mechanism,
                "xai_api_key_present": bool(env.get("XAI_API_KEY")),
                "anthropic_key_present_in_subprocess": any(k in env for k in _ANTHROPIC_ENV),
                "model_requested": model,
                "models_observed": models,
                "exit_code": code,
                "grok_http_calls": grok_http_calls,
                "saw_api_x_ai": saw_xai,
                "saw_api_anthropic": saw_anthropic,
                "not_signed_in": not_signed_in,
                "stdout_chars": len(stdout),
                "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
            }
        )

        combined_low = (stdout + "\n" + stderr).lower()
        if code != 0 and (
            not_signed_in
            or "not authenticated" in combined_low
            or ("please run" in combined_low and "login" in combined_low)
            or ("auth" in combined_low and "expired" in combined_low and "not signed in" in combined_low)
        ):
            raise ProviderError(
                "grok CLI is not signed in (OIDC session unusable and XAI_API_KEY not accepted)",
                code="AUTH_EXPIRED",
                retryable=False,
            )
        if saw_anthropic:
            raise ProviderError(
                "grok subprocess referenced api.anthropic.com; refusing",
                code="ANTHROPIC_ENDPOINT",
                retryable=False,
            )
        text = stdout.strip() or ""
        max_turns_stop = code != 0 and "max turns" in combined_low
        if code != 0 and not (max_turns_stop and text):
            safe_err = _redact((stderr or stdout)[:500])
            raise ProviderError(
                f"grok CLI exited {code}: {safe_err}",
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
    """Official grok CLI backend (external plugin; not imported by core)."""

    name = "grok_cli"
    requires_anthropic_key = False
    supports_inprocess_mcp = False

    def __init__(self, cli_path: Optional[str] = None):
        self._cli_path = cli_path

    def session(self, options: SessionOptions) -> GrokCLISession:
        bin_path = _resolve_grok_bin(options.cli_path or self._cli_path)
        return GrokCLISession(options, bin_path)


def get_provider() -> GrokCLIProvider:
    return GrokCLIProvider()
