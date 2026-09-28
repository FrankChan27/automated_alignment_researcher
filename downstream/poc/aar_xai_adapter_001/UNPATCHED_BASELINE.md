# UNPATCHED_BASELINE — AAR-xAI-adapter-001

**Date:** 2026-09-28T09:07:33+08:00
**HEAD_AT_FREEZE:** b5c3dd3c3f9db8f2acd2a0edb05917c9aaf11df0
**PINNED_UPSTREAM_SHA:** 02dbe9d2cadc553720d17cdf6259c0b8727e6cde

## Entry gate

```
ANTHROPIC_API_KEY_SET=false
CMD: python run.py agent --idea-uid unpatched --idea-name unpatched --local --max-iterations 1
Error: ANTHROPIC_API_KEY is required for agent mode
EXIT=0
```

## Hard-bind citations

- `run.py:33-35` — requires ANTHROPIC_API_KEY
- `aar/research_loop/agent.py:21-28` — imports ClaudeSDKClient / ClaudeAgentOptions / message types
- `BaseAgent._execute_once` — `async with ClaudeSDKClient`
- Tools: `claude_agent_sdk.tool` / `create_sdk_mcp_server`

## Verdict

| Field | Value |
|-------|-------|
| UNPATCHED_AGENT_ENTRY | BLOCKED |
| CLAUDE_HARD_BIND | true |
| PROVIDER_INTERFACE_EXISTS | false |
