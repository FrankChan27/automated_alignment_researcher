# CORE_PATCH meta

| Field | Value |
|-------|-------|
| CORE_PATCH_REQUIRED | true |
| CORE_PATCH_FILES | aar/research_loop/agent.py, aar/research_loop/provider.py, aar/research_loop/providers/__init__.py, aar/research_loop/providers/claude_sdk.py, run.py |
| CORE_PATCH_LINES_ADDED | 310 |
| CORE_PATCH_LINES_REMOVED | 98 |
| WHY | UNPATCHED has no Provider interface; ClaudeSDKClient hard-imported in agent.py + ANTHROPIC_API_KEY gate in run.py. Minimal unbind so Grok CLI OIDC backend can drive AutonomousAgentLoop without grok code in core. |
| RESTORE_CLAUDE_HARD_BIND | `git checkout HEAD -- run.py aar/research_loop/agent.py && rm -rf aar/research_loop/provider.py aar/research_loop/providers` → ANTHROPIC_API_KEY gate + ClaudeSDKClient import return. |

Audit: core contains **zero** grok-specific imports. Grok lives under `downstream/poc/aar_xai_adapter_001/provider/`.
