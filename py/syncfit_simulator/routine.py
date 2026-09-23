"""Deterministic routine generation from the shared exercise catalog.

Given one or more muscle groups (isolated, region or pattern) and a target
language, this builds a safe routine using only catalog exercises. It is the
fluid, offline path used while the hardware is being built and while the AI
reasoning layer is optional; the AI layer produces the same shape.
"""

from __future__ import annotations

from typing import Iterable

from syncfit_contracts import (
    Exercise,
    ExerciseImpact,
    MuscleGroup,
    RoutineRequest,
    RoutineResponse,
    exercises_for_groups,
    localize,
)

DEFAULT_EXERCISES_PER_GROUP = 2

_IMPACT_RANK = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}


def _value(item: object) -> str:
    return item.value if hasattr(item, "value") else str(item)


def _impact_rank(impact: object) -> int:
    return _IMPACT_RANK.get(_value(impact), 2)


def _localized_name(exercise: Exercise) -> dict[str, str]:
    name = exercise.name
    data = {"en": name.en}
    data.update(name.model_extra or {})
    return data


def _localized_description(exercise: Exercise) -> dict[str, str]:
    description = exercise.description
    data = {"en": description.en}
    data.update(description.model_extra or {})
    return data


def to_adaptation(exercise: Exercise, language: str, max_impact: str = "HIGH") -> dict:
    """Convert a catalog exercise into an `ExerciseAdaptation`-shaped entry."""
    blocked = _impact_rank(exercise.impact) > _impact_rank(max_impact)
    return {
        "exercise_original": localize(exercise.name, language),
        "blocked": blocked,
        "block_reason": (
            f"Impact {_value(exercise.impact)} above the safe limit {max_impact}."
            if blocked
            else ""
        ),
        "exercise_substitute": "",
        "series_adapted": 3,
        "reps_adapted": 10,
        "weight_suggested_kg": 0.0,
        "exercise_id": exercise.id,
        "muscle_groups": list(exercise.muscle_groups),
        "impact": _value(exercise.impact),
        "description": _localized_description(exercise),
        "image_url": exercise.image_url,
        "media_url": exercise.media_url,
    }


def select_exercises(
    muscle_groups: Iterable[str],
    exercises_per_group: int = DEFAULT_EXERCISES_PER_GROUP,
    max_impact: str = "HIGH",
) -> list[Exercise]:
    """Pick catalog exercises covering every requested muscle group, deduplicated."""
    selected: list[Exercise] = []
    seen: set[str] = set()
    for group in muscle_groups:
        candidates = exercises_for_groups([group])
        safe = [e for e in candidates if _impact_rank(e.impact) <= _impact_rank(max_impact)]
        pool = safe or candidates
        count = 0
        for exercise in pool:
            if exercise.id in seen:
                continue
            seen.add(exercise.id)
            selected.append(exercise)
            count += 1
            if count >= exercises_per_group:
                break
    return selected


def build_routine(
    muscle_groups: Iterable[str],
    language: str = "EN",
    exercises_per_group: int = DEFAULT_EXERCISES_PER_GROUP,
    max_impact: str = "HIGH",
    session_id: str | None = None,
) -> dict:
    """Build a validated `RoutineResponse`-shaped dictionary."""
    groups = [_value(g) for g in muscle_groups]
    exercises = select_exercises(groups, exercises_per_group, max_impact)
    routine = [to_adaptation(exercise, language, max_impact) for exercise in exercises]
    response = RoutineResponse(
        session_id=session_id,
        language=language,
        muscle_groups=groups,
        routine=routine,
    )
    return response.model_dump(mode="json")


def build_routine_from_request(request: RoutineRequest, max_impact: str = "HIGH") -> dict:
    """Build a routine directly from a contract request."""
    groups = [_value(g) for g in request.muscle_groups]
    count = request.exercises_per_group or DEFAULT_EXERCISES_PER_GROUP
    return build_routine(
        groups,
        language=_value(request.language),
        exercises_per_group=count,
        max_impact=max_impact,
        session_id=request.session_id,
    )


def muscle_group_catalog() -> dict[str, list[str]]:
    """Group the catalog ids by muscle group, for UI hints."""
    result: dict[str, list[str]] = {}
    for group in MuscleGroup:
        group_value = _value(group)
        ids = [e.id for e in exercises_for_groups([group_value])]
        if ids:
            result[group_value] = ids
    return result


__all__ = [
    "DEFAULT_EXERCISES_PER_GROUP",
    "to_adaptation",
    "select_exercises",
    "build_routine",
    "build_routine_from_request",
    "muscle_group_catalog",
]
