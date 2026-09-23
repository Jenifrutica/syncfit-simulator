import { describe, expect, it } from "vitest";

import { generateFrame } from "../src/generator.js";
import { getScenario } from "../src/scenarios.js";
import { buildTelemetryMessage, TelemetrySocket } from "../src/wsClient.js";

function frame() {
  return generateFrame(getScenario("normal"), { sessionId: "3f1b2c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d" });
}

describe("buildTelemetryMessage", () => {
  it("builds a telemetry envelope", () => {
    const message = buildTelemetryMessage(frame(), "req-1");
    expect(message.type).toBe("telemetry");
    expect(message.correlation_id).toBe("req-1");
    expect(message.payload.session_id).toBe(frame().session_id);
  });

  it("omits correlation id when absent", () => {
    expect(buildTelemetryMessage(frame()).correlation_id).toBeUndefined();
  });
});

describe("TelemetrySocket", () => {
  it("sends JSON envelopes through the socket", () => {
    const sentRaw: string[] = [];
    const socket = new TelemetrySocket("ws://localhost:8000/ws");
    socket.connect(() => ({
      send: (data: string) => sentRaw.push(data),
      close: () => undefined,
    }));
    const message = socket.send(frame(), "req-2");
    expect(sentRaw).toHaveLength(1);
    expect(JSON.parse(sentRaw[0] ?? "{}")).toEqual(message);
    expect(socket.history()).toHaveLength(1);
    socket.close();
  });

  it("throws when not connected", () => {
    const socket = new TelemetrySocket("ws://localhost:8000/ws");
    expect(() => socket.send(frame())).toThrow();
  });
});
