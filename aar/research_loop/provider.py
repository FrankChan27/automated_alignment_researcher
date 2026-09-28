"""Provider-neutral researcher-inference seam for AutonomousAgentLoop.

Built-in backend: claude_sdk only. Any other provider loads via
AAR_AGENT_PROVIDER_MODULE (importlib) — no vendor name branches in core.
"""
from __future__ import annotations

import importlib
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, AsyncIterator, Optional, Protocol, Union, runtime_checkable


@dataclass
class TextPart:
    text: str


@dataclass
class ToolUsePart:
    name: str
    input: dict
    id: Optional[str] = None


@dataclass
class ThinkingPart:
    thinking: str


Part = Union[TextPart, ToolUsePart, ThinkingPart]


@dataclass
class AssistantEvent:
    content: list


@dataclass
class ResultEvent:
    result: Any = None
    stop_reason: Optional[str] = None


ProviderEvent = Union[AssistantEvent, ResultEvent]


@dataclass
class SessionOptions:
    model: str
    cwd: str | Path
    system_prompt: Optional[str] = None
    allowed_tools: Optional[list[str]] = None
    permission_mode: str = "bypassPermissions"
    mcp_servers: Optional[dict[str, Any]] = None
    max_turns: Optional[int] = None
    cli_path: Optional[str] = None
    extra: dict[str, Any] = field(default_factory=dict)


class ProviderError(Exception):
    def __init__(self, message: str, code: Optional[str] = None, retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.retryable = retryable


@runtime_checkable
class AgentSession(Protocol):
    async def __aenter__(self) -> "AgentSession": ...
    async def __aexit__(self, *exc: Any) -> None: ...
    async def query(self, task: str) -> None: ...
    def receive_response(self) -> AsyncIterator[ProviderEvent]: ...


@runtime_checkable
class AgentProvider(Protocol):
    name: str

    def session(self, options: SessionOptions) -> AgentSession: ...


# Built-in aliases only — LEGACY_DEFAULT. No other vendor names here.
_BUILTIN_CLAUDE = frozenset({"claude", "claude_sdk", "anthropic"})


def get_agent_provider(name: Optional[str] = None) -> AgentProvider:
    """Factory.

    LEGACY_DEFAULT: AAR_AGENT_PROVIDER in {claude,claude_sdk,anthropic} (default)
      → ClaudeSDKProvider
    EXTERNAL_PLUGIN: any other name (or when AAR_AGENT_PROVIDER_MODULE is set)
      → require AAR_AGENT_PROVIDER_MODULE; optional PATH / CLASS; get_provider() or CLASS()
    """
    name = (name or os.getenv("AAR_AGENT_PROVIDER") or "claude_sdk").strip().lower()
    mod_path = (os.getenv("AAR_AGENT_PROVIDER_MODULE") or "").strip()

    if name in _BUILTIN_CLAUDE and not mod_path:
        from aar.research_loop.providers.claude_sdk import ClaudeSDKProvider
        return ClaudeSDKProvider()

    # EXTERNAL_PLUGIN path — module required; no vendor-specific defaults
    if not mod_path:
        raise ProviderError(
            f"unknown AAR_AGENT_PROVIDER={name!r}: set AAR_AGENT_PROVIDER_MODULE "
            f"to a dotted module exporting get_provider() or AAR_AGENT_PROVIDER_CLASS",
            code="PROVIDER_MODULE_REQUIRED",
        )

    extra_path = (os.getenv("AAR_AGENT_PROVIDER_PATH") or "").strip()
    if extra_path:
        p = str(Path(extra_path).resolve())
        if p not in sys.path:
            sys.path.insert(0, p)

    try:
        mod = importlib.import_module(mod_path)
    except ImportError as e:
        raise ProviderError(
            f"failed to import AAR_AGENT_PROVIDER_MODULE={mod_path!r}: {e}",
            code="PROVIDER_IMPORT_FAILED",
        ) from e

    if hasattr(mod, "get_provider") and callable(mod.get_provider):
        return mod.get_provider()

    cls_name = (os.getenv("AAR_AGENT_PROVIDER_CLASS") or "").strip()
    if cls_name:
        if not hasattr(mod, cls_name):
            raise ProviderError(
                f"module {mod_path!r} has no class {cls_name!r}",
                code="PROVIDER_CLASS_MISSING",
            )
        return getattr(mod, cls_name)()

    raise ProviderError(
        f"module {mod_path!r} has neither get_provider() nor AAR_AGENT_PROVIDER_CLASS",
        code="PROVIDER_FACTORY_MISSING",
    )
