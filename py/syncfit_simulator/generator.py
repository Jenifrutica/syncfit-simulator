"""Synthetic telemetry generation.

Produces telemetry frames shaped exactly like the device output, so the rest of
the stack can be developed and tested while the physical hardware is being
assembled. The frames validate against `syncfit-contracts`.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Iterator

import numpy as np

from .scenarios import Scenario

SAMPLE_RATE_HZ = 100
DEFAULT_WINDOW_SIZE = 256


def synthesize_ppg(
    seconds: float = 2.56,
    fs: int = SAMPLE_RATE_HZ,
    hr_bpm: float = 70.0,
    noise: float = 0.02,
    seed: int = 0,
) -> np.ndarray:
    """Generate a plausible PPG waveform at `fs` Hz."""
    n = int(round(seconds * fs))
    if n <= 0:
        raise ValueError("seconds must be positive")
    t = np.arange(n) / fs
    base_freq = hr_bpm / 60.0
    # Fundamental plus a harmonic, resembling a systolic peak.
    signal = np.sin(2 * np.pi * base_freq * t) + 0.5 * np.sin(4 * np.pi * base_freq * t)
    rng = np.random.default_rng(seed)
    return (signal + rng.normal(0, noise, n)).astype(float)


def generate_frame(
    scenario: Scenario,
    session_id: str,
    device_id: str = "esp32-syncfit-sim",
    timestamp: datetime | None = None,
    window_size: int = DEFAULT_WINDOW_SIZE,
    frame_index: int = 0,
) -> dict:
    """Build one telemetry frame as a plain dictionary (contract-shaped)."""
    ts = timestamp or datetime.now(timezone.utc)
    ppg = synthesize_ppg(
        seconds=window_size / SAMPLE_RATE_HZ,
        hr_bpm=scenario.hr_bpm,
        seed=scenario.seed + frame_index,
    )
    return {
        "schema_version": "1.0.0",
        "device_id": device_id,
        "session_id": session_id,
        "timestamp": ts.isoformat().replace("+00:00", "Z"),
        "modality": scenario.modality.value,
        "day_or_week": scenario.day_or_week,
        "biomarkers": {
            "delta_temperature_c": scenario.delta_temperature_c,
            "rmssd_hrv_ms": scenario.rmssd_hrv_ms,
            "isometric_force_loss_pct": scenario.isometric_force_loss_pct,
        },
        "ppg_window": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "window_size": window_size,
            "samples": [round(float(x), 4) for x in ppg],
        },
    }


def generate_session(
    scenario: Scenario,
    session_id: str | None = None,
    device_id: str = "esp32-syncfit-sim",
    frames: int = 5,
    frame_interval_s: float = 1.0,
    window_size: int = DEFAULT_WINDOW_SIZE,
    start: datetime | None = None,
) -> list[dict]:
    """Generate a sequence of telemetry frames for a session."""
    if frames <= 0:
        raise ValueError("frames must be positive")
    session = session_id or str(uuid.uuid4())
    base = start or datetime.now(timezone.utc)
    return [
        generate_frame(
            scenario,
            session_id=session,
            device_id=device_id,
            timestamp=base + timedelta(seconds=i * frame_interval_s),
            window_size=window_size,
            frame_index=i,
        )
        for i in range(frames)
    ]


def stream_session(
    scenario: Scenario,
    session_id: str,
    frames: int = 5,
    frame_interval_s: float = 1.0,
) -> Iterator[dict]:
    """Yield frames lazily (for streaming into a WebSocket or harness)."""
    yield from generate_session(
        scenario, session_id=session_id, frames=frames, frame_interval_s=frame_interval_s
    )


__all__ = [
    "SAMPLE_RATE_HZ",
    "DEFAULT_WINDOW_SIZE",
    "synthesize_ppg",
    "generate_frame",
    "generate_session",
    "stream_session",
]
