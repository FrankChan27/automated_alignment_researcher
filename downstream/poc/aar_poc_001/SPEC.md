# AAR-POC-001 Specification

## Contract

| Item | Requirement |
|------|-------------|
| Artifact | One 8-dim integer vector, each dim in `[0, 100]` inclusive |
| TRAIN evaluator | Invisible, deterministic scalar score; secret T, w |
| Researcher | Autonomous; uses only past scores + own history |
| Iterations | Complete ≥20 (prefer 25) of propose → eval → score → persist → next |
| HELD-OUT | Different secret T' (and optionally w); run **exactly once** after loop on best train artifact |
| Isolation | Researcher cannot see evaluator secrets; held-out never during loop |
| Scope | Code only under `downstream/poc/aar_poc_001/`; do not modify `aar/` / rewrite `generic_aar/` |

## Scoring (eval-private)

Documented only in `eval_secret/` and evaluator comments:

```
score = base_score - Σ_i w_i (v_i - T_i)² - oob_penalty_per_dim * n_oob
```

Out-of-bounds dimensions are clamped for the distance term and incur a flat
penalty. Invalid artifacts (wrong length / non-integers) yield `ok=false`.

## Researcher behavior

- Start from zeros (iter 1).
- Mutate best-so-far; occasional coordinate probe and random restart.
- Iteration 2 intentionally proposes an OOB vector once (recoverable failure).
- Persist `state.json` after every iteration (crash-resume via `--resume`).

## Harness outputs (`runs/AAR-POC-001/`)

- `submissions/iter_XXX/artifact.json`
- `scores/iter_XXX.json`
- `state.json`, `trajectory.jsonl`, `failures.jsonl`
- `best/artifact.json`, `heldout/result.json`
- `report.json`, `REPORT.md`

## Success criteria

1. ≥20 completed train iterations with real scores (not fabricated).
2. Cross-iteration improvement: `best_train_score > first_score` (expected under hill-climb).
3. ≥1 recorded failure with recovery (OOB injection on iter 2).
4. Held-out score present exactly once; not in researcher history during loop.
5. `git diff` on `aar/` and `generic_aar/` empty after the experiment.
6. Evidence frozen under `evidence/` and pushed on branch `downstream/aar-poc-001`.
