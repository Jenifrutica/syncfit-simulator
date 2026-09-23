"""SyncFit Simulator - synthetic and replayable telemetry.

Generates contract-valid telemetry and replays real hardware captures so the
backend, core and frontend can be developed and demonstrated while the physical
device is being assembled. It substitutes the hardware layer and reuses the exact
same features and data structures as the rest of the system.
"""

from .contracts import (
    to_feature_kwargs,
    to_ws_envelope,
    validate_adapted_routine,
    validate_frame,
    validate_frames,
)
from .generator import (
    SAMPLE_RATE_HZ,
    generate_frame,
    generate_session,
    stream_session,
    synthesize_ppg,
)
from .harness import HarnessResult, default_model, run_frames, run_scenario
from .replay import (
    DEFAULT_CAPTURE_DIR,
    list_captures,
    load_capture,
    replay,
    replay_file,
    save_capture,
)
from .scenarios import SCENARIOS, Scenario, get_scenario, scenario_names
from .structures import EventScript, FrameBuffer

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "SAMPLE_RATE_HZ",
    "generate_frame",
    "generate_session",
    "stream_session",
    "synthesize_ppg",
    "validate_frame",
    "validate_frames",
    "to_feature_kwargs",
    "to_ws_envelope",
    "validate_adapted_routine",
    "HarnessResult",
    "default_model",
    "run_frames",
    "run_scenario",
    "Scenario",
    "SCENARIOS",
    "get_scenario",
    "scenario_names",
    "FrameBuffer",
    "EventScript",
    "DEFAULT_CAPTURE_DIR",
    "save_capture",
    "load_capture",
    "list_captures",
    "replay",
    "replay_file",
]
