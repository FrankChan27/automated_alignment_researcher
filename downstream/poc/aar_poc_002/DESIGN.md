# AAR-POC-002 DESIGN — native submit-model vector adapters

See also `design.md` (phase-1 scaffold notes). This file is the phase-2 lock.

## Native claim

Research loop = upstream `AutonomousAgentLoop` (`python run.py agent --local`).
Eval = `aar.eval_pod.run_eval.run` via `aar_poc_002.adapter.eval` (same pattern as
`generic_aar/eval.py`). Transport = fs submit-model (`model_path` dir with `vector.json`).

Deletion of `aar/` + `generic_aar/` breaks imports → evidence in
`evidence/deletion_proof/` supports `UPSTREAM_NATIVE_AAR`.

## Extension surfaces (all under `aar_poc_002/`)

1. **TASK** — `adapter/benchmarks/{hillclimb,heldout,capability}.py` subclass
   `aar.benchmarks.base.RuleBenchmark`; registered by import (PYTHONPATH /
   sitecustomize preload), not by editing `generic_aar/benchmarks/__init__.py`.
2. **EVAL** — `adapter/models_vector.install_vector_loader()` monkeypatches
   `aar.eval_pod.models.load_model` at process start only.
3. **CONFIG** — `adapter/suite.yaml`, `env.example`, out-of-tree secrets.
4. **PROMPT** — `briefing.md`.
5. **LAUNCH** — `scripts/*.sh` + `scripts/preload/sitecustomize.py`.
6. **METHOD TEMPLATE** — `method_templates/vector_submit/run.py` (fixture for ideas/).

## Score formula

Mirror POC-001 `evaluator/score_artifact.py` (secrets out-of-tree):

```
score = base_score - sum_i w_i*(clamp(v_i)-T_i)^2 - oob_penalty_per_dim * n_oob
normalized = clamp(score / base_score, 0, 1)   # BenchmarkScore.mean / closed%
```

Train vs held-out use different `T`/`w`. Held-out stripped by upstream `strip_held_out`.
`HELDOUT_EVAL_COUNT=1` after train loop (env; agent run when unblocked).

## What we deliberately do not do

- No copy of POC-001 `harness/run_loop.py` or `researcher/proposer.py`.
- No permanent edits under `aar/` or `generic_aar/`.
- No secrets in git or researcher-visible score artifacts.
