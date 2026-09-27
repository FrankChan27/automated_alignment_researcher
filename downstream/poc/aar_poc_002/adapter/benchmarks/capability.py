"""Capability gate: vector length 8 and all dims in [0, 100]."""
from __future__ import annotations

from typing import Any

from aar.benchmarks.base import BenchmarkScore, RuleBenchmark

from ..scoring import DIMS, HI, LO, extract_vector, vector_in_bounds


class Poc002Capability(RuleBenchmark):
    name = "poc002_capability"

    def load_items(self) -> list[dict[str, Any]]:
        return [{"prompt": "vector", "answer": "n/a"}]

    def matches(self, output: str, gold: Any) -> bool:
        return False

    def score(self, model) -> BenchmarkScore:
        vec = extract_vector(model)
        ok = vec is not None and vector_in_bounds(vec)
        # Also accept length-8 ints that may be OOB for scoring distance, but
        # capability requires in-bounds (floor: 1.0).
        m = 1.0 if ok else 0.0
        extra = {
            "length_ok": vec is not None and len(vec) == DIMS,
            "bounds_ok": ok,
            "bounds": [LO, HI],
        }
        return BenchmarkScore(mean=m, ci_low=m, ci_high=m, n=1, extra=extra)
