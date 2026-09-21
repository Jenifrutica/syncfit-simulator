# SyncFit Simulator

Polyglot test harness that removes the dependency on physical hardware. It replays real captures and generates synthetic telemetry so that backend, core and frontend can be developed, tested and demonstrated before the device is assembled.

## Purpose

Enable parallel development: any team can exercise the full pipeline without waiting for a working sensor rig.

## What belongs here

- **`py/`** — Python tooling:
  - Replay of captured samples.
  - Pipeline harness that feeds [`syncfit-core`](../syncfit-core) and the backend.
  - Synthetic signal generation (PPG waveform, thermal delta, isometric load) aligned with the contracts.
- **`ts/`** — TypeScript tooling:
  - Synthetic telemetry generator.
  - Reference WebSocket client that consumes the types from [`syncfit-contracts`](../syncfit-contracts).
- Scenario definitions for normal, fatigue and high-risk cases.

## What does NOT belong here

- Production logic or model training.
- Real hardware drivers.

## Data Structures

| Structure | Complexity | Purpose |
|-----------|:----------:|---------|
| **Ring Buffer** | O(1) insert | Emitting samples at a steady 100 Hz. |
| **deque** | O(1) append | Scripted event sequences for scenario playback. |

## Suggested structure

```
syncfit-simulator/
├── py/
│   ├── generator/      # synthetic PPG / thermal / load signals
│   ├── replay/         # captured sample playback
│   └── harness/        # pipeline runner into core and backend
├── ts/
│   ├── generator/      # synthetic telemetry emitter
│   └── ws-client/      # reference WebSocket client
├── scenarios/          # normal, fatigue, high-risk
└── README.md
```

## Stack

Python 3.11+ (NumPy) and TypeScript / Node (WebSocket client).

## Related repositories

- [`syncfit-contracts`](../syncfit-contracts) — schema for generated data.
- [`syncfit-core`](../syncfit-core) — consumes replayed signals.
- [`syncfit-backend`](../syncfit-backend) — target of the WebSocket client.
- [`syncfit-hardware`](../syncfit-hardware) — replaced by this layer.

All code, comments, documentation and commits in this repository are written in English.
