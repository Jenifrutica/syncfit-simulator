import numpy as np
import pytest

from syncfit_simulator.generator import (
    SAMPLE_RATE_HZ,
    generate_frame,
    generate_session,
    synthesize_ppg,
)
from syncfit_simulator.scenarios import get_scenario


def test_synthesize_ppg_shape_and_range():
    signal = synthesize_ppg(seconds=2.0, hr_bpm=60, seed=1)
    assert signal.shape == (200,)
    assert np.isfinite(signal).all()


def test_generate_frame_matches_window_size():
    scenario = get_scenario("normal")
    frame = generate_frame(scenario, session_id="sid", window_size=128)
    assert frame["ppg_window"]["sample_rate_hz"] == SAMPLE_RATE_HZ
    assert len(frame["ppg_window"]["samples"]) == 128
    assert frame["modality"] == scenario.modality.value
    assert frame["day_or_week"] == scenario.day_or_week


def test_generate_session_is_ordered_and_deterministic():
    scenario = get_scenario("fatigue")
    a = generate_session(scenario, session_id="sid", frames=3)
    b = generate_session(scenario, session_id="sid", frames=3)
    assert len(a) == 3
    assert [f["timestamp"] for f in a] == sorted(f["timestamp"] for f in a)
    assert a[0]["ppg_window"]["samples"] == b[0]["ppg_window"]["samples"]


def test_generate_session_invalid():
    with pytest.raises(ValueError):
        generate_session(get_scenario("normal"), frames=0)
    with pytest.raises(ValueError):
        synthesize_ppg(seconds=0)
