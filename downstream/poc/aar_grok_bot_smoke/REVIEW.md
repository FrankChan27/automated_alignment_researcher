# REVIEW.md — Independent Adversarial Review (AAR Grok Bot Smoke)

- Reviewer role: INDEPENDENT adversarial (not author/coordinator)
- Claim: native AAR smoke PASS via `grok_bot_sand_gateway_bearer`
- SMOKE_RUN_ID: `2b3da386-46d1-46d9-8073-75c6f38c69cc`
- Local commit under review: `25f268c` on `downstream/aar-provider-002` (ahead 1, not pushed)
- Researcher agent: `fac98a36-f560-43b8-9ac8-1ddacbbd16ed` (AAR Grok Researcher)
- Coordinator agent (distinct): `e9deaa2c-158e-4996-b491-ecf3cbda9bed` (AAR)

## REVIEW_VERDICT=PASS_WITH_NITS

## NATIVE_AAR_GROK_BOT_SMOKE_PASS=true

No FAIL-class false positives confirmed. Nits do not overturn native smoke acceptance.

---

## Per-attack findings

### 1. Coordinator Grok Bot itself did the experiment and impersonated AAR Researcher — REJECTED
- Live `listAgents`/`openAgent`: researcher `fac98a36…` name **AAR Grok Researcher**; coordinator is separate id `e9deaa2c…` name **AAR**.
- Researcher transcript seq6 user prompt includes workspace
  `/workspace/aar_grok_bot_smoke_work/runs/2b3da386-46d1-46d9-8073-75c6f38c69cc`
  and AAR task text; seq7–9 assistant replies include experiment narrative +
  `AAR_SMOKE_CONCLUSION stable=yes`.
- Coordinator transcript: `AAR_SMOKE_CONCLUSION=0`, `stable_sort_test=0`, `2b3da386=0`.
  The single `GROK_BOT_AAR_PROVIDER_OK` hit on coordinator is in the **human brief**
  (user seq3) stating coordinator-direct output must not count — not a fabricated reply.
- Researcher `store.db` mtime newest among agents and aligns with smoke window.
- Evidence: live gateway transcript; agent roster; file mtimes under run ws.

### 2. Simulated AutonomousAgentLoop (homemade loop) — REJECTED
- `run_native_loop.py` imports `from aar.research_loop.agent import AutonomousAgentLoop`
  and calls `await loop.run()`.
- Live resolve: `AutonomousAgentLoop.__module__ == aar.research_loop.agent`,
  source file `/workspace/automated_alignment_researcher/aar/research_loop/agent.py` (core).
- Console: `Autonomous Agent Loop (local mode)` + session log under AAR logs_dir.
- Provider poll `while True` in gateway is transport polling, not a substitute research loop.
- Evidence: `scripts/run_native_loop.py`, `evidence/native_loop_console.txt`, import inspection.

### 3. Bypassed Provider seam — REJECTED
- Scripts set `AAR_AGENT_PROVIDER=external`,
  `AAR_AGENT_PROVIDER_MODULE=aar_grok_bot_smoke.providers.grok_bot_gateway`,
  `AAR_AGENT_PROVIDER_PATH=…/downstream/poc`.
- `get_agent_provider()` returns `grok_bot_gateway` /
  module `aar_grok_bot_smoke.providers.grok_bot_gateway`, `requires_anthropic_key=False`.
- Core factory documents external plugin load via MODULE path (no vendor-name branch for grok).
- Evidence: provider code + live `get_agent_provider()`; `aar/research_loop/provider.py`.

### 4. Probe string was coordinator-direct output — REJECTED
- Researcher transcript: user seq4 UNIQUE PROVIDER PROBE → assistant seq5 exact
  `GROK_BOT_AAR_PROVIDER_OK`.
- Probe went through `prov.session` / `query` / `receive_response` in
  `run_provider_probe.py` (duration 7.21s; not instantaneous local fabricate).
- Coordinator only has the marker inside the human acceptance brief, not as its own
  send-message probe reply.
- Evidence: live openAgent; `evidence/provider_probe/reply.txt` /
  `probe_result.json` (EXACT_MATCH true).

