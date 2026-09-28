# COMPATIBILITY_REGRESSION — AAR-provider-002 PHASE 3

| Check | Result | Evidence |
|-------|--------|----------|
| ClaudeSDKProvider construct (no Anthropic runtime) | PASS | evidence/phase3_claude_stub.txt |
| Claude requires_anthropic_key=True / supports_inprocess_mcp=True | PASS | phase3_claude_stub.txt |
| External GrokCLIProvider via AAR_AGENT_PROVIDER_MODULE | PASS | evidence/phase3_external_load.txt |
| External requires_anthropic_key=False / supports_inprocess_mcp=False | PASS | phase3_external_load.txt |
| Unknown name without MODULE → ProviderError | PASS | (PHASE2 smoke) |
| CORE_VENDOR_REFERENCES | 0 | evidence/CORE_VENDOR_SCAN.txt |
| No Anthropic / xAI API key on researcher path | true | keys unset in tests |

NO Anthropic live runtime invoked in PHASE 3 (construction/import only).
