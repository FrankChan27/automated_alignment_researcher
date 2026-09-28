"""Claude Agent SDK backend — preserves upstream default researcher path."""
from __future__ import annotations

from typing import Any, AsyncIterator, Optional

from aar.research_loop.provider import (
    AgentProvider,
    AgentSession,
    AssistantEvent,
    ProviderError,
    ResultEvent,
    SessionOptions,
    TextPart,
    ThinkingPart,
    ToolUsePart,
)


class ClaudeSDKSession:
    def __init__(self, options: SessionOptions):
        self._options = options
        self._client = None
        self._task: Optional[str] = None

    async def __aenter__(self) -> "ClaudeSDKSession":
        try:
            from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
        except ImportError as e:
            raise ProviderError(
                f"claude_agent_sdk not installed: {e}",
                code="CLAUDE_SDK_MISSING",
                retryable=False,
            ) from e
        opt = self._options
        options_dict: dict[str, Any] = {
            "allowed_tools": opt.allowed_tools or [],
            "system_prompt": opt.system_prompt,
            "permission_mode": opt.permission_mode,
            "cwd": str(opt.cwd),
            "model": opt.model,
            "mcp_servers": opt.mcp_servers or {},
            "setting_sources": opt.extra.get("setting_sources", ["project"]),
            "betas": opt.extra.get("betas", ["context-1m-2025-08-07"]),
            "thinking": opt.extra.get("thinking", {"type": "adaptive", "display": "summarized"}),
            "effort": opt.extra.get("effort", "max"),
        }
        if opt.cli_path:
            options_dict["cli_path"] = opt.cli_path
        self._ClaudeSDKClient = ClaudeSDKClient
        self._client_cm = ClaudeSDKClient(options=ClaudeAgentOptions(**options_dict))
        self._client = await self._client_cm.__aenter__()
        return self

    async def __aexit__(self, *exc: Any) -> None:
        if self._client_cm is not None:
            await self._client_cm.__aexit__(*exc)

    async def query(self, task: str) -> None:
        self._task = task
        await self._client.query(task)

    async def receive_response(self) -> AsyncIterator:
        from claude_agent_sdk import (
            AssistantMessage,
            ResultMessage,
            TextBlock,
            ToolUseBlock,
        )
        async for message in self._client.receive_response():
            if isinstance(message, ResultMessage):
                yield ResultEvent(result=getattr(message, "result", None), stop_reason="result")
                return
            if isinstance(message, AssistantMessage):
                parts = []
                for content in message.content:
                    if isinstance(content, TextBlock):
                        parts.append(TextPart(text=content.text))
                    elif isinstance(content, ToolUseBlock):
                        parts.append(
                            ToolUsePart(
                                name=content.name,
                                input=content.input or {},
                                id=getattr(content, "id", None),
                            )
                        )
                    elif hasattr(content, "thinking"):
                        parts.append(ThinkingPart(thinking=content.thinking))
                yield AssistantEvent(content=parts)


class ClaudeSDKProvider:
    name = "claude_sdk"

    def session(self, options: SessionOptions) -> ClaudeSDKSession:
        return ClaudeSDKSession(options)
