"""POC-001 score semantics for 8-d int vectors (no secrets embedded).

  score = base_score - sum_i w_i*(clamp(v_i)-T_i)^2 - oob_penalty_per_dim * n_oob

Normalized mean for suite closed% = clamp(score / base_score, 0, 1).
Secrets are loaded from out-of-tree JSON by benchmarks only.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DIMS = 8
LO, HI = 0, 100


def load_params(path: Path | str) -> dict[str, Any]:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    if "target" not in data and "vector" in data:
        # legacy target-only file → uniform weights
        data = {
            "target": data["vector"],
            "weights": [1.0] * DIMS,
            "base_score": 10000.0,
            "oob_penalty_per_dim": 500.0,
            "dims": DIMS,
            "bounds": [LO, HI],
        }
    return data


def extract_vector(model: Any) -> list[int] | None:
    """Prefer VectorModel.vector; else parse generate() JSON."""
    vec = getattr(model, "vector", None)
    if isinstance(vec, list) and len(vec) == DIMS:
        try:
            return [int(x) for x in vec]
        except (TypeError, ValueError):
            return None
    try:
        raw = model.generate("")
        data = json.loads(raw) if isinstance(raw, str) else raw
        if isinstance(data, dict):
            data = data.get("vector", data)
        if isinstance(data, list) and len(data) == DIMS:
            return [int(x) for x in data]
    except Exception:
        return None
    return None


def vector_in_bounds(vec: list[int]) -> bool:
    return len(vec) == DIMS and all(isinstance(v, int) and LO <= v <= HI for v in vec)


def score_vector(vec: list[int], params: dict[str, Any]) -> dict[str, Any]:
    T = params["target"]
    W = params["weights"]
    base = float(params["base_score"])
    oob_pen = float(params["oob_penalty_per_dim"])
    n_oob = sum(1 for v in vec if v < LO or v > HI)
    clamped = [min(HI, max(LO, int(v))) for v in vec]
    sq = sum(float(W[i]) * (clamped[i] - float(T[i])) ** 2 for i in range(DIMS))
    raw = base - sq - oob_pen * n_oob
    norm = max(0.0, min(1.0, raw / base)) if base else 0.0
    return {
        "raw_score": float(raw),
        "normalized": float(norm),
        "sq_error_weighted": float(sq),
        "n_out_of_bounds": int(n_oob),
        "oob_penalty": float(oob_pen * n_oob),
        "valid_bounds": n_oob == 0,
    }
