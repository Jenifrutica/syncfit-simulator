import pytest

from syncfit_simulator.contracts import (
    to_feature_kwargs,
    to_ws_envelope,
    validate_frame,
    validate_frames,
)
from syncfit_simulator.generator import generate_frame
from syncfit_simulator.scenarios import get_scenario


def test_generated_frame_validates_against_contracts():
    frame = generate_frame(get_scenario("high_risk"), session_id="sid")
    validated = validate_frame(frame)
    assert validated.modality == "MENSTRUAL_CYCLE"
    assert validated.biomarkers.isometric_force_loss_pct == 18.0


def test_validate_frames_batch():
    frames = [generate_frame(get_scenario("gestational_t2"), session_id="sid")]
    assert len(validate_frames(frames)) == 1


def test_invalid_frame_is_rejected():
    frame = generate_frame(get_scenario("normal"), session_id="sid")
    frame["biomarkers"]["rmssd_hrv_ms"] = 9999
    with pytest.raises(Exception):
        validate_frame(frame)


def test_feature_kwargs_link_to_core_adapter():
    frame = generate_frame(get_scenario("fatigue"), session_id="sid")
    kwargs = to_feature_kwargs(frame)
    assert kwargs["rmssd_hrv_ms"] == 26.0
    assert kwargs["day_or_week"] == 24


def test_ws_envelope_is_valid():
    frame = generate_frame(get_scenario("normal"), session_id="3f1b2c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d")
    envelope = to_ws_envelope(frame)
    assert envelope["type"] == "telemetry"
    assert envelope["payload"]["session_id"] == frame["session_id"]
