"""Provider-neutral researcher-inference seam for AutonomousAgentLoop.

No vendor-specific imports here. Backends: claude_sdk (legacy), grok_cli (downstream).
"""
from __future__ import annotations

import importlib
import os
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


def get_agent_provider(name: Optional[str] = None) -> AgentProvider:
    """Factory. AAR_AGENT_PROVIDER=claude_sdk|grok_cli (default claude_sdk)."""
    name = (name or os.getenv("AAR_AGENT_PROVIDER") or "claude_sdk").strip().lower()
    if name in ("claude", "claude_sdk", "anthropic"):
        from aar.research_loop.providers.claude_sdk import ClaudeSDKProvider
        return ClaudeSDKProvider()
    if name in ("grok", "grok_cli", "xai_grok"):
        mod_path = os.getenv(
            "AAR_GROK_PROVIDER_MODULE",
            "aar_xai_adapter_001.provider.grok_cli",
        )
        # Ensure downstream/poc is on path for aar_xai_adapter_001
        poc_root = Path(__file__).resolve().parents[2] / "downstream" / "poc"
        import sys
        if str(poc_root) not in sys.path:
            sys.path.insert(0, str(poc_root))
        mod = importlib.import_module(mod_path)
        if hasattr(mod, "get_provider"):
            return mod.get_provider()
        return mod.GrokCLIProvider()
    raise ProviderError(f"unknown AAR_AGENT_PROVIDER={name!r}", code="UNKNOWN_PROVIDER")
