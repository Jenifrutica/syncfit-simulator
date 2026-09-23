"""Capture replay.

Real captures recorded from the hardware will be dropped into `captures/` as
JSON files. The simulator can replay them through the same harness used for
synthetic data, so the rest of the system does not care where the data came from.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

DEFAULT_CAPTURE_DIR = Path(__file__).resolve().parents[2] / "captures"


def save_capture(frames: list[dict[str, Any]], path: str | Path) -> Path:
    """Persist a list of frames as a JSON capture file."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(frames, indent=2), encoding="utf-8")
    return target


def load_capture(path: str | Path) -> list[dict[str, Any]]:
    """Load frames from a JSON capture file."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"capture not found: {source}")
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("capture file must contain a JSON array of frames")
    return data


def list_captures(directory: str | Path | None = None) -> list[Path]:
    """List available capture files, sorted by name."""
    target = Path(directory) if directory else DEFAULT_CAPTURE_DIR
    if not target.is_dir():
        return []
    return sorted(target.glob("*.json"))


def replay(frames: list[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    """Yield frames in order."""
    yield from frames


def replay_file(path: str | Path) -> Iterator[dict[str, Any]]:
    yield from replay(load_capture(path))


__all__ = [
    "DEFAULT_CAPTURE_DIR",
    "save_capture",
    "load_capture",
    "list_captures",
    "replay",
    "replay_file",
]
