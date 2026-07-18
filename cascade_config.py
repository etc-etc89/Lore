"""
CascadeFlow Configuration – Agent Governance

Monitors per-session call count, estimated token cost, and latency budgets.
Raises RuntimeError if constraints are exceeded so the agent loop can surface
a graceful error rather than silently over-spending.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

try:
    from cascadeflow import CascadeMonitor

    _monitor = CascadeMonitor(
        max_calls_per_session=50,
        max_latency_ms=8000,
        cost_per_call_usd=0.0,  # Gemini 1.5 Flash free-tier
    )

    def check_constraints() -> None:
        """Raise RuntimeError if any governance constraint is violated."""
        _monitor.check()

    def record_call() -> None:
        """Notify cascadeflow that one LLM call has completed."""
        _monitor.record()

except ImportError:
    # Graceful fallback: lightweight manual tracker
    @dataclass
    class _FallbackTracker:
        max_calls: int = 50
        calls: int = 0
        _start: float = field(default_factory=time.monotonic)

    _tracker = _FallbackTracker()

    def check_constraints() -> None:  # type: ignore[misc]
        if _tracker.calls >= _tracker.max_calls:
            raise RuntimeError(
                f"Session limit reached: {_tracker.max_calls} calls. "
                "Please start a new session."
            )

    def record_call() -> None:  # type: ignore[misc]
        _tracker.calls += 1
