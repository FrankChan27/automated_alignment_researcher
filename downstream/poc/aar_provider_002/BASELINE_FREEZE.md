# BASELINE_FREEZE — AAR-provider-002 PHASE 0

Read-only verification of adapter-001 freeze/review. **No mutation** of `aar_xai_adapter_001/` evidence.

| Field | Value |
|-------|-------|
| BASELINE_MISSION | AAR-xAI-adapter-001 |
| BASELINE_REVIEW_SHA | `cb57ed923548c7daf319ef05bc0e44aa0afeea88` |
| BASELINE_FREEZE_SHA | `7ed5c43940dececf7b9c8ca68abf41c64ed7296e` |
| BASELINE_FINAL_CASE | A |
| BASELINE_REVIEW_VERDICT | PASS_WITH_NITS |
| BASELINE_CAN | CAN_AAR_NATIVE_RESEARCH_LOOP_RUN_WITH_XAI_OAUTH=true (allowed with nits) |
| BRANCH_THIS | downstream/aar-provider-002 |
| TIP_AT_PHASE0 | 9ef1c16 (scaffold) |
| HUMAN | 0 |
| timestamp_utc8 | 2026-09-28T09:42+08 |

## Nits carried OPEN (attacks this mission closes)

| ID | REVIEW attack | Status |
|----|---------------|--------|
| NIT_1 | #8 Core patch beyond provider-neutral seam — grok aliases / `AAR_GROK_PROVIDER_MODULE` / default `aar_xai_adapter_001...` hardcoded in core; agent.py+run.py name-match grok | **OPEN** |
| NIT_2 | #10 Deletion proof fake — import-only; `*_DELETION_BREAKS_RUN` overclaims RUN | **OPEN** |

## Additional baseline nits (address if cheap)

- provenance HEAD stale vs FREEZE
- stop_reason "unknown" despite max_iterations
- EXIT conflicts (raw-first)

## Verified artifacts (read-only)

- `downstream/poc/aar_xai_adapter_001/REVIEW.md` — PASS_WITH_NITS; #8 HIT medium; #10 HIT medium
- `downstream/poc/aar_xai_adapter_001/STATUS.md` / `STATUS.json` — FINAL_CASE=A; SESSIONS=5
- `downstream/poc/aar_xai_adapter_001/provider/grok_cli.py` — transport-only GrokCLIProvider + get_provider()
- Core still contains grok branches (provider.py / agent.py / run.py) as of tip 9ef1c16

## Core question this mission must answer

`CAN_AAR_LOAD_EXTERNAL_RESEARCHER_PROVIDER_WITHOUT_VENDOR_KNOWLEDGE`

Only CASE A ⇒ CAN=true + PROVIDER_ARCHITECTURE=VENDOR_NEUTRAL. Vendor knowledge remaining in core ⇒ cannot PASS.
