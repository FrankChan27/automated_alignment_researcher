"""Deterministic successful external provider (no network, no vendor)."""
from __future__ import annotations

from typing import Any, AsyncIterator, Optional

from aar.research_loop.provider import (
    AssistantEvent,
    ResultEvent,
    SessionOptions,
    TextPart,
)


class FakeOkSession:
    def __init__(self, options: SessionOptions):
        self._options = options
        self._task: Optional[str] = None

    async def __aenter__(self) -> "FakeOkSession":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        return None

    async def query(self, task: str) -> None:
        self._task = task

    async def receive_response(self) -> AsyncIterator:
        text = f"FAKE_OK_RESULT task_len={len(self._task or '')}"
        yield AssistantEvent(content=[TextPart(text=text)])
        yield ResultEvent(result=text, stop_reason="end_turn")


class FakeOkProvider:
    name = "fake_ok"
    requires_anthropic_key = False
    supports_inprocess_mcp = False

    def session(self, options: SessionOptions) -> FakeOkSession:
        return FakeOkSession(options)


def get_provider() -> FakeOkProvider:
    return FakeOkProvider()
