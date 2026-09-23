import { describe, expect, it } from "vitest";

import { generateFrame } from "../src/generator.js";
import { createTelemetryValidator, resolveSchemaDir } from "../src/schema.js";
import { getScenario } from "../src/scenarios.js";

const schemaDir = resolveSchemaDir();
const validator = createTelemetryValidator();
const describeIfSchemas = schemaDir ? describe : describe.skip;
const SESSION = "3f1b2c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d";

describeIfSchemas("contract validation (schemas found)", () => {
  it("accepts a generated frame", () => {
    const frame = generateFrame(getScenario("high_risk"), { sessionId: SESSION });
    expect(validator?.(frame)).toBe(true);
  });

  it("rejects an out-of-range biomarker", () => {
    const frame = generateFrame(getScenario("normal"), { sessionId: SESSION });
    frame.biomarkers.rmssd_hrv_ms = 9999;
    expect(validator?.(frame)).toBe(false);
  });

  it("rejects a wrong sample rate", () => {
    const frame = generateFrame(getScenario("normal"), { sessionId: SESSION });
    (frame.ppg_window as { sample_rate_hz: number }).sample_rate_hz = 50;
    expect(validator?.(frame)).toBe(false);
  });
});

describe("schema resolution", () => {
  it("reports whether the contracts schemas are available", () => {
    expect(schemaDir === null || typeof schemaDir === "string").toBe(true);
  });
});
