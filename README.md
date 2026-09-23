# SyncFit Simulator

Polyglot test harness that removes the dependency on physical hardware. It replays real captures and generates synthetic telemetry so that backend, core and frontend can be developed, tested and demonstrated before the device is assembled.

## Purpose

Enable parallel development: any team can exercise the full pipeline without waiting for a working sensor rig.

## What belongs here

- **`py/`** — Python package `syncfit_simulator`:
  - Synthetic signal generation (PPG waveform, thermal delta, isometric loss) shaped as telemetry frames.
  - Capture replay: real hardware samples dropped into `captures/` are replayed through the same harness.
  - Pipeline harness that feeds `syncfit-core` exactly as the backend would with real data.
  - Validation against `syncfit-contracts`.
- **`typescript/`** — TypeScript package `@syncfit/simulator`:
  - Synthetic telemetry generator (deterministic).
  - Reference WebSocket client that emits contract-shaped envelopes.
  - Optional JSON Schema validation using the contracts schemas.
- **`scenarios/`** — scenario documentation.
- **`captures/`** — real hardware captures (JSON), replayed while new ones are recorded.

## Substituting the hardware

While the physical device is being assembled, this repository stands in for it:

1. `generateFrame` / `generate_session` produce contract-valid telemetry at 100 Hz.
2. The harness validates each frame with `syncfit-contracts` and pushes it through
   `syncfit-core`, producing the same `k_load` decisions the device would trigger.
3. When real captures arrive (from `syncfit-hardware`), drop them in `captures/`
   as JSON and replay them: the rest of the stack cannot tell the difference.
4. The TypeScript WebSocket client emits the identical envelopes, so the backend
   can be developed against simulated traffic.

## What does NOT belong here

- Production logic, model training or hardware drivers.

## Data Structures

| Structure | Complexity | Purpose |
|-----------|:----------:|---------|
| **Ring Buffer** | O(1) insert | FrameBuffer reuses `syncfit_core.structures.RingBuffer` (fixed-memory frame buffering). |
| **deque** | O(1) append/popleft | `EventScript` for scripted event sequences during a simulated session. |

## Repository layout

```
syncfit-simulator/
├── py/
│   ├── syncfit_simulator/
│   │   ├── generator.py     # synthetic PPG / thermal / load frames
│   │   ├── replay.py        # capture save/load and replay
│   │   ├── harness.py       # feeds syncfit-core
│   │   ├── contracts.py     # linkage to syncfit-contracts
│   │   ├── scenarios.py     # normal / fatigue / high_risk / gestational_t2
│   │   └── structures.py    # FrameBuffer (Ring Buffer), EventScript (deque)
│   ├── tests/
│   └── pyproject.toml
├── typescript/
│   ├── src/                 # generator, schema, WebSocket client
│   ├── test/
│   ├── package.json
│   └── tsconfig.json
├── captures/                # real hardware captures
├── scenarios/
└── README.md
```

## Usage

### Python

```bash
cd py
pip install -e ".[dev]"
pytest
python -m syncfit_simulator --list-scenarios
python -m syncfit_simulator --scenario high_risk --frames 3
python -m syncfit_simulator --scenario fatigue --save ../captures/fatigue.json
```

```python
from syncfit_simulator import get_scenario, run_scenario, save_capture, generate_session

result = run_scenario(get_scenario("high_risk"), frames=3)
print(result.to_dict())
```

### TypeScript

```bash
cd typescript
npm install
npm run typecheck
npm test
```

## Stack

Python 3.11+ (NumPy, `syncfit-contracts`, `syncfit-core`) and TypeScript / Node (ajv, vitest).

## Tasks

> **Language:** Python (backend tooling) and TypeScript (client tooling).

### Requirements

- [x] `py/` — implement synthetic PPG, thermal and load signal generation.
- [x] `py/` — implement replay of captured samples.
- [x] `py/` — implement the pipeline harness that feeds `syncfit-core`.
- [x] `ts/` — implement the synthetic telemetry generator.
- [x] `ts/` — implement the reference WebSocket client.
- [x] Define scenarios for normal, fatigue, high-risk and gestational cases.
- [x] Ensure all generated output validates against `syncfit-contracts`.
- [x] Document how to run each scenario end to end.

## Related repositories

- [`syncfit-contracts`](https://github.com/Jenifrutica/syncfit-contracts) — schema for generated data.
- [`syncfit-core`](https://github.com/Jenifrutica/syncfit-core) — consumes simulated and replayed signals.
- [`syncfit-ai-reasoning`](https://github.com/Jenifrutica/syncfit-ai-reasoning) — downstream reasoning.
- [`syncfit-backend`](https://github.com/Jenifrutica/syncfit-backend) — target of the WebSocket client.
- [`syncfit-hardware`](https://github.com/Jenifrutica/syncfit-hardware) — replaced by this layer while real captures are recorded.

All code, comments, documentation and commits in this repository are written in English.
