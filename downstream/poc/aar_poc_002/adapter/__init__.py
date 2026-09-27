"""POC-002 adapter: VectorModel loader shim + suite benchmarks + eval entry."""
from .models_vector import VectorModel, install_vector_loader, looks_like_vector_dir

__all__ = ["VectorModel", "install_vector_loader", "looks_like_vector_dir"]
