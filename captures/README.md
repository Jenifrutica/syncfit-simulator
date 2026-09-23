# Captures

Real telemetry captures recorded from the hardware live here as JSON files. While
new captures are being recorded, the simulator generates synthetic data; once a
capture is available, replay it through the same harness.

## Format

A capture is a JSON array of telemetry frames (the exact device payload):

```json
[
  {
    "schema_version": "1.0.0",
    "device_id": "esp32-syncfit-01",
    "session_id": "3f1b2c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
    "timestamp": "2026-09-21T13:24:05Z",
    "modality": "MENSTRUAL_CYCLE",
    "day_or_week": 14,
    "biomarkers": { "delta_temperature_c": 0.42, "rmssd_hrv_ms": 28.5, "isometric_force_loss_pct": 12.8 },
    "ppg_window": { "sample_rate_hz": 100, "window_size": 256, "samples": [721.5, 723.1] }
  }
]
```

## Replay

```python
from syncfit_simulator import load_capture, run_frames

frames = load_capture("captures/session-01.json")
result = run_frames(frames)
print(result.to_dict())
```

Generate a sample capture to inspect the format:

```bash
cd py
python -m syncfit_simulator --scenario fatigue --frames 3 --save ../captures/fatigue-sample.json --no-run
```