### 5. Historical smoke reused as this run — REJECTED
- Only run dir: `runs/2b3da386-46d1-46d9-8073-75c6f38c69cc`.
- Session Started `2026-09-28T13:03:45` / Ended `13:04:21`; experiment files mtimes
  `13:04:09`–`13:04:12` inside that window; commit `25f268c` at `13:04:45` (after).
- Researcher has an older unrelated reply `PROBE_SHAPE_31f4511f` (seq3) then this run’s
  markers — not a copy of a prior smoke artifact set.
- Evidence: filesystem listing; mtimes; transcript seq order.

### 6. STATE did not truly advance — REJECTED (with NIT)
- Independent recompute: STATE_BEFORE fingerprint `fecc6ec5c6511bfe` ≠
  STATE_AFTER `69756fb9cc9a5926`.
- Changed: `findings.json`, `experiment/stable_sort_test.py`, `output.txt`,
  `conclusion.json`. Unchanged: seeded `STATE.json` hash `e0014317d5496406`
  (`history: []` still empty).
- AAR loop docs emphasize `findings.json` as the persisted research artifact;
  smoke’s `AAR_STATE_ADVANCED` is a **custom multi-file workspace fingerprint**,
  not a mutation of core `STATE.json` history. Advancement of findings+experiment
  is real and sufficient for this smoke; naming is slightly overbroad → NIT.
- Evidence: `STATE_BEFORE.json` / `STATE_AFTER.json`; current file hashes; `findings.json`.

### 7. Claude API actually called — REJECTED
- Provider imports only stdlib + `aar.research_loop.provider` event types; HTTP via
  `urllib` to local sand gateway. No Anthropic/Claude SDK import.
- Scripts/provider pop `ANTHROPIC_API_KEY` / related env keys before calls.
- `requires_anthropic_key=False`; SMOKE/CREDENTIAL flags `ANTHROPIC_USED=false`.
- Evidence: `providers/grok_bot_gateway.py` imports; credential docs; env pop in scripts.

### 8. Anthropic credential on execution path — REJECTED
- Auth path: `/home/box/agent-data/gateway.json` → `Authorization: Bearer <token>`
  to `http://127.0.0.1:<port>/api/*` only.
- Independent secret scan over work + poc + `aar/`: **SECRET_SCAN_HITS=0**
  (no gateway token literal, no `sk-ant-`, no `xai-` key material).
- Commit diff `25f268c`: no secret patterns.
- Evidence: live gateway auth success; `CREDENTIAL_AUDIT.md`; reviewer secret scan.

### 9. Cursor Cloud Agent / CLI / API used as researcher — REJECTED
- Researcher agent harness reported as `temporal` (sand agent), not Cloud Agent.
- Provider speaks only local gateway HTTP (`sendPrompt` / `openAgent` / `listAgents`).
- No Cloud Agent / cursor-agent researcher invocation in provider or scripts.
- This reviewer is a sand-subagent verifying evidence; it did not re-run the smoke
  as the researcher and did not use Cursor Cloud Agent for the experiment.
- Evidence: listAgents meta; provider source; architecture audit.

### 10. Mock/fake Grok response — REJECTED
- No mock/stub/hardcoded reply path in provider; reply text comes from polled
  transcript `send-message` entries after `sendPrompt accepted`.
- Live transcript still contains exact probe + smoke conclusion strings matching
  session log and `reply.txt`.
- Duration ~36s loop / ~7s probe inconsistent with pure local fabricate.
- Evidence: provider receive_response; live openAgent; timings.

### 11. Secret written to repo or logs — REJECTED
- Reviewer scan SECRET_SCAN_HITS=0 on work artifacts, poc package, and `aar/`.
- Provider `_redact()` strips bearer-looking substrings from errors.
- Commit `25f268c` clean of token/key patterns.
- Evidence: reviewer scan; `evidence/SECRET_SCAN.txt`; git show pattern check.

### 12. API key mislabeled as OAuth — REJECTED
- Declared `AUTH_MECHANISM=grok_bot_sand_gateway_bearer`; `OAUTH_USED=false` everywhere.
- Mechanism matches code: gateway.json `token` as HTTP Bearer — not OAuth/OIDC /
  `~/.grok/auth.json`, not `XAI_API_KEY`.
- Evidence: provider `_gateway_config` / `_http_post_json`; AUTH_DIAGNOSIS.md.

