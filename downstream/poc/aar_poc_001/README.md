# AAR-POC-001 — Downstream toy PoC (8-D vector hill-climb)

**DOWNSTREAM-LOCAL** experiment under `downstream/poc/aar_poc_001/`.
Does **not** modify `aar/` or `generic_aar/` core.

## What it is

A minimal proof that an autonomous **Researcher** can iterate against an
**invisible TRAIN evaluator**, persist state, recover from failures, and only
then face an independent **HELD-OUT** evaluator once.

- Artifact: 8-dimensional integer vector, each dim ∈ [0, 100]
- TRAIN evaluator: deterministic secret target T + weights (process-isolated)
- HELD-OUT evaluator: different secret T' (+ weights); run exactly once at end
- Researcher: mutation / probe / random-restart searcher using only past scores

## Layout

```
eval_secret/     # TRAIN + HELDOUT params (mode 700); researcher must not read
evaluator/       # score_artifact.py — separate process, secret via env
researcher/      # proposer.py — no secret env; history-only search
harness/         # run_loop.py — submissions/, scores/, state, trajectory
runs/AAR-POC-001/# live run outputs (gitignored)
evidence/        # frozen summary committed for review
```

## Run

```bash
# from repo root, with any python3 (no torch needed)
python3 downstream/poc/aar_poc_001/harness/run_loop.py --n 25

# or smoke venv:
/workspace/aar-infra/.venv-smoke/bin/python \
  downstream/poc/aar_poc_001/harness/run_loop.py --n 25
```

## Isolation (PoC-level)

Inspired by upstream `ISOLATION.md` / transport put/scores pattern:

1. Harness spawns evaluator as a **subprocess** with `AAR_POC_SECRET_PATH`.
2. Researcher subprocess **does not** receive that env var and asserts absence.
3. Score JSON omits target/weights.
4. Held-out scores/params are never fed back into the researcher loop.

On a multi-user host, keep `eval_secret/` mode `700` owned by an eval-only user
(kernel-enforced). This PoC demonstrates the process/env channel split on a
single-user box.

## Success criteria

See `SPEC.md`.
