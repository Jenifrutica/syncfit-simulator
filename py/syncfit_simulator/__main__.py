"""Command line entry point for the simulator.

Usage:
    python -m syncfit_simulator --scenario fatigue --frames 3
    python -m syncfit_simulator --list-scenarios
    python -m syncfit_simulator --groups GLUTES,QUADRICEPS --language ES
"""

from __future__ import annotations

import argparse
import json

from .generator import generate_session
from .harness import run_frames
from .replay import save_capture
from .routine import build_routine
from .scenarios import get_scenario, scenario_names


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SyncFit Edge telemetry simulator.")
    parser.add_argument("--scenario", default="normal")
    parser.add_argument("--frames", type=int, default=3)
    parser.add_argument("--session-id", default="3f1b2c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d")
    parser.add_argument("--save", help="write the generated frames to a capture file")
    parser.add_argument("--no-run", action="store_true", help="only generate, do not run core")
    parser.add_argument("--list-scenarios", action="store_true")
    parser.add_argument("--groups", help="comma-separated muscle groups to build a routine")
    parser.add_argument("--language", default="EN", help="routine language: EN, ES, ZH")
    parser.add_argument("--per-group", type=int, default=2)
    parser.add_argument("--max-impact", default="HIGH", choices=["LOW", "MEDIUM", "HIGH"])
    args = parser.parse_args(argv)

    if args.list_scenarios:
        for name in scenario_names():
            scenario = get_scenario(name)
            print(f"{name:16s} {scenario.description}")
        return 0

    if args.groups:
        groups = [g.strip() for g in args.groups.split(",") if g.strip()]
        routine = build_routine(
            groups,
            language=args.language,
            exercises_per_group=args.per_group,
            max_impact=args.max_impact,
            session_id=args.session_id,
        )
        print(json.dumps(routine, indent=2, ensure_ascii=False))
        return 0

    scenario = get_scenario(args.scenario)
    frames = generate_session(scenario, session_id=args.session_id, frames=args.frames)

    if args.save:
        path = save_capture(frames, args.save)
        print(f"saved {len(frames)} frames -> {path}")

    if args.no_run:
        return 0

    result = run_frames(frames)
    print(json.dumps(result.to_dict()["decisions"][-1], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
