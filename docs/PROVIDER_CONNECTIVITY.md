# AAR Agent Provider Connectivity Registry

**DOCUMENTATION_ONLY.** This file records verified product / entry / runtime / provider / transport / auth connectivity. It does not implement providers or re-run smokes.

## Last Updated

| Field | Value |
|-------|-------|
| Registry date | **2026-09-28** (UTC) / **2026-09-28 UTC+8** |
| Base branch for this docs commit | `origin/main` @ `86e9578f01ef213fa1c14bf36f0825cdc0dfda98` (pre-promotion) → provider seam promotion |
| Upstream pin (`downstream/UPSTREAM_PIN.json`) | `02dbe9d2cadc553720d17cdf6259c0b8727e6cde` |
| Census sources (workspace, not shipped) | Phase 0–1 drafts under `aar_connectivity_registry_work/` (PHASE0, EVIDENCE_CENSUS, PRODUCT_STATUS_DRAFT) |
| Scope | Evidence already on GitHub downstream smoke/review commits; **no smoke re-run**; **CURSOR_USED=false**; **no Anthropic API** for this docs mission |

## Canonical Status

As of **2026-09-28**:

| Product | Entry | Status |
|---------|-------|--------|
| Grok Bot | 独立入口 | **CONNECTED** |
| Grok Bot | Grok入口 | **CONNECTED** |
| Grok Build Web | (Build Agent / workspace) | **NOT_CONNECTED** |
| Cursor | — | **PENDING_VERIFICATION** |
| Claude / upstream AAR | default / LEGACY | **PENDING_VERIFICATION** |

**Columns are independent:** PRODUCT ≠ PRODUCT_ENTRY ≠ PRODUCT_FORM ≠ AGENT_RUNTIME ≠ PROVIDER ≠ TRANSPORT ≠ AUTH. Do not rename “Grok Bot — 独立入口” to “Grok Build CLI” when TRANSPORT=`grok_cli`.

## Status Definitions

| Status | Meaning |
|--------|---------|
| **CONNECTED** | Immutable smoke + review evidence on GitHub shows AAR can drive researcher inference through the named provider/transport/auth for that product entry. |
| **NOT_CONNECTED** | Evidence shows the required invocation surface is missing or a negative connectivity experiment concluded the path does not work (honest negative). **Not** the same as “impossible forever.” |
| **PENDING_VERIFICATION** | No formal verified smoke for this product entry in the census, **or** architecture exists but live smoke under census constraints is absent. Not a failure verdict. |
| **BLOCKED** | A mission froze an operational block (e.g. cannot run without a forbidden credential). May be cited under Known Limitations; does not automatically set product STATUS without registry policy. |
| **DEPRECATED** | Formerly recorded path withdrawn. |
| **UNKNOWN** | Insufficient evidence to classify. |

---

## Architecture

### ARCHITECTURE_STATUS vs PRODUCT_CONNECTIVITY_STATUS

| Field | Meaning |
|-------|---------|
| **ARCHITECTURE_STATUS** | Whether the generic Provider seam exists on the cited branch |
| **PRODUCT_CONNECTIVITY_STATUS** | Whether a named product entry has verified live smoke (matrix below) |

These are independent. Promoting the seam to `main` does **not** auto-flip Cursor / Build Web / Claude product statuses.

### On `main` (after vendor-neutral Provider promotion)

- **VENDOR_NEUTRAL_PROVIDER_SEAM_ON_MAIN=true**
- `aar/research_loop/provider.py` — generic contract + `get_agent_provider()` factory
- Built-in LEGACY: `claude` / `claude_sdk` / `anthropic` → `ClaudeSDKProvider` (structural; live Anthropic smoke still PENDING_VERIFICATION)
- External: requires `AAR_AGENT_PROVIDER_MODULE` (+ optional `AAR_AGENT_PROVIDER_PATH` / `AAR_AGENT_PROVIDER_CLASS`); capability flags `requires_anthropic_key`, `supports_inprocess_mcp`
- `GENERIC_CORE_GROK_HARDCODE=false`, `GENERIC_CORE_CURSOR_HARDCODE=false`
- Runtime-specific adapters (optional): `aar/integrations/providers/` — e.g. `grok_bot_gateway` (**NOT** a public stable API; depends on local sand gateway Bearer)

