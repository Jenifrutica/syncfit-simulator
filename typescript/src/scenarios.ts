export type Modality = "MENSTRUAL_CYCLE" | "GESTATIONAL";

export interface Scenario {
  name: string;
  modality: Modality;
  dayOrWeek: number;
  deltaTemperatureC: number;
  rmssdHrvMs: number;
  isometricForceLossPct: number;
  hrBpm: number;
  seed: number;
  description: string;
}

export const SCENARIOS: Record<string, Scenario> = {
  normal: {
    name: "normal",
    modality: "MENSTRUAL_CYCLE",
    dayOrWeek: 8,
    deltaTemperatureC: 0.12,
    rmssdHrvMs: 62,
    isometricForceLossPct: 3,
    hrBpm: 66,
    seed: 1,
    description: "Recovered athlete in the follicular phase.",
  },
  fatigue: {
    name: "fatigue",
    modality: "MENSTRUAL_CYCLE",
    dayOrWeek: 24,
    deltaTemperatureC: 0.38,
    rmssdHrvMs: 26,
    isometricForceLossPct: 14,
    hrBpm: 74,
    seed: 2,
    description: "Late luteal phase with autonomic and neuromuscular fatigue.",
  },
  high_risk: {
    name: "high_risk",
    modality: "MENSTRUAL_CYCLE",
    dayOrWeek: 14,
    deltaTemperatureC: 0.45,
    rmssdHrvMs: 18,
    isometricForceLossPct: 18,
    hrBpm: 78,
    seed: 3,
    description: "Ovulatory peak with elevated laxity and low HRV.",
  },
  gestational_t2: {
    name: "gestational_t2",
    modality: "GESTATIONAL",
    dayOrWeek: 18,
    deltaTemperatureC: 0.3,
    rmssdHrvMs: 40,
    isometricForceLossPct: 8,
    hrBpm: 80,
    seed: 4,
    description: "Second trimester; supine exercises become contraindicated.",
  },
};

export function getScenario(name: string): Scenario {
  const scenario = SCENARIOS[name];
  if (!scenario) {
    throw new Error(`unknown scenario '${name}'. Available: ${Object.keys(SCENARIOS).sort().join(", ")}`);
  }
  return scenario;
}

export function scenarioNames(): string[] {
  return Object.keys(SCENARIOS).sort();
}
