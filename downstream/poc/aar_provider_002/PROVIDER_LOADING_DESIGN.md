# PROVIDER_LOADING_DESIGN — AAR-provider-002 PHASE 1

## Factory algorithm (`get_agent_provider`)

```
name = (AAR_AGENT_PROVIDER or "claude_sdk").strip().lower()
if name in {"claude", "claude_sdk", "anthropic"} AND not AAR_AGENT_PROVIDER_MODULE:
    return ClaudeSDKProvider()   # LEGACY_DEFAULT
# EXTERNAL_PLUGIN
mod = AAR_AGENT_PROVIDER_MODULE
if not mod:
    raise ProviderError("set AAR_AGENT_PROVIDER_MODULE for non-built-in provider",
                        code="PROVIDER_MODULE_REQUIRED")
if AAR_AGENT_PROVIDER_PATH: sys.path insert
m = importlib.import_module(mod)
if hasattr(m, "get_provider"): return m.get_provider()
cls_name = AAR_AGENT_PROVIDER_CLASS or None
if cls_name: return getattr(m, cls_name)()
raise ProviderError("module lacks get_provider() / CLASS", code="PROVIDER_FACTORY_MISSING")
```

No vendor branches. Built-in set is **claude aliases only**.

## Call-site changes

### `run.py`

```python
from aar.research_loop.provider import get_agent_provider
prov = get_agent_provider()
if getattr(prov, "requires_anthropic_key", True) and not os.getenv("ANTHROPIC_API_KEY"):
    sys.exit(1)
```

### `AutonomousAgentLoop.__init__` / `_create_agent`

```python
self._provider = get_agent_provider()
if getattr(self._provider, "supports_inprocess_mcp", False):
    # create MCP servers (existing Claude path)
else:
    self.mcp_servers = {}
    print("[Init] provider supports_inprocess_mcp=False — skipping in-process MCP")
# _create_agent: use supports_inprocess_mcp for mcp__ allowlist + cli_path=claude
```

## External package layout (OUT)

```
aar_provider_002/
  providers/
    __init__.py
    grok_cli.py      # GrokCLIProvider + get_provider(); flags False/False
  scripts/
    run_native_loop.py
    live_deletion_proof.sh
    rename_proof.sh
```

Runtime env example:

```
AAR_AGENT_PROVIDER=external
AAR_AGENT_PROVIDER_MODULE=aar_provider_002.providers.grok_cli
AAR_AGENT_PROVIDER_PATH=<repo>/downstream/poc   # if needed
```

## Rename proof (PHASE 6)

Copy/move module to neutral name (e.g. `aar_provider_002.providers.ext_cli`); change **only** env module path; zero core edits; loop still loads.

## Live deletion (PHASE 5)

Scratch tree: baseline must enter `AutonomousAgentLoop.run()` (session attempt), then delete core loop OR external provider module; same command fails. Document `*_DELETION_BREAKS_RUN` only with run-path evidence.
