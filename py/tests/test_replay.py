from syncfit_simulator.generator import generate_session
from syncfit_simulator.replay import (
    list_captures,
    load_capture,
    replay,
    replay_file,
    save_capture,
)
from syncfit_simulator.scenarios import get_scenario


def test_save_and_load_capture(tmp_path):
    frames = generate_session(get_scenario("normal"), session_id="sid", frames=2)
    path = save_capture(frames, tmp_path / "captures" / "normal.json")
    assert path.is_file()
    loaded = load_capture(path)
    assert loaded == frames


def test_replay_and_replay_file(tmp_path):
    frames = generate_session(get_scenario("fatigue"), session_id="sid", frames=2)
    path = save_capture(frames, tmp_path / "fatigue.json")
    assert list(replay(frames)) == frames
    assert list(replay_file(path)) == frames


def test_list_captures(tmp_path):
    frames = generate_session(get_scenario("normal"), session_id="sid", frames=1)
    save_capture(frames, tmp_path / "a.json")
    save_capture(frames, tmp_path / "b.json")
    assert [p.name for p in list_captures(tmp_path)] == ["a.json", "b.json"]


def test_load_missing_capture(tmp_path):
    import pytest

    with pytest.raises(FileNotFoundError):
        load_capture(tmp_path / "missing.json")
