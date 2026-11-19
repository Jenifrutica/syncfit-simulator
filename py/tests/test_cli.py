"""The command line entry point (python -m syncfit_simulator)."""

import json

from syncfit_simulator.__main__ import main
from syncfit_simulator.scenarios import scenario_names


def test_list_scenarios_prints_every_scenario(capsys):
    assert main(["--list-scenarios"]) == 0
    out = capsys.readouterr().out
    for name in scenario_names():
        assert name in out


def test_groups_prints_a_routine_as_json(capsys):
    assert main(["--groups", "GLUTES", "--language", "ES", "--count", "2"]) == 0
    routine = json.loads(capsys.readouterr().out)
    assert routine["language"] == "ES"
    assert routine["muscle_groups"] == ["GLUTES"]


def test_save_without_running_writes_a_capture(tmp_path, capsys):
    target = tmp_path / "capture.json"
    assert main(["--scenario", "normal", "--frames", "2", "--save", str(target), "--no-run"]) == 0
    assert "saved 2 frames" in capsys.readouterr().out
    assert target.exists() and target.stat().st_size > 0
