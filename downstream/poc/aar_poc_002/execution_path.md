# AAR-POC-002 — Upstream native execution path (read-only map)

**Repo:** `FrankChan27/automated_alignment_researcher`  
**Checkout:** `/workspace/aar-infra/automated_alignment_researcher`  
**Branch:** `downstream/aar-poc-002-native` @ baseline `c145825`  
**Pinned upstream:** `02dbe9d` (merge-base = self)  
**Mapped at:** 2026-09-28 (UTC+8)  
**Rule:** every hop cites a real file/function/command verified in this tree. No POC-001 `proposer`/`run_loop` on this path.
**Verified/corrected:** 2026-09-28 ~01:50 UTC+8 (executor) — Flask not uvicorn; EVAL_VIA_WORKER poll-only; BaseAgent.execute/_execute_once NEXT-ITER detail; blockers paths.

---

## 0. One-line answer

Native autonomous loop = Claude agent sessions driven by `AutonomousAgentLoop`, scoring via **submit-model** (`model_path` → transport → eval pod → composite scores).  
`generic_aar/` is the **task-agnostic template** (benchmarks + suite + `eval.py`) that reuses `aar/` unchanged.  
POC-001’s `downstream/poc/aar_poc_001/harness/run_loop.py` is a **downstream-local substitute**, not this path.

---

## 1. ENTRYPOINT → NEXT ITERATION

### A. Operator launch (commands)

```bash
# Terminal 1 — dashboard / API (local mode)
python run.py server --port 8000
# → run.py:cmd_server → subprocess `python app.py` in aar/web_ui/backend (Flask, NOT uvicorn/fastapi)

# Terminal 2 — research agent
export ANTHROPIC_API_KEY=…          # required (run.py:cmd_agent)
export MAX_ITERATIONS=5             # or --max-iterations
export PROMPT_TEMPLATE=prompt_safety.jinja2   # optional; default prompt.jinja2
export SUITE_NAME=…                 # suite consumed by evaluate_model
export HARNESS_TRANSPORT=fs         # default; local shared FS
export HOLDOUT_DIR=…                # eval-private (mode 700); outside researcher env
export SUBMISSIONS_DIR=… SCORES_DIR=…
python run.py agent --idea-uid <uid> --idea-name <name> --local --max-iterations 5
```

Generic-task eval-only smoke (no agent loop):

```bash
PYTHONPATH=. bash generic_aar/run_example.sh
# → generic_aar/eval.py → aar.eval_pod.run_eval.run
```

### B. Agent process chain

| Step | File | Symbol / command |
|------|------|------------------|
| 1 | `run.py` | `main()` → `cmd_agent()` — requires `ANTHROPIC_API_KEY`; `--local` sets `ORCHESTRATOR_API_URL`/`LOCAL_MODE`; constructs `AutonomousAgentLoop` then `asyncio.run(loop.run())` |
| 2 | `aar/research_loop/agent.py` | `AutonomousAgentLoop.__init__` — MCP `create_server_api_tools_server()`, optional findings sync (skipped in local), `max_iterations`/`MAX_ITERATIONS` |
| 3 | `aar/research_loop/agent.py` | `AutonomousAgentLoop.run` — `while True`: stop if `session_count >= max_iterations` or `_StopChecker.check()`; else `await _run_session()`; **on success only** `session_count += 1` then optional `_sync_to_s3` (**NEXT ITERATION** = back to while) |
| 4 | `aar/research_loop/agent.py` | `_run_session` — mint `session_<nnn>_<tag>_<ts>` log; `prompt = _get_prompt()` (`PROMPT_TEMPLATE` → `resolve_prompt`); `_create_agent(...)`; `await agent.execute(task=prompt)` (**prompt is the task query, not `system_prompt`** — `_create_agent` leaves `system_prompt=None`) |
| 5a | `aar/research_loop/agent.py` | `_create_agent` — tools: Read/Write/Edit/Bash/Glob/Grep/WebSearch/WebFetch + MCP `evaluate_model`, `evaluate_predictions`, `share_finding`, `get_leaderboard`, `get_literature`, `share_literature`, `submit_idea_proposal` (+ `download_snapshot` if not local) |
| 5b | `aar/research_loop/agent.py` | `BaseAgent.execute` → `_execute_once` → `ClaudeSDKClient(ClaudeAgentOptions(...))` → `client.query(task)` → `receive_response` until `ResultMessage`; 529 overload retries in `execute` |
| 6 | Agent action (prompted) | Write `aar/ideas/<name>/run.py` with `run_experiment(config) -> {"model_path": ...}` (**submit-model contract**; see `aar/ideas/TEMPLATE/run.py`) |
| 7 | MCP | `submit_idea_proposal` → `aar/research_loop/monitor.py` integrity gate (approval bound to `run.py` bytes; `MONITOR_REQUIRED` default on) |
| 8 | MCP | `server_api_tools.evaluate_model` — gate → `_stamp_run_proposal` → `transport.put_model` |
| 9 | Transport | `aar/transport.py:put_model(model_path, run_id)` → `SUBMISSIONS_DIR/<run_id>/model` + `.submitted` (fs) |
| 10a fs | `aar/web_ui/backend/eval_orchestration.py:evaluate_model` | **Default `EVAL_VIA_WORKER=true`:** **poll-only** (`poll_scores` / `transport.read_scores`) — does **not** spawn. **`EVAL_VIA_WORKER=false`:** `spawn_eval` → Slurm `sbatch EVAL_SLURM_SCRIPT` **or** local `Popen(python -m aar.eval_pod.entrypoint …)` then `poll_scores` |
| 10b s3 | `server_api_tools` HTTP `/api/evaluate-model` → orchestration `_spawn_s3` | RunPod `deploy_pod` running `aar.eval_pod.entrypoint` |
| 11 | `aar/eval_pod/entrypoint.py:main` | `transport.get_model` → `resolve_suite_dir` → `run_eval.run` → `strip_held_out` → `transport.put_scores`; full held-out → `HELDOUT_SCORES_DIR` |
| 12 | `aar/eval_pod/run_eval.py:run` | `load_model` (`aar/eval_pod/models.py`) → per-benchmark score → `compute_composite` (`aar/benchmarks/composite.py`); research `out` is held-out-stripped |
| 13 | Back to agent | scores returned (extra `_strip_held_out` in MCP) → optional `share_finding` → session log ends → **return to step 3** |

