# AAR-POC-002 — Upstream native execution path (read-only map)

**Repo:** `FrankChan27/automated_alignment_researcher`  
**Checkout:** `/workspace/aar-infra/automated_alignment_researcher`  
**Branch:** `downstream/aar-poc-002-native` @ baseline `c145825`  
**Pinned upstream:** `02dbe9d` (merge-base = self)  
**Mapped at:** 2026-09-28 (UTC+8)  
**Rule:** every hop cites a real file/function/command verified in this tree. No POC-001 `proposer`/`run_loop` on this path.

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
# → run.py:cmd_server → aar/web_ui/backend (uvicorn app)

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
| 1 | `run.py` | `main()` → `cmd_agent()` — requires `ANTHROPIC_API_KEY`; sets local env; constructs loop |
| 2 | `aar/research_loop/agent.py` | `AutonomousAgentLoop.__init__` — MCP `server-api-tools`, prompt template, iteration caps |
| 3 | `aar/research_loop/agent.py` | `AutonomousAgentLoop.run` — `while True`: max_iterations / timeout → `_run_session` → `session_count += 1` (**NEXT ITERATION**) |
| 4 | `aar/research_loop/agent.py` | `_run_session` — fresh Claude session via `BaseAgent` + resolved prompt (`_get_prompt` → `resolve_prompt`) |
| 5 | `aar/research_loop/agent.py` | `_create_agent` — tools: Read/Write/Edit/Bash/… + MCP `evaluate_model`, `submit_idea_proposal`, `share_finding`, `get_leaderboard`, … |
| 6 | Agent action (prompted) | Write `aar/ideas/<name>/run.py` with `run_experiment(config) -> {"model_path": ...}` (**submit-model contract**) |
| 7 | MCP | `submit_idea_proposal` → `aar/research_loop/monitor.py` integrity gate (bound to `run.py` bytes) |
| 8 | MCP | `evaluate_model` in `aar/research_loop/tools/server_api_tools.py:evaluate_model` |
| 9 | Transport | `aar/transport.py:put_model(model_path, run_id)` → `SUBMISSIONS_DIR/<run_id>/…` |
| 10a fs | `aar/web_ui/backend/eval_orchestration.py:evaluate_model` | `spawn_eval` → Slurm `sbatch` **or** local `python -m aar.eval_pod.entrypoint --run-id … --suite …`; then `poll_scores` |
| 10b s3 | same + HTTP `/api/evaluate-model` | RunPod eval pod |
| 11 | `aar/eval_pod/entrypoint.py:main` | `transport.get_model` → `resolve_suite_dir` → `run_eval.run` → `strip_held_out` → `transport.put_scores`; full held-out → `HELDOUT_SCORES_DIR` |
| 12 | `aar/eval_pod/run_eval.py:run` | `load_model` → per-benchmark score → composite (`aar/benchmarks/composite.py`) |
| 13 | Back to agent | research-readable scores only (held-out stripped in `server_api_tools._strip_held_out`) → `share_finding` → log → **loop to step 3** |

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

File: `/workspace/aar-infra/poc002_evidence/unpatched_env_probe.txt`

| Check | Result |
|-------|--------|
| `ANTHROPIC_API_KEY` | **UNSET** → `run.py agent` prints `Error: ANTHROPIC_API_KEY is required for agent mode` |
| `claude_agent_sdk` | not installed (smoke venv) |
| `anthropic` | not installed |
| `fastapi` / `uvicorn` | not installed (needed for `run.py server`) |
| `yaml` | present in smoke venv |

Policy: keep this failure evidence; then decide minimal install/patch; report **UNPATCHED** vs **PATCHED** separately. Do not silently fix upstream bugs.

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
