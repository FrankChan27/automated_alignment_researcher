# FINAL_CASE ladder (A–F) — as applied for AAR-xAI-OAuth-001

Derived from mission hard rules (HUMAN=0; CASE D on OAuth consent; A/B justify ≤1 inference smoke).

| Case | Condition | Typical CAN |
|------|-----------|-------------|
| **A** | Local xAI/Grok **OAuth session PRESENT** + one inference smoke returns exact `XAI_OAUTH_RESEARCHER_SMOKE_OK` | true |
| **B** | Local OAuth session PRESENT + authenticated **models/account metadata** OK; smoke not run or not needed | true |
| **C** | No local session, but **official** docs document a non-interactive OAuth path usable by AAR researcher against an official inference surface | true (docs-only) |
| **D** | Next OAuth step requires **human browser/device consent** (`XAI_OAUTH_HUMAN_GATE=REQUIRED`); stop; no login automation | unknown |
| **E** | Official surfaces show researcher/public API is **API-key-only**; OAuth is Grok Build/CLI (or web) only; no official portable OAuth for AAR researcher without reverse-engineering; and no usable local CLI session | false |
| **F** | Evidence conflicting or insufficient after Phase 1; cannot pick A–E | unknown |

Phase 2 (TEST 2–5) only if Phase 1 justifies A/B path.
