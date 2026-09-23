"""Linkage to the shared contract (`syncfit-contracts`) and the core engine.

The simulator does not invent payloads: every frame it generates is validated
against the contract, and the feature mapping is delegated to `syncfit-core` so
the simulated data flows through the exact same path as real data.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from syncfit_contracts import AdaptedRoutine, TelemetryFrame, WsEnvelope
from syncfit_core.contracts_adapter import features_from_telemetry_frame


def validate_frame(frame: dict[str, Any]) -> TelemetryFrame:
    """Validate a generated frame against the telemetry contract."""
    return TelemetryFrame.model_validate(frame)


def validate_frames(frames: list[dict[str, Any]]) -> list[TelemetryFrame]:
    return [validate_frame(frame) for frame in frames]


def to_feature_kwargs(frame: dict[str, Any]) -> dict[str, Any]:
    """Map a frame to the keyword arguments of the core feature builder."""
    return features_from_telemetry_frame(frame)


def to_ws_envelope(frame: dict[str, Any], correlation_id: str | None = None) -> dict[str, Any]:
    """Wrap a frame in a validated WebSocket envelope."""
    envelope = WsEnvelope(
        type="telemetry",
        timestamp=datetime.now(timezone.utc),
        session_id=frame.get("session_id"),
        correlation_id=correlation_id,
        payload=frame,
    )
    return envelope.model_dump(mode="json")


def validate_adapted_routine(payload: dict[str, Any]) -> AdaptedRoutine:
    """Validate a reasoning output (useful when checking simulations end to end)."""
    return AdaptedRoutine.model_validate(payload)


__all__ = [
    "validate_frame",
    "validate_frames",
    "to_feature_kwargs",
    "to_ws_envelope",
    "validate_adapted_routine",
]