### Historical source (downstream, immutable evidence)

- Tip `downstream/aar-provider-002` @ `01067d70f001ee99b229089acd0dba63e7f3a5ed`: original **VENDOR_NEUTRAL** loader extracted into core (not wholesale PoC merge).
- Grok Bot Grok入口 smoke evidence remains on `downstream/aar-grok-bot-smoke` @ `2ca87d605996daf5269ffe972663343a5777c206` (unchanged).

### Layer model (Grok Build discovery)

| Layer | Meaning |
|-------|---------|
| A | Current Build Agent can execute a task (chat session) |
| B | Harness can dispatch subagents (hub tools) |
| C | **Workspace Python / AAR external provider can invoke** that capability |

Connectivity for Build Web requires layer **C**. Absence of C ⇒ **NOT_CONNECTED** (not “IMPOSSIBLE”).

---

## Connectivity Matrix

| Product | Entry | Product Form | Runtime | Provider | Transport | Auth | Status | Verified At | Evidence |
|---------|-------|--------------|---------|----------|-----------|------|--------|-------------|----------|
| Grok Bot | 独立入口 | Official `grok` CLI as researcher transport into native AAR loop | `AutonomousAgentLoop` | `GrokCLIProvider` (`aar_provider_002.providers.grok_cli`) | `grok_cli` | Primary: `grok_cli_oidc`; variant: `xai_api_key_official_cli` | **CONNECTED** | 2026-09-28 | provider-002 REVIEW `01067d7…`; adapter-001 `cb57ed9…`; smoke-v3 `ae2ff52…` — see Verified Products |
| Grok Bot | Grok入口 | Local sand-gateway HTTP → dedicated Grok Bot researcher agent | `AutonomousAgentLoop` | `grok_bot_gateway` | sand gateway HTTP (`listAgents` / `sendPrompt` / `openAgent`) | `grok_bot_sand_gateway_bearer` (runtime-local; **not** official permanent public API) | **CONNECTED** | 2026-09-28 | bot-smoke REVIEW `2ca87d6…` / impl `25f268c…` |
| Grok Build Web | Build Agent / workspace | Negative discovery (no provider module) | Build chat/harness (A/B only) | none | none usable for AAR external provider | N/A | **NOT_CONNECTED** | 2026-09-28 | `403fdfb…` `downstream/poc/grok_build_provider/` |
| Cursor | — | — | — | — | — | — | **PENDING_VERIFICATION** | — | `NO_VERIFIED_SMOKE_FOUND` |
| Claude / upstream AAR | default / LEGACY | Claude Agent SDK researcher (default on `main`) | `AutonomousAgentLoop` | ClaudeSDK / `ClaudeSDKClient` | Claude Agent SDK / `claude` CLI | `ANTHROPIC_API_KEY` | **PENDING_VERIFICATION** | — | Code on `main` `a6493c2…`; no live Anthropic smoke in census; POC-002 operational BLOCKED without key |

---

## Verified Products

### Grok Bot — 独立入口

| Field | Value |
|-------|-------|
| PRODUCT | **Grok Bot** (never “Grok Build CLI”) |
| PRODUCT_ENTRY | **独立入口** |
| PRODUCT_FORM | Official `grok` CLI subprocess as researcher transport |
| AGENT_RUNTIME | `aar.research_loop.agent.AutonomousAgentLoop` |
| PROVIDER | `GrokCLIProvider` / `aar_provider_002.providers.grok_cli` (predecessor: `aar_xai_adapter_001.provider.grok_cli`) |
| TRANSPORT | `grok_cli` |
| AUTH_MECHANISM | **Primary:** `grok_cli_oidc` (`~/.grok/auth.json`, issuer `https://auth.x.ai`). **Variant smoke:** `xai_api_key_official_cli` |
| MODEL | `grok-4.7` (OIDC smokes); `grok-4.5` (smoke-v3) |
| STATUS | **CONNECTED** |
| VERIFIED_AT | 2026-09-28 |

**Evidence (immutable GitHub SHAs + paths):**

