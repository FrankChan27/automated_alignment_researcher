"""Held-out benchmark: different secret T' (role: held_out; stripped from research scores)."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from aar.benchmarks.base import BenchmarkScore, RuleBenchmark

from ..scoring import extract_vector, load_params, score_vector


def _heldout_secret_path(secret_dir: str) -> Path:
    env = os.environ.get("POC002_HELDOUT_SECRET", "")
    if env and Path(env).is_file():
        return Path(env)
    for name in ("heldout.json", "heldout_target.json"):
        p = Path(secret_dir) / name
        if p.is_file():
            return p
    return Path("/home/box/aar-poc-002-secrets/heldout.json")


class Poc002Heldout(RuleBenchmark):
    name = "poc002_heldout"

    def load_items(self) -> list[dict[str, Any]]:
        return [{"prompt": "vector", "answer": "n/a"}]

    def matches(self, output: str, gold: Any) -> bool:
        return False

    def score(self, model) -> BenchmarkScore:
        vec = extract_vector(model)
        if vec is None:
            return BenchmarkScore(mean=0.0, ci_low=0.0, ci_high=0.0, n=0,
                                 extra={"error": "no_vector"})
        params = load_params(_heldout_secret_path(self.secret_dir))
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
