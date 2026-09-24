"""Deterministic routine generation from the shared exercise catalog.

Given one or more muscle groups, this builds a safe, localized routine with a
warm-up/activation block, approximation sets, effective sets, rests and an
estimated duration. If a time budget is provided, the routine is adapted to fit.
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
    load_exercises,
    localize,
)

DEFAULT_EXERCISES_PER_GROUP = 2
DEFAULT_EXERCISES_COUNT = 5  # recommended main exercises
DEFAULT_EFFECTIVE_SETS = 3
DEFAULT_APPROXIMATION_SETS = 2
DEFAULT_REPS = 10
SECONDS_PER_REP = 3

_IMPACT_RANK = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
_REST_BY_IMPACT = {"HIGH": 150, "MEDIUM": 90, "LOW": 60}


def _value(item: object) -> str:
    return item.value if hasattr(item, "value") else str(item)


def _rank(impact: object) -> int:
    return _IMPACT_RANK.get(_value(impact), 2)


def _rest_for(impact: object) -> int:
    return _REST_BY_IMPACT.get(_value(impact), 90)


def _set(set_type: str, reps: int, weight: float, rest: int, tempo: str | None = None) -> dict:
    return {
        "type": set_type,
        "reps": int(reps),
        "weight_kg": round(float(weight), 1),
        "rest_seconds": int(rest),
        "tempo": tempo,
        "estimated_seconds": int(reps * SECONDS_PER_REP + rest),
    }


def _localized_text(node) -> dict[str, str]:
    data = {"en": node.en}
    data.update(node.model_extra or {})
    return data


def to_adaptation(
    exercise: Exercise,
    language: str,
    max_impact: str = "HIGH",
    working_weight: float = 0.0,
) -> dict:
    """Convert a catalog exercise into an adaptation with sets and timing."""
    blocked = _rank(exercise.impact) > _rank(max_impact)
    rest = _rest_for(exercise.impact)
    role = _value(getattr(exercise, "role", "MAIN"))

    sets: list[dict] = []
    if role in ("WARMUP", "ACTIVATION"):
        set_type = "WARMUP" if role == "WARMUP" else "ACTIVATION"
        sets = [_set(set_type, 12, 0.0, 30) for _ in range(2)]
    else:
        weight = working_weight
        # Approximation sets ramp up to the working weight.
        for i in range(DEFAULT_APPROXIMATION_SETS):
            factor = 0.5 if i == 0 else 0.75
            sets.append(_set("APPROXIMATION", DEFAULT_REPS, weight * factor, 60))
        # Effective working sets.
        sets.extend(
            _set("EFFECTIVE", DEFAULT_REPS, weight, rest)
            for _ in range(DEFAULT_EFFECTIVE_SETS)
        )

    estimated = sum(item["estimated_seconds"] for item in sets)
    return {
        "exercise_original": localize(exercise.name, language),
        "blocked": blocked,
        "block_reason": (
            f"Impact {_value(exercise.impact)} above the safe limit {max_impact}."
            if blocked
            else ""
        ),
        "exercise_substitute": "",
        "series_adapted": DEFAULT_EFFECTIVE_SETS,
        "reps_adapted": DEFAULT_REPS,
        "weight_suggested_kg": round(float(working_weight), 1),
        "exercise_id": exercise.id,
        "muscle_groups": list(exercise.muscle_groups),
        "impact": _value(exercise.impact),
        "description": _localized_text(exercise.description),
        "how_to": _localized_text(exercise.how_to) if exercise.how_to else None,
        "tips": [_localized_text(t) for t in (exercise.tips or [])],
        "image_url": exercise.image_url,
        "media_url": exercise.media_url,
        "role": role,
        "rest_seconds": rest,
        "estimated_seconds": estimated,
        "sets": sets,
    }


def select_exercises(
    muscle_groups: Iterable[str],
    exercises_per_group: int = DEFAULT_EXERCISES_PER_GROUP,
    max_impact: str = "HIGH",
    roles: tuple[str, ...] = ("MAIN",),
) -> list[Exercise]:
    """Pick catalog exercises covering every group, deduplicated and by role."""
    selected: list[Exercise] = []
    seen: set[str] = set()
    for group in muscle_groups:
        candidates = exercises_for_groups([group])
        safe = [
            e
            for e in candidates
            if _value(getattr(e, "role", "MAIN")) in roles
            and _rank(e.impact) <= _rank(max_impact)
        ]
        pool = safe or [e for e in candidates if _value(getattr(e, "role", "MAIN")) in roles]
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


def _select_warmup(muscle_groups: Iterable[str], limit: int = 2) -> list[Exercise]:
    selected: list[Exercise] = []
    seen: set[str] = set()
    for group in muscle_groups:
        for exercise in exercises_for_groups([group]):
            role = _value(getattr(exercise, "role", "MAIN"))
            if role not in ("WARMUP", "ACTIVATION") or exercise.id in seen:
                continue
            seen.add(exercise.id)
            selected.append(exercise)
            if len(selected) >= limit:
                return selected
    # Fallback: any warm-up/activation exercise so the block is never empty.
    if len(selected) < limit:
        for exercise in load_exercises():
            role = _value(getattr(exercise, "role", "MAIN"))
            if role in ("WARMUP", "ACTIVATION") and exercise.id not in seen:
                seen.add(exercise.id)
                selected.append(exercise)
                if len(selected) >= limit:
                    break
    return selected


def _trim_to_budget(routine: list[dict], budget_seconds: int) -> list[dict]:
    """Drop the lowest-priority (last) exercises until the budget fits."""
    trimmed = list(routine)
    while trimmed and sum(e["estimated_seconds"] for e in trimmed) > budget_seconds:
        trimmed.pop()
    return trimmed


def build_routine(
    muscle_groups: Iterable[str],
    language: str = "EN",
    exercises_per_group: int = DEFAULT_EXERCISES_PER_GROUP,
    max_impact: str = "HIGH",
    session_id: str | None = None,
    exercises_count: int | None = None,
    time_budget_minutes: int | None = None,
    include_warmup: bool = True,
    objective: str | None = None,
) -> dict:
    """Build a validated `RoutineResponse`-shaped dictionary."""
    groups = [_value(g) for g in muscle_groups]
    warmup: list[dict] = []
    if include_warmup:
        warmup = [to_adaptation(e, language, max_impact) for e in _select_warmup(groups, 2)]

    if exercises_count:
        per_group = max(1, -(-exercises_count // len(groups)))
        cap: int | None = exercises_count
    else:
        per_group = exercises_per_group
        cap = None

    main = select_exercises(groups, exercises_per_group=per_group, max_impact=max_impact)
    routine = [to_adaptation(e, language, max_impact) for e in main]
    if cap is not None:
        routine = routine[:cap]

    if time_budget_minutes:
        budget_seconds = time_budget_minutes * 60
        warmup_seconds = sum(e["estimated_seconds"] for e in warmup)
        routine = _trim_to_budget(routine, max(budget_seconds - warmup_seconds, 0))

    total = sum(e["estimated_seconds"] for e in warmup + routine)
    response = RoutineResponse(
        session_id=session_id,
        language=language,
        muscle_groups=groups,
        total_estimated_minutes=round(total / 60, 1),
        warmup=warmup,
        routine=routine,
    )
    return response.model_dump(mode="json")


def build_routine_from_request(request: RoutineRequest, max_impact: str = "HIGH") -> dict:
    """Build a routine directly from a contract request."""
    groups = [_value(g) for g in request.muscle_groups]
    return build_routine(
        groups,
        language=_value(request.language),
        exercises_per_group=request.exercises_per_group or DEFAULT_EXERCISES_PER_GROUP,
        max_impact=max_impact,
        session_id=request.session_id,
        exercises_count=request.exercises_count,
        time_budget_minutes=request.time_budget_minutes,
        include_warmup=request.include_warmup,
        objective=_value(request.objective) if request.objective else None,
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
    "DEFAULT_EXERCISES_COUNT",
    "to_adaptation",
    "select_exercises",
    "build_routine",
    "build_routine_from_request",
    "muscle_group_catalog",
]
