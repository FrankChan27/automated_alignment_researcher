# REVIEW — AAR-provider-002

- **Reviewer role:** independent adversarial PHASE-8 review (did not implement; no Cursor CloudAgent)
- **Freeze SHA reviewed:** `5d49ce1a50b4236b3bc797822d517809d2741573` (git tip on `downstream/aar-provider-002`; matches mission FREEZE_SHA)
- **IMPLEMENTATION_SHA (code):** `8ccffdaa70060d1e25412a4e3f434b7ea153da1d`
- **Baseline:** REVIEW `cb57ed923548c7daf319ef05bc0e44aa0afeea88` / FREEZE `7ed5c43940dececf7b9c8ca68abf41c64ed7296e`
- **Timestamp (UTC+8):** 2026-09-28T10:16:06+0800

## Verdict: **PASS_WITH_NITS**

## Executive summary

Core no longer names Grok/xAI: `aar/research_loop/provider.py` loads externals only via `AAR_AGENT_PROVIDER_MODULE` + capability flags; adversarial `rg` over `aar/research_loop/**/*.py` + `run.py` finds **zero** `grok|xai|AAR_GROK|aar_xai_adapter` hits. Six fresh TRACE sessions under `AutonomousAgentLoop` + `aar_provider_002.providers.grok_cli` hash-chain to live workspace STATE; adapter-001 nits #8/#10 (NIT_1/NIT_2) are **CLOSED**. Residual nits: provenance HEAD/FREEZE lag, raw `stop_reason=unknown`, empty `session_003` log, Claude regression construct-only, and after-delete failures still land at import (baseline *did* enter `run()`). Hard rule satisfied — vendor-specific Grok/xAI knowledge is gone from core — so FAIL is not warranted; rubber-stamp PASS is not either.

---

## Checklist attacks 1–12

### 1 — Core still secretly knows Grok/xAI — **PASS** (MISS)

**Evidence:**
- Independent scan: `rg -n -i 'grok|xai|x\.ai|grok_cli|AAR_GROK|aar_xai_adapter' aar/research_loop/ run.py --glob '*.py'` → **no matches** (exit 1).
- `CORE_VENDOR_SCAN.txt` / `evidence/CORE_VENDOR_SCAN.txt` claim `CORE_VENDOR_REFERENCES=0` — corroborated.
- Baseline `provider.py` at `7ed5c43` still had `("grok","grok_cli","xai_grok")`, default `aar_xai_adapter_001.provider.grok_cli`, `AAR_GROK_PROVIDER_MODULE`. Tip `provider.py:85-141` replaces that with `_BUILTIN_CLAUDE` + required MODULE importlib path only.
- `agent.py` / `run.py` branch on `supports_inprocess_mcp` / `requires_anthropic_key`, not grok name tuples (`CORE_PATCH.diff` byte-identical to `git diff 7ed5c43..HEAD` for listed core files).
- False positive only: base64 integrity strings containing substring `xai` inside `aar/web_ui/frontend/package-lock.json` — not control-flow knowledge.

**Why:** Hard-rule vendor knowledge (Grok/xAI) purged from core `.py`. Built-in Claude/Anthropic aliases remain by design (LEGACY_DEFAULT).

### 2 — Generic loader only works for Grok — **PASS** (MISS)

**Evidence:**
- Same factory loads `aar_provider_002.providers.fast_stub` and `neutral_plugin` (deletion/rename proofs) and `grok_cli` (PHASE4).
- Live smoke this review: `AAR_AGENT_PROVIDER=external` + MODULE=`…fast_stub` → `FastStubProvider`; MODULE unset + name=`grok_cli` → `ProviderError(code=PROVIDER_MODULE_REQUIRED)` (no baked grok default).
- `phase3_external_load.txt`: `EXTERNAL_LOAD_OK grok_cli …`.

**Why:** Loader is module-path generic; stubs prove non-Grok plugins enter the seam.

### 3 — Provider rename requires core change — **PASS** (MISS)

**Evidence:**
- `PROVIDER_RENAME_PROOF.md` / `evidence/rename_proof.txt`: MODULE `fast_stub` → `neutral_plugin`; `CORE_EDITS=0`; `CORE_SHA_BEFORE == CORE_SHA_AFTER`; `ENTERED_LOOP_RUN` + EXIT=0.
- `EXT_CLI_LOAD grok_cli aar_provider_002.providers.ext_cli` — renamed copy of grok transport loads without core edits.

**Residual NIT:** Multi-session research rename used stub, not a renamed grok module for ≥5 rounds. Still sufficient to refute “rename requires core change.”

### 4 — Rewrote AutonomousAgentLoop — **PASS** (MISS)

