"""
Memory Manager – Hindsight integration

Uses Hindsight's retain/recall API to store and retrieve temporal lore facts
associated with pairs of entities (keyed as "entity_a::entity_b").
"""
from __future__ import annotations

try:
    from hindsight import Memory

    _mem = Memory()

    def retain(key: str, value: str) -> None:
        """Store a lore fact under the given key."""
        _mem.retain(key=key, value=value)

    def recall(key: str) -> str | None:
        """Recall the most recent lore fact for the given key, or None."""
        result = _mem.recall(key=key)
        return result if result else None

except ImportError:
    # Graceful fallback: in-process dictionary when Hindsight is unavailable
    _store: dict[str, str] = {}

    def retain(key: str, value: str) -> None:  # type: ignore[misc]
        _store[key] = value

    def recall(key: str) -> str | None:  # type: ignore[misc]
        return _store.get(key)
