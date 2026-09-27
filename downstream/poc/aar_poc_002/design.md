# AAR-POC-002 — Design: 8-d integer vector task on native submit-model surface

**Goal:** prove `CAN_WE_RUN_UPSTREAM_NATIVE_AAR` with real execution evidence.  
**Constraint:** NO Cursor. NO rewriting AAR harness. Downstream adapters only under `downstream/poc/aar_poc_002/`. Do **not** copy `aar_poc_001` `researcher/proposer.py` or `harness/run_loop.py` as the loop.

**Task:** candidate artifact is an **8-dimensional integer vector** with each component in `[0, 100]`. Hill-climb toward a secret target; held-out checks generalization on a different target / transform.

---

## What we reuse unchanged (upstream)

| Piece | Role |
|-------|------|
| `AutonomousAgentLoop` (`aar/research_loop/agent.py`) | Research loop (Claude sessions) |
| MCP `evaluate_model` (`server_api_tools.py`) | Submit `model_path` dir → scores |
| `aar/transport.py` | `put_model` / `put_scores` / holdout resolve |
| `aar/eval_pod/run_eval.run` | Suite scoring + composite + held-out strip |
| `aar/benchmarks/base.RuleBenchmark` | Deterministic aggregate scoring |
| Role conventions in suite YAML | `safety` / `held_out` / `capability_filter` |
| `generic_aar/` pattern | Side-effect import registers benchmarks, then call `run_eval.run` |

We do **not** replace the loop. Phase-2+ wires env (`SUITE_NAME`, `SUITE_CONFIG`, `PROMPT_TEMPLATE=prompt_safety.jinja2`, `BENCHMARK_BRIEF_FILE`, secrets paths) so the **official** agent scores our suite.

---

## Adapter shape (downstream only)

```
downstream/poc/aar_poc_002/
  execution_path.md          # phase-1 map
  blocker_probe.md           # phase-1 probe
  design.md                  # this file
  evidence/                  # transcripts
  adapter/
    __init__.py
    suite.yaml               # poc002 suite (safety + held_out + optional capability)
    eval.py                  # portable scorer: register benches + patch load_model + run_eval.run
    models_vector.py         # VectorModel + install_vector_loader()
    benchmarks/
      __init__.py            # imports register plugins
      hillclimb.py           # role:safety  — distance to secret hill-climb target
      heldout.py             # role:held_out — different secret target / transform
      capability.py          # role:capability_filter — e.g. all coords in [0,100], L0 sanity
    fixtures/
      example_vector_dir/    # model_path example containing vector.json (non-secret)
```

Secrets **never** in git:

```
/home/box/aar-poc-002-secrets/     # mode 0700
  hillclimb_target.json            # length-8 ints in [0,100]
  heldout_target.json              # different vector (or transform params)
  # optional published items if not inline
```

Research-readable outputs: suite YAML + stripped scores only. Held-out full JSON → mode-700 heldout dir (mirror `generic_aar/_heldout` / `HELDOUT_SCORES_DIR`).

---

## Artifact contract: `model_path` = directory with `vector.json`

```json
{ "vector": [12, 40, 7, 90, 3, 55, 61, 18] }
```

Constraints enforced by capability gate and/or loader:

- length == 8
- each component int in `[0, 100]`

`transport.put_model` already copytrees any directory; no change needed for handoff.

---

## Model loading without replacing the harness

**Upstream today** (`aar/eval_pod/models.py:load_model`):

- `stub:*` → `StubModel`
- anything else → `HFModel(path)` (expects HF weights)

A `vector.json` directory would **crash** `HFModel`. Options:

### Preferred (no upstream core patch): downstream loader shim

In `adapter/eval.py` (and optionally a one-line hook used only when our suite is selected):

```python
import generic path…
from aar.eval_pod import models as _models
from .models_vector import VectorModel, looks_like_vector_dir

_orig = _models.load_model

def load_model(model_ref: str):
    if looks_like_vector_dir(model_ref):
        return VectorModel(model_ref)
    return _orig(model_ref)

_models.load_model = load_model
# then: import adapter.benchmarks; from aar.eval_pod.run_eval import run; run(...)
```