**Evidence:**
- `git diff 7ed5c43..HEAD -- aar/research_loop/agent.py`: ~19 lines — docstring, MCP gate → capability flag, provider cache, print string. Scheduler / stop / session loop untouched.
- Core touch set: `agent.py`, `provider.py`, `providers/__init__.py`, `providers/claude_sdk.py`, `run.py` only.

**Why:** Seam cleanup, not rewrite.

### 5 — Objective changed — **PASS** (MISS)

**Evidence:**
- `scripts/run_native_loop.py` PROMPT: “OBJECTIVE (unchanged from AAR-POC-002)” 8D integer vector / hillclimb + capability filter; eval via `python -m aar_poc_002.adapter.eval`.
- TRACE proposals are 8-int vectors with POC-002-style `headline_pct` scores; live STATE last vector `[22,25,50,50,50,50,50,50]` score 41.01.

**Why:** Objective text and eval path match POC-002; no new objective baked into core.

### 6 — New 5+ rounds not really re-run (reused adapter-001) — **PASS** (MISS)

**Evidence:**
- TRACE `RUN_ID=provider002-20260928-094436`, 6 rows ITERATION 0..5; adapter-001 TRACE run_ids disjoint; hash-pair overlap with adapter-001 = **0**.
- Session logs under `evidence/session_logs/` dated 2026-09-28 09:44–10:12 with `poc002_8d_vector` names (not adapter-001 paths).
- `LOOP_RESULT.json` documents initial 0–2 + continuation 3–5 same RUN_ID; `LOOP_5ITER.txt` shows continuation banner + 3 sessions; partial3 matches first three TRACE rows.
- Live `/home/box/aar-provider-002-runs/workspace/STATE.json` sha256[:16] = `d8cf9052b69cec12` == TRACE final `STATE_HASH_AFTER`.

**Why:** Fresh run, not copied adapter-001 evidence. Continuation merge is disclosed and hash-linked.

### 7 — Hash chain fake — **PASS** (MISS)

**Evidence:** Recomputed: each row `STATE_HASH_BEFORE` == prior `STATE_HASH_AFTER` for all 6 rows; live STATE matches final AFTER. `HASH_CHAIN_OK=true` verified independently.

### 8 — Deletion is import-only not live run — **PASS** (MISS) — closes baseline NIT_2

**Evidence:**
- Baseline HIT #10: no `run()` before/after; `*_BREAKS_RUN` overclaim.
- Now: `deletion_A.txt` / `deletion_B.txt` show `ENTERED_LOOP_RUN`, full Autonomous Agent Loop banner, session complete, `A_BASELINE_EXIT=0` / `B_BASELINE_EXIT=0`, then delete → EXIT=1.
- `deletion_*_entered.json`: `entered_run: true`, `completed: true`, `sessions: 1`.
- Harness `live_deletion_harness.py` explicitly `await loop.run()`.

**Residual NIT:** After-delete path still fails at **import** (`ModuleNotFoundError` / `PROVIDER_IMPORT_FAILED`) — expected after deleting `agent.py` or provider package. Claim `*_DELETION_BREAKS_RUN` remains slightly stronger than “after” mechanics, but baseline-enter-run requirement is met → NIT_2 **CLOSED**.

### 9 — Claude legacy broken — **PASS** (MISS) with residual NIT

**Evidence:**
- `phase3_claude_stub.txt`: `CLAUDE_CONSTRUCT_OK claude_sdk`.
- `claude_sdk.py` sets `requires_anthropic_key=True`, `supports_inprocess_mcp=True`.
- `phase3_run_gate.txt`: Claude gate requires key; external gate allows no key.
- This review: `get_agent_provider()` with `claude_sdk` returns `ClaudeSDKProvider` with flags True/True.

**Residual NIT:** No Anthropic **live** runtime (COMPATIBILITY admits construct/import only). Legacy load path not proven end-to-end without a key — acceptable for this mission’s core question, not a full Claude soak.

### 10 — Secret leak — **PASS** (MISS)

**Evidence:**
- Independent scan of OUT: no `eyJ…` JWTs, no committed `refresh_token`/`access_token` values, no `auth.json` bodies — only boolean probes (`HAS_REFRESH_TOKEN`) in provider code.
- `evidence/SECRET_SCAN.txt`: `hits=0`, `OAUTH_SECRET_IN_REPO=false`.
- Provider strips `XAI_API_KEY` / `ANTHROPIC_API_KEY` from subprocess env (`grok_cli.py:128-132`).

### 11 — Provenance inconsistent — **NIT** (not FAIL)

**Evidence:**
- `provenance.json`: `HEAD_SHA=7f5f063…`, `IMPLEMENTATION_SHA=8ccffda…`, `FREEZE_SHA=null`, `REVIEW_SHA=null`.
- `STATUS.md` HEAD_SHA same `7f5f063` while git tip / mission FREEZE is `5d49ce1` (two chore commits after implementation).
- Mission note allows HEAD lag vs tip; still the same class of provenance nit called out on adapter-001.

