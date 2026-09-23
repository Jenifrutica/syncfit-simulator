import { describe, expect, it } from "vitest";

import { generateFrame, generateSession, synthesizePpg } from "../src/generator.js";
import { getScenario } from "../src/scenarios.js";

describe("generator", () => {
  it("synthesizes the requested number of samples", () => {
    expect(synthesizePpg(2, 60, 1)).toHaveLength(200);
  });

  it("generates a contract-shaped frame", () => {
    const frame = generateFrame(getScenario("normal"), { sessionId: "sid", windowSize: 128 });
    expect(frame.ppg_window.sample_rate_hz).toBe(100);
    expect(frame.ppg_window.samples).toHaveLength(128);
    expect(frame.modality).toBe("MENSTRUAL_CYCLE");
  });

  it("is deterministic for a fixed seed", () => {
    const opts = { sessionId: "sid", frameIndex: 0 };
    const a = generateFrame(getScenario("fatigue"), opts);
    const b = generateFrame(getScenario("fatigue"), opts);
    expect(a.ppg_window.samples).toEqual(b.ppg_window.samples);
  });

  it("generates an ordered session", () => {
    const frames = generateSession(getScenario("high_risk"), "sid", 3);
    expect(frames).toHaveLength(3);
    const times = frames.map((f) => Date.parse(f.timestamp));
    expect(times).toEqual([...times].sort((x, y) => x - y));
  });

  it("rejects invalid input", () => {
    expect(() => generateSession(getScenario("normal"), "sid", 0)).toThrow();
  });
});