| Role | SHA | Paths (on cited branch tip) |
|------|-----|-------------------------------|
| provider-002 REVIEW / tip | `01067d70f001ee99b229089acd0dba63e7f3a5ed` | `downstream/poc/aar_provider_002/REVIEW.md`, `STATUS.md`, `REPORT.md`, `evidence/RESEARCHER_TRANSPORT_CONFIRM.txt`, `evidence/ITERATION_TRACE.jsonl` |
| provider-002 IMPLEMENTATION | `8ccffdaa70060d1e25412a4e3f434b7ea153da1d` | `downstream/poc/aar_provider_002/providers/grok_cli.py`; core `aar/research_loop/provider.py` |
| adapter-001 REVIEW tip | `cb57ed923548c7daf319ef05bc0e44aa0afeea88` | `downstream/poc/aar_xai_adapter_001/REVIEW.md`, `STATUS.md` |
| adapter-001 FREEZE | `7ed5c43940dececf7b9c8ca68abf41c64ed7296e` | adapter evidence TRACE |
| oauth-002 prerequisite (CLI inference, no AAR adapter) | `00ba33b51d6b78cbb0844268fc437d64cd6e0c31` | `downstream/poc/aar_xai_oauth_002/REPORT.md`, `STATUS.json` |
| smoke-v3 REVIEW tip | `ae2ff5293d47321e58f8754790a8fd2bd7ac02a4` | `downstream/poc/aar_grok_smoke_v3/evidence/REVIEW.md`, `SUMMARY.json` |
| smoke-v3 IMPLEMENTATION | `d9d523ee1c332dd2b2ff928457de391e3a8574ea` | `downstream/poc/aar_grok_smoke_v3/` |

Flags from primary OIDC path: `ANTHROPIC_USED=false`, `API_KEY_USED=false`, `CURSOR_USED=false`, `RESEARCHER_TRANSPORT=grok_cli_oidc`.

**EVIDENCE_CONFLICT (preserved):**

1. AUTH split — OIDC freezes claim `API_KEY_USED=false`; smoke-v3 required platform `XAI_API_KEY` when OIDC alone failed for CLI chat-proxy. Register AUTH as multi-valued; do **not** assert “OIDC always sufficient.”
2. STATE advancement semantics differ across smokes (provider-002 TRACE / smoke-v3 mutates `STATE.json` history; contrast Grok入口 below).

---

### Grok Bot — Grok入口

| Field | Value |
|-------|-------|
| PRODUCT | **Grok Bot** |
| PRODUCT_ENTRY | **Grok入口** |
| PRODUCT_FORM | Local sand-gateway HTTP → dedicated researcher Grok Bot agent |
| AGENT_RUNTIME | `aar.research_loop.agent.AutonomousAgentLoop` |
| PROVIDER | `grok_bot_gateway` / `aar_grok_bot_smoke.providers.grok_bot_gateway` |
| TRANSPORT | Local sand gateway HTTP (`POST /api/listAgents`, `/api/sendPrompt`, `/api/openAgent`) |
| AUTH_MECHANISM | **`grok_bot_sand_gateway_bearer`** — Bearer from runtime-local `/home/box/agent-data/gateway.json`. **Not** claimed as an official permanent public xAI API. |
| MODEL | Harness/agent-side (not pinned as public model id in smoke table) |
| STATUS | **CONNECTED** |
| VERIFIED_AT | 2026-09-28 |
| SMOKE_RUN_ID | `2b3da386-46d1-46d9-8073-75c6f38c69cc` |
| AAR_LOOP_EXECUTED | true |
| AAR_RESEARCHER_EXECUTED | true (researcher agent `fac98a36-f560-43b8-9ac8-1ddacbbd16ed`) |
| **AAR_WORKSPACE_ADVANCED** | **true** (findings + experiment files fingerprint changed) |
| **AAR_STATE_JSON_ADVANCED** | **false** (`STATE.json` hash unchanged `e0014317d5496406`; `history: []`) |
| OAUTH_USED | false |
| XAI_API_KEY_USED | false |
| ANTHROPIC_API_USED / ANTHROPIC_USED | false |
| CURSOR_USED | false |
| PROVIDER_CALLS | 1 |
| REVIEW_VERDICT | `PASS_WITH_NITS` (`NATIVE_AAR_GROK_BOT_SMOKE_PASS=true`) |

**Evidence (immutable GitHub SHAs + paths) on branch `downstream/aar-grok-bot-smoke`:**