**Session failure path:** if `_run_session` raises, `session_count` is **not** incremented; `_StopChecker.record_error()`; sleep 30s (or `OVERLOADED_WAIT_SECONDS` on 529) then retry while-loop.

Stop conditions (`AutonomousAgentLoop.run`): `max_iterations` / `MAX_ITERATIONS`, runtime timeout (`_StopChecker`), user interrupt.

### C. `generic_aar` task template (official task surface)

| Piece | Path | Role |
|-------|------|------|
| Benchmarks | `generic_aar/benchmarks/*.py` | Subclass `aar.benchmarks.base.RuleBenchmark` / Judge / Trajectory; auto-register |
| Suite | `generic_aar/suite.yaml` | `role: safety` (hill-climb), `held_out`, `capability_filter` |
| Eval wrapper | `generic_aar/eval.py:main` | `import generic_aar.benchmarks` then `aar.eval_pod.run_eval.run` |
| Briefing | `generic_aar/briefing.md` | Prompt content for custom task (no held-out leakage) |
| Demo | `generic_aar/run_example.sh` | stub:perfect / stub:weak, no GPU/keys |

Custom tasks are meant to plug in by **benchmarks + suite + briefing + env**, then the **same** `run.py agent` loop — not a new scheduler.

### D. Isolation dirs (`aar/config.py`, `PORTABILITY.md`)

| Var | Default idea | Who reads |
|-----|--------------|-----------|
| `HOLDOUT_DIR` | `$WORKSPACE/_holdout` | eval only (mode 700) |
| `HELDOUT_SCORES_DIR` | under HOLDOUT | eval/human only |
| `SUBMISSIONS_DIR` | under harness runs | research writes model; eval reads |
| `SCORES_DIR` | under harness runs | research polls aggregates |
| `SUITE_NAME` / `SUITE_CONFIG` | suite selection | both sides |

**POC-002 requirement:** TRAIN/HELDOUT secrets must **not** live in the git tree (POC-001 `eval_secret/` in-repo is a known defect to fix).

---

## 2. Official extension surfaces (allowed for POC-002)

All new code under `downstream/poc/aar_poc_002/` only. Must **not** rewrite/replace upstream scheduler, research loop, transport, state, or evaluator protocol.

