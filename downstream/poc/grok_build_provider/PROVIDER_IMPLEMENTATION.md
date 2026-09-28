# PROVIDER_IMPLEMENTATION

## Decision

`EXTERNAL_PROVIDER_IMPLEMENTED=false`

No `GrokBuildAgentProvider` (or equivalent) was added. Phase 2 of the
experiment says to implement only **if** a usable invocation surface
exists. It does not. A class that returns canned text, shells out to
`grok`, or calls `XAI_API_KEY` would fail the acceptance criteria and
the false-positive list.

## Seam that would have been used (unchanged)

Verified on `downstream/aar-provider-002` @ `01067d70f001ee99b229089acd0dba63e7f3a5ed`.

- `aar/research_loop/agent.py`: `AutonomousAgentLoop` constructs
  `BaseAgent`, which calls `provider.session(SessionOptions)` then
  `query` / `receive_response`.
- `aar/research_loop/provider.py`: `get_agent_provider()`.
  - Legacy names `claude` / `claude_sdk` / `anthropic` and no module →
    built-in `ClaudeSDKProvider`.
  - Any other label **requires** `AAR_AGENT_PROVIDER_MODULE`.
  - Factory: `get_provider()` or `AAR_AGENT_PROVIDER_CLASS`.
  - Optional `AAR_AGENT_PROVIDER_PATH` prepended to `sys.path`.
- Capability flags, not vendor name branches:
  `requires_anthropic_key`, `supports_inprocess_mcp`.
- Historical external example (not used here):
  `downstream/poc/aar_provider_002/providers/grok_cli.py`
  (`GrokCLIProvider`). Left in place.

A future provider, if a runtime surface appears, would live only under
`downstream/poc/...` and export `get_provider()` returning an object
with `name`, `requires_anthropic_key=False`,
`supports_inprocess_mcp=False`, and `session()`.

## Core edits this experiment

None. `git diff` against `01067d70` for `aar/` and `run.py` is empty
aside from these new `downstream/poc/grok_build_provider/` documents.
