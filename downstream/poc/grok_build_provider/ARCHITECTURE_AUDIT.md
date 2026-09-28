# ARCHITECTURE_AUDIT

Baseline re-verified read-only on
`FrankChan27/automated_alignment_researcher`
branch `downstream/aar-provider-002`
HEAD `01067d70f001ee99b229089acd0dba63e7f3a5ed`
(the prompt's historical SHA matches the real branch tip;
`main` is `a6493c288ead7e9e7fbb35311a136c70eca37108` and was not used).

Upstream pin (`downstream/UPSTREAM_PIN.json`):

- repo `YuehHanChen/automated_alignment_researcher`
- pinned SHA `02dbe9d2cadc553720d17cdf6259c0b8727e6cde`

## Baseline claims

| Claim | Re-check | Result |
|---|---|---|
| PROVIDER_ARCHITECTURE | `get_agent_provider()` loads non-legacy providers only via `AAR_AGENT_PROVIDER_MODULE`; no grok name tuple | VENDOR_NEUTRAL |
| CORE_VENDOR_REFERENCES | `grep -RInE -i 'grok\|xai\|x\.ai\|grok_cli\|AAR_GROK\|aar_xai_adapter' aar/research_loop run.py --include='*.py'` | 0 |
| EXTERNAL_PROVIDER_SUPPORTED | module import + `get_provider()` / class env; GrokCLIProvider is one out-of-core implementation | true |
| UPSTREAM_AAR_LOOP_LIVE | `class AutonomousAgentLoop` in `aar/research_loop/agent.py` still owns the session loop; provider-002 review recorded live sessions. This experiment did not re-execute that loop | true (code live; not re-smoked here) |
| PROVIDER_SEAM_LIVE | `BaseAgent._execute_once` still calls `provider.session` / `query` / `receive_response` | true (code live; Build provider not attached) |

Historical Claude/Anthropic code remains in the tree (benchmarks, web UI,
legacy default provider). That matches the prior review: vendor-neutrality
here means **no Grok/xAI knowledge in the researcher-loop core**. The
active path of this experiment did not call Claude.

## Intended chain vs actual chain

Intended:

```
AAR_CORE → PROVIDER_SEAM → EXTERNAL_PROVIDER → BUILD_AGENT_RUNTIME
```

Actual:

```
AAR_CORE → PROVIDER_SEAM → (no Build provider)
BUILD_AGENT_RUNTIME exists only as this chat session and its harness
subagent tool, which guest Python cannot call
```

## Forbidden transports

| Check | Result | Evidence |
|---|---|---|
| GROK_CLI_USED | false | `grok` not on PATH; `grok_cli.py` not executed |
| XAI_API_KEY_USED | false | key present in env, never read or sent |
| CLAUDE_API_USED | false | no Anthropic client call |
| ANTHROPIC_API_USED | false | same |
| Core polluted with Build-specific logic | false | no `aar/` edits |

## This experiment's call chain

Stopped at discovery. No iteration, no state file, no probe string
produced by a provider.
