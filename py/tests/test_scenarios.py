import pytest

from syncfit_simulator.scenarios import SCENARIOS, get_scenario, scenario_names


def test_scenarios_available():
    assert set(scenario_names()) == {"normal", "fatigue", "high_risk", "gestational_t2"}
    assert all(isinstance(s, str) for s in scenario_names())


def test_get_scenario_returns_expected():
    scenario = get_scenario("high_risk")
    assert scenario.day_or_week == 14
    assert scenario.rmssd_hrv_ms == 18.0
    assert scenario.modality.value == "MENSTRUAL_CYCLE"


def test_unknown_scenario_lists_available():
    with pytest.raises(KeyError) as excinfo:
        get_scenario("nope")
    assert "normal" in str(excinfo.value)


def test_all_scenarios_have_descriptions():
    assert all(scenario.description for scenario in SCENARIOS.values())
