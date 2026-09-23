from syncfit_simulator.generator import generate_session
from syncfit_simulator.harness import run_frames, run_scenario
from syncfit_simulator.scenarios import get_scenario


def test_run_scenario_end_to_end(model):
    result = run_scenario(get_scenario("high_risk"), frames=2, model=model)
    payload = result.to_dict()
    assert payload["frames"] == 2
    assert payload["phase_inferred"] == "OVULATORY"
    assert 0.70 <= payload["k_load_multiplier"] <= 1.05
    assert len(payload["decisions"]) == 2


def test_run_frames_preserves_biomarker_rmssd(model):
    frames = generate_session(get_scenario("fatigue"), session_id="sid", frames=1)
    result = run_frames(frames, model=model)
    assert result.final.rmssd_hrv_ms == 26.0


def test_run_frames_can_derive_rmssd(model):
    frames = generate_session(get_scenario("normal"), session_id="sid", frames=1)
    result = run_frames(frames, model=model, derive_rmssd=True)
    assert result.final.rmssd_hrv_ms >= 0.0


def test_gestational_scenario_infers_trimester(model):
    result = run_scenario(get_scenario("gestational_t2"), frames=1, model=model)
    assert result.final.phase_inferred.value == "TRIMESTER_2"
