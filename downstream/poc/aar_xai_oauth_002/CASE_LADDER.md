# FINAL_CASE ladder (A–F) — AAR-xAI-OAuth-002 mission defs

| Case | Condition |
|------|-----------|
| **A** | Native inference PASS (local OAuth session + smoke returns exact `XAI_OAUTH_RESEARCHER_SMOKE_OK`) |
| **B** | Session OK; inference blocked |
| **C** | Login failed |
| **D** | Human gate pending (only if still waiting for consent) |
| **E** | Capability partial |
| **F** | Ready for adapter |

This ladder supersedes oauth-001's A–F meanings for this POC.
