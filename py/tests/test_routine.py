from syncfit_contracts import RoutineRequest, RoutineResponse
from syncfit_simulator.routine import (
    build_routine,
    build_routine_from_request,
    muscle_group_catalog,
    select_exercises,
    to_adaptation,
)
from syncfit_contracts import get_exercise


def test_build_routine_is_valid_and_localized():
    result = build_routine(["GLUTES", "QUADRICEPS"], language="ES")
    model = RoutineResponse.model_validate(result)
    assert model.language == "ES"
    assert set(model.muscle_groups) == {"GLUTES", "QUADRICEPS"}
    assert len(model.routine) >= 2
    # Spanish names come from the catalog.
    assert all(entry.image_url for entry in model.routine)
    assert all(entry.description is not None for entry in model.routine)


def test_build_routine_supports_chinese():
    result = build_routine(["SHOULDERS"], language="ZH")
    assert result["language"] == "ZH"
    assert result["routine"][0]["description"]["zh"]


def test_select_exercises_covers_requested_groups():
    exercises = select_exercises(["GLUTES", "ABS"], exercises_per_group=1)
    all_groups = {str(g) for e in exercises for g in e.muscle_groups}
    assert "GLUTES" in all_groups
    assert "ABS" in all_groups
    ids = [e.id for e in exercises]
    assert len(ids) == len(set(ids))  # deduplicated


def test_max_impact_filters_high_impact():
    routines = build_routine(["FULL_LEG"], max_impact="LOW")
    assert all(entry["impact"] == "LOW" for entry in routines["routine"])


def test_general_group_selection():
    routines = build_routine(["UPPER_BODY"], exercises_per_group=3)
    assert len(routines["routine"]) >= 1
    all_groups = {str(g) for entry in routines["routine"] for g in entry["muscle_groups"]}
    assert "UPPER_BODY" in all_groups


def test_build_from_request():
    request = RoutineRequest(muscle_groups=["GLUTES"], language="EN", exercises_per_group=2)
    result = build_routine_from_request(request)
    model = RoutineResponse.model_validate(result)
    assert model.session_id == request.session_id
    assert len(model.routine) >= 1


def test_to_adaptation_shape():
    exercise = get_exercise("goblet-squat")
    assert exercise is not None
    entry = to_adaptation(exercise, "EN")
    assert entry["exercise_id"] == "goblet-squat"
    assert entry["image_url"].startswith("https://")
    assert entry["impact"] == "LOW"
    assert entry["blocked"] is False


def test_muscle_group_catalog_has_glutes():
    catalog = muscle_group_catalog()
    assert "GLUTES" in catalog and len(catalog["GLUTES"]) >= 1


def _flat(groups):
    return {str(g) for g in groups}
