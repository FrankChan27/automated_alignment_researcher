"""Minimal AgentProvider for live-deletion proofs — completes one session instantly."""
from __future__ import annotations
from typing import Any, AsyncIterator, Optional
from aar.research_loop.provider import AssistantEvent, ResultEvent, SessionOptions, TextPart

class FastStubSession:
    def __init__(self, options: SessionOptions):
        self._options = options
        self._task = None
        self._ran = False
    async def __aenter__(self): return self
    async def __aexit__(self, *exc): return None
    async def query(self, task: str) -> None:
        self._task = task
    async def receive_response(self) -> AsyncIterator:
        if self._ran: return
        self._ran = True
        yield AssistantEvent(content=[TextPart(text="FAST_STUB_SESSION_OK")])
        yield ResultEvent(result="FAST_STUB_SESSION_OK", stop_reason="end_turn")

class FastStubProvider:
    name = "neutral_plugin"
    requires_anthropic_key = False
    supports_inprocess_mcp = False
    def session(self, options: SessionOptions) -> FastStubSession:
        return FastStubSession(options)

def get_provider():
    return FastStubProvider()