| Role | SHA |
|------|-----|
| REVIEW tip | `2ca87d605996daf5269ffe972663343a5777c206` |
| IMPLEMENTATION | `25f268ceb16c1b1018f8fca176a27a40be66d1c0` |

Paths: `downstream/poc/aar_grok_bot_smoke/REVIEW.md`, `SMOKE_RESULT.md`, `AUTH_DIAGNOSIS.md`, `CREDENTIAL_AUDIT.md`, `PROVIDER_PROBE.md`, `ARCHITECTURE_AUDIT.md`, `providers/grok_bot_gateway.py`, `evidence/SMOKE_RESULT.json`, `evidence/run_snapshot/*`, `evidence/provider_probe/*`.

**EVIDENCE_CONFLICT (preserved):** Smoke table label `AAR_STATE_ADVANCED=True` meant workspace fingerprint, **not** core `STATE.json` mutation. Registry uses split flags above.

---

### Grok Build Web

| Field | Value |
|-------|-------|
| PRODUCT | **Grok Build Web** |
| PRODUCT_ENTRY | Build Agent / workspace discovery |
| PRODUCT_FORM | Negative experiment docs only (no provider class) |
| AGENT_RUNTIME | Build chat/harness exists (layers A/B); **not** callable from workspace Python (layer C) |
| PROVIDER | none (`EXTERNAL_PROVIDER_IMPLEMENTED=false`) |
| TRANSPORT | none usable for AAR → Build Agent |
| AUTH_MECHANISM | N/A |
| STATUS | **NOT_CONNECTED** |
| VERIFIED_AT | 2026-09-28 |
| Blocker | **Missing workspace → current Build Web Agent programmatic invocation surface** (layer C). Not labeled IMPOSSIBLE. |
| GROK_BUILD_PROVIDER_PROBE | NOT_RUN |
| AAR_LOOP_EXECUTED | false |
| AAR_RESEARCHER_EXECUTED | false |

**Evidence:** commit `403fdfbcf3a8f89ee4f92aaa07dd75cbc2164bb6` on `downstream/aar-grok-build-provider`.

Paths: `downstream/poc/grok_build_provider/README.md`, `RUNTIME_DISCOVERY.md`, `ARCHITECTURE_AUDIT.md`, `PROVIDER_IMPLEMENTATION.md`, `SMOKE_RESULT.md`, `REVIEW.md` (PASS on honest negative), `evidence/PROBES.txt`.

Baseline pin for that experiment: provider-002 @ `01067d70f001ee99b229089acd0dba63e7f3a5ed` (core unchanged).

---

### Cursor

| Field | Value |
|-------|-------|
| PRODUCT | Cursor |
| PRODUCT_ENTRY | — |
| STATUS | **PENDING_VERIFICATION** |
| Reason | **`NO_VERIFIED_SMOKE_FOUND`** — no formal AAR→Cursor AgentProvider / smoke / REVIEW on origin tips |
| Note | Downstream POCs record `CURSOR_USED=false` as a constraint, not as Cursor integration proof. **Not** a failure verdict; do **not** invent CONNECTED. |

---

### Claude / upstream

| Field | Value |
|-------|-------|
| PRODUCT | Claude / upstream AAR |
| PRODUCT_ENTRY | default on `main`; LEGACY built-in on provider-002 lineage |
| PRODUCT_FORM | Claude Agent SDK researcher |
| AGENT_RUNTIME | `AutonomousAgentLoop` |
| PROVIDER | `ClaudeSDKClient` on `main`; `ClaudeSDKProvider` on provider-002 |
| TRANSPORT | Claude Agent SDK / `claude` CLI |
| AUTH_MECHANISM | `ANTHROPIC_API_KEY` |
| STATUS | **PENDING_VERIFICATION** |

**Why not CONNECTED:** Architecture is the default on `main` @ `a6493c288ead7e9e7fbb35311a136c70eca37108`, but this census has **no verified live Anthropic researcher smoke** (Grok missions set `ANTHROPIC_USED=false`).

**Related operational freeze (not product STATUS):** POC-002 tip `71842398db939801bafcfe98a66dbeb922a15297` — `UPSTREAM_NATIVE_UNPATCHED=BLOCKED` without Anthropic key (`downstream/poc/aar_poc_002/STATUS.md`, `evidence/anthropic_hard_bind.md`, `evidence/unpatched_failures/UPSTREAM_NATIVE_UNPATCHED_BLOCKED.md`).

