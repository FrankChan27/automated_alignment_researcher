# CASE ladder — aar_xai_oauth_001

Mission-authoritative C/D (user brief / coordinator). **Do not redefine.**

| CASE | Flag | Meaning |
|------|------|---------|
| **C** | `XAI_OAUTH_AUTH_ONLY=PASS` | OAuth login 真实存在, but cannot prove programmatic inference we need |
| **D** | `XAI_OAUTH_HUMAN_GATE=REQUIRED` | Official OAuth path exists; env not yet authorized; stop at consent (not a failure) |

**This run: FINAL_CASE=D** (`HUMAN_GATE=REQUIRED`; AUTH_ONLY not PASS). See `STATUS.json`, `REPORT.md`, `LADDER.md`.
