import { Scenario } from "./scenarios.js";

export const SAMPLE_RATE_HZ = 100;
export const DEFAULT_WINDOW_SIZE = 256;

/** Deterministic PRNG so generated samples are reproducible. */
function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function synthesizePpg(
  seconds: number,
  hrBpm: number,
  seed = 0,
  noise = 0.02,
  fs = SAMPLE_RATE_HZ,
): number[] {
  const n = Math.round(seconds * fs);
  if (n <= 0) {
    throw new Error("seconds must be positive");
  }
  const rng = mulberry32(seed);
  const baseFreq = hrBpm / 60;
  const samples: number[] = [];
  for (let i = 0; i < n; i += 1) {
    const t = i / fs;
    const gauss = (rng() + rng() + rng() + rng() - 2) / 0.8165; // approx normal
    samples.push(Math.sin(2 * Math.PI * baseFreq * t) + 0.5 * Math.sin(4 * Math.PI * baseFreq * t) + noise * gauss);
  }
  return samples;
}

export interface TelemetryFrame {
  schema_version: string;
  device_id: string;
  session_id: string;
  timestamp: string;
  modality: string;
  day_or_week: number;
  biomarkers: {
    delta_temperature_c: number;
    rmssd_hrv_ms: number;
    isometric_force_loss_pct: number;
  };
  ppg_window: {
    sample_rate_hz: number;
    window_size: number;
    samples: number[];
  };
}

export interface FrameOptions {
  sessionId: string;
  deviceId?: string;
  windowSize?: number;
  frameIndex?: number;
  timestamp?: Date;
}

export function generateFrame(scenario: Scenario, options: FrameOptions): TelemetryFrame {
  const windowSize = options.windowSize ?? DEFAULT_WINDOW_SIZE;
  const timestamp = options.timestamp ?? new Date();
  const frameIndex = options.frameIndex ?? 0;
  const samples = synthesizePpg(
    windowSize / SAMPLE_RATE_HZ,
    scenario.hrBpm,
    scenario.seed + frameIndex,
  ).map((x) => Math.round(x * 10000) / 10000);

  return {
    schema_version: "1.0.0",
    device_id: options.deviceId ?? "esp32-syncfit-sim",
    session_id: options.sessionId,
    timestamp: timestamp.toISOString(),
    modality: scenario.modality,
    day_or_week: scenario.dayOrWeek,
    biomarkers: {
      delta_temperature_c: scenario.deltaTemperatureC,
      rmssd_hrv_ms: scenario.rmssdHrvMs,
      isometric_force_loss_pct: scenario.isometricForceLossPct,
    },
    ppg_window: {
      sample_rate_hz: SAMPLE_RATE_HZ,
      window_size: windowSize,
      samples,
    },
  };
}

export function generateSession(
  scenario: Scenario,
  sessionId: string,
  frames = 5,
  frameIntervalS = 1,
): TelemetryFrame[] {
  if (frames <= 0) {
    throw new Error("frames must be positive");
  }
  const start = Date.now();
  return Array.from({ length: frames }, (_, i) =>
    generateFrame(scenario, {
      sessionId,
      frameIndex: i,
      timestamp: new Date(start + i * frameIntervalS * 1000),
    }),
  );
}
