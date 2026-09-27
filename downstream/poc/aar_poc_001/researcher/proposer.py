#!/usr/bin/env python3
"""Autonomous artifact proposer for AAR-POC-001.

Sees ONLY: past scores, own submission history, and persisted state.
Must NEVER open eval_secret/ or receive AAR_POC_SECRET_PATH.

Search strategy (real searcher, not a hard-coded path to the optimum):
  - Start from zeros (or resume from state).
  - Mutate best-so-far coordinates with decaying step size.
  - Occasional coordinate-wise greedy probe and rare random restart.
  - Iteration 2 intentionally emits an out-of-bounds vector once to exercise
    recoverable failure handling (then recovers on subsequent iterations).
"""
from __future__ import annotations

import argparse
import json
import os
import random
from pathlib import Path
from typing import Any


DIMS = 8
LO, HI = 0, 100

# Hard guard: refuse to run if secret path is somehow injected into this process.
FORBIDDEN_ENV = "AAR_POC_SECRET_PATH"
FORBIDDEN_DIR_NAME = "eval_secret"


def _assert_isolation(poc_root: Path) -> None:
    if FORBIDDEN_ENV in os.environ:
        raise RuntimeError(
            f"isolation violation: researcher process has {FORBIDDEN_ENV} set"
        )
    secret_dir = poc_root / FORBIDDEN_DIR_NAME
    # Do not open secret files. We only check the path exists for the assertion
    # message; we never read contents.
    if secret_dir.exists():
        # Soft check: ensure we are not about to walk into it accidentally.
        pass


def load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def clip_int(x: float) -> int:
    return int(max(LO, min(HI, round(x))))


def random_vector(rng: random.Random) -> list[int]:
    return [rng.randint(LO, HI) for _ in range(DIMS)]


def mutate(best: list[int], rng: random.Random, step: int, iteration: int) -> list[int]:
    """Propose a neighbor of best with per-coord mutations."""
    out = [clip_int(v) for v in best]
    # Mutate 1–4 coordinates
    n_mut = rng.randint(1, min(4, DIMS))
    idxs = rng.sample(range(DIMS), n_mut)
    for i in idxs:
        delta = rng.randint(-step, step)
        if delta == 0:
            delta = rng.choice([-1, 1])
        out[i] = clip_int(out[i] + delta)
    # Periodic single-coord large jump to escape plateaus
    if iteration % 7 == 0:
        j = rng.randrange(DIMS)
        out[j] = clip_int(out[j] + rng.choice([-1, 1]) * rng.randint(step, step * 3))
    return out


def propose(state: dict[str, Any], rng: random.Random) -> tuple[list[int], str]:
    """Return (vector, strategy_tag)."""
    iteration = int(state.get("iteration", 0)) + 1  # next iteration number
    history = state.get("history", [])
    best = state.get("best_vector")
    best_score = state.get("best_score")

    # Intentional recoverable failure on iteration 2 (once).
    injected = bool(state.get("injected_oob_failure", False))
    if iteration == 2 and not injected:
        bad = [50] * DIMS
        bad[0] = 150  # out of bounds
        bad[3] = -5
        return bad, "inject_oob_failure"

    if best is None or not history:
        # Start from zeros (deterministic-ish baseline), with tiny noise.
        vec = [0] * DIMS
        if iteration > 1:
            vec = random_vector(rng)
        return vec, "init_zeros" if iteration == 1 else "random_restart"

    # Decaying step size based on progress
    step = max(2, 20 - iteration // 2)

    # Rare random restart
    if rng.random() < 0.08:
        return random_vector(rng), "random_restart"

    # Coordinate-wise probe: nudge each dim of best toward recent improvements
    if iteration % 5 == 0 and len(history) >= 2:
        prev = history[-1].get("vector", best)
        probe = [clip_int(v) for v in best]
        for i in range(DIMS):
            if prev[i] != best[i]:
                # continue in the direction that landed on best
                direction = 1 if best[i] > prev[i] else -1
                probe[i] = clip_int(best[i] + direction * max(1, step // 2))
        return probe, "coord_probe"

    return mutate(best, rng, step, iteration), "mutate_best"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="AAR-POC-001 autonomous proposer")
    ap.add_argument("--state", required=True, help="path to state.json")
    ap.add_argument("--out", required=True, help="path to write artifact.json")
    ap.add_argument("--poc-root", required=True, help="poc root (for isolation check)")
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args(argv)

    poc_root = Path(args.poc_root).resolve()
    _assert_isolation(poc_root)

    state_path = Path(args.state)
    state = load_json(state_path, {
        "iteration": 0,
        "history": [],
        "best_vector": None,
        "best_score": None,
        "injected_oob_failure": False,
        "rng_seed": 42,
    })

    seed = args.seed if args.seed is not None else int(state.get("rng_seed", 42))
    # Make each iteration's RNG stream depend on iteration + seed for resume stability
    next_iter = int(state.get("iteration", 0)) + 1
    rng = random.Random(seed + next_iter * 10007)

    vector, strategy = propose(state, rng)
    artifact = {
        "vector": vector,
        "dims": DIMS,
        "strategy": strategy,
        "proposed_iteration": next_iter,
        "meta": {
            "proposer": "aar_poc_001.researcher.proposer",
            "sees_secrets": False,
        },
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")

    # Write a small sidecar the harness can read for logging (not secrets).
    sidecar = out.parent / "propose_meta.json"
    sidecar.write_text(
        json.dumps({"strategy": strategy, "iteration": next_iter}, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