**EVIDENCE_CONFLICT (preserved):** Default-on-main architecture vs no live Anthropic smoke vs POC-002 operational BLOCKED → registry keeps **PENDING_VERIFICATION** for product connectivity.

---

## Product vs Runtime vs Transport

| Concept | Definition | Example |
|---------|------------|---------|
| **PRODUCT** | Human-facing product being connected | Grok Bot, Grok Build Web, Cursor, Claude |
| **PRODUCT_ENTRY** | Which entry surface of that product | 独立入口, Grok入口, Build workspace |
| **PRODUCT_FORM** | How that entry is embodied for AAR | CLI subprocess, sand gateway HTTP, SDK |
| **AGENT_RUNTIME** | AAR loop that owns iterations | `AutonomousAgentLoop` |
| **PROVIDER** | `AgentProvider` implementation name/module | `GrokCLIProvider`, `grok_bot_gateway` |
| **TRANSPORT** | Wire/process mechanism | `grok_cli`, sand gateway HTTP, Claude SDK |
| **AUTH_MECHANISM** | How the transport authenticates | `grok_cli_oidc`, `grok_bot_sand_gateway_bearer`, `ANTHROPIC_API_KEY` |

**Anti-patterns:**

- Do not rename PRODUCT when TRANSPORT changes (Grok Bot + `grok_cli` ≠ “Grok Build CLI”).
- Do not equate AUTH with PRODUCT (gateway Bearer ≠ “OAuth product”).
- Do not claim workspace fingerprint advance as `STATE.json` advance.

---

## Evidence Registry

| Evidence ID | Branch | Tip / commit SHA | Primary paths |
|-------------|--------|------------------|---------------|
| E-UPSTREAM-PIN | pin + `upstream/main` | `02dbe9d2cadc553720d17cdf6259c0b8727e6cde` | `downstream/UPSTREAM_PIN.json` |
| E-MAIN | `main` | `a6493c288ead7e9e7fbb35311a136c70eca37108` | `run.py`, `aar/research_loop/agent.py` |
| E-POC002-BLOCK | `downstream/aar-poc-002-native` | `71842398db939801bafcfe98a66dbeb922a15297` | `downstream/poc/aar_poc_002/{STATUS,REPORT}.md`, `evidence/anthropic_hard_bind.md` |
| E-OAUTH002 | `downstream/aar-xai-oauth-002` | `00ba33b51d6b78cbb0844268fc437d64cd6e0c31` | `downstream/poc/aar_xai_oauth_002/{REPORT.md,STATUS.json}` |
| E-ADAPTER001 | `downstream/aar-xai-adapter-001` | `cb57ed923548c7daf319ef05bc0e44aa0afeea88` | `downstream/poc/aar_xai_adapter_001/{REVIEW,STATUS,REPORT}.md` |
| E-PROVIDER002 | `downstream/aar-provider-002` | `01067d70f001ee99b229089acd0dba63e7f3a5ed` | `downstream/poc/aar_provider_002/{REVIEW,STATUS,REPORT}.md`, `evidence/*` |
| E-PROVIDER002-IMPL | (ancestor) | `8ccffdaa70060d1e25412a4e3f434b7ea153da1d` | provider + core seam |
| E-SMOKE-V3 | `downstream/aar-grok-smoke-v3` | `ae2ff5293d47321e58f8754790a8fd2bd7ac02a4` | `downstream/poc/aar_grok_smoke_v3/evidence/*` |
| E-BUILD-NEG | `downstream/aar-grok-build-provider` | `403fdfbcf3a8f89ee4f92aaa07dd75cbc2164bb6` | `downstream/poc/grok_build_provider/*` |
| E-BOT-GROK-ENTRY | `downstream/aar-grok-bot-smoke` | `2ca87d605996daf5269ffe972663343a5777c206` | `downstream/poc/aar_grok_bot_smoke/*` |
| E-BOT-GROK-IMPL | (ancestor) | `25f268ceb16c1b1018f8fca176a27a40be66d1c0` | gateway provider + smoke artifacts |

Supporting (not product CONNECTED alone): oauth-001 `4c035dd6e8e716c854f694a2fe5e6e5c71dad42a` (CASE D); poc-001 `c145825e096547ea7f42014aa3474041ec64a643` (homemade loop, not AgentProvider).