| Surface | Intent for 8-d int vector (0–100) |
|---------|-----------------------------------|
| **TASK adapter** | Benchmark(s) expressing vector hill-climb / capability / held-out generalization, registered for the suite (import via launch `PYTHONPATH`, not by forking `AutonomousAgentLoop`) |
| **EVALUATOR adapter** | Map submit-model `model_path` (dir containing vector artifact) → score against **out-of-tree** secrets; preserve held-out strip |
| **CONFIG** | Suite YAML, axis/env, dirs pointing secrets **outside** repo |
| **PROMPT** | Briefing / prompt overlay for vector task (no secret leakage) |
| **LAUNCH WRAPPER** | Env + optional monkeypatch registration + start server/agent; deletion of `aar/`+`generic_aar/` must break the loop |
| **TEST FIXTURE** | Stub vectors, smoke scores, UNPATCHED failure logs |

**Forbidden:** copying POC-001 `researcher/proposer.py` or `harness/run_loop.py` as a fake “native” loop.

---

## 3. Deletion proof (UPSTREAM_NATIVE_AAR)

After adapters exist, temporarily remove/rename `aar/` and `generic_aar/` and attempt the same launch wrapper:

- If the full autonomous loop **still** completes → `UPSTREAM_NATIVE_AAR=false` (must not PASS).
- If it **fails** because those packages are required → evidence supports native dependency.

---

## 4. UNPATCHED blockers (evidence captured)

Evidence dirs (do not install yet):
- `downstream/poc/aar_poc_002/evidence/unpatched_failures/` — `env_probe.txt`, `agent_local.txt`, `agent_local_with_fake_key.txt`, `server.txt`
- `/workspace/aar-infra/poc002_evidence/unpatched_env_probe.txt` — condensed probe on `.venv-smoke`

| Check | Result | Evidence command / file |
|-------|--------|-------------------------|
| `ANTHROPIC_API_KEY` | **UNSET** → agent exits before import | `python run.py agent --idea-uid poc002 --idea-name poc002 --local` → `agent_local.txt` |
| `claude_agent_sdk` | **MISSING** (system python + smoke venv) | after fake key: `ModuleNotFoundError: claude_agent_sdk` → `agent_local_with_fake_key.txt` |
| `anthropic` | **MISSING** | `python3 -c 'import anthropic'` / `env_probe.txt` |
| `flask` (+ `flask_cors`) | **MISSING** — **actual** `run.py server` stack | `python run.py server` → `server.txt` (`from flask import Flask`) |
| `fastapi` / `uvicorn` | **MISSING** | listed in probes; **not** what `cmd_server` launches (Flask `app.py`) |
| `yaml` (PyYAML) | **MISSING** in system `python3`; **present** in `/workspace/aar-infra/.venv-smoke` | needed by `aar.eval_pod.run_eval` (`import yaml`) |
| `jinja2` | **MISSING** (system + smoke) | needed by `resolve_prompt` / prompt templates |

Policy: keep this failure evidence; then decide minimal install/patch; report **UNPATCHED** vs **PATCHED** separately. Do not silently fix upstream bugs.

### Upstream bugs noted while mapping (do not fix)
- `HARNESS.md` ends with a stray markdown fence (```) after the Phase-2 list.
- Docs/probes sometimes say fastapi/uvicorn for the dashboard; code path is Flask (`aar/web_ui/backend/app.py`).
- `LAUNCH.md` notes `AutonomousAgentLoop` still carries some W2S-flow assumptions; first live local multi-iter is a smoke test.

---

## 5. Contrast with POC-001 (do not copy)

| | POC-001 | Native (this map) |
|--|---------|-------------------|
| Loop | `downstream/poc/aar_poc_001/harness/run_loop.py` | `AutonomousAgentLoop.run` |
| Proposer | `researcher/proposer.py` | Claude session + `ideas/*/run.py` |
| Artifact | vector JSON via custom harness | submit-model `model_path` |
| Eval | subprocess + in-tree `eval_secret/` | eval pod + `HOLDOUT_DIR` out of tree |
| Upstream touch | none (also no native loop) | uses `aar/` + `generic_aar/` |

---

## 6. Next implementation steps (POC-002)

1. TASK/EVAL/CONFIG/PROMPT/LAUNCH under `downstream/poc/aar_poc_002/` for 8-d vector semantics on submit-model + generic_aar-style suite.
2. Secrets only under out-of-repo eval-only path (e.g. `/workspace/aar-infra/poc002_eval_secret/`).
3. Attempt **UNPATCHED** native `run.py agent` ≥5 iterations; record failure if blocked.
4. Minimal env install / independent patch if needed; **PATCHED** run; held-out **once** post-loop (`HELDOUT_EVAL_COUNT=1`).
5. Freeze evidence + provenance; push `downstream/aar-poc-002-native`; callback coordinator + reviewer.
