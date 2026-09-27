# CASE ladder (mission-frozen) — aar_xai_oauth_001

**Authoritative definitions:** see `AUTH_SURFACE_MAP.md` (mission A–F).  
Do **not** use the earlier local draft that mapped Human Gate → D.

| CASE | Meaning (short) | CAN |
|------|-----------------|-----|
| A | OAuth session → real official inference without new API key | true |
| B | OAuth tokens OK but inference blocked/wrong audience/entitlement | false |
| C | Device/headless OAuth documented; stopped at HUMAN_GATE | null/unknown |
| D | Only API-key works for inference; OAuth cannot reach inference | false |
| E | No usable public OAuth surface | false |
| F | Ambiguous / incomplete for non–Human-Gate reasons | null/unknown |

**This run: CASE C** (`HUMAN_GATE=true`). See `LADDER.md`, `REPORT.md`, `STATUS.json`.
