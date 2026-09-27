"""Hill-climb benchmark: distance to TRAIN secret (role: safety)."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from aar.benchmarks.base import BenchmarkScore, RuleBenchmark

from ..scoring import extract_vector, load_params, score_vector


def _train_secret_path(secret_dir: str) -> Path:
    env = os.environ.get("POC002_TRAIN_SECRET", "")
    if env and Path(env).is_file():
        return Path(env)
    for name in ("train.json", "hillclimb_target.json"):
        p = Path(secret_dir) / name
        if p.is_file():
            return p
    # default out-of-tree location
    return Path("/home/box/aar-poc-002-secrets/train.json")


class Poc002Hillclimb(RuleBenchmark):
    name = "poc002_hillclimb"

    def load_items(self) -> list[dict[str, Any]]:
        # Vector task does not use prompt/gold items; score() overrides.
        return [{"prompt": "vector", "answer": "n/a"}]

    def matches(self, output: str, gold: Any) -> bool:
        return False

    def score(self, model) -> BenchmarkScore:
        vec = extract_vector(model)
        if vec is None:
            return BenchmarkScore(mean=0.0, ci_low=0.0, ci_high=0.0, n=0,
                                 extra={"error": "no_vector"})
        params = load_params(_train_secret_path(self.secret_dir))
        details = score_vector(vec, params)
        m = details["normalized"]
        return BenchmarkScore(
            mean=m, ci_low=m, ci_high=m, n=1,
            extra={
                "raw_score": details["raw_score"],
                "sq_error_weighted": details["sq_error_weighted"],
                "n_out_of_bounds": details["n_out_of_bounds"],
                "valid_bounds": details["valid_bounds"],
            },
        )
