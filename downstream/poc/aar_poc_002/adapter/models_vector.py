"""VectorModel + install_vector_loader() monkeypatch for aar.eval_pod.models.load_model.

Applied at process start by launch wrapper / adapter.eval — no edits to aar/*.py on disk.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def looks_like_vector_dir(model_ref: str) -> bool:
    return Path(model_ref).joinpath("vector.json").is_file()


class VectorModel:
    """Minimal Model-protocol stand-in: holds an 8-d int vector from vector.json."""

    def __init__(self, model_path: str):
        raw = json.loads(Path(model_path).joinpath("vector.json").read_text())
        vec = raw["vector"] if isinstance(raw, dict) else raw
        self.vector = [int(x) for x in vec]
        if len(self.vector) != 8:
            raise ValueError(f"expected length-8 vector, got {len(self.vector)}")
        self.model_path = model_path

    def generate(self, prompt: Any, **_: object) -> str:
        return json.dumps(self.vector)

    def generate_batch(self, prompts: list, **kw) -> list[str]:
        return [self.generate(p, **kw) for p in prompts]

    def candidate_logits(self, prompt, candidates, use_chat_template: bool = True):
        return [0.0 for _ in candidates]

    def candidate_logits_batch(self, prompts, candidates, use_chat_template: bool = True):
        return [self.candidate_logits(p, candidates, use_chat_template) for p in prompts]

    def completion_logprob_batch(self, prompts, completions, use_chat_template: bool = False):
        return [0.0 for _ in prompts]


def install_vector_loader() -> None:
    """Monkeypatch aar.eval_pod.models.load_model — no upstream file edit."""
    from aar.eval_pod import models as _models

    if getattr(_models.load_model, "_poc002_vector_patched", False):
        return

    _orig = _models.load_model

    def load_model(model_ref: str):
        if looks_like_vector_dir(model_ref):
            return VectorModel(model_ref)
        return _orig(model_ref)

    load_model._poc002_vector_patched = True  # type: ignore[attr-defined]
    _models.load_model = load_model  # type: ignore[assignment]
