"""Deterministic failing external provider — honest error, no fabricated result."""
from __future__ import annotations

from typing import Any, AsyncIterator, Optional

from aar.research_loop.provider import ProviderError, SessionOptions


class FakeFailSession:
    def __init__(self, options: SessionOptions):
        self._options = options
        self._task: Optional[str] = None

    async def __aenter__(self) -> "FakeFailSession":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        return None

    async def query(self, task: str) -> None:
        self._task = task

    async def receive_response(self) -> AsyncIterator:
        raise ProviderError(
            "fake provider deliberately failed",
            code="FAKE_PROVIDER_FAILURE",
            retryable=False,
        )
        yield  # pragma: no cover — make this an async generator


class FakeFailProvider:
    name = "fake_fail"
    requires_anthropic_key = False
    supports_inprocess_mcp = False

    def session(self, options: SessionOptions) -> FakeFailSession:
        return FakeFailSession(options)


def get_provider() -> FakeFailProvider:
    return FakeFailProvider()
