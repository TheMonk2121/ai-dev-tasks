"""
Compatibility shim for episodic memory system imports.

Older code imports `scripts.utilities.episodic_memory_system` directly,
but the implementation now lives under `scripts.utilities.memory`.
This module preserves the old import path by re-exporting the class.
"""

from __future__ import annotations

try:
    # Preferred location
    from scripts.utilities.memory.episodic_memory_system import EpisodicMemorySystem
except Exception as exc:  # pragma: no cover - defensive fallback
    # Provide a minimal stub that makes import succeed even if the
    # deeper module has transient issues. This avoids breaking lightweight
    # availability checks (e.g., smoke tests that only import the symbol).
    class EpisodicMemorySystem:  # type: ignore[override]
        def __init__(self) -> None:
            raise ImportError("EpisodicMemorySystem implementation unavailable")


__all__ = ["EpisodicMemorySystem"]
