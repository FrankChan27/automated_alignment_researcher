# eval_secret (EVAL-PRIVATE)

Train and held-out scoring parameters for AAR-POC-001.

**Isolation rule:** Researcher code must never open this directory.
The harness passes the secret path only to the evaluator subprocess via
`AAR_POC_SECRET_PATH`. Researcher processes do not receive that env var.

Formulas (documented here only; do not import from researcher/):

```
score = base_score - sum_i w_i * (v_i - T_i)^2 - oob_penalty
oob_penalty = oob_penalty_per_dim * count(v_i not in [0,100])
```

- `train_params.json` — invisible TRAIN evaluator target T and weights
- `heldout_params.json` — independent HELDOUT target T' (different) and weights

Directory mode should be `700` on a real multi-user host; on this PoC box we
enforce process-level isolation (separate evaluator process + env gating).
