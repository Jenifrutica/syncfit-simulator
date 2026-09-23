import { TelemetryFrame } from "./generator.js";

export interface WsEnvelope {
  schema_version: string;
  type: "telemetry" | "alert" | "prescription" | "ack" | "error" | "ping" | "pong";
  timestamp: string;
  session_id?: string;
  correlation_id?: string;
  payload: TelemetryFrame | Record<string, unknown>;
}

/** Build a telemetry WebSocket message matching the contracts schema. */
export function buildTelemetryMessage(
  frame: TelemetryFrame,
  correlationId?: string,
): WsEnvelope {
  return {
    schema_version: "1.0.0",
    type: "telemetry",
    timestamp: new Date().toISOString(),
    session_id: frame.session_id,
    ...(correlationId ? { correlation_id: correlationId } : {}),
    payload: frame,
  };
}

export interface SocketLike {
  send(data: string): void;
  close(): void;
}

/**
 * Reference WebSocket client. It sends telemetry frames as JSON envelopes and
 * identifies itself with a stable session header suffix where possible.
 */
export class TelemetrySocket {
  private socket: SocketLike | null = null;
  private readonly sent: WsEnvelope[] = [];

  constructor(private readonly url: string) {}

  connect(factory: (url: string) => SocketLike = defaultSocketFactory): void {
    this.socket = factory(this.url);
  }

  send(frame: TelemetryFrame, correlationId?: string): WsEnvelope {
    if (!this.socket) {
      throw new Error("socket not connected; call connect() first");
    }
    const message = buildTelemetryMessage(frame, correlationId);
    this.socket.send(JSON.stringify(message));
    this.sent.push(message);
    return message;
  }

  close(): void {
    this.socket?.close();
    this.socket = null;
  }

  history(): WsEnvelope[] {
    return [...this.sent];
  }
}

function defaultSocketFactory(url: string): SocketLike {
  const WebSocketCtor = (globalThis as { WebSocket?: new (url: string) => unknown }).WebSocket;
  if (!WebSocketCtor) {
    throw new Error("global WebSocket is not available in this runtime");
  }
  return new WebSocketCtor(url) as unknown as SocketLike;
}
