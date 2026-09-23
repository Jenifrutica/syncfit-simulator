# Scenarios

Scenario parameters are defined in code
(`py/syncfit_simulator/scenarios.py` and `typescript/src/scenarios.ts`) so both
runtimes generate the same situations.

| Scenario | Modality | Day/Week | RMSSD (ms) | Force loss (%) | Intent |
|----------|----------|:--------:|:----------:|:--------------:|--------|
| `normal` | MENSTRUAL_CYCLE | 8 | 62 | 3 | Recovered athlete, follicular phase |
| `fatigue` | MENSTRUAL_CYCLE | 24 | 26 | 14 | Late luteal, autonomic + neuromuscular fatigue |
| `high_risk` | MENSTRUAL_CYCLE | 14 | 18 | 18 | Ovulatory peak, elevated laxity |
| `gestational_t2` | GESTATIONAL | 18 | 40 | 8 | Second trimester, supine contraindicated |

List and run them:

```bash
cd py
python -m syncfit_simulator --list-scenarios
python -m syncfit_simulator --scenario high_risk --frames 3
```
