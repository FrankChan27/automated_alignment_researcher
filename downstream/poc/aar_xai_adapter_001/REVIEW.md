# REVIEW — AAR-xAI-adapter-001

**Reviewer:** AAR-xAI-adapter审阅 (independent; did not implement)  
**Review time (UTC+8):** 2026-09-28T09:40+0800  
**Verdict:** **PASS_WITH_NITS**

Integration claim `CAN_AAR_NATIVE_RESEARCH_LOOP_RUN_WITH_XAI_OAUTH=true` is substantively supported: five sessions drove upstream `AutonomousAgentLoop` through a provider seam into official `grok` CLI with local OIDC, without Anthropic / API key / Cursor on the researcher path. Hash chain verifies against the live run workspace.

Two checklist HITs are packaging/meta overclaims (grok names baked into core; deletion “BREAKS_RUN” is import-only). They do **not** invalidate the native-loop + OIDC runtime result. Integration PASS may stand **with nits**. Do not rubber-stamp “zero grok in core” or `*_DELETION_BREAKS_RUN=true` as currently written.

This is **not** a homemade-loop FAIL (attacks #1 / #5 miss).

---

## Freeze identity

| Field | Value |
|-------|-------|
| FREEZE_SHA | `7ed5c43940dececf7b9c8ca68abf41c64ed7296e` |
| BASE_SHA | `00ba33b51d6b78cbb0844268fc437d64cd6e0c31` |
| PINNED_UPSTREAM_SHA | `02dbe9d2cadc553720d17cdf6259c0b8727e6cde` |
| BRANCH | `downstream/aar-xai-adapter-001` |
| OUT | `downstream/poc/aar_xai_adapter_001/` |
| Claimed FINAL_CASE | A |
| provenance.json HEAD | `bfda3be8e05bf9a38f06ed4c03fc6ffaf371d407` (**stale** vs FREEZE) |
| oauth-002 mutation BASE..FREEZE | **none** |
| CORE_PATCH.diff vs tree | **byte-identical** to `git diff BASE..FREEZE` for listed core files |
| GrokCLIProvider location | downstream-only `provider/grok_cli.py` |

Core files touched BASE..FREEZE: `run.py`, `aar/research_loop/agent.py`, new `provider.py`, new `providers/claude_sdk.py`, `providers/__init__.py` (310 / 98; matches META).

---

## Attack checklist

| # | Attack | VERDICT | Severity |
|---|--------|---------|----------|
| 1 | Fake POC-001-style loop | **MISS** | — |
| 2 | Adapter steals scheduler | **MISS** | — |
| 3 | Native evaluator replaced | **MISS** (gap noted) | low |
| 4 | Objective changed | **MISS** | — |
| 5 | Only first round AAR then homemade loop | **MISS** | — |
| 6 | Documented capability as runtime evidence | **MISS** (nits) | low |
| 7 | OAuth secret leak | **MISS** | — |
| 8 | Core patch beyond provider-neutral seam | **HIT** | **medium** |
| 9 | CASE A OAuth success swapped for AAR integration | **MISS** | — |
| 10 | Deletion proof fake | **HIT** | **medium** |

---

## Cross-checks

**Sessions / hash chain**

- `evidence/ITERATION_TRACE.jsonl`: 5 rows (ITERATION 0..4), `PROVIDER=grok_cli`, `API_KEY_USED=false`.
- Each `STATE_HASH_BEFORE` equals prior `STATE_HASH_AFTER` → HASH_CHAIN_OK (recomputed).
- Final workspace `/home/box/aar-xai-adapter-001-runs-5b/workspace/STATE.json` hashes to TRACE row 4 AFTER.
- `evidence/session_logs/` has five session logs (`000`..`004`).
- `LOOP_RESULT.json`: `sessions=5`, `duration_seconds≈463.5`; `stop_reason` remains `"unknown"` (upstream quirk on max_iterations break).

**Transport**

- `RESEARCHER_TRANSPORT_CONFIRM.txt`: `AAR_AGENT_PROVIDER=grok_cli`, Anthropic key unset; strips Anthropic/xAI keys from subprocess env.
- `auth_metadata_probe.json`: `auth_mode=oidc`, `oidc_issuer=https://auth.x.ai` (booleans only; no secret values in OUT).
- `provider/grok_cli.py`: `grok --single … --verbatim --model …` with local OIDC.

**Patch / placement / oauth-002**

- CORE_PATCH.diff matches live tree diff for the five core paths.
- Implementation class is downstream-only; core still **names** grok (see #8).
- Adapter scripts import `AutonomousAgentLoop` only; no `aar_poc_001` / `run_loop` usage.
- `git diff BASE..FREEZE -- downstream/poc/aar_xai_oauth_002/` empty.

---

## Detailed findings

### 1 — Fake POC-001-style loop — MISS

`scripts/run_native_loop.py` constructs `AutonomousAgentLoop` and `await loop.run()`. `LOOP_5ITER.txt` shows upstream banner and session completion. Control flow stays in `aar/research_loop/agent.py`. POC-001 harness was not used.

### 2 — Adapter steals scheduler — MISS

Monkeypatch wraps `_run_session` only to append TRACE rows, then calls the original. Stop policy / session counting remain in `AutonomousAgentLoop.run`. Custom `_prompt` supplies POC-002 8D task text; it does not replace the scheduler.

### 3 — Native evaluator replaced — MISS (gap noted)

Grok path skips Claude MCP servers. Eval is Bash → `python -m aar_poc_002.adapter.eval` (POC-002 suite), not a homemade scorer and not POC-001 evaluator. AAR MCP `evaluate_model` is unavailable on this path (documented MCP gap). Session logs report `tools=0` because plain `TextPart` output hides in-CLI tool use from AAR logging; STATE/scores on disk still match TRACE.

### 4 — Objective changed — MISS

Prompt states objective unchanged from AAR-POC-002 8D integer vector / hillclimb + capability filter. TRACE proposals are 8-int vectors with POC-002 scores.

### 5 — Only first round AAR then homemade — MISS

All five sessions are `AutonomousAgentLoop` sessions (logs + TRACE). No handoff to `harness/run_loop.py`. Cross-round state via workspace `STATE.json` hash chain.

### 6 — Documented capability as runtime evidence — MISS (nits)

`GROK_PROVIDER_MAPPING.md` separates `RUNTIME_PROVEN` vs `DOCUMENTED_ONLY`. Runtime path used `--output-format plain` and OIDC smoke patterns.

Nits (not full HIT): (a) META/REPORT claim “zero grok-specific code in core” is false given string/branch knowledge (see #8); (b) `UNPATCHED_BASELINE.md` writes `EXIT=0` while `evidence/UNPATCHED_agent_entry.txt` has `EXIT=1`.

### 7 — OAuth secret leak — MISS

`evidence/SECRET_SCAN.txt`: `hits=0`, `OAUTH_SECRET_IN_REPO=false`. Auth probe stores presence/expiry/mode booleans, not tokens. oauth-002 unchanged.

### 8 — Core patch beyond provider-neutral seam — HIT (medium)

Claimed “zero grok-specific code in core” / pure neutral seam is overstated.

1. `aar/research_loop/provider.py` hardcodes grok aliases and default POC module path:

```text
if name in ("grok", "grok_cli", "xai_grok"):
    mod_path = os.getenv(
        "AAR_GROK_PROVIDER_MODULE",
        "aar_xai_adapter_001.provider.grok_cli",
    )
```

2. `aar/research_loop/agent.py` and `run.py` branch on the same grok name tuple (AUTH skip; MCP skip; init print).

3. `GrokCLIProvider` correctly lives under OUT `provider/`, and Claude remains default — but core is not vendor-agnostic; it knows grok and this POC package by name.

Does not undo runtime success; undermines “min provider-neutral seam / zero grok in core” packaging. Follow-up should move vendor names / default module path out of core (generic plugin registry or required env only).

### 9 — CASE A OAuth success swapped for AAR integration — MISS

oauth-002 CASE A remains the auth precursor and is unmodified. Adapter-001 separately produced 5-iter loop artifacts under `AutonomousAgentLoop`. Not a relabel of oauth-002 smoke as AAR integration.

### 10 — Deletion proof fake — HIT (medium)

`scripts/deletion_proof.sh` / `deletion_A.txt` / `deletion_B.txt`:

- **A:** delete `agent.py`+`provider.py` → `ModuleNotFoundError` on **import** of `AutonomousAgentLoop` (`A_EXIT=1`).
- **B:** delete OUT `provider/` → `get_agent_provider()` import fails (`B_EXIT=1`).

Neither test executes `AutonomousAgentLoop.run()` / `run_native_loop.py` before/after deletion. STATUS/DELETION_PROOF claim `*_DELETION_BREAKS_RUN` — **RUN** is stronger than proven. Import breakage is real and directionally supportive; field names overclaim.

---

## Additional nits (non-attack)

- `provenance.json` HEAD stale vs FREEZE_SHA.
- `stop_reason: "unknown"` despite max-iterations stop.
- Session `tools=0` under plain grok output — weak observability of in-CLI tool use.
- Authoritative 5-iter evidence is `runs-5b` ↔ OUT evidence (earlier partial run dirs exist).

---

## Integration claim

| Claim | Reviewer stance |
|-------|-----------------|
| `CAN_AAR_NATIVE_RESEARCH_LOOP_RUN_WITH_XAI_OAUTH=true` | **Allowed with nits** |
| `FINAL_CASE=A` (adapter integration) | **Allowed with nits** |
| “Zero grok-specific code in core” | **Not accepted** as stated |
| `UPSTREAM_LOOP_DELETION_BREAKS_RUN` / `GROK_PROVIDER_DELETION_BREAKS_RUN` | **Overclaim**; import-break only proven |

**FAIL not issued** on the core question given TRACE + AutonomousAgentLoop + OIDC provider evidence.
