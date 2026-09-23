# syncfit-simulator (Python)

Synthetic and replayable telemetry for SyncFit Edge. Generates contract-valid
frames and feeds them through `syncfit-core`, standing in for the hardware.

```bash
pip install .
python -m syncfit_simulator --list-scenarios
python -m syncfit_simulator --scenario high_risk --frames 3
```

See the repository root `README.md` for the full description.