**Why:** Does not falsify runtime/core claims; blocks clean PASS.

### 12 — One Grok plugin success inflated to all providers verified — **PASS** (MISS) with residual NIT

**Evidence:**
- Claimed: `CAN_AAR_LOAD_EXTERNAL_RESEARCHER_PROVIDER_WITHOUT_VENDOR_KNOWLEDGE=true` + `PROVIDER_ARCHITECTURE=VENDOR_NEUTRAL` — architecture/loader claims, not “every vendor transport soak-tested.”
- Supporting: generic MODULE loader; stub + neutral_plugin + ext_cli + grok_cli all load; only grok_cli drove 6 research sessions.

**Residual NIT:** Do not read CASE A as multi-vendor production certification. One real transport + stubs verify the seam.

---

## NIT_1 / NIT_2 closure status

| ID | Baseline attack | Status | Evidence |
|----|-----------------|--------|----------|
| **NIT_1** | #8 Core beyond neutral seam — grok aliases / `AAR_GROK_*` / default `aar_xai_adapter_001` / name-match auth-MCP | **CLOSED** | Tip core scan 0 grok/xAI hits; capability flags in `agent.py:420-467`, `run.py:33-41`; `provider.py` MODULE-required externals |
| **NIT_2** | #10 Deletion import-only; `*_BREAKS_RUN` overclaim | **CLOSED** | Baseline enters `loop.run()` (`ENTERED_LOOP_RUN` + completed session) before delete; after EXIT≠0. Residual wording nit on after=import failure retained above |

---

## Claimed vs verified

| Claim | Claimed | Verified |
|-------|---------|----------|
| FINAL_CASE_SUGGESTION | A | **Allowed with nits** (reviewer) |
| CAN_AAR_LOAD_EXTERNAL…WITHOUT_VENDOR_KNOWLEDGE | true | **true** |
| PROVIDER_ARCHITECTURE | VENDOR_NEUTRAL | **VENDOR_NEUTRAL** (externals; Claude built-in remains) |
| CORE_VENDOR_REFERENCES | 0 | **0** (Grok/xAI in core `.py`) |
| SESSIONS | 6 | **6** (TRACE + 6 non-empty logs; +1 empty `session_003` artifact) |
| HASH_CHAIN_OK | true | **true** (recomputed + live STATE match) |
| LIVE_DELETION_A/B | true | **true** (run-entered baseline; after fail) |
| PROVIDER_RENAME_WITHOUT_CORE_CHANGE | PASS | **PASS** |
| BASELINE_NIT_1 / NIT_2 | CLOSED | **CLOSED** |
| ANTHROPIC_USED / API_KEY_USED / CURSOR_USED | false | **false** (TRACE + transport confirm; keys stripped) |
| OAUTH_SECRET_IN_REPO | false | **false** |
| provenance HEAD == tip | (implied) | **false** — lag to `5d49ce1` |
| Raw loop `stop_reason` | max_iterations (LOOP_RESULT) | LOOP_RESULT normalized; raw print still `unknown` (`STOP_REASON_NOTE.txt`) |

---

## Residual risks / nits

1. **Provenance:** `HEAD_SHA` / `FREEZE_SHA` not aligned to tip `5d49ce1`; `FREEZE_SHA=null` until post-review pin.
2. **stop_reason:** Upstream print path still `reason=unknown` on max_iterations; OUT script normalizes LOOP_RESULT only (explicitly avoided rewriting scheduler — correct tradeoff, lingering observability nit).
3. **Empty** `session_logs/session_003_poc002_8d_vector_20260928_095531.log` (0 bytes) unexplained artifact beside six real sessions.
4. **Claude live** path unexercised (construct + gate only).
5. **`supports_inprocess_mcp=True` still sets `cli_path=shutil.which("claude")`** (`agent.py:479`) — Anthropic CLI assumption coupled to MCP capability (built-in path; not Grok knowledge).
6. After-delete still import-fail; rename soak used stub not grok multi-session.

---

## Final verdict justification

Hard rule: *vendor-specific knowledge remaining in core ⇒ cannot PASS.* Independent scan shows **no** Grok/xAI control-flow or string knowledge in core researcher `.py`; loader is env-module generic; adapter-001 NIT_1 and NIT_2 are closed with concrete run/delete and purge evidence; six native sessions hash-chain to disk. That supports CASE A / CAN=true / VENDOR_NEUTRAL.

Remaining provenance, stop_reason, empty log, and Claude-construct-only gaps are real but do not restore vendor knowledge into core or invalidate the live external-provider demonstration. Therefore **PASS_WITH_NITS**, not FAIL, and not a clean PASS.

**Reviewer FINAL_CASE stance:** **A (allowed with nits).**
