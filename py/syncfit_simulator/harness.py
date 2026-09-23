"""Pipeline harness.

Feeds simulated (or replayed) telemetry through the deterministic core engine,
exactly as the backend would with real data, and collects the per-frame
decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from syncfit_core import EngineResult, FatigueModel, SyncFitEngine, train_default_model
from syncfit_core.enums import Modality

from .contracts import validate_frame
from .generator import generate_session
from .scenarios import Scenario

_DEFAULT_MODEL: FatigueModel | None = None


def default_model() -> FatigueModel:
    """Train (once per process) and cache the default fatigue model."""
    global _DEFAULT_MODEL
    if _DEFAULT_MODEL is None:
        _DEFAULT_MODEL = train_default_model(n_samples=1000, seed=42)
    return _DEFAULT_MODEL


@dataclass
class HarnessResult:
    """Outcome of running a set of frames through the engine."""

    frames: list[dict[str, Any]]
    results: list[EngineResult]

    @property
    def final(self) -> EngineResult:
        if not self.results:
            raise ValueError("no results")
        return self.results[-1]

    def to_dict(self) -> dict[str, Any]:
        return {
            "frames": len(self.frames),
            "phase_inferred": self.final.phase_inferred.value,
            "fatigue_level": self.final.fatigue_level.value,
            "k_load_multiplier": self.final.k_load,
            "decisions": [r.as_dict() for r in self.results],
        }


def run_frames(
    frames: list[dict[str, Any]],
    model: FatigueModel | None = None,
    window_size: int = 1024,
    derive_rmssd: bool = False,
) -> HarnessResult:
    """Run a list of frames through `SyncFitEngine`.

    When `derive_rmssd` is False the RMSSD reported in the frame is used (as the
    backend would when the device already computed it); when True, RMSSD is
    derived from the ingested PPG window.
    """
    engine_model = model or default_model()
    engine = SyncFitEngine(engine_model, window_size=window_size)
    results: list[EngineResult] = []
    for frame in frames:
        validated = validate_frame(frame)
        engine.ingest(validated.ppg_window.samples)
        result = engine.evaluate(
            modality=Modality(validated.modality),
            day_or_week=validated.day_or_week,
            delta_temperature_c=validated.biomarkers.delta_temperature_c,
            isometric_force_loss_pct=validated.biomarkers.isometric_force_loss_pct,
            rmssd_hrv_ms=None if derive_rmssd else validated.biomarkers.rmssd_hrv_ms,
        )
        results.append(result)
    return HarnessResult(frames=frames, results=results)


def run_scenario(
    scenario: Scenario,
    session_id: str = "3f1b2c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
    frames: int = 3,
    model: FatigueModel | None = None,
    derive_rmssd: bool = False,
) -> HarnessResult:
    """Generate synthetic frames for a scenario and run them through the engine."""
    generated = generate_session(scenario, session_id=session_id, frames=frames)
    return run_frames(generated, model=model, derive_rmssd=derive_rmssd)


__all__ = ["HarnessResult", "default_model", "run_frames", "run_scenario"]