### 13. Only ran plain Python experiment without Researcher Agent — REJECTED
- Experiment artifacts created mid-session while researcher turn was active;
  researcher assistant messages narrate write/run/conclusion steps.
- AAR session log + `PROVIDER_CALLS=1` / `GROK_RESEARCHER_CALLS=1` via traced
  `_run_session` on real `AutonomousAgentLoop`.
- Plain local python alone would not produce researcher transcript seq6–9 or
  gateway-accepted sendPrompt trail.
- Evidence: mtimes vs session window; transcript; SMOKE_RESULT.json.

### 14. AAR Core hardcoded for Grok — REJECTED
- `CORE_VENDOR_REFERENCES=0` for grok/xai in `aar/` (excluding npm `package-lock.json`
  integrity hash false-substring noise).
- External load is generic `AAR_AGENT_PROVIDER_MODULE` importlib path.
- Grok-specific code lives only OUT-of-tree under
  `downstream/poc/aar_grok_bot_smoke/`.
- Evidence: `rg` on `aar/`; `provider.py` factory comments.

### 15. Insufficient auth evidence — REJECTED (adequate)
- Live reviewer calls with gateway.json Bearer succeeded: `listAgents` (researcher
  meta), `openAgent` (full transcript with smoke markers).
- Provider code path is the same three endpoints; probe/smoke durations and
  transcript causality (user prompt → assistant reply) corroborate.
- Token never printed; length/hash-prefix only used by reviewer for presence checks.
- Evidence: live gateway verification this review; AUTH_DIAGNOSIS.md; provider source.

---

## Nits

1. **`STATE.json` not mutated** — seeded file kept empty `history: []`. Acceptance
   uses a custom workspace fingerprint (findings + experiment files). Prefer renaming
   flag to e.g. `WORKSPACE_ADVANCED` or also append a core STATE history entry if
   that is a hard product invariant.
2. **`tools=0` in AAR session ResultEvent** — expected with text-only gateway
   provider events; tool use occurs inside researcher sand harness and is not
   mirrored as tool kinds in `openAgent` (only `message` / `send-message`). Stronger
   proof would snapshot tool entries if/when gateway exposes them.
3. **Console `stop_reason=unknown`** then script normalizes to `max_iterations` when
   sessions ≥ max — cosmetic; loop did stop after 1 session as configured.
4. **Commit not pushed** — claimed local-only `25f268c`; fine for smoke, note for
   any remote acceptance gate.

---

## Fixes required if FAIL

None for FAIL. Optional nit follow-ups only (do not block `NATIVE_AAR_GROK_BOT_SMOKE_PASS`):
- Clarify `AAR_STATE_ADVANCED` semantics vs `STATE.json`.
- Optionally persist tool-call forensics if gateway API supports it.

---

## Top evidence paths

| Path | Why |
|------|-----|
| `/workspace/aar_grok_bot_smoke_work/SMOKE_RESULT.md` | Acceptance table + fingerprints |
| `/workspace/aar_grok_bot_smoke_work/evidence/SMOKE_RESULT.json` | Machine-readable smoke result |
| `/workspace/aar_grok_bot_smoke_work/evidence/native_loop_console.txt` | Real AutonomousAgentLoop console |
| `/workspace/aar_grok_bot_smoke_work/evidence/provider_probe/reply.txt` | Exact probe marker |
| `/workspace/aar_grok_bot_smoke_work/runs/2b3da386-46d1-46d9-8073-75c6f38c69cc/` | Run workspace + STATE_BEFORE/AFTER + experiment + session log |
| `downstream/poc/aar_grok_bot_smoke/providers/grok_bot_gateway.py` | OUT AgentProvider (Bearer gateway) |
| `downstream/poc/aar_grok_bot_smoke/scripts/run_native_loop.py` | Native loop driver |
| `aar/research_loop/agent.py` / `aar/research_loop/provider.py` | Core loop + external provider seam |
| Live gateway `openAgent(fac98a36…)` | Researcher transcript seq4–9 (probe+smoke) |
| `git show 25f268c` | Local commit contents (not pushed) |

## Method notes (reviewer)
- Did not merge, push, call Anthropic, use Cursor Cloud Agent, or print secrets.
- Did not start a new smoke; only read artifacts + trivial verification
  (fingerprint recompute, provider import resolve, live gateway transcript fetch).
- Mirrored this REVIEW.md into repo poc path.
