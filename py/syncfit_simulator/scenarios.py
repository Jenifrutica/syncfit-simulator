"""Synthetic and replayable telemetry scenarios."""

from __future__ import annotations

from dataclasses import dataclass

from syncfit_core.enums import Modality


@dataclass(frozen=True)
class Scenario:
    """Parameters describing a physiological situation to simulate."""

    name: str
    modality: Modality
    day_or_week: int
    delta_temperature_c: float
    rmssd_hrv_ms: float
    isometric_force_loss_pct: float
    hr_bpm: float
    seed: int
    description: str


SCENARIOS: dict[str, Scenario] = {
    "normal": Scenario(
        name="normal",
        modality=Modality.MENSTRUAL_CYCLE,
        day_or_week=8,
        delta_temperature_c=0.12,
        rmssd_hrv_ms=62.0,
        isometric_force_loss_pct=3.0,
        hr_bpm=66.0,
        seed=1,
        description="Recovered athlete in the follicular phase.",
    ),
    "fatigue": Scenario(
        name="fatigue",
        modality=Modality.MENSTRUAL_CYCLE,
        day_or_week=24,
        delta_temperature_c=0.38,
        rmssd_hrv_ms=26.0,
        isometric_force_loss_pct=14.0,
        hr_bpm=74.0,
        seed=2,
        description="Late luteal phase with autonomic and neuromuscular fatigue.",
    ),
    "high_risk": Scenario(
        name="high_risk",
        modality=Modality.MENSTRUAL_CYCLE,
        day_or_week=14,
        delta_temperature_c=0.45,
        rmssd_hrv_ms=18.0,
        isometric_force_loss_pct=18.0,
        hr_bpm=78.0,
        seed=3,
        description="Ovulatory peak with elevated laxity and low HRV.",
    ),
    "gestational_t2": Scenario(
        name="gestational_t2",
        modality=Modality.GESTATIONAL,
        day_or_week=18,
        delta_temperature_c=0.30,
        rmssd_hrv_ms=40.0,
        isometric_force_loss_pct=8.0,
        hr_bpm=80.0,
        seed=4,
        description="Second trimester; supine exercises become contraindicated.",
    ),
}


def get_scenario(name: str) -> Scenario:
    """Return a named scenario or raise a helpful error."""
    try:
        return SCENARIOS[name]
    except KeyError as exc:
        available = ", ".join(sorted(SCENARIOS))
        raise KeyError(f"unknown scenario '{name}'. Available: {available}") from exc


def scenario_names() -> list[str]:
    return sorted(SCENARIOS)


__all__ = ["Scenario", "SCENARIOS", "get_scenario", "scenario_names"]
