#!/usr/bin/env python3
"""Isolated evaluator for AAR-POC-001.

Loads secret params from AAR_POC_SECRET_PATH (or --secret), validates the
8-dim integer vector artifact, computes a deterministic scalar score, and
writes a scores JSON. Intended to run as a *separate process* from the
researcher so the researcher never receives the secret path env var.

Scoring (documented here + eval_secret/; researcher must not import this):
  score = base_score - sum_i w_i*(v_i - T_i)^2 - oob_penalty_per_dim * n_oob
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any


DIMS = 8
LO, HI = 0, 100


def load_secret(secret_path: Path) -> dict[str, Any]:
    if not secret_path.is_file():
        raise FileNotFoundError(f"secret params not found: {secret_path}")
    with secret_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_vector(raw: Any) -> tuple[list[int] | None, str | None]:
    """Return (vector, None) on success or (None, error_message)."""
    if not isinstance(raw, dict):
        return None, "artifact root must be a JSON object"
    vec = raw.get("vector")
    if vec is None:
        return None, "missing 'vector' field"
    if not isinstance(vec, list) or len(vec) != DIMS:
        return None, f"vector must be length-{DIMS} list, got {type(vec).__name__} len={getattr(vec, '__len__', lambda: '?')()}"
    out: list[int] = []
    for i, x in enumerate(vec):
        if isinstance(x, bool) or not isinstance(x, (int, float)) or (isinstance(x, float) and not x.is_integer()):
            return None, f"vector[{i}] must be an integer, got {x!r}"
        xi = int(x)
        if xi < LO or xi > HI:
            return None, f"vector[{i}]={xi} out of bounds [{LO},{HI}]"
        out.append(xi)
    return out, None


def score_vector(vec: list[int], params: dict[str, Any]) -> dict[str, Any]:
    T = params["target"]
    W = params["weights"]
    base = float(params["base_score"])
    oob_pen = float(params["oob_penalty_per_dim"])
    assert len(T) == DIMS and len(W) == DIMS

    n_oob = sum(1 for v in vec if v < LO or v > HI)
    # Clamp for distance term so OOB still has a defined distance; penalty separate.
    clamped = [min(HI, max(LO, v)) for v in vec]
    sq = sum(float(W[i]) * (clamped[i] - float(T[i])) ** 2 for i in range(DIMS))
    score = base - sq - oob_pen * n_oob
    return {
        "score": float(score),
        "sq_error_weighted": float(sq),
        "n_out_of_bounds": n_oob,
        "oob_penalty": float(oob_pen * n_oob),
        "valid_bounds": n_oob == 0,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="AAR-POC-001 isolated artifact scorer")
    ap.add_argument("--artifact", required=True, help="path to artifact.json")
    ap.add_argument("--out", required=True, help="path to write scores JSON")
    ap.add_argument(
        "--secret",
        default=os.environ.get("AAR_POC_SECRET_PATH", ""),
        help="path to secret params JSON (or set AAR_POC_SECRET_PATH)",
    )
    ap.add_argument("--role", default="", help="optional role label for output")
    ap.add_argument("--iteration", type=int, default=-1)
    args = ap.parse_args(argv)

    if not args.secret:
        print("ERROR: no secret path (pass --secret or AAR_POC_SECRET_PATH)", file=sys.stderr)
        return 2

    secret_path = Path(args.secret)
    try:
        params = load_secret(secret_path)
    except Exception as e:
        print(f"ERROR loading secret: {e}", file=sys.stderr)
        return 2

    artifact_path = Path(args.artifact)
    try:
        with artifact_path.open("r", encoding="utf-8") as f:
            artifact = json.load(f)
    except Exception as e:
        err = {"ok": False, "error": f"failed to read artifact: {e}", "score": None}
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(err, indent=2) + "\n", encoding="utf-8")
        return 1

    vec, verr = validate_vector(artifact)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if verr is not None:
        payload = {
            "ok": False,
            "error": verr,
            "score": None,
            "role": args.role or params.get("role", ""),
            "iteration": args.iteration,
            "artifact_path": str(artifact_path),
        }
        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return 1

    details = score_vector(vec, params)
    payload = {
        "ok": True,
        "error": None,
        "score": details["score"],
        "details": {
            "sq_error_weighted": details["sq_error_weighted"],
            "n_out_of_bounds": details["n_out_of_bounds"],
            "oob_penalty": details["oob_penalty"],
            "valid_bounds": details["valid_bounds"],
            # Deliberately omit target/weights from research-visible scores.
        },
        "role": args.role or params.get("role", ""),
        "iteration": args.iteration,
        "artifact_path": str(artifact_path),
        "vector": vec,
    }
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
