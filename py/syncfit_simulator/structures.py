"""Data structures used by the simulator.

The frame buffer reuses the Ring Buffer implemented in `syncfit-core` (O(1)
insertion, fixed memory), keeping one implementation across the project. The
event script uses a deque for O(1) append/popleft.
"""

from __future__ import annotations

from collections import deque
from typing import Any, Iterator

from syncfit_core.structures import RingBuffer


class FrameBuffer:
    """Fixed-capacity buffer of telemetry frames backed by the core Ring Buffer."""

    def __init__(self, capacity: int = 64) -> None:
        self._buffer: RingBuffer[dict[str, Any]] = RingBuffer(capacity=capacity)

    @property
    def capacity(self) -> int:
        return self._buffer.capacity

    def push(self, frame: dict[str, Any]) -> None:
        self._buffer.append(frame)

    def latest(self) -> dict[str, Any] | None:
        return self._buffer.latest()

    def to_list(self) -> list[dict[str, Any]]:
        return self._buffer.to_list()

    def __len__(self) -> int:
        return self._buffer.size


class EventScript:
    """A queue of timestamped events to emit during a simulated session."""

    def __init__(self, events: list[tuple[float, str, dict[str, Any]]] | None = None) -> None:
        self._events: deque[tuple[float, str, dict[str, Any]]] = deque(events or [])

    def add(self, at_seconds: float, kind: str, payload: dict[str, Any] | None = None) -> None:
        self._events.append((at_seconds, kind, payload or {}))

    def next(self) -> tuple[float, str, dict[str, Any]] | None:
        return self._events.popleft() if self._events else None

    def __len__(self) -> int:
        return len(self._events)

    def __iter__(self) -> Iterator[tuple[float, str, dict[str, Any]]]:
        return iter(self._events)


__all__ = ["FrameBuffer", "EventScript"]