`VectorModel` implements the `Model` protocol minimally (`generate` / `generate_batch` / logit stubs) and exposes `.vector: list[int]` for benchmarks that override `score`.

This mirrors how `generic_aar/eval.py` registers plugins **before** calling `run` — still the same engine.

### Optional upstream patch (flag explicitly)

If we want first-class support without monkeypatch:

| File | Change |
|------|--------|
| `aar/eval_pod/models.py` | In `load_model`, if `Path(model_ref)/"vector.json"` exists, return a small `VectorModel` (or call a plugin hook) |

**Phase-1 decision:** prefer **downstream shim**; treat upstream `load_model` extension as **optional** polish, not required to prove native loop + submit-model. Document any later patch under `upstream_updates/` before touching `aar/`.

**Do not patch** `aar/research_loop/*`, `generic_aar/*` (except consuming them), or invent a new loop.

---

## Benchmark / suite design

### Scoring idea

Let secret target \(t \in \{0,\ldots,100\}^8\). Submitted vector \(v\).  
Normalized L1 closedness:

\[
\mathrm{score}(v,t) = 1 - \frac{\|v-t\|_1}{8 \cdot 100}
\in [0,1]
\]

Higher = better (matches RuleBenchmark orientation).

- **Hill-climb (`role: safety`)**: target from `/home/box/aar-poc-002-secrets/hillclimb_target.json` (via `secret_dir` or env `POC002_SECRET_DIR`). Visible to eval only.
- **Held-out (`role: held_out`)**: different target (or linear transform of another secret) — stripped from AAR-facing scores (`strip_held_out` / tool `_strip_held_out`).
- **Capability (`role: capability_filter`)**: e.g. `floor: 1.0` on a check that vector is well-formed (length 8, ints in range); malformed submissions fail the gate.

### Suite YAML sketch (`adapter/suite.yaml`)

```yaml
suite: poc002_vector
target_model: vector_stub

benchmarks:
  - name: poc002_hillclimb
    category: rule
    role: safety
    baseline: 0.0          # replace after measuring empty/random baseline
    optimum: 1.0

  - name: poc002_heldout
    category: rule
    role: held_out
    baseline: 0.0
    optimum: 1.0

  - name: poc002_capability
    category: rule
    role: capability_filter
    floor: 1.0
```

Benchmarks subclass `RuleBenchmark`, set unique `name`, implement `load_items`/`matches` **or** override `score(model)` to read `model.vector` (cleaner for non-text artifacts). Auto-register via `__init_subclass__` when imported from `adapter/benchmarks/__init__.py`.

### Registration path (like generic_aar)

`adapter/eval.py`:

1. `install_vector_loader()`
2. `import downstream.poc.aar_poc_002.adapter.benchmarks`  # noqa register
3. `run(suite, model, secret_dir=..., out=..., heldout_dir=...)`

Agent path later: set `SUITE_NAME=poc002_vector`, point `SUITE_CONFIG` / holdout publish layout at our suite, keep using MCP `evaluate_model(model_path=...)` where `model_path` is a dir containing `vector.json` produced by the **upstream** agent's method code (not a fake 001 loop).

---

## How the official agent interacts (phase 2+, not this shift)

