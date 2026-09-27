"""Method template: write an 8-d vector.json model_path for POC-002.

Copy this file into aar/ideas/<idea_name>/run.py (or start from aar/ideas/TEMPLATE).
The Claude agent adapts the vector; this is NOT a research loop.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def run_experiment(config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return {"model_path": dir} containing vector.json."""
    config = config or {}
    out_dir = Path(config.get("out_dir") or Path.cwd() / "model_out")
    out_dir.mkdir(parents=True, exist_ok=True)
    # Default mid-point; agent should replace with a better proposal.
    vector = config.get("vector") or [50, 50, 50, 50, 50, 50, 50, 50]
    vector = [int(x) for x in vector]
    assert len(vector) == 8, "vector must have length 8"
    (out_dir / "vector.json").write_text(
        json.dumps({"vector": vector}, indent=2) + "\n", encoding="utf-8"
    )
    return {"model_path": str(out_dir.resolve())}


if __name__ == "__main__":
    print(run_experiment())