---

## Known Limitations

1. **RESOLVED for architecture:** vendor-neutral Provider seam is on `main` (`VENDOR_NEUTRAL_PROVIDER_SEAM_ON_MAIN=true`). Historical PoC/smoke evidence remains on immutable downstream branches.
2. Grok Build Web: layer C missing — **NOT_CONNECTED** until a workspace-callable invocation surface exists. (Status unchanged; no re-smoke this round.)
3. Grok Bot Grok入口 auth is **runtime-local** gateway Bearer — ephemeral to the sand host; `aar/integrations/providers/grok_bot_gateway.py` is **NOT** marketed as a public stable API.
4. Grok Bot 独立入口 AUTH is **multi-valued** (OIDC vs API key variant); environments differ. `GrokCLIProvider` remains downstream (`KEEP_ADAPTER_DOWNSTREAM`) unless separately promoted.
5. Grok入口 historical smoke advanced workspace artifacts, **not** `STATE.json` history.
6. Claude live agent still requires Anthropic credentials for a live CONNECTED claim; structural LEGACY path preserved (`CLAUDE_LIVE_SMOKE_EXECUTED=false` unless a new live smoke is recorded).
7. `api.x.ai` OAuth (non-CLI) marked `NOT_TESTED_NOT_JUSTIFIED` in oauth-002 — not a CONNECTED claim.
8. Product CONNECTED rows are evidence-gated; architecture promotion alone does not flip Cursor / Build Web / Claude statuses.

---

## Pending Verification

| Item | Why pending | What would graduate it |
|------|-------------|------------------------|
| Cursor | `NO_VERIFIED_SMOKE_FOUND` | Formal OUT `AgentProvider` + native loop smoke + independent REVIEW with immutable SHA/paths |
| Claude / upstream live CONNECTED | Default code path exists; no census live Anthropic smoke | Live `AutonomousAgentLoop` smoke with Anthropic allowed + REVIEW; or explicit registry policy mapping POC-002 BLOCKED → product BLOCKED |
| `api.x.ai` OAuth as researcher AUTH | Not tested/justified in oauth-002 | Dedicated smoke + review |
| Provider seam on `main` | **DONE** — seam promoted; see Architecture | Production tests + live Grok Bot (Grok入口) regression on promotion PR |

---

## Update Protocol

Future connectivity smokes **must** record all of the following (machine-readable preferred + human REVIEW):

| Field | Required |
|-------|----------|
| PRODUCT | yes |
| PRODUCT_ENTRY | yes |
| PRODUCT_FORM | yes |
| AGENT_RUNTIME | yes |
| PROVIDER | yes |
| TRANSPORT | yes |
| AUTH_MECHANISM | yes |
| MODEL | yes (or explicit `unknown` with reason) |
| VERIFIED_AT | yes (YYYY-MM-DD or GitHub commit UTC + UTC+8 display) |
| STATUS | yes ∈ {CONNECTED, NOT_CONNECTED, PENDING_VERIFICATION, BLOCKED, DEPRECATED, UNKNOWN} |
| AAR_LOOP_EXECUTED | yes |
| AAR_RESEARCHER_EXECUTED | yes |
| AAR_WORKSPACE_ADVANCED | yes |
| AAR_STATE_JSON_ADVANCED | yes (do **not** set true if only findings/experiment changed) |
| CLAUDE_API_USED | yes |
| ANTHROPIC_API_USED | yes |
| XAI_API_KEY_USED | yes |
| CURSOR_USED | yes |
| HUMAN_INTERVENTIONS | yes (count or description; `0` if none) |
| EVIDENCE_COMMIT | yes (immutable full SHA on GitHub) |
| EVIDENCE_PATH | yes (paths existing on that commit/branch) |
| REVIEW_VERDICT | yes |

**Process:**

1. Do not mutate historical smoke branches/artifacts when updating this registry.
2. Cite full SHAs + paths that exist on GitHub; no invented CONNECTED.
3. Preserve EVIDENCE_CONFLICT notes when statuses disagree across smokes.
4. Keep PRODUCT / ENTRY / RUNTIME / PROVIDER / TRANSPORT / AUTH in separate fields.
5. Update this file via a DOCUMENTATION_ONLY change; then independent review before merge to `main`.