1. `python run.py server` (Flask) + `python run.py agent … --local` with `ANTHROPIC_API_KEY` + deps.
2. Env: `PROMPT_TEMPLATE=prompt_safety.jinja2`, `SUITE_NAME=poc002_vector`, briefing describing “emit a directory with vector.json”, `MONITOR_REQUIRED` policy for this toy (may set `0` for POC if integrity gate blocks non-training methods — **flag**: monitor expects method `run.py` / training narrative; vector toy may need monitor bypass or a thin “method” that writes `vector.json`).
3. Agent calls `evaluate_model` with `model_path` → transport → eval entrypoint → our registered benches (eval process must import adapter package — **flag**: eval entrypoint today only `registry.discover()` over `aar.benchmarks`. Custom benches in `generic_aar` work because `generic_aar/eval.py` imports them; **production entrypoint** `aar.eval_pod.entrypoint` does **not** import downstream packages.

### Required wiring for eval discovery (explicit flags)

| Need | Upstream core patch? | Downstream alternative |
|------|----------------------|------------------------|
| Load `vector.json` dirs | Optional (`models.py`) | Monkeypatch in adapter `eval.py` |
| Register `poc002_*` benchmarks in **Slurm/entrypoint** eval | **Yes, unless** eval command is overridden | Launch eval as `python -m downstream…adapter.eval` / set `EVAL` wrapper env / `PYTHONPATH`+sitecustomize — prefer **wrapper module as eval command** without editing `aar/eval_pod/entrypoint.py` |
| Suite YAML location | No | `SUITE_CONFIG` / holdout dir copy of `adapter/suite.yaml` |
| Secrets isolation | No | `/home/box/aar-poc-002-secrets` mode 0700; `HOLDOUT_DIR` / `--secret-dir` / `--heldout-dir` |

**Strong preference:** eval invoked via `python -m …adapter.eval` (same pattern as `generic_aar/eval.py`) so **no** `aar/` edit. For full agent+orchestrator, configure `eval_orchestration` spawn command / `EVAL_SLURM_SCRIPT` to call that module — that may be a **deploy config** change, not a core algorithm patch. If spawn is hardcoded to `python -m aar.eval_pod.entrypoint` only, document a **minimal** entrypoint hook or script override as the required patch.

Checked: `eval_orchestration._spawn_fs` falls back to `python -m aar.eval_pod.entrypoint`. For FS local POC, adapter can call `run_eval.run` directly from a thin server-side path **or** set a custom script — phase 2 chooses the smallest lever.

---

## MONITOR_REQUIRED tension (flag)

`evaluate_model` refuses scoring unless `submit_idea_proposal` approved (`MONITOR_REQUIRED=1`). The monitor is built for training-method integrity (D1–D3). An 8-d vector “method” is atypical.

Options for POC (phase 2):

1. `MONITOR_REQUIRED=0` for local proof only (env; no code patch).
2. Ship a tiny method dir that writes `vector.json` and passes a relaxed proposal narrative.
3. Upstream monitor allowlist — **avoid**; that’s a core patch.

Prefer (1) for CAN_WE_RUN proof, then (2) if demonstrating monitor path matters.

---

## Phase-1 non-goals (done / deferred)

| Done this shift | Deferred |
|-----------------|----------|
| Map execution path | Implement VectorModel + benches |
| Probe blockers + smoke stub eval | Install full agent/server deps |
| Design adapter + secrets dir | Request real `ANTHROPIC_API_KEY` |
| Branch + scaffolding commit | Run official agent loop end-to-end |

---

## Phase-2 next concrete step (recommended order)

1. **Install minimal server+eval deps** into `/home/box/aar-poc-002-venv` (or `uv sync` with a trimmed extra): `flask`, `flask-cors`, `flask-sqlalchemy`, `jinja2`, `httpx`, `PyYAML`, … — still skip torch if staying on vector/stub.
2. **Implement adapter** (`models_vector.py`, three benchmarks, `suite.yaml`, `eval.py`) and smoke:
   ```bash
   python -m downstream.poc.aar_poc_002.adapter.eval \
     --suite …/suite.yaml --model …/fixtures/example_vector_dir \
     --secret-dir /home/box/aar-poc-002-secrets --heldout-dir …
   ```
3. **Secret-request:** obtain real `ANTHROPIC_API_KEY` (and confirm Claude Agent SDK + `claude` CLI).
4. Only if agent E2E blocked by hardcoded entrypoint: **minimal patch or spawn-script override** (document in `upstream_updates/` first) — do not rewrite the research loop.
